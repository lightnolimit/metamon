# OBS Widgets Guide for Mystery-Gift Streaming

This guide explains how to use the new OBS widget system for displaying Mystery-Gift training stats with flexible positioning.

## What Are OBS Widgets?

OBS widgets are individual text files that contain specific training stats. Each file can be added as a separate Text source in OBS, allowing you to position stats anywhere on your stream overlay with transparent backgrounds.

## Widget Files Location

All widget files are created in: `stream_data/mystery_gift_stats/widgets/`

## Available Widgets

| Widget File | Description | Format Example |
|-------------|-------------|----------------|
| `win_rate.txt` | Overall win rate percentage | `67.5%` |
| `battles.txt` | Total number of battles | `155` |
| `record.txt` | Wins-Losses record | `19W - 136L` |
| `current_streak.txt` | Current winning streak | `0` |
| `best_streak.txt` | Best streak achieved | `3` |
| `vs_humans.txt` | Human opponent stats | `0 battles (0.0% WR)` |
| `vs_bots.txt` | Bot opponent stats | `155 battles (12.3% WR)` |
| `recent_performance.txt` | Last 10 battle results | `W L W W L L W W L W` |
| `countdown.txt` | Time until next battle | `1:30` |
| `current_opponent.txt` | Current opponent name | `🤖 RandomBaseline-1234` |
| `search_status.txt` | Human opponent search status | `Searching for human opponents...` |

## Setup Instructions

### 1. Start Mystery-Gift Stream

```bash
./RUN_MYSTERY_GIFT.sh
```

The stream will automatically create widget files and display their paths:
```
OBS widgets created in: /Users/area/repos/metamon/stream_data/mystery_gift_stats/widgets
Add these as Text sources in OBS for flexible positioning:
  win_rate: file:///Users/area/repos/metamon/stream_data/mystery_gift_stats/widgets/win_rate.txt
  battles: file:///Users/area/repos/metamon/stream_data/mystery_gift_stats/widgets/battles.txt
  ...
```

### 2. Add Widgets to OBS

For each widget you want to display:

1. In OBS, add a new "Text" source
2. Select "Read from file"
3. Browse to the widget file in `stream_data/mystery_gift_stats/widgets/`
4. Choose font, size, and color
5. Position the widget anywhere on screen
6. Repeat for each stat you want to display

### 3. Recommended Layout Ideas

#### Corner Stats Layout
- Top-left: Win Rate (large font)
- Top-right: Current Streak (medium font)
- Bottom-left: Total Battles (small font)
- Bottom-right: Record (small font)

#### Progress Bar Layout
- Win Rate: Large, center screen
- Recent Performance: Small, below win rate
- Countdown Timer: Medium, right side

#### Battle Info Layout
- Current Opponent: Medium, top center
- Search Status: Small, below opponent
- Countdown: Large, prominent position

## Features

### Real-Time Updates
- Widgets update immediately after each battle completes
- Countdown timer updates every 3 seconds during wait periods
- Search status updates when human opponent search is active

### Human Opponent Indicators
- Human opponents: `👤 Username`
- Bot opponents: `🤖 BotName-1234`

### Countdown Display
- Shows time remaining until next battle
- Format: `M:SS` for >60 seconds, `XXs` for <60 seconds
- Clears to "Starting..." when countdown reaches 0

### Recent Performance
- Shows last 10 battles as W/L sequence
- Updates after each battle
- Useful for showing current form

## Customization

### Font and Styling
Each widget can be customized independently in OBS:
- Font family and size
- Color and opacity
- Background color (set to transparent for overlay effect)
- Outline and shadow effects

### Widget Combinations
You can combine multiple widgets in a single Text source by creating your own wrapper files that read multiple widget contents.

## Troubleshooting

### Widget Not Updating
- Check that the Mystery-Gift stream is running
- Verify the file path in OBS is correct
- Refresh the Text source in OBS

### File Not Found
- Ensure the stream has started at least once
- Check the `stream_data/mystery_gift_stats/widgets/` directory exists
- Run the stream with `--ladder` flag if human search features aren't working

### Performance
- Widget updates are lightweight and shouldn't impact stream performance
- Files are updated only when values change
- No performance impact from having many Text sources in OBS

## Example OBS Scene Setup

Here's a recommended setup for a clean streaming layout:

```
┌─────────────────────────────────────────────────┐
│  Win Rate: 67.5%              🤖 RandomBaseline  │
│                                Streak: 3        │
│                                                 │
│              [Battle Replay Viewer]             │
│                                                 │
│  Recent: W L W W L W W L W W     Battles: 155   │
│  1:30 until next battle         Record: 19-136   │
└─────────────────────────────────────────────────┘
```

## Integration with Existing Overlay

The widgets work alongside the existing HTML overlay (`obs_overlay.html`). You can use:
- Widgets for individual stats with custom positioning
- HTML overlay for comprehensive stats display
- Both together for maximum flexibility

## Advanced Usage

### Custom Widget Files
You can create your own widget files that combine or format stats differently by:
1. Reading the training_metrics.json file directly
2. Creating custom formatting logic
3. Writing to your own text files

### Multiple Agent Streams
If running multiple agents, each will have its own widget directory based on their configuration.