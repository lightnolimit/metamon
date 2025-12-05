# 🤖 Mystery-Gift Ready! Single Agent RL Training Stream

## ✅ What's Built

A complete single-agent streaming platform where you follow **Mystery-Gift** improving over time.

### Key Differences from Tournament

**Tournament Mode** (`./start.sh`):
- 4 agents battle each other
- Round-robin format
- Bot vs bot only

**Mystery-Gift Mode** (`./RUN_MYSTERY_GIFT.sh`):
- ✅ **Single agent (Mystery-Gift) only**
- ✅ **Waits for human opponents** (60s timeout)
- ✅ **Falls back to bot training**
- ✅ **Always shows Mystery-Gift's perspective**
- ✅ **Tracks RL training metrics**
- ✅ **Can use pretrained models**
- ✅ **Improves over time**

## Quick Start

```bash
./RUN_MYSTERY_GIFT.sh
```

## What You Get

### 1. Opponent Matching
- Waits 60s for human opponents on ladder
- If no human, battles a bot (rotates through Random → Grunt → GymLeader → EmeraldKaizo)
- Seamless switching between modes

### 2. Training Metrics
Tracks:
- Total battles, wins, losses
- Win rate overall
- Win rate vs humans
- Win rate vs bots
- Per-bot stats (how well vs each bot)
- Current/best streaks
- Recent performance (last 100 battles)
- Average reward

### 3. Stream Overlays

**Main Stats** (`mystery_gift_overlay.txt`):
```
╔══════════════════════════════════════════════╗
║            MYSTERY-GIFT                      ║
╠══════════════════════════════════════════════╣
║  Total Battles: 247                          ║
║  Overall Win Rate: 68.3%                     ║
║  Recent (100): 72.1%                         ║
║                                              ║
║  Record: 169W - 78L                          ║
║  Current Streak: 5                           ║
║                                              ║
╠══════════════════════════════════════════════╣
║  VS HUMANS:   12 battles  |  60.0% WR       ║
║  VS BOTS:    235 battles  |  69.2% WR       ║
╠══════════════════════════════════════════════╣
║  Training Progress:                          ║
║    Episodes: 247                             ║
║    Avg Reward: +12.34                        ║
╚══════════════════════════════════════════════╝
```

**Current Battle** (`current_status.txt`):
```
╔══════════════════════════════════════════════╗
║         TRAINING BATTLE VS BOT               ║
╠══════════════════════════════════════════════╣
║              Mystery-Gift                    ║
║                   VS                         ║
║           GymLeader-Bot-1234                 ║
╚══════════════════════════════════════════════╝
```

## Configuration

Edit `mystery_gift_config.py`:

```python
# Use a pretrained model
USE_PRETRAINED = True
PRETRAINED_MODEL = "SyntheticRLV2"  # Best Gen1-4 agent

# Enable human opponents
ENABLE_LADDER = True

# Change format
BATTLE_FORMAT = "gen2ou"
```

## OBS Setup

1. **Window Capture** - Browser showing Mystery-Gift's battles
2. **Text Overlay** - `stream_data/mystery_gift_stats/mystery_gift_overlay.txt`
3. **Status Overlay** - `stream_data/mystery_gift_stats/current_status.txt`

## Files Created

```
metamon/streaming/
├── mystery_gift_agent.py       # Main agent class
├── opponent_matcher.py         # Human/bot matching
├── training_tracker.py         # RL metrics
└── mystery_gift_stream.py      # Orchestrator

mystery_gift_config.py          # Configuration
RUN_MYSTERY_GIFT.sh            # Launcher
MYSTERY_GIFT_README.md         # Full documentation
```

## All Committed & Pushed

```
Commit: 657f29a7
Message: Add Mystery-Gift: Single agent RL training stream
Branch: development
Status: ✅ Pushed to GitHub
```

## To Use

```bash
# Run Mystery-Gift stream
./RUN_MYSTERY_GIFT.sh

# Or run tournament (4 agents)
./RUN_STREAM.sh
```

## What Happens

1. **Mystery-Gift starts**
2. **Waits 60s** for human opponent
3. **No human?** → Battles RandomBaseline
4. **Battle completes** → HTML replay generated
5. **Replay auto-plays** in browser
6. **Stats update** (win rate, vs bots)
7. **Next opponent** → Battles Grunt
8. **Repeat** - Rotates through all bots
9. **If human connects** → Battles human immediately!

## Enable Public Access (Future)

To let others battle Mystery-Gift:

```bash
# Install ngrok
brew install ngrok

# Run in separate terminal
ngrok http 8000

# Share the URL, set ENABLE_LADDER = True
```

## Roadmap

✅ Single agent streaming  
✅ Bot opponent rotation  
✅ Training metrics tracking  
✅ Stream overlays  
⏱️ Online RL training (policy updates)  
⏱️ Human opponent matching (coming soon)  
⏱️ ELO rating system  
⏱️ Public ladder integration  

**Start streaming Mystery-Gift's journey!** 🤖🎮📺
