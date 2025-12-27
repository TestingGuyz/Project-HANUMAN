# 🔱 PROJECT HANUMAN - Divine Voice Assistant

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-red)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An elite, production-grade voice assistant with **Lord Hanuman's divine persona**. Single-file architecture with embedded UI, multi-model STT with fuzzy wake word detection, robust TTS with retry logic, and 5 command modes.

## ✨ Features

### 🎙️ Advanced Speech Recognition
- **Fuzzy Wake Word Detection**: Recognize "Hanuman", "Anuman", "Human", "Humanan", etc.
- **Multi-Model STT**: Groq Whisper → Local Whisper → Google Speech Recognition (intelligent fallback)
- **3.5 second recording window** with automatic processing
- **Noise handling** and confidence filtering

### 🔊 Production-Grade TTS
- **ElevenLabs Integration** with `eleven_turbo_v2` model
- **Retry logic**: 3 attempts with fallback voice switching (Hanuman → Rachel → Antoni → Elli → Arnold)
- **Exponential backoff** for resilience
- **Automatic microphone pause** during playback

### 🧠 Intelligent LLM Integration
- **Groq API** with multiple model fallbacks (Mixtral-8x7b → Llama2-70b → Gemma-7b)
- **Temperature control** for personality consistency
- **Hanuman system prompt** with 60% English, 25% Hindi, 15% Sanskrit

### 🎮 Five Command Modes

1. **AAGYA MODE** (Advisory/Chat) 🎙️
   - Ask anything - wisdom, knowledge, problem-solving
   - Example: "Aagya, what is dharma?"

2. **HASYA MODE** (Humor) 😄
   - Hear jokes, funny stories, pranks
   - Example: "Hasya, tell me a funny story"

3. **YUDHA KREEDA** (Battle Game) ⚔️
   - Rock-Paper-Scissors best of 3
   - Bilingual support: English + Hindi (पत्थर, कागज, कैंची)
   - Score tracking with visual feedback

4. **GANDHARVA MODE** (Music) 🎵
   - YouTube music search and streaming
   - Example: "Gandharva, play Jai Shri Ram"
   - Shows title, link, and thumbnail

5. **KHOJ MODE** (Web Search) 🔍
   - Web search via Tavily API
   - LLM-enhanced summaries in Hanuman's style
   - Example: "Khoj, tell me about artificial intelligence"

### 🏛️ Divine Persona
- **Authentic Hanuman Personality**: Wisdom, Strength, Devotion, Playfulness
- **Warm, Humble Tone**: "By Ram's grace", "Jai Shri Ram!", "mitra" (friend)
- **Multilingual**: English, Hindi, Sanskrit seamlessly mixed
- **Contextual Responses**: Different tone for each mode

### 🎨 Beautiful Temple-Themed UI
- **Saffron & Gold Aesthetic**: Temple-inspired design
- **Live Console Logging**: Real-time STT/TTS/LLM activity
- **Dialogue History**: All conversations saved
- **Status Indicators**: Mode, system health, now playing
- **Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Microphone (for audio input)
- Internet connection
- API keys (see below)

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/TestingGuyz/Project-HANUMAN.git
cd Project-HANUMAN
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup API Keys
```bash
# Copy template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required API Keys:**
- **Groq**: https://console.groq.com (free tier: 30 req/min)
- **ElevenLabs**: https://elevenlabs.io (free: 10k char/month)

**Optional:**
- **Tavily**: https://tavily.com (for Khoj mode)
- **HuggingFace**: https://huggingface.co/settings/tokens (advanced STT)

#### 5. Run HANUMAN
```bash
python main.py
```

Open browser: **http://localhost:5000**

## 📖 Usage Guide

### 1. Wake Up Hanuman
```
Say: "Hanuman" (or "Hanumanji", "O Hanuman", "Hey Hanuman")
✅ Works with fuzzy matching: "Anuman", "Human", "Humanan", etc.
```

### 2. Choose a Mode
```
Available modes:
- "Aagya" → Chat & Knowledge
- "Hasya" → Jokes & Humor  
- "Yudha" → Rock-Paper-Scissors Game
- "Gandharva" → Music Streaming
- "Khoj" → Web Search
```

### 3. Universal Commands
```
- "Help" → Show command guide (works anytime)
- "Exit" → Return to main menu
```

### Example Conversations

**You**: Hanuman
**Hanuman**: Jai Shri Ram! 🙏 Main Hanuman, aapki seva mein hazir hoon...

**You**: Aagya, what is Ramayana
**Hanuman**: The Ramayana is the eternal tale of Lord Ram's devotion...

**You**: Hasya, tell a funny joke
**Hanuman**: 😄 You know what? When I was young, I thought I could swallow the sun...

**You**: Yudha, rock
**Hanuman**: I chose scissors. 🎉 You win this round! Score: You 1, Me 0...

**You**: Gandharva, play Jai Shri Ram
**Hanuman**: 🎵 Now playing: Jai Shri Ram - [YouTube Link]...

**You**: Khoj, tell me about Lord Hanuman
**Hanuman**: 🔍 Khoj results... [Web search + AI summary]...

## 🛠️ Architecture

### Single File Design
```
main.py (1700+ lines)
├── Logging Setup
├── Configuration & Constants
├── Hanuman System Prompts
├── State Management (UserState)
├── Wake Word Detection (WakeWordDetector)
├── Speech Recognition (STTEngine)
├── Text-to-Speech (TTSEngine)
├── LLM Integration (LLMEngine)
├── Command Processing (CommandProcessor)
├── Flask Routes
├── HTML Frontend (embedded)
└── Main Execution
```

### Data Flow
```
🎤 Microphone Input
    ↓
💾 Save Audio (WebM)
    ↓
🔤 Transcribe (Groq → Local → Google)
    ↓
🔍 Wake Word Detection (Fuzzy Matching)
    ↓
⚡ Command Routing (5 modes)
    ↓
🧠 LLM Response Generation (Hanuman Persona)
    ↓
🔊 TTS Generation (ElevenLabs with retry)
    ↓
🎵 Audio Playback (with mic pause)
    ↓
📺 UI Update (chat, now-playing, console)
```

## 🔧 Configuration

### Environment Variables
```env
GROQ_API_KEY=xxx          # Required
ELEVENLABS_API_KEY=xxx    # Required
TAVILY_API_KEY=xxx        # Optional (for Khoj mode)
HUGGINGFACE_TOKEN=xxx     # Optional (advanced STT)
DEBUG=False               # Set to True for development
```

### Wake Word Customization
```python
# In main.py, modify these:
WAKE_WORDS_PRIMARY = ['hanuman', 'hey hanuman', ...]
WAKE_WORDS_FUZZY = ['anuman', 'human', ...]  # Typos/mistranscriptions
WAKE_WORD_THRESHOLD = 75  # Fuzzy matching threshold (0-100)
```

### Voice Selection
```python
ELEVENLABS_VOICES = {
    "Hanuman": "iHH6IS4rB3R9HSWIJNzL",    # Primary
    "Rachel": "21m00Tcm4TlvDq8ikWAM",     # Fallback 1
    # ... more voices
}
```

## 📊 Console Output

```
✅ Wake word detected (fuzzy 85%): 'anuman' → 'hanuman'
🎙️ Listening loop started
💾 Audio saved: audio_files/recording_20240101_120000_123456.webm
👂 Heard: "tell me a joke"
🔤 Groq Whisper: tell me a joke
🧠 Calling LLM: mixtral-8x7b-32768
✅ LLM reply (mixtral-8x7b): Once Hanuman swallowed the sun...
🔊 TTS attempt 1 with Hanuman...
✅ TTS generated: audio_20240101_120000.mp3
🔊 Playing TTS (Mic Paused)
✅ TTS finished (Mic Resumed)
```

## 🐛 Troubleshooting

### Issue: "Wake word not detected"
**Solution**: 
- Speak clearly and distinctly
- Try variations: "Hanuman", "Hanumanji", "Hey Hanuman"
- Check microphone levels
- Lower `WAKE_WORD_THRESHOLD` in main.py if needed

### Issue: "Groq API error"
**Solution**:
- Verify API key in .env
- Check rate limit (30 req/min on free tier)
- Use fallback models automatically triggered

### Issue: "No audio output / TTS failing"
**Solution**:
- Verify ElevenLabs API key
- Check speaker/audio device
- Confirm quota (free: 10k characters/month)
- Check console for detailed error

### Issue: "Microphone not working"
**Solution**:
- Grant microphone permission to browser
- Use HTTPS for production (required by WebRTC)
- Test microphone in browser settings

## 📱 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Full | Recommended |
| Firefox | ✅ Full | Works perfectly |
| Safari | ✅ Good | May need HTTPS |
| Edge | ✅ Full | Works great |
| Mobile Browsers | ⚠️ Limited | Use HTTPS + grant permissions |

## 🔒 Security

- ❌ **Never commit .env** - add to .gitignore
- ✅ **API keys** are server-side only (not sent to browser)
- ✅ **Audio files** are temporary and auto-deleted
- ✅ **CORS enabled** for localhost development
- ⚠️ **HTTPS recommended** for production deployment

## 📦 Dependencies Overview

| Package | Purpose | Alternative |
|---------|---------|-------------|
| flask | Web framework | Django, FastAPI |
| elevenlabs | TTS | Google TTS, Azure |
| groq | LLM + STT | OpenAI, Claude |
| whisper | Local STT | AssemblyAI, Deepgram |
| speech_recognition | Google STT fallback | pocketsphinx |
| youtube-search | Music search | yt-dlp, pytube |
| tavily-python | Web search | SerpAPI, Perplexity |
| fuzzywuzzy | Fuzzy matching | Levenshtein, regex |

## 🚀 Deployment

### Local Development
```bash
python main.py
# Runs on http://localhost:5000
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD ["python", "main.py"]
```

### Cloud Deployment
- **Heroku**: Add Procfile, deploy from git
- **AWS**: Use EC2 or Lambda
- **Google Cloud**: Cloud Run (serverless)
- **Replit**: Direct upload

## 📈 Performance

- **Wake Word Detection**: <50ms (fuzzy matching)
- **STT (Groq)**: 1-3 seconds (depends on audio length)
- **LLM Response**: 2-5 seconds (depends on model)
- **TTS Generation**: 1-3 seconds (depends on text length)
- **Total Latency**: ~5-15 seconds per interaction

## 🤝 Contributing

Contributions welcome! Areas:
- [ ] Additional voice models
- [ ] More command modes
- [ ] Hindi/Sanskrit speech output
- [ ] Mobile app wrapper
- [ ] Database for conversation history

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- **Lord Hanuman**: Divine inspiration and persona
- **Groq**: Lightning-fast LLM inference
- **ElevenLabs**: Beautiful TTS voices
- **OpenAI**: Whisper speech recognition
- **Tavily**: Web search API

## 📞 Support

For issues, questions, or suggestions:
- Open GitHub issue
- Check troubleshooting section
- Review console output for detailed logs

---

## 🎯 Roadmap

- [ ] Voice cloning with custom Hanuman voice
- [ ] Offline mode (fully local)
- [ ] Database for long-term memory
- [ ] Multi-language support (Hindi, Sanskrit)
- [ ] Mobile native app
- [ ] Telegram/WhatsApp integration
- [ ] Voice shortcuts and macros
- [ ] Real-time transcription display

---

**Jai Shri Ram! 🔱**

> *"Just as Hanuman devoted himself to Lord Ram with unwavering devotion, this assistant dedicates every byte of code to serve you with divine precision."*

🚀 **Start using HANUMAN today!**
```bash
git clone https://github.com/TestingGuyz/Project-HANUMAN.git
cd Project-HANUMAN
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python main.py
```

Then open: **http://localhost:5000**
