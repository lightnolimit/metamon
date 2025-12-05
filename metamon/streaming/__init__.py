"""Metamon 24/7 Streaming Module

Automatic battle replay generation and sequential viewing for OBS streaming.
"""

from .replay_saver import generate_replay_html, save_replay_html
from .stats_tracker import StatsTracker, TournamentStatsTracker
from .replay_viewer import ReplayViewer
from .tournament_manager import TournamentManager, TournamentConfig, TournamentAgent
from .training_stream import start_tournament_stream
from .mystery_gift_agent import MysteryGiftAgent
from .opponent_matcher import OpponentMatcher, OpponentInfo
from .training_tracker import TrainingMetrics
from .mystery_gift_stream import start_mystery_gift_stream
from .obs_widgets import OBSWidgetManager

__all__ = [
    'generate_replay_html',
    'save_replay_html',
    'StatsTracker',
    'TournamentStatsTracker',
    'ReplayViewer',
    'TournamentManager',
    'TournamentConfig',
    'TournamentAgent',
    'start_tournament_stream',
    'MysteryGiftAgent',
    'OpponentMatcher',
    'OpponentInfo',
    'TrainingMetrics',
    'start_mystery_gift_stream',
    'OBSWidgetManager',
]
