# 🎉 24/7 Tournament Streaming - Setup Complete!

## What Was Built

A complete 24/7 Pokemon battle streaming system with:

✅ **HTML Replay Generation** - Automatic conversion of battles to viewable HTML files  
✅ **Sequential Replay Viewer** - Playwright-based auto-player for OBS capture  
✅ **Tournament Manager** - Round-robin battles between multiple agents  
✅ **Stats Tracking** - Win rates, streaks, and leaderboards  
✅ **OBS-Ready Overlays** - Text files for current matchup and standings  
✅ **One-Command Startup** - `./start.sh` launches everything  

## File Tree

```
metamon/
├── metamon/
│   └── streaming/              ← NEW: Complete streaming system
│       ├── __init__.py
│       ├── replay_saver.py     # HTML generation from battle logs
│       ├── replay_viewer.py    # Playwright auto-viewer
│       ├── stats_tracker.py    # Tournament stats & overlays
│       ├── tournament_manager.py # Round-robin orchestration
│       └── training_stream.py  # Main coordinator
│
├── stream_config.py            ← NEW: Tournament configuration
├── start.sh                    ← NEW: One-command launcher
├── streaming_requirements.txt  ← NEW: Additional dependencies
├── test_streaming.py           ← NEW: Verify installation
│
├── STREAMING_README.md         ← NEW: Complete documentation
├── INSTALL_STREAMING.md        ← NEW: Installation guide
└── SETUP_COMPLETE.md          ← NEW: This file
```

## Quick Start (3 Steps)

### 1. Install Everything

```bash
# Install metamon and dependencies
pip install -e .

# Install streaming dependencies
pip install -r streaming_requirements.txt
playwright install chromium

# Install Pokemon Showdown
cd server/pokemon-showdown
npm install
cd ../..
```

### 2. Test Installation

```bash
python3 test_streaming.py
```

Should output: `✓ Core streaming system ready!`

### 3. Start Streaming!

```bash
./start.sh
```

That's it! A browser window will open showing battles. Point OBS at it.

## What Happens When You Run `./start.sh`

```
1. Checks dependencies ✓
2. Starts Pokemon Showdown server (port 8000) ✓
3. Loads tournament config (stream_config.py) ✓
4. Starts round-robin battles ✓
5. Opens browser with auto-playing replays ✓
6. Updates stats files for OBS overlays ✓
```

## How It Works

### Battle Flow

```
1. Tournament Manager picks next matchup
   ↓
2. Creates battle environment with both agents
   ↓
3. Battle executes on Showdown server
   ↓
4. On completion:
   - Saves JSON trajectory (.json.lz4)
   - Generates HTML replay (.html)
   - Updates tournament stats
   ↓
5. Replay Viewer detects new HTML file
   ↓
6. Opens replay in browser (auto-plays)
   ↓
7. OBS captures browser window
   ↓
8. Repeat with next battle
```

### Data Flow

```
Agent 1 vs Agent 2
       ↓
Pokemon Showdown Server (battle simulation)
       ↓
Battle Log (turn-by-turn text)
       ↓
HTML Replay (wrapped with replay-embed.js)
       ↓
Replay Queue (sorted by creation time)
       ↓
Playwright Browser (auto-loads & plays)
       ↓
OBS Window Capture
       ↓
Twitch/YouTube Stream
```

## Files Generated During Streaming

```
stream_data/
├── gen1ou/
│   ├── battle-*.json.lz4           # For RL training
│   └── html_replays/
│       ├── battle-000001.html      # For OBS viewing
│       ├── battle-000002.html
│       └── battle-000003.html
│
├── tournament_stats/
│   ├── current_matchup.txt         # OBS overlay: current battle
│   ├── tournament_standings.txt    # OBS overlay: leaderboard
│   ├── tournament_data.json        # Full data (programmatic access)
│   ├── Lass_stats.json             # Per-agent stats
│   ├── Scout_stats.json
│   ├── Ace_stats.json
│   └── Rookie_stats.json
│
└── tournament.log                  # All activity
```

## Customization

### Change Battle Format

Edit `stream_config.py`:
```python
BATTLE_FORMAT = "gen2ou"  # gen1ou, gen2ou, gen3ou, gen4ou, gen9ou
```

### Add/Remove Agents

Edit `stream_config.py`:
```python
TOURNAMENT_AGENTS = [
    TournamentAgent(
        name="YourAgent",
        agent_type="baseline",
        agent_config={"baseline_name": "GymLeader"},
        team_set="competitive",
    ),
    # Add more...
]
```

### Change Best-of-N

Edit `stream_config.py`:
```python
BATTLES_PER_MATCHUP = 5  # Best of 5
```

## OBS Setup

### Window Capture (Recommended)

1. **Add Source**: Window Capture
2. **Select**: Chromium/Playwright browser window
3. **Crop**: To battle area only (remove browser chrome)

### Text Overlays

1. **Add Source**: Text (FreeType 2)
2. **Enable**: "Read from file"
3. **Enable**: "Chatlog mode" (auto-updates)
4. **File Path**: `stream_data/tournament_stats/current_matchup.txt`

Repeat for `tournament_standings.txt`

### Scene Layout Example

```
┌────────────────────────────────────┐
│  [Window Capture: Battle Viewer]  │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Pokemon Battle Animation    │ │
│  │  (Chromium browser)          │ │
│  └──────────────────────────────┘ │
│                                    │
│  [Text: Current Matchup]          │
│  Lass vs Scout (Gen1OU)           │
│                                    │
│  [Text: Tournament Standings]     │
│  1. Ace     (12-3, 80.0%)         │
│  2. Lass    (10-5, 66.7%)         │
│  3. Scout   (7-8, 46.7%)          │
│  4. Rookie  (1-14, 6.7%)          │
└────────────────────────────────────┘
```

## Advanced Usage

### Run Without Viewer (Headless)

Modify `metamon/streaming/training_stream.py`:
```python
orchestrator = TournamentStreamOrchestrator(
    agents=agents,
    config=config,
    output_dir=output_dir,
    start_viewer=False,  # Disable viewer
)
```

Then manually view replays later:
```bash
python -m metamon.streaming.replay_viewer \
    --replay_dir stream_data/gen1ou/html_replays \
    --delay 3
```

### Use Custom Agents

```python
# your_agent.py
from metamon.baselines.base import Baseline

class MyAgent(Baseline):
    def choose_move(self, battle):
        # Your logic here
        return self.choose_random_move(battle)

# stream_config.py
TournamentAgent(
    name="MyBot",
    agent_type="baseline",
    agent_config={"baseline_name": "MyAgent"},
    team_set="competitive",
)
```

### Multi-Format Tournament

Run multiple instances:
```bash
# Terminal 1
BATTLE_FORMAT=gen1ou ./start.sh

# Terminal 2 (different port for Showdown)
# Edit server/config.js to use port 8001
BATTLE_FORMAT=gen2ou ./start.sh
```

### 24/7 Production Deployment

Use systemd (Linux):
```bash
# See STREAMING_README.md for systemd setup
sudo systemctl start metamon-stream
```

Use PM2 (Node.js process manager):
```bash
pm2 start start.sh --name metamon-stream
pm2 save
pm2 startup
```

Use Docker:
```dockerfile
FROM python:3.10
# ... install dependencies ...
CMD ["./start.sh"]
```

## Troubleshooting

### Browser doesn't open
- Check Playwright installed: `playwright install chromium`
- Check headless=False in `replay_viewer.py`

### No replays appearing
- Check battles completing: `tail -f stream_data/tournament.log`
- Check HTML directory exists: `ls stream_data/gen1ou/html_replays/`
- Check Showdown running: `lsof -i :8000`

### OBS overlays not updating
- Enable "Chatlog mode" in text source
- Check file path is absolute
- Verify files exist: `cat stream_data/tournament_stats/current_matchup.txt`

### Battles too slow/fast
- Edit `metamon/streaming/replay_viewer.py`
- Change `base_duration = 30.0` (seconds)

## Components Overview

### `replay_saver.py`
- Extracts battle logs from poke-env Battle objects
- Wraps logs in HTML template
- Saves to disk atomically

### `replay_viewer.py`
- Launches headless Chromium browser
- Watches directory for new HTML files
- Auto-loads and plays replays sequentially
- CLI: `python -m metamon.streaming.replay_viewer`

### `stats_tracker.py`
- Tracks per-agent win/loss/streaks
- Generates tournament leaderboard
- Writes OBS-ready text files
- Saves JSON for programmatic access

### `tournament_manager.py`
- Generates round-robin matchups
- Manages tournament rounds
- Creates agent instances (baseline or pretrained)
- Shuffles and loops matchups

### `training_stream.py`
- Orchestrates everything
- Runs battles via Metamon environments
- Coordinates viewer and stats
- Handles cleanup and errors

### `stream_config.py`
- User-editable configuration
- Defines tournament participants
- Sets battle format and rules
- Easy to customize without code changes

### `start.sh`
- Checks dependencies
- Starts Pokemon Showdown
- Launches tournament stream
- Handles cleanup on Ctrl+C

## Integration with Existing Metamon

### Modified Files

Only ONE file was modified:
- `metamon/env/wrappers.py` - Added HTML replay generation (20 lines)

All other changes are NEW files in `metamon/streaming/`

### Backward Compatibility

✅ All existing Metamon functionality unchanged  
✅ Streaming is opt-in (only if you use `save_trajectories_to`)  
✅ No breaking changes to environments or interfaces  
✅ Can still use Metamon for RL training as before  

## What You Can Do Now

1. **Stream Gen1-4 Tournaments** - 4 players, round-robin, 24/7
2. **Generate Training Data** - JSON trajectories saved alongside replays
3. **Test New Agents** - Easy to add custom baselines to tournament
4. **Analyze Meta** - Stats show which agents/strategies dominate
5. **Showcase Your Agent** - Stream "Lass" improving over time
6. **Run Multi-Gen Events** - Different tournaments for each generation

## Next Steps

1. **Install dependencies**:
   ```bash
   pip install -e .
   pip install -r streaming_requirements.txt
   playwright install chromium
   cd server/pokemon-showdown && npm install
   ```

2. **Test setup**:
   ```bash
   python3 test_streaming.py
   ```

3. **Start streaming**:
   ```bash
   ./start.sh
   ```

4. **Set up OBS**:
   - Window capture → browser window
   - Text overlays → stats files

5. **Go live on Twitch/YouTube**!

## Documentation

- **STREAMING_README.md** - Complete documentation
- **INSTALL_STREAMING.md** - Installation guide
- **stream_config.py** - Configuration reference
- **test_streaming.py** - Verify setup
- **This file** - Overview & summary

## Support

If you encounter issues:

1. Run `python3 test_streaming.py` to diagnose
2. Check `stream_data/tournament.log` for errors
3. Check `showdown.log` for server issues
4. Verify dependencies with `pip list | grep -E "playwright|metamon"`

## Credits

Built on top of:
- **Metamon** - RL environment and dataset
- **Pokemon Showdown** - Battle simulation
- **Playwright** - Browser automation
- **poke-env** - Python ↔ Showdown bridge

---

**You're ready to stream! Run `./start.sh` to begin.** 🎮📺

Enjoy your 24/7 Pokemon tournament stream!
