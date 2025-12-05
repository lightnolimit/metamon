"""OBS Stats Overlay for Mystery-Gift Streaming

Provides real-time statistics display for OBS streaming.
Generates HTML overlay that auto-refreshes with current battle stats.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OBSOverlay:
    """OBS-compatible stats overlay that updates in real-time."""

    def __init__(self, stats_dir: Path, overlay_file: str = "obs_overlay.html"):
        """Initialize OBS overlay.

        Args:
            stats_dir: Directory containing mystery gift stats
            overlay_file: Name of overlay HTML file to generate
        """
        self.stats_dir = Path(stats_dir)
        self.overlay_file = self.stats_dir / overlay_file
        self.current_stats = {
            "agent_name": "Mystery-Gift",
            "total_battles": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "current_streak": 0,
            "best_streak": 0,
            "opponent_breakdown": {},
            "recent_performance": [],
            "current_battle_status": "Waiting for battle...",
            "last_updated": "",
        }

    def update_stats(self, metrics_data: Dict[str, Any]):
        """Update stats from training metrics.

        Args:
            metrics_data: Dictionary containing current metrics
        """
        try:
            # Load current metrics from mystery gift stats file
            stats_file = self.stats_dir / "mystery_gift_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)

                # Extract relevant stats
                self.current_stats.update({
                    "total_battles": stats.get("total_battles", 0),
                    "wins": stats.get("wins", 0),
                    "losses": stats.get("losses", 0),
                    "win_rate": stats.get("win_rate", 0.0),
                    "current_streak": stats.get("current_streak", 0),
                    "best_streak": stats.get("best_streak", 0),
                    "opponent_breakdown": stats.get("opponent_breakdown", {}),
                    "recent_performance": stats.get("recent_performance", [])[-10:],  # Last 10
                })

            # Update current battle status if provided
            if "current_battle_status" in metrics_data:
                self.current_stats["current_battle_status"] = metrics_data["current_battle_status"]

            # Update agent name
            if "agent_name" in metrics_data:
                self.current_stats["agent_name"] = metrics_data["agent_name"]

            # Update timestamp
            self.current_stats["last_updated"] = datetime.now().strftime("%H:%M:%S")

            # Generate new overlay
            self._generate_overlay()

        except Exception as e:
            logger.error(f"Error updating OBS overlay: {e}")

    def _generate_overlay(self):
        """Generate the HTML overlay file."""
        html_content = self._get_html_template()

        try:
            with open(self.overlay_file, 'w') as f:
                f.write(html_content)
            logger.debug(f"Updated OBS overlay: {self.overlay_file}")
        except Exception as e:
            logger.error(f"Error writing overlay file: {e}")

    def _get_html_template(self) -> str:
        """Generate HTML template with current stats."""
        win_rate_pct = f"{self.current_stats['win_rate']:.1f}%"
        streak_color = "green" if self.current_stats['current_streak'] > 0 else "red"

        # Format recent performance
        recent_html = ""
        for i, result in enumerate(self.current_stats['recent_performance'][-5:]):  # Last 5
            symbol = "✓" if result.get('won', False) else "✗"
            color = "green" if result.get('won', False) else "red"
            recent_html += f'<span style="color: {color}; font-weight: bold;">{symbol}</span>'

        # Format opponent breakdown
        opponent_html = ""
        for opponent, stats in list(self.current_stats['opponent_breakdown'].items())[:4]:  # Top 4
            opp_win_rate = stats.get('win_rate', 0) * 100
            opponent_html += f"""
            <div class="opponent-stat">
                <span class="opponent-name">{opponent}</span>
                <span class="opponent-win-rate">{opp_win_rate:.0f}%</span>
            </div>"""

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mystery-Gift Stats Overlay</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            margin: 0;
            font-size: 18px;
            line-height: 1.4;
        }}

        .stats-container {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            min-width: 400px;
        }}

        .header {{
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}

        .stats-row {{
            display: flex;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 8px;
            backdrop-filter: blur(5px);
        }}

        .stat-label {{
            color: #ccc;
        }}

        .stat-value {{
            font-weight: bold;
        }}

        .win-rate {{
            color: #4CAF50;
        }}

        .streak {{
            color: {streak_color};
        }}

        .current-status {{
            text-align: center;
            background: rgba(255, 255, 255, 0.2);
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            animation: pulse 2s infinite;
        }}

        .recent-performance {{
            text-align: center;
            font-size: 20px;
            letter-spacing: 8px;
        }}

        .opponent-stats {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .opponent-stat {{
            display: flex;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.05);
            padding: 5px 10px;
            border-radius: 4px;
        }}

        .opponent-name {{
            color: #ccc;
        }}

        .opponent-win-rate {{
            font-weight: bold;
        }}

        .timestamp {{
            text-align: center;
            font-size: 12px;
            color: #666;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="stats-container">
        <div class="header">
            {self.current_stats['agent_name']} Stats
        </div>

        <div class="current-status">
            {self.current_stats['current_battle_status']}
        </div>

        <div class="stats-row">
            <span class="stat-label">Total Battles:</span>
            <span class="stat-value">{self.current_stats['total_battles']}</span>
        </div>

        <div class="stats-row">
            <span class="stat-label">Wins/Losses:</span>
            <span class="stat-value">{self.current_stats['wins']}/{self.current_stats['losses']}</span>
        </div>

        <div class="stats-row">
            <span class="stat-label">Win Rate:</span>
            <span class="stat-value win-rate">{win_rate_pct}</span>
        </div>

        <div class="stats-row">
            <span class="stat-label">Current Streak:</span>
            <span class="stat-value streak">{self.current_stats['current_streak']}</span>
        </div>

        <div class="stats-row">
            <span class="stat-label">Best Streak:</span>
            <span class="stat-value">{self.current_stats['best_streak']}</span>
        </div>

        <div class="stats-row">
            <span class="stat-label">Recent (Last 5):</span>
            <span class="stat-value recent-performance">{recent_html}</span>
        </div>

        <div class="stats-row">
            <span class="stat-label">Opponent Win Rates:</span>
        </div>

        <div class="opponent-stats">
            {opponent_html}
        </div>

        <div class="timestamp">
            Last updated: {self.current_stats['last_updated']}
        </div>
    </div>

    <script>
        // Auto-refresh every 5 seconds
        setTimeout(function() {{
            window.location.reload();
        }}, 5000);
    </script>
</body>
</html>"""

    def start(self):
        """Start the overlay system."""
        logger.info(f"Starting OBS overlay at: {self.overlay_file}")
        self._generate_overlay()

    def stop(self):
        """Stop the overlay system."""
        logger.info("OBS overlay stopped")