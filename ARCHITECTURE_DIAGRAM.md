# Metamon Architecture Diagram

## High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR STREAM                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  OBS Studio                                               │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Browser Window (Replay Viewer)                     │  │   │
│  │  │  ┌──────────────────────────────────────────────┐  │  │   │
│  │  │  │  Pokemon Battle Replay (HTML + JS)            │  │  │   │
│  │  │  │  ┌────────────────────────────────────────┐  │  │  │   │
│  │  │  │  │  🎮 Battle Animation                    │  │  │  │   │
│  │  │  │  │  Turn 1: Alakazam vs Tauros           │  │  │  │   │
│  │  │  │  │  Alakazam used Psychic!                │  │  │  │   │
│  │  │  │  └────────────────────────────────────────┘  │  │  │   │
│  │  │  └──────────────────────────────────────────────┘  │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Text Overlay: LASS TRAINING STATS                 │  │   │
│  │  │  Battles: 1247  Win Rate: 68.3%                    │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Window Capture
                              │
┌─────────────────────────────────────────────────────────────────┐
│              Metamon Streaming Pipeline                          │
│                                                                  │
│  ┌────────────────────┐         ┌──────────────────────┐        │
│  │  Replay Viewer     │◄────────│  HTML Replay Queue   │        │
│  │  (Playwright)      │  FIFO   │  - battle-001.html   │        │
│  │                    │         │  - battle-002.html   │        │
│  │  - Auto-load HTML  │         │  - battle-003.html   │        │
│  │  - Detect complete │         │  ...                 │        │
│  │  - Next replay     │         └──────────────────────┘        │
│  └────────────────────┘                   ▲                     │
│           ▲                               │ Write HTML          │
│           │ Read stats.txt                │                     │
│           │                               │                     │
│  ┌────────────────────┐         ┌──────────────────────┐        │
│  │  Stats Tracker     │         │  Replay Generator    │        │
│  │                    │         │                      │        │
│  │  - Win rate        │         │  - Extract battle    │        │
│  │  - Battle count    │         │    logs              │        │
│  │  - Streaks         │         │  - Wrap in HTML      │        │
│  │  - Write to file   │         │  - Save to disk      │        │
│  └────────────────────┘         └──────────────────────┘        │
│           ▲                               ▲                     │
│           │ Update stats                  │ On battle end       │
│           │                               │                     │
└───────────┼───────────────────────────────┼─────────────────────┘
            │                               │
┌───────────┴───────────────────────────────┴─────────────────────┐
│                   Metamon Core                                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Environment Wrapper (PokeEnvWrapper)                      │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Training Loop                                        │ │ │
│  │  │                                                        │ │ │
│  │  │  for episode in range(total_battles):                │ │ │
│  │  │      state = env.reset()                             │ │ │
│  │  │      while not done:                                 │ │ │
│  │  │          action = agent.act(state)  ──────┐          │ │ │
│  │  │          state, reward, done = env.step() │          │ │ │
│  │  │      # Battle complete ─────────────────┐ │          │ │ │
│  │  └────────────────────────────────────────┼─┼──────────┘ │ │
│  │                                            │ │            │ │
│  │  On battle end:                            │ │            │ │
│  │  ├─ Save JSON trajectory (.json.lz4) ──────┼─┘            │ │
│  │  ├─ Extract battle log                     │              │ │
│  │  ├─ Generate HTML replay ──────────────────┘              │ │
│  │  └─ Update stats tracker                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  RL Agent     │  │  Observation │  │  Action Space        │ │
│  │  (Pretrained/ │  │  Space       │  │  (13 discrete:       │ │
│  │   Your Own)   │  │              │  │   4 moves + 5 switch │ │
│  │               │  │  - Pokemon   │  │   + 4 tera moves)    │ │
│  │  - Policy π   │  │  - Stats     │  │                      │ │
│  │  - Value V    │  │  - Moves     │  │  UniversalAction     │ │
│  │               │  │  - Types     │  │         ▼            │ │
│  └───────┬───────┘  └──────────────┘  │  BattleOrder         │ │
│          │                             └──────────────────────┘ │
│          │ select_action()                        │             │
│          └────────────────────────────────────────┘             │
└──────────────────────────────────────┬───────────────────────────┘
                                       │ WebSocket
┌──────────────────────────────────────┴───────────────────────────┐
│          Pokemon Showdown Local Server (Node.js)                 │
│                                                                   │
│  ┌────────────────────┐    ┌──────────────────────────────────┐ │
│  │  Battle Rooms      │    │  Battle Simulator                │ │
│  │                    │    │                                  │ │
│  │  battle-gen1ou-1   │◄───┤  - Process moves                │ │
│  │  battle-gen1ou-2   │    │  - Calculate damage             │ │
│  │  ...               │    │  - Apply status effects         │ │
│  │                    │    │  - Update state                 │ │
│  │  Log: |turn|1|    │───►│  - Determine winner             │ │
│  │       |move|p1| ...│    │                                  │ │
│  └────────────────────┘    └──────────────────────────────────┘ │
│                                                                   │
│  http://localhost:8000                                           │
└───────────────────────────────────────────────────────────────────┘
```

---

## Data Flow for a Single Battle

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Battle Start                                                  │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Agent receives UniversalState                                 │
│    - Your Pokemon: Alakazam (HP: 301/301)                        │
│    - Opponent: Tauros (HP: 353/353)                              │
│    - Field conditions, weather, etc.                             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. ObservationSpace converts to agent input                      │
│    state → tokenized_obs (e.g., tensor of token IDs)            │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Agent selects action                                          │
│    action_idx = agent.act(obs)  # e.g., 0 = use move 0          │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. ActionSpace converts to UniversalAction                       │
│    action_idx → UniversalAction(action_idx=0)                    │
│    "Use Psychic" (move 0 alphabetically)                         │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. UniversalAction → BattleOrder (poke-env format)              │
│    "/choose move 2" (Showdown protocol)                          │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Send to Pokemon Showdown server via WebSocket                │
│    Server processes: damage calc, effects, etc.                 │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Server sends back state update                                │
│    |turn|2                                                       │
│    |-damage|p2a: Tauros|215/353                                 │
│    |move|p2a: Tauros|Body Slam|p1a: Alakazam                    │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. Parse update → new UniversalState                             │
│    Agent sees: Tauros took damage, used Body Slam                │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10. RewardFunction calculates reward                             │
│     +damage_dealt, -damage_received, etc.                        │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 11. Store trajectory                                             │
│     states: [state_t, state_{t+1}, ...]                          │
│     actions: [action_t, action_{t+1}, ...]                       │
└────────┬────────────────────────────────────────────────────────┘
         │
         │ Repeat steps 2-11 until...
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 12. Battle Ends                                                  │
│     |win|Lass  (or |win|Opponent)                                │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────┬──────────────────────────┐
         ▼                             ▼                          ▼
┌──────────────────┐    ┌──────────────────────┐   ┌─────────────────┐
│ Save JSON        │    │ Generate HTML Replay │   │ Update Stats    │
│ Trajectory       │    │                      │   │                 │
│ (.json.lz4)      │    │ - Get battle log     │   │ - win_rate++    │
│                  │    │ - Wrap in template   │   │ - total_battles │
│ For offline RL   │    │ - Save .html file    │   │ - Write file    │
└──────────────────┘    └──────────┬───────────┘   └─────────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │  HTML Replay Queue       │
                     │  Auto-picked up by       │
                     │  Replay Viewer           │
                     └──────────┬───────────────┘
                                │
                                ▼
                     ┌──────────────────────────┐
                     │  Viewed by Playwright    │
                     │  Captured by OBS         │
                     │  Streamed to Twitch      │
                     └──────────────────────────┘
```

---

## Directory Structure (After Setup)

```
metamon/
├── metamon/
│   ├── baselines/         # Heuristic/IL opponents
│   ├── backend/           # Showdown parsing, team prediction
│   ├── data/              # Dataset utilities
│   ├── env/               # Gym environments
│   ├── il/                # Imitation learning
│   ├── interface.py       # Obs/Action/Reward spaces
│   ├── rl/                # RL training (AMAGO)
│   ├── tokenizer/         # Text tokenization
│   └── streaming/         # ← NEW: Your livestream code
│       ├── __init__.py
│       ├── replay_saver.py      # Generate HTML from battles
│       ├── replay_viewer.py     # Auto-play replays
│       ├── stats_tracker.py     # Track win rate, etc.
│       └── training_stream.py   # All-in-one script
│
├── server/
│   ├── pokemon-showdown/  # Local Showdown server
│   └── config.js          # Server settings
│
├── stream_data/           # ← NEW: Generated data
│   ├── gen1ou/
│   │   ├── battle-*.json.lz4    # JSON trajectories
│   │   └── html_replays/
│   │       ├── battle-001.html  # HTML replays
│   │       ├── battle-002.html
│   │       └── ...
│   └── stats.txt          # OBS text overlay
│
├── .cache/                # Downloaded datasets/teams
│   ├── teams/
│   │   ├── competitive/
│   │   └── modern_replays/
│   └── parsed-replays/
│
├── examples/
│   └── evaluate_custom_models.py
│
├── README.md
├── METAMON_ARCHITECTURE_AND_EXTENSION_PLAN.md  # ← Full details
├── QUICKSTART_STREAMING.md                      # ← Implementation guide
└── ARCHITECTURE_DIAGRAM.md                      # ← This file
```

---

## Component Responsibilities

### Metamon Core
- **Environment**: Wrap Showdown API, handle state/action conversion
- **Interface**: Define observation/action/reward abstractions
- **RL/IL**: Train agents with AMAGO or behavior cloning
- **Baselines**: Heuristic/learned opponents for evaluation
- **Data**: Manage 1M+ human replay dataset

### Pokemon Showdown Server
- **Battle Simulation**: Damage calculation, move effects, win conditions
- **WebSocket API**: Real-time communication with agents
- **Battle Logging**: Turn-by-turn logs for replay reconstruction
- **Ladder System**: ELO-based matchmaking (optional)

### Streaming Pipeline (Your Code)
- **Replay Saver**: Extract logs → HTML format
- **Replay Viewer**: Sequential auto-playback via Playwright
- **Stats Tracker**: Calculate win rate, save to file
- **Training Stream**: Orchestrate training + viewing

### OBS Studio
- **Window Capture**: Record browser window
- **Text Overlays**: Display stats from file
- **Scene Management**: Transitions, layouts
- **Stream Output**: Twitch/YouTube RTMP

---

## Technology Stack

```
┌───────────────────────────────────────────────────────────┐
│  Application Layer                                        │
├───────────────────────────────────────────────────────────┤
│  - Python 3.10+                                           │
│  - PyTorch (RL agent neural networks)                     │
│  - Gymnasium (RL env interface)                           │
│  - Playwright (Browser automation)                        │
│  - AMAGO (RL training framework)                          │
├───────────────────────────────────────────────────────────┤
│  Pokemon Showdown Layer                                   │
├───────────────────────────────────────────────────────────┤
│  - Node.js (Showdown server)                              │
│  - poke-env (Python ↔ Showdown bridge)                    │
│  - WebSocket (Communication protocol)                     │
├───────────────────────────────────────────────────────────┤
│  Data Layer                                               │
├───────────────────────────────────────────────────────────┤
│  - HuggingFace Datasets (Replay storage)                  │
│  - LZ4 Compression (Trajectory files)                     │
│  - JSON (Battle logs, team files)                         │
├───────────────────────────────────────────────────────────┤
│  Streaming Layer                                          │
├───────────────────────────────────────────────────────────┤
│  - OBS Studio (Capture + encoding)                        │
│  - Chromium (Replay rendering)                            │
│  - Twitch/YouTube (Stream destination)                    │
└───────────────────────────────────────────────────────────┘
```

---

## Key Interfaces

### UniversalState → ObservationSpace → Agent Input
```python
UniversalState(
    player_active={'species': 'alakazam', 'hp': 301, ...},
    opponent_active={'species': 'tauros', 'hp': 353, ...},
    player_team=[...],
    ...
)
↓ (ObservationSpace)
{
    'pokemon_text': ['alakazam', 'tauros', ...],
    'moves_text': ['psychic', 'recover', ...],
    'hp_frac': [1.0, 1.0, ...],
    ...
}
↓ (TokenizedObservationSpace)
tensor([42, 156, 89, ...])  # Token IDs for transformer
```

### Agent Output → ActionSpace → BattleOrder
```python
action_idx = 0  # Agent's choice
↓ (ActionSpace)
UniversalAction(action_idx=0)  # "Use first move alphabetically"
↓ (to_BattleOrder)
BattleOrder("/choose move 2")  # Showdown protocol
```

### Battle Log → HTML Replay
```python
battle_log = 
"|player|p1|Lass|
|player|p2|GymLeader|
|teamsize|p1|6
|teamsize|p2|6
|start
|switch|p1a: Alakazam|Alakazam, L50|100/100
..."
↓ (wrap_in_template)
<!DOCTYPE html>
<script type="text/plain" class="battle-log-data">
[battle_log]
</script>
<script src=".../replay-embed.js"></script>
```

---

## State Machine: Training Loop

```
     START
       │
       ▼
   ┌─────────┐
   │ RESET   │◄──────────────┐
   │ env     │               │
   └────┬────┘               │
        │                    │
        │ Get initial state  │
        ▼                    │
   ┌─────────┐               │
   │ SELECT  │               │
   │ ACTION  │               │
   └────┬────┘               │
        │                    │
        │ agent.act()        │
        ▼                    │
   ┌─────────┐               │
   │ EXECUTE │               │
   │ STEP    │               │
   └────┬────┘               │
        │                    │
        │ env.step()         │
        ▼                    │
   ┌─────────┐               │
   │ UPDATE  │               │
   │ STATE   │               │
   └────┬────┘               │
        │                    │
        ├─ Save to trajectory│
        ├─ Calculate reward  │
        │                    │
        ▼                    │
    ┌──────┐                 │
    │Done? │─No──────────────┘
    └──┬───┘
       │ Yes
       ▼
  ┌──────────┐
  │ SAVE     │
  │ REPLAYS  │
  │ & STATS  │
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ Next     │
  │ Episode? │─Yes──┐
  └────┬─────┘      │
       │ No         │
       ▼            │
      END           │
       ▲            │
       └────────────┘
```

---

## Replay Flow

```
ONLINE BATTLE         OFFLINE DATASET       STREAMING
─────────────         ───────────────       ─────────

┌──────────┐         ┌──────────┐          ┌──────────┐
│ Battle   │         │ Human    │          │ Current  │
│ Executes │         │ Replay   │          │ Training │
│ (Real    │         │ (JSON)   │          │ Run      │
│  time)   │         │          │          │          │
└────┬─────┘         └────┬─────┘          └────┬─────┘
     │                    │                     │
     │ Extract log        │ Parse               │ Generate
     ▼                    ▼                     ▼
┌──────────┐         ┌──────────┐          ┌──────────┐
│ JSON     │         │ States + │          │ HTML     │
│ Trajectory│        │ Actions  │          │ Replay   │
│          │         │          │          │          │
│ For RL   │         │ For RL   │          │ For OBS  │
└──────────┘         └──────────┘          └────┬─────┘
                                                 │
                                                 │ Queue
                                                 ▼
                                            ┌──────────┐
                                            │ Auto-    │
                                            │ Viewer   │
                                            └────┬─────┘
                                                 │
                                                 ▼
                                            ┌──────────┐
                                            │ Twitch   │
                                            │ Stream   │
                                            └──────────┘
```

---

This architecture enables:
✅ Continuous RL training
✅ Real-time replay generation  
✅ Automatic sequential viewing
✅ Live stat tracking
✅ 24/7 streaming capability
