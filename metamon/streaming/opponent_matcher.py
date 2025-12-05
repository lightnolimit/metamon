"""Opponent matching system: human opponents or bot fallback"""

import time
import logging
import random
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from metamon.baselines import get_baseline

logger = logging.getLogger(__name__)


@dataclass
class OpponentInfo:
    """Information about an opponent."""
    opponent_type: str  # 'human' or 'bot'
    name: str
    baseline_class: Optional[Any] = None  # For bot opponents
    is_ladder_match: bool = False


class OpponentMatcher:
    """Manages finding opponents for Mystery-Gift.
    
    Strategy:
    1. Wait for human opponents on ladder (60s timeout)
    2. If no human, select a bot opponent
    3. Rotate through bots or use curriculum
    """
    
    def __init__(
        self,
        human_wait_timeout: int = 60,
        bot_rotation: list = None,
    ):
        """Initialize opponent matcher.
        
        Args:
            human_wait_timeout: Seconds to wait for human opponent
            bot_rotation: List of bot baseline names to rotate through
        """
        self.human_wait_timeout = human_wait_timeout
        
        # Default bot rotation
        if bot_rotation is None:
            self.bot_rotation = [
                "RandomBaseline",
                "Grunt",
                "GymLeader",
                "EmeraldKaizo",
            ]
        else:
            self.bot_rotation = bot_rotation
        
        self.current_bot_index = 0
        self.battles_completed = 0
    
    def find_opponent(self, enable_ladder: bool = False) -> OpponentInfo:
        """Find an opponent (human or bot).
        
        Args:
            enable_ladder: Whether to wait for human opponents
        
        Returns:
            OpponentInfo with opponent details
        """
        if enable_ladder:
            # Try to find human opponent
            human = self._wait_for_human()
            if human:
                return human
        
        # Fall back to bot opponent
        return self._get_bot_opponent()
    
    def _wait_for_human(self) -> Optional[OpponentInfo]:
        """Wait for human opponent on ladder.
        
        This is a placeholder for now. Full implementation would:
        - Use QueueOnLocalLadder
        - Actually wait for incoming challenges
        - Return opponent info when someone connects
        
        Returns:
            OpponentInfo if human found, None otherwise
        """
        logger.info(f"Waiting {self.human_wait_timeout}s for human opponent...")
        
        # TODO: Implement actual ladder waiting logic
        # For now, just wait and return None (always use bots)
        # In the future, this would check for incoming challenges
        
        start_time = time.time()
        while time.time() - start_time < self.human_wait_timeout:
            # Check for incoming challenges (not implemented yet)
            time.sleep(1)
        
        logger.info("No human opponent found, using bot")
        return None
    
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
            suffix = ''.join(str(random.randint(0, 9)) for _ in range(4))
            return f"{opponent.name}-Bot-{suffix}"
