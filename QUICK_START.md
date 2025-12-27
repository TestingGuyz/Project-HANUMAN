# 🚀 HANUMAN - Quick Start Guide (5 Minutes)

## Step 1: Get API Keys (2 min)

### 🔥 Groq (for LLM & STT)
1. Go to: https://console.groq.com
2. Sign up (free)
3. Copy your API Key

### 🎵 ElevenLabs (for TTS/Voice)
1. Go to: https://elevenlabs.io
2. Sign up (free - 10k chars/month)
3. Copy your API Key

## Step 2: Setup Project (2 min)

### Windows/Mac/Linux
```bash
# 1. Clone
git clone https://github.com/TestingGuyz/Project-HANUMAN.git
cd Project-HANUMAN

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup .env
cp .env.example .env
# Edit .env with your API keys
```

### NixOS (You!)
```bash
# Clone
git clone https://github.com/TestingGuyz/Project-HANUMAN.git
cd Project-HANUMAN

# Enter NixOS environment
nix-shell
# All dependencies auto-loaded, .env created!
```

## Step 3: Configure (1 min)

### Edit .env
```bash
# Option 1: Nano
nano .env

# Option 2: Your favorite editor
vim .env
code .env  # VS Code
```

### Required Fields
```env
GROQ_API_KEY=paste_your_groq_key_here
ELEVENLABS_API_KEY=paste_your_elevenlabs_key_here
```

## Step 4: Run! (1 min)

```bash
python main.py
```

✅ You'll see:
```
╔═══════════════════════════════════════════════════════════════════════╗
║             🔱 PROJECT HANUMAN - DIVINE VOICE ASSISTANT 🔱             ║
║                                                                         ║
║  Starting server on http://localhost:5000                              ║
║                                                                         ║
║  Commands:                                                              ║
║  - Say "Hanuman" to wake up                                            ║
║  - Choose: Aagya, Hasya, Yudha, Gandharva, or Khoj                     ║
║  - Say "Help" for detailed guide                                       ║
║  - Say "Exit" to return to main menu                                   ║
║                                                                         ║
║  Jai Shri Ram! 🙏                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Step 5: Open Browser

👉 **http://localhost:5000**

## Try It!

### 1. Click "Start Listening"

### 2. Say Commands
```
"Hanuman"              → Wake up Hanuman
"Aagya, tell me about AI"     → Chat mode
"Hasya, tell a joke"   → Humor mode
"Yudha, rock"          → Play game
"Gandharva, play music" → Music mode
"Khoj, what is Python" → Web search
"Help"                 → Show guide
"Exit"                 → Back to menu
```

### 3. Enjoy!

🔊 You'll hear Hanuman's divine voice respond!

---

## Troubleshooting

### "API Key Error"
✅ Check .env file
✅ Verify keys match exactly
✅ No quotes around values

### "Microphone not working"
✅ Grant browser permission
✅ Test in browser settings
✅ Check speaker volume

### "No audio output"
✅ Check ElevenLabs quota
✅ Verify speaker is on
✅ Check browser volume

### "Wake word not detected"
✅ Speak clearly: "Ha-NU-man"
✅ Wait for mic circle to pulse
✅ Try variations: "Hanumanji", "Hey Hanuman"

---

## Advanced Setup

### Optional: Tavily API (for Khoj mode)
Get free key: https://tavily.com
Add to .env:
```env
TAVILY_API_KEY=your_tavily_key
```

### Optional: HuggingFace Token (for advanced STT)
Get from: https://huggingface.co/settings/tokens
Add to .env:
```env
HUGGINGFACE_TOKEN=your_hf_token
```

---

## Performance Tips

- 🎙️ **Speak clearly** for better STT
- ⏱️ **Wait 3.5 seconds** before speaking again
- 🔊 **Keep speakers at 50%+** for TTS
- 📶 **Good internet** for API calls
- 💻 **Close other tabs** for better performance

---

## Next Steps

1. ✅ Try all 5 modes
2. ✅ Check console logs
3. ✅ Customize persona in main.py
4. ✅ Add new commands
5. ✅ Deploy to cloud

---

## Getting Help

- 📖 **README.md** - Full documentation
- 🐛 **GitHub Issues** - Report bugs
- 💬 **Discussions** - Ask questions
- 🔍 **Console logs** - Debug info

---

## What You Get

✅ **5 Command Modes**
- Aagya (Chat)
- Hasya (Jokes)
- Yudha (Games)
- Gandharva (Music)
- Khoj (Search)

✅ **Production Features**
- Fuzzy wake word detection (Hanuman → Anuman)
- Multi-model STT fallback
- Robust TTS with retry logic
- Beautiful UI with live console
- Full error handling

✅ **Divine Persona**
- Authentic Hanuman personality
- 60% English, 25% Hindi, 15% Sanskrit
- Warm, humble, devoted tone
- Contextual responses per mode

---

## Architecture at a Glance

```
🎙️ Microphone
    ↓
💾 Save Audio (WebM)
    ↓
📝 Transcribe (Groq Whisper)
    ↓
🔍 Wake Word Detection (Fuzzy)
    ↓
⚡ Route to Mode (5 options)
    ↓
🧠 LLM Response (Hanuman Persona)
    ↓
🔊 TTS Generation (ElevenLabs)
    ↓
🎵 Audio Playback
    ↓
💻 Update UI
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| <kbd>Space</kbd> | Start/Stop Listening |
| <kbd>Enter</kbd> | Submit in chat |
| <kbd>Esc</kbd> | Cancel recording |
| <kbd>F12</kbd> | Open developer console |

---

## First Time Tips

1. **Allow microphone** when browser asks
2. **Use HTTPS** on mobile (required by browser)
3. **Speak naturally** - don't be robotic
4. **Check console** (F12) for debug info
5. **Be patient** - first request may take 5s

---

## Hardware Requirements

- CPU: Intel i5 or better (or Arm equivalent)
- RAM: 4GB minimum
- Network: 5+ Mbps
- Audio: Microphone + Speaker
- Browser: Chrome, Firefox, Safari, Edge

---

## Cost

**FREE Tier Limits:**
- Groq: 30 requests/min
- ElevenLabs: 10,000 chars/month (~40 min voice)
- Tavily: Basic search API

**Pricing** (if you exceed):
- Groq: $0.50/hour after free tier
- ElevenLabs: $0.03 per 1000 chars
- Tavily: Pay-as-you-go starting $0.003/search

---

## Enjoy!

```
🔱 Jai Shri Ram! 🙏
```

Your divine voice assistant awaits. Start listening!

👉 **http://localhost:5000**
