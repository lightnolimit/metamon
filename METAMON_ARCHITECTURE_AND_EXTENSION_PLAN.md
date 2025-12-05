# Metamon Architecture & 24/7 Livestream Extension Plan

## Project Overview

**Metamon** is a research platform for Pokemon Showdown RL that provides:
- Battle environments (Gymnasium-compatible)
- 1M+ human replay dataset for offline RL
- Pretrained transformer-based RL agents
- Heuristic/IL/RL baselines
- Team prediction & generation
- Replay parsing & reconstruction

**Current State**: You can run battles, train agents, and save replays in JSON format.

**Your Goal**: Create a 24/7 livestream of your RL agent "Lass" training in Gen1 with automatic, seamless battle playback for OBS.

---

## Architecture Deep Dive

### 1. **Battle Flow**
```
Player (You/Agent) → Metamon Environment → Pokemon Showdown Server → Battle Logs → Replays
```

When you run `python -m metamon.env`:
- Creates `BattleAgainstBaseline` environment (metamon/env/wrappers.py:444)
- Spawns 2 players on local Showdown server (localhost:8000)
- Each turn: Agent → Action → UniversalAction → BattleOrder → Showdown
- Battle ends → Replay data saved

### 2. **Replay System**

**Online Battles** (metamon/env/wrappers.py:400-432):
- Saves trajectories as `.json.lz4` files
- Format: `{"states": [...], "actions": [...]}`
- Stored in `save_trajectories_to` directory
- One file per battle

**Showdown's Native Replay System** (server/pokemon-showdown/test/common.js:132-145):
```javascript
function saveReplay(battleStream, file) {
  const battleLog = battle.log.join('\n');
  const html = `<!DOCTYPE html>
<script type="text/plain" class="battle-log-data">${battleLog}</script>
<script src="https://play.pokemonshowdown.com/js/replay-embed.js"></script>`;
  fs.writeFileSync(file, html);
}
```

**This is the HTML format you like!** It creates a standalone HTML file that plays the battle.

### 3. **Key Components**

**Environments** (metamon/env/):
- `BattleAgainstBaseline` - vs built-in AI
- `QueueOnLocalLadder` - vs anyone on local server  
- `PokeAgentLadder` - vs online ladder

**Observation/Action/Reward** (metamon/interface.py):
- `UniversalState` - Full battle state snapshot
- `UniversalAction` - 13 discrete actions (4 moves, 5 switches, 4 tera moves)
- `ObservationSpace` - Converts state → agent input
- `ActionSpace` - Converts agent output → action
- `RewardFunction` - Shaped rewards (+100 win, -100 loss, damage/status shaping)

**Training** (metamon/rl/):
- `train.py` - Train from scratch with AMAGO
- `finetune_from_hf.py` - Finetune pretrained models
- `evaluate.py` - Eval vs baselines/ladder
- `pretrained.py` - 20+ pretrained models (SyntheticRLV2 is best)

**Baselines** (metamon/baselines/):
- `RandomBaseline` - Random legal moves
- `Grunt` - Max damage heuristic
- `GymLeader` - Smarter heuristic
- `EmeraldKaizo` - Advanced rule-based AI
- `BaseRNN` - Simple IL baseline

---

## The Gap: Automatic HTML Replay Generation

**Current Limitation**: Metamon saves JSON trajectories but doesn't automatically generate the HTML replay files you want for streaming.

**The Solution**: Create a pipeline that:
1. Monitors completed battles
2. Converts battle logs to HTML format
3. Auto-opens each replay in sequence for OBS capture

---

## Extension Plan: 24/7 "Lass" Training Livestream

### Phase 1: Replay HTML Generator (CRITICAL)

**File**: `metamon/streaming/replay_generator.py`

```python
# Extract battle logs from Showdown server
# Convert to standalone HTML files
# Pattern: battle-genXou-TIMESTAMP.html
```

**How it works**:
- Hook into Showdown server's battle completion events
- Extract `battle.log` from the battle room
- Wrap in HTML template with `replay-embed.js`
- Save to `replays/` directory

**Alternative**: Modify `metamon/env/wrappers.py:400-432` to save both JSON + HTML when `save_trajectories_to` is set.

### Phase 2: Auto-Replay Viewer

**File**: `metamon/streaming/replay_viewer.py`

```python
# Watch replay directory
# Open each HTML in headless browser (Selenium/Playwright)
# Auto-advance to next battle when complete
# OBS captures the browser window
```

**Features**:
- Sequential replay playback
- Configurable delay between battles
- Battle stats overlay (win rate, episode #, etc.)
- Skip/resume controls

### Phase 3: Training Loop Integration

**File**: `metamon/streaming/training_stream.py`

```python
# Launch RL training in background
# Monitor for completed battles
# Generate HTML replays
# Feed to viewer
# Update stats dashboard
```

**Architecture**:
```
Training Loop → Battles → JSON Trajectories
                    ↓
              Battle Logs → HTML Replays
                    ↓
              Replay Queue → Auto Viewer → OBS
                    ↓
              Stats/Metrics → Dashboard Overlay
```

### Phase 4: OBS Integration

**Components**:
1. **Browser Source** - Captures replay viewer
2. **Text Overlays** - Stats, winrate, elo
3. **Scene Transitions** - Between battles
4. **Chat Bot** - Twitch chat commands (!stats, !team, !replay)

---

## Recommended Implementation Path

### Week 1: Replay HTML Generator

**Goal**: Auto-generate HTML replays from battles

**Tasks**:
1. Create `metamon/streaming/` module
2. Hook battle completion in `wrappers.py`
3. Extract Showdown battle logs
4. Generate HTML with embedded log
5. Test: Run 10 battles → Get 10 HTML files

**Key Files to Modify**:
- `metamon/env/wrappers.py:400-432` (add HTML save)
- New: `metamon/streaming/replay_generator.py`

### Week 2: Sequential Replay Viewer

**Goal**: Auto-play HTML replays in sequence

**Tasks**:
1. Set up Playwright/Selenium headless browser
2. File watcher for new replays
3. Auto-load and play each replay
4. Configurable speed/delay
5. Test: Queue 10 replays → Auto-play all

**New Files**:
- `metamon/streaming/replay_viewer.py`
- `metamon/streaming/replay_queue.py`

### Week 3: Training Integration

**Goal**: Seamless training → viewing pipeline

**Tasks**:
1. Async training loop
2. Real-time replay generation
3. Stats dashboard
4. Win rate tracking
5. Test: 24hr continuous run

**New Files**:
- `metamon/streaming/training_stream.py`
- `metamon/streaming/stats_tracker.py`

### Week 4: OBS & Production Polish

**Goal**: Production-ready stream

**Tasks**:
1. OBS scene setup
2. Overlays and graphics
3. Chat integration
4. Error handling/auto-restart
5. Test: 7-day uptime test

---

## Technical Details: HTML Replay Generation

### Option A: Server-Side Hook (Recommended)

Modify Pokemon Showdown server to auto-save HTML replays:

**File**: `server/pokemon-showdown/server/room-battle.ts`

Add after battle ends (around line 875):
```typescript
// Auto-save HTML replay
const replayHTML = this.generateReplayHTML();
fs.writeFileSync(`replays/${this.roomid}.html`, replayHTML);
```

### Option B: Client-Side Extraction

Hook into `metamon/env/wrappers.py` step function:

```python
def step(self, action):
    # ... existing code ...
    if terminated or truncated:
        # Extract battle log
        battle_log = self.current_battle.battle_log_data
        # Generate HTML
        self.save_replay_html(battle_log, battle_id)
```

### Option C: Post-Battle Processing

Process saved JSON trajectories to reconstruct battle logs:

```python
# metamon/streaming/replay_reconstructor.py
def json_to_html(trajectory_file):
    states = load_trajectory(trajectory_file)
    battle_log = reconstruct_log_from_states(states)
    html = wrap_in_replay_template(battle_log)
    return html
```

**Recommendation**: Option B is easiest - modify `wrappers.py` to save HTML alongside JSON.

---

## Data Flow for Streaming

```
1. Training Loop
   ↓
2. Battle Execution (env.step)
   ↓
3. Battle Completion
   ↓
4. Save Trajectory JSON + HTML Replay
   ↓
5. Replay Queue (FIFO)
   ↓
6. Auto Viewer (Playwright)
   ↓
7. OBS Browser Source
   ↓
8. Twitch/YouTube Stream
```

---

## Tech Stack Recommendations

**Replay Viewing**:
- **Playwright** (preferred) - Better headless browser control
- **Selenium** - More mature but heavier
- **Puppeteer** - Good for Chromium-only

**Dashboard/Overlays**:
- **Flask** - Simple web dashboard for stats
- **React** - For interactive overlays
- **WebSockets** - Real-time stat updates

**Stream Integration**:
- **OBS WebSocket** - Programmatic scene control
- **Streamlabs API** - Alerts and events
- **Twitch API** - Chat bot integration

**Process Management**:
- **systemd** - Linux service for 24/7 uptime
- **PM2** - Node.js process manager
- **Docker** - Containerize entire stack

---

## What You Can Build (Ideas Based on Codebase)

### 1. **Multi-Generation Tournament Stream**
- Train separate agents for Gen1-4
- Round-robin tournament
- Live ladder climbing
- Elo tracking across generations

### 2. **Team Evolution Visualizer**
- Track which teams perform best
- Visualize meta shifts as agent learns
- Auto-generate new teams based on weaknesses

### 3. **Training vs Human Dashboard**
- Challenge your agent on stream
- Viewers can queue for battles
- Live win rate against humans

### 4. **Dataset Expansion Loop**
- Agent plays battles
- Saves high-quality trajectories
- Periodically retrains with new data
- "Watch me improve in real-time"

### 5. **Baseline Gauntlet Mode**
- Sequential battles vs all baselines
- Live progression tracker
- "Can Lass beat EmeraldKaizo today?"

### 6. **Team Prediction Showcase**
- Display predicted opponent team
- Show confidence scores
- Reveal actual team at end
- Accuracy tracking

### 7. **Replay Commentary Bot**
- LLM-powered play-by-play
- Move explanations
- Strategy insights
- Text-to-speech for stream

### 8. **Self-Play Evolution**
- Agent battles previous checkpoints
- Visualize skill progression
- "Lass today vs Lass from last week"

---

## Immediate Next Steps

1. **Set up Showdown server**:
   ```bash
   cd server/pokemon-showdown
   npm install
   node pokemon-showdown start --no-security
   ```

2. **Test battle execution**:
   ```bash
   python -m metamon.env --battle_format gen1ou --episodes 10
   ```

3. **Inspect battle data**:
   - Check Showdown logs: `server/pokemon-showdown/logs/`
   - Battle IDs, player names, turn logs

4. **Prototype HTML generation**:
   - Extract battle log from completed battle
   - Wrap in HTML template
   - Test in browser

5. **Build minimal viewer**:
   - Simple Python script with Playwright
   - Load HTML replay
   - Auto-advance when done

---

## Key Advantages of This Approach

**Leverages Existing Infrastructure**:
- Showdown server already running
- Battle logs already generated
- HTML replay format proven and tested

**Modular & Extensible**:
- Each component independent
- Easy to swap viewers/generators
- Can add features incrementally

**Production-Ready**:
- Showdown designed for 24/7 operation
- RL training loop is stable
- Only need glue code for automation

**Engaging Content**:
- Real battles, not simulations
- Actual RL agent improving
- Viewer can understand what's happening

---

## Questions to Answer Before Building

1. **Where to run?**
   - Local machine, VPS, cloud GPU?
   - Training needs GPU, viewing needs display

2. **Training regime?**
   - Continuous online RL?
   - Periodic finetuning?
   - Fixed opponent or curriculum?

3. **Stream frequency?**
   - Every battle or filtered highlights?
   - Speed up replay playback?

4. **Viewer interaction?**
   - Chat commands?
   - Vote on teams?
   - Challenge bot?

5. **Metrics to display?**
   - Win rate, Elo, damage dealt?
   - Move accuracy, switch decisions?
   - Team composition stats?

---

## Existing Code You Can Reuse

**Save Trajectories**:
```python
from metamon.env import QueueOnLocalLadder
env = QueueOnLocalLadder(
    ...,
    save_trajectories_to="./stream_replays",  # Auto-saves JSON
)
```

**Load Pretrained Agent**:
```python
from metamon.rl.pretrained import get_pretrained_model
agent = get_pretrained_model("SyntheticRLV2")  # Best Gen1-4 agent
```

**Battle on Ladder**:
```python
from metamon.rl.evaluate import pretrained_vs_local_ladder
results = pretrained_vs_local_ladder(
    pretrained_model=agent,
    username="Lass",
    battle_format="gen1ou",
    team_set=teams,
    total_battles=1000,
)
```

**Custom Baseline**:
```python
from metamon.baselines.base import Baseline
class LassOpponent(Baseline):
    def choose_move(self, battle):
        # Your logic here
        return self.choose_random_move(battle)
```

---

## The Missing Piece: Automatic HTML Replay Flow

**Current**: Battles happen → JSON saved → Manual HTML generation → Manual playback

**Needed**: Battles happen → JSON + HTML saved → Auto-queued → Auto-played

**Implementation**: Modify `metamon/env/wrappers.py:400-432`:

```python
if terminated or truncated:
    # ... existing JSON save code ...
    
    # NEW: Generate HTML replay
    if self.save_trajectories_to is not None:
        html_content = self._generate_replay_html(
            battle_log=self.current_battle.to_showdown_log(),
            battle_id=battle_id,
        )
        html_path = os.path.join(
            self.save_trajectories_to,
            f"{battle_id}.html"
        )
        with open(html_path, 'w') as f:
            f.write(html_content)
```

**Helper Method**:
```python
def _generate_replay_html(self, battle_log: str, battle_id: str) -> str:
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Battle {battle_id}</title>
</head>
<body>
<script type="text/plain" class="battle-log-data">{battle_log}</script>
<script src="https://play.pokemonshowdown.com/js/replay-embed.js"></script>
</body>
</html>'''
```

---

## Summary

**What Metamon Gives You**:
- RL environment for Pokemon battles
- Pretrained agents (including SOTA "SyntheticRLV2")
- Training infrastructure (AMAGO + offline RL)
- Team generation and prediction
- Replay dataset (1M+ battles)

**What You Need to Build**:
1. **Replay HTML Generator** - Convert battles to viewable HTML
2. **Auto Replay Viewer** - Sequential browser playback
3. **Stream Integration** - OBS capture + overlays
4. **Training Loop** - Continuous RL with replay generation
5. **Stats Dashboard** - Real-time win rate, elo, metrics

**Fastest Path to 24/7 Stream**:
1. Modify `wrappers.py` to save HTML replays ✅
2. Build Playwright viewer for sequential playback ✅
3. Set up QueueOnLocalLadder with continuous battles ✅
4. Point OBS at browser window ✅
5. Add stat overlays ✅
6. Deploy on VPS with systemd ✅

**Time Estimate**: 2-3 weeks for MVP, 4-6 weeks for production quality

---

*Ready to build? Start with Phase 1 (Replay HTML Generator) and I'll help you implement it!*
