"""Live agent system for human opponent matching in Mystery-Gift multi-agent streaming.

Implements live agents that:
- Search for human opponents on Pokemon Showdown ladder
- Battle immediately when matched (no scouting/forfeiting)
- Use same MysteryGiftAgent battle logic as main agent
- Contribute to shared training metrics
- Use unified sequential naming system (mysgift-l-XXXXXXX)
"""

import asyncio
import time
import logging
import threading
from typing import Optional, Dict, Any, List
from pathlib import Path

from metamon.streaming.mystery_gift_agent import MysteryGiftAgent
from metamon.streaming.agent_naming import get_naming_manager
from metamon.streaming.training_tracker import SharedTrainingMetrics
from metamon.env import BattleAgainstBaseline, QueueOnLocalLadder

logger = logging.getLogger(__name__)


class LiveMysteryGiftAgent:
    """Live agent that uses QueueOnLocalLadder for human opponent matching.

    Simplified implementation that uses the existing battle infrastructure
    with real human opponent matching instead of placeholder functionality.
    """

    def __init__(
        self,
        mystery_gift_agent: MysteryGiftAgent,
        username: str,
        battle_format: str,
        team_set: str,
        output_dir: str = "./stream_data",
        training_metrics: Optional[SharedTrainingMetrics] = None,
    ):
        """Initialize live agent.

        Args:
            mystery_gift_agent: MysteryGiftAgent instance for decision logic
            username: Username for this live agent (from unified naming system)
            battle_format: Pokemon battle format (e.g., gen1ou)
            team_set: Team set to use (e.g., competitive)
            output_dir: Directory for saving replays and data
            training_metrics: Shared training metrics for multi-agent tracking
        """
        self.mystery_gift_agent = mystery_gift_agent
        self.username = username
        self.battle_format = battle_format
        self.team_set = team_set
        self.output_dir = Path(output_dir)
        self.training_metrics = training_metrics

        # Battle state
        self.battle_count = 0
        self.in_battle = False

        logger.info(f"LiveMysteryGiftAgent initialized: {username} for {battle_format}")

    def run_human_battle(self) -> bool:
        """Run a single battle against a human opponent.

        Returns:
            True if the live agent won the battle
        """
        try:
            self.in_battle = True
            logger.info(f"Live agent {self.username} searching for human battle...")

            # Get agent configuration for battle setup
            agent_config = self.mystery_gift_agent.get_config()

            # Create QueueOnLocalLadder environment for human opponent matching
            env = QueueOnLocalLadder(
                battle_format=self.battle_format,
                num_battles=1,  # One battle at a time for continuous loop
                observation_space=agent_config['observation_space'],
                action_space=agent_config['action_space'],
                reward_function=agent_config['reward_function'],
                player_team_set=self.team_set,
                player_username=self.username,
                save_trajectories_to=str(self.output_dir),
            )

            # Run battle with human opponent
            state, info = env.reset()
            done = False
            total_reward = 0.0

            while not done:
                # Agent selects action using MysteryGiftAgent logic
                legal_actions = info.get('legal_actions', [0])
                action = self.mystery_gift_agent.select_action(state, legal_actions)

                state, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                done = terminated or truncated

            # Get battle result
            won = info.get('won', False)
            opponent_name = info.get('opponent_name', 'Human')

            logger.info(
                f"Live agent {self.username} {'WON' if won else 'LOST'} vs {opponent_name} "
                f"(Battle {self.battle_count + 1})"
            )

            # Update battle count
            self.battle_count += 1

            # Update shared training metrics
            if self.training_metrics:
                self.training_metrics.update_agent_battle(
                    agent_id=self.username,
                    won=won,
                    opponent_type='human',
                    opponent_name=opponent_name,
                    reward=total_reward,
                )

            logger.info(f"Updated shared training metrics for {self.username}")

            # Cleanup
            try:
                env.close(purge=True)
            except Exception as e:
                logger.warning(f"Error closing live agent environment: {e}")

            return won

        except Exception as e:
            logger.error(f"Error in live agent battle for {self.username}: {e}")
            self.in_battle = False
            return False
        finally:
            self.in_battle = False


class LiveAgentManager:
    """Manages multiple live agents for human opponent matching.

    Creates and manages live agents that use QueueOnLocalLadder for real
    human opponent battles with MysteryGiftAgent integration.
    """

    def __init__(
        self,
        mystery_gift_agent: MysteryGiftAgent,
        battle_format: str,
        team_set: str,
        output_dir: str = "./stream_data",
        training_metrics: Optional[SharedTrainingMetrics] = None,
        max_live_agents: int = 2,
    ):
        """Initialize live agent manager.

        Args:
            mystery_gift_agent: MysteryGiftAgent instance for decision logic
            battle_format: Pokemon battle format
            team_set: Team set to use for live agents
            output_dir: Directory for saving replays and data
            training_metrics: Shared training metrics for multi-agent tracking
            max_live_agents: Maximum number of concurrent live agents
        """
        self.mystery_gift_agent = mystery_gift_agent
        self.battle_format = battle_format
        self.team_set = team_set
        self.output_dir = Path(output_dir)
        self.training_metrics = training_metrics
        self.max_live_agents = max_live_agents

        self.naming_manager = get_naming_manager()
        self.live_agents: Dict[str, LiveMysteryGiftAgent] = {}
        self.agent_threads: List[threading.Thread] = []
        self.running = False

        logger.info(f"LiveAgentManager initialized (max {max_live_agents} agents)")

    def start_live_agents(self):
        """Start live agents to search for human opponents."""
        if self.running:
            logger.warning("Live agents already running")
            return

        self.running = True

        # Create real live agents
        for i in range(self.max_live_agents):
            username = self.naming_manager.get_next_username('l')  # 'l' for live

            live_agent = LiveMysteryGiftAgent(
                mystery_gift_agent=self.mystery_gift_agent,
                username=username,
                battle_format=self.battle_format,
                team_set=self.team_set,
                output_dir=str(self.output_dir),
                training_metrics=self.training_metrics,
            )

            self.live_agents[username] = live_agent

        logger.info(f"Created {self.max_live_agents} live agents for human battles")

        # Start each agent in its own thread
        for username, agent in self.live_agents.items():
            thread = threading.Thread(
                target=self._run_agent_loop,
                args=(agent,),
                daemon=True,
                name=f"LiveAgent-{username}"
            )
            self.agent_threads.append(thread)
            thread.start()
            logger.info(f"Started live agent thread for: {username}")

        logger.info(f"All {self.max_live_agents} live agents started and searching for human battles")

    def _run_agent_loop(self, agent: LiveMysteryGiftAgent):
        """Run continuous battle loop for a single live agent."""
        try:
            while self.running:
                try:
                    # Run battle with human opponent
                    won = agent.run_human_battle()

                    # Wait between battles to avoid overwhelming the server
                    for _ in range(30):  # 30 seconds wait, checking every second
                        if not self.running:
                            break
                        time.sleep(1)

                except Exception as e:
                    logger.error(f"Error in live agent loop for {agent.username}: {e}")
                    # Wait before retrying
                    time.sleep(60)

        except Exception as e:
            logger.error(f"Fatal error in live agent loop for {agent.username}: {e}")

    def stop_live_agents(self):
        """Stop all live agents."""
        logger.info("Stopping live agents...")
        self.running = False

        # Wait for threads to finish
        for thread in self.agent_threads:
            if thread.is_alive():
                thread.join(timeout=5)
                if thread.is_alive():
                    logger.warning(f"Live agent thread {thread.name} did not stop gracefully")

        self.agent_threads.clear()
        self.live_agents.clear()
        logger.info("All live agents stopped")

    def get_live_agent_status(self) -> Dict[str, Any]:
        """Get status of all live agents.

        Returns:
            Dictionary with live agent status information
        """
        status = {
            'running': self.running,
            'total_agents': len(self.live_agents),
            'active_threads': len([t for t in self.agent_threads if t.is_alive()]),
            'agents': {},
        }

        for agent_id, agent in self.live_agents.items():
            status['agents'][agent_id] = {
                'username': agent.username,
                'battle_count': agent.battle_count,
                'in_battle': agent.in_battle,
                'thread_alive': any(
                    agent_id in thread.name and thread.is_alive()
                    for thread in self.agent_threads
                ),
            }

        return status