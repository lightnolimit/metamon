"""Mystery-Gift: The main RL agent that improves over time"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from metamon.env import get_metamon_teams, TeamSet
from metamon.interface import (
    DefaultObservationSpace,
    DefaultActionSpace,
    DefaultShapedReward,
    ObservationSpace,
    ActionSpace,
    RewardFunction,
)

logger = logging.getLogger(__name__)


class MysteryGiftAgent:
    """The main RL agent that improves over time through battles.
    
    Mystery-Gift is a single persistent agent that:
    - Battles humans when available
    - Trains against bots otherwise
    - Improves via online RL
    - Has dedicated teams for each format
    """
    
    def __init__(
        self,
        battle_format: str = "gen1ou",
        base_name: str = "Mystery-Gift",
        team_set: str = "competitive",
        use_pretrained: bool = False,
        pretrained_model: Optional[str] = None,
    ):
        """Initialize Mystery-Gift agent.
        
        Args:
            battle_format: Pokemon format (gen1ou, gen2ou, etc.)
            base_name: Agent's display name
            team_set: Which team set to use
            use_pretrained: Whether to use a pretrained RL model
            pretrained_model: Name of pretrained model (e.g., "SyntheticRLV2")
        """
        self.base_name = base_name
        self.battle_format = battle_format
        self.team_set_name = team_set
        
        # Load teams
        self.team_set = get_metamon_teams(battle_format, team_set)
        
        # Set up observation/action/reward spaces
        self.observation_space = DefaultObservationSpace()
        self.action_space = DefaultActionSpace()
        self.reward_function = DefaultShapedReward()
        
        # RL Policy (can be None for random, or a trained model)
        self.rl_policy = None
        if use_pretrained and pretrained_model:
            self.rl_policy = self._load_pretrained(pretrained_model)
        
        logger.info(f"Mystery-Gift initialized for {battle_format}")
        logger.info(f"  Team set: {team_set}")
        logger.info(f"  Policy: {pretrained_model if use_pretrained else 'Random baseline'}")
    
    def _load_pretrained(self, model_name: str):
        """Load a pretrained RL model."""
        try:
            from metamon.rl.pretrained import get_pretrained_model
            
            pretrained = get_pretrained_model(model_name)
            agent = pretrained.initialize_agent(log=False)
            
            # Update spaces to match pretrained model
            self.observation_space = pretrained.observation_space
            self.action_space = pretrained.action_space
            self.reward_function = pretrained.reward_function
            
            logger.info(f"Loaded pretrained model: {model_name}")
            return agent
        except ImportError:
            logger.warning("AMAGO not installed, cannot use pretrained models")
            return None
        except Exception as e:
            logger.error(f"Failed to load pretrained model: {e}")
            return None
    
    def select_action(self, obs, legal_actions):
        """Select action using RL policy or random baseline.
        
        Args:
            obs: Current observation
            legal_actions: List of legal action indices
        
        Returns:
            Selected action index
        """
        if self.rl_policy:
            # Use trained policy
            # This would need proper integration with AMAGO
            # For now, fallback to random
            import random
            return random.choice(legal_actions) if legal_actions else 0
        else:
            # Random policy
            import random
            return random.choice(legal_actions) if legal_actions else 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get agent configuration for environment setup."""
        return {
            'observation_space': self.observation_space,
            'action_space': self.action_space,
            'reward_function': self.reward_function,
            'team_set': self.team_set,
        }
