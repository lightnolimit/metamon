# Mystery-Gift: 24/7 RL Training Stream

## What Is This?

Instead of a tournament, stream follows **one agent** (Mystery-Gift) improving over time:
- ✅ Battles human opponents when available
- ✅ Trains against bots otherwise
- ✅ Tracks RL training metrics
- ✅ Shows improvement over time
- ✅ Fully automated 24/7 stream

## Quick Start

```bash
./RUN_MYSTERY_GIFT.sh
```

## What Happens

```
1. Mystery-Gift waits for human opponent (60s)
   ↓
2a. Human found → Battle human
   OR
2b. No human → Battle bot (Random, Grunt, GymLeader, or EmeraldKaizo)
   ↓
3. Battle completes → Save replay + update stats
   ↓
4. Replay auto-plays in browser
   ↓
5. Stats overlay updates (win rate, vs humans, vs bots)
   ↓
6. Repeat from step 1
```

## Configuration

Edit `mystery_gift_config.py`:

```python
# Battle format
BATTLE_FORMAT = "gen1ou"  # gen1ou, gen2ou, gen3ou, gen4ou

# Team set
TEAM_SET = "competitive"  # or "modern_replays"

# Enable human opponents
ENABLE_LADDER = True  # Set to True when ready for humans

# Use pretrained model (requires AMAGO)
USE_PRETRAINED = True
PRETRAINED_MODEL = "SyntheticRLV2"
```

## Stream Overlays

**Mystery-Gift Stats** (`stream_data/mystery_gift_stats/mystery_gift_overlay.txt`):
```
╔══════════════════════════════════════════════════════╗
║                   MYSTERY-GIFT                       ║
╠══════════════════════════════════════════════════════╣
║  Total Battles: 1,247                                ║
║  Overall Win Rate: 68.3%                             ║
║  Recent (100): 72.1%                                 ║
║                                                      ║
║  Record: 850W - 397L                                 ║
║  Current Streak: 5                                   ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  VS HUMANS:   42 battles  |  60.0% win rate         ║
║  VS BOTS:  1,205 battles  |  68.9% win rate         ║
╠══════════════════════════════════════════════════════╣
║  Training Progress:                                  ║
║    Episodes: 1,247                                   ║
║    Avg Reward: +12.34                                ║
╚══════════════════════════════════════════════════════╝
```

**Current Status** (`stream_data/mystery_gift_stats/current_status.txt`):
```
╔══════════════════════════════════════════════════════╗
║              BATTLE VS HUMAN OPPONENT                ║
╠══════════════════════════════════════════════════════╣
║                   Mystery-Gift                       ║
║                       VS                             ║
║                  CoolPlayer123                       ║
╚══════════════════════════════════════════════════════╝
```

## OBS Setup

### 1. Window Capture
- Sources → Window Capture
- Select: Chromium browser
- Shows all of Mystery-Gift's battles

### 2. Stats Overlay
- Sources → Text (GDI+)
- Read from file: `stream_data/mystery_gift_stats/mystery_gift_overlay.txt`
- Enable "Chatlog mode"

### 3. Current Battle Overlay
- Sources → Text (GDI+)
- Read from file: `stream_data/mystery_gift_stats/current_status.txt`
- Enable "Chatlog mode"

## Differences from Tournament Mode

### Tournament Mode (`./start.sh`)
- Multiple agents battle each other
- Round-robin format
- All matches are bot vs bot
- Shows different perspectives

### Mystery-Gift Mode (`./RUN_MYSTERY_GIFT.sh`)
- **Single agent (Mystery-Gift) only**
- Waits for human opponents
- Falls back to training vs bots
- **Always shows Mystery-Gift's perspective**
- Tracks RL training metrics
- Can improve over time

## Enable Human Opponents

### Option 1: Local Network
1. Find your local IP: `ifconfig | grep "inet "`
2. Share IP with friends: `192.168.1.X:8000`
3. They connect via browser to your Showdown server
4. They challenge "Mystery-Gift"

### Option 2: Public Internet (Advanced)

**Using ngrok:**
```bash
# Install ngrok
brew install ngrok  # macOS

# Expose Showdown server
ngrok http 8000
```

Copy the public URL (e.g., `https://abc123.ngrok.io`) and share it!

**Using port forwarding:**
- Configure router to forward port 8000
- Share your public IP

## RL Training Integration (Future)

Full online RL training coming soon:

```python
# In mystery_gift_config.py
ENABLE_ONLINE_TRAINING = True
TRAINING_UPDATE_FREQUENCY = 100  # Update policy every 100 battles

# Mystery-Gift will:
# 1. Collect battle trajectories
# 2. Train RL policy on experiences
# 3. Update behavior every 100 battles
# 4. Get progressively better
```

## Files Generated

```
stream_data/
├── gen1ou/
│   ├── *.json.lz4 (RL training data)
│   └── html_replays/
│       ├── battle-000001.html
│       └── ...
│
├── mystery_gift_stats/
│   ├── training_metrics.json
│   ├── mystery_gift_overlay.txt (OBS)
│   └── current_status.txt (OBS)
│
└── mystery_gift.log
```

## Bot Opponent Rotation

Mystery-Gift fights bots in this order:
1. **RandomBaseline** - Warmup (random moves)
2. **Grunt** - Basic offensive (max damage)
3. **GymLeader** - Smart player (healing, boosts)
4. **EmeraldKaizo** - Very strong AI

After battle 4, rotates back to #1. Occasionally randomizes for variety.

## Troubleshooting

**"Too many open files"**
- Fixed! Environments now close properly with `purge=True`

**"No humans connecting"**
- Make sure `ENABLE_LADDER = True`
- Share your server URL with friends
- Or run in bot-only mode for testing

**Browser doesn't auto-play**
- Fixed! Auto-clicks play button and waits for completion

## Next Steps

1. **Test bot-only mode**: `./RUN_MYSTERY_GIFT.sh`
2. **Verify replays work**: Check browser window
3. **Set up OBS**: Add stat overlays
4. **Enable ladder**: Edit `mystery_gift_config.py`
5. **Go live**: Stream Mystery-Gift's journey!

## Future Features

- [ ] Full online RL training
- [ ] Policy updates every N battles
- [ ] ELO rating system
- [ ] Win rate graphs over time
- [ ] Best battle highlights
- [ ] Twitch chat integration
- [ ] Team rotation/selection
- [ ] Meta analysis

---

**Run `./RUN_MYSTERY_GIFT.sh` to start streaming!** 🤖🎮
