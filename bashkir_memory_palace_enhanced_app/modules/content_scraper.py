"""
Content Scraper for Bashkir Reading Practice
============================================
Web scraping and content curation for reading practice materials.

Features:
- Curated Bashkir text sources
- Content difficulty grading
- Vocabulary extraction and highlighting
- Offline content caching
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Optional imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class DifficultyLevel(Enum):
    """Reading difficulty levels."""
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    NATIVE = 5


@dataclass
class ReadingText:
    """A reading practice text."""
    id: str
    title: str
    content: str
    source: str
    difficulty: DifficultyLevel
    word_count: int
    vocabulary: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    audio_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'difficulty': self.difficulty.name,
            'word_count': self.word_count,
            'vocabulary': self.vocabulary,
            'topics': self.topics,
            'audio_url': self.audio_url,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ReadingText':
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            source=data['source'],
            difficulty=DifficultyLevel[data['difficulty']],
            word_count=data['word_count'],
            vocabulary=data.get('vocabulary', []),
            topics=data.get('topics', []),
            audio_url=data.get('audio_url'),
            created_at=data.get('created_at', datetime.now().isoformat())
        )


class ContentScraper:
    """
    Service for scraping and curating Bashkir reading content.

    Provides graded reading materials from various sources,
    with vocabulary extraction and difficulty assessment.
    """

    # Curated content sources (for reference, actual scraping requires permission)
    CONTENT_SOURCES = {
        'wikipedia': {
            'name': 'Bashkir Wikipedia',
            'url': 'https://ba.wikipedia.org',
            'type': 'encyclopedia',
            'difficulty': DifficultyLevel.INTERMEDIATE
        },
        'bashinform': {
            'name': 'Bashinform News',
            'url': 'https://www.bashinform.ru/news/',
            'type': 'news',
            'difficulty': DifficultyLevel.ADVANCED
        }
    }

    # Built-in reading texts (curated, no scraping needed)
    BUILTIN_TEXTS = [
        {
            'id': 'intro_001',
            'title': 'Һаумыһығыҙ! (Hello!)',
            'content': '''Һаумыһығыҙ! Мин — Әминә. Мин Өфөлә йәшәйем.
Өфө — Башҡортостан башҡалаһы. Ул матур ҡала.
Минең ғаиләм ҙур: атай, әсәй, олатай, өләсәй, ҡустым һәм һеңлем.
Мин башҡорт телен һөйәм. Ул матур тел!''',
            'source': 'Curated beginner text',
            'difficulty': DifficultyLevel.BEGINNER,
            'topics': ['greetings', 'family', 'city'],
            'vocabulary': ['һаумыһығыҙ', 'мин', 'йәшәйем', 'башҡала', 'матур', 'ғаилә', 'атай', 'әсәй', 'тел']
        },
        {
            'id': 'intro_002',
            'title': 'Минең көнөм (My Day)',
            'content': '''Мин иртән һәғәт етелә торам. Өйҙә иртәнге аш ашайым.
Һуңынан мәктәпкә барам. Мәктәптә дәрестәр бар.
Көн уртаһында ял итәм һәм төшкө аш ашайым.
Кистән өйгә ҡайтам. Кискә өй эштәрен эшләйем.
Төнлә йоҡлайым. Яҡшы төндәр!''',
            'source': 'Curated beginner text',
            'difficulty': DifficultyLevel.BEGINNER,
            'topics': ['daily routine', 'time', 'school'],
            'vocabulary': ['иртән', 'торам', 'аш', 'мәктәп', 'дәрес', 'ял', 'өй', 'төн', 'йоҡлайым']
        },
        {
            'id': 'nature_001',
            'title': 'Башҡортостан тәбиғәте (Nature of Bashkortostan)',
            'content': '''Башҡортостан — матур ил. Унда тауҙар, урмандар, йылғалар бар.
Урал тауҙары — иң бейек тауҙар. Ямантау — иң бейек тау.
Ағиҙел — иң оҙон йылға. Ул Ураллан ағып сыға.
Урмандарҙа айыуҙар, бүреләр, төлкөләр йәшәй.
Башҡортостан — умарта иле. Башҡорт балы — бик тәмле!''',
            'source': 'Curated elementary text',
            'difficulty': DifficultyLevel.ELEMENTARY,
            'topics': ['nature', 'geography', 'animals'],
            'vocabulary': ['тәбиғәт', 'тау', 'урман', 'йылға', 'бейек', 'айыу', 'бүре', 'бал', 'тәмле']
        },
        {
            'id': 'legend_001',
            'title': 'Урал батыр тураһында (About Ural-Batyr)',
            'content': '''Урал батыр — башҡорт халҡының легендар геройы.
Ул Йәнбирҙә һәм Йәнбикә ғаиләһендә тыуған.
Урал батырҙың ағаһы — Шүлгән.
Урал батыр яуызлыҡ менән көрәште. Ул Үлемде еңде.
Үлгәс, Урал батыр тау булып ҡалды. Ул тау хәҙер Урал тауҙары тип атала.
Шүлгән мәңгелек хәтергә ҡалды Шүлгәнташ мәмерйәһендә.''',
            'source': 'Curated intermediate text',
            'difficulty': DifficultyLevel.INTERMEDIATE,
            'topics': ['mythology', 'Ural-Batyr', 'legend'],
            'vocabulary': ['батыр', 'халыҡ', 'легенда', 'тыуған', 'көрәш', 'еңеү', 'тау', 'мәмерйә']
        },
        {
            'id': 'history_001',
            'title': 'Башҡортостан тарихы (History of Bashkortostan)',
            'content': '''Башҡорттар — Урал тауҙарында йәшәгән иҫке халыҡ.
XVI быуатта башҡорттар Рәсәй составына инде.
1917 йылда Башҡортостан автономияһы булды.
1919 йылда Башҡорт АССР ойошторолдо — тәүге автоном республика.
1990 йылда Башҡортостан суверенитет яралышты.
Бөгөн Башҡортостан — Рәсәй Федерацияһының республикаһы.
4 миллион кеше йәшәй. Башҡала — Өфө.''',
            'source': 'Curated intermediate text',
            'difficulty': DifficultyLevel.INTERMEDIATE,
            'topics': ['history', 'politics', 'autonomy'],
            'vocabulary': ['тарих', 'халыҡ', 'быуат', 'автономия', 'республика', 'суверенитет', 'федерация']
        },
        {
            'id': 'culture_001',
            'title': 'Сабантуй (Sabantuy Festival)',
            'content': '''Сабантуй — башҡорт һәм татар халыҡтарының иң ҙур бәйрәме.
"Сабан" — "һабан" (плуг), "туй" — "бәйрәм" тигәнде аңлата.
Сабантуй яҙҙа, сәсеү эштәре тамамланғас, үткәрелә.

Бәйрәмдә күп уйындар бар:
— Көрәш — милли көрәш, иң көслө батыр булырға
— Ат сабышы — атлар йүгереше
— Ҡап-ҡап — ҡаплы йүгереш
— Ҡашыҡ менән йомортҡа — тиҙ йүгереү

Сабантуйҙа йырлайҙар, бейейҙәр, ҡурай уйнайҙар.
Бөтә халыҡ бергә шатлана!''',
            'source': 'Curated intermediate text',
            'difficulty': DifficultyLevel.INTERMEDIATE,
            'topics': ['culture', 'festival', 'traditions'],
            'vocabulary': ['бәйрәм', 'көрәш', 'ат сабышы', 'уйын', 'йыр', 'бейеү', 'ҡурай', 'халыҡ']
        },
        {
            'id': 'literature_001',
            'title': 'Мостай Кәрим — башҡорт шағиры (Mustai Karim — Bashkir Poet)',
            'content': '''Мостай Кәрим (1919-2005) — бөйөк башҡорт яҙыусыһы һәм шағиры.
Ул Кляшево ауылында тыуған. Әҫәл исеме — Мостафа Сафич Каримов.

Мостай Кәрим күп әҫәрҙәр яҙған:
— "Оҙон-оҙаҡ бала саҡ" — автобиографик повесть
— "Ай тотолған төндә" — драма
— "Үлмәҫбай" — пьеса
— Күп шиғырҙар һәм поэмалар

Мостай Кәрим Социалистик Хеҙмәт Геройы исемен алды.
Уның әҫәрҙәре күп телгә тәржемә ителде.
Өфөлә Мостай Кәрим исемендәге театр һәм музей бар.''',
            'source': 'Curated advanced text',
            'difficulty': DifficultyLevel.ADVANCED,
            'topics': ['literature', 'poetry', 'famous people'],
            'vocabulary': ['шағир', 'яҙыусы', 'әҫәр', 'повесть', 'драма', 'шиғыр', 'поэма', 'тәржемә']
        },
        {
            'id': 'proverbs_001',
            'title': 'Башҡорт мәҡәлдәре (Bashkir Proverbs)',
            'content': '''Башҡорт халҡының күп аҡыллы мәҡәлдәре бар:

🐴 Ат — ир ҡанаты.
(A horse is a man's wings.)

🏠 Ата йорто — алтын бишек.
(Father's home is a golden cradle.)

📚 Белем — байлыҡ, белемһеҙлек — ярлылыҡ.
(Knowledge is wealth, ignorance is poverty.)

🤝 Берҙәмлек булһа — тереклек булыр.
(Where there is unity, there is life.)

💪 Эш беткәс уйна.
(Play after work is done.)

🌾 Хеҙмәт итһәң, ризыҡ табырһың.
(If you work, you will find sustenance.)

🗣️ Тел — бал, тел — бал ҡорто.
(The tongue is honey, the tongue is a bee.)

❤️ Туған ер — алтын бишек.
(Native land is a golden cradle.)''',
            'source': 'Curated elementary text',
            'difficulty': DifficultyLevel.ELEMENTARY,
            'topics': ['proverbs', 'wisdom', 'culture'],
            'vocabulary': ['мәҡәл', 'ат', 'йорт', 'белем', 'хеҙмәт', 'тел', 'туған ер']
        }
    ]

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize content scraper.

        Args:
            cache_dir: Directory for caching content
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path('data/reading_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._texts: Dict[str, ReadingText] = {}
        self._load_builtin_texts()

    def _load_builtin_texts(self):
        """Load built-in curated texts."""
        for text_data in self.BUILTIN_TEXTS:
            text = ReadingText(
                id=text_data['id'],
                title=text_data['title'],
                content=text_data['content'],
                source=text_data['source'],
                difficulty=text_data['difficulty'],
                word_count=len(text_data['content'].split()),
                vocabulary=text_data.get('vocabulary', []),
                topics=text_data.get('topics', [])
            )
            self._texts[text.id] = text

    @property
    def is_scraping_available(self) -> bool:
        """Check if web scraping dependencies are available."""
        return REQUESTS_AVAILABLE and BS4_AVAILABLE

    def get_all_texts(self) -> List[ReadingText]:
        """Get all available reading texts."""
        return list(self._texts.values())

    def get_text_by_id(self, text_id: str) -> Optional[ReadingText]:
        """Get a specific text by ID."""
        return self._texts.get(text_id)

    def get_texts_by_difficulty(self, difficulty: DifficultyLevel) -> List[ReadingText]:
        """Get texts filtered by difficulty level."""
        return [t for t in self._texts.values() if t.difficulty == difficulty]

    def get_texts_by_topic(self, topic: str) -> List[ReadingText]:
        """Get texts filtered by topic."""
        topic_lower = topic.lower()
        return [t for t in self._texts.values()
                if any(topic_lower in t.lower() for t in t.topics)]

    def analyze_difficulty(self, text: str, dictionary: List[Dict]) -> DifficultyLevel:
        """
        Analyze text difficulty based on vocabulary coverage.

        Args:
            text: Text to analyze
            dictionary: Word dictionary for known words

        Returns:
            Estimated difficulty level
        """
        # Extract words
        words = set(re.findall(r'\b[а-яәөүғҡңһҙёА-ЯӘӨҮҒҠҢҺҘЁ]+\b', text.lower()))

        # Get dictionary words
        dict_words = {w['bashkir'].lower() for w in dictionary}

        # Calculate coverage
        if not words:
            return DifficultyLevel.BEGINNER

        known_words = words & dict_words
        coverage = len(known_words) / len(words)

        # Average word length
        avg_length = sum(len(w) for w in words) / len(words)

        # Sentence complexity (words per sentence)
        sentences = re.split(r'[.!?]', text)
        sentences = [s for s in sentences if s.strip()]
        words_per_sentence = len(words) / max(len(sentences), 1)

        # Determine difficulty
        if coverage > 0.8 and avg_length < 5 and words_per_sentence < 8:
            return DifficultyLevel.BEGINNER
        elif coverage > 0.6 and avg_length < 6 and words_per_sentence < 12:
            return DifficultyLevel.ELEMENTARY
        elif coverage > 0.4 and words_per_sentence < 15:
            return DifficultyLevel.INTERMEDIATE
        elif coverage > 0.2:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.NATIVE

    def extract_vocabulary(self, text: str, dictionary: List[Dict]) -> List[Dict]:
        """
        Extract vocabulary from text with dictionary matches.

        Args:
            text: Text to analyze
            dictionary: Word dictionary

        Returns:
            List of vocabulary items with translations
        """
        # Extract unique words
        words = set(re.findall(r'\b[а-яәөүғҡңһҙёА-ЯӘӨҮҒҠҢҺҘЁ]+\b', text.lower()))

        # Build lookup
        dict_lookup = {w['bashkir'].lower(): w for w in dictionary}

        vocabulary = []
        for word in sorted(words):
            if word in dict_lookup:
                entry = dict_lookup[word]
                vocabulary.append({
                    'word': entry['bashkir'],
                    'english': entry.get('english', ''),
                    'russian': entry.get('russian', ''),
                    'in_dictionary': True
                })
            else:
                vocabulary.append({
                    'word': word,
                    'english': '',
                    'russian': '',
                    'in_dictionary': False
                })

        return vocabulary

    def highlight_vocabulary(
        self,
        text: str,
        known_words: set,
        dictionary: List[Dict]
    ) -> str:
        """
        Add HTML highlighting to vocabulary in text.

        Args:
            text: Original text
            known_words: Set of words the user has learned
            dictionary: Word dictionary

        Returns:
            HTML-formatted text with highlighting
        """
        dict_words = {w['bashkir'].lower() for w in dictionary}

        def replace_word(match):
            word = match.group(0)
            word_lower = word.lower()

            if word_lower in known_words:
                # Known word - green
                return f'<span class="known-word" style="color: #00AF66;">{word}</span>'
            elif word_lower in dict_words:
                # In dictionary but not learned - blue (clickable)
                return f'<span class="dict-word" style="color: #0066B3; cursor: pointer;" data-word="{word_lower}">{word}</span>'
            else:
                # Unknown word - gray
                return f'<span class="unknown-word" style="color: #888;">{word}</span>'

        # Replace Cyrillic words
        highlighted = re.sub(
            r'\b[а-яәөүғҡңһҙёА-ЯӘӨҮҒҠҢҺҘЁ]+\b',
            replace_word,
            text
        )

        return highlighted

    def add_custom_text(
        self,
        title: str,
        content: str,
        source: str,
        difficulty: DifficultyLevel,
        topics: List[str] = None
    ) -> ReadingText:
        """
        Add a custom reading text.

        Args:
            title: Text title
            content: Text content
            source: Source attribution
            difficulty: Difficulty level
            topics: List of topics

        Returns:
            Created ReadingText object
        """
        # Generate ID
        text_id = f"custom_{hashlib.md5(content.encode()).hexdigest()[:8]}"

        text = ReadingText(
            id=text_id,
            title=title,
            content=content,
            source=source,
            difficulty=difficulty,
            word_count=len(content.split()),
            topics=topics or [],
            vocabulary=[]
        )

        self._texts[text_id] = text
        self._save_to_cache(text)

        return text

    def _save_to_cache(self, text: ReadingText):
        """Save a text to the cache."""
        cache_file = self.cache_dir / f"{text.id}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(text.to_dict(), f, ensure_ascii=False, indent=2)

    def load_from_cache(self):
        """Load cached texts."""
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    text = ReadingText.from_dict(data)
                    self._texts[text.id] = text
            except Exception as e:
                print(f"Error loading cached text {cache_file}: {e}")

    def get_reading_stats(self, completed_texts: List[str]) -> Dict:
        """
        Get reading statistics.

        Args:
            completed_texts: List of completed text IDs

        Returns:
            Statistics dictionary
        """
        total_texts = len(self._texts)
        completed_count = len(completed_texts)

        # Words read
        words_read = sum(
            self._texts[tid].word_count
            for tid in completed_texts
            if tid in self._texts
        )

        # By difficulty
        by_difficulty = {}
        for level in DifficultyLevel:
            level_texts = self.get_texts_by_difficulty(level)
            completed_at_level = [t for t in level_texts if t.id in completed_texts]
            by_difficulty[level.name] = {
                'total': len(level_texts),
                'completed': len(completed_at_level)
            }

        return {
            'total_texts': total_texts,
            'completed_texts': completed_count,
            'completion_rate': completed_count / total_texts if total_texts else 0,
            'words_read': words_read,
            'by_difficulty': by_difficulty
        }


# Singleton instance
_content_scraper: Optional[ContentScraper] = None


def get_content_scraper() -> ContentScraper:
    """Get or create the content scraper singleton."""
    global _content_scraper
    if _content_scraper is None:
        _content_scraper = ContentScraper()
    return _content_scraper
