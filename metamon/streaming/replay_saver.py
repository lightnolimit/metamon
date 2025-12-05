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
    
    <!-- Base URL so all assets load from Pokemon Showdown CDN -->
    <!-- Removed to fix CORS issues when viewing local files -->
    <!-- <base href="https://play.pokemonshowdown.com/" />
    
    <!-- Load Pokemon Showdown CSS for proper replay rendering -->
    <link rel="stylesheet" href="https://play.pokemonshowdown.com/style/battle.css" />
    <link rel="stylesheet" href="https://play.pokemonshowdown.com/style/replay.css" />
    
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Verdana, sans-serif;
        }}
        /* Show the battle log by default */
        .battle-log {{
            display: block !important;
        }}
        /* Full screen layout for streaming */
        .ps-room {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }}
    </style>
</head>
<body>
<!-- Container for Pokemon Showdown replay -->
<div class="ps-room ps-room-opaque" data-battle>
    <div class="battle">
        <div class="battle-log" data-log></div>
    </div>
</div>

<!-- Battle data -->
<script type="text/plain" class="battle-log-data">{battle_log}</script>

<!-- Pokemon Showdown replay embed script -->
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
        battle: poke_env Battle object (MetamonBackendBattle or similar)
    
    Returns:
        Raw battle log string in Pokemon Showdown format
    """
    battle_log_lines = []
    
    # Method 1: Check for _raw_battle_log (MetamonBackendBattle)
    if hasattr(battle, '_raw_battle_log'):
        battle_log_lines = battle._raw_battle_log
    
    # Method 2: Check for _received_messages (standard poke-env)
    elif hasattr(battle, '_received_messages'):
        for messages in battle._received_messages.values():
            if isinstance(messages, list):
                battle_log_lines.extend(messages)
            else:
                battle_log_lines.append(str(messages))
    
    # Method 3: Check battle_tag and logs dict
    elif hasattr(battle, 'battle_tag') and hasattr(battle, 'logs'):
        battle_log_lines = battle.logs.get(battle.battle_tag, [])
    
    # Method 4: Check _battle_log
    elif hasattr(battle, '_battle_log'):
        battle_log_lines = battle._battle_log
    
    # Join all lines into a single string
    if battle_log_lines:
        # Make sure each line starts with | if it doesn't already
        formatted_lines = []
        for line in battle_log_lines:
            line_str = str(line)
            if line_str and not line_str.startswith('|'):
                line_str = '|' + line_str
            formatted_lines.append(line_str)
        return '\n'.join(formatted_lines)
    
    # Fallback: minimal log (this won't make a playable replay)
    return f"|player|p1|{battle.player_username}|\n|player|p2|{battle.opponent_username}|\n|start\n"
