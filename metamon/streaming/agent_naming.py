"""Agent naming system for Mystery-Gift multi-agent streaming.

Provides unified sequential numbering across all agent types with:
- Thread-safe global counter
- Persistent counter storage
- Agent type prefixing (b=bot, l=live)
- 18-character username limit compliance
"""

import os
import json
import threading
from typing import Optional
from pathlib import Path


class AgentNamingManager:
    """Manages sequential naming across all Mystery-Gift agents.

    Provides thread-safe sequential numbering with agent type prefixes:
    - mysgift-b-00000001 (bot agent)
    - mysgift-l-00000002 (live agent)
    - mysgift-b-00000003 (next bot agent)
    etc.
    """

    def __init__(self, persist_file: Optional[str] = None):
        """Initialize the naming manager.

        Args:
            persist_file: Path to counter persistence file. If None, uses default.
        """
        # Default to storing counter in stream_data directory
        if persist_file is None:
            persist_file = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "stream_data", "agent_counter.json"
            )

        self.counter_file = Path(persist_file)
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)

        # Thread safety
        self._lock = threading.RLock()
        self._counter = None

        # Load existing counter or start fresh
        self._load_counter()

    def _load_counter(self):
        """Load counter from persistent storage."""
        with self._lock:
            try:
                if self.counter_file.exists():
                    with open(self.counter_file, 'r') as f:
                        data = json.load(f)
                        self._counter = data.get('global_counter', 0)
                        # Validate counter is reasonable
                        if not isinstance(self._counter, int) or self._counter < 0:
                            self._counter = 0
                        elif self._counter > 99999999:  # Prevent overflow
                            self._counter = 99999999
                else:
                    self._counter = 0
                    self._save_counter()
            except (json.JSONDecodeError, IOError, ValueError) as e:
                # Start fresh if file is corrupted
                self._counter = 0
                self._save_counter()

    def _save_counter(self):
        """Save counter to persistent storage."""
        try:
            with open(self.counter_file, 'w') as f:
                json.dump({
                    'global_counter': self._counter,
                    'last_updated': str(self.counter_file.stat().st_mtime) if self.counter_file.exists() else None
                }, f, indent=2)
        except IOError:
            # Continue without persistence if save fails
            pass

    def get_next_username(self, agent_type: str = 'b') -> str:
        """Get next sequential username with type prefix.

        Args:
            agent_type: Agent type prefix ('b' for bot, 'l' for live)

        Returns:
            Username in format: mysgift-{type}-{counter:08d}

        Example:
            >>> naming = AgentNamingManager()
            >>> naming.get_next_username('b')
            'mysgift-b-00000001'
            >>> naming.get_next_username('l')
            'mysgift-l-00000002'
        """
        with self._lock:
            # Increment counter
            self._counter += 1

            # Prevent overflow
            if self._counter > 99999999:
                self._counter = 1  # Wrap around instead of overflow

            # Validate agent type
            valid_types = {'b', 'l'}  # bot, live
            if agent_type not in valid_types:
                agent_type = 'b'  # Default to bot

            # Generate username (18 chars max: mysgfit-b-12345678)
            username = f"mysgift-{agent_type}-{self._counter:08d}"

            # Save updated counter
            self._save_counter()

            # Validate username length
            assert len(username) <= 18, f"Username too long: {username} ({len(username)} chars)"

            return username

    def get_current_counter(self) -> int:
        """Get current counter value without incrementing.

        Returns:
            Current counter value
        """
        with self._lock:
            return self._counter

    def reset_counter(self, start_from: int = 0):
        """Reset counter to specific value.

        Args:
            start_from: Starting counter value
        """
        with self._lock:
            if 0 <= start_from <= 99999999:
                self._counter = start_from
                self._save_counter()
            else:
                raise ValueError("Counter must be between 0 and 99999999")

    def get_agent_type_from_username(self, username: str) -> Optional[str]:
        """Extract agent type from username.

        Args:
            username: Username in format mysgift-{type}-{number}

        Returns:
            Agent type ('b', 'l') or None if format invalid
        """
        try:
            # Expected format: mysgift-{type}-{number}
            parts = username.split('-')
            if len(parts) == 3 and parts[0] == 'mysgift' and parts[1] in {'b', 'l'}:
                return parts[1]
        except (AttributeError, IndexError):
            pass
        return None

    def get_counter_from_username(self, username: str) -> Optional[int]:
        """Extract counter number from username.

        Args:
            username: Username in format mysgift-{type}-{number}

        Returns:
            Counter number or None if format invalid
        """
        try:
            # Expected format: mysgift-{type}-{number}
            parts = username.split('-')
            if len(parts) == 3 and parts[0] == 'mysgift':
                return int(parts[2])
        except (AttributeError, IndexError, ValueError):
            pass
        return None


# Global instance for convenience
_global_naming_manager = None
_naming_lock = threading.Lock()


def get_naming_manager(persist_file: Optional[str] = None) -> AgentNamingManager:
    """Get global naming manager instance.

    Args:
        persist_file: Optional persistence file path

    Returns:
        AgentNamingManager instance
    """
    global _global_naming_manager

    with _naming_lock:
        if _global_naming_manager is None:
            _global_naming_manager = AgentNamingManager(persist_file)
        return _global_naming_manager


def reset_global_naming_manager(persist_file: Optional[str] = None):
    """Reset global naming manager instance.

    Args:
        persist_file: Optional persistence file path
    """
    global _global_naming_manager

    with _naming_lock:
        _global_naming_manager = AgentNamingManager(persist_file)