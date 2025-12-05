#!/bin/bash

# Metamon 24/7 Tournament Stream Launcher
# This script starts everything needed for streaming battles to OBS

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      Metamon 24/7 Tournament Stream Launcher               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# =============================================================================
# 1. Check Dependencies
# =============================================================================

echo -e "${YELLOW}[1/4] Checking dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js not found. Please install Node.js${NC}"
    exit 1
fi

# Check if Playwright is installed
if ! python3 -c "import playwright" 2>/dev/null; then
    echo -e "${YELLOW}Playwright not found. Installing...${NC}"
    pip install playwright
    playwright install chromium
fi

# Check if metamon is installed
if ! python3 -c "import metamon" 2>/dev/null; then
    echo -e "${RED}ERROR: Metamon not installed. Run: pip install -e .${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies OK${NC}"
echo ""

# =============================================================================
# 2. Start Pokemon Showdown Server
# =============================================================================

echo -e "${YELLOW}[2/4] Starting Pokemon Showdown server...${NC}"

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Server already running on port 8000${NC}"
else
    cd server/pokemon-showdown
    
    # Check if npm modules are installed
    if [ ! -d "node_modules" ]; then
        echo "Installing Pokemon Showdown dependencies..."
        npm install
    fi
    
    # Start server in background
    echo "Starting Pokemon Showdown server..."
    nohup node pokemon-showdown start --no-security > ../../showdown.log 2>&1 &
    SERVER_PID=$!
    
    # Save PID for cleanup
    echo $SERVER_PID > ../../.showdown.pid
    
    # Wait for server to start
    echo "Waiting for server to start..."
    sleep 5
    
    # Check if server started successfully
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Pokemon Showdown server started (PID: $SERVER_PID)${NC}"
        echo "  Log: showdown.log"
    else
        echo -e "${RED}ERROR: Server failed to start. Check showdown.log${NC}"
        exit 1
    fi
    
    cd "$SCRIPT_DIR"
fi

echo ""

# =============================================================================
# 3. Configure Tournament
# =============================================================================

echo -e "${YELLOW}[3/4] Loading tournament configuration...${NC}"

if [ ! -f "stream_config.py" ]; then
    echo -e "${RED}ERROR: stream_config.py not found${NC}"
    exit 1
fi

# Display config info
python3 -c "
import stream_config
config = stream_config.get_tournament_config()
agents = stream_config.get_tournament_agents()

print(f'  Format: {config.battle_format}')
print(f'  Battles per matchup: {config.battles_per_matchup}')
print(f'  Participants: {len(agents)}')
for agent in agents:
    print(f'    - {agent.name} ({agent.agent_type})')
"

echo -e "${GREEN}✓ Configuration loaded${NC}"
echo ""

# =============================================================================
# 4. Start Tournament Stream
# =============================================================================

# Set cache directory if not set
if [ -z "$METAMON_CACHE_DIR" ]; then
    export METAMON_CACHE_DIR="$SCRIPT_DIR/.cache"
    echo "  Using cache directory: $METAMON_CACHE_DIR"
fi

# Clean old replays for fresh start
echo -e "${YELLOW}Cleaning old replays for fresh start...${NC}"
if [ -d "stream_data/gen1ou/html_replays" ]; then
    rm -f stream_data/gen1ou/html_replays/*.html
    echo "  ✓ Removed old HTML replays"
fi
if [ -d "stream_data/gen2ou/html_replays" ]; then
    rm -f stream_data/gen2ou/html_replays/*.html
fi
if [ -d "stream_data/gen3ou/html_replays" ]; then
    rm -f stream_data/gen3ou/html_replays/*.html
fi
if [ -d "stream_data/gen4ou/html_replays" ]; then
    rm -f stream_data/gen4ou/html_replays/*.html
fi
if [ -d "stream_data/gen9ou/html_replays" ]; then
    rm -f stream_data/gen9ou/html_replays/*.html
fi

echo -e "${YELLOW}[4/4] Starting tournament stream...${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Tournament stream is starting!${NC}"
echo -e "${GREEN}  ═══════════════════════════════════════════════════${NC}"
echo ""
echo "  🎮 Battle replays will appear in a browser window"
echo "  📊 Stats available in: ./stream_data/tournament_stats/"
echo "  🎥 Capture the browser window in OBS"
echo ""
echo "  Press Ctrl+C to stop the stream"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping stream...${NC}"
    
    # Kill tournament stream
    if [ ! -z "$TOURNAMENT_PID" ]; then
        kill $TOURNAMENT_PID 2>/dev/null || true
    fi
    
    # Optionally stop Showdown server
    read -p "Stop Pokemon Showdown server? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f ".showdown.pid" ]; then
            SHOWDOWN_PID=$(cat .showdown.pid)
            kill $SHOWDOWN_PID 2>/dev/null || true
            rm .showdown.pid
            echo -e "${GREEN}✓ Server stopped${NC}"
        fi
    fi
    
    echo -e "${GREEN}Stream stopped. Thanks for watching!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start the tournament stream
python3 << 'PYTHON_SCRIPT'
import stream_config
from metamon.streaming import start_tournament_stream

agents = stream_config.get_tournament_agents()
config = stream_config.get_tournament_config()

start_tournament_stream(
    battle_format=config.battle_format,
    output_dir=stream_config.OUTPUT_DIR,
    agents=agents,
    config=config,
)
PYTHON_SCRIPT

TOURNAMENT_PID=$!

# Wait for process
wait $TOURNAMENT_PID
