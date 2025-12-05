"""Automatic sequential replay viewer for OBS streaming"""
import time
import os
from pathlib import Path
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ReplayViewer:
    """Automatically play HTML replays in sequence for streaming.
    
    Uses Playwright to open replays in a browser window that OBS can capture.
    """
    
    def __init__(
        self,
        replay_dir: str,
        speed: float = 1.0,
        delay_between_battles: int = 5,
        window_width: int = 1280,
        window_height: int = 720,
        on_replay_start: Optional[Callable[[str], None]] = None,
        on_replay_end: Optional[Callable[[str], None]] = None,
    ):
        """Initialize replay viewer.
        
        Args:
            replay_dir: Directory containing HTML replay files
            speed: Playback speed multiplier (not implemented yet)
            delay_between_battles: Seconds to wait between replays
            window_width: Browser window width
            window_height: Browser window height
            on_replay_start: Callback when replay starts
            on_replay_end: Callback when replay ends
        """
        self.replay_dir = Path(replay_dir)
        self.speed = speed
        self.delay = delay_between_battles
        self.window_width = window_width
        self.window_height = window_height
        self.on_replay_start = on_replay_start
        self.on_replay_end = on_replay_end
        
        self.playwright = None
        self.browser = None
        self.page = None
        self.played_replays = set()
        self.running = False
    
    def start(self):
        """Start browser instance."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "Playwright is required for replay viewing. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        logger.info("Starting Playwright browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=[
                '--window-position=0,0',
                f'--window-size={self.window_width},{self.window_height}',
            ]
        )
        self.page = self.browser.new_page()
        self.page.set_viewport_size({
            "width": self.window_width,
            "height": self.window_height
        })
        self.running = True
        logger.info("Browser ready for replay viewing")
    
    def play_replay(self, replay_path: Path):
        """Play a single replay file.
        
        Args:
            replay_path: Path to HTML replay file
        """
        logger.info(f"Playing replay: {replay_path.name}")
        
        if self.on_replay_start:
            self.on_replay_start(str(replay_path))
        
        # Load replay in browser
        file_url = f"file://{replay_path.absolute()}"
        self.page.goto(file_url, wait_until="networkidle")
        
        # Wait for replay to load
        logger.info("Waiting for replay to load...")
        time.sleep(3)
        
        # Auto-click the play button
        try:
            logger.info("Auto-clicking play button...")
            # Try multiple selectors for the play button
            play_clicked = self.page.evaluate("""
                () => {
                    // Try to find and click play button
                    const playButton = document.querySelector('button.playbutton') ||
                                     document.querySelector('button[name="play"]') ||
                                     document.querySelector('.controls button:first-child') ||
                                     document.querySelector('button[title="Play"]');
                    
                    if (playButton) {
                        playButton.click();
                        return true;
                    }
                    
                    // Sometimes it auto-plays, check if already playing
                    return false;
                }
            """)
            
            if play_clicked:
                logger.info("✓ Play button clicked")
            else:
                logger.info("No play button found (may auto-play)")
            
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not auto-click play: {e}")
        
        # Wait for battle to complete by polling
        logger.info("Waiting for battle to complete...")
        self._wait_for_battle_complete()
        
        if self.on_replay_end:
            self.on_replay_end(str(replay_path))
        
        self.played_replays.add(replay_path)
        logger.info(f"✓ Replay complete: {replay_path.name}")
    
    def _wait_for_battle_complete(self):
        """Wait for the battle replay to finish playing.
        
        Polls the replay state to detect when it's done.
        """
        max_wait = 300  # 5 minutes max
        poll_interval = 2  # Check every 2 seconds
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                # Check if replay is finished
                is_finished = self.page.evaluate("""
                    () => {
                        // Check if we can find "Battle ended" or similar text
                        const logText = document.body.innerText || '';
                        
                        // Look for winner message
                        if (logText.includes('won the battle') || 
                            logText.includes('Battle ended') ||
                            logText.includes('forfeited')) {
                            
                            // Also check if replay controls show it's at the end
                            const replayControls = document.querySelector('.replay-controls');
                            if (replayControls) {
                                const seekBar = document.querySelector('input[type="range"]');
                                if (seekBar) {
                                    // If seek bar is at max, replay is done
                                    return seekBar.value === seekBar.max;
                                }
                            }
                            
                            return true;
                        }
                        
                        return false;
                    }
                """)
                
                if is_finished:
                    logger.info("Battle replay finished!")
                    return
                
            except Exception as e:
                logger.debug(f"Error checking replay state: {e}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        logger.warning(f"Battle replay timeout after {max_wait}s")
    
    def _estimate_battle_duration(self) -> float:
        """Estimate how long the battle will take to play.
        
        NOTE: This is deprecated in favor of polling for completion.
        
        Returns:
            Estimated duration in seconds
        """
        # Simple estimate: ~2 seconds per turn, assume 15 turns average
        base_duration = 30.0
        return base_duration / self.speed
    
    def get_unplayed_replays(self):
        """Get list of replays that haven't been played yet."""
        all_replays = sorted(self.replay_dir.glob("battle-*.html"))
        return [r for r in all_replays if r not in self.played_replays]
    
    def watch_directory(self, max_replays: Optional[int] = None):
        """Continuously watch directory and play new replays.
        
        Args:
            max_replays: Maximum number of replays to play (None = infinite)
        """
        logger.info(f"Watching {self.replay_dir} for new replays...")
        replays_played = 0
        
        while self.running:
            unplayed = self.get_unplayed_replays()
            
            if unplayed:
                replay = unplayed[0]  # Play oldest unplayed replay
                self.play_replay(replay)
                replays_played += 1
                
                if max_replays and replays_played >= max_replays:
                    logger.info(f"Reached max replays ({max_replays}), stopping")
                    break
                
                # Delay before next battle
                if self.delay > 0:
                    logger.info(f"Waiting {self.delay}s before next battle...")
                    time.sleep(self.delay)
            else:
                # No new replays, check again soon
                time.sleep(5)
    
    def stop(self):
        """Stop browser and cleanup."""
        logger.info("Stopping replay viewer...")
        self.running = False
        
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Replay viewer stopped")


def main():
    """CLI entry point for standalone replay viewer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-play Pokemon Showdown replays")
    parser.add_argument("--replay_dir", required=True, help="Directory with HTML replays")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed")
    parser.add_argument("--delay", type=int, default=5, help="Delay between battles (seconds)")
    parser.add_argument("--width", type=int, default=1280, help="Window width")
    parser.add_argument("--height", type=int, default=720, help="Window height")
    parser.add_argument("--max_replays", type=int, help="Max replays to play")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    viewer = ReplayViewer(
        replay_dir=args.replay_dir,
        speed=args.speed,
        delay_between_battles=args.delay,
        window_width=args.width,
        window_height=args.height,
    )
    
    try:
        viewer.start()
        viewer.watch_directory(max_replays=args.max_replays)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        viewer.stop()


if __name__ == "__main__":
    main()
