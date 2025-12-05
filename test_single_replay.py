#!/usr/bin/env python3
"""Test single replay viewing with Playwright"""

import os
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we have a debug replay
replay_file = "./debug_replay/battle-debug-test.html"
if not os.path.exists(replay_file):
    print(f"Error: {replay_file} not found")
    print("Run: python3 debug_replay.py first")
    sys.exit(1)

print(f"Testing replay viewer with: {replay_file}")
print("=" * 60)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright not installed")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Start Playwright
print("\n[1/5] Starting browser...")
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page()
page.set_viewport_size({"width": 1280, "height": 720})
print("✓ Browser ready")

# Load replay
print("\n[2/5] Loading replay...")
file_url = f"file://{os.path.abspath(replay_file)}"
page.goto(file_url, wait_until="networkidle")
time.sleep(3)
print("✓ Replay loaded")

# Try to find play button
print("\n[3/5] Looking for play button...")
button_info = page.evaluate("""
    () => {
        // Get all buttons
        const buttons = Array.from(document.querySelectorAll('button'));
        
        return {
            total_buttons: buttons.length,
            button_texts: buttons.map(b => ({
                text: b.textContent,
                title: b.title,
                name: b.name,
                class: b.className,
                html: b.innerHTML.substring(0, 50)
            }))
        };
    }
""")

print(f"Found {button_info['total_buttons']} buttons:")
for i, btn in enumerate(button_info['button_texts'][:10]):
    print(f"  {i+1}. text='{btn['text']}' title='{btn['title']}' class='{btn['class']}'")

# Check page content
print("\n[4/5] Checking page content...")
page_info = page.evaluate("""
    () => {
        return {
            hasScript: !!document.querySelector('script.battle-log-data'),
            scriptContent: (document.querySelector('script.battle-log-data')?.textContent || '').substring(0, 200),
            bodyText: document.body.innerText.substring(0, 300),
            hasReplayEmbed: !!document.querySelector('.battle, .replay, #battle'),
        };
    }
""")

print(f"Has battle-log-data script: {page_info['hasScript']}")
if page_info['hasScript']:
    print(f"Script content preview: {page_info['scriptContent'][:100]}...")
print(f"Has replay embed: {page_info['hasReplayEmbed']}")
print(f"Body text: {page_info['bodyText'][:150]}...")

# Try to auto-click
print("\n[5/5] Attempting auto-click...")
clicked = page.evaluate("""
    () => {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            console.log('Checking button:', btn.textContent, btn.className);
            // Click any button that looks like a play button
            if (btn.textContent.toLowerCase().includes('play') ||
                btn.className.includes('play') ||
                btn.innerHTML.includes('▶')) {
                console.log('Clicking:', btn);
                btn.click();
                return { clicked: true, button: btn.textContent };
            }
        }
        
        // If we can't find play, try clicking first button
        if (buttons.length > 0) {
            console.log('Clicking first button as fallback');
            buttons[0].click();
            return { clicked: true, button: 'first-button-fallback' };
        }
        
        return { clicked: false, button: null };
    }
""")

if clicked['clicked']:
    print(f"✓ Clicked: {clicked['button']}")
else:
    print("✗ Could not find/click any button")

print("\n" + "=" * 60)
print("Browser will stay open for 30 seconds...")
print("Check if the battle is playing!")
print("Press Ctrl+C to close early")
print("=" * 60)

try:
    time.sleep(30)
except KeyboardInterrupt:
    print("\nClosing...")

# Cleanup
page.close()
browser.close()
playwright.stop()

print("\nTest complete!")
