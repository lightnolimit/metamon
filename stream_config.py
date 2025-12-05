"""Configuration for 24/7 Tournament Stream

Edit this file to customize your tournament participants and settings.
"""
from metamon.streaming.tournament_manager import TournamentAgent, TournamentConfig


# =============================================================================
# TOURNAMENT CONFIGURATION
# =============================================================================

BATTLE_FORMAT = "gen1ou"  # Options: gen1ou, gen2ou, gen3ou, gen4ou, gen9ou
BATTLES_PER_MATCHUP = 3  # Best of N (odd numbers recommended)
SHUFFLE_MATCHUPS = True  # Randomize matchup order each round
LOOP_FOREVER = True  # Keep running rounds indefinitely
OUTPUT_DIR = "./stream_data"  # Where to save replays and stats

# Replay viewer settings
VIEWER_DELAY = 5  # Seconds between replays
WINDOW_WIDTH = 1280  # Browser window width
WINDOW_HEIGHT = 720  # Browser window height

# =============================================================================
# TOURNAMENT PARTICIPANTS
# =============================================================================

# Define your agents here. Each agent needs:
#   - name: Display name
#   - agent_type: 'baseline' or 'pretrained'
#   - agent_config: Configuration dict (see examples below)
#   - team_set: Which teams to use (competitive, modern_replays, etc.)

TOURNAMENT_AGENTS = [
    # Example: Heuristic baseline agents
    TournamentAgent(
        name="Lass",
        agent_type="baseline",
        agent_config={
            "baseline_name": "GymLeader"  # Smart offensive player
        },
        team_set="competitive",
    ),
    
    TournamentAgent(
        name="Scout",
        agent_type="baseline",
        agent_config={
            "baseline_name": "Grunt"  # Simple max damage
        },
        team_set="competitive",
    ),
    
    TournamentAgent(
        name="Ace",
        agent_type="baseline",
        agent_config={
            "baseline_name": "EmeraldKaizo"  # Very strong AI
        },
        team_set="competitive",
    ),
    
    TournamentAgent(
        name="Rookie",
        agent_type="baseline",
        agent_config={
            "baseline_name": "RandomBaseline"  # Random moves
        },
        team_set="competitive",
    ),
    
    # Example: Pretrained RL agent (uncomment to use)
    # NOTE: Requires AMAGO installation and pretrained models
    # TournamentAgent(
    #     name="Champion",
    #     agent_type="pretrained",
    #     agent_config={
    #         "model_name": "SyntheticRLV2",  # Best Gen1-4 agent
    #         "checkpoint": None,  # None = default checkpoint
    #     },
    #     team_set="competitive",
    # ),
]


# =============================================================================
# AVAILABLE BASELINES
# =============================================================================
# 
# You can use any of these as baseline_name:
#
# - RandomBaseline: Completely random moves
# - BugCatcher: Intentionally bad (picks worst moves)
# - Gen1BossAI: Mimics Pokemon Red/Blue AI
# - Grunt: Max damage heuristic
# - GymLeader: Smart offensive play with healing
# - EmeraldKaizo: Very sophisticated rule-based AI
# - PokeEnvHeuristic: poke-env's default heuristic
# - EasyPokeEnvHeuristic: Easier version
# - MediumPokeEnvHeuristic: Medium difficulty
# - HardPokeEnvHeuristic: Harder version
# - BaseRNN: Simple learned baseline (CPU)
#
# =============================================================================


# =============================================================================
# AVAILABLE TEAM SETS
# =============================================================================
#
# - competitive: Human-made sample teams from Smogon forums (small, high quality)
# - modern_replays: Predicted teams from recent replays (large, diverse)
# - modern_replays_v2: Updated version with more teams
# - paper_variety: Procedurally generated teams (Gen 1-4 only)
# - paper_replays: Older predicted teams (Gen 1-4 OU only)
#
# =============================================================================


def get_tournament_config():
    """Get tournament configuration."""
    config = TournamentConfig(
        battle_format=BATTLE_FORMAT,
        battles_per_matchup=BATTLES_PER_MATCHUP,
        shuffle_matchups=SHUFFLE_MATCHUPS,
        loop_forever=LOOP_FOREVER,
    )
    return config


def get_tournament_agents():
    """Get list of tournament agents."""
    return TOURNAMENT_AGENTS
