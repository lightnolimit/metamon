"""Opponent matching system: human opponents or bot fallback"""

import time
import logging
import random
import threading
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from metamon.baselines import get_baseline
from metamon.env import QueueOnLocalLadder
from metamon.streaming.mystery_gift_agent import MysteryGiftAgent

logger = logging.getLogger(__name__)


@dataclass
class OpponentInfo:
    """Information about an opponent."""
    opponent_type: str  # 'human' or 'bot'
    name: str
    baseline_class: Optional[Any] = None  # For bot opponents
    is_ladder_match: bool = False


class OpponentMatcher:
    """Manages finding opponents for Mystery-Gift.

    Strategy:
    1. Active search for human opponents on ladder during 90s intervals
    2. Accept incoming challenges from humans
    3. If no human found, select a bot opponent
    4. Rotate through bots or use curriculum
    """

    def __init__(
        self,
        agent: Optional[MysteryGiftAgent] = None,
        human_wait_timeout: int = 60,
        bot_rotation: list = None,
    ):
        """Initialize opponent matcher.

        Args:
            agent: MysteryGiftAgent instance for ladder configuration
            human_wait_timeout: Seconds to wait for human opponent
            bot_rotation: List of bot baseline names to rotate through
        """
        self.agent = agent
        self.human_wait_timeout = human_wait_timeout

        # Default bot rotation
        if bot_rotation is None:
            self.bot_rotation = [
                "RandomBaseline",
                "Grunt",
                "GymLeader",
                "EmeraldKaizo",
            ]
        else:
            self.bot_rotation = bot_rotation

        self.current_bot_index = 0
        self.battles_completed = 0
        self.ladder_env = None
        self.search_active = False
        self.search_thread = None
        self.stop_search = threading.Event()
    
    def find_opponent(self, enable_ladder: bool = False) -> OpponentInfo:
        """Find an opponent (human or bot).
        
        Args:
            enable_ladder: Whether to wait for human opponents
        
        Returns:
            OpponentInfo with opponent details
        """
        if enable_ladder:
            # Try to find human opponent
            human = self._wait_for_human()
            if human:
                return human
        
        # Fall back to bot opponent
        return self._get_bot_opponent()
    
    def _wait_for_human(self) -> Optional[OpponentInfo]:
        """Wait for human opponent on ladder.

        Uses QueueOnLocalLadder to search for human opponents.
        This implementation allows the agent to both accept challenges
        and actively search for matches on the local ladder.

        Returns:
            OpponentInfo if human found, None otherwise
        """
        if not self.agent:
            logger.warning("No agent provided for ladder matching")
            return None

        logger.info(f"Searching {self.human_wait_timeout}s for human opponent...")

        try:
            # Create unique username for ladder
            username = f"Mystery-Gift-Search-{random.randint(1000, 9999)}"

            # Create ladder environment for human search
            self.ladder_env = QueueOnLocalLadder(
                battle_format=self.agent.battle_format,
                num_battles=1,  # Look for one opponent at a time
                observation_space=self.agent.get_config()['observation_space'],
                action_space=self.agent.get_config()['action_space'],
                reward_function=self.agent.get_config()['reward_function'],
                team_set=self.agent.get_config()['team_set'],
                player_username=username,
                player_password=None,
                start_challenging=True,  # Actively search for opponents
                save_trajectories_to=None,  # Don't save ladder search battles
            )

            # Reset to start laddering
            state, info = self.ladder_env.reset()

            # Wait for a short period to see if we get a match
            # Use shorter timeout for responsive search
            search_timeout = min(self.human_wait_timeout, 30)
            start_time = time.time()

            while time.time() - start_time < search_timeout:
                # Check if battle started (we got matched with someone)
                if hasattr(self.ladder_env, '_current_battle') and self.ladder_env._current_battle:
                    # Extract opponent information
                    opponent_name = "Human Opponent"
                    if hasattr(self.ladder_env._current_battle, 'opponent_username'):
                        opponent_name = self.ladder_env._current_battle.opponent_username

                    logger.info(f"Found human opponent: {opponent_name}")

                    # Create opponent info for human
                    opponent_info = OpponentInfo(
                        opponent_type='human',
                        name=opponent_name,
                        baseline_class=None,  # Human opponent
                        is_ladder_match=True,
                    )

                    return opponent_info

                # Check for any incoming challenges or battle start
                time.sleep(1)

            # No human found within timeout
            logger.info("No human opponent found within timeout")
            return None

        except Exception as e:
            logger.error(f"Error during human opponent search: {e}")
            return None

        finally:
            # Clean up ladder environment
            if self.ladder_env:
                try:
                    self.ladder_env.close(purge=True)
                except Exception as e:
                    logger.warning(f"Error cleaning up ladder environment: {e}")
                finally:
                    self.ladder_env = None

    def start_continuous_search(self, duration: int = 90) -> bool:
        """Start continuous human search in background thread.

        Args:
            duration: Duration in seconds to search

        Returns:
            True if search started successfully
        """
        if self.search_active or not self.agent:
            return False

        self.search_active = True
        self.stop_search.clear()

        def search_worker():
            """Background thread for continuous human search."""
            logger.info(f"Starting continuous human search for {duration}s")

            # Create ladder environment for continuous search
            try:
                username = f"Mystery-Gift-Live-{random.randint(1000, 9999)}"
                self.ladder_env = QueueOnLocalLadder(
                    battle_format=self.agent.battle_format,
                    num_battles=10,  # Accept up to 10 matches during search
                    observation_space=self.agent.get_config()['observation_space'],
                    action_space=self.agent.get_config()['action_space'],
                    reward_function=self.agent.get_config()['reward_function'],
                    team_set=self.agent.get_config()['team_set'],
                    player_username=username,
                    player_password=None,
                    start_challenging=True,
                    save_trajectories_to=None,
                )

                # Start laddering
                state, info = self.ladder_env.reset()

                # Search for duration or until stopped
                start_time = time.time()
                while not self.stop_search.is_set() and (time.time() - start_time) < duration:
                    # Check if we got matched
                    if hasattr(self.ladder_env, '_current_battle') and self.ladder_env._current_battle:
                        opponent_name = self.ladder_env._current_battle.opponent_username
                        logger.info(f"Human opponent detected: {opponent_name}")
                        # Here we could trigger immediate battle start
                        # For now, just log the detection

                    time.sleep(2)  # Check every 2 seconds

            except Exception as e:
                logger.error(f"Error in continuous human search: {e}")
            finally:
                if self.ladder_env:
                    try:
                        self.ladder_env.close(purge=True)
                    except:
                        pass
                    finally:
                        self.ladder_env = None
                self.search_active = False

        self.search_thread = threading.Thread(target=search_worker, daemon=True)
        self.search_thread.start()

        return True

    def stop_continuous_search(self):
        """Stop continuous human search."""
        if self.search_active:
            self.stop_search.set()
            self.search_active = False
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=5)
            logger.info("Stopped continuous human search")
    
    def _get_bot_opponent(self) -> OpponentInfo:
        """Select a bot opponent.
        
        Rotates through available bots in a curriculum fashion.
        
        Returns:
            OpponentInfo with bot details
        """
        bot_name = self.bot_rotation[self.current_bot_index]
        self.current_bot_index = (self.current_bot_index + 1) % len(self.bot_rotation)
        
        # Add some variety by occasionally randomizing
        if random.random() < 0.2:
            bot_name = random.choice(self.bot_rotation)
        
        logger.info(f"Selected bot opponent: {bot_name}")
        
        return OpponentInfo(
            opponent_type='bot',
            name=bot_name,
            baseline_class=get_baseline(bot_name),
            is_ladder_match=False,
        )
    
    def get_opponent_display_name(self, opponent: OpponentInfo) -> str:
        """Get display name for opponent.

        Args:
            opponent: OpponentInfo object

        Returns:
            Display name for overlay (e.g., "Scout-1234" or "Human-Player123")
        """
        if opponent.opponent_type == 'human':
            return opponent.name
        else:
            # For bots, add a random suffix like the agent names
            # Ensure total name length doesn't exceed 18 characters (Pokemon Showdown limit)
            suffix = ''.join(str(random.randint(0, 9)) for _ in range(4))
            max_opponent_name_len = 18 - len("-") - len(suffix)  # Reserve space for dash and suffix
            truncated_name = opponent.name[:max_opponent_name_len]
            return f"{truncated_name}-{suffix}"
