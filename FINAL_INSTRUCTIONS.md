# ✅ ALL SET! Final Instructions

## Everything is Ready!

All code has been built and tested. The streaming system is complete and working.

## Quick Start (3 Commands)

```bash
# 1. Set environment variable (add to ~/.bashrc or ~/.zshrc to make permanent)
export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache

# 2. Start the stream
./start.sh

# 3. Point OBS at the browser window that opens
```

That's it!

## What Will Happen

1. **Start script runs** - Checks dependencies, starts Showdown server
2. **Tournament begins** - Round-robin battles between 4 agents
3.  **Browser opens** - Shows battles automatically, one after another
4. **Stats update** - Win rates and standings refresh in real-time
5. **Stream!** - Capture browser window in OBS

## To Make METAMON_CACHE_DIR Permanent

Add to your shell config file:

```bash
# For bash
echo 'export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache' >> ~/.bashrc

# For zsh (macOS default)
echo 'export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache' >> ~/.zshrc
```

Then restart your terminal or run: `source ~/.zshrc`

## Files You Can Edit

**stream_config.py** - Tournament configuration:
- Change format (gen1ou → gen2ou, etc.)
- Add/remove agents
- Adjust battles per matchup
- Change team sets

## OBS Setup Guide

### 1. Add Window Capture
- Sources → Add → Window Capture
- Window: Select the Chromium browser
- Crop to battle area

### 2. Add Text Overlays (Optional)
- Sources → Add → Text (GDI+)  
- Check "Read from file"
- Check "Chatlog mode"

**Current Matchup overlay:**
- File: `stream_data/tournament_stats/current_matchup.txt`

**Tournament Standings overlay:**
- File: `stream_data/tournament_stats/tournament_standings.txt`

## Troubleshooting

### "METAMON_CACHE_DIR not set"
```bash
export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache
```

### "Port 8000 already in use"
Showdown is already running. That's fine - the script will detect it.

### "No browser window opens"
Make sure Playwright is installed:
```bash
pip install -r streaming_requirements.txt
playwright install chromium
```

### "No battles happening"
Check the logs:
```bash
tail -f stream_data/tournament.log
tail -f showdown.log
```

##Files Generated

```
stream_data/
├── gen1ou/
│   ├── *.json.lz4           # Training data
│   └── html_replays/
│       └── battle-*.html    # For viewing/OBS
└── tournament_stats/
    ├── current_matchup.txt      # OBS overlay
    ├── tournament_standings.txt # OBS overlay
    └── *.json                   # Stats data
```

## Documentation

- **START_HERE.md** - Quick overview
- **STREAMING_README.md** - Complete guide  
- **SETUP_COMPLETE.md** - Architecture deep dive
- **stream_config.py** - Configuration options

## Ready to Go!

```bash
export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache
./start.sh
```

Enjoy your 24/7 Pokemon tournament stream! 🎮📺
