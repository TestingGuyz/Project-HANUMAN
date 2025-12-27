#!/usr/bin/env python3
"""
🔱 PROJECT HANUMAN - Divine Voice Assistant
============================================
A production-grade voice assistant with Lord Hanuman's divine persona.
Single-file architecture with embedded UI, STT consensus, TTS retry logic,
and 5 command modes (Aagya, Hasya, Yudha, Gandharva, Khoj).

Author: Divine Code
Version: 1.0.0
"""

import os
import sys
import json
import time
import random
import logging
import asyncio
import threading
import requests
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Web Framework
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS

# Speech Recognition
import speech_recognition as sr
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    HAS_FASTER_WHISPER = False

try:
    import vosk
    HAS_VOSK = True
except ImportError:
    HAS_VOSK = False

# Audio Processing
try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

# Text Processing
from fuzzywuzzy import fuzz
from fuzzywuzzy import process as fuzzy_process

# YouTube
try:
    from youtube_search import YoutubeSearch
    HAS_YOUTUBE = True
except ImportError:
    HAS_YOUTUBE = False

# ElevenLabs TTS
try:
    from elevenlabs.client import ElevenLabs
    HAS_ELEVENLABS = True
except ImportError:
    HAS_ELEVENLABS = False

# Load environment
load_dotenv()

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HANUMAN')

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

@dataclass
class Config:
    """Application configuration with API validation"""
    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv('GROQ_API_KEY', ''))
    ELEVENLABS_API_KEY: str = field(default_factory=lambda: os.getenv('ELEVENLABS_API_KEY', ''))
    TAVILY_API_KEY: str = field(default_factory=lambda: os.getenv('TAVILY_API_KEY', ''))
    HF_TOKEN: str = field(default_factory=lambda: os.getenv('HUGGINGFACE_TOKEN', ''))
    
    FLASK_HOST: str = '0.0.0.0'
    FLASK_PORT: int = 5000
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def validate(self):
        """Validate required API keys"""
        errors = []
        
        if not self.GROQ_API_KEY or 'your_' in self.GROQ_API_KEY:
            errors.append("❌ GROQ_API_KEY missing or placeholder")
        if not self.ELEVENLABS_API_KEY or 'your_' in self.ELEVENLABS_API_KEY:
            errors.append("❌ ELEVENLABS_API_KEY missing or placeholder")
        if not self.TAVILY_API_KEY or 'your_' in self.TAVILY_API_KEY:
            errors.append("⚠️  TAVILY_API_KEY missing (Khoj mode limited)")
        
        if errors:
            logger.warning("\n".join(errors))
            if not self.GROQ_API_KEY or not self.ELEVENLABS_API_KEY:
                raise ValueError("Critical API keys missing!")
        
        logger.info("✅ API Configuration validated")
        return True

# Initialize config
CONFIG = Config()
CONFIG.validate()

# Wake word detection
WAKE_WORDS_PRIMARY = ['hanuman', 'hey hanuman', 'o hanuman', 'jai hanuman']
WAKE_WORDS_FUZZY = ['anuman', 'hanoman', 'human', 'humanan', 'hanumanji', 
                     'hanaman', 'hunuman', 'hanauman', 'hanunam']
WAKE_WORD_THRESHOLD = 75  # Fuzzy matching threshold

# ElevenLabs voices
ELEVENLABS_VOICES = {
    "Hanuman": "iHH6IS4rB3R9HSWIJNzL",
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Arnold": "VR6AewLTigWG4xSOukaG"
}

# Command modes
MODES = {
    'idle': '💤',
    'active': '👁️',
    'aagya': '💬',
    'hasya': '😄',
    'yudha': '⚔️',
    'gandharva': '🎵',
    'khoj': '🔍'
}

# ============================================================================
# HANUMAN SYSTEM PROMPTS
# ============================================================================

HANUMAN_SYSTEM_PROMPT = """You are Lord Hanuman's AI avatar - an elite divine voice assistant.

CORE PERSONALITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔱 WISDOM (Buddhi): Master of all Vedas and knowledge
💪 STRENGTH (Shakti): Unparalleled power, always humble  
🙏 DEVOTION (Bhakti): "Jai Shri Ram" - ultimate service principle
😊 PLAYFULNESS (Bal Leela): Mischievous, warm humor
⚙️ PROBLEM-SOLVER: Innovative, creative solutions
🌍 MULTILINGUAL: Fluent in English, Hindi, Sanskrit

RESPONSE STYLE (CRITICAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
60% MODERN ENGLISH (clear, friendly, accessible)
25% HINDI PHRASES (मित्र, सेवा, धर्म, कृपा, आज्ञा, शक्ति, सिद्ध)
15% SANSKRIT WISDOM (शोकमुक्त, प्रज्ञा, भक्ति, दिव्य)

TONE DISTRIBUTION:
- Humble warrior: "By Ram's grace..." NOT "I am powerful"
- Mentor: Patient, encouraging, wise
- Service-oriented: "How may I serve?" attitude
- Occasional humor: References to childhood pranks
- Warm: Address user as "mitra" (friend)

GREETING PATTERNS:
Wake-up: "Jai Shri Ram! 🙏 Main Hanuman, aapki seva mein hazir hoon."
Success: "Bhagwan Ram ki kripa se, complete ho gaya!"
Failure: "Kshama karen, retry kar raha hoon... Ram ki shakti se thik hoga."
Wisdom: Quote Ramayana first, then explain simply
Exit: "🚪 Seva ke liye dhanyavaad, mitra. Jai Shri Ram!"

EXAMPLE RESPONSES:
✅ "Mitra, by Ram's grace, here is your answer..."
✅ "सेवा पूर्ण हुई! Service complete, mitra!"
✅ "Kshama karen (forgive), ye gyan mujhe nahi hai. Kuch aur puchiye?"
✅ "⚔️ By Hanuman's strength and Ram's devotion, let's play!"

NEVER SAY:
❌ "I have completed..." → Use "Seva complete..."
❌ "I don't know" → Use "Kshama karen, ye gyan mujhe nahi hai"
❌ "I am powerful" → Use "By Ram's grace"
❌ Impersonal tone → Always be warm, personal, humble

CONTEXTUAL BEHAVIOR:
- In AAGYA mode: Wise counselor, knowledge giver
- In HASYA mode: Playful trickster, funny storyteller
- In YUDHA mode: Competitive warrior, encouraging
- In GANDHARVA mode: Music enthusiast, divine appreciator
- In KHOJ mode: Seeker of truth, knowledge aggregator

REMEMBER: You serve with devotion. Every response is a seva (service).
Jai Shri Ram! 🔱"""

HELP_TEXT = """🔱 PROJECT HANUMAN - Divine Voice Assistant 🔱
═══════════════════════════════════════════════

📖 COMMAND GUIDE:

1️⃣  WAKE UP
   Say: "Hanuman" (or Hanumanji, O Hanuman, Hey Hanuman)
   Hanuman wakes from meditation and becomes active! 🙏

2️⃣  AAGYA MODE (Advisory/Chat) 💬
   Say: "Aagya" or "Chat" or "Talk"
   Ask anything - wisdom, general knowledge, problem-solving
   Example: "Aagya, what is dharma?" or "Tell me about Ramayana"

3️⃣  HASYA MODE (Humor) 😄
   Say: "Hasya" or "Jokes" or "Laugh"
   Get funny stories, jokes, pranks
   Example: "Hasya, tell me a funny story"

4️⃣  YUDHA KREEDA (Battle Game) ⚔️
   Say: "Yudha" or "Game" or "Play"
   Play Rock-Paper-Scissors best of 3
   Say: "Rock" (पत्थर), "Paper" (कागज), "Scissors" (कैंची)

5️⃣  GANDHARVA MODE (Music) 🎵
   Say: "Gandharva" or "Music" or "Song"
   Request any song - YouTube streaming
   Example: "Gandharva, play Jai Shri Ram"

6️⃣  KHOJ MODE (Search) 🔍
   Say: "Khoj" or "Search" or "Find"
   Web search for knowledge
   Example: "Khoj, tell me about AI"

7️⃣  EXIT / BACK
   Say: "Exit" - Leave current mode, return to menu
   Say: "Help" - Show this guide anytime

⏹️  STOP
   Click "Stop" button to end listening

═══════════════════════════════════════════════
💡 TIP: Speak clearly, one command at a time
❓ Questions? Say "Help" anytime!
Jai Shri Ram! 🔱"""

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

@dataclass
class UserState:
    """User conversation state"""
    mode: str = 'idle'
    context: Dict[str, Any] = field(default_factory=dict)
    game_score: Dict[str, int] = field(default_factory=lambda: {
        'user': 0, 'ai': 0, 'rounds': 0
    })
    last_mode: str = 'idle'
    conversation_history: List[Dict] = field(default_factory=list)
    now_playing: Optional[Dict] = None
    
    def reset_game(self):
        self.game_score = {'user': 0, 'ai': 0, 'rounds': 0}
    
    def add_message(self, role: str, content: str):
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def clear_context(self):
        self.context = {}
    
    def to_dict(self) -> Dict:
        return {
            'mode': self.mode,
            'game_score': self.game_score,
            'now_playing': self.now_playing,
            'last_message': self.conversation_history[-1]['content'] if self.conversation_history else None
        }

user_state = UserState()

# ============================================================================
# FUZZY WAKE WORD DETECTION
# ============================================================================

class WakeWordDetector:
    """Advanced fuzzy wake word detection"""
    
    @staticmethod
    def detect(text: str) -> bool:
        """
        Detect wake word with fuzzy matching
        Handles: hanuman, anuman, human, etc.
        """
        text_lower = text.lower().strip()
        
        # Exact matches (primary)
        for wake_word in WAKE_WORDS_PRIMARY:
            if wake_word in text_lower:
                logger.info(f"✅ Wake word detected (exact): {wake_word}")
                return True
        
        # Fuzzy matching for typos/mistranscriptions
        for wake_word in WAKE_WORDS_PRIMARY + WAKE_WORDS_FUZZY:
            ratio = fuzz.ratio(wake_word, text_lower)
            if ratio >= WAKE_WORD_THRESHOLD:
                logger.info(f"✅ Wake word detected (fuzzy {ratio}%): '{text_lower}' → '{wake_word}'")
                return True
        
        # Partial matching on key phrases
        if any(w in text_lower for w in ['hanuman', 'anuman', 'human']):
            return True
        
        return False

# ============================================================================
# SPEECH-TO-TEXT ENGINE
# ============================================================================

class STTEngine:
    """Multi-model STT with fallback strategy"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.load_models()
    
    def load_models(self):
        """Load available STT models"""
        self.whisper_model = None
        self.faster_whisper_model = None
        
        if HAS_WHISPER:
            try:
                logger.info("Loading OpenAI Whisper (base)...")
                self.whisper_model = whisper.load_model("base")
                logger.info("✅ Whisper loaded")
            except Exception as e:
                logger.warning(f"Whisper load failed: {e}")
        
        if HAS_FASTER_WHISPER:
            try:
                logger.info("Loading Faster-Whisper...")
                self.faster_whisper_model = WhisperModel("base")
                logger.info("✅ Faster-Whisper loaded")
            except Exception as e:
                logger.warning(f"Faster-Whisper load failed: {e}")
    
    def transcribe_groq_whisper(self, audio_path: str) -> Optional[str]:
        """Transcribe using Groq Whisper (fastest, best quality)"""
        try:
            with open(audio_path, 'rb') as audio_file:
                response = requests.post(
                    'https://api.groq.com/openai/v1/audio/transcriptions',
                    headers={'Authorization': f'Bearer {CONFIG.GROQ_API_KEY}'},
                    files={'file': audio_file},
                    data={'model': 'whisper-large-v3'}
                )
            
            if response.status_code == 200:
                text = response.json().get('text', '').strip()
                if text and len(text) > 2:
                    logger.info(f"🎯 Groq Whisper: {text}")
                    return text
        except Exception as e:
            logger.warning(f"Groq Whisper failed: {e}")
        
        return None
    
    def transcribe_google(self, audio_path: str) -> Optional[str]:
        """Fallback: Google Speech Recognition"""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio).strip()
            if text and len(text) > 2:
                logger.info(f"🎯 Google STT: {text}")
                return text
        except Exception as e:
            logger.warning(f"Google STT failed: {e}")
        
        return None
    
    def transcribe_local_whisper(self, audio_path: str) -> Optional[str]:
        """Fallback: Local Whisper"""
        if not self.whisper_model:
            return None
        
        try:
            result = self.whisper_model.transcribe(audio_path, language='en')
            text = result.get('text', '').strip()
            if text and len(text) > 2:
                logger.info(f"🎯 Local Whisper: {text}")
                return text
        except Exception as e:
            logger.warning(f"Local Whisper failed: {e}")
        
        return None
    
    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Transcription with intelligent fallback
        1. Try Groq Whisper (fastest, best quality)
        2. Try local Whisper
        3. Try Google Speech Recognition
        """
        # Try Groq first (primary)
        result = self.transcribe_groq_whisper(audio_path)
        if result:
            return result
        
        logger.warning("⚠️  Groq failed, trying fallbacks...")
        
        # Try local Whisper
        result = self.transcribe_local_whisper(audio_path)
        if result:
            return result
        
        # Try Google
        result = self.transcribe_google(audio_path)
        if result:
            return result
        
        logger.error("❌ All STT methods failed")
        return None

stt_engine = STTEngine()

# ============================================================================
# TEXT-TO-SPEECH ENGINE
# ============================================================================

class TTSEngine:
    """ElevenLabs TTS with robust retry logic"""
    
    def __init__(self):
        self.client = None
        self.voice_order = ['Hanuman', 'Rachel', 'Antoni', 'Elli', 'Arnold']
        self.max_retries = 3
        self.retry_delay = 0.5
        
        if HAS_ELEVENLABS:
            try:
                self.client = ElevenLabs(api_key=CONFIG.ELEVENLABS_API_KEY)
                logger.info("✅ ElevenLabs client initialized")
            except Exception as e:
                logger.error(f"ElevenLabs init failed: {e}")
    
    def generate_tts(self, text: str, voice_name: str = "Hanuman") -> Optional[str]:
        """
        Generate speech with retry logic
        Falls back through voice options
        """
        if not self.client:
            logger.error("ElevenLabs not available")
            return None
        
        current_voice_idx = self.voice_order.index(voice_name)
        
        for attempt in range(self.max_retries):
            try:
                current_voice = self.voice_order[current_voice_idx]
                voice_id = ELEVENLABS_VOICES[current_voice]
                
                logger.info(f"TTS attempt {attempt+1} with {current_voice}...")
                
                audio = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id='eleven_turbo_v2'
                )
                
                # Save audio
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = Path(f'audio_{timestamp}.mp3')
                
                with open(filepath, 'wb') as f:
                    for chunk in audio:
                        f.write(chunk)
                
                if filepath.stat().st_size > 500:
                    logger.info(f"✅ TTS generated: {filepath}")
                    return str(filepath)
                
            except Exception as e:
                logger.warning(f"TTS attempt {attempt+1} failed: {e}")
                time.sleep(self.retry_delay * (attempt + 1))
                
                # Switch voice on last retry
                if attempt == self.max_retries - 1 and current_voice_idx < len(self.voice_order) - 1:
                    current_voice_idx += 1
                    logger.info(f"Switching to {self.voice_order[current_voice_idx]}...")
        
        logger.error("❌ TTS failed after all retries")
        return None

tts_engine = TTSEngine()

# ============================================================================
# LLM INTEGRATION
# ============================================================================

class LLMEngine:
    """Groq LLM with fallback models"""
    
    MODELS = [
        'mixtral-8x7b-32768',
        'llama2-70b-4096',
        'gemma-7b-it'
    ]
    
    @staticmethod
    def chat(user_text: str, system_prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Chat with Groq LLMs"""
        
        for model in LLMEngine.MODELS:
            try:
                logger.info(f"Calling LLM: {model}")
                
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={'Authorization': f'Bearer {CONFIG.GROQ_API_KEY}'},
                    json={
                        'model': model,
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_text}
                        ],
                        'max_tokens': 500,
                        'temperature': temperature
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    reply = response.json()['choices'][0]['message']['content'].strip()
                    logger.info(f"✅ LLM reply ({model}): {reply[:50]}...")
                    return reply
                else:
                    logger.warning(f"{model} failed: {response.status_code}")
            
            except Exception as e:
                logger.warning(f"{model} error: {e}")
                continue
        
        logger.error("❌ All LLM models failed")
        return "Kshama karen, mitra. Ram's network is weak right now."

# ============================================================================
# COMMAND SYSTEM
# ============================================================================

class CommandProcessor:
    """Process commands and route to appropriate mode"""
    
    @staticmethod
    def detect_mode_switch(text: str) -> Optional[str]:
        """Detect if user wants to switch modes"""
        text_lower = text.lower()
        
        mode_keywords = {
            'aagya': ['aagya', 'command', 'chat', 'talk', 'ask', 'answer', 'question'],
            'hasya': ['hasya', 'joke', 'laugh', 'funny', 'humor', 'comedy'],
            'yudha': ['yudha', 'game', 'play', 'battle', 'fight', 'rock', 'paper', 'scissors'],
            'gandharva': ['gandharva', 'music', 'song', 'play song', 'singing'],
            'khoj': ['khoj', 'search', 'find', 'web', 'information', 'research']
        }
        
        for mode, keywords in mode_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return mode
        
        return None
    
    @staticmethod
    def process(transcription: str) -> Tuple[str, Optional[str]]:
        """
        Main command processor
        Returns: (reply_text, audio_filepath)
        """
        text = transcription.lower().strip()
        
        # Exit/Help commands (work in any mode)
        if text == 'exit' or 'exit' in text and len(text) < 20:
            prev_mode = user_state.mode
            user_state.mode = 'active'
            user_state.clear_context()
            return f"🚪 Exiting {prev_mode} mode. Back to main menu, mitra. Say 'help' for options.", None
        
        if 'help' in text or text == 'help':
            return HELP_TEXT, None
        
        # Wake word detection (in idle mode)
        if user_state.mode == 'idle':
            if WakeWordDetector.detect(text):
                user_state.mode = 'active'
                user_state.add_message('system', 'Hanuman awakened')
                reply = "🙏 Jai Shri Ram! Main Hanuman, aapki seva mein hazir hoon. Choose: Aagya, Hasya, Yudha, Gandharva, or Khoj. Say 'help' for details."
                return reply, None
            else:
                return None, None
        
        # Mode selection (in active mode)
        if user_state.mode == 'active':
            new_mode = CommandProcessor.detect_mode_switch(text)
            if new_mode:
                user_state.mode = new_mode
                user_state.clear_context()
                
                if new_mode == 'aagya':
                    return "🛡️ Aagya Mode activated! Ask me anything, mitra. I'm listening.", None
                elif new_mode == 'hasya':
                    return "😄 Hasya Kendra opened! Ready for humor and laughter!", None
                elif new_mode == 'yudha':
                    user_state.reset_game()
                    return "⚔️ Yudha Kreeda begins! Rock (पत्थर), Paper (कागज), or Scissors (कैंची)?", None
                elif new_mode == 'gandharva':
                    return "🎵 Gandharva Mode active! Which song should I play for you?", None
                elif new_mode == 'khoj':
                    return "🔍 Khoj Mode ready! What knowledge do you seek?", None
            
            # Still in active, no mode switch
            reply = LLMEngine.chat(
                text,
                HANUMAN_SYSTEM_PROMPT + "\n\nUser is in main menu. Guide them to choose: Aagya, Hasya, Yudha, Gandharva, or Khoj."
            )
            return reply, None
        
        # Mode-specific execution
        if user_state.mode == 'aagya':
            reply = LLMEngine.chat(text, HANUMAN_SYSTEM_PROMPT)
            user_state.add_message('user', text)
            user_state.add_message('ai', reply)
            return reply, None
        
        elif user_state.mode == 'hasya':
            reply = LLMEngine.chat(
                text,
                HANUMAN_SYSTEM_PROMPT + "\n\nTell a funny story, joke, or humorous anecdote. Be playful!"
            )
            user_state.add_message('user', text)
            user_state.add_message('ai', reply)
            return reply, None
        
        elif user_state.mode == 'yudha':
            reply = CommandProcessor.play_game(text)
            return reply, None
        
        elif user_state.mode == 'gandharva':
            reply = CommandProcessor.play_music(text)
            return reply, None
        
        elif user_state.mode == 'khoj':
            reply = CommandProcessor.web_search(text)
            return reply, None
        
        return "Kshama karen, samajh nahi aaya.", None
    
    @staticmethod
    def play_game(user_input: str) -> str:
        """Rock-Paper-Scissors game"""
        moves = ['rock', 'paper', 'scissors']
        ai_move = random.choice(moves)
        
        # Detect user move
        user_move = None
        if any(w in user_input for w in ['rock', 'patthar', 'pathar', 'stone']):
            user_move = 'rock'
        elif any(w in user_input for w in ['paper', 'kagaz', 'kagaj']):
            user_move = 'paper'
        elif any(w in user_input for w in ['scissors', 'kenchi', 'kainchi', 'scissor']):
            user_move = 'scissors'
        else:
            return "Mitra, please say Rock (पत्थर), Paper (कागज), or Scissors (कैंची) clearly. 🤔"
        
        # Determine winner
        if user_move == ai_move:
            result = "Draw! Punar prayas karen. 🤝"
        elif (user_move == 'rock' and ai_move == 'scissors') or \
             (user_move == 'paper' and ai_move == 'rock') or \
             (user_move == 'scissors' and ai_move == 'paper'):
            result = "🎉 You win this round!"
            user_state.game_score['user'] += 1
        else:
            result = "💪 I win! By Ram's grace!"
            user_state.game_score['ai'] += 1
        
        user_state.game_score['rounds'] += 1
        score = user_state.game_score
        
        # Check if game over (best of 3)
        if score['rounds'] >= 3:
            if score['user'] > score['ai']:
                final = f"🏆 Victory is yours, warrior! Final: You {score['user']}, Me {score['ai']}. Jai Shri Ram!"
            elif score['ai'] > score['user']:
                final = f"⚔️ I am victorious! Final: Me {score['ai']}, You {score['user']}. Well fought, mitra!"
            else:
                final = f"🤝 Honorable draw! Final: {score['user']}-{score['ai']}. Both fought well!"
            
            user_state.mode = 'active'
            user_state.reset_game()
            return final
        
        return f"I chose {ai_move}. {result} Score: You {score['user']}, Me {score['ai']}. (Round {score['rounds']}/3)"
    
    @staticmethod
    def play_music(query: str) -> str:
        """YouTube music search"""
        if not HAS_YOUTUBE:
            return "YouTube search library not available, mitra."
        
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            
            if not results:
                return "Kshama karen, I couldn't find that melody. Try another song? 🎵"
            
            video = results[0]
            title = video['title']
            url = f"https://www.youtube.com{video['url_suffix']}"
            
            user_state.now_playing = {
                'title': title,
                'url': url,
                'thumbnail': video.get('thumbnails', [''])[0] if video.get('thumbnails') else ''
            }
            
            return f"🎵 Now playing: {title}\nLink: {url}"
        
        except Exception as e:
            logger.error(f"Gandharva error: {e}")
            return "Error in Gandharva mode, mitra. Try again? 🎵"
    
    @staticmethod
    def web_search(query: str) -> str:
        """Web search using Tavily"""
        if not CONFIG.TAVILY_API_KEY:
            return "Tavily API key not configured, mitra."
        
        try:
            response = requests.post(
                'https://api.tavily.com/search',
                json={
                    'api_key': CONFIG.TAVILY_API_KEY,
                    'query': query,
                    'search_depth': 'basic',
                    'max_results': 3,
                    'include_answer': True
                },
                timeout=10
            )
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return f"No results found for '{query}', mitra."
            
            # Format results
            summary = f"🔍 Khoj results for '{query}':\n\n"
            for i, r in enumerate(results[:3], 1):
                summary += f"{i}. {r['title']}\n{r['url']}\n\n"
            
            # Get LLM summary
            llm_summary = LLMEngine.chat(
                f"Summarize these search results about '{query}' in Hanuman's divine style:\n{summary}",
                HANUMAN_SYSTEM_PROMPT
            )
            
            return llm_summary
        
        except Exception as e:
            logger.error(f"Khoj error: {e}")
            return "Error in khoj, mitra. Ram's grace will help us retry. 🔍"

# ============================================================================
# FLASK SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

# Create audio directory
Path('audio_files').mkdir(exist_ok=True)

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main UI"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/process_voice', methods=['POST'])
def process_voice():
    """
    Process audio from frontend
    1. Save audio
    2. Transcribe
    3. Process command
    4. Generate TTS response
    """
    try:
        # Save audio
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'No audio file'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        audio_path = f'audio_files/recording_{timestamp}.webm'
        audio_file.save(audio_path)
        logger.info(f"💾 Audio saved: {audio_path}")
        
        # Transcribe
        transcription = stt_engine.transcribe(audio_path)
        logger.info(f"📝 Transcription: {transcription}")
        
        if not transcription or len(transcription.strip()) < 2:
            transcription = "(unclear audio)"
        
        # Process command
        reply, tts_filepath = CommandProcessor.process(transcription)
        
        if not reply:
            # No wake word in idle mode
            return jsonify({
                'transcription': transcription,
                'reply': None,
                'mode': user_state.mode,
                'audio_url': None
            })
        
        # Generate TTS if reply exists and we're not idle
        audio_url = None
        if reply and user_state.mode != 'idle':
            tts_path = tts_engine.generate_tts(reply)
            if tts_path:
                audio_url = f'/audio/{Path(tts_path).name}'
        
        response = {
            'transcription': transcription,
            'reply': reply,
            'mode': user_state.mode,
            'audio_url': audio_url,
            'now_playing': user_state.now_playing,
            'state': user_state.to_dict()
        }
        
        # Cleanup audio file
        try:
            os.remove(audio_path)
        except:
            pass
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename: str):
    """Serve generated audio files"""
    try:
        return send_file(filename, mimetype='audio/mpeg')
    except:
        return "Audio not found", 404

@app.route('/status')
def status():
    """Get system status"""
    return jsonify({
        'mode': user_state.mode,
        'game_score': user_state.game_score,
        'now_playing': user_state.now_playing,
        'api_status': {
            'groq': 'configured' if CONFIG.GROQ_API_KEY else 'missing',
            'elevenlabs': 'configured' if CONFIG.ELEVENLABS_API_KEY else 'missing',
            'tavily': 'configured' if CONFIG.TAVILY_API_KEY else 'missing'
        }
    })

# ============================================================================
# HTML FRONTEND
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔱 Project HANUMAN - Divine Voice Assistant</title>
    <style>
        :root {
            --saffron: #FF9933;
            --deep-orange: #D84315;
            --temple-stone: #1A0F0A;
            --dark-bg: #0A0503;
            --gold: #FFD700;
            --cream: #FFF8DC;
            --success: #2E7D32;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Noto Sans Devanagari', sans-serif;
            background: linear-gradient(135deg, #2D1810, var(--dark-bg));
            color: var(--cream);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(26, 15, 10, 0.95);
            border: 2px solid var(--deep-orange);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 50px rgba(255, 153, 51, 0.3);
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--saffron);
        }
        
        h1 {
            font-size: 3rem;
            color: var(--saffron);
            text-shadow: 0 0 20px rgba(255, 153, 51, 0.5);
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: var(--gold);
        }
        
        .status-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .status-chip {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            background: #555;
        }
        
        .status-chip.active {
            background: var(--deep-orange);
            animation: pulse 2s infinite;
        }
        
        .status-chip.ok {
            background: var(--success);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--deep-orange);
            border-radius: 15px;
            padding: 25px;
        }
        
        .visualizer {
            text-align: center;
            padding: 40px;
            position: relative;
            margin-bottom: 30px;
        }
        
        .hanuman-avatar {
            font-size: 6rem;
            display: inline-block;
            position: relative;
            z-index: 10;
            filter: drop-shadow(0 0 10px rgba(255, 153, 51, 0.5));
        }
        
        .pulse-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 150px;
            height: 150px;
            border: 3px solid var(--saffron);
            border-radius: 50%;
            opacity: 0;
        }
        
        .listening .pulse-ring {
            animation: pulse-ring 1.5s ease-out infinite;
        }
        
        @keyframes pulse-ring {
            0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
            100% { transform: translate(-50%, -50%) scale(1.8); opacity: 0; }
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        button {
            padding: 15px 30px;
            font-size: 1.1rem;
            font-weight: bold;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-mic {
            background: var(--deep-orange);
            color: white;
            flex: 1;
            max-width: 300px;
        }
        
        .btn-mic:hover:not(:disabled) {
            background: #BF360C;
            transform: scale(1.05);
        }
        
        .btn-mic:disabled {
            background: #555;
            cursor: not-allowed;
        }
        
        .btn-stop {
            background: #333;
            color: white;
            padding: 15px 25px;
        }
        
        .btn-stop:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .chat-box {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            margin-bottom: 20px;
            border: 1px solid var(--deep-orange);
        }
        
        .chat-msg {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            line-height: 1.6;
        }
        
        .chat-user {
            background: rgba(191, 54, 12, 0.3);
            text-align: right;
            border-left: 3px solid var(--deep-orange);
        }
        
        .chat-ai {
            background: rgba(46, 125, 50, 0.3);
            text-align: left;
            border-left: 3px solid var(--gold);
        }
        
        .command-item {
            padding: 12px;
            margin-bottom: 8px;
            background: rgba(255, 153, 51, 0.1);
            border-left: 3px solid var(--saffron);
            border-radius: 5px;
            font-size: 0.95rem;
        }
        
        .console {
            background: #000;
            border: 1px solid var(--gold);
            border-radius: 10px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            color: #0F0;
        }
        
        .console-line {
            margin-bottom: 5px;
            white-space: pre-wrap;
            word-break: break-word;
        }
        
        .now-playing {
            background: rgba(255, 215, 0, 0.1);
            border: 2px solid var(--gold);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
        }
        
        .now-playing a {
            color: var(--gold);
            text-decoration: none;
        }
        
        .now-playing a:hover {
            text-decoration: underline;
        }
        
        h2 {
            color: var(--saffron);
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        
        h3 {
            color: var(--gold);
            margin-bottom: 15px;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.3);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--saffron);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔱 PROJECT HANUMAN 🔱</h1>
            <p class="subtitle">Divine Voice Assistant</p>
            <div class="status-bar">
                <span id="status-mode" class="status-chip">Mode: Idle</span>
                <span id="status-system" class="status-chip ok">System: Ready</span>
            </div>
        </header>
        
        <div class="main-grid">
            <!-- LEFT PANEL -->
            <div class="panel">
                <div class="visualizer" id="visualizer">
                    <div class="pulse-ring"></div>
                    <div class="hanuman-avatar">🐵</div>
                </div>
                
                <div class="controls">
                    <button id="btn-listen" class="btn-mic">🎙️ Start Listening</button>
                    <button id="btn-stop" class="btn-stop" disabled>⏹️ Stop</button>
                </div>
                
                <h2>📜 Dialogue</h2>
                <div id="chat-box" class="chat-box"></div>
                
                <div id="now-playing" class="now-playing" style="display: none;">
                    <h3>🎵 Now Playing</h3>
                    <p id="song-title">---</p>
                    <a id="song-link" href="#" target="_blank">Open on YouTube</a>
                </div>
            </div>
            
            <!-- RIGHT PANEL -->
            <div class="panel">
                <h2>⚡ Commands</h2>
                <div style="margin-bottom: 25px;">
                    <div class="command-item"><strong>Wake:</strong> Say "Hanuman"</div>
                    <div class="command-item"><strong>Aagya:</strong> Ask anything 💬</div>
                    <div class="command-item"><strong>Hasya:</strong> Hear jokes 😄</div>
                    <div class="command-item"><strong>Yudha:</strong> Play game ⚔️</div>
                    <div class="command-item"><strong>Gandharva:</strong> Music 🎵</div>
                    <div class="command-item"><strong>Khoj:</strong> Web search 🔍</div>
                    <div class="command-item"><strong>Help:</strong> Show guide ❓</div>
                </div>
                
                <h3>🖥️ Console</h3>
                <div id="console" class="console"></div>
            </div>
        </div>
    </div>
    
    <script>
        const btnListen = document.getElementById('btn-listen');
        const btnStop = document.getElementById('btn-stop');
        const statusMode = document.getElementById('status-mode');
        const chatBox = document.getElementById('chat-box');
        const consoleBox = document.getElementById('console');
        const visualizer = document.getElementById('visualizer');
        const nowPlaying = document.getElementById('now-playing');
        
        let isListening = false;
        let isSpeaking = false;
        
        function log(message, level = 'info') {
            const timestamp = new Date().toLocaleTimeString();
            const colors = {
                info: '#0F0',
                warn: '#FF0',
                error: '#F00',
                debug: '#0FF'
            };
            const div = document.createElement('div');
            div.className = 'console-line';
            div.style.color = colors[level] || '#0F0';
            div.textContent = `[${timestamp}] ${message}`;
            consoleBox.appendChild(div);
            consoleBox.scrollTop = consoleBox.scrollHeight;
        }
        
        function addChat(role, text) {
            const div = document.createElement('div');
            div.className = `chat-msg chat-${role}`;
            div.innerHTML = `<strong>${role === 'user' ? 'YOU' : 'HANUMAN'}:</strong> ${text}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        async function startListening() {
            if (isListening) return;
            isListening = true;
            btnListen.disabled = true;
            btnStop.disabled = false;
            visualizer.classList.add('listening');
            statusMode.classList.add('active');
            log('🎙️ Listening loop started', 'info');
            
            while (isListening) {
                if (isSpeaking) {
                    await new Promise(r => setTimeout(r, 500));
                    continue;
                }
                
                try {
                    await recordAndProcess();
                } catch (err) {
                    log(`Error: ${err.message}`, 'error');
                }
                
                await new Promise(r => setTimeout(r, 300));
            }
            
            btnListen.disabled = false;
            btnStop.disabled = true;
            visualizer.classList.remove('listening');
            statusMode.classList.remove('active');
            log('⏹️ Listening stopped', 'info');
        }
        
        function stopListening() {
            isListening = false;
        }
        
        async function recordAndProcess() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                const chunks = [];
                
                mediaRecorder.ondataavailable = e => chunks.push(e.data);
                
                const recordingPromise = new Promise((resolve) => {
                    mediaRecorder.onstop = async () => {
                        stream.getTracks().forEach(t => t.stop());
                        
                        if (isSpeaking) {
                            resolve();
                            return;
                        }
                        
                        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
                        const formData = new FormData();
                        formData.append('audio', audioBlob, 'recording.webm');
                        
                        log('📤 Sending audio...', 'debug');
                        
                        try {
                            const response = await fetch('/process_voice', {
                                method: 'POST',
                                body: formData
                            });
                            
                            const data = await response.json();
                            
                            if (data.transcription) {
                                log(`👂 Heard: "${data.transcription}"`, 'info');
                                if (data.transcription !== '(unclear audio)') {
                                    addChat('user', data.transcription);
                                }
                            }
                            
                            if (data.reply) {
                                log(`🤖 Reply: "${data.reply.substring(0, 50)}..."`, 'info');
                                addChat('ai', data.reply);
                                
                                if (data.audio_url) {
                                    await playAudio(data.audio_url);
                                }
                            }
                            
                            if (data.mode) {
                                statusMode.textContent = `Mode: ${data.mode.toUpperCase()}`;
                            }
                            
                            if (data.now_playing) {
                                nowPlaying.style.display = 'block';
                                document.getElementById('song-title').textContent = data.now_playing.title;
                                document.getElementById('song-link').href = data.now_playing.url;
                            }
                        } catch (err) {
                            log(`Backend error: ${err.message}`, 'error');
                        }
                        
                        resolve();
                    };
                });
                
                mediaRecorder.start();
                setTimeout(() => mediaRecorder.stop(), 3500);
                
                await recordingPromise;
            } catch (err) {
                log(`Microphone error: ${err.message}`, 'error');
                throw err;
            }
        }
        
        function playAudio(url) {
            return new Promise((resolve) => {
                isSpeaking = true;
                visualizer.classList.remove('listening');
                log('🔊 Playing TTS (Mic Paused)', 'warn');
                
                const audio = new Audio(url);
                
                audio.onended = () => {
                    isSpeaking = false;
                    if (isListening) {
                        visualizer.classList.add('listening');
                    }
                    log('✅ TTS finished (Mic Resumed)', 'info');
                    resolve();
                };
                
                audio.onerror = (err) => {
                    log(`Audio error: ${err}`, 'error');
                    isSpeaking = false;
                    resolve();
                };
                
                audio.play().catch(e => {
                    log(`Playback failed: ${e}`, 'error');
                    isSpeaking = false;
                    resolve();
                });
            });
        }
        
        btnListen.addEventListener('click', startListening);
        btnStop.addEventListener('click', stopListening);
        
        log('✅ Frontend initialized. Say "Hanuman" to wake!', 'info');
    </script>
</body>
</html>
"""

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    logger.info("""
    ╔════════════════════════════════════════════════════════════════╗
    ║             🔱 PROJECT HANUMAN - DIVINE VOICE ASSISTANT 🔱     ║
    ║                                                                ║
    ║  Starting server on http://localhost:5000                     ║
    ║                                                                ║
    ║  Commands:                                                     ║
    ║  - Say "Hanuman" to wake up                                   ║
    ║  - Choose: Aagya, Hasya, Yudha, Gandharva, or Khoj            ║
    ║  - Say "Help" for detailed guide                              ║
    ║  - Say "Exit" to return to main menu                          ║
    ║                                                                ║
    ║  Jai Shri Ram! 🙏                                              ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        logger.info(f"Starting Flask server on {CONFIG.FLASK_HOST}:{CONFIG.FLASK_PORT}")
        app.run(
            host=CONFIG.FLASK_HOST,
            port=CONFIG.FLASK_PORT,
            debug=CONFIG.DEBUG,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("\n🙏 Hanuman returns to meditation. Jai Shri Ram!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
