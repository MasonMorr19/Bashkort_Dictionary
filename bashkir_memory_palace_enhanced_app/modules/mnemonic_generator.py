"""
Mnemonic Generator: AI-Powered Memory Story Creator
====================================================
Generates vivid, culturally-rich mnemonics for Bashkir vocabulary
using the Four Birds framework and sensory storytelling.
"""

import random
from typing import Dict, Optional, List


# Template Components
SENSORY_VERBS = {
    'sight': ['see', 'watch', 'glimpse', 'behold', 'witness', 'observe'],
    'sound': ['hear', 'listen to', 'catch the sound of', 'echo'],
    'touch': ['feel', 'touch', 'grasp', 'embrace', 'sense'],
    'taste': ['taste', 'savor', 'sample'],
    'smell': ['smell', 'breathe in', 'catch the scent of']
}

EMOTIONS = ['wonder', 'joy', 'courage', 'peace', 'awe', 'love', 'surprise', 
            'ancient memory', 'warmth', 'determination', 'mystery']

CULTURAL_SYMBOLS = {
    'Eagle': ['golden crown', 'constitution scroll', 'mountain peak', 'Ural-Batyr\'s sword', 
              'parliament dome', 'fierce eyes', 'spreading wings'],
    'Crow': ['ancient painting', 'cave shadow', 'river mist', 'stalactite', 
             'fossilized bone', 'underground stream', '14,000 years'],
    'Anqa': ['phoenix flame', 'mountain smoke', 'hidden potential', 'transformation fire',
             'summit wind', 'dangerous path', 'rising ash'],
    'Ringdove': ['honey jar', 'kuray music', 'grandmother\'s hands', 'village hearth',
                 'family table', 'wedding ring', 'horse mane', 'festival banner']
}

ACTIONS = {
    'Eagle': ['declares', 'proclaims', 'guards', 'watches over', 'descends upon', 'carries'],
    'Crow': ['whispers', 'remembers', 'guards', 'reveals', 'emerges from', 'guides through'],
    'Anqa': ['transforms', 'rises from', 'ignites', 'awakens', 'burns away', 'emerges'],
    'Ringdove': ['coos', 'nests in', 'shares', 'nurtures', 'welcomes', 'celebrates']
}

LOCATIONS = {
    'Ufa': ['parliament steps', 'central square', 'constitution hall', 'government building'],
    'Shulgan-Tash': ['cave mouth', 'painted chamber', 'underground river', 'stalactite gallery'],
    'Yamantau': ['mountain peak', 'treeline', 'rocky path', 'summit wind'],
    'Beloretsk': ['iron forge', 'factory floor', 'craftsman\'s workshop', 'cooling furnace'],
    'Bizhbulyak': ['village hearth', 'family home', 'honey cellar', 'festival ground']
}


class MnemonicGenerator:
    """Generate vivid, culturally-rich mnemonics for Bashkir vocabulary."""
    
    BIRD_TEMPLATES = {
        'Eagle': [
            "🦅 At the {location}, the Eagle {action}! {symbol} {verb} with {emotion}! '{english}' thunders as '{bashkir}' — {phonetic_hint}!",
            "🦅 '{phonetic_hint}!' The Eagle {action} from {location}! {symbol} glows as '{bashkir}' echoes through the hall — {english}!",
            "🦅 The Eagle's eyes fix on you at {location}. '{bashkir}!' it {action}. {verb} the {emotion} as {symbol} reveals: {english}.",
        ],
        'Crow': [
            "🐦⬛ In the {location}, the Crow {action}: '{bashkir}' — {phonetic_hint}! {symbol} holds the secret of {english}.",
            "🐦⬛ '{phonetic_hint}!' {verb} the {emotion} as the Crow {action} through {location}! '{bashkir}' means {english} — the ancestors remember.",
            "🐦⬛ The Crow guards {symbol} in {location}. It {action} the ancient word: '{bashkir}' — {english}. {phonetic_hint}!",
        ],
        'Anqa': [
            "🔥🕊️ From {location}, the Anqa {action}! '{bashkir}' — {phonetic_hint}! {verb} the {emotion} as {symbol} transforms into {english}!",
            "🔥🕊️ '{phonetic_hint}!' The Anqa {action} at {location}! {symbol} burns with {emotion}! '{bashkir}' = {english}!",
            "🔥🕊️ Danger and potential meet at {location}. The Anqa {action}, speaking fire: '{bashkir}' — {english}. {phonetic_hint}!",
        ],
        'Ringdove': [
            "🕊️ At the {location}, the Ringdove {action}! '{bashkir}' — {phonetic_hint}! Share {symbol} with {emotion}. {english}.",
            "🕊️ '{phonetic_hint}!' The Ringdove {action} in {location}. {verb} the {emotion} of {symbol}! '{bashkir}' = {english}.",
            "🕊️ The Ringdove brings {symbol} to {location}. It {action} with {emotion}: '{bashkir}' — {english}. {phonetic_hint}!",
        ]
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the generator with optional random seed."""
        if seed is not None:
            random.seed(seed)
    
    def generate(self, word_data: Dict) -> str:
        """Generate a mnemonic for a word entry."""
        bashkir = word_data.get('bashkir', '')
        english = word_data.get('english', '')
        palace = word_data.get('memory_palace', {})
        bird = palace.get('bird', 'Ringdove')
        locus = palace.get('locus', 'Bizhbulyak')
        
        # Generate phonetic hint
        phonetic_hint = self._create_phonetic_hint(bashkir, english)
        
        # Select template components
        template = random.choice(self.BIRD_TEMPLATES.get(bird, self.BIRD_TEMPLATES['Ringdove']))
        location = random.choice(LOCATIONS.get(locus, ['village']))
        symbol = random.choice(CULTURAL_SYMBOLS.get(bird, ['symbol']))
        action = random.choice(ACTIONS.get(bird, ['reveals']))
        verb = random.choice(random.choice(list(SENSORY_VERBS.values())))
        emotion = random.choice(EMOTIONS)
        
        # Fill template
        mnemonic = template.format(
            location=location,
            symbol=symbol,
            action=action,
            verb=verb.capitalize(),
            emotion=emotion,
            bashkir=bashkir,
            english=english,
            phonetic_hint=phonetic_hint
        )
        
        return mnemonic
    
    def _create_phonetic_hint(self, bashkir: str, english: str) -> str:
        """Create a phonetic memory hook from the Bashkir word."""
        # Simple syllable-based hints
        syllables = self._approximate_syllables(bashkir)
        
        if len(syllables) == 1:
            return f"{syllables[0].upper()}"
        elif len(syllables) == 2:
            return f"{syllables[0].upper()}-{syllables[1].lower()}"
        else:
            return f"{syllables[0].upper()}-{'-'.join(s.lower() for s in syllables[1:])}"
    
    def _approximate_syllables(self, word: str) -> List[str]:
        """Approximate syllable breakdown of a Bashkir word."""
        vowels = 'аәеиоөуүыэюя'
        syllables = []
        current = ''
        
        for char in word.lower():
            current += char
            if char in vowels:
                syllables.append(current)
                current = ''
        
        if current:
            if syllables:
                syllables[-1] += current
            else:
                syllables.append(current)
        
        return syllables if syllables else [word]
    
    def generate_batch(self, words_data: List[Dict]) -> Dict[str, str]:
        """Generate mnemonics for multiple words."""
        return {w['bashkir']: self.generate(w) for w in words_data}
    
    def regenerate(self, word_data: Dict) -> str:
        """Generate a new mnemonic (different from previous)."""
        # Reseed to get different result
        random.seed()
        return self.generate(word_data)


class StoryChainGenerator:
    """Generate connected story chains for vocabulary sequences."""
    
    CONNECTORS = [
        "As you step forward,",
        "The path leads you to",
        "Suddenly,",
        "In the distance,",
        "Your guide points toward",
        "The air changes as",
        "Memory awakens:",
        "Time shifts, and",
    ]
    
    def generate_chain(self, words_data: List[Dict], locus: str) -> str:
        """Generate a connected story visiting all words in sequence."""
        if not words_data:
            return ""
        
        story_parts = []
        bird = words_data[0].get('memory_palace', {}).get('bird', 'Ringdove')
        
        # Opening
        opening = self._generate_opening(locus, bird)
        story_parts.append(opening)
        
        # Middle - each word
        for i, word_data in enumerate(words_data):
            connector = random.choice(self.CONNECTORS) if i > 0 else ""
            word_story = self._generate_word_encounter(word_data, connector)
            story_parts.append(word_story)
        
        # Closing
        closing = self._generate_closing(locus, bird, len(words_data))
        story_parts.append(closing)
        
        return "\n\n".join(story_parts)
    
    def _generate_opening(self, locus: str, bird: str) -> str:
        """Generate opening paragraph for the story chain."""
        openings = {
            'Eagle': f"You stand at the threshold of {locus}. The Eagle circles above, golden feathers catching the light. 'Voyager,' its voice echoes, 'I am the Intellect that knows. Follow me.'",
            'Crow': f"The entrance to {locus} looms before you. The Crow emerges from shadow, ancient eyes gleaming. 'Voyager,' it croaks, 'I am Memory itself. What was, remains.'",
            'Anqa': f"The path to {locus} rises before you, wreathed in mist. The Anqa appears in flame and smoke. 'Voyager,' it speaks in fire, 'I am Potential. Danger transforms.'",
            'Ringdove': f"The gates of {locus} open with warmth. The Ringdove coos from the eaves. 'Voyager,' it sings, 'I am the Soul that nurtures. Welcome home.'"
        }
        return openings.get(bird, openings['Ringdove'])
    
    def _generate_word_encounter(self, word_data: Dict, connector: str) -> str:
        """Generate encounter paragraph for a single word."""
        bashkir = word_data.get('bashkir', '')
        english = word_data.get('english', '')
        mnemonic = word_data.get('memory_palace', {}).get('mnemonic', '')
        
        if mnemonic:
            return f"{connector} {mnemonic}"
        else:
            return f"{connector} You encounter **{bashkir}** ({english}). The word settles into your memory."
    
    def _generate_closing(self, locus: str, bird: str, word_count: int) -> str:
        """Generate closing paragraph for the story chain."""
        closings = {
            'Eagle': f"The Eagle alights beside you. '{word_count} words now fly with you. The law is learned; the knowledge rises. Return when you are ready to soar higher.'",
            'Crow': f"The Crow folds its wings. '{word_count} memories restored. What was forgotten is remembered again. The ancestors smile.' The cave grows still.",
            'Anqa': f"The Anqa's flames subside. '{word_count} transformations complete. From danger, wisdom. From fear, strength.' The mountain releases you.",
            'Ringdove': f"The Ringdove accompanies you to the gate. '{word_count} words shared, {word_count} gifts received. You are no longer a stranger here. Return with honey on your lips.'"
        }
        return closings.get(bird, closings['Ringdove'])


# Convenience functions
def generate_mnemonic(word_data: Dict) -> str:
    """Generate a single mnemonic."""
    generator = MnemonicGenerator()
    return generator.generate(word_data)


def generate_story_chain(words_data: List[Dict], locus: str) -> str:
    """Generate a connected story for a sequence of words."""
    generator = StoryChainGenerator()
    return generator.generate_chain(words_data, locus)


if __name__ == "__main__":
    # Test the module
    test_word = {
        'bashkir': 'бал',
        'english': 'honey',
        'memory_palace': {
            'bird': 'Ringdove',
            'locus': 'Bizhbulyak'
        }
    }
    
    generator = MnemonicGenerator()
    print("Generated mnemonic for 'бал' (honey):")
    print(generator.generate(test_word))
    print("\nAnother version:")
    print(generator.regenerate(test_word))
