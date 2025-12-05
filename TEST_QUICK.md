# Quick Test

To verify everything is working:

```bash
# 1. Set cache directory
export METAMON_CACHE_DIR=/Users/area/repos/metamon/.cache

# 2. Run ONE battle test (no viewer)
python3 -c "
import os
os.makedirs('./test_run', exist_ok=True)

from metamon.env import BattleAgainstBaseline, get_metamon_teams
from metamon.baselines import get_baseline
from metamon.interface import DefaultObservationSpace, DefaultActionSpace, DefaultShapedReward

env = BattleAgainstBaseline(
    battle_format='gen1ou',
    observation_space=DefaultObservationSpace(),
    action_space=DefaultActionSpace(),
    reward_function=DefaultShapedReward(),
    team_set=get_metamon_teams('gen1ou', 'competitive'),
    opponent_type=get_baseline('RandomBaseline'),
    save_trajectories_to='./test_run',
    battle_backend='metamon',
)

print('Starting test battle...')
state, info = env.reset()
done = False
turns = 0

while not done and turns < 100:
    action = env.action_space.sample()
    state, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    turns += 1

print(f'Battle complete in {turns} turns')
print(f'Result: {\"WIN\" if info.get(\"won\") else \"LOSS\"}')

env.close()

# Check HTML was generated
import os
html_dir = './test_run/gen1ou/html_replays'
if os.path.exists(html_dir):
    html_files = os.listdir(html_dir)
    print(f'HTML replays generated: {len(html_files)}')
    if html_files:
        print(f'  Example: {html_files[0]}')
        print('  Open in browser to verify!')
else:
    print('ERROR: No HTML replays generated')
"

# 3. Check the output
ls -lh test_run/gen1ou/html_replays/
```

If you see HTML files, everything works!

To run full tournament stream:
```bash
./RUN_STREAM.sh
```
