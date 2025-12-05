#!/bin/bash

# Mystery-Gift Training Stream Launcher
# Follows single agent improving via RL

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Mystery-Gift RL Training Stream Launcher           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Find Python in conda metamon environment if available
PYTHON_CMD="python3"
if [ -d "/opt/homebrew/Caskroom/miniconda/base/envs/metamon/bin" ]; then
    PYTHON_CMD="/opt/homebrew/Caskroom/miniconda/base/envs/metamon/bin/python3"
fi

# Check if metamon is installed
if ! $PYTHON_CMD -c "import metamon" 2>/dev/null; then
    echo -e "${RED}ERROR: Metamon not installed. Run: pip install -e .${NC}"
    exit 1
fi

# Set cache directory
if [ -z "$METAMON_CACHE_DIR" ]; then
    export METAMON_CACHE_DIR="$SCRIPT_DIR/.cache"
    echo -e "${YELLOW}Using cache directory: $METAMON_CACHE_DIR${NC}"
fi

# Check Showdown server
echo -e "${YELLOW}[1/3] Checking Pokemon Showdown server...${NC}"

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Server running on port 8000${NC}"
else
    echo -e "${YELLOW}Starting Pokemon Showdown server...${NC}"
    cd server/pokemon-showdown
    
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    nohup node pokemon-showdown start --no-security > ../../showdown.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > ../../.showdown.pid
    
    sleep 5
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
    else
        echo -e "${RED}ERROR: Server failed to start${NC}"
        exit 1
    fi
    
    cd "$SCRIPT_DIR"
fi

# Clean old replays
echo -e "${YELLOW}[2/3] Cleaning old replays...${NC}"
rm -f stream_data/*/html_replays/*.html 2>/dev/null
echo -e "${GREEN}✓ Ready for fresh start${NC}"

# Start Mystery-Gift stream
echo -e "${YELLOW}[3/3] Starting Mystery-Gift stream...${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Mystery-Gift is going live!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "  🤖 Following: Mystery-Gift (RL Agent)"
echo "  🎮 Browser will open showing all battles"
echo "  📊 Stats: stream_data/mystery_gift_stats/"
echo "  🎥 Capture browser window in OBS"
echo ""
echo "  Press Ctrl+C to stop"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

# Cleanup handler
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping stream...${NC}"
    
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
    
    echo -e "${GREEN}Stream stopped. Mystery-Gift will be back!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run Mystery-Gift stream
$PYTHON_CMD << 'PYTHON_SCRIPT'
import mystery_gift_config
from metamon.streaming import start_mystery_gift_stream

config = mystery_gift_config.get_mystery_gift_config()

start_mystery_gift_stream(
    battle_format=config['battle_format'],
    output_dir=config['output_dir'],
    team_set=config['team_set'],
    enable_ladder=config['enable_ladder'],
    human_wait_timeout=config['human_wait_timeout'],
    use_pretrained=config['use_pretrained'],
    pretrained_model=config['pretrained_model'],
    max_battles=config['max_battles'],
)
PYTHON_SCRIPT

wait
