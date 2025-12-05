"""Main orchestration for 24/7 tournament streaming"""
import os
import time
import threading
import logging
from pathlib import Path
from typing import Optional

from metamon.env import BattleAgainstBaseline, get_metamon_teams
from metamon.streaming.tournament_manager import (
    TournamentManager,
    TournamentConfig,
    TournamentAgent,
    create_default_tournament,
)
from metamon.streaming.stats_tracker import TournamentStatsTracker
from metamon.streaming.replay_viewer import ReplayViewer
from metamon.streaming.replay_saver import save_replay_html, extract_battle_log_from_battle

logger = logging.getLogger(__name__)


class TournamentStreamOrchestrator:
    """Orchestrate tournament battles and replay viewing for streaming."""
    
    def __init__(
        self,
        agents: list,
        config: TournamentConfig,
        output_dir: str = "./stream_data",
        start_viewer: bool = True,
        viewer_delay: int = 5,
    ):
        """Initialize tournament stream orchestrator.
        
        Args:
            agents: List of TournamentAgent objects
            config: Tournament configuration
            output_dir: Directory for replays and stats
            start_viewer: Whether to start replay viewer automatically
            viewer_delay: Seconds between replays in viewer
        """
        self.tournament = TournamentManager(agents, config)
        self.config = config
        self.output_dir = Path(output_dir)
        self.replay_dir = self.output_dir / config.battle_format / "html_replays"
        self.stats_dir = self.output_dir / "tournament_stats"
        
        # Create directories
        self.replay_dir.mkdir(parents=True, exist_ok=True)
        self.stats_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize stats tracker
        self.stats = TournamentStatsTracker(str(self.stats_dir))
        
        # Replay viewer (optional)
        self.viewer = None
        self.viewer_thread = None
        self.should_start_viewer = start_viewer
        if start_viewer:
            self.viewer = ReplayViewer(
                replay_dir=str(self.replay_dir),
                delay_between_battles=viewer_delay,
            )
        
        self.running = False
        self.battles_completed = 0
    
    def run_battle(
        self,
        agent1: TournamentAgent,
        agent2: TournamentAgent,
        battle_number: int,
    ) -> bool:
        """Run a single battle between two agents.
        
        Args:
            agent1: First agent
            agent2: Second agent
            battle_number: Battle number (for logging)
        
        Returns:
            True if agent1 won, False if agent2 won
        """
        logger.info(f"Battle {battle_number}: {agent1.name} vs {agent2.name}")
        
        # Update current matchup display
        self.stats.set_current_matchup(agent1.name, agent2.name)
        
        # Get team sets
        team_set1 = get_metamon_teams(self.config.battle_format, agent1.team_set)
        team_set2 = get_metamon_teams(self.config.battle_format, agent2.team_set)
        
        # Get agent info
        agent1_info = self.tournament.get_agent_info(agent1)
        agent2_info = self.tournament.get_agent_info(agent2)
        
        # For now, we'll use baseline vs baseline battles
        # More complex RL agent vs agent battles would require different setup
        if not agent1_info['is_baseline'] or not agent2_info['is_baseline']:
            logger.warning("Non-baseline agents not fully supported yet, using baseline")
        
        # Create battle environment
        # CRITICAL: Must set save_trajectories_to for HTML replay generation
        # Use agent names instead of random MM-XXXXX
        import random
        random_suffix = ''.join(str(random.randint(0, 9)) for _ in range(4))
        
        env = BattleAgainstBaseline(
            battle_format=self.config.battle_format,
            observation_space=agent1_info['observation_space'],
            action_space=agent1_info['action_space'],
            reward_function=agent1_info['reward_function'],
            team_set=team_set1,
            opponent_type=agent2_info['opponent_type'],
            battle_backend=self.config.battle_backend,
            save_trajectories_to=str(self.output_dir),
            player_username=f"{agent1.name}-{random_suffix}",
            opponent_username=f"{agent2.name}-{random_suffix}",
        )
        
        # Override opponent team
        env._current_opponent.team = team_set2
        
        # Run battle
        state, info = env.reset()
        done = False
        
        while not done:
            # Random policy for now (you can plug in real agents here)
            action = env.action_space.sample()
            state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        
        # Get result
        agent1_won = info.get('won', False)
        winner = agent1.name if agent1_won else agent2.name
        
        logger.info(f"Battle {battle_number} complete: {winner} wins!")
        
        # Save HTML replay
        try:
            battle_log = extract_battle_log_from_battle(env.current_battle)
            battle_id = f"{battle_number:06d}"
            
            save_replay_html(
                battle_log=battle_log,
                battle_id=battle_id,
                output_dir=str(self.replay_dir),
                player_name=agent1.name,
                opponent_name=agent2.name,
                battle_format=self.config.battle_format,
            )
            logger.info(f"Saved HTML replay: battle-{battle_id}.html")
        except Exception as e:
            logger.error(f"Failed to save HTML replay: {e}")
        
        # Update stats
        self.stats.record_battle(agent1.name, agent2.name, winner)
        
        # Cleanup
        env.close()
        
        return agent1_won
    
    def run_matchup(
        self,
        agent1: TournamentAgent,
        agent2: TournamentAgent,
        matchup_number: int,
    ):
        """Run a series of battles for one matchup.
        
        Args:
            agent1: First agent
            agent2: Second agent
            matchup_number: Matchup number (for logging)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Matchup {matchup_number}: {agent1.name} vs {agent2.name}")
        logger.info(f"Best of {self.config.battles_per_matchup}")
        logger.info(f"{'='*60}\n")
        
        agent1_wins = 0
        agent2_wins = 0
        
        for i in range(self.config.battles_per_matchup):
            self.battles_completed += 1
            
            agent1_won = self.run_battle(agent1, agent2, self.battles_completed)
            
            if agent1_won:
                agent1_wins += 1
            else:
                agent2_wins += 1
            
            # Check if we have a winner
            needed_wins = (self.config.battles_per_matchup // 2) + 1
            if agent1_wins >= needed_wins or agent2_wins >= needed_wins:
                break
        
        winner = agent1.name if agent1_wins > agent2_wins else agent2.name
        logger.info(f"\nMatchup complete: {winner} wins {max(agent1_wins, agent2_wins)}-{min(agent1_wins, agent2_wins)}")
    
    def start_viewer(self):
        """Start replay viewer in background thread."""
        if not self.viewer:
            logger.warning("No viewer configured")
            return
        
        def viewer_loop():
            try:
                logger.info("Starting replay viewer...")
                self.viewer.start()
                self.viewer.watch_directory()
            except Exception as e:
                logger.error(f"Viewer error: {e}")
            finally:
                self.viewer.stop()
        
        self.viewer_thread = threading.Thread(target=viewer_loop, daemon=True)
        self.viewer_thread.start()
        logger.info("Replay viewer started in background")
        
        # Give viewer time to start
        time.sleep(3)
    
    def run_tournament(self):
        """Run the complete tournament."""
        self.running = True
        
        logger.info("\n" + self.tournament.get_tournament_summary())
        
        # Start viewer AFTER showing summary but BEFORE first battle
        # This way the browser opens and is ready when first replay arrives
        if self.should_start_viewer and self.viewer:
            self.start_viewer()
            # Give viewer extra time to fully start
            logger.info("Waiting for viewer to fully start...")
            time.sleep(5)
        
        matchup_number = 0
        
        while self.running:
            matchup = self.tournament.get_next_matchup()
            
            if matchup is None:
                logger.info("Tournament complete!")
                break
            
            matchup_number += 1
            agent1, agent2 = matchup
            
            self.run_matchup(agent1, agent2, matchup_number)
            
            # Small delay between matchups
            time.sleep(2)
    
    def stop(self):
        """Stop the tournament."""
        logger.info("Stopping tournament...")
        self.running = False
        
        if self.viewer:
            self.viewer.stop()


def start_tournament_stream(
    battle_format: str = "gen1ou",
    output_dir: str = "./stream_data",
    agents: Optional[list] = None,
    config: Optional[TournamentConfig] = None,
):
    """Start a 24/7 tournament stream.
    
    Args:
        battle_format: Pokemon format (e.g., gen1ou, gen2ou)
        output_dir: Directory for output files
        agents: List of TournamentAgent objects (None = use defaults)
        config: TournamentConfig (None = use defaults)
    """
    # Create output directory if needed
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{output_dir}/tournament.log'),
            logging.StreamHandler()
        ]
    )
    
    # Use default tournament if not specified
    if agents is None or config is None:
        agents, config = create_default_tournament(battle_format)
    
    # Update format in config if needed
    config.battle_format = battle_format
    
    # Create and run orchestrator
    orchestrator = TournamentStreamOrchestrator(
        agents=agents,
        config=config,
        output_dir=output_dir,
        start_viewer=True,
        viewer_delay=5,
    )
    
    try:
        orchestrator.run_tournament()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        orchestrator.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start 24/7 tournament stream")
    parser.add_argument("--format", default="gen1ou", help="Battle format")
    parser.add_argument("--output", default="./stream_data", help="Output directory")
    
    args = parser.parse_args()
    
    start_tournament_stream(
        battle_format=args.format,
        output_dir=args.output,
    )
