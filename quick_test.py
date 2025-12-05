#!/usr/bin/env python3
"""Quick test to verify battle execution without viewer"""

import os
import logging

logging.basicConfig(level=logging.INFO)

print("Testing battle execution...")
print("=" * 60)

# Test imports
print("\n[1/4] Testing imports...")
try:
    from metamon.env import BattleAgainstBaseline, get_metamon_teams
    from metamon.baselines import get_baseline
    from metamon.interface import DefaultObservationSpace, DefaultActionSpace, DefaultShapedReward
    print("✓ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Create test directory
print("\n[2/4] Creating test directory...")
test_dir = "./test_run"
os.makedirs(test_dir, exist_ok=True)
print(f"✓ Created {test_dir}")

# Run a quick battle
print("\n[3/4] Running test battle...")
try:
    env = BattleAgainstBaseline(
        battle_format="gen1ou",
        observation_space=DefaultObservationSpace(),
        action_space=DefaultActionSpace(),
        reward_function=DefaultShapedReward(),
        team_set=get_metamon_teams("gen1ou", "competitive"),
        opponent_type=get_baseline("RandomBaseline"),
        save_trajectories_to=test_dir,
        battle_backend="metamon",
    )
    
    print("  Starting battle...")
    state, info = env.reset()
    done = False
    turns = 0
    
    while not done:
        action = env.action_space.sample()
        state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        turns += 1
        if turns % 5 == 0:
            print(f"    Turn {turns}...")
    
    won = info.get('won', False)
    print(f"✓ Battle complete! Result: {'WIN' if won else 'LOSS'} in {turns} turns")
    
    env.close()
    
except Exception as e:
    print(f"❌ Battle failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Check outputs
print("\n[4/4] Checking outputs...")
json_dir = os.path.join(test_dir, "gen1ou")
html_dir = os.path.join(test_dir, "gen1ou", "html_replays")

if os.path.exists(json_dir):
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.lz4')]
    print(f"✓ JSON trajectories: {len(json_files)} found")
else:
    print("⚠️  No JSON directory")

if os.path.exists(html_dir):
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    print(f"✓ HTML replays: {len(html_files)} found")
    if html_files:
        print(f"  Example: {html_files[0]}")
else:
    print("⚠️  No HTML replays directory")

print("\n" + "=" * 60)
print("✓ Test completed successfully!")
print("\nTo view the replay:")
print(f"  open {os.path.join(html_dir, html_files[0]) if html_files else 'test_run/gen1ou/html_replays/*.html'}")
print("\nReady to run full tournament with:")
print("  ./start.sh")
