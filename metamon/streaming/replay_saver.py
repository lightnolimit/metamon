"""Generate HTML replays from Pokemon Showdown battle logs"""
import os
from typing import Optional


def generate_replay_html(
    battle_log: str,
    battle_id: str,
    player_name: str = "Player1",
    opponent_name: str = "Player2",
    battle_format: str = "gen1ou",
) -> str:
    """Generate standalone HTML replay file from battle log.
    
    Args:
        battle_log: Raw Pokemon Showdown battle log (pipe-separated format)
        battle_id: Unique identifier for this battle
        player_name: Name of the player (shown in replay)
        opponent_name: Name of the opponent
        battle_format: Battle format (e.g., gen1ou, gen2ou)
    
    Returns:
        Complete HTML string ready to be written to file
    """
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>{player_name} vs {opponent_name} - {battle_format.upper()}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            font-family: Verdana, sans-serif;
        }}
        .battle-log {{
            display: none;
        }}
    </style>
</head>
<body>
<script type="text/plain" class="battle-log-data">{battle_log}</script>
<script src="https://play.pokemonshowdown.com/js/replay-embed.js"></script>
</body>
</html>'''


def save_replay_html(
    battle_log: str,
    battle_id: str,
    output_dir: str,
    player_name: str = "Player1",
    opponent_name: str = "Player2",
    battle_format: str = "gen1ou",
) -> str:
    """Save HTML replay to file.
    
    Args:
        battle_log: Raw Pokemon Showdown battle log
        battle_id: Unique identifier for this battle
        output_dir: Directory to save HTML file
        player_name: Name of the player
        opponent_name: Name of the opponent
        battle_format: Battle format
    
    Returns:
        Path to saved HTML file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    html_content = generate_replay_html(
        battle_log=battle_log,
        battle_id=battle_id,
        player_name=player_name,
        opponent_name=opponent_name,
        battle_format=battle_format,
    )
    
    filepath = os.path.join(output_dir, f"battle-{battle_id}.html")
    
    # Atomic write to avoid partial files
    temp_path = filepath + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    os.rename(temp_path, filepath)
    
    return filepath


def extract_battle_log_from_battle(battle) -> str:
    """Extract battle log from poke-env Battle object.
    
    Args:
        battle: poke_env Battle object
    
    Returns:
        Raw battle log string
    """
    # Try multiple methods to get battle log
    if hasattr(battle, 'battle_tag') and hasattr(battle, 'logs'):
        # Newer poke-env versions
        return '\n'.join(battle.logs.get(battle.battle_tag, []))
    elif hasattr(battle, '_battle_log'):
        # Older versions
        return '\n'.join(battle._battle_log)
    elif hasattr(battle, 'get_showdown_log'):
        return battle.get_showdown_log()
    else:
        # Fallback: try to reconstruct from available data
        return f"|player|p1|{battle.player_username}|\n|player|p2|{battle.opponent_username}|\n"
