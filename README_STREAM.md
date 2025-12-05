# 24/7 Pokemon Tournament Stream - READY TO GO!

## Instant Start

```bash
./RUN_STREAM.sh
```

This will:
1. ✅ Start Pokemon Showdown server
2. ✅ Begin tournament battles (4 agents, round-robin)
3. ✅ Open browser window with auto-playing replays
4. ✅ Update stats in real-time

**Then**: Point OBS at the browser window and go live!

---

## What Happens

- **Browser Opens**: Chromium window appears showing Pokemon battles
- **Auto-Play**: Battles play sequentially, one after another
- **Stats Update**: Win rates and standings refresh after each battle
- **Infinite Loop**: Tournament repeats forever (Ctrl+C to stop)

---

## OBS Setup

### Quick Method
1. OBS → Sources → Window Capture
2. Select: Chromium browser window
3. Done!

### With Overlays (Optional)
Add text sources reading from:
- `stream_data/tournament_stats/current_matchup.txt`
- `stream_data/tournament_stats/tournament_standings.txt`

Enable "Chatlog mode" for auto-updates.

---

## Customize

Edit `stream_config.py`:
```python
BATTLE_FORMAT = "gen2ou"  # Change format
BATTLES_PER_MATCHUP = 5   # Best of 5
# Add/remove agents, change teams, etc.
```

---

## Stop Stream

Press `Ctrl+C` in the terminal.

Optional: Stop Showdown server when prompted.

---

## Files Generated

```
stream_data/
├── gen1ou/
│   ├── *.json.lz4           # RL training data
│   └── html_replays/
│       └── battle-*.html    # Viewable replays
└── tournament_stats/
    ├── current_matchup.txt      # OBS overlay
    ├── tournament_standings.txt # OBS overlay
    └── *.json                   # Raw data
```

---

## Troubleshooting

**Browser doesn't open?**
- Check: `pip list | grep playwright`
- Install: `pip install -r streaming_requirements.txt && playwright install chromium`

**No battles starting?**
- Check logs: `tail -f stream_data/tournament.log`
- Check Showdown: `tail -f showdown.log`

**Battles but no replays?**
- Check directory: `ls stream_data/gen1ou/html_replays/`
- HTML files should appear after each battle

---

## That's It!

Run `./RUN_STREAM.sh` and start streaming! 🎮📺

Full docs: `STREAMING_README.md`
