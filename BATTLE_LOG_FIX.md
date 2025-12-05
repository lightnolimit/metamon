# ✅ Battle Log Extraction Fixed!

## Problem

HTML replays were being generated but didn't show any battle data:
- Replays loaded in browser
- But showed no turns, moves, or animations  
- Play button did nothing (no battle data to play)
- Only contained player names (57 characters total)

## Root Cause

The `MetamonBackendBattle` object was processing battle messages via the replay parser, but **not storing the raw messages** needed for HTML replay generation.

When we tried to extract the battle log after the battle ended:
```python
battle_log = extract_battle_log_from_battle(battle)
# Result: "|player|p1|MM-xxx|\n|player|p2|MM-yyy|\n|start\n"
# Only 57 characters - missing ALL the actual battle!
```

## Solution

### 1. Added Message Storage to Battle Object

**File**: `metamon/env/metamon_battle.py`

```python
def __init__(self, ...):
    # ... existing code ...
    
    # STREAMING: Store raw battle log for replay generation
    self._raw_battle_log: List[str] = []

def parse_message(self, split_message: List[str]):
    # STREAMING: Save raw message for replay generation
    raw_message = '|'.join(split_message[1:])
    self._raw_battle_log.append(raw_message)
    
    # Then process it normally
    self._sim_protocol.interpret_message(split_message[1:])
```

### 2. Updated Extraction Logic

**File**: `metamon/streaming/replay_saver.py`

```python
def extract_battle_log_from_battle(battle) -> str:
    # Method 1: Check for _raw_battle_log (MetamonBackendBattle)
    if hasattr(battle, '_raw_battle_log'):
        battle_log_lines = battle._raw_battle_log
        # Returns FULL battle: 20,000+ characters
```

## Result

### Before
```
Battle log: 57 characters
|player|p1|MM-xxx|
|player|p2|MM-yyy|
|start
```

HTML replay shows: Empty battle, no turns

### After
```
Battle log: 23,645 characters
|init|battle
|title|MM-xxx vs. MM-yyy
|j|☆MM-xxx
|j|☆MM-yyy
|t:|1764895445
|gametype|singles
|player|p1|MM-xxx|266|
|player|p2|MM-yyy|266|
|gen|1
|tier|[Gen 1] OU
... (hundreds more lines) ...
|move|p1a: Alakazam|Psychic|p2a: Tauros
|-damage|p2a: Tauros|215/353
|move|p2a: Tauros|Body Slam|p1a: Alakazam
... (all turns, moves, damage) ...
|win|MM-xxx
```

HTML replay shows: **Complete battle with all turns and animations!**

## How It Works

```
1. Battle message arrives from Showdown server
   |move|p1a: Alakazam|Psychic|p2a: Tauros
   ↓
2. MetamonPlayer passes to Battle.parse_message()
   ↓
3. Battle saves raw message
   self._raw_battle_log.append("|move|p1a: Alakazam|Psychic|p2a: Tauros")
   ↓
4. Battle processes message with replay parser
   (updates game state, parses effects, etc.)
   ↓
5. At battle end, extract full log
   battle_log = '\n'.join(battle._raw_battle_log)
   ↓
6. Generate HTML with complete battle data
   <script class="battle-log-data">...full log...</script>
   ↓
7. Replay loads and plays correctly!
```

## Testing

Run the debug script:
```bash
export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache
python3 debug_replay.py
```

Output:
```
Extracted battle log: 23,645 characters
Saved test replay to: ./debug_replay/battle-debug-test.html
```

Open the HTML file in a browser - battle now plays correctly!

## Committed & Pushed

```bash
git commit -m "Fix battle log extraction for auto-playing replays"
git push origin development
```

## Now Run the Stream

```bash
./RUN_STREAM.sh
```

Expected behavior:
1. ✅ Browser opens
2. ✅ First replay loads with COMPLETE battle data
3. ✅ Auto-clicks play button
4. ✅ Battle plays out with all turns and animations
5. ✅ Waits for "won the battle" message
6. ✅ Moves to next replay
7. ✅ Repeat forever

All replays will now show the actual battles! 🎮📺
