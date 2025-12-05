# Quick Start: 24/7 Lass Training Livestream

## What You Have
- ✅ Pokemon Showdown server (local)
- ✅ Metamon RL environment
- ✅ Pretrained agents (SyntheticRLV2 etc.)
- ✅ Battle execution (`python -m metamon.env`)
- ✅ JSON trajectory saving

## What You Need
1. **HTML replay auto-generation** ← START HERE
2. **Sequential replay viewer** (Playwright/Selenium)
3. **OBS integration** (browser source capture)
4. **Stats dashboard** (win rate, episode count, etc.)

---

## Step 1: Generate HTML Replays (Week 1)

### Quick Implementation

Create `metamon/streaming/replay_saver.py`:

```python
"""Save battles as HTML replays for streaming"""
import os
from typing import Optional

def generate_replay_html(battle_log: str, battle_id: str, 
                        player_name: str = "Lass", 
                        opponent_name: str = "Opponent") -> str:
    """Generate standalone HTML replay file"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>{player_name} vs {opponent_name} - Battle {battle_id}</title>
    <meta charset="utf-8" />
</head>
<body>
<script type="text/plain" class="battle-log-data">{battle_log}</script>
<script src="https://play.pokemonshowdown.com/js/replay-embed.js"></script>
</body>
</html>'''

def save_replay_html(battle_log: str, battle_id: str, output_dir: str,
                     player_name: str = "Lass", opponent_name: str = "Opponent"):
    """Save HTML replay to file"""
    os.makedirs(output_dir, exist_ok=True)
    html_content = generate_replay_html(battle_log, battle_id, player_name, opponent_name)
    filepath = os.path.join(output_dir, f"battle-{battle_id}.html")
    with open(filepath, 'w') as f:
        f.write(html_content)
    return filepath
```

### Integrate into Metamon

Modify `metamon/env/wrappers.py` around line 400:

```python
# In PokeEnvWrapper.step() method, after line 426:

if self.save_trajectories_to is not None:
    # ... existing JSON save code ...
    
    # NEW: Also save HTML replay
    try:
        from metamon.streaming.replay_saver import save_replay_html
        battle_log = self.current_battle.get_showdown_log()
        html_path = save_replay_html(
            battle_log=battle_log,
            battle_id=battle_id,
            output_dir=os.path.join(self.save_trajectories_to, "html_replays"),
            player_name=self.player_username,
            opponent_name=opponent_name
        )
        print(f"Saved HTML replay: {html_path}")
    except Exception as e:
        print(f"Failed to save HTML replay: {e}")
```

### Test It

```bash
# Terminal 1: Start Showdown server
cd server/pokemon-showdown
node pokemon-showdown start --no-security

# Terminal 2: Run battles with replay saving
python -c "
from metamon.env import BattleAgainstBaseline, get_metamon_teams
from metamon.baselines import get_baseline
from metamon.interface import DefaultObservationSpace, DefaultActionSpace, DefaultShapedReward

env = BattleAgainstBaseline(
    battle_format='gen1ou',
    observation_space=DefaultObservationSpace(),
    action_space=DefaultActionSpace(),
    reward_function=DefaultShapedReward(),
    team_set=get_metamon_teams('gen1ou', 'competitive'),
    opponent_type=get_baseline('GymLeader'),
    save_trajectories_to='./stream_data',
)

for i in range(5):
    state, info = env.reset()
    done = False
    while not done:
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        done = terminated or truncated
    print(f'Battle {i+1} complete')
"

# Check results
ls stream_data/gen1ou/html_replays/
# You should see battle-*.html files!

# Open one in browser to verify
open stream_data/gen1ou/html_replays/battle-*.html
```

---

## Step 2: Sequential Replay Viewer (Week 2)

### Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Create Viewer

`metamon/streaming/replay_viewer.py`:

```python
"""Automatically play HTML replays in sequence for streaming"""
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

class ReplayViewer:
    def __init__(self, replay_dir: str, speed: float = 1.0, 
                 delay_between_battles: int = 5):
        self.replay_dir = Path(replay_dir)
        self.speed = speed
        self.delay = delay_between_battles
        self.playwright = None
        self.browser = None
        self.page = None
        
    def start(self):
        """Start browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 720})
        
    def play_replay(self, replay_path: Path):
        """Play a single replay"""
        print(f"Playing: {replay_path.name}")
        self.page.goto(f"file://{replay_path.absolute()}")
        
        # Wait for replay to load
        time.sleep(2)
        
        # Auto-play the replay
        # (The replay-embed.js handles playback automatically)
        
        # Wait for battle to complete (estimate based on turn count)
        # You may need to adjust this or detect completion via JS
        time.sleep(30 * self.speed)  # ~30 seconds per battle average
        
    def watch_directory(self):
        """Continuously watch for new replays and play them"""
        played_replays = set()
        
        while True:
            replays = sorted(self.replay_dir.glob("battle-*.html"))
            
            for replay in replays:
                if replay not in played_replays:
                    self.play_replay(replay)
                    played_replays.add(replay)
                    print(f"Waiting {self.delay}s before next battle...")
                    time.sleep(self.delay)
            
            # Check for new replays every 5 seconds
            time.sleep(5)
    
    def stop(self):
        """Cleanup"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay_dir", required=True)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--delay", type=int, default=5)
    args = parser.parse_args()
    
    viewer = ReplayViewer(args.replay_dir, args.speed, args.delay)
    try:
        viewer.start()
        viewer.watch_directory()
    except KeyboardInterrupt:
        print("Stopping viewer...")
    finally:
        viewer.stop()
```

### Test Viewer

```bash
# Play existing replays
python -m metamon.streaming.replay_viewer \
    --replay_dir stream_data/gen1ou/html_replays \
    --speed 1.5 \
    --delay 3

# This will open a browser window and auto-play each replay
# Point OBS Browser Source at this window!
```

---

## Step 3: OBS Integration (Week 3)

### OBS Setup

1. **Add Browser Source**:
   - Sources → Add → Window Capture
   - Select the Playwright browser window
   - Crop to just the battle area

2. **Add Text Overlays**:
   - Stats file: `stream_data/stats.txt`
   - Update every battle with win rate, episode count

3. **Scene Transitions**:
   - Fade between battles
   - "Next Battle" overlay during delay

### Stats Tracker

`metamon/streaming/stats_tracker.py`:

```python
"""Track training statistics for stream overlays"""
import json
import os

class StatsTracker:
    def __init__(self, output_file: str = "stream_data/stats.txt"):
        self.output_file = output_file
        self.stats = {
            "total_battles": 0,
            "wins": 0,
            "losses": 0,
            "current_streak": 0,
            "best_streak": 0,
        }
        
    def update(self, won: bool):
        """Update stats after a battle"""
        self.stats["total_battles"] += 1
        
        if won:
            self.stats["wins"] += 1
            self.stats["current_streak"] += 1
            self.stats["best_streak"] = max(
                self.stats["best_streak"], 
                self.stats["current_streak"]
            )
        else:
            self.stats["losses"] += 1
            self.stats["current_streak"] = 0
        
        self.save()
    
    def save(self):
        """Save stats to file for OBS text source"""
        win_rate = (self.stats["wins"] / self.stats["total_battles"] * 100 
                   if self.stats["total_battles"] > 0 else 0)
        
        text = f"""
╔══════════════════════════════════╗
║     LASS TRAINING STATS          ║
╠══════════════════════════════════╣
║  Battles: {self.stats['total_battles']:>4}                   ║
║  Win Rate: {win_rate:>5.1f}%                ║
║  Record: {self.stats['wins']:>3}W - {self.stats['losses']:>3}L          ║
║  Current Streak: {self.stats['current_streak']:>3}           ║
║  Best Streak: {self.stats['best_streak']:>3}              ║
╚══════════════════════════════════╝
"""
        
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            f.write(text)
```

---

## Step 4: Complete Training Stream (Week 4)

### All-in-One Script

`metamon/streaming/training_stream.py`:

```python
"""Complete 24/7 training livestream setup"""
import os
import threading
import time
from metamon.env import QueueOnLocalLadder, get_metamon_teams
from metamon.rl.pretrained import get_pretrained_model
from metamon.streaming.stats_tracker import StatsTracker
from metamon.streaming.replay_viewer import ReplayViewer

def training_loop(
    battle_format: str = "gen1ou",
    total_battles: int = 10000,
    output_dir: str = "./stream_data"
):
    """Run training loop with replay generation"""
    
    # Load pretrained agent
    pretrained = get_pretrained_model("SyntheticRLV2")
    agent = pretrained.initialize_agent()
    
    # Create environment
    env = QueueOnLocalLadder(
        battle_format=battle_format,
        num_battles=total_battles,
        observation_space=pretrained.observation_space,
        action_space=pretrained.action_space,
        reward_function=pretrained.reward_function,
        player_team_set=get_metamon_teams(battle_format, "competitive"),
        player_username="Lass",
        save_trajectories_to=output_dir,
        battle_backend="metamon",
    )
    
    # Stats tracker
    stats = StatsTracker(os.path.join(output_dir, "stats.txt"))
    
    # Training loop
    for episode in range(total_battles):
        state, info = env.reset()
        done = False
        
        while not done:
            # Agent selects action (you can use pretrained or your own)
            action = env.action_space.sample()  # Replace with agent.act(state)
            state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        
        # Update stats
        stats.update(info["won"])
        print(f"Battle {episode + 1}/{total_battles} - Win: {info['won']}")

if __name__ == "__main__":
    # Start training in background thread
    training_thread = threading.Thread(
        target=training_loop,
        kwargs={"total_battles": 10000, "output_dir": "./stream_data"}
    )
    training_thread.daemon = True
    training_thread.start()
    
    # Start replay viewer in main thread
    time.sleep(10)  # Wait for first battle
    viewer = ReplayViewer(
        replay_dir="./stream_data/gen1ou/html_replays",
        speed=1.5,
        delay=5
    )
    
    try:
        viewer.start()
        viewer.watch_directory()
    except KeyboardInterrupt:
        print("Stopping stream...")
    finally:
        viewer.stop()
```

### Run the Full Stream

```bash
# Terminal 1: Start Showdown
cd server/pokemon-showdown
node pokemon-showdown start --no-security

# Terminal 2: Start training + viewer
python -m metamon.streaming.training_stream
```

---

## Pro Tips

### Better Replay Detection
Instead of time.sleep, detect when replay completes:

```python
# In replay_viewer.py
def wait_for_replay_complete(self):
    """Poll for replay completion"""
    while True:
        # Check if battle log has "winner" message
        is_complete = self.page.evaluate("""
            () => {
                const log = document.querySelector('.battle-log');
                return log && log.textContent.includes('won the battle');
            }
        """)
        if is_complete:
            break
        time.sleep(1)
```

### Multiple Formats
Train different agents for Gen1-4 simultaneously:

```python
# Rotate between formats
formats = ["gen1ou", "gen2ou", "gen3ou", "gen4ou"]
for fmt in formats:
    run_battles(battle_format=fmt, count=10)
```

### Twitch Chat Integration

```bash
pip install twitchio

# Add chat commands:
# !stats - Show win rate
# !team - Display current team
# !replay - Link to last replay
```

---

## Production Checklist

- [ ] HTML replays auto-generate after battles
- [ ] Viewer auto-plays replays sequentially
- [ ] OBS captures viewer browser window
- [ ] Stats overlay updates in real-time
- [ ] Training loop runs continuously
- [ ] Error handling & auto-restart
- [ ] 24hr+ uptime test passed

---

## Next Level Ideas

1. **Team Rotation**: Switch teams every 100 battles
2. **Opponent Variety**: Cycle through different baselines
3. **Live Ladder**: Stream ladder climbing instead of baselines
4. **Commentary Bot**: LLM-powered play-by-play via TTS
5. **Viewer Challenges**: Twitch integration for viewers to battle Lass
6. **Meta Tracking**: Visualize most-used Pokemon/moves over time
7. **Multi-Gen Tournament**: Round-robin across all generations

---

## Troubleshooting

**HTML replays not generating?**
- Check: Is `save_trajectories_to` set?
- Check: Does `metamon/streaming/` exist?
- Check: Battle logs accessible via `battle.get_showdown_log()`?

**Viewer not auto-advancing?**
- Increase `time.sleep()` duration for battle completion
- Add JS detection for "winner" message
- Check file watcher polling interval

**OBS capture flickering?**
- Use Window Capture instead of Browser Source
- Disable hardware acceleration in browser
- Lock browser window size

---

**You're ready to build! Start with Step 1 and iterate from there.**
