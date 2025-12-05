# 🎮 24/7 Pokemon Tournament Streaming - START HERE

## What This Is

A complete system for streaming Pokemon battles to OBS with automatic replay viewing and tournament management.

## Quick Start

```bash
# 1. Install
pip install -e .
pip install -r streaming_requirements.txt
playwright install chromium

# 2. Test
python3 test_streaming.py

# 3. Start!
./start.sh
```

A browser will open with auto-playing battles. Capture it in OBS.

## Configuration

Edit `stream_config.py` to customize:
- Battle format (gen1ou, gen2ou, etc.)
- Tournament participants
- Number of battles per matchup
- Team sets

## Documentation

- **SETUP_COMPLETE.md** - What was built & how it works
- **STREAMING_README.md** - Complete usage guide
- **INSTALL_STREAMING.md** - Installation troubleshooting
- **stream_config.py** - Configuration options

## Files Created

```
metamon/streaming/     # Complete streaming system
stream_config.py       # Tournament configuration
start.sh               # Launch script
test_streaming.py      # Verify setup
```

## What You Get

✅ HTML replay generation  
✅ Auto-playing viewer (Playwright)  
✅ Round-robin tournament mode  
✅ Stats tracking & OBS overlays  
✅ One-command startup  

## Need Help?

1. Run: `python3 test_streaming.py`
2. Check: `INSTALL_STREAMING.md`
3. Read: `STREAMING_README.md`

---

**Ready? Run `./start.sh` to begin streaming!** 🎥
