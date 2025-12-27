# 🔧 MAIN.PY FIX GUIDE

## The Problem

Your `main.py` is calling `FuzzyCommandMatcher` but the class doesn't exist in the same file. It's been created as a **separate module** called `fuzzy_matcher.py`.

---

## The Solution

### Step 1: Add Import Statement

At the top of `main.py`, add:

```python
# ============================================================================
# IMPORTS
# ============================================================================

import os
import sys
import json
import random
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
from functools import lru_cache

# Third-party imports
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import requests
from fuzzywuzzy import fuzz

try:
    from google.cloud import speech_v1, texttospeech_v1
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    from youtube_search import YoutubeSearch
    HAS_YOUTUBE = True
except ImportError:
    HAS_YOUTUBE = False

# ✅ ADD THIS LINE - Import FuzzyCommandMatcher
from fuzzy_matcher import FuzzyCommandMatcher

# ... rest of imports ...
```

---

### Step 2: Use It Correctly

When you need to detect commands, use it like this:

#### Wake Word Detection
```python
# Before sending to CommandProcessor, check for wake word
wake_word, confidence = FuzzyCommandMatcher.detect_wake_word(text)

if wake_word:
    logger.info(f"🔱 Wake word detected (fuzzy {confidence}%): {wake_word}")
    # Continue processing
else:
    logger.info(f"No wake word detected")
    return None
```

#### Mode Detection
```python
# Inside CommandProcessor.process()
mode, confidence = FuzzyCommandMatcher.detect_mode(text)

if mode:
    logger.info(f"🎯 Mode detected (fuzzy {confidence}%): {mode}")
    return handle_mode(mode, text)
else:
    return "Kshama karen, samajh nahi aaya."
```

#### Game Move Detection
```python
# Inside play_game()
user_move, confidence = FuzzyCommandMatcher.detect_move(user_input)

if not user_move:
    return "Please say Rock, Paper, or Scissors clearly."

logger.info(f"🎮 Game move detected (fuzzy {confidence}%): {user_move}")
```

#### Action Detection (Help/Exit)
```python
# Detect help or exit commands
action, confidence = FuzzyCommandMatcher.detect_action(text)

if action == 'help':
    return show_help()
elif action == 'exit':
    return handle_exit()
```

---

## Step 3: Remove Inline Fuzzy Code

**Delete this section from main.py** (if it exists):

```python
# ❌ DELETE THIS - Now in fuzzy_matcher.py
class FuzzyCommandMatcher:
    # ... all the fuzzy matching code ...
```

You don't need it anymore since it's now in `fuzzy_matcher.py`.

---

## Complete Example Flow

Here's how it should work in `CommandProcessor.process()`:

```python
@staticmethod
def process(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Process user input with FUZZY MATCHING.
    1. Check for wake word
    2. Detect mode
    3. Process command
    """
    text_lower = text.lower().strip()
    
    # Step 1: Check wake word (with fuzzy matching)
    if user_state.mode == 'idle':
        wake_word, conf = FuzzyCommandMatcher.detect_wake_word(text_lower)
        if not wake_word:
            return None, None  # No wake word, stay idle
        
        # Wake word detected, switch to active
        user_state.mode = 'active'
        logger.info(f"🔱 Hanuman awakens! (fuzzy {conf}%)")
        return "🙏 Jai Shri Ram! Main hazir hoon. Kya seva karoon? (Aagya/Hasya/Yudha/Gandharva/Khoj)", None
    
    # Step 2: Detect mode (with fuzzy matching)
    mode, conf = FuzzyCommandMatcher.detect_mode(text_lower)
    
    if mode:
        user_state.mode = mode
        logger.info(f"🎯 Mode detected (fuzzy {conf}%): {mode}")
        
        if mode == 'aagya':
            reply = CommandProcessor.chat(text)
            user_state.add_message('user', text)
            user_state.add_message('ai', reply)
            return reply, None
        
        elif mode == 'hasya':
            reply = CommandProcessor.tell_joke()
            return reply, None
        
        elif mode == 'yudha':
            reply = CommandProcessor.play_game(text)
            return reply, None
        
        elif mode == 'gandharva':
            reply = CommandProcessor.play_music(text)
            return reply, None
        
        elif mode == 'khoj':
            reply = CommandProcessor.web_search(text)
            return reply, None
    
    # Step 3: Check for actions (help/exit)
    action, conf = FuzzyCommandMatcher.detect_action(text_lower)
    
    if action == 'help':
        return show_help(), None
    elif action == 'exit':
        user_state.mode = 'idle'
        return "🙏 Jai Shri Ram! Aapki seva karte hue khus rahoonga. Namaste!", None
    
    # No command recognized
    return "Kshama karen, samajh nahi aaya.", None
```

---

## Step 4: Update Game Logic

In `play_game()`, use fuzzy matcher for moves:

```python
@staticmethod
def play_game(user_input: str) -> str:
    """Rock-Paper-Scissors with FUZZY MOVE DETECTION"""
    moves = ['rock', 'paper', 'scissors']
    ai_move = random.choice(moves)
    
    # ✅ Use fuzzy matcher to detect user move
    user_move, confidence = FuzzyCommandMatcher.detect_move(user_input)
    
    if not user_move:
        return "Mitra, please say Rock (पत्थर), Paper (कागज), or Scissors (कैंची) clearly. 🤔"
    
    logger.info(f"🎮 Game move detected (fuzzy {confidence}%): {user_move}")
    
    # ... rest of game logic ...
```

---

## Step 5: Verify Dependencies

Make sure your `requirements.txt` includes:

```txt
fuzzywuzzy==0.18.0
python-Levenshtein==0.21.1
flask==2.3.0
flask-cors==4.0.0
requests==2.31.0
google-cloud-speech==2.20.0
google-cloud-texttospeech==2.13.0
youtube-search==2.1.0
```

Then install:

```bash
pip install -r requirements.txt
```

---

## Testing

Test that fuzzy matching works:

```bash
# Test in Python
python3 -c "
from fuzzy_matcher import FuzzyCommandMatcher

# Test wake word
result, conf = FuzzyCommandMatcher.detect_wake_word('humanan')
print(f'Wake word: {result} ({conf}%)')

# Test mode
result, conf = FuzzyCommandMatcher.detect_mode('agya')
print(f'Mode: {result} ({conf}%)')

# Test move
result, conf = FuzzyCommandMatcher.detect_move('rok')
print(f'Move: {result} ({conf}%)')
"
```

Expected output:
```
Wake word: hanuman (87%)
Mode: aagya (80%)
Move: rock (92%)
```

---

## Summary of Changes

| What | Where | Action |
|------|-------|--------|
| **Import** | Top of main.py | Add `from fuzzy_matcher import FuzzyCommandMatcher` |
| **Wake word** | process() | Use `FuzzyCommandMatcher.detect_wake_word()` |
| **Mode** | process() | Use `FuzzyCommandMatcher.detect_mode()` |
| **Game move** | play_game() | Use `FuzzyCommandMatcher.detect_move()` |
| **Actions** | process() | Use `FuzzyCommandMatcher.detect_action()` |
| **Delete** | main.py | Remove inline FuzzyCommandMatcher class |

---

## Common Issues & Fixes

### Issue: `ModuleNotFoundError: No module named 'fuzzy_matcher'`

**Fix:** Make sure `fuzzy_matcher.py` is in the same directory as `main.py`

```bash
ls -la
# Should show:
# main.py
# fuzzy_matcher.py
# requirements.txt
```

### Issue: `ImportError: cannot import name 'FuzzyCommandMatcher'`

**Fix:** Check the import statement:

```python
# ✅ Correct
from fuzzy_matcher import FuzzyCommandMatcher

# ❌ Wrong
from fuzzy_matcher import *
```

### Issue: Fuzzy matching not working

**Fix:** Make sure `fuzzywuzzy` is installed:

```bash
pip install fuzzywuzzy python-Levenshtein
```

---

## Congratulations! 🎉

Your HANUMAN assistant now has:

✅ **Proper separation of concerns** - fuzzy matching in its own module
✅ **Clean imports** - easy to maintain and test
✅ **Full fuzzy matching support** - for all commands
✅ **Confidence logging** - see exactly what was matched
✅ **Production-ready code** - proper error handling

**Jai Shri Ram!** 🙏
