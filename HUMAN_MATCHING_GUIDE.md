# Human Opponent Matching Guide for Mystery-Gift

This guide explains how to connect as a human opponent and battle against Mystery-Gift in real-time.

## Quick Start

### 1. Start Mystery-Gift with Ladder Enabled

```bash
./RUN_MYSTERY_GIFT.sh --ladder
```

Or edit `mystery_gift_config.py` and set `ENABLE_LADDER = True`.

### 2. Connect to Local Pokemon Showdown

- **DO NOT** connect to the public Pokemon Showdown website
- Open your browser and go to: `http://localhost:8000`
- This is your local Pokemon Showdown server

### 3. Create Your Team

1. Click "Teambuilder" in the local server
2. Create a **Gen 1 OU** team (Standard format with original 151 Pokemon)
3. Save your team

### 4. Queue for Battle

1. Go back to the main page
2. Click "Find a battle" or use the format dropdown
3. Select **"Gen 1 OU"** format
4. Click "Start searching"

### 5. Wait for Match

Mystery-Gift will automatically find you during its 90-second search intervals. When matched:
- You'll see the battle start automatically
- Battle will play out with Mystery-Gift's AI decisions
- Result will be recorded in the agent's training data

## Detailed Setup

### Server Requirements

The local Pokemon Showdown server must be running:

```bash
cd server/pokemon-showdown
npm install  # Only needed once
npm start
```

The server runs on `http://localhost:8000` by default.

### Team Format Requirements

- **Format**: Gen 1 OU (RBY OU)
- **Allowed Pokemon**: Original 151 Pokemon
- **Clauses**: Standard OU clauses (no Ubers, no OHKO moves, etc.)
- **Team Size**: 6 Pokemon
- **Items**: None (Gen 1 has no items)

### What Mystery-Gift Does

When ladder is enabled, Mystery-Gift:
1. Searches for human opponents during 90-second intervals
2. Uses usernames like "Mystery-Gift-Search-1234"
3. Accepts incoming challenges automatically
4. Falls back to bot opponents if no humans found

### Battle Process

1. **Match Found**: Battle starts automatically
2. **Mystery-Gift Plays**: Agent makes its own moves
3. **No Human Input**: You watch the AI battle
4. **Result Recorded**: Win/loss affects training data
5. **Next Search**: Agent searches for next opponent

## Troubleshooting

### "Not finding any opponents"

- Check that Mystery-Gift is running with `--ladder` flag
- Ensure you're connected to `http://localhost:8000`, not public showdown
- Verify you're queuing in "Gen 1 OU" format
- Wait up to 90 seconds for the search cycle

### "Server not running"

```bash
cd server/pokemon-showdown
npm start
```

If port 8000 is in use:
```bash
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
```

### "Can't connect to localhost:8000"

- Check if local server is running
- Try `http://127.0.0.1:8000` instead
- Ensure firewall allows localhost connections

### "Format not compatible"

- Mystery-Gift plays Gen 1 OU by default
- Edit `BATTLE_FORMAT` in `mystery_gift_config.py` if you want different format
- Both you and agent must use same format

### Still not connecting?

Check the Mystery-Gift logs:
```bash
tail -f stream_data/mystery_gift.log
```

Look for:
- "Ladder enabled: True"
- "Searching for human opponents..."
- "Found human opponent:"

## Advanced Options

### Change Battle Format

Edit `mystery_gift_config.py`:
```python
BATTLE_FORMAT = "gen2ou"  # Gen 2 OU
BATTLE_FORMAT = "gen3ou"  # Gen 3 OU
# etc.
```

### Set Wait Time

Edit `mystery_gift_config.py`:
```python
HUMAN_WAIT_TIMEOUT = 120  # Wait 2 minutes for humans
```

### Multiple Human Opponents

The system supports multiple humans:
- Multiple humans can queue simultaneously
- Mystery-Gift will match with whoever is available first
- Each human gets a separate battle

## Privacy and Data

- Your battles are saved locally in `stream_data/`
- No data is sent to external servers
- Teams and moves are recorded for training purposes
- All data stays on your local machine

## Tips for Better Battles

1. **Use Standard Teams**: Competitive OU teams provide better training
2. **Vary Playstyles**: Different team compositions help agent learn
3. **Stay Connected**: Keep your browser open during search periods
4. **Watch replays**: Check `stream_data/*/html_replays/` for battle recordings

## Need Help?

If you encounter issues:

1. Check the logs: `stream_data/mystery_gift.log`
2. Verify server is running on port 8000
3. Ensure you're using local Pokemon Showdown
4. Confirm format compatibility

The system is designed for local testing and training. Human opponents help the agent learn real battling strategies beyond bot opponents.