"""Configuration for Mystery-Gift Training Stream

Mystery-Gift is a single RL agent that:
- Battles humans when available
- Trains against bots otherwise  
- Improves over time via RL
- Always streams from its perspective
"""

# =============================================================================
# MYSTERY-GIFT CONFIGURATION
# =============================================================================

# Agent settings
AGENT_NAME = "Mystery-Gift"
BATTLE_FORMAT = "gen1ou"  # gen1ou, gen2ou, gen3ou, gen4ou, gen9ou
TEAM_SET = "competitive"  # competitive, modern_replays, modern_replays_v2

# Pretrained model (optional)
USE_PRETRAINED = False  # Set to True to use a trained model
PRETRAINED_MODEL = "SyntheticRLV2"  # Best Gen1-4 model (requires AMAGO)

# Output directory
OUTPUT_DIR = "./stream_data"

# =============================================================================
# OPPONENT MATCHING
# =============================================================================

# Ladder settings
ENABLE_LADDER = False  # Set to True to accept human opponents
HUMAN_WAIT_TIMEOUT = 60  # Seconds to wait for human before using bot

# Bot opponents (rotates through these)
BOT_OPPONENTS = [
    "RandomBaseline",  # Easy warmup
    "Grunt",           # Medium
    "GymLeader",       # Hard
    "EmeraldKaizo",    # Very hard
]

# =============================================================================
# STREAMING SETTINGS
# =============================================================================

# Replay viewer
VIEWER_DELAY = 5  # Seconds between replays
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Max battles (None = infinite)
MAX_BATTLES = None  # Run forever

# =============================================================================
# RL TRAINING (Future)
# =============================================================================

# These will be used when full RL training is integrated
ENABLE_ONLINE_TRAINING = False  # Train policy online from battles
TRAINING_UPDATE_FREQUENCY = 100  # Update policy every N battles
SAVE_CHECKPOINT_FREQUENCY = 1000  # Save checkpoint every N battles

# =============================================================================
# PUBLIC ACCESS (Future)
# =============================================================================

# Make server publicly accessible for human opponents
ENABLE_PUBLIC_SERVER = False  # Expose via ngrok/port forwarding
PUBLIC_SERVER_URL = None  # Will be set when enabled

# =============================================================================

def get_mystery_gift_config():
    """Get all configuration as dict."""
    return {
        'agent_name': AGENT_NAME,
        'battle_format': BATTLE_FORMAT,
        'team_set': TEAM_SET,
        'use_pretrained': USE_PRETRAINED,
        'pretrained_model': PRETRAINED_MODEL if USE_PRETRAINED else None,
        'output_dir': OUTPUT_DIR,
        'enable_ladder': ENABLE_LADDER,
        'human_wait_timeout': HUMAN_WAIT_TIMEOUT,
        'max_battles': MAX_BATTLES,
    }
