"""Track RL training metrics for Mystery-Gift"""

import json
import os
from typing import Dict, Optional
from datetime import datetime
from collections import deque


class TrainingMetrics:
    """Track RL training progress and battle statistics."""
    
    def __init__(self, agent_name: str, output_file: str):
        """Initialize training metrics.
        
        Args:
            agent_name: Name of the agent
            output_file: Path to save metrics
        """
        self.agent_name = agent_name
        self.output_file = output_file
        
        self.metrics = {
            "agent_name": agent_name,
            "total_battles": 0,
            "wins": 0,
            "losses": 0,
            
            # Split by opponent type
            "vs_humans_battles": 0,
            "vs_humans_wins": 0,
            "vs_bots_battles": 0,
            "vs_bots_wins": 0,
            
            # Per-bot stats
            "vs_bots": {},  # {bot_name: {battles, wins, losses}}
            
            # Training metrics
            "training_episodes": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,
            
            # Streaks
            "current_streak": 0,
            "best_streak": 0,
            
            # Recent performance (last 100 battles)
            "recent_wins": 0,
            "recent_total": 0,
            
            # Time tracking
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
        
        # Circular buffer for recent battles
        self.recent_results = deque(maxlen=100)
        
        self.load()
    
    def load(self):
        """Load existing metrics from file."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    saved = json.load(f)
                    self.metrics.update(saved)
                    logger.info(f"Loaded existing metrics: {self.metrics['total_battles']} battles")
            except Exception as e:
                logger.warning(f"Could not load metrics: {e}")
    
    def update(
        self,
        won: bool,
        opponent_type: str,  # 'human' or 'bot'
        opponent_name: str,
        reward: float = 0.0,
    ):
        """Update metrics after a battle.
        
        Args:
            won: Whether Mystery-Gift won
            opponent_type: 'human' or 'bot'
            opponent_name: Name of opponent
            reward: Total reward from battle
        """
        self.metrics["total_battles"] += 1
        self.metrics["training_episodes"] += 1
        
        if won:
            self.metrics["wins"] += 1
            self.metrics["current_streak"] += 1
            self.metrics["best_streak"] = max(
                self.metrics["best_streak"],
                self.metrics["current_streak"]
            )
        else:
            self.metrics["losses"] += 1
            self.metrics["current_streak"] = 0
        
        # Update opponent-specific stats
        if opponent_type == 'human':
            self.metrics["vs_humans_battles"] += 1
            if won:
                self.metrics["vs_humans_wins"] += 1
        else:
            self.metrics["vs_bots_battles"] += 1
            if won:
                self.metrics["vs_bots_wins"] += 1
            
            # Track per-bot stats
            if opponent_name not in self.metrics["vs_bots"]:
                self.metrics["vs_bots"][opponent_name] = {
                    "battles": 0,
                    "wins": 0,
                    "losses": 0,
                }
            
            self.metrics["vs_bots"][opponent_name]["battles"] += 1
            if won:
                self.metrics["vs_bots"][opponent_name]["wins"] += 1
            else:
                self.metrics["vs_bots"][opponent_name]["losses"] += 1
        
        # Update reward tracking
        self.metrics["total_reward"] += reward
        self.metrics["average_reward"] = (
            self.metrics["total_reward"] / self.metrics["training_episodes"]
        )
        
        # Update recent performance
        self.recent_results.append(won)
        recent_wins = sum(self.recent_results)
        self.metrics["recent_total"] = len(self.recent_results)
        self.metrics["recent_wins"] = recent_wins
        
        self.metrics["last_updated"] = datetime.now().isoformat()
        
        self.save()
    
    def save(self):
        """Save metrics to file."""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        temp_path = self.output_file + ".tmp"
        with open(temp_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        os.rename(temp_path, self.output_file)
    
    def get_win_rate(self) -> float:
        """Overall win rate percentage."""
        if self.metrics["total_battles"] == 0:
            return 0.0
        return (self.metrics["wins"] / self.metrics["total_battles"]) * 100
    
    def get_win_rate_vs_humans(self) -> float:
        """Win rate vs human opponents."""
        if self.metrics["vs_humans_battles"] == 0:
            return 0.0
        return (self.metrics["vs_humans_wins"] / self.metrics["vs_humans_battles"]) * 100
    
    def get_win_rate_vs_bots(self) -> float:
        """Win rate vs bot opponents."""
        if self.metrics["vs_bots_battles"] == 0:
            return 0.0
        return (self.metrics["vs_bots_wins"] / self.metrics["vs_bots_battles"]) * 100
    
    def get_recent_win_rate(self) -> float:
        """Win rate for last 100 battles."""
        if self.metrics["recent_total"] == 0:
            return 0.0
        return (self.metrics["recent_wins"] / self.metrics["recent_total"]) * 100
    
    def generate_stream_overlay(self) -> str:
        """Generate text for OBS overlay."""
        overall_wr = self.get_win_rate()
        vs_human_wr = self.get_win_rate_vs_humans()
        vs_bot_wr = self.get_win_rate_vs_bots()
        recent_wr = self.get_recent_win_rate()
        
        text = f"""╔══════════════════════════════════════════════════════╗
║  {self.agent_name:^50s}  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Total Battles: {self.metrics['total_battles']:>5}                            ║
║  Overall Win Rate: {overall_wr:>5.1f}%                         ║
║  Recent (100): {recent_wr:>5.1f}%                              ║
║                                                      ║
║  Record: {self.metrics['wins']:>4}W - {self.metrics['losses']:>4}L                             ║
║  Current Streak: {self.metrics['current_streak']:>3}                             ║
║  Best Streak: {self.metrics['best_streak']:>3}                                ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  VS HUMANS:  {self.metrics['vs_humans_battles']:>4} battles  |  {vs_human_wr:>5.1f}% win rate  ║
║  VS BOTS:    {self.metrics['vs_bots_battles']:>4} battles  |  {vs_bot_wr:>5.1f}% win rate  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Training Progress:                                  ║
║    Episodes: {self.metrics['training_episodes']:>5}                                ║
║    Avg Reward: {self.metrics['average_reward']:>+7.2f}                            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
        
        return text
    
    def save_stream_overlay(self, output_path: str):
        """Save overlay text to file for OBS."""
        overlay_text = self.generate_stream_overlay()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(overlay_text)
