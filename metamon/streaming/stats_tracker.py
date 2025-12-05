"""Track battle statistics for stream overlays"""
import json
import os
from typing import Dict, Optional
from datetime import datetime


class StatsTracker:
    """Track statistics for a single agent/player."""
    
    def __init__(self, player_name: str, output_file: Optional[str] = None):
        self.player_name = player_name
        self.output_file = output_file
        self.stats = {
            "player_name": player_name,
            "total_battles": 0,
            "wins": 0,
            "losses": 0,
            "current_streak": 0,
            "best_streak": 0,
            "last_updated": datetime.now().isoformat(),
        }
        self.load()
    
    def load(self):
        """Load existing stats from file if available."""
        if self.output_file and os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    saved = json.load(f)
                    self.stats.update(saved)
            except Exception as e:
                print(f"Could not load stats: {e}")
    
    def update(self, won: bool):
        """Update stats after a battle."""
        self.stats["total_battles"] += 1
        
        if won:
            self.stats["wins"] += 1
            self.stats["current_streak"] += 1
            self.stats["best_streak"] = max(
                self.stats["best_streak"],
                self.stats["current_streak"]
            )
        else:
            self.stats["losses"] += 1
            self.stats["current_streak"] = 0
        
        self.stats["last_updated"] = datetime.now().isoformat()
        self.save()
    
    def save(self):
        """Save stats to file."""
        if self.output_file:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            temp_path = self.output_file + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
            os.rename(temp_path, self.output_file)
    
    def get_win_rate(self) -> float:
        """Get win rate percentage."""
        if self.stats["total_battles"] == 0:
            return 0.0
        return (self.stats["wins"] / self.stats["total_battles"]) * 100
    
    def to_display_text(self) -> str:
        """Generate text for OBS overlay."""
        win_rate = self.get_win_rate()
        
        text = f"""╔══════════════════════════════════════╗
║  {self.player_name:^36s}  ║
╠══════════════════════════════════════╣
║  Battles: {self.stats['total_battles']:>5}                      ║
║  Win Rate: {win_rate:>5.1f}%                    ║
║  Record: {self.stats['wins']:>4}W - {self.stats['losses']:>4}L              ║
║  Current Streak: {self.stats['current_streak']:>4}              ║
║  Best Streak: {self.stats['best_streak']:>4}                 ║
╚══════════════════════════════════════╝"""
        
        return text


class TournamentStatsTracker:
    """Track statistics for a tournament with multiple agents."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.player_stats: Dict[str, StatsTracker] = {}
        self.matchup_history = []
        self.current_matchup = None
    
    def get_or_create_player_stats(self, player_name: str) -> StatsTracker:
        """Get or create stats tracker for a player."""
        if player_name not in self.player_stats:
            stats_file = os.path.join(
                self.output_dir,
                f"{player_name}_stats.json"
            )
            self.player_stats[player_name] = StatsTracker(player_name, stats_file)
        return self.player_stats[player_name]
    
    def record_battle(self, player1: str, player2: str, winner: str):
        """Record the result of a battle."""
        p1_stats = self.get_or_create_player_stats(player1)
        p2_stats = self.get_or_create_player_stats(player2)
        
        p1_won = (winner == player1)
        p2_won = (winner == player2)
        
        p1_stats.update(p1_won)
        p2_stats.update(p2_won)
        
        self.matchup_history.append({
            "player1": player1,
            "player2": player2,
            "winner": winner,
            "timestamp": datetime.now().isoformat(),
        })
        
        self.save_tournament_summary()
    
    def set_current_matchup(self, player1: str, player2: str):
        """Set the current matchup being played."""
        self.current_matchup = {
            "player1": player1,
            "player2": player2,
        }
        self.save_current_matchup()
    
    def save_current_matchup(self):
        """Save current matchup to file for overlay."""
        if self.current_matchup:
            filepath = os.path.join(self.output_dir, "current_matchup.txt")
            p1 = self.current_matchup["player1"]
            p2 = self.current_matchup["player2"]
            
            p1_stats = self.get_or_create_player_stats(p1)
            p2_stats = self.get_or_create_player_stats(p2)
            
            text = f"""╔══════════════════════════════════════════════════════════════════════╗
║                        CURRENT MATCHUP                               ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  {p1:^30s}  🆚  {p2:^30s}  ║
║                                                                      ║
║  Record: {p1_stats.stats['wins']:>3}W-{p1_stats.stats['losses']:>3}L ({p1_stats.get_win_rate():>5.1f}%)      Record: {p2_stats.stats['wins']:>3}W-{p2_stats.stats['losses']:>3}L ({p2_stats.get_win_rate():>5.1f}%)  ║
║  Streak: {p1_stats.stats['current_streak']:>3}                         Streak: {p2_stats.stats['current_streak']:>3}                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝"""
            
            with open(filepath, 'w') as f:
                f.write(text)
    
    def save_tournament_summary(self):
        """Save overall tournament standings."""
        filepath = os.path.join(self.output_dir, "tournament_standings.txt")
        
        # Sort players by win rate
        players = sorted(
            self.player_stats.values(),
            key=lambda s: (s.get_win_rate(), s.stats['wins']),
            reverse=True
        )
        
        text = "╔══════════════════════════════════════════════════════════════╗\n"
        text += "║                  TOURNAMENT STANDINGS                        ║\n"
        text += "╠══════════════════════════════════════════════════════════════╣\n"
        text += "║  Rank  Player              Record    Win Rate    Streak     ║\n"
        text += "╠══════════════════════════════════════════════════════════════╣\n"
        
        for i, stats in enumerate(players, 1):
            win_rate = stats.get_win_rate()
            name = stats.player_name[:16].ljust(16)
            record = f"{stats.stats['wins']:>3}W-{stats.stats['losses']:>3}L"
            text += f"║  {i:>2}.   {name}  {record}   {win_rate:>6.1f}%    {stats.stats['current_streak']:>3}      ║\n"
        
        text += "╚══════════════════════════════════════════════════════════════╝"
        
        with open(filepath, 'w') as f:
            f.write(text)
        
        # Also save JSON for programmatic access
        json_filepath = os.path.join(self.output_dir, "tournament_data.json")
        tournament_data = {
            "players": {
                name: stats.stats
                for name, stats in self.player_stats.items()
            },
            "matchup_history": self.matchup_history,
        }
        with open(json_filepath, 'w') as f:
            json.dump(tournament_data, f, indent=2)
