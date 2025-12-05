# Installation Guide: 24/7 Tournament Streaming

## Prerequisites

- Python 3.10+
- Node.js 16+
- Git

## Step-by-Step Installation

### 1. Install Metamon (if not already done)

```bash
cd /path/to/metamon
pip install -e .
```

### 2. Install Pokemon Showdown

```bash
cd server/pokemon-showdown
npm install
cd ../..
```

### 3. Install Streaming Dependencies

```bash
pip install -r streaming_requirements.txt
playwright install chromium
```

### 4. Verify Installation

```bash
python3 test_streaming.py
```

You should see:
```
✓ Core streaming system ready!
```

### 5. Start Streaming!

```bash
./start.sh
```

## What Gets Installed

**Python Packages** (from `streaming_requirements.txt`):
- `playwright` - Browser automation for replay viewing

**Browser**:
- Chromium (via Playwright) - Displays battle replays

**Already Included**:
- All streaming code in `metamon/streaming/`
- Configuration in `stream_config.py`
- Launcher in `start.sh`

## Troubleshooting Installation

### "pip install -e . fails"

Make sure you're in the metamon directory:
```bash
cd /path/to/metamon
pip install -e .
```

If you get dependency errors:
```bash
pip install --upgrade pip
pip install -e . --no-deps
pip install -r streaming_requirements.txt
```

### "npm install fails"

Update npm:
```bash
npm install -g npm@latest
```

Or use a different Node version:
```bash
# Using nvm
nvm install 18
nvm use 18
```

### "playwright install chromium fails"

Try manual installation:
```bash
python3 -m playwright install chromium
```

Or use system Chromium:
```bash
# Edit metamon/streaming/replay_viewer.py
# Change: chromium.launch(...) to chromium.launch(executable_path='/path/to/chrome')
```

### "test_streaming.py fails"

Check each component individually:

```bash
# Test Python version
python3 --version  # Should be 3.10+

# Test metamon
python3 -c "import metamon; print('OK')"

# Test streaming
python3 -c "from metamon.streaming import ReplayViewer; print('OK')"

# Test playwright
python3 -c "import playwright; print('OK')"
```

## Minimal Installation (No Viewer)

If you just want to generate replays without auto-viewing:

```bash
# Install only metamon
pip install -e .

# Skip playwright
# Skip start.sh

# Run battles manually
python3 -c "
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

# Battles will save HTML to stream_data/gen1ou/html_replays/
"
```

Then open HTML files manually in your browser.

## Full Installation Check

```bash
# 1. Check Python
python3 --version

# 2. Check Node
node --version

# 3. Check Metamon
python3 -c "import metamon"

# 4. Check Streaming
python3 -c "from metamon.streaming import ReplayViewer"

# 5. Check Playwright
python3 -c "from playwright.sync_api import sync_playwright"

# 6. Check Showdown
cd server/pokemon-showdown && ls node_modules | wc -l
# Should show many packages

# 7. Run full test
cd ../..
python3 test_streaming.py
```

All checks should pass!

## Next Steps

After successful installation:

1. **Read STREAMING_README.md** for full documentation
2. **Edit stream_config.py** to customize tournament
3. **Run ./start.sh** to begin streaming
4. **Set up OBS** to capture the browser window

Enjoy! 🎮
