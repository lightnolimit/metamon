"""Track RL training metrics for Mystery-Gift multi-agent system"""

import json
import os
import logging
import threading
from typing import Dict, Optional, Any
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


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


class SharedTrainingMetrics:
    """Thread-safe training metrics for multi-agent Mystery-Gift system.

    Aggregates statistics from all mysgift-* agents and maintains
    shared training state across concurrent battles.
    """

    def __init__(self, agent_name: str = "Mystery-Gift-MultiAgent", output_file: str = "./stream_data/mystery_gift_stats/shared_metrics.json"):
        """Initialize shared training metrics.

        Args:
            agent_name: Name for the agent system
            output_file: Path to save shared metrics
        """
        self.agent_name = agent_name
        self.output_file = output_file

        # Thread safety
        self._lock = threading.RLock()

        # Per-agent statistics for individual agent tracking
        self.agent_stats = {}  # {agent_id: {battles, wins, losses, rewards, opponent_type_counts}}

        # Combined statistics across all agents
        self.shared_metrics = {
            "system_name": agent_name,
            "active_agents": 0,
            "total_agents_created": 0,

            # Combined battle statistics
            "total_battles": 0,
            "wins": 0,
            "losses": 0,

            # Split by opponent type (aggregated)
            "vs_humans_battles": 0,
            "vs_humans_wins": 0,
            "vs_bots_battles": 0,
            "vs_bots_wins": 0,

            # Training metrics (aggregated)
            "training_episodes": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,

            # Performance tracking
            "current_streak": 0,
            "best_streak": 0,

            # Recent performance (last 200 battles across all agents)
            "recent_wins": 0,
            "recent_total": 0,

            # Time tracking
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

        # Circular buffer for recent battle results (larger for multi-agent)
        self.recent_results = deque(maxlen=200)

        # Load existing metrics if available
        self.load()

    def load(self):
        """Load existing shared metrics from file."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    saved = json.load(f)
                    self.shared_metrics.update(saved)

                    # Load per-agent stats if present
                    if "agent_stats" in saved:
                        self.agent_stats = saved["agent_stats"]

                    logger.info(f"Loaded shared metrics: {self.shared_metrics['total_battles']} battles, {len(self.agent_stats)} agents")
            except Exception as e:
                logger.warning(f"Could not load shared metrics: {e}")

    def update_agent_battle(
        self,
        agent_id: str,
        won: bool,
        opponent_type: str,
        opponent_name: str,
        reward: float = 0.0,
    ):
        """Thread-safe update from any agent's battle completion.

        Args:
            agent_id: Unique agent identifier (e.g., "mysgift-b-00000001")
            won: Whether this agent won the battle
            opponent_type: 'human' or 'bot'
            opponent_name: Name of the opponent
            reward: Total reward from battle for this agent
        """
        with self._lock:
            # Initialize agent stats if first battle
            if agent_id not in self.agent_stats:
                self.agent_stats[agent_id] = {
                    "battles": 0,
                    "wins": 0,
                    "losses": 0,
                    "rewards": [],
                    "vs_humans": 0,
                    "vs_bots": 0,
                    "created_at": datetime.now().isoformat(),
                    "last_battle": datetime.now().isoformat(),
                }
                self.shared_metrics["total_agents_created"] += 1

            # Update per-agent statistics
            agent_stats = self.agent_stats[agent_id]
            agent_stats["battles"] += 1
            agent_stats["last_battle"] = datetime.now().isoformat()

            if won:
                agent_stats["wins"] += 1
                self.shared_metrics["current_streak"] += 1
                self.shared_metrics["best_streak"] = max(
                    self.shared_metrics["best_streak"],
                    self.shared_metrics["current_streak"]
                )
            else:
                agent_stats["losses"] += 1
                self.shared_metrics["current_streak"] = 0

            # Track opponent types per agent
            if opponent_type == 'human':
                agent_stats["vs_humans"] += 1
            else:
                agent_stats["vs_bots"] += 1

            # Store reward
            agent_stats["rewards"].append(reward)
            # Keep only last 100 rewards per agent to prevent memory bloat
            if len(agent_stats["rewards"]) > 100:
                agent_stats["rewards"] = agent_stats["rewards"][-100:]

            # Update combined (shared) metrics
            self.shared_metrics["total_battles"] += 1
            self.shared_metrics["training_episodes"] += 1

            if won:
                self.shared_metrics["wins"] += 1
            else:
                self.shared_metrics["losses"] += 1

            # Update opponent-specific aggregated stats
            if opponent_type == 'human':
                self.shared_metrics["vs_humans_battles"] += 1
                if won:
                    self.shared_metrics["vs_humans_wins"] += 1
            else:
                self.shared_metrics["vs_bots_battles"] += 1
                if won:
                    self.shared_metrics["vs_bots_wins"] += 1

            # Update reward tracking
            self.shared_metrics["total_reward"] += reward
            if self.shared_metrics["training_episodes"] > 0:
                self.shared_metrics["average_reward"] = (
                    self.shared_metrics["total_reward"] / self.shared_metrics["training_episodes"]
                )

            # Update recent performance
            self.recent_results.append(won)
            recent_wins = sum(self.recent_results)
            self.shared_metrics["recent_total"] = len(self.recent_results)
            self.shared_metrics["recent_wins"] = recent_wins

            self.shared_metrics["last_updated"] = datetime.now().isoformat()

            # Update active agents count (agents with recent activity)
            self._update_active_agents()

            # Save to file
            self.save()

    def _update_active_agents(self):
        """Update count of currently active agents."""
        current_time = datetime.now()
        active_count = 0

        for agent_id, agent_stats in self.agent_stats.items():
            try:
                last_battle_time = datetime.fromisoformat(agent_stats["last_battle"])
                # Consider agent active if it had a battle in the last 5 minutes
                if (current_time - last_battle_time).total_seconds() < 300:
                    active_count += 1
            except (ValueError, KeyError):
                # Skip if date parsing fails
                continue

        self.shared_metrics["active_agents"] = active_count

    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status (e.g., 'active', 'idle', 'error').

        Args:
            agent_id: Agent identifier
            status: Current status of the agent
        """
        with self._lock:
            if agent_id not in self.agent_stats:
                self.agent_stats[agent_id] = {
                    "battles": 0,
                    "wins": 0,
                    "losses": 0,
                    "rewards": [],
                    "vs_humans": 0,
                    "vs_bots": 0,
                    "created_at": datetime.now().isoformat(),
                    "last_battle": datetime.now().isoformat(),
                    "status": status,
                }
                self.shared_metrics["total_agents_created"] += 1
            else:
                self.agent_stats[agent_id]["status"] = status
                self.agent_stats[agent_id]["last_updated"] = datetime.now().isoformat()

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent statistics dict or None if agent not found
        """
        with self._lock:
            return self.agent_stats.get(agent_id)

    def get_all_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents.

        Returns:
            Dict mapping agent_id to their statistics
        """
        with self._lock:
            return self.agent_stats.copy()

    def get_shared_metrics(self) -> Dict[str, Any]:
        """Get the combined shared metrics.

        Returns:
            Shared metrics dict
        """
        with self._lock:
            return self.shared_metrics.copy()

    def get_win_rate(self) -> float:
        """Overall win rate percentage across all agents."""
        if self.shared_metrics["total_battles"] == 0:
            return 0.0
        return (self.shared_metrics["wins"] / self.shared_metrics["total_battles"]) * 100

    def get_win_rate_vs_humans(self) -> float:
        """Win rate vs human opponents across all agents."""
        if self.shared_metrics["vs_humans_battles"] == 0:
            return 0.0
        return (self.shared_metrics["vs_humans_wins"] / self.shared_metrics["vs_humans_battles"]) * 100

    def get_win_rate_vs_bots(self) -> float:
        """Win rate vs bot opponents across all agents."""
        if self.shared_metrics["vs_bots_battles"] == 0:
            return 0.0
        return (self.shared_metrics["vs_bots_wins"] / self.shared_metrics["vs_bots_battles"]) * 100

    def get_recent_win_rate(self) -> float:
        """Win rate for last 200 battles across all agents."""
        if self.shared_metrics["recent_total"] == 0:
            return 0.0
        return (self.shared_metrics["recent_wins"] / self.shared_metrics["recent_total"]) * 100

    def get_top_performers(self, limit: int = 5) -> list:
        """Get top performing agents by win rate.

        Args:
            limit: Maximum number of agents to return

        Returns:
            List of (agent_id, win_rate, battles) tuples
        """
        performers = []

        for agent_id, stats in self.agent_stats.items():
            if stats["battles"] >= 5:  # Minimum battles to qualify
                win_rate = (stats["wins"] / stats["battles"]) * 100
                performers.append((agent_id, win_rate, stats["battles"]))

        # Sort by win rate (descending) and by battles (descending for ties)
        performers.sort(key=lambda x: (-x[1], -x[2]))
        return performers[:limit]

    def generate_multi_agent_overlay(self) -> str:
        """Generate text for multi-agent OBS overlay."""
        overall_wr = self.get_win_rate()
        vs_human_wr = self.get_win_rate_vs_humans()
        vs_bot_wr = self.get_win_rate_vs_bots()
        recent_wr = self.get_recent_win_rate()

        # Get top performers
        top_performers = self.get_top_performers(3)

        text = f"""╔══════════════════════════════════════════════════════╗
║  {self.agent_name:^50s}  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  System Statistics:                                   ║
║  Active Agents: {self.shared_metrics['active_agents']:>2}                             ║
║  Total Created: {self.shared_metrics['total_agents_created']:>3}                          ║
║  Total Battles: {self.shared_metrics['total_battles']:>5}                            ║
║  Overall Win Rate: {overall_wr:>5.1f}%                         ║
║  Recent (200): {recent_wr:>5.1f}%                              ║
║                                                      ║
║  Combined Record: {self.shared_metrics['wins']:>4}W - {self.shared_metrics['losses']:>4}L                    ║
║  Current Streak: {self.shared_metrics['current_streak']:>3}                             ║
║  Best Streak: {self.shared_metrics['best_streak']:>3}                                ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  VS HUMANS:  {self.shared_metrics['vs_humans_battles']:>4} battles  |  {vs_human_wr:>5.1f}% win rate  ║
║  VS BOTS:    {self.shared_metrics['vs_bots_battles']:>4} battles  |  {vs_bot_wr:>5.1f}% win rate  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Training Progress:                                  ║
║    Episodes: {self.shared_metrics['training_episodes']:>5}                                ║
║    Avg Reward: {self.shared_metrics['average_reward']:>+7.2f}                            ║
║                                                      ║"""

        # Add top performers section if we have enough data
        if top_performers:
            text += "║  Top Performers:                                      ║\n"
            for i, (agent_id, win_rate, battles) in enumerate(top_performers, 1):
                # Shorten agent ID for display
                short_id = agent_id[-10:] if len(agent_id) > 10 else agent_id
                text += f"║  {i}. {short_id:<10} | {win_rate:>5.1f}% | {battles:>3} battles        ║\n"

        text += "╚══════════════════════════════════════════════════════╝"

        return text

    def save(self):
        """Save shared metrics to file."""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        temp_path = self.output_file + ".tmp"

        # Combine shared metrics and agent stats
        save_data = self.shared_metrics.copy()
        save_data["agent_stats"] = self.agent_stats

        try:
            with open(temp_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            os.rename(temp_path, self.output_file)
        except IOError as e:
            logger.error(f"Failed to save shared metrics: {e}")

    def save_multi_agent_overlay(self, output_path: str):
        """Save multi-agent overlay text to file for OBS."""
        overlay_text = self.generate_multi_agent_overlay()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(overlay_text)
