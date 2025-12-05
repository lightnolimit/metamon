"""Mystery-Gift streaming: Follow one agent improving via RL"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Optional

from metamon.env import BattleAgainstBaseline, QueueOnLocalLadder, get_metamon_teams
from metamon.streaming.mystery_gift_agent import MysteryGiftAgent
from metamon.streaming.opponent_matcher import OpponentMatcher, OpponentInfo
from metamon.streaming.training_tracker import TrainingMetrics
from metamon.streaming.replay_viewer import ReplayViewer
from metamon.streaming.obs_overlay import OBSOverlay

logger = logging.getLogger(__name__)


class MysteryGiftStreamOrchestrator:
    """Stream Mystery-Gift's journey to Pokemon mastery."""
    
    def __init__(
        self,
        agent: MysteryGiftAgent,
        output_dir: str = "./stream_data",
        enable_ladder: bool = False,
        human_wait_timeout: int = 60,
        start_viewer: bool = True,
        viewer_delay: int = 5,
    ):
        """Initialize Mystery-Gift stream orchestrator.
        
        Args:
            agent: MysteryGiftAgent instance
            output_dir: Directory for replays and stats
            enable_ladder: Whether to accept human opponents
            human_wait_timeout: Seconds to wait for humans
            start_viewer: Whether to start replay viewer
            viewer_delay: Seconds between replays
        """
        self.agent = agent
        self.output_dir = Path(output_dir)
        self.replay_dir = self.output_dir / agent.battle_format / "html_replays"
        self.stats_dir = self.output_dir / "mystery_gift_stats"
        
        # Create directories
        self.replay_dir.mkdir(parents=True, exist_ok=True)
        self.stats_dir.mkdir(parents=True, exist_ok=True)
        
        # Opponent matcher
        self.opponent_matcher = OpponentMatcher(
            human_wait_timeout=human_wait_timeout
        )
        
        # Training metrics
        self.training_metrics = TrainingMetrics(
            agent_name=agent.base_name,
            output_file=str(self.stats_dir / "training_metrics.json"),
        )
        
        # Replay viewer
        self.viewer = None
        self.viewer_thread = None
        self.should_start_viewer = start_viewer
        if start_viewer:
            self.viewer = ReplayViewer(
                replay_dir=str(self.replay_dir),
                delay_between_battles=viewer_delay,
            )

        # OBS overlay
        self.obs_overlay = OBSOverlay(self.stats_dir)

        self.enable_ladder = enable_ladder
        self.running = False
        self.battles_completed = 0
    
    def _generate_agent_username(self, battle_num: int) -> str:
        """Generate username for Mystery-Gift."""
        # Use battle number as suffix for uniqueness (support up to 99999 battles)
        return f"{self.agent.base_name}-{battle_num % 100000:05d}"
    
    def run_battle(self, opponent: OpponentInfo, battle_number: int) -> bool:
        """Run a single battle.
        
        Args:
            opponent: OpponentInfo for this battle
            battle_number: Battle number (for logging)
        
        Returns:
            True if Mystery-Gift won
        """
        agent_username = self._generate_agent_username(battle_number)
        opponent_display = self.opponent_matcher.get_opponent_display_name(opponent)
        
        logger.info(f"Battle {battle_number}: {agent_username} vs {opponent_display}")

        # Update OBS overlay with battle start status
        battle_status = f"Battle {battle_number}: Starting vs {opponent_display}"
        self.obs_overlay.update_stats({
            "current_battle_status": battle_status,
            "agent_name": agent_username
        })

        # Save current opponent status
        self._save_current_status(opponent, opponent_display)
        
        # Create battle environment
        agent_config = self.agent.get_config()
        
        env = BattleAgainstBaseline(
            battle_format=self.agent.battle_format,
            observation_space=agent_config['observation_space'],
            action_space=agent_config['action_space'],
            reward_function=agent_config['reward_function'],
            team_set=agent_config['team_set'],
            opponent_type=opponent.baseline_class,
            battle_backend="metamon",
            save_trajectories_to=str(self.output_dir),
            player_username=agent_username,
            opponent_username=opponent_display,
        )
        
        # Run battle
        state, info = env.reset()
        done = False
        total_reward = 0.0
        
        while not done:
            # Agent selects action
            legal_actions = info.get('legal_actions', [0])
            action = self.agent.select_action(state, legal_actions)
            
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated
        
        # Get result
        mystery_gift_won = info.get('won', False)
        
        logger.info(
            f"Battle {battle_number} complete: "
            f"{agent_username} {'WON' if mystery_gift_won else 'LOST'} "
            f"vs {opponent_display}"
        )
        
        # Update training metrics
        self.training_metrics.update(
            won=mystery_gift_won,
            opponent_type=opponent.opponent_type,
            opponent_name=opponent.name,
            reward=total_reward,
        )
        
        # Save overlay
        self.training_metrics.save_stream_overlay(
            str(self.stats_dir / "mystery_gift_overlay.txt")
        )

        # Update OBS overlay with current battle status
        battle_status = f"Battle {battle_number}: {'WON' if mystery_gift_won else 'LOST'} vs {opponent_display}"
        self.obs_overlay.update_stats({
            "current_battle_status": battle_status,
            "agent_name": agent_username
        })

        # Cleanup
        try:
            env.close(purge=True)
        except Exception as e:
            logger.warning(f"Error closing environment: {e}")

        # Force garbage collection to free memory
        import gc
        gc.collect()

        # Clean up old replays (keep last 10)
        self._cleanup_old_replays()

        self.battles_completed += 1

        return mystery_gift_won
    
    def _save_current_status(self, opponent: OpponentInfo, opponent_display: str):
        """Save current battle status for overlay."""
        status_file = self.stats_dir / "current_status.txt"
        
        if opponent.opponent_type == 'human':
            status = f"""╔══════════════════════════════════════════════════════╗
║              BATTLE VS HUMAN OPPONENT                ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  {self.agent.base_name:^50s}  ║
║                       VS                             ║
║  {opponent_display:^50s}  ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
        else:
            status = f"""╔══════════════════════════════════════════════════════╗
║              TRAINING BATTLE VS BOT                  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  {self.agent.base_name:^50s}  ║
║                       VS                             ║
║  {opponent_display:^50s}  ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
        
        with open(status_file, 'w') as f:
            f.write(status)

    def _cleanup_old_replays(self):
        """Clean up old replay files to keep only the last 10 battles."""
        try:
            # Find HTML replay directories
            for format_dir in self.output_dir.glob("*/html_replays"):
                if not format_dir.is_dir():
                    continue

                # Get all HTML replays and sort by modification time
                replay_files = list(format_dir.glob("battle-*.html"))
                replay_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

                # Keep only the last 10
                if len(replay_files) > 10:
                    for old_replay in replay_files[10:]:
                        try:
                            old_replay.unlink()
                            logger.debug(f"Removed old replay: {old_replay.name}")
                        except Exception as e:
                            logger.warning(f"Failed to remove {old_replay}: {e}")

            # Also clean up compressed replay files
            for format_dir in self.output_dir.glob("*/"):
                if format_dir.is_dir():
                    lz4_files = list(format_dir.glob("*.json.lz4"))
                    if len(lz4_files) > 10:
                        lz4_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        for old_lz4 in lz4_files[10:]:
                            try:
                                old_lz4.unlink()
                                logger.debug(f"Removed old LZ4 file: {old_lz4.name}")
                            except Exception as e:
                                logger.warning(f"Failed to remove {old_lz4}: {e}")

        except Exception as e:
            logger.warning(f"Error during replay cleanup: {e}")

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
                import traceback
                traceback.print_exc()
            finally:
                self.viewer.stop()
        
        self.viewer_thread = threading.Thread(target=viewer_loop, daemon=True)
        self.viewer_thread.start()
        logger.info("Replay viewer started in background")

        # Give viewer time to start
        time.sleep(3)

    def _wait_between_battles(self):
        """Wait 30 seconds between battles with opponent search."""
        logger.info("Waiting 30 seconds before next battle...")

        # Update OBS overlay with waiting status
        self.obs_overlay.update_stats({
            "current_battle_status": "Waiting for next battle...",
            "agent_name": self.agent.base_name
        })

        # Split wait into 5-second intervals to check for stop signal
        for i in range(6):  # 6 * 5 = 30 seconds
            if not self.running:
                break

            remaining = 30 - (i * 5)
            if remaining > 0:
                # Update OBS overlay with countdown
                self.obs_overlay.update_stats({
                    "current_battle_status": f"Waiting for next battle... ({remaining}s remaining)",
                    "agent_name": self.agent.base_name
                })

            time.sleep(5)

            # Only search for human opponents during wait
            if self.enable_ladder and i == 2:  # Check once at 15 seconds
                logger.info("Checking for human opponents...")
                # Could add human opponent check here if needed
    
    def run_training_stream(self, max_battles: Optional[int] = None):
        """Run the training stream.
        
        Args:
            max_battles: Maximum battles to run (None = infinite)
        """
        self.running = True
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Mystery-Gift Training Stream Starting")
        logger.info(f"Format: {self.agent.battle_format}")
        logger.info(f"Ladder enabled: {self.enable_ladder}")
        logger.info(f"{'='*60}\n")
        
        # Start viewer
        if self.should_start_viewer and self.viewer:
            self.start_viewer()
            logger.info("Waiting for viewer to fully start...")
            time.sleep(5)

        # Start OBS overlay
        self.obs_overlay.start()
        overlay_path = self.obs_overlay.overlay_file
        logger.info(f"OBS overlay started: {overlay_path}")
        logger.info("Add this as a Browser source in OBS:")
        logger.info(f"  URL: file://{overlay_path.absolute()}")
        logger.info(f"  Width: 450, Height: Auto")

        battle_num = 0
        
        while self.running:
            if max_battles and battle_num >= max_battles:
                logger.info(f"Reached max battles ({max_battles})")
                break
            
            battle_num += 1
            
            # Find opponent
            opponent = self.opponent_matcher.find_opponent(
                enable_ladder=self.enable_ladder
            )
            
            # Run battle
            self.run_battle(opponent, battle_num)

            # Wait 30 seconds between battles with opponent search
            self._wait_between_battles()
    
    def stop(self):
        """Stop the stream."""
        logger.info("Stopping Mystery-Gift stream...")
        self.running = False
        
        if self.viewer:
            self.viewer.stop()


def start_mystery_gift_stream(
    battle_format: str = "gen1ou",
    output_dir: str = "./stream_data",
    team_set: str = "competitive",
    enable_ladder: bool = False,
    human_wait_timeout: int = 60,
    use_pretrained: bool = False,
    pretrained_model: Optional[str] = None,
    max_battles: Optional[int] = None,
):
    """Start Mystery-Gift training stream.
    
    Args:
        battle_format: Pokemon format
        output_dir: Directory for output files
        team_set: Which team set to use
        enable_ladder: Whether to accept human opponents
        human_wait_timeout: Seconds to wait for humans
        use_pretrained: Use a pretrained model
        pretrained_model: Name of pretrained model
        max_battles: Max battles to run (None = infinite)
    """
    # Set up logging
    os.makedirs(output_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{output_dir}/mystery_gift.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create Mystery-Gift agent
    agent = MysteryGiftAgent(
        battle_format=battle_format,
        base_name="Mystery-Gift",
        team_set=team_set,
        use_pretrained=use_pretrained,
        pretrained_model=pretrained_model,
    )
    
    # Create and run orchestrator
    orchestrator = MysteryGiftStreamOrchestrator(
        agent=agent,
        output_dir=output_dir,
        enable_ladder=enable_ladder,
        human_wait_timeout=human_wait_timeout,
        start_viewer=True,
        viewer_delay=5,
    )
    
    try:
        orchestrator.run_training_stream(max_battles=max_battles)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        orchestrator.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Mystery-Gift training stream")
    parser.add_argument("--format", default="gen1ou", help="Battle format")
    parser.add_argument("--output", default="./stream_data", help="Output directory")
    parser.add_argument("--ladder", action="store_true", help="Enable ladder matching")
    parser.add_argument("--max-battles", type=int, help="Max battles to run")
    
    args = parser.parse_args()
    
    start_mystery_gift_stream(
        battle_format=args.format,
        output_dir=args.output,
        enable_ladder=args.ladder,
        max_battles=args.max_battles,
    )
