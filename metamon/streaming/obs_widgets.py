"""OBS Widget Manager for Mystery-Gift Streaming

Creates separate text files for each stat that can be used as individual
sources in OBS for flexible positioning and transparent backgrounds.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OBSWidgetManager:
    """Manages OBS widget files for individual stat display."""

    def __init__(self, stats_dir: str):
        """Initialize OBS widget manager.

        Args:
            stats_dir: Directory containing mystery gift stats
        """
        self.stats_dir = Path(stats_dir)
        self.widgets_dir = self.stats_dir / "widgets"
        self.widgets_dir.mkdir(exist_ok=True)

        # Define all widget files
        self.widget_files = {
            "win_rate": self.widgets_dir / "win_rate.txt",
            "battles": self.widgets_dir / "battles.txt",
            "record": self.widgets_dir / "record.txt",
            "current_streak": self.widgets_dir / "current_streak.txt",
            "best_streak": self.widgets_dir / "best_streak.txt",
            "vs_humans": self.widgets_dir / "vs_humans.txt",
            "vs_bots": self.widgets_dir / "vs_bots.txt",
            "recent_performance": self.widgets_dir / "recent_performance.txt",
            "countdown": self.widgets_dir / "countdown.txt",
            "current_opponent": self.widgets_dir / "current_opponent.txt",
            "search_status": self.widgets_dir / "search_status.txt",
        }

        # Initialize all widget files
        self._initialize_widgets()

    def _initialize_widgets(self):
        """Initialize all widget files with default values."""
        defaults = {
            "win_rate": "0.0%",
            "battles": "0",
            "record": "0W - 0L",
            "current_streak": "0",
            "best_streak": "0",
            "vs_humans": "0 battles (0.0% WR)",
            "vs_bots": "0 battles (0.0% WR)",
            "recent_performance": "No recent battles",
            "countdown": "",
            "current_opponent": "Waiting...",
            "search_status": "Idle",
        }

        for widget_name, default_value in defaults.items():
            self._write_widget(widget_name, default_value)

        logger.info(f"Initialized {len(self.widget_files)} OBS widget files in {self.widgets_dir}")

    def _write_widget(self, widget_name: str, value: str):
        """Write value to a widget file.

        Args:
            widget_name: Name of the widget
            value: Text value to write
        """
        if widget_name not in self.widget_files:
            logger.warning(f"Unknown widget: {widget_name}")
            return

        try:
            with open(self.widget_files[widget_name], 'w') as f:
                f.write(str(value))
        except Exception as e:
            logger.error(f"Failed to write widget {widget_name}: {e}")

    def update_all_widgets(self, metrics_data: Dict[str, Any]):
        """Update all stat widgets from training metrics.

        Args:
            metrics_data: Dictionary containing training metrics
        """
        try:
            # Extract basic stats
            total_battles = metrics_data.get("total_battles", 0)
            wins = metrics_data.get("wins", 0)
            losses = metrics_data.get("losses", 0)
            current_streak = metrics_data.get("current_streak", 0)
            best_streak = metrics_data.get("best_streak", 0)

            # Calculate win rates
            overall_win_rate = (wins / total_battles * 100) if total_battles > 0 else 0.0

            # Human vs Bot stats
            vs_humans_battles = metrics_data.get("vs_humans_battles", 0)
            vs_humans_wins = metrics_data.get("vs_humans_wins", 0)
            vs_bots_battles = metrics_data.get("vs_bots_battles", 0)
            vs_bots_wins = metrics_data.get("vs_bots_wins", 0)

            vs_humans_wr = (vs_humans_wins / vs_humans_battles * 100) if vs_humans_battles > 0 else 0.0
            vs_bots_wr = (vs_bots_wins / vs_bots_battles * 100) if vs_bots_battles > 0 else 0.0

            # Recent performance (last 10 from recent_results if available)
            recent_results = metrics_data.get("recent_results", [])
            if recent_results:
                # Take last 10 results
                last_10 = recent_results[-10:] if len(recent_results) >= 10 else recent_results
                recent_text = " ".join(["W" if r else "L" for r in last_10])
            else:
                recent_text = "No recent battles"

            # Update all widgets
            self._write_widget("win_rate", f"{overall_win_rate:.1f}%")
            self._write_widget("battles", str(total_battles))
            self._write_widget("record", f"{wins}W - {losses}L")
            self._write_widget("current_streak", str(current_streak))
            self._write_widget("best_streak", str(best_streak))
            self._write_widget("vs_humans", f"{vs_humans_battles} battles ({vs_humans_wr:.1f}% WR)")
            self._write_widget("vs_bots", f"{vs_bots_battles} battles ({vs_bots_wr:.1f}% WR)")
            self._write_widget("recent_performance", recent_text)

            logger.debug(f"Updated {len(self.widget_files) - 2} stat widgets")  # -2 for countdown and opponent

        except Exception as e:
            logger.error(f"Failed to update widgets: {e}")

    def update_countdown(self, seconds_remaining: int):
        """Update countdown widget.

        Args:
            seconds_remaining: Seconds remaining until next battle
        """
        if seconds_remaining > 0:
            minutes = seconds_remaining // 60
            seconds = seconds_remaining % 60
            if minutes > 0:
                countdown_text = f"{minutes}:{seconds:02d}"
            else:
                countdown_text = f"{seconds}s"
        else:
            countdown_text = "Starting..."

        self._write_widget("countdown", countdown_text)

    def update_current_opponent(self, opponent_name: str, opponent_type: str = "bot"):
        """Update current opponent widget.

        Args:
            opponent_name: Name of current opponent
            opponent_type: Type of opponent ('human' or 'bot')
        """
        if opponent_name:
            # Add emoji to indicate opponent type
            if opponent_type == "human":
                opponent_text = f"👤 {opponent_name}"
            else:
                opponent_text = f"🤖 {opponent_name}"
        else:
            opponent_text = "Waiting..."

        self._write_widget("current_opponent", opponent_text)

    def update_search_status(self, status: str):
        """Update search status widget.

        Args:
            status: Current search status message
        """
        self._write_widget("search_status", status)

    def get_widget_paths(self) -> Dict[str, str]:
        """Get paths to all widget files for OBS setup.

        Returns:
            Dictionary mapping widget names to file paths
        """
        return {name: str(path) for name, path in self.widget_files.items()}

    def list_widget_files(self) -> list:
        """List all widget file paths.

        Returns:
            List of widget file paths
        """
        return [str(path) for path in self.widget_files.values()]