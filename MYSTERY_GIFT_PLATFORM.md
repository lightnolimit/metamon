# Mystery-Gift: RL Training Streaming Platform

## Vision

A 24/7 livestream following "Mystery-Gift" - an RL agent that improves over time by:
- Battling human opponents when available
- Training against bots when no humans online
- Streaming all battles from Mystery-Gift's perspective
- Showing RL training metrics and improvement over time

## Architecture

```
                    MYSTERY-GIFT BOT
                          │
                          ├─ Has humans online? (60s queue)
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
       YES                                 NO
        │                                   │
        ▼                                   ▼
  Battle Human                      Battle Bot
  (Ladder Match)                    (Training Match)
        │                                   │
        └─────────────────┬─────────────────┘
                          │
                          ▼
                 Battle Completes
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
  Save Replay      Update RL Stats    Update Stream
  (HTML + JSON)    (Win Rate, ELO)    (Overlays)
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
                          ▼
                 Back to Queue (60s wait)
```

## Components Needed

### 1. Mystery-Gift Agent Manager
**File**: `metamon/streaming/mystery_gift.py`

```python
class MysteryGiftAgent:
    """Main RL agent that improves over time"""
    
    def __init__(self, format="gen1ou"):
        self.name = "Mystery-Gift"
        self.format = format
        self.rl_policy = None  # Can be pretrained or training
        self.teams = self.load_teams_for_format(format)
        self.stats = AgentStats(self.name)
    
    def load_teams_for_format(self, format):
        """Load premade teams for this format"""
        # gen1ou, gen2ou, gen3ou, gen4ou teams
        pass
    
    def select_action(self, battle_state):
        """Use RL policy to select action"""
        if self.rl_policy:
            return self.rl_policy.act(battle_state)
        else:
            return random_action()  # Fallback
    
    def update_from_battle(self, trajectory):
        """Update RL policy from battle experience"""
        # Online RL training
        pass
```

### 2. Opponent Queue System
**File**: `metamon/streaming/opponent_queue.py`

```python
class OpponentQueue:
    """Manages finding opponents (humans or bots)"""
    
    def wait_for_opponent(self, timeout=60):
        """Wait for human opponent on ladder"""
        # Try to find ranked match for 60 seconds
        # Return (opponent_type, opponent_info)
        pass
    
    def get_bot_opponent(self):
        """Select a bot opponent for training"""
        # Rotate through: Lass, Scout, Ace, Rookie
        # Or use curriculum learning (start easy, get harder)
        pass
```

### 3. Training Metrics Tracker
**File**: `metamon/streaming/training_metrics.py`

```python
class TrainingMetrics:
    """Track RL training progress for stream overlays"""
    
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.metrics = {
            "total_battles": 0,
            "vs_humans": 0,
            "vs_bots": 0,
            "win_rate_overall": 0.0,
            "win_rate_vs_humans": 0.0,
            "win_rate_vs_bots": 0.0,
            "elo_rating": 1500,
            "training_episodes": 0,
            "policy_updates": 0,
            "average_reward": 0.0,
        }
    
    def update(self, battle_result, opponent_type):
        """Update metrics after battle"""
        pass
    
    def generate_overlay(self):
        """Create text file for OBS overlay"""
        # Show current ELO, win rate, training progress
        pass
```

### 4. Ladder Integration
**File**: `metamon/streaming/public_ladder.py`

```python
class PublicLadderServer:
    """Make Mystery-Gift available on public ladder"""
    
    def start_server(self, agent):
        """Start accepting challenges from anyone"""
        # Use QueueOnLocalLadder but make server public
        # Or connect to PokeAgent ladder
        pass
    
    def accept_challenge(self, challenger):
        """Auto-accept incoming challenges"""
        pass
```

## Implementation Plan

### Phase 1: Fix Crashes & Resource Leaks (NOW)
- ✅ Fix "Too many open files" error
- ✅ Properly close environments after battles
- ✅ Handle Playwright cleanup gracefully

### Phase 2: Single Agent Mode (Week 1)
- Create Mystery-Gift agent class
- Load premade teams for Gen1-4
- Switch from tournament to single agent streaming
- Always follow Mystery-Gift's perspective

### Phase 3: Opponent Queue System (Week 1-2)
- Implement 60s wait for human opponents
- Fall back to bot battles
- Seamless switching between modes
- Track opponent types

### Phase 4: RL Training Integration (Week 2-3)
- Online RL training from battle experience
- Save trajectories for offline training
- Periodic policy updates
- Track training metrics (loss, rewards, etc.)

### Phase 5: Public Ladder (Week 2-3)
- Expose local Showdown server publicly (port forwarding/ngrok)
- Or deploy to PokeAgent ladder
- Accept challenges from anyone
- Ranking system integration

### Phase 6: Enhanced Stream Overlays (Week 3-4)
- ELO rating graph over time
- Win rate vs humans/bots split
- Training metrics dashboard
- Recent battles feed
- "Waiting for opponent" timer

## Quick Start For Now

I'll create a simplified version that:
1. ✅ Fixes the crash (close environments properly)
2. ✅ Has single "Mystery-Gift" bot
3. ✅ Battles against rotating opponents
4. ✅ Tracks basic stats
5. ⏱️ Waits for h humans (future)
6. ⏱️ RL training (future)

## Premade Teams Structure

```
.cache/teams/
├── mystery-gift/
│   ├── gen1ou/
│   │   ├── team1.gen1ou_team
│   │   ├── team2.gen1ou_team
│   │   └── ...
│   ├── gen2ou/
│   ├── gen3ou/
│   ├── gen4ou/
│   └── gen9ou/
```

Mystery-Gift will rotate through these teams or select based on meta.

## Stream Layout

```
┌────────────────────────────────────────────┐
│  MYSTERY-GIFT TRAINING STREAM              │
├────────────────────────────────────────────┤
│                                            │
│  [Battle View - Following Mystery-Gift]   │
│  ┌────────────────────────────────────┐   │
│  │  Pokemon Battle                     │   │
│  │  (Mystery-Gift's perspective)       │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Stats Overlay]                           │
│  ┌────────────────────────────────────┐   │
│  │  MYSTERY-GIFT STATS                 │   │
│  │  Total Battles: 1,247               │   │
│  │  ELO: 1,653                         │   │
│  │  Win Rate: 68.3%                    │   │
│  │  vs Humans: 12W-8L (60.0%)          │   │
│  │  vs Bots: 839W-388L (68.4%)         │   │
│  │                                      │   │
│  │  Training Progress:                 │   │
│  │  Episodes: 1,247                    │   │
│  │  Policy Updates: 42                 │   │
│  │  Avg Reward: +12.3                  │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Current Status]                          │
│  ⏱️  Waiting for opponent... (23s)         │
│  or                                        │
│  🎮 Battle vs Scout-1234 in progress...   │
└────────────────────────────────────────────┘
```

## Files to Create

1. `metamon/streaming/mystery_gift_agent.py` - Main agent class
2. `metamon/streaming/opponent_matcher.py` - Queue + fallback logic
3. `metamon/streaming/training_tracker.py` - RL metrics
4. `metamon/streaming/mystery_gift_stream.py` - Main orchestrator
5. `mystery_gift_config.py` - Configuration
6. `RUN_MYSTERY_GIFT.sh` - Launcher

## Next Steps

Let me:
1. ✅ Fix the crash now (environment cleanup)
2. ✅ Create simplified Mystery-Gift mode
3. ✅ Commit and push
4. 📝 Document full RL training integration plan
