# 🎮 START YOUR 24/7 POKEMON TOURNAMENT STREAM

## ⚡ One Command to Rule Them All

```bash
./RUN_STREAM.sh
```

That's it! This will:
1. ✅ Start Pokemon Showdown server (if not running)
2. ✅ Launch tournament (4 agents, round-robin, best of 3)
3. ✅ Open browser with auto-playing replays
4. ✅ Generate stats overlays for OBS
5. ✅ Loop forever (Ctrl+C to stop)

---

## 🎯 What You'll See

**A browser window will open automatically** showing Pokemon battles playing one after another.

- Battle 1 plays → Finished → Brief pause → Battle 2 starts
- Stats update after each battle
- Infinite loop (round-robin tournament repeats forever)

**Point OBS at the browser window and you're streaming!**

---

## 🎬 OBS Quick Setup

### Method 1: Window Capture (Easiest)
1. OBS → Sources → Add → **Window Capture**
2. Window: Select **Chromium** browser
3. Done! The battles will stream automatically

### Method 2: With Stats Overlays
**Add Current Matchup:**
1. Sources → Add → **Text (GDI+)**
2. Check ☑ **Read from file**
3. Check ☑ **Chatlog mode**
4. File: `stream_data/tournament_stats/current_matchup.txt`

**Add Tournament Standings:**
1. Same as above
2. File: `stream_data/tournament_stats/tournament_standings.txt`

---

## ⚙️ Customize Tournament

Edit `stream_config.py`:

```python
# Change Pokemon generation
BATTLE_FORMAT = "gen2ou"  # gen1ou, gen2ou, gen3ou, gen4ou

# Change battles per matchup
BATTLES_PER_MATCHUP = 5  # Best of 5

# Add/remove agents
TOURNAMENT_AGENTS = [
    TournamentAgent(
        name="YourBot",
        agent_type="baseline",
        agent_config={"baseline_name": "GymLeader"},
        team_set="competitive",
    ),
    # Add more agents here...
]
```

**Available Baselines:**
- `RandomBaseline` - Random moves
- `Grunt` - Max damage heuristic
- `GymLeader` - Smart offensive AI
- `EmeraldKaizo` - Very strong AI
- `Gen1BossAI` - Pokemon Red/Blue AI

**Available Team Sets:**
- `competitive` - High-quality Smogon teams
- `modern_replays` - Diverse predicted teams
- `modern_replays_v2` - Latest predicted teams

---

## 🛠️ Troubleshooting

### "FileNotFoundError: tournament.log"
**Fixed!** The script now auto-creates all needed directories.

### "Browser doesn't open"
Install Playwright:
```bash
pip install -r streaming_requirements.txt
playwright install chromium
```

### "No battles starting"
Check logs:
```bash
tail -f stream_data/tournament.log
tail -f showdown.log
```

### "Port 8000 already in use"
That's fine! The script detects running server and uses it.

### "METAMON_CACHE_DIR not set"
The `RUN_STREAM.sh` script sets this automatically.
To set manually:
```bash
export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache
```

---

## 📊 Output Files

```
stream_data/
├── gen1ou/
│   ├── *.json.lz4                    # RL training data
│   └── html_replays/
│       ├── battle-000001.html        # Viewable in browser
│       ├── battle-000002.html
│       └── ...
│
├── tournament_stats/
│   ├── current_matchup.txt           # OBS overlay
│   ├── tournament_standings.txt      # OBS overlay
│   ├── tournament_data.json          # Raw tournament data
│   ├── Lass_stats.json               # Per-agent stats
│   ├── Scout_stats.json
│   ├── Ace_stats.json
│   └── Rookie_stats.json
│
└── tournament.log                    # Full activity log
```

---

## 🎮 Default Tournament

**Format:** Gen 1 OU (Kanto Pokemon, Original 151)

**Participants:**
- **Lass** - GymLeader AI (smart offensive)
- **Scout** - Grunt AI (max damage)
- **Ace** - EmeraldKaizo AI (very strong)
- **Rookie** - RandomBaseline (beginner)

**Mode:** Round-robin (everyone battles everyone)
**Battles:** Best of 3 per matchup
**Loop:** Infinite (starts over after each round)
**Teams:** Competitive Smogon sample teams

---

## 🔧 Advanced Usage

### Run Without Viewer (Generate Replays Only)
Edit `stream_config.py`:
```python
# In start_tournament_stream() call
start_viewer=False
```

### View Replays Manually Later
```bash
python -m metamon.streaming.replay_viewer \
    --replay_dir stream_data/gen1ou/html_replays \
    --delay 3
```

### Run Multiple Formats Simultaneously
```bash
# Terminal 1: Gen 1
BATTLE_FORMAT=gen1ou ./RUN_STREAM.sh

# Terminal 2: Gen 2 (need to change Showdown port first)
BATTLE_FORMAT=gen2ou ./RUN_STREAM.sh
```

---

## 📖 Documentation

- **This file** - Quick start guide
- **STREAMING_README.md** - Complete documentation
- **SETUP_COMPLETE.md** - Architecture & how it works
- **stream_config.py** - All configuration options

---

## 🎥 Ready to Stream!

```bash
./RUN_STREAM.sh
```

1. Browser opens with battles ✓
2. Point OBS at browser window ✓
3. Add stats overlays (optional) ✓
4. Go live on Twitch/YouTube! ✓

**Press Ctrl+C to stop**

---

## ✨ Features

✅ Auto-playing replays (no manual clicking)  
✅ Tournament mode (4+ agents battling)  
✅ Stats tracking (win rates, streaks, standings)  
✅ OBS-ready overlays (text files auto-update)  
✅ Infinite loop (24/7 streaming ready)  
✅ Full RL training data (JSON trajectories)  
✅ HTML replays (share/download individual battles)  

---

**Enjoy your 24/7 Pokemon tournament stream!** 🎮📺
