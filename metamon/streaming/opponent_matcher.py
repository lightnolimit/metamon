"""Opponent matching system: bot opponents and live agent coordination"""

import time
import logging
import random
from typing import Optional, Dict, Any
from dataclasses import dataclass

from metamon.baselines import get_baseline
from metamon.streaming.agent_naming import get_naming_manager

logger = logging.getLogger(__name__)


@dataclass
class OpponentInfo:
    """Information about an opponent."""
    opponent_type: str  # 'human' or 'bot'
    name: str
    baseline_class: Optional[Any] = None  # For bot opponents
    is_ladder_match: bool = False


class OpponentMatcher:
    """Manages bot opponents for Mystery-Gift multi-agent system.

    Strategy:
    1. Provide bot opponents with curriculum difficulty progression
    2. Rotate through different bot types for varied training
    3. Support unified naming system for multi-agent coordination
    """

    def __init__(
        self,
        bot_rotation: list = None,
    ):
        """Initialize opponent matcher.

        Args:
            bot_rotation: List of bot baseline names to rotate through
        """
        # Default bot rotation with curriculum progression
        if bot_rotation is None:
            self.bot_rotation = [
                "RandomBaseline",  # Easy warmup
                "Grunt",           # Medium
                "GymLeader",       # Hard
                "EmeraldKaizo",    # Very hard
            ]
        else:
            self.bot_rotation = bot_rotation

        self.current_bot_index = 0

        # Initialize naming manager for unified agent naming
        self.naming_manager = get_naming_manager()
    
    def find_opponent(self) -> OpponentInfo:
        """Find an opponent (bot only in multi-agent system).

        Returns:
            OpponentInfo with opponent details
        """
        # In multi-agent system, human matching is handled by live agents
        # This method only provides bot opponents for main agent
        return self._get_bot_opponent()
    
    def _get_bot_opponent(self) -> OpponentInfo:
        """Select a bot opponent.
        
        Rotates through available bots in a curriculum fashion.
        
        Returns:
            OpponentInfo with bot details
        """
        bot_name = self.bot_rotation[self.current_bot_index]
        self.current_bot_index = (self.current_bot_index + 1) % len(self.bot_rotation)
        
        # Add some variety by occasionally randomizing
        if random.random() < 0.2:
            bot_name = random.choice(self.bot_rotation)
        
        logger.info(f"Selected bot opponent: {bot_name}")
        
        return OpponentInfo(
            opponent_type='bot',
            name=bot_name,
            baseline_class=get_baseline(bot_name),
            is_ladder_match=False,
        )
    
    def get_opponent_display_name(self, opponent: OpponentInfo) -> str:
        """Get display name for opponent.

        Args:
            opponent: OpponentInfo object

        Returns:
            Display name for overlay (e.g., "Scout-1234" or "Human-Player123")
        """
        if opponent.opponent_type == 'human':
            return opponent.name
        else:
            # For bots, add a random suffix like the agent names
            # Ensure total name length doesn't exceed 18 characters (Pokemon Showdown limit)
            suffix = ''.join(str(random.randint(0, 9)) for _ in range(4))
            max_opponent_name_len = 18 - len("-") - len(suffix)  # Reserve space for dash and suffix
            truncated_name = opponent.name[:max_opponent_name_len]
            return f"{truncated_name}-{suffix}"

    def get_next_agent_username(self, agent_type: str = 'b') -> str:
        """Get next username for a new agent using unified naming system.

        Args:
            agent_type: Agent type ('b' for bot, 'l' for live)

        Returns:
            Username in format: mysgift-{type}-{counter:08d}
        """
        return self.naming_manager.get_next_username(agent_type)

    def get_current_agent_count(self) -> int:
        """Get current agent count from naming manager.

        Returns:
            Current global counter value
        """
        return self.naming_manager.get_current_counter()
