#!/usr/bin/env python3
"""Debug script to check battle log extraction"""

import os
os.environ['METAMON_CACHE_DIR'] = '/Users/area/repos/metamon/.cache'

from metamon.env import BattleAgainstBaseline, get_metamon_teams
from metamon.baselines import get_baseline
from metamon.interface import DefaultObservationSpace, DefaultActionSpace, DefaultShapedReward

print("Running debug battle to check log extraction...")

env = BattleAgainstBaseline(
    battle_format="gen1ou",
    observation_space=DefaultObservationSpace(),
    action_space=DefaultActionSpace(),
    reward_function=DefaultShapedReward(),
    team_set=get_metamon_teams("gen1ou", "competitive"),
    opponent_type=get_baseline("RandomBaseline"),
    battle_backend="metamon",
)

print("Starting battle...")
state, info = env.reset()
done = False
turns = 0

while not done and turns < 10:
    action = env.action_space.sample()
    state, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    turns += 1

print(f"\nBattle completed in {turns} turns")

# Now check what's in the battle object
battle = env.current_battle
print("\nBattle object attributes:")

# Check for various log attributes
if hasattr(battle, '_received_messages'):
    print(f"  _received_messages: {len(battle._received_messages)} entries")
    # Show first few
    for tag, msgs in list(battle._received_messages.items())[:2]:
        print(f"    {tag}: {len(msgs) if isinstance(msgs, list) else 1} messages")
        if isinstance(msgs, list) and msgs:
            print(f"      First: {msgs[0][:80]}...")

if hasattr(battle, 'battle_tag'):
    print(f"  battle_tag: {battle.battle_tag}")

if hasattr(battle, 'logs'):
    print(f"  logs: {type(battle.logs)}")
    if battle.battle_tag in battle.logs:
        print(f"    logs[battle_tag]: {len(battle.logs[battle.battle_tag])} lines")

if hasattr(battle, '_battle_log'):
    print(f"  _battle_log: {len(battle._battle_log)} lines")

# Try to extract log
from metamon.streaming.replay_saver import extract_battle_log_from_battle

battle_log = extract_battle_log_from_battle(battle)
print(f"\nExtracted battle log: {len(battle_log)} characters")
print(f"First 500 chars:\n{battle_log[:500]}")
print(f"\nLast 500 chars:\n{battle_log[-500:]}")

# Save a test HTML
from metamon.streaming.replay_saver import save_replay_html

html_path = save_replay_html(
    battle_log=battle_log,
    battle_id="debug-test",
    output_dir="./debug_replay",
    player_name=env.player_username,
    opponent_name="RandomBaseline",
    battle_format="gen1ou",
)

print(f"\nSaved test replay to: {html_path}")
print("Open this in a browser to check if it plays!")

env.close()
