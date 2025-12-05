"""Tournament manager for 24/7 round-robin battles"""
import random
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from itertools import combinations

logger = logging.getLogger(__name__)


@dataclass
class TournamentAgent:
    """Configuration for a tournament participant."""
    name: str
    agent_type: str  # 'baseline', 'pretrained', or 'custom'
    agent_config: Dict  # Configuration specific to agent type
    team_set: str  # e.g., 'competitive', 'modern_replays'


@dataclass
class TournamentConfig:
    """Configuration for tournament mode."""
    battle_format: str = "gen1ou"
    battles_per_matchup: int = 3  # Best of 3
    shuffle_matchups: bool = True
    loop_forever: bool = True
    battle_backend: str = "metamon"


class TournamentManager:
    """Manage round-robin tournament between multiple agents."""
    
    def __init__(
        self,
        agents: List[TournamentAgent],
        config: TournamentConfig,
    ):
        """Initialize tournament manager.
        
        Args:
            agents: List of agents participating in tournament
            config: Tournament configuration
        """
        if len(agents) < 2:
            raise ValueError("Need at least 2 agents for a tournament")
        
        self.agents = agents
        self.config = config
        self.matchups = self._generate_matchups()
        self.current_matchup_index = 0
        self.round_number = 1
        
        logger.info(f"Tournament initialized with {len(agents)} agents")
        logger.info(f"Total matchups per round: {len(self.matchups)}")
    
    def _generate_matchups(self) -> List[Tuple[TournamentAgent, TournamentAgent]]:
        """Generate all possible matchups (round-robin)."""
        matchups = list(combinations(self.agents, 2))
        
        if self.config.shuffle_matchups:
            random.shuffle(matchups)
        
        return matchups
    
    def get_next_matchup(self) -> Optional[Tuple[TournamentAgent, TournamentAgent]]:
        """Get the next matchup to play.
        
        Returns:
            Tuple of (agent1, agent2) or None if tournament is complete
        """
        if self.current_matchup_index >= len(self.matchups):
            if self.config.loop_forever:
                # Start new round
                self.current_matchup_index = 0
                self.round_number += 1
                logger.info(f"Starting round {self.round_number}")
                
                if self.config.shuffle_matchups:
                    random.shuffle(self.matchups)
            else:
                # Tournament complete
                return None
        
        matchup = self.matchups[self.current_matchup_index]
        self.current_matchup_index += 1
        
        return matchup
    
    def create_baseline_agent(self, agent: TournamentAgent):
        """Create a baseline agent instance."""
        from metamon.baselines import get_baseline
        
        baseline_class = get_baseline(agent.agent_config['baseline_name'])
        return baseline_class
    
    def create_pretrained_agent(self, agent: TournamentAgent):
        """Create a pretrained agent instance."""
        try:
            from metamon.rl.pretrained import get_pretrained_model
        except ImportError:
            raise ImportError(
                "Pretrained agents require AMAGO. Install with: pip install amago-rl"
            )
        
        model_name = agent.agent_config['model_name']
        checkpoint = agent.agent_config.get('checkpoint', None)
        
        pretrained = get_pretrained_model(model_name)
        return pretrained.initialize_agent(checkpoint=checkpoint, log=False)
    
    def get_agent_info(self, agent: TournamentAgent) -> Dict:
        """Get agent information for environment setup.
        
        Returns:
            Dict with keys: observation_space, action_space, reward_function, agent_instance
        """
        if agent.agent_type == 'baseline':
            from metamon.interface import (
                DefaultObservationSpace,
                DefaultActionSpace,
                DefaultShapedReward,
            )
            
            return {
                'observation_space': DefaultObservationSpace(),
                'action_space': DefaultActionSpace(),
                'reward_function': DefaultShapedReward(),
                'opponent_type': self.create_baseline_agent(agent),
                'is_baseline': True,
            }
        
        elif agent.agent_type == 'pretrained':
            try:
                from metamon.rl.pretrained import get_pretrained_model
            except ImportError:
                raise ImportError(
                    "Pretrained agents require AMAGO. Install with: pip install amago-rl"
                )
            
            pretrained_model = get_pretrained_model(agent.agent_config['model_name'])
            
            return {
                'observation_space': pretrained_model.observation_space,
                'action_space': pretrained_model.action_space,
                'reward_function': pretrained_model.reward_function,
                'agent_instance': self.create_pretrained_agent(agent),
                'is_baseline': False,
            }
        
        else:
            raise ValueError(f"Unknown agent type: {agent.agent_type}")
    
    def get_tournament_summary(self) -> str:
        """Get a text summary of tournament configuration."""
        summary = "Tournament Configuration:\n"
        summary += f"  Format: {self.config.battle_format}\n"
        summary += f"  Battles per matchup: {self.config.battles_per_matchup}\n"
        summary += f"  Total agents: {len(self.agents)}\n"
        summary += f"  Matchups per round: {len(self.matchups)}\n"
        summary += f"  Current round: {self.round_number}\n"
        summary += "\nParticipants:\n"
        
        for agent in self.agents:
            summary += f"  - {agent.name} ({agent.agent_type})\n"
        
        return summary


def create_default_tournament(battle_format: str = "gen1ou") -> Tuple[List[TournamentAgent], TournamentConfig]:
    """Create a default tournament with common baselines.
    
    Args:
        battle_format: Battle format to use
    
    Returns:
        Tuple of (agents, config)
    """
    agents = [
        TournamentAgent(
            name="Lass",
            agent_type="baseline",
            agent_config={"baseline_name": "GymLeader"},
            team_set="competitive",
        ),
        TournamentAgent(
            name="Scout",
            agent_type="baseline",
            agent_config={"baseline_name": "Grunt"},
            team_set="competitive",
        ),
        TournamentAgent(
            name="Ace",
            agent_type="baseline",
            agent_config={"baseline_name": "EmeraldKaizo"},
            team_set="competitive",
        ),
        TournamentAgent(
            name="Newbie",
            agent_type="baseline",
            agent_config={"baseline_name": "RandomBaseline"},
            team_set="competitive",
        ),
    ]
    
    config = TournamentConfig(
        battle_format=battle_format,
        battles_per_matchup=3,
        shuffle_matchups=True,
        loop_forever=True,
    )
    
    return agents, config
