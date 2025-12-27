#!/usr/bin/env python3
"""
🎯 FUZZY COMMAND MATCHER
========================
Handles fuzzy matching for all HANUMAN commands.
Detects mishearings and variations with confidence scoring.
"""

import logging
from typing import Tuple, Optional, Dict
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)


class FuzzyCommandMatcher:
    """Fuzzy matching engine for all HANUMAN commands."""

    # Thresholds
    THRESHOLD_WAKE_WORD = 75
    THRESHOLD_COMMAND = 70
    THRESHOLD_MOVE = 75
    THRESHOLD_ACTION = 70

    # Wake words
    WAKE_WORDS = {
        'hanuman': {
            'primary': ['hanuman', 'hey hanuman', 'o hanuman', 'jai hanuman'],
            'fuzzy': ['anuman', 'humanan', 'hunuman', 'hanoman', 'hanumanji', 
                     'hanaman', 'hanauman', 'hanunam', 'ha numan', 'hanman', 
                     'hamuman', 'hanuran', 'human']
        }
    }

    # Command modes
    COMMAND_VARIATIONS = {
        'aagya': {
            'primary': ['aagya', 'aagya mode', 'command', 'chat', 'talk', 'ask', 'answer'],
            'fuzzy': ['agya', 'agyaa', 'ayga', 'chatting', 'talking', 'asking', 
                     'answering', 'command mode', 'knowledge', 'learning mode',
                     'question', 'advice', 'information']
        },
        'hasya': {
            'primary': ['hasya', 'hasya mode', 'joke', 'jokes', 'laugh', 'funny', 
                       'humor', 'comedy'],
            'fuzzy': ['hassa', 'hassya', 'joking', 'laughing', 'humorous', 'comic',
                     'ha ha', 'laughter', 'prank', 'pranks', 'joke mode', 'funny mode',
                     'laugh mode', 'funny story', 'humor time']
        },
        'yudha': {
            'primary': ['yudha', 'yudha mode', 'game', 'play', 'battle', 'fight'],
            'fuzzy': ['yudh', 'yudhha', 'gaming', 'playing', 'battling', 'fighting',
                     'game mode', 'play mode', 'battle mode', 'rps', 'dice game',
                     'card game', 'challenge me']
        },
        'gandharva': {
            'primary': ['gandharva', 'gandharva mode', 'music', 'song', 'play song', 
                       'singing', 'songs'],
            'fuzzy': ['gandharv', 'music mode', 'song mode', 'musical', 'melody',
                     'tune', 'audio', 'sound', 'entertainment', 'play music',
                     'music time', 'playlist', 'singer mode', 'musician']
        },
        'khoj': {
            'primary': ['khoj', 'khoj mode', 'search', 'find', 'web', 'information', 
                       'research', 'google'],
            'fuzzy': ['search mode', 'finding', 'research mode', 'searching',
                     'lookup', 'inquire', 'ask online', 'search online',
                     'web search', 'find online', 'internet search', 'information mode',
                     'knowledge search', 'google it']
        }
    }

    # Game moves
    GAME_MOVES = {
        'rock': {
            'primary': ['rock', 'patthar', 'pathar', 'stone', 'boulder'],
            'fuzzy': ['rok', 'roack', 'roc', 'rocks', 'stonee']
        },
        'paper': {
            'primary': ['paper', 'kagaz', 'kagaj', 'cloth'],
            'fuzzy': ['papper', 'papar', 'papeer', 'paper sheet']
        },
        'scissors': {
            'primary': ['scissors', 'kenchi', 'kainchi', 'cuts'],
            'fuzzy': ['scissor', 'scizzors', 'cutting', 'cutting tool']
        }
    }

    # Actions
    ACTIONS = {
        'help': {
            'primary': ['help', 'guide', 'help me', 'how to', 'instructions'],
            'fuzzy': ['help mode', 'helping', 'guideline', 'guide me', 'instruction',
                     'tutorial', 'how do i', 'show me', 'tell me how']
        },
        'exit': {
            'primary': ['exit', 'quit', 'leave', 'back', 'go back', 'stop'],
            'fuzzy': ['exits', 'exiting', 'quit mode', 'leaving', 'go to main',
                     'main menu', 'home', 'cancel', 'close', 'end', 'return']
        }
    }

    @staticmethod
    def detect_wake_word(text: str) -> Tuple[Optional[str], int]:
        """Detect wake word with fuzzy matching."""
        text_lower = text.lower().strip()
        
        # Exact matches first
        for wake_word, variations in FuzzyCommandMatcher.WAKE_WORDS.items():
            for primary in variations['primary']:
                if primary in text_lower:
                    logger.info(f"✅ Wake word detected (exact 100%): {primary}")
                    return wake_word, 100
        
        # Fuzzy matches
        best_match = None
        best_score = 0
        
        for wake_word, variations in FuzzyCommandMatcher.WAKE_WORDS.items():
            for primary in variations['primary']:
                score = fuzz.partial_ratio(primary, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = wake_word
            
            for fuzzy_var in variations['fuzzy']:
                score = fuzz.partial_ratio(fuzzy_var, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = wake_word
        
        if best_score >= FuzzyCommandMatcher.THRESHOLD_WAKE_WORD:
            logger.info(f"🎯 Wake word detected (fuzzy {best_score}%): {best_match}")
            return best_match, best_score
        
        return None, 0

    @staticmethod
    def detect_mode(text: str) -> Tuple[Optional[str], int]:
        """Detect command mode with fuzzy matching."""
        text_lower = text.lower().strip()
        
        # Exact matches first
        for mode, variations in FuzzyCommandMatcher.COMMAND_VARIATIONS.items():
            for primary in variations['primary']:
                if primary in text_lower:
                    logger.info(f"🎯 Mode detected (exact 100%): {mode}")
                    return mode, 100
        
        # Fuzzy matches
        best_match = None
        best_score = 0
        
        for mode, variations in FuzzyCommandMatcher.COMMAND_VARIATIONS.items():
            for primary in variations['primary']:
                score = fuzz.partial_ratio(primary, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = mode
            
            for fuzzy_var in variations['fuzzy']:
                score = fuzz.partial_ratio(fuzzy_var, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = mode
        
        if best_score >= FuzzyCommandMatcher.THRESHOLD_COMMAND:
            logger.info(f"🎯 Mode detected (fuzzy {best_score}%): {best_match}")
            return best_match, best_score
        
        return None, 0

    @staticmethod
    def detect_move(text: str) -> Tuple[Optional[str], int]:
        """Detect game move with fuzzy matching."""
        text_lower = text.lower().strip()
        
        # Exact matches first
        for move, variations in FuzzyCommandMatcher.GAME_MOVES.items():
            for primary in variations['primary']:
                if primary in text_lower:
                    logger.info(f"🎯 Game move detected (exact 100%): {move}")
                    return move, 100
        
        # Fuzzy matches
        best_match = None
        best_score = 0
        
        for move, variations in FuzzyCommandMatcher.GAME_MOVES.items():
            for primary in variations['primary']:
                score = fuzz.partial_ratio(primary, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = move
            
            for fuzzy_var in variations['fuzzy']:
                score = fuzz.partial_ratio(fuzzy_var, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = move
        
        if best_score >= FuzzyCommandMatcher.THRESHOLD_MOVE:
            logger.info(f"🎯 Game move detected (fuzzy {best_score}%): {best_match}")
            return best_match, best_score
        
        return None, 0

    @staticmethod
    def detect_action(text: str) -> Tuple[Optional[str], int]:
        """Detect action commands (help/exit) with fuzzy matching."""
        text_lower = text.lower().strip()
        
        # Exact matches first
        for action, variations in FuzzyCommandMatcher.ACTIONS.items():
            for primary in variations['primary']:
                if primary in text_lower:
                    logger.info(f"✅ Action detected (exact 100%): {action}")
                    return action, 100
        
        # Fuzzy matches
        best_match = None
        best_score = 0
        
        for action, variations in FuzzyCommandMatcher.ACTIONS.items():
            for primary in variations['primary']:
                score = fuzz.partial_ratio(primary, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = action
            
            for fuzzy_var in variations['fuzzy']:
                score = fuzz.partial_ratio(fuzzy_var, text_lower)
                if score > best_score:
                    best_score = score
                    best_match = action
        
        if best_score >= FuzzyCommandMatcher.THRESHOLD_ACTION:
            logger.info(f"✅ Action detected (fuzzy {best_score}%): {best_match}")
            return best_match, best_score
        
        return None, 0

    @staticmethod
    def get_summary() -> Dict:
        """Get summary of all fuzzy patterns."""
        return {
            'wake_words': list(FuzzyCommandMatcher.WAKE_WORDS.keys()),
            'modes': list(FuzzyCommandMatcher.COMMAND_VARIATIONS.keys()),
            'game_moves': list(FuzzyCommandMatcher.GAME_MOVES.keys()),
            'actions': list(FuzzyCommandMatcher.ACTIONS.keys()),
            'thresholds': {
                'wake_word': FuzzyCommandMatcher.THRESHOLD_WAKE_WORD,
                'command': FuzzyCommandMatcher.THRESHOLD_COMMAND,
                'move': FuzzyCommandMatcher.THRESHOLD_MOVE,
                'action': FuzzyCommandMatcher.THRESHOLD_ACTION
            }
        }
