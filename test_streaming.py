#!/usr/bin/env python3
"""Quick test script to verify streaming setup"""

import sys

print("Testing Metamon Streaming Setup...")
print("=" * 60)

# Test 1: Check Python version
print("\n[1/6] Checking Python version...")
if sys.version_info < (3, 10):
    print("❌ Python 3.10+ required")
    sys.exit(1)
print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")

# Test 2: Check metamon installation
print("\n[2/6] Checking metamon installation...")
try:
    import metamon
    print("✓ Metamon installed")
except ImportError as e:
    print(f"❌ Metamon not installed: {e}")
    print("   Run: pip install -e .")
    sys.exit(1)

# Test 3: Check streaming module
print("\n[3/6] Checking streaming module...")
try:
    from metamon import streaming
    print("✓ Streaming module found")
except ImportError as e:
    print(f"❌ Streaming module error: {e}")
    sys.exit(1)

# Test 4: Check individual components
print("\n[4/6] Checking streaming components...")
try:
    from metamon.streaming import (
        ReplayViewer,
        TournamentManager,
        TournamentConfig,
        TournamentAgent,
        StatsTracker,
    )
    print("✓ All components imported")
except ImportError as e:
    print(f"❌ Component import failed: {e}")
    sys.exit(1)

# Test 5: Check Playwright (optional)
print("\n[5/6] Checking Playwright (optional)...")
try:
    import playwright
    print("✓ Playwright installed")
except ImportError:
    print("⚠️  Playwright not installed (required for auto-viewer)")
    print("   Run: pip install playwright && playwright install chromium")

# Test 6: Check Node.js (optional, for Showdown)
print("\n[6/6] Checking Node.js (optional)...")
import subprocess
try:
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True,
        text=True,
        timeout=2
    )
    if result.returncode == 0:
        print(f"✓ Node.js {result.stdout.strip()}")
    else:
        print("⚠️  Node.js not found (required for Showdown server)")
except Exception:
    print("⚠️  Node.js not found (required for Showdown server)")

# Test configuration
print("\n" + "=" * 60)
print("Testing configuration...")
print("=" * 60)

try:
    import stream_config
    
    config = stream_config.get_tournament_config()
    agents = stream_config.get_tournament_agents()
    
    print(f"\n✓ Configuration loaded")
    print(f"  Format: {config.battle_format}")
    print(f"  Battles per matchup: {config.battles_per_matchup}")
    print(f"  Agents: {len(agents)}")
    
    for agent in agents:
        print(f"    - {agent.name} ({agent.agent_type})")
    
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("SETUP STATUS")
print("=" * 60)

print("\n✓ Core streaming system ready!")
print("\nNext steps:")
print("  1. Install Playwright: pip install -r streaming_requirements.txt")
print("  2. Install Chromium: playwright install chromium")
print("  3. Start Showdown: cd server/pokemon-showdown && npm install")
print("  4. Run: ./start.sh")
print("\n" + "=" * 60)
