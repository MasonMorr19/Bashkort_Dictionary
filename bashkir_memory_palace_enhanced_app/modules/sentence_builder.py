"""
Sentence Builder: Interactive Bashkir Sentence Construction
===========================================================
Helps learners construct grammatically correct Bashkir sentences
with case marking, word order guidance, and audio generation.
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SentenceToken:
    """Represents a token in a constructed sentence."""
    word: str
    base_form: str
    english: str
    pos: str  # Part of speech
    case: str = "nominative"
    suffix: str = ""
    
    def get_display(self) -> str:
        """Get the display form with suffix."""
        return f"{self.word}{self.suffix}"


class BashkirGrammar:
    """Grammar rules and transformations for Bashkir."""
    
    # Vowel categories for harmony
    BACK_VOWELS = set('аоуы')
    FRONT_VOWELS = set('әөүеи')
    
    # Case suffixes (back/front vowel variants)
    CASE_SUFFIXES = {
        'nominative': ('', ''),
        'genitive': ('ның', 'нең'),
        'dative': ('ға', 'гә'),  # Also -ҡа/-кә after voiceless
        'accusative': ('ны', 'не'),  # Also -ды/-де/-ты/-те
        'locative': ('да', 'дә'),  # Also -та/-тә
        'ablative': ('дан', 'дән'),  # Also -тан/-тән/-нан/-нән
    }
    
    # Voiceless consonants (affect suffix selection)
    VOICELESS = set('пфктшсщчц')
    
    @classmethod
    def get_vowel_type(cls, word: str) -> str:
        """Determine if word uses back or front vowels."""
        for char in reversed(word.lower()):
            if char in cls.BACK_VOWELS:
                return 'back'
            elif char in cls.FRONT_VOWELS:
                return 'front'
        return 'back'  # Default to back
    
    @classmethod
    def get_final_consonant_type(cls, word: str) -> str:
        """Determine if word ends in voiced or voiceless consonant."""
        if word and word[-1].lower() in cls.VOICELESS:
            return 'voiceless'
        return 'voiced'
    
    @classmethod
    def apply_case(cls, word: str, case: str) -> Tuple[str, str]:
        """
        Apply case suffix to a word.
        
        Returns:
            Tuple of (suffix, full_word_with_suffix)
        """
        if case == 'nominative' or case not in cls.CASE_SUFFIXES:
            return '', word
        
        vowel_type = cls.get_vowel_type(word)
        suffix_pair = cls.CASE_SUFFIXES[case]
        
        suffix = suffix_pair[0] if vowel_type == 'back' else suffix_pair[1]
        
        return suffix, word + suffix
    
    @classmethod
    def conjugate_verb(cls, verb_stem: str, person: str, number: str) -> str:
        """
        Conjugate a verb stem for person and number.
        
        This is a simplified version - Bashkir verb morphology is complex!
        """
        vowel_type = cls.get_vowel_type(verb_stem)
        
        # Present tense suffixes (simplified)
        if vowel_type == 'back':
            suffixes = {
                ('1', 'sg'): 'ам',
                ('2', 'sg'): 'аһың',
                ('3', 'sg'): 'а',
                ('1', 'pl'): 'абыҙ',
                ('2', 'pl'): 'аһығыҙ',
                ('3', 'pl'): 'алар',
            }
        else:
            suffixes = {
                ('1', 'sg'): 'әм',
                ('2', 'sg'): 'әһең',
                ('3', 'sg'): 'ә',
                ('1', 'pl'): 'әбеҙ',
                ('2', 'pl'): 'әһегеҙ',
                ('3', 'pl'): 'әләр',
            }
        
        suffix = suffixes.get((person, number), 'а')
        return verb_stem + suffix


class SentenceBuilder:
    """Build Bashkir sentences from vocabulary."""
    
    def __init__(self, words_data: List[Dict], patterns_data: Dict):
        """
        Initialize the builder with vocabulary and patterns.
        
        Args:
            words_data: List of word dictionaries
            patterns_data: Dictionary with patterns and grammar reference
        """
        self.words = {w['bashkir']: w for w in words_data}
        self.words_by_english = {w['english'].lower(): w for w in words_data}
        self.patterns = patterns_data.get('patterns', [])
        self.grammar_ref = patterns_data.get('grammar_reference', {})
        self.word_bank = patterns_data.get('word_bank_categories', {})
        
        self.current_sentence: List[SentenceToken] = []
        self.saved_sentences: List[Dict] = []
    
    def get_word_bank(self, category: Optional[str] = None) -> List[Dict]:
        """Get words available for sentence building."""
        if category and category in self.word_bank:
            words_list = self.word_bank[category]
            return [self.words.get(w, {'bashkir': w, 'english': '?'}) for w in words_list]
        
        # Return all words grouped by POS
        result = []
        for word_data in self.words.values():
            result.append({
                'bashkir': word_data['bashkir'],
                'english': word_data.get('english', ''),
                'pos': word_data.get('pos', 'noun')
            })
        return result
    
    def add_word(self, bashkir: str, case: str = 'nominative') -> bool:
        """Add a word to the current sentence."""
        word_data = self.words.get(bashkir)
        if not word_data:
            return False
        
        suffix, full_form = BashkirGrammar.apply_case(bashkir, case)
        
        token = SentenceToken(
            word=bashkir,
            base_form=bashkir,
            english=word_data.get('english', ''),
            pos=word_data.get('pos', 'noun'),
            case=case,
            suffix=suffix
        )
        
        self.current_sentence.append(token)
        return True
    
    def remove_word(self, index: int) -> bool:
        """Remove a word from the current sentence by index."""
        if 0 <= index < len(self.current_sentence):
            self.current_sentence.pop(index)
            return True
        return False
    
    def clear_sentence(self):
        """Clear the current sentence."""
        self.current_sentence = []
    
    def get_sentence_text(self) -> str:
        """Get the current sentence as text."""
        return ' '.join(token.get_display() for token in self.current_sentence)
    
    def get_sentence_gloss(self) -> str:
        """Get word-by-word gloss of current sentence."""
        glosses = []
        for token in self.current_sentence:
            gloss = token.english
            if token.case != 'nominative':
                gloss += f" ({token.case})"
            glosses.append(gloss)
        return ' | '.join(glosses)
    
    def get_sentence_analysis(self) -> Dict:
        """Analyze the current sentence structure."""
        if not self.current_sentence:
            return {'error': 'No sentence to analyze'}
        
        analysis = {
            'text': self.get_sentence_text(),
            'gloss': self.get_sentence_gloss(),
            'word_count': len(self.current_sentence),
            'structure': [],
            'warnings': []
        }
        
        # Analyze structure
        has_verb = False
        has_subject = False
        
        for i, token in enumerate(self.current_sentence):
            analysis['structure'].append({
                'position': i + 1,
                'word': token.get_display(),
                'base': token.base_form,
                'english': token.english,
                'pos': token.pos,
                'case': token.case
            })
            
            if token.pos == 'verb':
                has_verb = True
            if token.pos == 'pronoun' and token.case == 'nominative':
                has_subject = True
        
        # Check word order (SOV)
        verb_position = None
        for i, token in enumerate(self.current_sentence):
            if token.pos == 'verb':
                verb_position = i
                break
        
        if verb_position is not None and verb_position < len(self.current_sentence) - 1:
            analysis['warnings'].append(
                "In Bashkir, verbs typically come at the END of the sentence (SOV order)"
            )
        
        if has_verb and not has_subject:
            analysis['warnings'].append(
                "Consider adding a subject pronoun (Мин, Һин, Ул, etc.)"
            )
        
        return analysis
    
    def save_sentence(self, english_translation: str = "") -> Dict:
        """Save the current sentence."""
        if not self.current_sentence:
            return {'error': 'No sentence to save'}
        
        sentence_data = {
            'bashkir': self.get_sentence_text(),
            'gloss': self.get_sentence_gloss(),
            'english': english_translation,
            'tokens': [
                {
                    'word': t.get_display(),
                    'base': t.base_form,
                    'pos': t.pos,
                    'case': t.case
                }
                for t in self.current_sentence
            ],
            'audio_hash': hashlib.md5(self.get_sentence_text().encode()).hexdigest()
        }
        
        self.saved_sentences.append(sentence_data)
        return sentence_data
    
    def get_pattern_suggestions(self) -> List[Dict]:
        """Get sentence patterns the user could try."""
        suggestions = []
        
        for pattern in self.patterns[:5]:  # Top 5 patterns
            suggestions.append({
                'name': pattern.get('name', ''),
                'template': pattern.get('template', ''),
                'english': pattern.get('english_pattern', ''),
                'level': pattern.get('level', 'beginner'),
                'example': pattern.get('examples', [{}])[0] if pattern.get('examples') else {}
            })
        
        return suggestions
    
    def apply_pattern(self, pattern_id: str, slot_values: Dict[str, str]) -> Optional[str]:
        """
        Apply a pattern with given slot values.
        
        Args:
            pattern_id: ID of the pattern to apply
            slot_values: Dict mapping slot positions to Bashkir words
        
        Returns:
            The constructed sentence or None if failed
        """
        pattern = None
        for p in self.patterns:
            if p.get('id') == pattern_id:
                pattern = p
                break
        
        if not pattern:
            return None
        
        # Clear current sentence
        self.clear_sentence()
        
        # Build sentence from pattern
        template = pattern.get('template', '')
        
        # Simple slot replacement
        for slot_key, word in slot_values.items():
            # Determine case from pattern slots
            case = 'nominative'
            for slot in pattern.get('slots', []):
                if str(slot.get('position')) == slot_key:
                    case = slot.get('case', 'nominative')
                    break
            
            self.add_word(word, case)
        
        return self.get_sentence_text()
    
    def export_phrasebook(self, filepath: str):
        """Export saved sentences to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.saved_sentences, f, ensure_ascii=False, indent=2)
    
    def import_phrasebook(self, filepath: str):
        """Import sentences from a JSON file."""
        if Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self.saved_sentences = json.load(f)


def load_sentence_builder(words_file: str, patterns_file: str) -> SentenceBuilder:
    """Load a sentence builder from data files."""
    with open(words_file, 'r', encoding='utf-8') as f:
        words_data = json.load(f)
    
    with open(patterns_file, 'r', encoding='utf-8') as f:
        patterns_data = json.load(f)
    
    return SentenceBuilder(words_data, patterns_data)


if __name__ == "__main__":
    # Test the module
    print("Testing BashkirGrammar...")
    
    # Test case application
    word = "тау"
    for case in ['nominative', 'genitive', 'dative', 'accusative', 'locative', 'ablative']:
        suffix, result = BashkirGrammar.apply_case(word, case)
        print(f"  {word} + {case} = {result}")
    
    print("\nTesting with front vowel word...")
    word = "өй"
    for case in ['nominative', 'genitive', 'dative']:
        suffix, result = BashkirGrammar.apply_case(word, case)
        print(f"  {word} + {case} = {result}")
