# Metamon 24/7 Tournament Streaming

Complete setup for streaming Pokemon battles to OBS with automatic replay viewing.

## Quick Start

```bash
# 1. Install streaming dependencies
pip install -r streaming_requirements.txt
playwright install chromium

# 2. Make sure Showdown is set up
cd server/pokemon-showdown
npm install
cd ../..

# 3. Configure your tournament (optional)
# Edit stream_config.py to customize participants

# 4. Start everything!
./start.sh
```

That's it! A browser window will open showing battles automatically. Point OBS at this window.

---

## What Happens When You Run `./start.sh`

1. **Checks dependencies** (Python, Node, Playwright)
2. **Starts Pokemon Showdown server** (localhost:8000)
3. **Loads tournament configuration** (from `stream_config.py`)
4. **Starts tournament battles** (agents battle in round-robin)
5. **Opens replay viewer** (browser window auto-playing replays)
6. **Updates stats** (tournament standings, win rates)

---

## OBS Setup

### Window Capture Method (Recommended)

1. **Add Window Capture Source**:
   - Sources → Add → Window Capture
   - Select the Chromium/Playwright browser window
   - Check "Capture Cursor" if desired

2. **Add Text Overlays**:
   - Sources → Add → Text (FreeType 2)
   - For current matchup: `stream_data/tournament_stats/current_matchup.txt`
   - For standings: `stream_data/tournament_stats/tournament_standings.txt`

3. **Configure Text Source**:
   - Check "Read from file"
   - Check "Chatlog mode" (auto-updates)
   - Choose monospace font (e.g., Courier New)
   - Adjust colors and size

### Browser Source Method (Alternative)

1. **Add Browser Source**:
   - Sources → Add → Browser Source
   - Width: 1280, Height: 720
   - URL: Point to HTML file
   - Check "Refresh browser when scene becomes active"

---

## File Structure

```
stream_data/
├── gen1ou/
│   ├── battle-*.json.lz4        # JSON trajectories (for RL training)
│   └── html_replays/
│       ├── battle-000001.html   # HTML replays (for viewing)
│       ├── battle-000002.html
│       └── ...
└── tournament_stats/
    ├── current_matchup.txt      # Current battle info (for OBS overlay)
    ├── tournament_standings.txt # Leaderboard (for OBS overlay)
    ├── tournament_data.json     # Full tournament data
    ├── Lass_stats.json          # Per-agent stats
    ├── Scout_stats.json
    └── ...
```

---

## Configuration

Edit `stream_config.py` to customize:

### Battle Format
```python
BATTLE_FORMAT = "gen1ou"  # Options: gen1ou, gen2ou, gen3ou, gen4ou, gen9ou
```

### Tournament Settings
```python
BATTLES_PER_MATCHUP = 3   # Best of N
SHUFFLE_MATCHUPS = True    # Randomize order
LOOP_FOREVER = True        # Run indefinitely
```

### Participants

Add/remove agents from `TOURNAMENT_AGENTS` list:

```python
TournamentAgent(
    name="MyAgent",           # Display name
    agent_type="baseline",    # or "pretrained"
    agent_config={
        "baseline_name": "GymLeader"
    },
    team_set="competitive",
)
```

**Available Baselines**:
- `RandomBaseline` - Random moves
- `Grunt` - Max damage
- `GymLeader` - Smart offensive
- `EmeraldKaizo` - Very strong AI
- `BaseRNN` - Simple learned baseline

**Available Team Sets**:
- `competitive` - High-quality Smogon teams
- `modern_replays` - Diverse predicted teams
- `modern_replays_v2` - Latest predicted teams

---

## Using Pretrained RL Agents

To use pretrained models (requires AMAGO):

```bash
# Install AMAGO
pip install amago-rl

# Uncomment pretrained agent in stream_config.py
TournamentAgent(
    name="Champion",
    agent_type="pretrained",
    agent_config={
        "model_name": "SyntheticRLV2",  # Best Gen1-4 agent
        "checkpoint": None,
    },
    team_set="competitive",
)
```

Available pretrained models:
- `SyntheticRLV2` - Best overall (Gen 1-4)
- `SmallRL` - Faster inference
- `Minikazam` - Gen 9 compatible
- See `metamon.rl.pretrained` for full list

---

## Customization

### Change Replay Speed

Edit `metamon/streaming/replay_viewer.py`:

```python
def _estimate_battle_duration(self) -> float:
    base_duration = 30.0  # Change this (seconds)
    return base_duration / self.speed
```

### Change Delay Between Battles

Edit `stream_config.py`:

```python
VIEWER_DELAY = 5  # Seconds between replays
```

### Change Window Size

Edit `stream_config.py`:

```python
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
```

---

## Advanced: Custom Agents

### Create Your Own Baseline

```python
# In your own file
from metamon.baselines.base import Baseline

class MyCustomAgent(Baseline):
    def choose_move(self, battle):
        # Your logic here
        return self.choose_random_move(battle)

# Add to stream_config.py
from my_agents import MyCustomAgent

TournamentAgent(
    name="MyBot",
    agent_type="baseline",
    agent_config={"baseline_name": "MyCustomAgent"},
    team_set="competitive",
)
```

### Manual Replay Viewer

Run replay viewer separately:

```bash
python -m metamon.streaming.replay_viewer \
    --replay_dir stream_data/gen1ou/html_replays \
    --delay 3 \
    --speed 1.5
```

### Manual Battle Execution

```python
from metamon.streaming import start_tournament_stream
from stream_config import get_tournament_agents, get_tournament_config

agents = get_tournament_agents()
config = get_tournament_config()

start_tournament_stream(
    battle_format="gen1ou",
    output_dir="./stream_data",
    agents=agents,
    config=config,
)
```

---

## Troubleshooting

### "Port 8000 already in use"
Pokemon Showdown is already running. Either:
- Use the existing server (it's fine)
- Kill it: `lsof -ti:8000 | xargs kill`

### "Playwright not found"
```bash
pip install playwright
playwright install chromium
```

### "Browser window doesn't open"
Check if running headless. Edit `metamon/streaming/replay_viewer.py`:
```python
self.browser = self.playwright.chromium.launch(
    headless=False,  # Make sure this is False
    ...
)
```

### "No replays appearing"
- Check `stream_data/gen1ou/html_replays/` exists
- Check battles are completing (see terminal output)
- Check `showdown.log` for server errors

### "Stats not updating in OBS"
- Enable "Chatlog mode" in OBS text source
- Make sure file path is correct
- Check file exists: `stream_data/tournament_stats/current_matchup.txt`

### "Battles are too slow"
Edit `metamon/streaming/replay_viewer.py`:
```python
base_duration = 15.0  # Reduce from 30.0
```

Or increase playback speed in `stream_config.py`:
```python
# Not implemented yet, but you can manually edit
viewer = ReplayViewer(..., speed=2.0)
```

---

## Tips for 24/7 Streaming

### Use a VPS or Dedicated Machine
Local machine sleep/restart will interrupt stream.

### Set up systemd (Linux)

Create `/etc/systemd/system/metamon-stream.service`:

```ini
[Unit]
Description=Metamon 24/7 Tournament Stream
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/metamon
ExecStart=/path/to/metamon/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable metamon-stream
sudo systemctl start metamon-stream
```

### Monitor Logs

```bash
# Tournament log
tail -f stream_data/tournament.log

# Showdown server log
tail -f showdown.log
```

### Disk Space Management

HTML replays pile up over time:

```bash
# Delete old replays (keep last 100)
cd stream_data/gen1ou/html_replays
ls -t battle-*.html | tail -n +101 | xargs rm
```

Or add to cron:
```bash
0 * * * * cd /path/to/metamon/stream_data/gen1ou/html_replays && ls -t battle-*.html | tail -n +1000 | xargs rm
```

---

## Architecture

```
┌─────────────────────────────────────┐
│  OBS Studio (Your Stream)          │
│  ┌───────────────────────────────┐ │
│  │ Window Capture                │ │
│  │ ┌─────────────────────────┐   │ │
│  │ │ Chromium Browser        │   │ │
│  │ │ (Auto-playing replays)  │   │ │
│  │ └─────────────────────────┘   │ │
│  ├───────────────────────────────┤ │
│  │ Text: Current Matchup         │ │
│  │ Text: Tournament Standings    │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
              ▲
              │ captures
              │
┌─────────────────────────────────────┐
│  Metamon Streaming System           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Replay Viewer (Playwright)  │   │
│  │ - Auto-loads HTML files     │   │
│  │ - Sequential playback       │   │
│  └─────────────────────────────┘   │
│              ▲                      │
│              │ reads                │
│  ┌─────────────────────────────┐   │
│  │ HTML Replay Queue           │   │
│  │ battle-001.html             │   │
│  │ battle-002.html             │   │
│  └─────────────────────────────┘   │
│              ▲                      │
│              │ generates            │
│  ┌─────────────────────────────┐   │
│  │ Tournament Manager          │   │
│  │ - Round-robin battles       │   │
│  │ - Stats tracking            │   │
│  │ - Replay generation         │   │
│  └─────────────────────────────┘   │
│              ▲                      │
│              │ uses                 │
│  ┌─────────────────────────────┐   │
│  │ Metamon Battle Env          │   │
│  │ - Gym environment           │   │
│  │ - Agent execution           │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
              ▲
              │ connects
              │
┌─────────────────────────────────────┐
│  Pokemon Showdown Server            │
│  - Battle simulation                │
│  - localhost:8000                   │
└─────────────────────────────────────┘
```

---

## What's Next?

**Implemented**:
- ✅ HTML replay generation
- ✅ Auto sequential viewing
- ✅ Tournament mode (round-robin)
- ✅ Stats tracking
- ✅ OBS-ready overlays
- ✅ One-command startup

**Future Ideas**:
- Twitch chat integration
- LLM-powered commentary
- Viewer voting on teams
- Meta analysis dashboards
- Multi-format tournaments
- Self-play training loops

---

Enjoy your 24/7 Pokemon battle stream! 🎮📺
