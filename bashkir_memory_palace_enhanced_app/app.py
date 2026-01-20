"""
🏰 Bashkir Memory Palace: Secrets of Voyaging
==============================================
A language learning app integrating Ibn Arabi's mystical framework,
memory palace techniques, and anthropological pedagogy.

The Four Birds guide your journey:
🦅 Eagle (First Intellect) - Civic knowledge at Ufa
🐦‍⬛ Crow (Universal Body) - Ancestral memory at Shulgan-Tash
🔥🕊️ Anqa (Prime Matter) - Transformation at Yamantau
🕊️ Ringdove (Universal Soul) - Daily life at Beloretsk & Bizhbulyak

Enhanced with retry logic, audio export, and OCM cultural classifications.
"""

import streamlit as st
import json
import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.retry import RetryConfig

# --- Audio Setup with Retry Logic ---
try:
    from gtts import gTTS
    import hashlib
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# --- Translation Setup ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

# --- Speech Recognition Setup (Whisper) ---
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Create audio cache directory
AUDIO_CACHE_DIR = Path(__file__).parent / "audio_cache"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)


def generate_audio_with_retry(text: str, slow: bool = True, language: str = 'ru') -> bytes:
    """
    Generate audio for Bashkir text with retry logic and caching.

    Uses exponential backoff: 2s, 4s, 8s, 16s delays between retries.
    Returns audio bytes or None if generation fails.
    """
    if not AUDIO_AVAILABLE:
        return None

    config = RetryConfig(
        max_retries=4,
        base_delay=2.0,
        exponential_base=2.0,
    )

    # Create a cached filename based on text hash
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    cache_file = AUDIO_CACHE_DIR / f"{text_hash}.mp3"

    # Return cached version if available
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return f.read()

    # Generate with retry logic
    for attempt in range(config.max_retries + 1):
        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(str(cache_file))

            with open(cache_file, 'rb') as f:
                return f.read()

        except Exception as e:
            if attempt >= config.max_retries:
                return None

            delay = config.base_delay * (config.exponential_base ** attempt)
            time.sleep(delay)

    return None


def play_audio(text: str, slow: bool = True, language: str = 'ru'):
    """Generate and play audio for Bashkir text with caching and retry logic."""
    if not AUDIO_AVAILABLE:
        st.warning("🔇 Audio unavailable. Install with: `pip install gTTS`")
        return

    audio_bytes = generate_audio_with_retry(text, slow, language)

    if audio_bytes:
        st.audio(audio_bytes, format='audio/mp3')
    else:
        st.error("🔇 Audio generation failed after multiple attempts.")


def translate_text(text: str, source: str = 'en', target: str = 'ru') -> str:
    """
    Translate text with retry logic.

    Uses exponential backoff: 2s, 4s, 8s, 16s delays between retries.
    """
    if not TRANSLATION_AVAILABLE:
        return text

    config = RetryConfig(
        max_retries=4,
        base_delay=2.0,
        exponential_base=2.0,
    )

    for attempt in range(config.max_retries + 1):
        try:
            translator = GoogleTranslator(source=source, target=target)
            return translator.translate(text)
        except Exception as e:
            if attempt >= config.max_retries:
                return text  # Return original on failure

            delay = config.base_delay * (config.exponential_base ** attempt)
            time.sleep(delay)

    return text


@st.cache_resource
def load_whisper_model():
    """Load Whisper model with caching for speech recognition."""
    if not WHISPER_AVAILABLE:
        return None

    config = RetryConfig(
        max_retries=4,
        base_delay=4.0,
        exponential_base=2.0,
    )

    for attempt in range(config.max_retries + 1):
        try:
            return whisper.load_model("base")
        except Exception as e:
            if attempt >= config.max_retries:
                return None

            delay = config.base_delay * (config.exponential_base ** attempt)
            time.sleep(delay)

    return None


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Whisper."""
    if not WHISPER_AVAILABLE:
        return ""

    model = load_whisper_model()
    if model is None:
        return ""

    try:
        result = model.transcribe(audio_path)
        return result.get('text', '')
    except Exception as e:
        return ""

# Page configuration
st.set_page_config(
    page_title="Bashkir Memory Palace",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading ---
@st.cache_data
def load_words():
    """Load vocabulary data."""
    data_path = Path(__file__).parent / "data" / "words.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def load_loci():
    """Load memory palace locations."""
    data_path = Path(__file__).parent / "data" / "loci.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def load_patterns():
    """Load sentence patterns."""
    data_path = Path(__file__).parent / "data" / "patterns.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def load_ocm_mapping():
    """Load OCM mapping data."""
    data_path = Path(__file__).parent / "data" / "ocm_mapping.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@st.cache_data
def load_ural_batyr_epic():
    """Load the Ural-Batyr epic data - the Golden Light."""
    data_path = Path(__file__).parent / "data" / "ural_batyr_epic.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@st.cache_data
def load_golden_light_data():
    """Load the comprehensive Golden Light data - independence, geography, alphabet, proverbs."""
    data_path = Path(__file__).parent / "data" / "golden_light_data.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# --- Initialize Session State ---
def init_session_state():
    """Initialize session state variables."""
    if 'current_locus' not in st.session_state:
        st.session_state.current_locus = None
    if 'current_station' not in st.session_state:
        st.session_state.current_station = None
    if 'learned_words' not in st.session_state:
        st.session_state.learned_words = set()
    if 'review_queue' not in st.session_state:
        st.session_state.review_queue = []
    if 'saved_sentences' not in st.session_state:
        st.session_state.saved_sentences = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Palace"
    if 'truth_unveiled' not in st.session_state:
        st.session_state.truth_unveiled = False
    if 'srs_data' not in st.session_state:
        st.session_state.srs_data = {}
    if 'builder_sentence' not in st.session_state:
        st.session_state.builder_sentence = []
    if 'epic_chapter' not in st.session_state:
        st.session_state.epic_chapter = 0
    
    # === NEW: Theological Framework Variables ===
    if 'breathing_completed' not in st.session_state:
        st.session_state.breathing_completed = False
    if 'logismoi_journal' not in st.session_state:
        st.session_state.logismoi_journal = []  # Distraction tracking
    if 'sacred_practice_count' not in st.session_state:
        st.session_state.sacred_practice_count = 0
    
    # === NEW: Pedagogical Framework Variables (Kierkegaard) ===
    if 'learning_stage' not in st.session_state:
        st.session_state.learning_stage = "aesthetic"  # aesthetic/ethical/religious
    if 'reflection_journal' not in st.session_state:
        st.session_state.reflection_journal = []
    if 'days_active' not in st.session_state:
        st.session_state.days_active = 0
    if 'first_visit_date' not in st.session_state:
        st.session_state.first_visit_date = datetime.now().isoformat()
    if 'total_reviews_completed' not in st.session_state:
        st.session_state.total_reviews_completed = 0
    
    # === NEW: Epistemological Framework Variables ===
    if 'eye_mode' not in st.session_state:
        st.session_state.eye_mode = "reason"  # senses/reason/contemplation
    if 'inquiry_mode' not in st.session_state:
        st.session_state.inquiry_mode = False  # Dialogical inquiry (Plato)
    
    # === NEW: Milestone Tracking ===
    if 'milestones' not in st.session_state:
        st.session_state.milestones = {
            'first_word': None,
            'first_sentence': None,
            'truth_unveiled_date': None,
            'fifty_words': None,
            'hundred_words': None,
            'two_hundred_words': None,
            'five_hundred_words': None,
            'thirty_day_streak': None
        }
    
    # === NEW: Station depth for choice gates ===
    if 'station_depth' not in st.session_state:
        st.session_state.station_depth = 0

init_session_state()

# --- CSS Styling v3 - Bashkortostan Flag Colors ---
# Flag: Blue (#0066B3), White (#FFFFFF), Green (#00AF66)
# Fixes: Light blue background, visible expanders, readable headers
st.markdown("""
<style>
    /* ===== MAIN BACKGROUND - Light Blue ===== */
    .stApp {
        background-color: #cce5ff !important;
        background: linear-gradient(180deg, #cce5ff 0%, #d9ecff 50%, #e6f2ff 100%) !important;
    }

    /* ===== SIDEBAR STYLING ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0066B3 0%, #004080 100%) !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: white !important;
    }

    /* ===== ALL HEADERS - Green & Readable ===== */
    h1 {
        color: #00AF66 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    h2 {
        color: #00AF66 !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
    }
    h3 {
        color: #00AF66 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    h4 {
        color: #00AF66 !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }
    /* Markdown headers too */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #00AF66 !important;
    }

    /* ===== EXPANDERS - Always Visible ===== */
    .streamlit-expanderHeader {
        background-color: #e6f2ff !important;
        border: 2px solid #0066B3 !important;
        border-radius: 8px !important;
        color: #004d00 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: #d9ecff !important;
        border-color: #00AF66 !important;
    }
    .streamlit-expanderContent {
        background-color: #f0f8ff !important;
        border: 1px solid #0066B3 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    /* Expander icon always visible */
    .streamlit-expanderHeader svg {
        color: #0066B3 !important;
        opacity: 1 !important;
    }

    /* Alternative expander styling for newer Streamlit */
    [data-testid="stExpander"] {
        border: 2px solid #0066B3 !important;
        border-radius: 10px !important;
        background-color: #e6f2ff !important;
    }
    [data-testid="stExpander"]:hover {
        background-color: #d9ecff !important;
        border-color: #00AF66 !important;
    }
    [data-testid="stExpander"] summary {
        color: #004d00 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 12px !important;
    }
    [data-testid="stExpander"] summary:hover {
        background-color: #d9ecff !important;
    }
    [data-testid="stExpander"] svg {
        color: #0066B3 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* ===== POPOVER BUTTONS - Always Visible ===== */
    [data-testid="stPopover"] > button,
    .stPopover > button {
        background-color: #e6f2ff !important;
        border: 2px solid #0066B3 !important;
        color: #004d00 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stPopover"] > button:hover,
    .stPopover > button:hover {
        background-color: #d9ecff !important;
        border-color: #00AF66 !important;
    }

    /* ===== BIRD CARDS ===== */
    .bird-card {
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid;
        color: #004d00;
    }
    .eagle-card { background: linear-gradient(135deg, #cce5ff 0%, #e6f2ff 100%); border-color: #0066B3; }
    .crow-card { background: linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%); border-color: #333333; }
    .anqa-card { background: linear-gradient(135deg, #ffe6e6 0%, #fff0f0 100%); border-color: #cc3333; }
    .ringdove-card { background: linear-gradient(135deg, #e6ffe6 0%, #f0fff0 100%); border-color: #00AF66; }

    /* ===== WORD CARDS ===== */
    .word-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 102, 179, 0.15);
        margin: 10px 0;
        border: 2px solid #0066B3;
    }

    /* Bashkir text - GREEN from flag */
    .bashkir-text {
        font-size: 1.8em;
        font-weight: bold;
        color: #00AF66 !important;
        display: block;
        margin-bottom: 8px;
    }

    /* IPA text - blue */
    .ipa-text {
        color: #0066B3;
        font-size: 1em;
        font-style: italic;
    }

    /* English translation - dark green */
    .english-text {
        color: #004d00;
        font-size: 1.2em;
        font-weight: bold;
        margin: 8px 0;
    }

    /* Russian - muted */
    .russian-text {
        color: #666666;
        font-size: 0.95em;
    }

    /* ===== MEDITATION BOXES ===== */
    .meditation-box {
        background: linear-gradient(135deg, #e6fff0 0%, #ccffe6 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00AF66;
        font-style: italic;
        margin: 15px 0;
        color: #004d00;
    }

    /* ===== STATS BOXES ===== */
    .stat-box {
        background: linear-gradient(135deg, #e6f2ff 0%, #cce5ff 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #0066B3;
        color: #004d00;
    }

    /* ===== MNEMONIC BOXES ===== */
    .mnemonic-text {
        background: linear-gradient(135deg, #fffff5 0%, #ffffd0 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00AF66;
        color: #004d00;
        line-height: 1.6;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background-color: #00AF66 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #008f55 !important;
        color: white !important;
    }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div {
        background-color: #00AF66 !important;
    }

    /* ===== GENERAL TEXT ===== */
    .stMarkdown, .stMarkdown p, .stText {
        color: #004d00;
    }

    /* ===== SELECTBOX & DROPDOWNS - Dark Text ===== */
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid #0066B3 !important;
        border-radius: 8px !important;
    }
    .stSelectbox label {
        color: #004d00 !important;
        font-weight: 600 !important;
    }
    /* Dropdown text - DARK */
    .stSelectbox [data-baseweb="select"] > div {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    .stSelectbox span {
        color: #1a1a1a !important;
    }
    /* Dropdown options */
    [data-baseweb="menu"] {
        background-color: white !important;
    }
    [data-baseweb="menu"] li {
        color: #1a1a1a !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #e6f2ff !important;
    }
    /* Selected option text */
    [data-baseweb="select"] [data-testid="stMarkdownContainer"] {
        color: #1a1a1a !important;
    }
    /* All input text dark */
    input, textarea, [contenteditable] {
        color: #1a1a1a !important;
    }
    /* Radio buttons */
    .stRadio label {
        color: #004d00 !important;
    }
    .stRadio label span {
        color: #1a1a1a !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e6f2ff !important;
        border-radius: 8px 8px 0 0 !important;
        color: #004d00 !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00AF66 !important;
        color: white !important;
    }

    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        color: #00AF66 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #004d00 !important;
    }

    /* ===== CAPTIONS ===== */
    .stCaption, small {
        color: #0066B3 !important;
    }

    /* ===== INPUT FIELDS - Lighter background, better contrast ===== */
    .stTextInput input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-size: 1.2em !important;
        padding: 12px 15px !important;
        border: 2px solid #0066B3 !important;
        border-radius: 8px !important;
    }
    .stTextInput input::placeholder {
        color: #666666 !important;
        font-size: 1.1em !important;
    }
    .stTextInput input:focus {
        border-color: #00AF66 !important;
        box-shadow: 0 0 5px rgba(0, 175, 102, 0.3) !important;
    }
    .stTextInput > label {
        color: #004d00 !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
    }
    /* SelectBox styling */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-size: 1.1em !important;
    }

    /* ===== RADIO BUTTONS - Green text for quizzes ===== */
    .stRadio > label {
        color: #00AF66 !important;
        font-weight: 600 !important;
    }
    .stRadio > div[role="radiogroup"] label {
        color: #004d00 !important;
        font-size: 1.1em !important;
    }
    .stRadio > div[role="radiogroup"] label:hover {
        color: #00AF66 !important;
    }
    /* Radio button option text */
    div[data-testid="stRadio"] label span {
        color: #004d00 !important;
    }
    div[data-testid="stRadio"] label:hover span {
        color: #00AF66 !important;
    }

    /* ===== STREAMLIT TABS - Better spacing and centering ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px !important;
        justify-content: center !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 15px 25px !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        color: #004d00 !important;
        border-radius: 10px 10px 0 0 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00AF66 !important;
        background-color: rgba(0, 175, 102, 0.1) !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00AF66 !important;
        border-bottom: 3px solid #00AF66 !important;
    }

    /* ===== NAVIGATION BUTTONS - Centered with spacing ===== */
    .nav-button-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 25px 0;
    }
    .nav-button-center {
        display: flex;
        justify-content: center;
        margin: 20px auto;
    }

    /* ===== MOBILE RESPONSIVENESS ===== */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.25rem !important; }
        .word-card { padding: 12px !important; }
        .bashkir-text { font-size: 1.5em !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("🏰 Memory Palace")

# Sidebar toggle hint for mobile users
st.sidebar.caption("📱 *Tap âœ• to collapse sidebar*")
st.sidebar.markdown("---")

# Navigation - Radio buttons for individual tabs
# Tab order: Palace, Golden Light, Independence, Four Birds, Ural-Batyr Epic, Geography, Alphabet...
pages = [
    "🗺️ Palace",
    "✨ Golden Light",
    "⚖️ Independence",
    "📚 Four Birds",
    "⚔️ Ural-Batyr Epic",
    "🗺️ Geography",
    "📺 Media",
    "🔤 Alphabet",
    "âœ️ Sentence Builder",
    "🔊 Audio Dictionary",
    "🔄 Review",
    "🕸️ BashkortNet Explorer",
    "📖 Cultural Context",
    "🌟 Truth Unveiled",
    "🧘 Sacred Practice",
    "📈 Your Journey",
    "📚 The Eleven Pillars",
    "⚙️ Settings"
]

selected_page = st.sidebar.radio("Navigate", pages, label_visibility="collapsed")

# Progress indicator
words_data = load_words()
learned_count = len(st.session_state.learned_words)
total_count = len(words_data)
progress = learned_count / total_count if total_count > 0 else 0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Progress")
st.sidebar.progress(progress)
st.sidebar.markdown(f"**{learned_count}** / {total_count} words learned")

# Quick stats
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Today")
st.sidebar.metric("Words to Review", len(st.session_state.review_queue))
st.sidebar.metric("Sentences Created", len(st.session_state.saved_sentences))

# === PAGE: PALACE ===
if "Palace" in selected_page:
    st.title("🏰 The Memory Palace of Bashkortostan")
    st.markdown("*Walk through the stations. Let the Four Birds guide your learning.*")

    # === NEW: Centering Practice Before Entry (Theological Framework) ===
    with st.expander("🌬️ Centering Practice (Optional)", expanded=False):
        st.markdown("""
        *Before entering the Palace, center yourself.*
        
        > "Draw your mind down from your head into your heart and hold it there."
        > — Saint Gregory of Sinai
        
        > "The journey made within yourself leads to yourself."
        > — Ibn Arabi, Secrets of Voyaging
        """)
        
        if st.button("Begin 30-second centering practice", key="palace_breathing"):
            progress_bar = st.progress(0)
            status = st.empty()
            
            phases = [
                ("🌬️ Breathe in... draw your attention inward", 5),
                ("💫 Hold... feel the stillness", 3),
                ("🌊 Breathe out... release distractions", 5),
                ("🏔️ Rest... you are ready to enter", 2)
            ]
            
            total_time = sum(p[1] for p in phases) * 2  # 2 cycles
            elapsed = 0
            
            for cycle in range(2):
                for phase_name, duration in phases:
                    status.markdown(f"**{phase_name}**")
                    for i in range(duration):
                        time.sleep(1)
                        elapsed += 1
                        progress_bar.progress(elapsed / total_time)
            
            st.session_state.breathing_completed = True
            st.success("✨ You are centered. Enter the Palace with presence.")
    
    # === NEW: Three Eyes View Toggle (Epistemological Framework) ===
    st.markdown("---")
    eye_mode = st.radio(
        "👁️ View Mode (The Three Eyes of Knowledge):",
        ["🔴 Eye of Senses", "🟡 Eye of Reason", "🟢 Eye of Contemplation"],
        horizontal=True,
        help="""
        🔴 Senses: Audio, pronunciation, how the word feels to speak
        🟡 Reason: Grammar, etymology, linguistic structure  
        🟢 Contemplation: Cultural meaning, spiritual significance
        """,
        key="palace_eye_mode"
    )
    st.session_state.eye_mode = eye_mode.split()[0]  # Store just the emoji indicator
    
    st.markdown("---")


    loci_data = load_loci()

    # Locus selection
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Choose Your Destination")

        locus_options = list(loci_data.keys())
        locus_display = {
            "Ufa": "🦅 Ó¨Ñ„Ó© â€“ Eagle's Perch (Civic)",
            "Shulgan-Tash": "🐦‍⬛ Ð¨Ò¯Ð»Ð³Ó™Ð½Ñ‚Ð°Ñˆ â€“ Crow's Archive (Ancestry)",
            "Yamantau": "🔥🕊️ Ð¯Ð¼Ð°Ð½Ñ‚Ð°Ñƒ â€“ Anqa's Ascent (Mystery)",
            "Beloretsk": "🕊️ Ð‘ÐµÐ»Ð¾Ñ€ÐµÑ‚ â€“ Ringdove's Forge (Labor)",
            "Bizhbulyak": "🕊️ Ð‘Ð¸Ð¶Ð±ÑƒÐ»ÑÐº â€“ Ringdove's Hearth (Home)"
        }

        selected_locus = st.selectbox(
            "Select Location",
            locus_options,
            format_func=lambda x: locus_display.get(x, x)
        )

    with col2:
        if selected_locus:
            locus = loci_data[selected_locus]
            bird_symbol = locus.get('symbol', '🐦')
            bird_name = locus.get('bird', 'Bird')
            # Handle nested description structure
            description = locus.get('description', {})
            if isinstance(description, dict):
                short_desc = description.get('short', '')
            else:
                short_desc = str(description)
            st.markdown(f"### {bird_symbol} {bird_name}")
            st.markdown(f"*{short_desc}*")

    st.markdown("---")

    # Display selected locus
    if selected_locus:
        locus = loci_data[selected_locus]

        # Handle nested description structure for Ibn Arabi connection
        description = locus.get('description', {})
        if isinstance(description, dict):
            ibn_arabi_connection = description.get('ibn_arabi_connection', '')
        else:
            ibn_arabi_connection = ''


        # Handle nested description structure for Ibn Arabi connection
        description = locus.get('description', {})
        if isinstance(description, dict):
            ibn_arabi_connection = description.get('ibn_arabi_connection', '')
        else:
            ibn_arabi_connection = ''

        # Ibn Arabi connection
        if ibn_arabi_connection:
            with st.expander("🌟 Ibn Arabi's Teaching", expanded=False):
                st.markdown(f"""
                <div class="meditation-box">
                {ibn_arabi_connection}
                </div>
                """, unsafe_allow_html=True)

        # Station walkthrough
        st.markdown("### 🚶 Station Walkthrough")

        for station in locus.get('stations', []):
            station_name = station.get('display_name', station.get('name', 'Station'))
            station_words = station.get('words', [])

            with st.expander(f"📍 Station {station.get('number', '?')}: {station_name}", expanded=True):
                # Opening meditation
                opening_med = station.get('opening_meditation', '')
                if opening_med:
                    st.markdown(f"""
                    <div class="meditation-box">
                    <strong>🕯️ Opening Meditation:</strong><br>
                    {opening_med}
                    </div>
                    """, unsafe_allow_html=True)

                # Words in this station
                st.markdown("#### Words at this Station:")

                # Create word cards - FIXED: properly filter words by station
                words_at_station = [w for w in words_data if w['bashkir'] in station_words]

                if words_at_station:
                    cols = st.columns(min(3, len(words_at_station)))
                    for idx, word in enumerate(words_at_station):
                        with cols[idx % 3]:
                            is_learned = word['bashkir'] in st.session_state.learned_words

                            # Using proper HTML structure with CSS classes
                            card_html = f'''
                            <div class="word-card">
                                <span class="bashkir-text">{word['bashkir']} {"âœ…" if is_learned else ""}</span>
                                <span class="ipa-text">{word.get('ipa', '')}</span>
                                <div class="english-text">{word['english']}</div>
                                <span class="russian-text">🇷🇺 {word.get('russian', '')}</span>
                            </div>
                            '''
                            st.markdown(card_html, unsafe_allow_html=True)

                            # Audio and Mnemonic buttons in a row
                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("🔊 Hear", key=f"audio_{station_name}_{word['bashkir']}_{idx}"):
                                    play_audio(word['bashkir'])

                            with btn_col2:
                                # Mnemonic
                                mnemonic = word.get('memory_palace', {}).get('mnemonic', '')
                                if mnemonic:
                                    with st.popover("💡 Hint"):
                                        st.markdown(f"""
                                        <div class="mnemonic-text">
                                        {mnemonic}
                                        </div>
                                        """, unsafe_allow_html=True)

                            # Learn button
                            if not is_learned:
                                if st.button(f"Learn '{word['bashkir']}'", key=f"learn_{station_name}_{word['bashkir']}_{idx}"):
                                    st.session_state.learned_words.add(word['bashkir'])
                                    st.session_state.review_queue.append(word['bashkir'])
                                    st.rerun()
                else:
                    st.info("No vocabulary words assigned to this station yet.")

                # Closing meditation
                closing_med = station.get('closing_meditation', '')
                if closing_med:
                    st.markdown(f"""
                    <div class="meditation-box">
                    <strong>🕯️ Closing Meditation:</strong><br>
                    {closing_med}
                    </div>
                    """, unsafe_allow_html=True)

# === PAGE: GOLDEN LIGHT (ÐÐ»Ñ‚Ñ‹Ð½ Ð¯Ò¡Ñ‚Ñ‹) ===
elif "Golden Light" in selected_page:
    # Load data
    golden_data = load_golden_light_data()
    gl_info = golden_data.get('golden_light', {})
    gl_title = gl_info.get('title', {})
    legacy_proverb = gl_info.get('legacy_proverb', {})
    stations = gl_info.get('memory_palace_stations', [])

    st.title("✨ ÐÐ»Ñ‚Ñ‹Ð½ Ð¯Ò¡Ñ‚Ñ‹ â€” Golden Light")
    st.markdown(f"*{gl_title.get('subtitle_bashkir', '')}*")
    st.markdown(f"*{gl_title.get('subtitle_english', '')}*")

    # Central bilingual motto - THE KEY QUOTE
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #d4af37 0%, #f4e4bc 50%, #d4af37 100%);
                padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;
                border: 3px solid #8B7355; box-shadow: 0 8px 32px rgba(212,175,55,0.3);">
        <h2 style="color: #2d1f10; margin-bottom: 15px; font-size: 1.8em;">🌟 The Legacy Proverb 🌟</h2>
        <p style="font-size: 1.5em; color: #2d1f10; font-weight: bold; margin: 15px 0;">
            "{legacy_proverb.get('bashkir', '')}"
        </p>
        <p style="font-size: 1.2em; color: #4a3728; font-style: italic; margin: 15px 0;">
            "{legacy_proverb.get('english', '')}"
        </p>
        <p style="font-size: 0.95em; color: #5a4738;">
            🇷🇺 {legacy_proverb.get('russian', '')}
        </p>
        <p style="font-size: 0.9em; color: #6a5748; margin-top: 10px;">
            [{legacy_proverb.get('phonetic', '')}]
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    *This proverb anchors the Ural-Batyr mythology. When the hero Ural poured the waters of life
    for all rather than drinking them himself, he demonstrated this truth: we live on through what we give.
    The Sesen storytellers have passed this wisdom through generations.*
    """)

    st.markdown("---")

    # Memory Palace Stations - Golden Light Version
    st.markdown("### 🏰 The Memory Palace of the Ural-Batyr Epic")
    st.markdown("*Walk through the 10 stations of the hero's journey. Each station holds vocabulary and wisdom.*")

    # Station navigation buttons
    if 'gl_station' not in st.session_state:
        st.session_state.gl_station = 0

    # Display station buttons in a row
    cols = st.columns(10)
    for idx, station in enumerate(stations):
        with cols[idx]:
            btn_style = "primary" if idx == st.session_state.gl_station else "secondary"
            if st.button(station.get('icon', '📍'), key=f"gl_station_{idx}", help=station.get('title', '')):
                st.session_state.gl_station = idx

    # Current station display
    if stations:
        current_station = stations[st.session_state.gl_station]

        # Station color mapping
        color_map = {
            'emerald': '#00AF66', 'sky': '#0066B3', 'blue': '#0044AA',
            'amber': '#d4af37', 'red': '#cc3333', 'purple': '#8B5CF6',
            'orange': '#F97316', 'cyan': '#06B6D4', 'slate': '#64748B'
        }
        station_color = color_map.get(current_station.get('color', 'emerald'), '#00AF66')

        st.markdown(f"""
        <div class="word-card" style="border-left: 5px solid {station_color}; background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 2em;">{current_station.get('icon', '📍')}</span>
                <span style="background: {station_color}; color: white; padding: 5px 15px; border-radius: 20px;">
                    Station {current_station.get('id', '?')}
                </span>
            </div>
            <h2 style="color: {station_color}; margin: 10px 0;">{current_station.get('title', '')}</h2>
            <p style="font-size: 1.2em; font-style: italic; color: #00AF66;">
                {current_station.get('bashkir', '')}
            </p>
            <p style="color: #333; margin: 10px 0;">{current_station.get('summary', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Memory techniques
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="stat-box" style="text-align: left;">
                <h4>🔑 Memory Peg</h4>
                <p style="font-size: 1.1em; font-family: monospace; color: #0066B3;">
                    {current_station.get('memory_peg', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="mnemonic-text">
                <h4>🎨 Visualization</h4>
                <p>{current_station.get('memory_image', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        # Vocabulary at this station
        st.markdown("### 📚 Station Vocabulary")
        vocab = current_station.get('vocab', [])

        if vocab:
            vocab_cols = st.columns(len(vocab))
            for idx, word in enumerate(vocab):
                with vocab_cols[idx]:
                    st.markdown(f"""
                    <div class="word-card" style="text-align: center;">
                        <span class="bashkir-text">{word.get('bashkir', '')}</span>
                        <span class="ipa-text">[{word.get('phonetic', '')}]</span>
                        <div class="english-text">{word.get('english', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🔊", key=f"gl_audio_{current_station['id']}_{idx}"):
                        play_audio(word.get('bashkir', ''), slow=True)

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.gl_station > 0:
            if st.button("â† Previous Station"):
                st.session_state.gl_station -= 1
                st.rerun()
    with col3:
        if st.session_state.gl_station < len(stations) - 1:
            if st.button("Next Station â†’"):
                st.session_state.gl_station += 1
                st.rerun()

# === PAGE: INDEPENDENCE (12 Reasons) ===
elif "Independence" in selected_page:
    golden_data = load_golden_light_data()
    independence = golden_data.get('independence', {})
    title_info = independence.get('title', {})
    reasons = independence.get('reasons', [])

    st.title("⚖️ Ð‘Ó™Ð¹Ò»ÐµÒ™Ð»ÐµÐº â€” Independence")
    st.markdown(f"### {title_info.get('subtitle', '')}")
    st.markdown(f"*By {independence.get('author', '')} â€” {independence.get('organization', '')}*")

    # Introduction with scroll/legal theme
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f5f5dc 0%, #ede6cc 100%);
                padding: 25px; border-radius: 15px; margin: 20px 0;
                border: 2px solid #8B7355; box-shadow: 0 4px 15px rgba(139,115,85,0.2);">
        <div style="text-align: center;">
            <span style="font-size: 3em;">📜⚖️📜</span>
            <h3 style="color: #4a3728; margin: 15px 0;">A Declaration of Rights</h3>
            <p style="color: #5a4738; font-style: italic;">
                "International law supports self-determination for peoples under colonial rule."
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Display the 12 Reasons in a grid layout
    st.markdown("### The Twelve Reasons")

    # Display reasons in a 2-column grid
    for i in range(0, len(reasons), 2):
        col1, col2 = st.columns(2)

        with col1:
            if i < len(reasons):
                reason = reasons[i]
                st.markdown(f"""
                <div class="word-card" style="border-left: 5px solid #8B7355; min-height: 180px;">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                        <span style="font-size: 2em;">{reason.get('icon', '📜')}</span>
                        <div>
                            <span style="background: #8B7355; color: white; padding: 2px 10px; border-radius: 10px; font-size: 0.8em;">
                                Reason {reason.get('id', '')}
                            </span>
                            <h4 style="color: #00AF66; margin: 5px 0;">{reason.get('title', '')}</h4>
                        </div>
                    </div>
                    <p style="color: #333; font-size: 0.95em;">{reason.get('description', '')}</p>
                    <p style="color: #0066B3; font-style: italic; margin-top: 10px;">
                        🏷️ {reason.get('bashkir_term', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            if i + 1 < len(reasons):
                reason = reasons[i + 1]
                st.markdown(f"""
                <div class="word-card" style="border-left: 5px solid #8B7355; min-height: 180px;">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                        <span style="font-size: 2em;">{reason.get('icon', '📜')}</span>
                        <div>
                            <span style="background: #8B7355; color: white; padding: 2px 10px; border-radius: 10px; font-size: 0.8em;">
                                Reason {reason.get('id', '')}
                            </span>
                            <h4 style="color: #00AF66; margin: 5px 0;">{reason.get('title', '')}</h4>
                        </div>
                    </div>
                    <p style="color: #333; font-size: 0.95em;">{reason.get('description', '')}</p>
                    <p style="color: #0066B3; font-style: italic; margin-top: 10px;">
                        🏷️ {reason.get('bashkir_term', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # Closing statement
    st.markdown("---")
    st.markdown(f"""
    <div class="meditation-box" style="text-align: center; border: 2px solid #8B7355;">
        <p style="font-size: 1.2em;">📜 ⚖️ 📜</p>
        <p style="font-size: 1.1em; color: #004d00;">
            <strong>"Ð¥Ð°Ð»Ñ‹Ò¡ ÐºÓ©ÑÓ© â€” Ñ‚Ð°Ñˆ Ñ‚Ð¸ÑˆÓ™"</strong><br>
            <em>The people's strength pierces stone.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

# === PAGE: FOUR BIRDS ===
elif "Four Birds" in selected_page:
    st.title("📚 The Four Birds of Ibn Arabi")
    st.markdown("*Understanding the cosmological framework of your learning journey.*")

    birds = [
        {
            "name": "Eagle",
            "arabic": "Ø§Ù„Ø¹Ù‚Ù„ Ø§Ù„Ø£ÙˆÙ„",
            "english": "First Intellect",
            "symbol": "🦅",
            "color": "eagle",
            "locus": "Ufa",
            "domain": "Civic & Legal Knowledge",
            "description": """The Eagle represents the First Intellect (al-'Aql al-Awwal) â€”
            the primordial light of knowledge from which all understanding flows.
            At Ufa, we encounter constitutional knowledge, legal rights, and civic identity.
            The Eagle sees the whole landscape from above; it knows the law that governs.""",
            "vocabulary": ["Ð‘Ð°ÑˆÒ¡Ð¾Ñ€Ñ‚Ð¾ÑÑ‚Ð°Ð½", "Ñ…Ð°Ð»Ñ‹Ò¡", "Ð¸Ñ€ÐºÐµÐ½Ð»ÐµÐº", "Ñ‚ÐµÐ»", "ÐºÐ¾Ð½ÑÑ‚Ð¸Ñ‚ÑƒÑ†Ð¸Ñ"]
        },
        {
            "name": "Crow",
            "arabic": "Ø§Ù„Ø¬Ø³Ù… Ø§Ù„ÙƒÙ„ÙŠ",
            "english": "Universal Body",
            "symbol": "🐦‍⬛",
            "color": "crow",
            "locus": "Shulgan-Tash",
            "domain": "Ancestral Memory & Nature",
            "description": """The Crow represents Universal Body (al-Jism al-Kulli) â€”
            matter infused with spirit, darkness containing light. In the cave's depths,
            we find manifestation: the physical traces of spiritual vision painted on stone.
            The Crow guards what was; it remembers what others forget.""",
            "vocabulary": ["Ò¡Ð¾ÑÑˆ", "Ð°Ð¹", "Ñ‚Ð°Ñˆ", "Ò»Ñ‹Ñƒ", "Ð¹Ñ‹Ð»Ò“Ð°", "ÐÒ“Ð¸Ò™ÐµÐ»"]
        },
        {
            "name": "Anqa",
            "arabic": "Ø§Ù„Ù‡ÙŠÙˆÙ„Ù‰",
            "english": "Prime Matter",
            "symbol": "🔥🕊️",
            "color": "anqa",
            "locus": "Yamantau",
            "domain": "Potential & Transformation",
            "description": """The Anqa represents Prime Matter (al-HayÅ«lÄ) â€”
            pure potentiality, the 'name without a body.' Like the mythical phoenix,
            it exists in the realm of possibility. At Yamantau ('Bad Mountain'),
            danger and transformation intertwine. From difficulty comes growth.""",
            "vocabulary": ["Ñ‚Ð°Ñƒ", "ÐµÐ»", "ÑƒÑ€Ð¼Ð°Ð½", "Ò¡ÑƒÑ€Ò¡Ñ‹Ð½Ñ‹Ñ", "ÐºÒ¯Ð»", "ÑÐ¼Ð°Ð½", "Ò™ÑƒÑ€"]
        },
        {
            "name": "Ringdove",
            "arabic": "Ø§Ù„Ù†ÙØ³ Ø§Ù„ÙƒÙ„ÙŠØ©",
            "english": "Universal Soul",
            "symbol": "🕊️",
            "color": "ringdove",
            "locus": "Beloretsk & Bizhbulyak",
            "domain": "Daily Life & Community",
            "description": """The Ringdove represents Universal Soul (al-Nafs al-Kulliyya) â€”
            the receptive, nurturing principle that brings potential into form.
            At Beloretsk, raw ore becomes steel through patient work.
            At Bizhbulyak, family, food, and music create the texture of daily life.""",
            "vocabulary": ["ÑÑˆ", "Ð±Ð¾Ð»Ð°Ñ‚", "Ð¾Ò«Ñ‚Ð°", "Ð±Ð°Ð»", "Ð°Ñ‚Ð°", "Ó™ÑÓ™", "Ó©Ð¹", "Ò¡ÑƒÑ€Ð°Ð¹", "Ð°Ñ‚"]
        }
    ]

    for bird in birds:
        st.markdown(f"""
        <div class="bird-card {bird['color']}-card">
            <h3>{bird['symbol']} {bird['name']} â€” {bird['english']}</h3>
            <p><em>Arabic: {bird['arabic']}</em></p>
            <p><strong>Domain:</strong> {bird['domain']}</p>
            <p><strong>Location:</strong> {bird['locus']}</p>
            <p>{bird['description']}</p>
            <p><strong>Key Vocabulary:</strong> {', '.join(bird['vocabulary'])}</p>
        </div>
        """, unsafe_allow_html=True)

    # Quiz section
    st.markdown("---")
    st.markdown("### 🎯 Test Your Understanding")

    quiz_questions = [
        {
            "question": "Which bird represents civic knowledge and legal rights?",
            "options": ["Crow", "Eagle", "Anqa", "Ringdove"],
            "correct": "Eagle"
        },
        {
            "question": "At which location would you find the Crow?",
            "options": ["Ufa", "Shulgan-Tash", "Yamantau", "Beloretsk"],
            "correct": "Shulgan-Tash"
        },
        {
            "question": "Which bird represents transformation and potential?",
            "options": ["Eagle", "Crow", "Anqa", "Ringdove"],
            "correct": "Anqa"
        }
    ]

    for i, q in enumerate(quiz_questions):
        answer = st.radio(q["question"], q["options"], key=f"quiz_{i}")
        if st.button("Check", key=f"check_{i}"):
            if answer == q["correct"]:
                st.success("âœ… Correct!")
            else:
                st.error(f"âŒ The correct answer is: {q['correct']}")

    # === NEW: Kierkegaard's Stages Parallel (Theological-Pedagogical Integration) ===
    st.markdown("---")
    st.markdown("### 🔄 Parallel Frameworks: Ibn Arabi & Kierkegaard")
    
    st.markdown("""
    <div class="meditation-box">
        <em>"The question is, under what categories one wants to contemplate 
        the entire world and would oneself live."</em>
        <br>— Kierkegaard, Either/Or
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Ibn Arabi's Four Birds")
        st.markdown("""
        1. 🦅 **Eagle** — First Intellect (Knowledge)
        2. 🐦‍⬛ **Crow** — Universal Body (Embodiment)
        3. 🔥🕊️ **Anqa** — Prime Matter (Transformation)
        4. 🕊️ **Ringdove** — Universal Soul (Integration)
        """)
    
    with col2:
        st.markdown("#### Kierkegaard's Three Stages")
        st.markdown("""
        1. 🔵 **Aesthetic** — Immediacy, sensation, curiosity
        2. 🟡 **Ethical** — Commitment, duty, daily practice
        3. 🟣 **Religious** — Faith, the leap, transformation
        
        *"The act of choosing is a literal and strict expression of the ethical."*
        """)
    
    st.markdown("### The Integration for Language Learning")
    
    st.markdown("""
    | Bird | Kierkegaard Stage | Learning Mode | Your Task |
    |------|-------------------|---------------|-----------|
    | 🦅 Eagle | Aesthetic → Ethical | Intellectual curiosity | Understand the system |
    | 🐦‍⬛ Crow | Ethical | Embodied practice | Commit to daily review |
    | 🔥🕊️ Anqa | Ethical → Religious | Transformation | Face the trials |
    | 🕊️ Ringdove | Religious | Union with language | Become a Bashkir speaker |
    """)
    
    st.markdown("""
    <div class="meditation-box" style="border-color: #cc3333;">
        <h4>🔇 The Limit of Language (Wittgenstein)</h4>
        <p><em>"There are indeed, things that are inexpressible. 
        They show themselves. That is the mystical."</em> — Tractatus 6.522</p>
        
        <p>The Anqa's transformation cannot be fully described. 
        It can only be <strong>undergone</strong>. 
        No words in this app will make you a Bashkir speaker. 
        Only practice, commitment, and the leap.</p>
        
        <p style="text-align: center; font-size: 1.5em;">🔥🕊️</p>
    </div>
    """, unsafe_allow_html=True)


# === PAGE: URAL-BATYR EPIC ===
elif "Ural-Batyr" in selected_page:
    st.title("⚔️ Ð£Ñ€Ð°Ð»-Ð‘Ð°Ñ‚Ñ‹Ñ€ / Ural-Batyr")
    st.markdown("*The foundational myth of the Bashkir people â€” 4,576 lines of heroic legend*")

    # Load epic data
    epic_data = load_ural_batyr_epic()
    chapters = epic_data.get('chapters', [])
    legacy_proverb = epic_data.get('legacy_proverb', {})

    # Legacy proverb banner
    st.markdown(f"""
    <div class="meditation-box" style="text-align: center; border-left: none; border: 3px solid #d4af37;">
        <p style="font-size: 1.3em; margin-bottom: 10px;">✨ <strong>{legacy_proverb.get('bashkir', '')}</strong></p>
        <p style="font-size: 1.1em; color: #004d00;">{legacy_proverb.get('english', '')}</p>
        <p style="font-size: 0.9em; color: #666;">[{legacy_proverb.get('phonetic', '')}]</p>
    </div>
    """, unsafe_allow_html=True)

    # Chapter navigation
    st.markdown("### 📖 The Ten Chapters")
    chapter_cols = st.columns(10)
    for idx, ch in enumerate(chapters):
        with chapter_cols[idx]:
            bird_colors = {'Eagle': '#0066B3', 'Crow': '#333333', 'Anqa': '#cc3333', 'Ringdove': '#00AF66'}
            color = bird_colors.get(ch.get('bird', 'Ringdove'), '#00AF66')
            if st.button(f"{ch.get('icon', '📖')}", key=f"ch_{idx}", help=ch.get('title', '')):
                st.session_state.epic_chapter = idx

    # Current chapter display
    if chapters:
        current_ch = chapters[st.session_state.epic_chapter]

        # Chapter header
        bird_colors = {'Eagle': 'eagle', 'Crow': 'crow', 'Anqa': 'anqa', 'Ringdove': 'ringdove'}
        card_class = bird_colors.get(current_ch.get('bird', 'Ringdove'), 'ringdove')

        st.markdown(f"""
        <div class="bird-card {card_class}-card">
            <h2>{current_ch.get('icon', '')} Chapter {current_ch.get('id', '')}: {current_ch.get('title', '')}</h2>
            <p style="font-size: 1.2em;"><em>{current_ch.get('bashkir', '')}</em></p>
            <p><strong>Bird Guide:</strong> {current_ch.get('bird', '')} | <strong>Theme:</strong> {current_ch.get('summary', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Create tabs for chapter content
        tab1, tab2, tab3, tab4 = st.tabs(["📜 Story", "🧠 Memory Palace", "📚 Vocabulary", "🌟 Unveiling"])

        with tab1:
            st.markdown("### The Tale")
            # Split text into paragraphs
            story_text = current_ch.get('text', '')
            paragraphs = story_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    st.markdown(f"_{para.strip()}_")
                    st.markdown("")

        with tab2:
            st.markdown("### 🧠 Method of Loci â€” Memory Palace Technique")
            memory = current_ch.get('memory_palace', {})

            st.markdown(f"""
            <div class="stat-box" style="text-align: left;">
                <h4>🔑 Memory Peg</h4>
                <p style="font-size: 1.3em; font-family: monospace; color: #0066B3;">{memory.get('peg', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="mnemonic-text">
                <h4>🎨 Visualization</h4>
                <p>{memory.get('image', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.info(f"**Technique:** {memory.get('technique', '')}")

        with tab3:
            st.markdown("### 📚 Chapter Vocabulary")
            vocab = current_ch.get('vocabulary', [])
            if vocab:
                vocab_cols = st.columns(len(vocab))
                for idx, word in enumerate(vocab):
                    with vocab_cols[idx]:
                        st.markdown(f"""
                        <div class="word-card" style="text-align: center;">
                            <span class="bashkir-text">{word.get('bashkir', '')}</span>
                            <span class="ipa-text">[{word.get('phonetic', '')}]</span>
                            <div class="english-text">{word.get('english', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🔊 Hear", key=f"epic_audio_{current_ch['id']}_{idx}"):
                            play_audio(word.get('bashkir', ''), slow=True)

        with tab4:
            st.markdown("### 🌟 The Unveiling")
            unveiling = current_ch.get('unveiling', '')
            st.markdown(f"""
            <div class="meditation-box">
                <p style="font-size: 1.1em; line-height: 1.8;">{unveiling}</p>
            </div>
            """, unsafe_allow_html=True)

            # Connection to the user's twin mythology
            if current_ch.get('id') == 1:
                st.markdown("""
                **The Duality of Twins:** Like Ural and Shulgen, twins carry the potential for both paths.
                One may seek the light, another may guard the depths. Both are necessaryâ€”the hero who
                sacrifices and the guardian who preserves memory in darkness.
                """)

    # Navigation buttons - centered with better spacing
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    with nav_col1:
        if st.session_state.epic_chapter > 0:
            if st.button("â† Previous Chapter", key="prev_chapter", use_container_width=True):
                st.session_state.epic_chapter -= 1
                st.rerun()
    with nav_col2:
        # Center indicator
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <span style="color: #00AF66; font-weight: bold; font-size: 1.2em;">
                Chapter {st.session_state.epic_chapter + 1} of {len(chapters)}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with nav_col3:
        if st.session_state.epic_chapter < len(chapters) - 1:
            if st.button("Next Chapter â†’", key="next_chapter", use_container_width=True):
                st.session_state.epic_chapter += 1
                st.rerun()

# === PAGE: GEOGRAPHY ===
elif "Geography" in selected_page:
    golden_data = load_golden_light_data()
    geography = golden_data.get('geography', {})
    geo_title = geography.get('title', {})
    overview = geography.get('overview', {})
    cities = geography.get('cities', [])
    landmarks = geography.get('landmarks', [])
    facts = geography.get('facts', [])
    map_bounds = geography.get('map_bounds', {})

    st.title("🗺️ Ð“ÐµÐ¾Ð³Ñ€Ð°Ñ„Ð¸Ó™ â€” Geography of Bashkortostan")
    st.markdown(f"*{geo_title.get('bashkir', '')}*")

    # Overview stats
    st.markdown("### 📊 Republic Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <h3>🛕️</h3>
            <p style="font-size: 1.1em; font-weight: bold;">{overview.get('capital', '')}</p>
            <small>Capital</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <h3>📍</h3>
            <p style="font-size: 1.1em; font-weight: bold;">{overview.get('area_km2', ''):,} kmÂ²</p>
            <small>Area</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <h3>👥</h3>
            <p style="font-size: 1.1em; font-weight: bold;">{overview.get('population', ''):,}</p>
            <small>Population</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <h3>🏷️</h3>
            <p style="font-size: 0.9em; font-weight: bold;">{overview.get('bashkir_name', '')}</p>
            <small>Official Name</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Create tabs for different geography sections
    tab1, tab2, tab3, tab4 = st.tabs(["🏙️ Cities", "â›°️ Landmarks", "📚 Facts", "🗺️ Map"])

    with tab1:
        st.markdown("### 🏙️ Major Cities")
        st.markdown("*Click on a city to hear its Bashkir name*")

        # Display cities in a grid
        for i in range(0, len(cities), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(cities):
                    city = cities[i + j]
                    with cols[j]:
                        city_type_colors = {'capital': '#d4af37', 'major': '#0066B3', 'city': '#00AF66'}
                        color = city_type_colors.get(city.get('type', 'city'), '#00AF66')

                        st.markdown(f"""
                        <div class="word-card" style="text-align: center; border-left: 4px solid {color};">
                            <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7em;">
                                {city.get('type', 'city').upper()}
                            </span>
                            <h4 style="color: #00AF66; margin: 10px 0;">{city.get('name', '')}</h4>
                            <p class="bashkir-text" style="font-size: 1.3em;">{city.get('bashkir', '')}</p>
                            <small>Pop: {city.get('population', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.button(f"🔊 Hear", key=f"city_{city.get('name', '')}"):
                            play_audio(city.get('bashkir', ''), slow=True)

    with tab2:
        st.markdown("### â›°️ Notable Landmarks")
        st.markdown("*Sacred mountains, rivers, and caves of Bashkortostan*")

        for landmark in landmarks:
            st.markdown(f"""
            <div class="word-card" style="border-left: 5px solid #d4af37;">
                <div style="display: flex; align-items: flex-start; gap: 15px;">
                    <span style="font-size: 2.5em;">{landmark.get('icon', '📍️')}</span>
                    <div style="flex: 1;">
                        <h4 style="color: #00AF66; margin: 0;">{landmark.get('name', '')}</h4>
                        <p class="bashkir-text" style="font-size: 1.2em; margin: 5px 0;">{landmark.get('bashkir', '')}</p>
                        <p style="color: #333;">{landmark.get('description', '')}</p>
                        <p style="color: #0066B3; font-style: italic; margin-top: 8px;">
                            🌟 <em>{landmark.get('significance', '')}</em>
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📚 Geographic & Natural Facts")

        # Filter by category
        fact_categories = list(set([f.get('category', 'general') for f in facts]))
        selected_cat = st.selectbox("Filter by category:", ['All'] + fact_categories)

        filtered_facts = facts if selected_cat == 'All' else [f for f in facts if f.get('category') == selected_cat]

        for fact in filtered_facts:
            cat_colors = {'geography': '#0066B3', 'nature': '#00AF66', 'resources': '#d4af37'}
            color = cat_colors.get(fact.get('category', ''), '#666')

            st.markdown(f"""
            <div class="word-card">
                <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">
                    {fact.get('category', 'general').upper()}
                </span>
                <h4 style="color: #00AF66; margin: 10px 0;">{fact.get('title', '')}</h4>
                <p style="color: #333;">{fact.get('content', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 🗺️ Map of Bashkortostan")
        st.markdown("*Interactive map showing cities and landmarks*")

        # Create map data for Streamlit
        try:
            import pandas as pd

            # Combine cities and landmarks for mapping
            map_data = []

            for city in cities:
                map_data.append({
                    'lat': city.get('lat', 54.0),
                    'lon': city.get('lon', 56.0),
                    'name': f"🏙️ {city.get('name', '')} ({city.get('bashkir', '')})",
                    'type': 'city'
                })

            for landmark in landmarks:
                map_data.append({
                    'lat': landmark.get('lat', 54.0),
                    'lon': landmark.get('lon', 56.0),
                    'name': f"{landmark.get('icon', 'â›°️')} {landmark.get('name', '')} ({landmark.get('bashkir', '')})",
                    'type': 'landmark'
                })

            df = pd.DataFrame(map_data)

            # Display the map
            st.map(df, latitude='lat', longitude='lon', zoom=6)

            # Legend
            st.markdown("""
            **Map Legend:**
            - 🏙️ Cities
            - â›°️ Mountains
            - 🎨 Cave (Shulgan-Tash)
            - 🌊 River

            *Map data: OpenStreetMap contributors*
            """)

        except ImportError:
            st.warning("Install pandas for map functionality: `pip install pandas`")
            st.info(f"Map would show area from {map_bounds.get('south')}Â° to {map_bounds.get('north')}Â° N, "
                    f"{map_bounds.get('west')}Â° to {map_bounds.get('east')}Â° E")

# === PAGE: MEDIA (TV Guide, Real Russia, Transcription) ===
elif "Media" in selected_page:
    st.title("📺 МедÐ¸Ð° â€” Media Center")
    st.markdown("*Watch Bashkir TV, follow Real Russia content, and transcribe audio*")

    # Create tabs for different media sections
    media_tab1, media_tab2, media_tab3, media_tab4 = st.tabs([
        "📺 TV Guide",
        "🇷🇺 Real Russia",
        "â¬‡️ Downloads",
        "âœ️ Media Transcript"
    ])

    # === TV GUIDE TAB ===
    with media_tab1:
        st.markdown("### 📺 Bashkir Television")
        st.markdown("*Live and recorded content from Bashkir TV channels*")

        # Dimmed viewing container
        st.markdown("""
        <style>
        .tv-container {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 0 40px rgba(0,0,0,0.5);
        }
        .channel-card {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .channel-card:hover {
            background: rgba(255,255,255,0.2);
        }
        </style>
        """, unsafe_allow_html=True)

        # TV Channels
        st.markdown('<div class="tv-container">', unsafe_allow_html=True)

        tv_channels = [
            {
                "name": "Ð‘Ð¡Ð¢ (Bashkir Satellite Television)",
                "description": "Main Bashkir language broadcaster - news, culture, entertainment",
                "stream_url": "https://bst.tv/live",
                "icon": "📡"
            },
            {
                "name": "ÐšÑƒÑ€Ð°Ð¹ Ð¢Ð’ (Kuray TV)",
                "description": "Music and cultural programs featuring traditional Bashkir arts",
                "stream_url": "https://kuray.tv",
                "icon": "🎵"
            },
            {
                "name": "Ð¡Ð°Ð»Ð°Ð²Ð°Ñ‚ Ð®Ð»Ð°ÐµÐ² Ð¢Ð’",
                "description": "Sports channel - hockey and regional sports coverage",
                "stream_url": "#",
                "icon": "💬"
            },
            {
                "name": "Ð¢Ð°Ð¼Ñ‹Ñ€ (Tamyr)",
                "description": "Children's programming in Bashkir language",
                "stream_url": "#",
                "icon": "👶"
            }
        ]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### 📺 Available Channels")
            for channel in tv_channels:
                st.markdown(f"""
                <div class="channel-card">
                    <h4 style="color: #00AF66; margin: 0;">{channel['icon']} {channel['name']}</h4>
                    <p style="color: #aaa; margin: 5px 0;">{channel['description']}</p>
                    <small style="color: #666;">Stream: {channel['stream_url']}</small>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 🕐 TV Schedule (Sample)")
            st.markdown("""
            **Ð‘Ð¡Ð¢ Tonight:**
            - 18:00 â€” Ð¥Ó™Ð±Ó™Ñ€Ò™Ó™Ñ€ (News)
            - 19:00 â€” Ð™Ñ‹Ñ€Ò™Ð°Ñ€ (Songs)
            - 20:00 â€” Ó˜ÐºÐ¸Ó™Ñ‚ (Folk Tales)
            - 21:00 â€” Ð”Ð¾ÐºÑƒÐ¼ÐµÐ½Ñ‚Ð°Ð»ÑŒ (Documentary)
            """)

        st.markdown('</div>', unsafe_allow_html=True)

        # VLC Player Section
        st.markdown("---")
        st.markdown("### 🎬 Video Player")
        st.markdown("*Paste a stream URL or video link to watch*")

        video_url = st.text_input("Enter video/stream URL:", placeholder="https://example.com/stream.m3u8")

        if video_url:
            st.markdown(f"""
            <div style="background: #000; padding: 20px; border-radius: 10px; text-align: center;">
                <p style="color: #666;">To watch: Open this URL in VLC Media Player</p>
                <code style="color: #00AF66;">{video_url}</code>
                <br><br>
                <small style="color: #444;">VLC can be downloaded from videolan.org</small>
            </div>
            """, unsafe_allow_html=True)

        # Sample video embed (YouTube Bashkir content)
        st.markdown("#### 📹 Sample Bashkir Content")
        st.markdown("*Educational content about Bashkir language and culture*")

        sample_videos = [
            {"title": "Bashkir Alphabet Song", "desc": "Learn the letters through music"},
            {"title": "Ural-Batyr Animation", "desc": "The epic legend told visually"},
            {"title": "Kuray Performance", "desc": "Traditional Bashkir flute music"}
        ]

        video_cols = st.columns(3)
        for idx, video in enumerate(sample_videos):
            with video_cols[idx]:
                st.markdown(f"""
                <div class="stat-box" style="text-align: center;">
                    <h5>{video['title']}</h5>
                    <p style="font-size: 0.9em; color: #666;">{video['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

    # === REAL RUSSIA TAB ===
    with media_tab2:
        st.markdown("### 🇷🇺 Real Russia â€” Sergey Baklykov")
        st.markdown("*Follow Sergey Baklykov's Telegram for authentic Russian and Bashkir content*")

        col1, col2 = st.columns([3, 2])

        with col1:
            # Telegram Feed Style Display
            st.markdown("""
            <div style="background: linear-gradient(135deg, #0088cc 0%, #006699 100%);
                        padding: 25px; border-radius: 15px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span style="font-size: 3em;">📱</span>
                    <div>
                        <h3 style="color: white; margin: 0;">@baklykovlive</h3>
                        <p style="color: rgba(255,255,255,0.8); margin: 5px 0;">Real Russia â€” Sergey Baklykov</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📰 Latest from Real Russia")

            # Simulated RSS-style feed entries
            feed_entries = [
                {
                    "title": "Exploring Bashkir Villages",
                    "preview": "Today we visited a traditional Bashkir village where honey is still harvested the ancient way...",
                    "date": "2 hours ago",
                    "engagement": "1.2K views"
                },
                {
                    "title": "Russian Language Tips",
                    "preview": "Quick lesson on common mistakes foreigners make when speaking Russian...",
                    "date": "Yesterday",
                    "engagement": "3.4K views"
                },
                {
                    "title": "Ural Mountains Winter",
                    "preview": "The Southern Urals are magical in winter. Here's what it's like to hike in -20Â°C...",
                    "date": "3 days ago",
                    "engagement": "5.6K views"
                },
                {
                    "title": "Local Food Guide: Ufa",
                    "preview": "The best places to try authentic Bashkir cuisine in the capital city...",
                    "date": "1 week ago",
                    "engagement": "8.2K views"
                }
            ]

            for entry in feed_entries:
                st.markdown(f"""
                <div class="word-card" style="border-left: 4px solid #0088cc;">
                    <h4 style="color: #004d00; margin-bottom: 5px;">{entry['title']}</h4>
                    <p style="color: #333; margin: 10px 0;">{entry['preview']}</p>
                    <div style="display: flex; justify-content: space-between; color: #666; font-size: 0.9em;">
                        <span>â° {entry['date']}</span>
                        <span>👀️ {entry['engagement']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # Channel Info
            st.markdown("""
            <div class="stat-box">
                <h4>📊 Channel Stats</h4>
                <p><strong>Platform:</strong> Telegram</p>
                <p><strong>Focus:</strong> Russian culture, travel, language</p>
                <p><strong>Languages:</strong> Russian, English</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔗 Connect")
            st.link_button("📱 Open Telegram Channel", "https://t.me/baklykovlive", use_container_width=True)

            st.markdown("#### 🎯 Why Follow?")
            st.markdown("""
            - 📍️ Authentic regional content
            - 🗣️ Language learning tips
            - 🏯 Cultural immersion
            - 📹 Regular video updates
            - 🌍 Travel insights
            """)

            st.markdown("#### 📚 Related Resources")
            st.markdown("""
            - [Real Russia YouTube](https://youtube.com)
            - [Patreon Support](https://patreon.com)
            - [Website](https://realrussia.com)
            """)

    # === DOWNLOADS TAB ===
    with media_tab3:
        st.markdown("### â¬‡️ Downloadable Content")
        st.markdown("*Resources you can save for offline study*")

        download_categories = st.tabs(["📄 PDFs", "🎵 Audio", "📖 Texts"])

        with download_categories[0]:
            st.markdown("#### 📄 PDF Resources")

            pdf_resources = [
                {"name": "Bashkir Alphabet Chart", "size": "1.2 MB", "desc": "Complete 42-letter alphabet with examples"},
                {"name": "Basic Phrases Guide", "size": "850 KB", "desc": "100 essential phrases for beginners"},
                {"name": "Grammar Reference", "size": "2.4 MB", "desc": "Comprehensive Bashkir grammar guide"},
                {"name": "OCM Cultural Categories", "size": "1.8 MB", "desc": "Outline of Cultural Materials reference"}
            ]

            for pdf in pdf_resources:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{pdf['name']}**")
                    st.caption(pdf['desc'])
                with col2:
                    st.caption(pdf['size'])
                with col3:
                    st.button(f"📥 Download", key=f"dl_{pdf['name'][:10]}")

        with download_categories[1]:
            st.markdown("#### 🎵 Audio Resources")

            audio_resources = [
                {"name": "Alphabet Pronunciation", "duration": "5:30", "desc": "All 42 letters spoken clearly"},
                {"name": "Basic Vocabulary Pack", "duration": "15:00", "desc": "First 100 words with repetition"},
                {"name": "Kuray Music Collection", "duration": "45:00", "desc": "Traditional flute performances"},
                {"name": "Ural-Batyr Epic Reading", "duration": "2:30:00", "desc": "Complete epic narration"}
            ]

            for audio in audio_resources:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{audio['name']}**")
                    st.caption(audio['desc'])
                with col2:
                    st.caption(f"🕐 {audio['duration']}")
                with col3:
                    st.button(f"📥 Download", key=f"dla_{audio['name'][:10]}")

        with download_categories[2]:
            st.markdown("#### 📖 Text Resources")

            text_resources = [
                {"name": "Word List (JSON)", "format": "JSON", "desc": "Complete vocabulary database"},
                {"name": "Sentence Patterns", "format": "TXT", "desc": "Common sentence structures"},
                {"name": "Cultural Context Notes", "format": "MD", "desc": "OCM-categorized cultural information"},
                {"name": "Memory Palace Map", "format": "JSON", "desc": "Loci data with Ibn Arabi connections"}
            ]

            for text in text_resources:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{text['name']}**")
                    st.caption(text['desc'])
                with col2:
                    st.caption(f"📄 {text['format']}")
                with col3:
                    st.button(f"📥 Download", key=f"dlt_{text['name'][:10]}")

    # === MEDIA TRANSCRIPT TAB ===
    with media_tab4:
        st.markdown("### âœ️ Media Transcription")
        st.markdown("*Transcribe Bashkir audio to text using AI-powered recognition*")

        st.info("🔬 **Powered by:** Turkic Languages Audio-to-Text Transcription technology")

        # Transcription interface
        st.markdown("#### 📤 Upload Audio for Transcription")

        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'ogg', 'm4a'],
            help="Supported formats: MP3, WAV, OGG, M4A"
        )

        if uploaded_file:
            st.audio(uploaded_file)

            col1, col2 = st.columns(2)
            with col1:
                language_mode = st.selectbox(
                    "Transcription Language",
                    ["Bashkir (Ð‘Ð°ÑˆÒ¡Ð¾Ñ€Ñ‚)", "Russian (Ð ÑƒÑÑÐºÐ¸Ð¹)", "Mixed/Auto-detect"]
                )
            with col2:
                output_format = st.selectbox(
                    "Output Format",
                    ["Plain Text", "With Timestamps", "SRT Subtitles"]
                )

            if st.button("🎯 Start Transcription", use_container_width=True):
                with st.spinner("Transcribing audio... This may take a moment."):
                    import time
                    time.sleep(2)  # Simulated processing

                st.success("âœ… Transcription complete!")

                # Sample output
                st.markdown("#### 📜 Transcription Result")
                st.markdown("""
                <div class="word-card" style="background: #f5f5f5;">
                    <p style="font-family: monospace; white-space: pre-wrap;">
[00:00:02] ÒºÐ°ÑƒÐ¼Ñ‹Ò»Ñ‹Ò“Ñ‹Ò™, Ð´ÑƒÒ«Ñ‚Ð°Ñ€!
[00:00:05] Ð‘Ò¯Ð³ÐµÐ½ Ð±ÐµÒ™ Ð‘Ð°ÑˆÒ¡Ð¾Ñ€Ñ‚Ð¾ÑÑ‚Ð°Ð½ Ñ‚ÑƒÑ€Ð°Ò»Ñ‹Ð½Ð´Ð° Ò»Ó©Ð¹Ð»Ó™ÑˆÐµÑ€Ð±ÐµÒ™.
[00:00:10] Ð‘Ð°ÑˆÒ¡Ð¾Ñ€Ñ‚Ð¾ÑÑ‚Ð°Ð½ â€” Ð±Ð¸Ðº Ð¼Ð°Ñ‚ÑƒÑ€ ÐµÑ€.
[00:00:15] Ð£Ð½Ð´Ð° Ñ‚Ð°Ñƒ, ÑƒÑ€Ð¼Ð°Ð½, Ð¹Ñ‹Ð»Ò“Ð° Ð±Ð°Ñ€.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("📋 Copy Text")
                with col2:
                    st.button("📥 Download TXT")
                with col3:
                    st.button("📥 Download SRT")
        else:
            st.markdown("""
            <div class="meditation-box" style="text-align: center;">
                <span style="font-size: 3em;">🎙️</span>
                <h4>Upload audio to begin transcription</h4>
                <p>Drag and drop or click to select a file</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Manual transcription tools
        st.markdown("#### ✏️ Manual Transcription Helper")
        st.markdown("*Type what you hear with assistance*")

        col1, col2 = st.columns([2, 1])

        with col1:
            manual_text = st.text_area(
                "Your transcription:",
                height=150,
                placeholder="Type the Bashkir text you hear..."
            )

            if manual_text:
                st.markdown("**Word Count:** " + str(len(manual_text.split())))
                st.markdown("**Character Count:** " + str(len(manual_text)))

        with col2:
            st.markdown("##### 🔤 Quick Insert")
            special_chars = ['Ó™', 'Ó©', 'Ò¯', 'Ò¡', 'Ò“', 'Ò»', 'Ò™', 'Ò«', 'Ò£']
            char_cols = st.columns(3)
            for idx, char in enumerate(special_chars):
                with char_cols[idx % 3]:
                    if st.button(char, key=f"char_{char}"):
                        st.toast(f"Copied: {char}")

        st.markdown("---")

        # Transcription tips
        with st.expander("💡 Transcription Tips"):
            st.markdown("""
            **For accurate Bashkir transcription:**

            1. **Listen for special sounds:** Pay attention to Ò¡ (like uvular k), Ò“ (like French r), and Ò» (like h)

            2. **Vowel harmony:** Bashkir uses front/back vowel harmony â€” this helps predict spelling

            3. **Common patterns:**
               - -Ð»Ð°Ñ€/-Ð»Ó™Ñ€ (plural suffix)
               - -Ò“Ð°/-Ð³Ó™/-Ò¡Ð°/-ÐºÓ™ (dative case)
               - -Ð´Ð°/-Ð´Ó™/-Ñ‚Ð°/-Ñ‚Ó™ (locative case)

            4. **Word boundaries:** Bashkir is agglutinative â€” long words are often root + multiple suffixes

            5. **Stress:** Usually on the last syllable, which can help identify word endings
            """)

# === PAGE: ALPHABET ===
elif "Alphabet" in selected_page:
    golden_data = load_golden_light_data()
    alphabet_data = golden_data.get('alphabet', {})
    alphabet_title = alphabet_data.get('title', {})
    full_alphabet = alphabet_data.get('full_alphabet', [])
    special_letters = alphabet_data.get('special_letters', [])

    st.title("🔤 БашÒ¡Ð¾Ñ€Ñ‚ Ó™Ð»Ð¸Ñ„Ð±Ð°Ò»Ñ‹ â€” The Bashkir Alphabet")
    st.markdown(f"*{alphabet_data.get('description', '')}*")

    # Full alphabet display
    st.markdown("### 📍 The Complete Alphabet (42 Letters)")

    # Display alphabet in rows
    cols_per_row = 14
    for i in range(0, len(full_alphabet), cols_per_row):
        row_letters = full_alphabet[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, letter in enumerate(row_letters):
            with cols[j]:
                # Highlight special Bashkir letters
                is_special = letter in ['Ó˜', 'Ó¨', 'Ò®', 'Ò’', 'Ò ', 'Ò¢', 'Ò˜', 'Òª', 'Òº']
                bg_color = '#00AF66' if is_special else '#e6f2ff'
                text_color = 'white' if is_special else '#004d00'

                st.markdown(f"""
                <div style="background: {bg_color}; color: {text_color}; padding: 10px;
                            text-align: center; border-radius: 8px; font-size: 1.5em;
                            font-weight: bold; margin: 2px; border: 2px solid #0066B3;">
                    {letter}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("""
    <p style="text-align: center; color: #666; margin-top: 10px;">
        <span style="background: #00AF66; color: white; padding: 2px 8px; border-radius: 4px;">Green</span>
        = Special Bashkir letters not found in Russian
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Special letters detailed
    st.markdown("### 🌟 The 9 Special Bashkir Letters")
    st.markdown("*These unique letters represent sounds not found in Russian*")

    for letter_info in special_letters:
        st.markdown(f"""
        <div class="word-card" style="display: flex; align-items: center; gap: 20px;">
            <div style="background: linear-gradient(135deg, #00AF66 0%, #008f55 100%);
                        color: white; padding: 20px 30px; border-radius: 12px;
                        font-size: 2.5em; font-weight: bold; min-width: 80px; text-align: center;">
                {letter_info.get('letter', '')}
            </div>
            <div style="flex: 1;">
                <h4 style="color: #00AF66; margin: 0 0 5px 0;">{letter_info.get('name', '')}</h4>
                <p style="color: #0066B3; margin: 5px 0;">
                    🔊 Sound: <strong>{letter_info.get('sound', '')}</strong>
                </p>
                <p style="color: #333; margin: 5px 0;">
                    📍 Example: <span class="bashkir-text" style="font-size: 1.1em;">{letter_info.get('example', '')}</span>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Audio button for example
        example_word = letter_info.get('example', '').split(' ')[0]  # Get just the Bashkir word
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(f"🔊 Hear example", key=f"alpha_{letter_info.get('letter', '')}"):
                play_audio(example_word, slow=True)
        with col2:
            st.write("")

    # Practice section
    st.markdown("---")
    st.markdown("### 🎯 Quick Reference")

    st.markdown("""
    | Letter | IPA | Similar To | Example |
    |:------:|:---:|:-----------|:--------|
    | **Ó˜** | /Ã¦/ | 'a' in "cat" | Ó™ÑÓ™ (mother) |
    | **Ó¨** | /Ã¸/ | German 'Ã¶' | Ó©Ð¹ (house) |
    | **Ò®** | /y/ | German 'Ã¼' | Ò¯Ò™ (self) |
    | **Ò’** | /Ê/ | Arabic 'Øº' (gh) | Ò“Ð°Ð¸Ð»Ó™ (family) |
    | **Ò ** | /q/ | Deep throat 'k' | Ò¡Ñ‹Ò™ (girl) |
    | **Ò¢** | /Å‹/ | 'ng' in "sing" | Ñ‚Ð°Ò£ (dawn) |
    | **Ò˜** | // | 'th' in "this" | Ò™ÑƒÑ€ (big) |
    | **Òª** | /Î¸/ | 'th' in "think" | Ò«Ó™Ñ (hair) |
    | **Òº** | /h/ | 'h' in "house" | Ò»Ñ‹Ñƒ (water) |
    """)

# === PAGE: SENTENCE BUILDER (Enhanced with Audio Export and Working Word Bank) ===
elif "Sentence Builder" in selected_page:
    st.title("âœ️ Sentence Builder")
    st.markdown("*Create your own Bashkir sentences, hear them spoken, and export audio for poems or stories!*")

    patterns = load_patterns()

    # Pattern templates
    st.markdown("### 📍 Sentence Patterns")

    pattern_list = patterns.get('patterns', [])[:5]

    if pattern_list:
        cols = st.columns(len(pattern_list))
        for idx, pattern in enumerate(pattern_list):
            with cols[idx]:
                st.markdown(f"""
                **{pattern['name']}**
                `{pattern['template']}`
                *{pattern['english_pattern']}*
                """)
                example = pattern.get('examples', [{}])[0]
                if example:
                    st.caption(f"Ex: {example.get('bashkir', '')}")

    st.markdown("---")

    # Word bank - enhanced with expanded categories
    st.markdown("### 🐦 Word Bank")
    st.markdown("*Click words to add them to your sentence. Words are organized by semantic categories.*")

    # Define OCM-based semantic categories for nouns
    nature_ocm = ['131', '132', '133', '134', '137', '138', '139', '221', '222', '231', '232', '233', '234', '235', '241', '242', '243', '244', '245', '246', '251', '252', '253', '254', '255', '256', '257', '258', '259']
    culture_ocm = ['530', '531', '532', '533', '534', '535', '536', '537', '538', '539', '541', '542', '543', '544', '545', '551', '552', '553', '554', '561', '562', '563', '564', '565', '566', '571', '572', '573', '574', '575', '576', '577', '578', '579', '581', '582', '583', '584', '585', '586', '587']
    people_ocm = ['591', '592', '593', '594', '595', '596', '597', '598', '599', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '621', '622', '623', '624', '625', '626', '627', '628', '629']
    places_ocm = ['361', '362', '363', '364', '365', '366', '367', '368', '369', '481', '482', '483', '484', '485', '486', '487', '488', '489', '131', '784']

    # Nature keywords for backup categorization
    nature_keywords = ['Ñ‚Ð°Ñƒ', 'Ò¡Ð¾ÑÑˆ', 'Ð°Ð¹', 'Ð¹Ð¾Ð½Ð´Ð¾Ò™', 'Ò»Ñ‹Ñƒ', 'Ð¹Ñ‹Ð»Ò“Ð°', 'ÐºÒ¯Ð»', 'Ð´Ð¸Ò£Ð³ÐµÒ™', 'ÑƒÑ€Ð¼Ð°Ð½', 'Ð°Ò“Ð°Ñ', 'ÑÓ™ÑÐºÓ™', 'Ò¯Ð»Ó™Ð½', 'Ò¡Ð¾Ñˆ', 'Ð°Ð¹Ñ‹Ñƒ', 'Ð±Ò¯Ñ€Ðµ', 'Ò¡ÑƒÐ¹', 'Ð°Ñ‚', 'Ò»Ñ‹Ð¹Ñ‹Ñ€', 'Ð±Ð°Ð»Ñ‹Ò¡', 'Ð¹Ñ‹Ð»Ð°Ð½', 'ÐµÐ»', 'Ò¡Ð°Ñ€', 'Ð±Ð¾Ò™', 'ÑÐ¼Ò“Ñ‹Ñ€', 'Ð±Ð¾Ð»Ð¾Ñ‚', 'ÐºÓ©Ð½', 'Ñ‚Ó©Ð½', 'ÑÒ™', 'Ð¹Ó™Ð¹', 'ÐºÓ©Ò™', 'Ò¡Ñ‹Ñˆ', 'Ñ‚Ð°Ñˆ', 'Ñ‚ÑƒÑ„Ñ€Ð°Ò¡', 'ÐµÑ€', 'Ð½ÑƒÑ€']
    culture_keywords = ['Ð±Ð°Ð¹Ñ€Ð°Ð¼', 'ÑÐ°Ð±Ð°Ð½Ñ‚ÑƒÐ¹', 'Ñ‚ÑƒÐ¹', 'Ð¹Ð¾Ð»Ð°', 'Ó™ÐºÐ¸Ó™Ñ‚', 'Ñ€Ð¸Ò¯Ó™Ð¹Ó™Ñ‚', 'Ð¹Ñ‹Ñ€', 'Ð¼Ð¾Ò£', 'Ð±ÐµÐ¹ÐµÒ¯', 'Ò¡ÑƒÑ€Ð°Ð¹', 'Ð´ÑƒÐ¼Ð±Ñ‹Ñ€Ð°', 'Ò¡ÑƒÐ±Ñ‹Ò™', 'Ð±Ð°Ð»', 'Ò¡Ñ‹Ð¼Ñ‹Ò™', 'Ð±ÑƒÒ™Ð°', 'Ð¸ÐºÐ¼Ó™Ðº', 'Ð¸Ñ‚', 'Ð°Ñˆ', 'ÑÓ™Ð¹', 'Ñ‚Ð¸Ñ€Ð¼Ó™', 'Ð±Ð¸Ò™Ó™Ðº', 'Ð¾Ð¹Ð¼Ð°', 'ÐºÓ©Ñ€Ó™Ñˆ', 'ÑƒÐ¹Ñ‹Ð½', 'Ð´Ð¸Ð½', 'Ð¼Ó™ÑÑŒÐµÑ‚', 'Ñ‚ÐµÐ°Ñ‚Ñ€']
    people_keywords = ['Ð°Ñ‚Ð°', 'Ó™ÑÓ™', 'Ð±Ð°Ð»Ð°', 'Ò¡Ñ‹Ò™', 'ÐµÐ³ÐµÑ‚', 'Ð±Ð°Ð±Ð°Ð¹', 'Ó©Ð»Ó™ÑÓ™Ð¹', 'Ñ‚ÑƒÒ“Ð°Ð½Ð´Ð°Ñ€', 'Ò“Ð°Ð¸Ð»Ó™', 'Ñ…Ð°Ð»Ñ‹Ò¡', 'Ð¼Ð¸Ð»Ð»Ó™Ñ‚', 'Ð´ÑƒÒ«', 'Ò¡ÑƒÐ½Ð°Ò¡', 'ÑƒÒ¡Ñ‹Ñ‚Ñ‹ÑƒÑÑ‹', 'ÑÑˆÑÐµ', 'Ð¾Ò«Ñ‚Ð°', 'Ð±Ð°Ñ‚Ñ‹Ñ€', 'Ð³Ñ€Ð°Ð¶Ð´Ð°Ð½', 'Ð¿Ñ€ÐµÐ·Ð¸Ð´ÐµÐ½Ñ‚']
    places_keywords = ['Ó¨Ñ„Ó©', 'Ð‘Ð°ÑˆÒ¡Ð¾Ñ€Ñ‚Ð¾ÑÑ‚Ð°Ð½', 'Ò¡Ð°Ð»Ð°', 'ÑƒÑ€Ð°Ð¼', 'Ð¼Ó™Ð¹Ò™Ð°Ð½', 'Ó©Ð¹', 'Ð¹Ð¾Ñ€Ñ‚', 'Ð¼Ó™ÐºÑ‚Ó™Ð¿', 'Ð·Ð°Ð²Ð¾Ð´', 'Ð¼Ð°Ð³Ð°Ð·Ð¸Ð½', 'Ð±Ð°Ð½Ðº', 'Ð¿Ð¾Ñ‡Ñ‚Ð°', 'Ð¸Ð»', 'Ð´Ó™Ò¯Ð»Ó™Ñ‚', 'Ñ€ÐµÑÐ¿ÑƒÐ±Ð»Ð¸ÐºÐ°', 'ÐÒ“Ð¸Ò™ÐµÐ»', 'Ð¨Ò¯Ð»Ð³Ó™Ð½Ñ‚Ð°Ñˆ', 'Ð¯Ð¼Ð°Ð½Ñ‚Ð°Ñƒ', 'Ð˜Ñ€ÐµÐ¼Ó™Ð»', 'Ð‘Ð¸Ð¶Ð±ÑƒÐ»ÑÐº', 'Ð‘ÐµÐ»Ð¾Ñ€ÐµÑ‚']

    # Expanded word categories
    word_categories = {
        "👥 Pronouns": [],
        "🌿 Nature": [],
        "🎭 Culture": [],
        "👨â€👩â€👧 People": [],
        "🛕️ Places": [],
        "💭 Concepts": [],
        "🎬 Verbs": [],
        "📍 Adjectives": [],
        "🔢 Numbers": []
    }

    for word in words_data:
        pos = word.get('pos', 'noun').lower()
        bashkir = word['bashkir']
        english = word.get('english', '').lower()

        # Get OCM codes from word data
        ocm_codes = []
        if 'cultural_context' in word and 'ocm_codes' in word['cultural_context']:
            ocm_codes = word['cultural_context']['ocm_codes']

        if pos == 'pronoun':
            word_categories["👥 Pronouns"].append(bashkir)
        elif pos == 'verb':
            word_categories["🎬 Verbs"].append(bashkir)
        elif pos in ['adjective', 'adj']:
            word_categories["📍 Adjectives"].append(bashkir)
        elif pos in ['number', 'numeral']:
            word_categories["🔢 Numbers"].append(bashkir)
        elif pos == 'noun':
            # Categorize nouns by OCM code or keywords
            categorized = False

            # Check OCM codes first
            for code in ocm_codes:
                if code in nature_ocm:
                    word_categories["🌿 Nature"].append(bashkir)
                    categorized = True
                    break
                elif code in culture_ocm:
                    word_categories["🎭 Culture"].append(bashkir)
                    categorized = True
                    break
                elif code in people_ocm:
                    word_categories["👨â€👩â€👧 People"].append(bashkir)
                    categorized = True
                    break
                elif code in places_ocm:
                    word_categories["🛕️ Places"].append(bashkir)
                    categorized = True
                    break

            # If not categorized by OCM, check keywords
            if not categorized:
                if any(kw in bashkir for kw in nature_keywords) or any(kw in english for kw in ['sun', 'moon', 'star', 'water', 'river', 'lake', 'tree', 'forest', 'bird', 'animal', 'wolf', 'bear', 'fish', 'horse', 'cow', 'sheep', 'snow', 'rain', 'wind', 'day', 'night', 'spring', 'summer', 'autumn', 'winter', 'flower', 'grass', 'mountain', 'stone', 'earth', 'sky']):
                    word_categories["🌿 Nature"].append(bashkir)
                elif any(kw in bashkir for kw in culture_keywords) or any(kw in english for kw in ['festival', 'wedding', 'song', 'dance', 'music', 'honey', 'kumis', 'bread', 'meat', 'tea', 'food', 'tradition', 'legend', 'tale', 'story', 'holiday', 'craft', 'art', 'ornament', 'religion']):
                    word_categories["🎭 Culture"].append(bashkir)
                elif any(kw in bashkir for kw in people_keywords) or any(kw in english for kw in ['father', 'mother', 'child', 'girl', 'boy', 'grandfather', 'grandmother', 'family', 'relative', 'people', 'nation', 'friend', 'guest', 'teacher', 'worker', 'hero', 'citizen', 'president']):
                    word_categories["👨â€👩â€👧 People"].append(bashkir)
                elif any(kw in bashkir for kw in places_keywords) or any(kw in english for kw in ['city', 'street', 'square', 'house', 'home', 'school', 'factory', 'shop', 'bank', 'post', 'country', 'state', 'republic', 'capital', 'village', 'ufa', 'bashkortostan']):
                    word_categories["🛕️ Places"].append(bashkir)
                else:
                    word_categories["💭 Concepts"].append(bashkir)
        else:
            word_categories["💭 Concepts"].append(bashkir)

    # Remove empty categories and deduplicate
    word_categories = {k: list(dict.fromkeys(v)) for k, v in word_categories.items() if v}

    if word_categories:
        # Create tabs with expanded categories
        tabs = st.tabs(list(word_categories.keys()))

        for tab, (category, word_list) in zip(tabs, word_categories.items()):
            with tab:
                st.markdown(f"**{len(word_list)} words available:**")

                # Display words in a grid - 4 columns for better readability
                cols_per_row = 4
                max_words = 40  # Increased limit for better coverage
                for row_start in range(0, min(len(word_list), max_words), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for idx, col in enumerate(cols):
                        word_idx = row_start + idx
                        if word_idx < len(word_list):
                            word = word_list[word_idx]
                            word_data = next((w for w in words_data if w['bashkir'] == word), None)
                            english = word_data.get('english', '?') if word_data else '?'

                            with col:
                                # Create a unique key for each word button
                                btn_key = f"wb_{category[:3]}_{word_idx}_{word[:5] if len(word) >= 5 else word}"
                                if st.button(f"**{word}**\n_{english}_", key=btn_key, use_container_width=True):
                                    st.session_state.builder_sentence.append({
                                        'word': word,
                                        'english': english
                                    })
                                    st.rerun()

                if len(word_list) > max_words:
                    st.caption(f"*Showing {max_words} of {len(word_list)} words. Use search in Audio Dictionary for more.*")
    else:
        st.warning("No words available. Check if words.json is properly loaded.")

    st.markdown("---")

    # Current sentence display
    st.markdown("### 📜 Your Sentence")

    if st.session_state.builder_sentence:
        sentence_text = ' '.join([w['word'] for w in st.session_state.builder_sentence])
        gloss_text = ' | '.join([w['english'] for w in st.session_state.builder_sentence])

        st.markdown(f"""
        <div class="word-card">
            <span class="bashkir-text">{sentence_text}</span>
            <br><br>
            <small style="color: #666;">Gloss: {gloss_text}</small>
        </div>
        """, unsafe_allow_html=True)

        # Audio controls
        st.markdown("### 🔊 Audio Controls")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔊 Hear Sentence"):
                play_audio(sentence_text, slow=False)

        with col2:
            if st.button("🔊 Hear Slow"):
                play_audio(sentence_text, slow=True)

        with col3:
            if st.button("💾 Save Sentence"):
                st.session_state.saved_sentences.append({
                    'bashkir': sentence_text,
                    'gloss': gloss_text,
                    'created': datetime.now().isoformat()
                })
                st.success("Sentence saved to your phrasebook!")

        with col4:
            if st.button("🗑️ Clear"):
                st.session_state.builder_sentence = []
                st.rerun()

        # Audio export
        st.markdown("### 💾 Export Audio")
        audio_bytes = generate_audio_with_retry(sentence_text, slow=True)
        if audio_bytes:
            st.download_button(
                label="â¬‡️ Download Audio (MP3)",
                data=audio_bytes,
                file_name=f"bashkir_sentence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                mime="audio/mp3"
            )

        # Grammar notes
        st.markdown("### 📖 Grammar Helper")
        st.info("""
        **Bashkir Word Order: Subject - Object - Verb (SOV)**

        Unlike English (I *see* the mountain), Bashkir puts the verb at the END:
        - ÐœÐ¸Ð½ Ñ‚Ð°ÑƒÒ™Ñ‹ **ÐºÒ¯Ñ€Ó™Ð¼** (I mountain **see**)

        **Case Suffixes:**
        - Nominative (subject): no suffix
        - Dative (to/for): -Ò“Ð°/-Ð³Ó™
        - Accusative (object): -Ð½Ñ‹/-Ð½Ðµ
        - Ablative (from): -Ð´Ð°Ð½/-Ð´Ó™Ð½
        """)
    else:
        st.markdown("*Click words from the Word Bank to build your sentence.*")

    # Saved sentences with audio export
    if st.session_state.saved_sentences:
        st.markdown("---")
        st.markdown("### 📒 Your Phrasebook")

        for idx, sentence in enumerate(st.session_state.saved_sentences[-5:]):
            with st.container():
                st.markdown(f"""
                <div class="word-card">
                    <strong>{sentence['bashkir']}</strong><br>
                    <small>{sentence.get('gloss', '')}</small>
                </div>
                """, unsafe_allow_html=True)

                sent_col1, sent_col2, sent_col3 = st.columns(3)
                with sent_col1:
                    if st.button(f"â–¶️ Play", key=f"play_saved_{idx}"):
                        play_audio(sentence['bashkir'], slow=True)
                with sent_col2:
                    audio_data = generate_audio_with_retry(sentence['bashkir'], slow=True)
                    if audio_data:
                        st.download_button(
                            label="â¬‡️ Download",
                            data=audio_data,
                            file_name=f"sentence_{idx+1}.mp3",
                            mime="audio/mp3",
                            key=f"download_saved_{idx}"
                        )
                with sent_col3:
                    if st.button(f"🗑️ Remove", key=f"remove_saved_{idx}"):
                        st.session_state.saved_sentences.pop(idx)
                        st.rerun()

# === PAGE: AUDIO DICTIONARY (Enhanced with OCM Categories) ===
elif "Audio Dictionary" in selected_page:
    st.title("🔊 Audio Dictionary")
    st.markdown("*Listen to all Bashkir words organized by cultural categories (OCM eHRAF 2021)*")

    # Load OCM mapping
    ocm_data = load_ocm_mapping()
    thematic_groups = ocm_data.get('thematic_groups', {})
    ocm_labels = ocm_data.get('ocm_labels', {})

    # Search bar with improved styling
    st.markdown("### 📄 Search")
    search_term = st.text_input("Search words (Bashkir, English, or Russian):",
                                 key="audio_search",
                                 placeholder="Type to search all words...")

    # Filter words based on search
    if search_term:
        filtered_words = [w for w in words_data if
                         search_term.lower() in w['bashkir'].lower() or
                         search_term.lower() in w.get('english', '').lower() or
                         search_term.lower() in w.get('russian', '').lower()]
        st.markdown(f"**Found {len(filtered_words)} matching words**")

        # Show search results
        for word in filtered_words:
            with st.expander(f"🔊 {word['bashkir']} â€” {word.get('english', '')}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    ocm_codes = word.get('cultural_context', {}).get('ocm_codes', [])
                    ocm_names = [ocm_labels.get(code, code) for code in ocm_codes[:3]]

                    st.markdown(f"""
                    <div class="word-card">
                        <span class="bashkir-text" style="font-size: 2em;">{word['bashkir']}</span>
                        <span class="ipa-text" style="font-size: 1.2em;">{word.get('ipa', '')}</span>
                        <div class="english-text" style="font-size: 1.3em; margin: 10px 0;">{word.get('english', '')}</div>
                        <span class="russian-text" style="font-size: 1.1em;">🇷🇺 {word.get('russian', '')}</span>
                        <br><br>
                        <span style="color: #0066B3; font-size: 0.9em;">📚 OCM: {', '.join(ocm_names) if ocm_names else 'General'}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("**🔊 Audio:**")
                    if st.button("â–¶️ Normal", key=f"audio_normal_{word['id']}"):
                        play_audio(word['bashkir'], slow=False)
                    if st.button("🏢 Slow", key=f"audio_slow_{word['id']}"):
                        play_audio(word['bashkir'], slow=True)

                    audio_bytes = generate_audio_with_retry(word['bashkir'], slow=True)
                    if audio_bytes:
                        st.download_button(
                            label="â¬‡️ Download",
                            data=audio_bytes,
                            file_name=f"{word['bashkir']}.mp3",
                            mime="audio/mp3",
                            key=f"download_{word['id']}"
                        )
    else:
        # Show all words organized by OCM thematic groups
        st.markdown("---")
        st.markdown("### 📚 Browse by Cultural Category (OCM eHRAF 2021)")
        st.markdown("*Words organized into 2-5 word groups by anthropological classification*")

        # Create tabs for thematic groups
        group_names = list(thematic_groups.keys())
        display_names = [thematic_groups[g].get('display_name', g) for g in group_names]

        if display_names:
            tabs = st.tabs(display_names)

            for tab, group_key in zip(tabs, group_names):
                with tab:
                    group_info = thematic_groups[group_key]
                    group_words_list = group_info.get('words', [])
                    ocm_codes = group_info.get('ocm_codes', [])

                    # Get OCM labels for this group
                    ocm_names = [f"{code}: {ocm_labels.get(code, 'Unknown')}" for code in ocm_codes[:5]]

                    st.markdown(f"**OCM Categories:** {', '.join(ocm_names[:3])}...")

                    # Find matching words from words_data
                    matching_words = []
                    for word in words_data:
                        word_ocm = word.get('cultural_context', {}).get('ocm_codes', [])
                        if any(code in word_ocm for code in ocm_codes):
                            matching_words.append(word)
                        elif word['bashkir'] in group_words_list:
                            matching_words.append(word)

                    # Remove duplicates
                    seen = set()
                    unique_words = []
                    for w in matching_words:
                        if w['bashkir'] not in seen:
                            seen.add(w['bashkir'])
                            unique_words.append(w)

                    if unique_words:
                        st.markdown(f"**{len(unique_words)} words in this category:**")

                        # Display in groups of 3-4 per row
                        for i in range(0, len(unique_words), 3):
                            cols = st.columns(3)
                            for j, col in enumerate(cols):
                                if i + j < len(unique_words):
                                    word = unique_words[i + j]
                                    with col:
                                        st.markdown(f"""
                                        <div class="word-card" style="text-align: center; min-height: 120px;">
                                            <span class="bashkir-text" style="font-size: 1.6em;">{word['bashkir']}</span>
                                            <span class="ipa-text">{word.get('ipa', '')}</span>
                                            <div style="color: #004d00; font-size: 1.1em; margin: 8px 0;">{word.get('english', '')}</div>
                                            <small style="color: #666;">🇷🇺 {word.get('russian', '')}</small>
                                        </div>
                                        """, unsafe_allow_html=True)

                                        bcol1, bcol2 = st.columns(2)
                                        with bcol1:
                                            if st.button("🔊", key=f"cat_audio_{group_key}_{word['id']}",
                                                        help=f"Play {word['bashkir']}"):
                                                play_audio(word['bashkir'], slow=True)
                                        with bcol2:
                                            audio_data = generate_audio_with_retry(word['bashkir'], slow=True)
                                            if audio_data:
                                                st.download_button(
                                                    "â¬‡️",
                                                    data=audio_data,
                                                    file_name=f"{word['bashkir']}.mp3",
                                                    mime="audio/mp3",
                                                    key=f"cat_dl_{group_key}_{word['id']}"
                                                )
                    else:
                        st.info("No words found in this category yet.")

        # Show total word count
        st.markdown("---")
        st.markdown(f"**📊 Total: {len(words_data)} words in dictionary**")

# === PAGE: REVIEW (Fixed ZeroDivisionError) ===
elif "Review" in selected_page:
    st.title("🔄 Spaced Repetition Review")
    st.markdown("*Review learned words using the SM-2 algorithm for optimal retention.*")

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-box">
            <h3>📚</h3>
            <h2>{}</h2>
            <p>Total Learned</p>
        </div>
        """.format(len(st.session_state.learned_words)), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-box">
            <h3>📋</h3>
            <h2>{}</h2>
            <p>Due Today</p>
        </div>
        """.format(len(st.session_state.review_queue)), unsafe_allow_html=True)

    with col3:
        mastered = len([w for w in st.session_state.learned_words
                       if st.session_state.srs_data.get(w, {}).get('interval', 0) >= 21])
        st.markdown(f"""
        <div class="stat-box">
            <h3>🏆</h3>
            <h2>{mastered}</h2>
            <p>Mastered</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        accuracy = 85  # Placeholder
        st.markdown(f"""
        <div class="stat-box">
            <h3>🎯</h3>
            <h2>{accuracy}%</h2>
            <p>Accuracy</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Review session
    if st.session_state.review_queue:
        st.markdown("### 📍 Review Session")

        # Get current word
        if 'review_index' not in st.session_state:
            st.session_state.review_index = 0

        if st.session_state.review_index < len(st.session_state.review_queue):
            current_word = st.session_state.review_queue[st.session_state.review_index]
            word_data = next((w for w in words_data if w['bashkir'] == current_word), None)

            if word_data:
                # Flashcard
                if 'show_answer' not in st.session_state:
                    st.session_state.show_answer = False

                st.markdown(f"""
                <div class="word-card" style="text-align: center; padding: 40px;">
                    <span class="bashkir-text" style="font-size: 2.5em;">{word_data['bashkir']}</span>
                    <br><br>
                    <small>{word_data.get('ipa', '')}</small>
                </div>
                """, unsafe_allow_html=True)

                if not st.session_state.show_answer:
                    if st.button("👀️ Show Answer", use_container_width=True):
                        st.session_state.show_answer = True
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="word-card" style="text-align: center; background: #e8f5e9;">
                        <h2>{word_data['english']}</h2>
                        <p><em>{word_data.get('russian', '')}</em></p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show mnemonic
                    mnemonic = word_data.get('memory_palace', {}).get('mnemonic', '')
                    if mnemonic:
                        st.markdown(f"""
                        <div class="mnemonic-text">
                        {mnemonic}
                        </div>
                        """, unsafe_allow_html=True)

                    # Rating buttons
                    st.markdown("**How well did you remember?**")

                    col1, col2, col3, col4 = st.columns(4)

                    ratings = [
                        ("😞 Forgot", 1, col1),
                        ("😕 Hard", 3, col2),
                        ("🏙‚ Good", 4, col3),
                        ("😄 Easy", 5, col4)
                    ]

                    for label, rating, col in ratings:
                        with col:
                            if st.button(label, key=f"rate_{rating}", use_container_width=True):
                                # Update SRS data
                                if current_word not in st.session_state.srs_data:
                                    st.session_state.srs_data[current_word] = {
                                        'ease': 2.5, 'interval': 0, 'reps': 0
                                    }

                                srs = st.session_state.srs_data[current_word]

                                if rating >= 3:
                                    if srs['reps'] == 0:
                                        srs['interval'] = 1
                                    elif srs['reps'] == 1:
                                        srs['interval'] = 6
                                    else:
                                        srs['interval'] = int(srs['interval'] * srs['ease'])
                                    srs['reps'] += 1
                                else:
                                    srs['interval'] = 1
                                    srs['reps'] = 0

                                srs['ease'] = max(1.3, srs['ease'] + (0.1 - (5 - rating) * 0.08))

                                # Move to next word
                                st.session_state.review_index += 1
                                st.session_state.show_answer = False
                                st.rerun()

                # Progress - FIXED: proper parentheses to avoid ZeroDivisionError
                total_reviews = len(st.session_state.review_queue)
                if total_reviews > 0:
                    progress = (st.session_state.review_index + 1) / total_reviews
                else:
                    progress = 0.0
                st.progress(min(progress, 1.0))
                st.caption(f"Card {st.session_state.review_index + 1} of {total_reviews}")
        else:
            st.success("🎉 Review session complete!")
            if st.button("Start New Session"):
                st.session_state.review_index = 0
                st.session_state.show_answer = False
                st.rerun()
    else:
        st.info("No words to review! Visit the Palace to learn new words.")
        if st.button("Go to Palace"):
            st.rerun()


    # === NEW: Self-Acting Progress Tracker (Theological Framework) ===
    st.markdown("---")
    st.markdown("### 📿 Progress Toward Self-Acting Fluency")
    st.markdown("""
    *From the Way of a Pilgrim: The goal is for Bashkir to arise naturally, without effort.*
    
    > "I spent the entire summer continuously repeating the Jesus Prayer... 
    > all thoughts seemed to vanish on their own... without any effort."
    > — The Pilgrim
    """)
    
    # Calculate total reviews across all words
    total_reviews = sum(
        st.session_state.srs_data.get(w, {}).get('reviews', 0) 
        for w in st.session_state.learned_words
    )
    st.session_state.total_reviews_completed = total_reviews
    
    # Map to Pilgrim's stages
    if total_reviews < 100:
        fluency_stage = "🌱 Beginning (like 3,000 prayers)"
        stage_progress = total_reviews / 100
        stage_desc = "Each word requires conscious effort. This is normal and necessary."
    elif total_reviews < 500:
        fluency_stage = "🌿 Ease (like 6,000 prayers)"
        stage_progress = (total_reviews - 100) / 400
        stage_desc = "Practice becomes easier. Words start to feel familiar."
    elif total_reviews < 2000:
        fluency_stage = "🌳 Delight (like 12,000 prayers)"
        stage_progress = (total_reviews - 500) / 1500
        stage_desc = "Joy in simple sentences. The language is becoming part of you."
    else:
        fluency_stage = "🌟 Self-Acting (the goal!)"
        stage_progress = 1.0
        stage_desc = "Bashkir arises naturally. You don't translate—you think."
    
    st.markdown(f"**Current Stage:** {fluency_stage}")
    st.progress(stage_progress)
    st.markdown(f"*{stage_desc}*")
    st.caption(f"Total Reviews Completed: {total_reviews}")
    
    # === NEW: Post-Review Reflection (Pedagogical Framework) ===
    st.markdown("---")
    st.markdown("### 📝 Review Reflection")
    st.markdown('*"Choose, and you shall see what validity there is in it."* — Kierkegaard')
    
    reflection_prompts = [
        "What word surprised you today?",
        "Which word do you feel you truly *know* now?",
        "What distracted you during this session? (logismoi)",
        "Did any word connect to your personal life?",
        "What would help you remember these words better?",
    ]
    
    import random
    if 'review_reflection_prompt' not in st.session_state:
        st.session_state.review_reflection_prompt = random.choice(reflection_prompts)
    
    st.markdown(f"*{st.session_state.review_reflection_prompt}*")
    
    review_reflection = st.text_area("Your reflection:", key="review_page_reflection", height=100)
    
    if st.button("Save Reflection", key="save_review_reflection"):
        if review_reflection.strip():
            st.session_state.reflection_journal.append({
                'date': datetime.now().isoformat(),
                'prompt': st.session_state.review_reflection_prompt,
                'reflection': review_reflection,
                'context': 'review_session'
            })
            st.success("Reflection saved to your journal!")
            # Pick a new prompt for next time
            st.session_state.review_reflection_prompt = random.choice(reflection_prompts)
        else:
            st.info("Write something first, then save.")

# === PAGE: BASHKORTNET EXPLORER (Enhanced with OCM and Neo4j) ===
elif "BashkortNet" in selected_page:
    st.title("🕸️ BashkortNet Explorer (Semantic Network)")
    st.markdown("*Explore the semantic network connecting Bashkir words with OCM cultural classifications.*")

    # Load OCM data
    ocm_data = load_ocm_mapping()
    ocm_labels = ocm_data.get('ocm_labels', {})
    bashkir_to_ocm = ocm_data.get('bashkir_to_ocm', {})

    # Neo4j integration info
    st.markdown("---")
    st.markdown("### 🗄️ Neo4j Graph Database Integration")
    st.info("""
    **Future Development:** BashkortNet is designed to integrate with Neo4j graph database for advanced semantic queries.

    **Planned Features:**
    - Cypher query support for complex relationship traversal
    - Visual graph exploration of word connections
    - Export semantic network to Neo4j format
    - Real-time knowledge graph updates

    **Current Data Format:** The BashkortNet relationships in this app use JSON-LD compatible structures
    that can be directly imported into Neo4j using APOC procedures.
    """)

    # Export to Neo4j format button
    if st.button("📤 Export to Neo4j Format (Cypher)"):
        # Generate Cypher statements
        cypher_statements = []
        cypher_statements.append("// Neo4j Cypher statements for BashkortNet")
        cypher_statements.append("// Run these in Neo4j Browser or neo4j-admin")
        cypher_statements.append("")

        for word in words_data[:20]:  # Limit for display
            bashkir = word['bashkir'].replace("'", "\\'")
            english = word.get('english', '').replace("'", "\\'")
            cypher_statements.append(f"CREATE (w:Word {{bashkir: '{bashkir}', english: '{english}', pos: '{word.get('pos', 'noun')}'}})")

            # Add relations
            bashkortnet_data = word.get('bashkortnet', {})
            relations = bashkortnet_data.get('relations', {})
            for rel_type, targets in relations.items():
                for target in targets:
                    if isinstance(target, dict):
                        target_word = target.get('target', '').replace("'", "\\'")
                    else:
                        target_word = str(target).replace("'", "\\'")
                    if target_word:
                        cypher_statements.append(f"// {bashkir} -{rel_type}-> {target_word}")

        st.code("\n".join(cypher_statements[:30]), language="cypher")
        st.caption("*Showing first 30 statements. Full export available for download.*")

    st.markdown("---")

    # Word search with Bashkir and English
    search_word = st.selectbox(
        "Select a word to explore (Bashkir / English):",
        [w['bashkir'] for w in words_data],
        format_func=lambda x: f"{x} ({next((w['english'] for w in words_data if w['bashkir'] == x), '?')})"
    )

    if search_word:
        word_data = next((w for w in words_data if w['bashkir'] == search_word), None)

        if word_data:
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"""
                <div class="word-card">
                    <span class="bashkir-text">{word_data['bashkir']} (Ð‘Ð°ÑˆÒ¡Ð¾Ñ€Ñ‚ Ñ‚ÐµÐ»Ðµ)</span>
                    <br>
                    <small>{word_data.get('ipa', '')}</small>
                    <br><br>
                    <strong>{word_data['english']} (English)</strong>
                    <br>
                    <em>{word_data.get('russian', '')}</em>
                    <br><br>
                    <small>POS: {word_data.get('pos', 'noun')}</small>
                </div>
                """, unsafe_allow_html=True)

                # Audio button
                if st.button("🔊 Play Pronunciation", key=f"bashkortnet_audio_{word_data['id']}"):
                    play_audio(word_data['bashkir'], slow=True)

            with col2:
                # Create tabs for different aspects
                tab1, tab2, tab3 = st.tabs(["🕸️ Semantic Network", "📚 OCM Codes", "🔗 Etymology"])

                with tab1:
                    st.markdown("### Semantic Relations")

                    bashkortnet = word_data.get('bashkortnet', {})
                    relations = bashkortnet.get('relations', {})

                    if relations:
                        for rel_type, targets in relations.items():
                            if targets:
                                rel_labels = {
                                    'SYN': '🔄 Synonyms',
                                    'ANT': 'â†”️ Antonyms',
                                    'ISA': 'â¬†️ Is a type of',
                                    'HAS_TYPE': 'â¬‡️ Types',
                                    'PART_OF': '🧩 Part of',
                                    'HAS_PART': '🔧 Has parts',
                                    'CULT_ASSOC': '🛕️ Cultural',
                                    'MYTH_LINK': '📜 Mythological'
                                }

                                st.markdown(f"**{rel_labels.get(rel_type, rel_type)}:**")

                                for target in targets:
                                    if isinstance(target, dict):
                                        target_word = target.get('target', target.get('gloss', str(target)))
                                        gloss = target.get('gloss', '')
                                        note = target.get('note', '')
                                        display = f"- {target_word}"
                                        if gloss:
                                            display += f" ({gloss})"
                                        if note:
                                            display += f" *({note})*"
                                        st.markdown(display)
                                    else:
                                        st.markdown(f"- {target}")
                    else:
                        st.info("No relations defined for this word yet.")

                with tab2:
                    st.markdown("### OCM Cultural Classification (eHRAF 2021)")

                    # Get OCM codes from multiple sources
                    word_ocm_codes = bashkir_to_ocm.get(word_data['bashkir'], [])
                    cultural_context = word_data.get('cultural_context', {})
                    embedded_ocm_codes = cultural_context.get('ocm_codes', [])

                    all_codes = list(set([str(c) for c in word_ocm_codes + embedded_ocm_codes]))

                    if all_codes:
                        for code in all_codes:
                            label = ocm_labels.get(str(code), f"Category {code}")
                            st.markdown(f"- **OCM {code}**: {label}")
                    else:
                        st.info("No OCM codes assigned to this word yet.")

                    # Cultural significance
                    if cultural_context.get('significance'):
                        st.markdown("### Cultural Significance")
                        st.markdown(f"_{cultural_context['significance']}_")

                with tab3:
                    st.markdown("### Etymology")

                    bashkortnet = word_data.get('bashkortnet', {})
                    etymology = bashkortnet.get('etymology', {})

                    if etymology:
                        proto = etymology.get('proto_form', '')
                        note = etymology.get('note', '')
                        if proto:
                            st.markdown(f"**Proto-form:** {proto}")
                        if note:
                            st.markdown(f"**Note:** {note}")
                    else:
                        st.info("No etymology information available.")

                    # Memory palace info
                    memory_palace = word_data.get('memory_palace', {})
                    if memory_palace:
                        st.markdown("### Memory Palace")
                        st.write(f"🐦 Bird: {memory_palace.get('bird', 'N/A')}")
                        st.write(f"📍 Locus: {memory_palace.get('locus', 'N/A')}")

# === PAGE: CULTURAL CONTEXT (Enhanced with OCM) ===
elif "Cultural Context" in selected_page:
    st.title("📖 Cultural Context")
    st.markdown("*Understand the anthropological depth behind each word with eHRAF 2021 OCM classifications.*")

    # Load OCM data
    ocm_data = load_ocm_mapping()
    ocm_labels = ocm_data.get('ocm_labels', {})
    bashkir_to_ocm = ocm_data.get('bashkir_to_ocm', {})
    thematic_groups = ocm_data.get('thematic_groups', {})

    # Truth Unveiled toggle
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔓 Truth Unveiled")
    st.session_state.truth_unveiled = st.sidebar.toggle(
        "Show sensitive sources",
        value=st.session_state.truth_unveiled,
        help="Enable to see academic sources that may be politically sensitive"
    )

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Browse by Word", "📊 Browse by OCM", "🎨 Thematic Groups"])

    with tab1:
        # Word selection
        search_word = st.selectbox(
            "Select a word:",
            [w['bashkir'] for w in words_data],
            format_func=lambda x: f"{x} ({next((w['english'] for w in words_data if w['bashkir'] == x), '?')})"
        )

        if search_word:
            word_data = next((w for w in words_data if w['bashkir'] == search_word), None)

            if word_data:
                st.markdown(f"## {word_data['bashkir']} â€” {word_data['english']}")

                cultural = word_data.get('cultural_context', {})

                # OCM codes
                word_ocm_codes = bashkir_to_ocm.get(word_data['bashkir'], [])
                embedded_ocm_codes = cultural.get('ocm_codes', [])
                all_codes = list(set([str(c) for c in word_ocm_codes + embedded_ocm_codes]))

                if all_codes:
                    st.markdown("### 🏷️ OCM Categories (eHRAF 2021)")
                    for code in all_codes:
                        label = ocm_labels.get(str(code), f"Category {code}")
                        st.markdown(f"- **{code}**: {label}")

                # Significance
                significance = cultural.get('significance', '')
                if significance:
                    st.markdown("### 📜 Cultural Significance")
                    st.markdown(f"""
                    <div class="meditation-box">
                    {significance}
                    </div>
                    """, unsafe_allow_html=True)

                # Sources
                sources = cultural.get('sources', [])
                if sources:
                    st.markdown("### 📚 Sources")
                    for source in sources:
                        if isinstance(source, dict):
                            st.markdown(f"- {source.get('author', '')} ({source.get('year', '')}). *{source.get('title', '')}*")
                        else:
                            st.markdown(f"- {source}")

                # Sensitivity warning
                sensitivity = cultural.get('sensitivity', {})
                if sensitivity.get('has_sensitive_context') and st.session_state.truth_unveiled:
                    st.markdown("### âš ️ Sensitivity Context")
                    st.warning(sensitivity.get('note', 'This topic has sensitive political context.'))

    with tab2:
        st.markdown("### Browse by OCM Category")
        st.markdown("*Explore words organized by anthropological classification*")

        # Get unique OCM codes from all words
        all_ocm_codes_list = []
        for word in words_data:
            cultural = word.get('cultural_context', {})
            codes = cultural.get('ocm_codes', [])
            all_ocm_codes_list.extend([str(c) for c in codes])

        unique_codes = sorted(set(all_ocm_codes_list))

        if unique_codes:
            selected_code = st.selectbox(
                "Select OCM Category:",
                unique_codes,
                format_func=lambda x: f"{x}: {ocm_labels.get(x, 'Unknown')}"
            )

            if selected_code:
                st.markdown(f"### {ocm_labels.get(selected_code, f'Category {selected_code}')}")

                # Find words with this OCM code
                matching_words = [
                    w for w in words_data
                    if selected_code in [str(c) for c in w.get('cultural_context', {}).get('ocm_codes', [])]
                ]

                if matching_words:
                    for word in matching_words:
                        st.markdown(f"- **{word['bashkir']}** ({word['english']})")
                else:
                    st.info("No words found with this OCM code.")
        else:
            st.info("No OCM codes found in vocabulary data.")

    with tab3:
        st.markdown("### Thematic Groups")
        st.markdown("*Words organized by cultural and linguistic themes*")

        if thematic_groups:
            for theme_name, theme_data in thematic_groups.items():
                display_name = theme_name.replace('_', ' ').title()
                theme_ocm_codes = theme_data.get('ocm_codes', [])
                theme_words = theme_data.get('words', [])

                with st.expander(f"🎨 {display_name}"):
                    if theme_ocm_codes:
                        st.markdown("**OCM Codes:**")
                        code_labels = [f"{c}: {ocm_labels.get(c, 'Unknown')}" for c in theme_ocm_codes]
                        st.write(", ".join(code_labels))

                    if theme_words:
                        st.markdown("**Words:**")
                        word_displays = []
                        for bword in theme_words:
                            word_info = next((w for w in words_data if w['bashkir'] == bword), None)
                            if word_info:
                                word_displays.append(f"**{bword}** ({word_info['english']})")
                            else:
                                word_displays.append(f"**{bword}**")
                        st.markdown(" | ".join(word_displays))
        else:
            st.info("No thematic groups defined yet.")

# === PAGE: TRUTH UNVEILED ===
elif "Truth Unveiled" in selected_page:
    st.title("🌟 Truth Unveiled â€” ÐÐ»Ñ‚Ñ‹Ð½ Ð¯Ò¡Ñ‚Ñ‹")
    st.markdown("*The Golden Light: Proverbs, Timeline, and the Deeper Knowledge*")

    # Load data from both sources for comprehensive coverage
    epic_data = load_ural_batyr_epic()
    golden_data = load_golden_light_data()

    # Use golden_light_data.json for proverbs and timeline (more comprehensive)
    proverbs = golden_data.get('proverbs', epic_data.get('proverbs', []))
    timeline = golden_data.get('timeline', epic_data.get('timeline', []))
    cultural_facts = epic_data.get('cultural_facts', [])

    # Legacy proverb from golden_light_data
    gl_info = golden_data.get('golden_light', {})
    legacy_proverb = gl_info.get('legacy_proverb', epic_data.get('legacy_proverb', {}))

    # The Golden Light Introduction
    st.markdown(f"""
    <div class="meditation-box" style="border: 3px solid #d4af37; border-left: 5px solid #d4af37;">
        <h3 style="color: #d4af37; text-align: center;">✨ ÐÐ»Ñ‚Ñ‹Ð½ Ð¯Ò¡Ñ‚Ñ‹ â€” Golden Light ✨</h3>
        <p style="text-align: center; font-size: 1.2em; margin: 15px 0;">
            <strong>"{legacy_proverb.get('bashkir', '')}"</strong>
        </p>
        <p style="text-align: center; font-style: italic;">
            "{legacy_proverb.get('english', '')}"
        </p>
        <p style="text-align: center; color: #666; font-size: 0.9em;">
            [{legacy_proverb.get('phonetic', '')}]
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    *This is the anchoring proverb of Golden Lightâ€”the Ural-Batyr legacy. It reflects the hero's
    ultimate sacrifice and the enduring Bashkir spirit. When Ural poured the waters of life for
    all rather than drinking them himself, he demonstrated this truth: we live on through what we give.*
    """)

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📜 Proverbs", "â³ Timeline", "📍️ Cultural Facts", "🔥 The Duality"])

    with tab1:
        st.markdown("### 📜 Bashkir Proverbs â€” ÐœÓ™Ò¡Ó™Ð»Ð´Ó™Ñ€")
        st.markdown("*Wisdom passed down through generations*")

        # Filter by category
        categories = list(set([p.get('category', 'General') for p in proverbs]))
        selected_category = st.selectbox("Filter by theme:", ['All'] + categories)

        filtered_proverbs = proverbs if selected_category == 'All' else [p for p in proverbs if p.get('category') == selected_category]

        for proverb in filtered_proverbs:
            st.markdown(f"""
            <div class="word-card" style="border-left: 5px solid #d4af37;">
                <span style="background: #d4af37; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">
                    {proverb.get('category', 'General')}
                </span>
                <p class="bashkir-text" style="margin-top: 10px;">{proverb.get('bashkir', '')}</p>
                <p class="russian-text">🇷🇺 {proverb.get('russian', '')}</p>
                <p class="english-text">🇬🇧 {proverb.get('english', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### â³ Historical Timeline â€” Ð¢Ð°Ñ€Ð¸Ñ… ÑŽÐ»Ñ‹")
        st.markdown("*Key moments in Bashkir history*")

        # Timeline visualization
        for idx, event in enumerate(timeline):
            year = event.get('year', '')
            desc = event.get('event', '')

            st.markdown(f"""
            <div style="display: flex; margin: 10px 0;">
                <div style="min-width: 80px; padding: 8px; background: #0066B3; color: white; border-radius: 8px; text-align: center; font-weight: bold;">
                    {year}
                </div>
                <div style="flex: 1; padding: 8px 15px; background: #e6f2ff; border-radius: 8px; margin-left: 10px; border-left: 3px solid #00AF66;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📍️ Cultural Facts â€” ÐœÓ™Ò™Ó™Ð½Ð¸Ó™Ñ‚")
        st.markdown("*Deep knowledge of Bashkir heritage*")

        # Filter by category
        fact_categories = list(set([f.get('category', 'general') for f in cultural_facts]))
        selected_fact_category = st.selectbox("Filter facts by:", ['All'] + fact_categories, key="fact_filter")

        filtered_facts = cultural_facts if selected_fact_category == 'All' else [f for f in cultural_facts if f.get('category') == selected_fact_category]

        for fact in filtered_facts:
            cat_colors = {'history': '#0066B3', 'culture': '#00AF66', 'geography': '#d4af37', 'language': '#cc3333'}
            color = cat_colors.get(fact.get('category', ''), '#666')

            st.markdown(f"""
            <div class="word-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">
                        {fact.get('category', 'general').upper()}
                    </span>
                    <span style="color: #666; font-size: 0.9em;">{fact.get('year', '')}</span>
                </div>
                <h4 style="color: #00AF66; margin: 5px 0;">{fact.get('title', '')}</h4>
                <p style="color: #004d00;">{fact.get('content', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 🔥 The Duality: Ural and Shulgen")
        st.markdown("*Understanding the twin paths of the Bashkir soul*")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="bird-card eagle-card" style="min-height: 350px;">
                <h3>📍️ URAL</h3>
                <p><strong>The Path of Light</strong></p>
                <hr>
                <p><strong>Choice:</strong> Sacrifice for all</p>
                <p><strong>Symbol:</strong> The Mountains</p>
                <p><strong>Legacy:</strong> Eternal protection</p>
                <hr>
                <p style="font-style: italic;">
                "I am not dyingâ€”I am becoming something greater. These mountains will be my body,
                and I will protect our people forever."
                </p>
                <hr>
                <p><strong>Lesson:</strong> True immortality comes through selfless action.
                The hero who gives everything gains everything.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="bird-card crow-card" style="min-height: 350px;">
                <h3>🌊 SHULGEN</h3>
                <p><strong>The Path of Depth</strong></p>
                <hr>
                <p><strong>Choice:</strong> Power over love</p>
                <p><strong>Symbol:</strong> The Cave</p>
                <p><strong>Legacy:</strong> Guardian of memory</p>
                <hr>
                <p style="font-style: italic;">
                "Brother... I see now what I became. Forgive me..."
                â€” Shulgen's final words
                </p>
                <hr>
                <p><strong>Redemption:</strong> Shulgan-Tash cave holds 16,000-year-old paintings.
                The one who fell guards the ancient memory in darkness.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        ---
        ### The Unity of Opposites

        In Bashkir philosophy, Ural and Shulgen are not simply good and evilâ€”they are
        complementary forces. The mountains rise into light; the caves descend into memory.
        Both are necessary.

        **For twins:** You carry both paths within you. One may be called to shine in the world;
        another may be called to preserve and protect from the depths. Neither path is lesser.
        Together, you form something completeâ€”like the mountains and the caves of Bashkortostan.

        *"Ð‘Ð°Ñ‚Ñ‹Ñ€ Ò¯Ð»Ð¼Ó™Ð¹, Ð°Ñ‚Ñ‹ Ò¡Ð°Ð»Ð°"* â€” The hero doesn't die, his name remains.
        """)

        st.markdown(f"""
        <div class="meditation-box" style="text-align: center; margin-top: 20px;">
            <p style="font-size: 1.1em;">
                📍️ The Ural Mountains are Ural-Batyr's body.<br>
                🌊 Shulgan-Tash Cave holds Shulgen's memory.<br>
                🌟 Together, they are Bashkortostan.
            </p>
        </div>
        """, unsafe_allow_html=True)

# === PAGE: SACRED PRACTICE (NEW - Theological Framework) ===
elif "Sacred Practice" in selected_page:
    st.title("🧘 Sacred Practice")
    st.markdown("*Contemplative exercises for language learning transformation*")
    
    st.markdown("""
    <div class="meditation-box">
        <em>"May the remembrance of Jesus unite with your breathing."</em>
        <br>— Saint John of the Ladder
        <br><br>
        <em>"The prayer alone filled my consciousness."</em>
        <br>— The Way of a Pilgrim
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different practices
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌬️ Breathing Practice", 
        "🛡️ Logismoi Awareness", 
        "🤫 The Silence",
        "📿 Self-Acting Progress"
    ])
    
    with tab1:
        st.markdown("### 🌬️ Breathing Practice")
        st.markdown("""
        *Adapted from the Hesychastic tradition of the Way of a Pilgrim*
        
        > "Sit down alone and in silence. Lower your head, shut your eyes, 
        > breathe out gently, and imagine yourself looking into your own heart."
        > — Saint Simeon the New Theologian
        
        **The Practice:**
        1. **Inhale (4 counts)**: See the Bashkir word in your mind
        2. **Hold (2 counts)**: Feel its meaning settle in your heart  
        3. **Exhale (4 counts)**: Speak the word aloud
        4. **Rest (2 counts)**: Let it settle like snow on Yamantau
        """)
        
        # Word selector for practice
        words_data = load_words()
        word_list = list(words_data.keys())
        
        selected_word = st.selectbox("Choose a word to practice:", word_list[:20])
        
        if selected_word and selected_word in words_data:
            word = words_data[selected_word]
            
            st.markdown(f"""
            <div class="word-card" style="text-align: center;">
                <p class="bashkir-text" style="font-size: 2.5em;">{word.get('bashkir', selected_word)}</p>
                <p class="english-text">{word.get('english', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🌬️ Begin 30-second breathing practice", key="breathing_btn"):
                progress_bar = st.progress(0)
                status = st.empty()
                
                phases = [
                    ("Inhale... see the word", 4),
                    ("Hold... feel its meaning", 2),
                    ("Exhale... speak it aloud", 4),
                    ("Rest... let it settle", 2)
                ]
                
                for cycle in range(2):  # 2 cycles = 24 seconds
                    for phase_name, duration in phases:
                        status.markdown(f"**{phase_name}**")
                        for i in range(duration):
                            time.sleep(1)
                            total_progress = (cycle * 12 + sum(p[1] for p in phases[:phases.index((phase_name, duration))]) + i + 1) / 24
                            progress_bar.progress(min(total_progress, 1.0))
                
                st.session_state.breathing_completed = True
                st.session_state.sacred_practice_count += 1
                st.success("✨ Practice complete. The word is settling into your heart.")
                st.balloons()
    
    with tab2:
        st.markdown("### 🛡️ Logismoi Awareness")
        st.markdown("""
        *From the Athonite tradition of Father Maximos*
        
        > "Logismoi are like airplanes. If there's no airport, they can't land.
        > If we don't allow a logismos to land inside the depths of our hearts
        > and minds, even if it bothers us, we should never be afraid of it."
        > — Father Maximos
        
        **What are Logismoi?**
        
        Logismoi are thoughts of special quality and power—not ordinary thoughts 
        but penetrating forces that can distract us from our practice. In language 
        learning, they are the distractions that pull us away from focused study.
        
        **The Five Stages of a Logismos:**
        1. **Assault**: The thought first attacks ("Check your phone")
        2. **Interaction**: You begin to engage with it
        3. **Consent**: You accept the distraction
        4. **Captivity**: The distraction takes residence
        5. **Passion**: It becomes habitual
        
        **Combat Method**: Notice → Refuse → Return to practice
        """)
        
        st.markdown("---")
        st.markdown("#### 📝 Track Your Logismoi")
        
        common_distractions = [
            "Phone/notifications",
            "Other tasks calling",
            "Feeling overwhelmed",
            "Boredom",
            "Self-doubt ('This is too hard')",
            "Perfectionism ('I need to understand everything')",
            "Physical discomfort",
            "External noise",
            "Other"
        ]
        
        distraction = st.selectbox("What distracted you today?", common_distractions)
        notes = st.text_input("Notes (optional):")
        
        if st.button("Record Logismos"):
            st.session_state.logismoi_journal.append({
                'date': datetime.now().isoformat(),
                'distraction': distraction,
                'notes': notes
            })
            st.success("Recorded. Awareness is the first step to freedom.")
        
        if st.session_state.logismoi_journal:
            st.markdown("#### Your Logismoi Patterns")
            from collections import Counter
            patterns = Counter([l['distraction'] for l in st.session_state.logismoi_journal])
            for distraction, count in patterns.most_common(5):
                st.markdown(f"- **{distraction}**: {count} times")
    
    with tab3:
        st.markdown("### 🤫 The Silence")
        st.markdown("""
        *From Wittgenstein and the apophatic tradition*
        
        > "Whereof one cannot speak, thereof one must be silent."
        > — Wittgenstein, Tractatus 7
        
        > "There are indeed, things that are inexpressible. 
        > They show themselves. That is the mystical."
        > — Wittgenstein, Tractatus 6.522
        
        **The Practice of Unknowing**
        
        Some things cannot be learned through words alone. The deepest knowledge 
        of a language comes not from definitions but from *dwelling* in it.
        
        Tyler identifies six "strategies of unknowing":
        1. Direction of locution (speaking to oneself)
        2. Contradiction (holding paradoxes)
        3. Avoiding conclusions (remaining open)
        4. Disorientation (breaking expectations)
        5. Humor (lightness amid depth)
        6. Ordinary speech (simplicity)
        
        **Contemplative Silence Practice**
        
        Sit for 2 minutes in silence. Let Bashkir words arise naturally.
        Do not force them. Simply be present.
        """)
        
        if st.button("🤫 Begin 2-minute silence"):
            progress_bar = st.progress(0)
            status = st.empty()
            status.markdown("*Enter the silence...*")
            
            for i in range(120):
                time.sleep(1)
                progress_bar.progress((i + 1) / 120)
                if i == 30:
                    status.markdown("*Let thoughts pass like clouds...*")
                elif i == 60:
                    status.markdown("*If a Bashkir word arises, welcome it...*")
                elif i == 90:
                    status.markdown("*Dwell in the space between words...*")
            
            status.markdown("*The silence continues within you.*")
            st.success("✨ Practice complete.")
    
    with tab4:
        st.markdown("### 📿 Self-Acting Progress")
        st.markdown("""
        *From the Way of a Pilgrim*
        
        The Pilgrim describes a progression in prayer practice:
        
        | Stage | Prayers/Day | Experience |
        |-------|-------------|------------|
        | Beginning | 3,000 | "Effort required" |
        | Ease | 6,000 | "Became easy and pleasant" |
        | Delight | 12,000 | "Joy and delight" |
        | Self-Acting | Continuous | "The prayer filled my consciousness" |
        
        **Applied to Language Learning:**
        
        | Stage | Words Mastered | Reviews | Experience |
        |-------|----------------|---------|------------|
        | Beginning | 0-50 | 0-100 | Conscious effort |
        | Ease | 50-200 | 100-500 | Growing comfort |
        | Delight | 200-500 | 500-2000 | Joy in simple sentences |
        | Self-Acting | 500+ | 2000+ | Bashkir arises naturally |
        """)
        
        # Calculate current stage
        words_mastered = len(st.session_state.learned_words)
        total_reviews = st.session_state.total_reviews_completed
        
        if words_mastered < 50:
            stage = "🌱 Beginning"
            stage_desc = "Each word requires conscious effort. This is normal."
            progress_in_stage = words_mastered / 50
        elif words_mastered < 200:
            stage = "🌿 Ease"
            stage_desc = "Words are becoming familiar. Practice is easier."
            progress_in_stage = (words_mastered - 50) / 150
        elif words_mastered < 500:
            stage = "🌳 Delight"
            stage_desc = "You find joy in simple sentences. Keep going!"
            progress_in_stage = (words_mastered - 200) / 300
        else:
            stage = "🌟 Self-Acting"
            stage_desc = "Bashkir is becoming part of you."
            progress_in_stage = 1.0
        
        st.markdown(f"""
        <div class="stat-box">
            <h3>{stage}</h3>
            <p>{stage_desc}</p>
            <p><strong>Words Mastered:</strong> {words_mastered}</p>
            <p><strong>Total Reviews:</strong> {total_reviews}</p>
            <p><strong>Sacred Practices:</strong> {st.session_state.sacred_practice_count}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(progress_in_stage)
        
        st.markdown("""
        ---
        > "I spent the entire summer continuously repeating the Jesus Prayer... 
        > all thoughts seemed to vanish on their own... without any effort."
        > — The Pilgrim
        
        *Your goal: When Bashkir words arise naturally, without effort, 
        you will have reached self-acting fluency.*
        """)

# === PAGE: YOUR JOURNEY (NEW - Pedagogical Framework) ===
elif "Your Journey" in selected_page:
    st.title("📈 Your Journey")
    st.markdown("*Track your progression through the stages of learning*")
    
    st.markdown("""
    <div class="meditation-box">
        <em>"The question is, under what categories one wants to contemplate 
        the entire world and would oneself live."</em>
        <br>— Kierkegaard, Either/Or
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    words_learned = len(st.session_state.learned_words)
    sentences_created = len(st.session_state.saved_sentences)
    reviews_done = st.session_state.total_reviews_completed
    truth_unveiled = st.session_state.truth_unveiled
    reflections = len(st.session_state.reflection_journal)
    
    # Determine current stage (Kierkegaard)
    aesthetic_score = min(100, (words_learned * 2) + (sentences_created * 5))
    ethical_score = min(100, (reviews_done // 5) + (st.session_state.days_active * 3))
    religious_score = min(100, (50 if truth_unveiled else 0) + (reflections * 10) + (words_learned // 5))
    
    if religious_score >= 50:
        current_stage = "🟣 Religious (Identity Seeker)"
        stage_quote = "Faith is: that the self in being itself and in wanting to be itself is grounded transparently in God."
    elif ethical_score >= 50:
        current_stage = "🟡 Ethical (Committed Learner)"
        stage_quote = "The act of choosing is a literal and strict expression of the ethical."
    else:
        current_stage = "🔵 Aesthetic (Curious Explorer)"
        stage_quote = "The aesthetic factor in a person is that by which he is immediately what he is."
    
    # Display current stage
    st.markdown(f"### Current Stage: {current_stage}")
    st.markdown(f"*\"{stage_quote}\"* — Kierkegaard")
    
    st.markdown("---")
    
    # Three stages progress
    st.markdown("### The Three Stages")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="bird-card eagle-card">
            <h4>🔵 AESTHETIC</h4>
            <p><em>Curiosity & Exploration</em></p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(aesthetic_score / 100)
        st.markdown(f"**{aesthetic_score}%** complete")
        st.markdown("""
        - Browse the Palace ✓
        - Explore Four Birds ✓
        - Listen to audio ✓
        """)
    
    with col2:
        st.markdown("""
        <div class="bird-card ringdove-card">
            <h4>🟡 ETHICAL</h4>
            <p><em>Commitment & Duty</em></p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(ethical_score / 100)
        st.markdown(f"**{ethical_score}%** complete")
        checkmarks = [
            ("Daily practice", reviews_done >= 50),
            ("100+ reviews", reviews_done >= 100),
            ("Build sentences", sentences_created >= 5)
        ]
        for task, done in checkmarks:
            st.markdown(f"- {task} {'✓' if done else '○'}")
    
    with col3:
        st.markdown("""
        <div class="bird-card anqa-card">
            <h4>🟣 RELIGIOUS</h4>
            <p><em>Identity & Transformation</em></p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(religious_score / 100)
        st.markdown(f"**{religious_score}%** complete")
        checkmarks = [
            ("Truth Unveiled", truth_unveiled),
            ("Reflect on journey", reflections >= 3),
            ("500+ words", words_learned >= 500)
        ]
        for task, done in checkmarks:
            st.markdown(f"- {task} {'✓' if done else '○'}")
    
    st.markdown("---")
    
    # Reflection Journal
    st.markdown("### 📝 Reflection Journal")
    st.markdown("*\"Choose, and you shall see what validity there is in it.\"* — Kierkegaard")
    
    prompts = [
        "Why are you learning Bashkir? What do you hope to become?",
        "What word has surprised you or moved you recently?",
        "What is the hardest part of this journey? What keeps you going?",
        "How has your understanding of Bashkir culture changed?",
        "If you could speak Bashkir fluently tomorrow, what would you do first?",
        "What does 'Батыр үлмәй, аты қала' (The hero doesn't die, his name remains) mean to you?",
        "Describe a moment when a Bashkir word suddenly 'clicked' for you.",
        "What would you tell someone just beginning this journey?"
    ]
    
    today_prompt = prompts[datetime.now().day % len(prompts)]
    
    st.markdown(f"**Today's Prompt:**")
    st.markdown(f"*{today_prompt}*")
    
    reflection_text = st.text_area("Your reflection:", key="journey_reflection", height=150)
    
    if st.button("Save Reflection"):
        if reflection_text.strip():
            st.session_state.reflection_journal.append({
                'date': datetime.now().isoformat(),
                'prompt': today_prompt,
                'reflection': reflection_text
            })
            st.success("Reflection saved!")
        else:
            st.warning("Please write something before saving.")
    
    # Show previous reflections
    if st.session_state.reflection_journal:
        with st.expander(f"📖 Previous Reflections ({len(st.session_state.reflection_journal)})"):
            for entry in reversed(st.session_state.reflection_journal[-10:]):
                st.markdown(f"**{entry['date'][:10]}** — *{entry['prompt']}*")
                st.markdown(f"> {entry['reflection']}")
                st.markdown("---")
    
    st.markdown("---")
    
    # Milestones
    st.markdown("### 🎯 Milestones")
    
    milestones = st.session_state.milestones
    
    # Check and update milestones
    if words_learned >= 1 and not milestones.get('first_word'):
        milestones['first_word'] = datetime.now().isoformat()
    if sentences_created >= 1 and not milestones.get('first_sentence'):
        milestones['first_sentence'] = datetime.now().isoformat()
    if truth_unveiled and not milestones.get('truth_unveiled_date'):
        milestones['truth_unveiled_date'] = datetime.now().isoformat()
    if words_learned >= 50 and not milestones.get('fifty_words'):
        milestones['fifty_words'] = datetime.now().isoformat()
    if words_learned >= 100 and not milestones.get('hundred_words'):
        milestones['hundred_words'] = datetime.now().isoformat()
    
    milestone_display = [
        ("🌱 First word learned", milestones.get('first_word')),
        ("✏️ First sentence built", milestones.get('first_sentence')),
        ("🌟 Truth Unveiled activated", milestones.get('truth_unveiled_date')),
        ("🌿 50 words mastered", milestones.get('fifty_words')),
        ("🌳 100 words mastered", milestones.get('hundred_words')),
        ("🏔️ 200 words mastered", milestones.get('two_hundred_words')),
        ("⭐ 500 words mastered", milestones.get('five_hundred_words')),
    ]
    
    for name, date in milestone_display:
        if date:
            st.markdown(f"✅ **{name}** — {date[:10]}")
        else:
            st.markdown(f"⬜ {name} — *not yet*")

# === PAGE: THE ELEVEN PILLARS (NEW - Educational Transparency) ===
elif "Eleven Pillars" in selected_page:
    st.title("📚 The Eleven Pillars")
    st.markdown("*The epistemological foundation of the Bashkir Memory Palace*")
    
    st.markdown("""
    <div class="meditation-box">
        <em>"This is not a random library but a blueprint for ethical, rigorous, 
        responsive knowledge preservation."</em>
        <br>— The Epistemology Blueprint
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    This app integrates wisdom from **14 foundational texts** organized into 
    a seven-layer epistemological system. This page explains the theoretical 
    foundations so you understand not just *what* you're learning, but *how* 
    the system is designed to help you learn.
    """)
    
    st.markdown("---")
    st.markdown("### The Seven-Layer Architecture")
    
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │  Layer 7: IMAGINATIVE EMBODIMENT (Le Guin)                  │
    │           → The Memory Palace itself: maps, journeys        │
    ├─────────────────────────────────────────────────────────────┤
    │  Layer 6: CULTURAL PATHOLOGY DIAGNOSIS (Coombes/Dalrymple)  │
    │           → What NOT to do; why Bashkir preservation matters│
    ├─────────────────────────────────────────────────────────────┤
    │  Layer 5: LIFEWORLD ANCHORING (Eriksen, Kirsch)             │
    │           → Bashkir communities, indigenous self-determination│
    ├─────────────────────────────────────────────────────────────┤
    │  Layer 4: MYSTICAL & INEFFABLE (Tyler, Wittgenstein, Ibn Arabi)│
    │           → What can only be SHOWN, not said                │
    ├─────────────────────────────────────────────────────────────┤
    │  Layer 3: EXISTENTIAL COMMITMENT (Kierkegaard)              │
    │           → Knowledge is LIVED, not just understood         │
    ├─────────────────────────────────────────────────────────────┤
    │  Layer 2: PHILOSOPHICAL FOUNDATIONS (Plato)                 │
    │           → Archetypal questions; dialogical inquiry        │
    ├─────────────────────────────────────────────────────────────┤
    │  Layer 1: LOGICAL CRITERIA (Hurley, Wittgenstein)           │
    │           → What counts as valid knowledge; limits of language│
    └─────────────────────────────────────────────────────────────┘
    ```
    """)
    
    st.markdown("---")
    st.markdown("### The Eleven Works")
    
    works = [
        {
            "title": "A Concise Introduction to Logic",
            "author": "Patrick Hurley",
            "layer": "Layer 1: Logical Criteria",
            "icon": "🔢",
            "function": "Establishes what counts as valid reasoning and good arguments.",
            "key_concept": "Validity, soundness, fallacies, probability, causality"
        },
        {
            "title": "Tractatus Logico-Philosophicus",
            "author": "Ludwig Wittgenstein",
            "layer": "Layer 1: Logical Criteria",
            "icon": "🔇",
            "function": "Defines the limits of what language can express.",
            "key_concept": "\"Whereof one cannot speak, thereof one must be silent.\""
        },
        {
            "title": "Complete Works (The Republic, etc.)",
            "author": "Plato",
            "layer": "Layer 2: Philosophical Foundations",
            "icon": "💭",
            "function": "Provides archetypal questions and the dialogical method.",
            "key_concept": "Forms, the soul, justice, the Socratic method"
        },
        {
            "title": "Either/Or",
            "author": "Søren Kierkegaard",
            "layer": "Layer 3: Existential Commitment",
            "icon": "⚖️",
            "function": "Models how meaning is lived through choice.",
            "key_concept": "Aesthetic, ethical, and religious stages; the leap"
        },
        {
            "title": "Fear and Trembling / Sickness Unto Death",
            "author": "Søren Kierkegaard",
            "layer": "Layer 3: Existential Commitment",
            "icon": "🙏",
            "function": "Explores faith as existential risk and despair as spiritual sickness.",
            "key_concept": "The Knight of Faith, the absurd, despair"
        },
        {
            "title": "The Return to the Mystical",
            "author": "Peter Tyler",
            "layer": "Layer 4: Mystical & Ineffable",
            "icon": "✨",
            "function": "Operationalizes Wittgenstein's saying/showing distinction in mystical practice.",
            "key_concept": "Strategies of unknowing, performative discourse, affective transformation"
        },
        {
            "title": "Small Places, Large Issues",
            "author": "Thomas Hylland Eriksen",
            "layer": "Layer 5: Lifeworld Anchoring",
            "icon": "🌍",
            "function": "Grounds knowledge in comparative cultural study.",
            "key_concept": "Ethnography, culture, power, globalization, decolonization"
        },
        {
            "title": "Engaged Anthropology",
            "author": "Stuart Kirsch",
            "layer": "Layer 5: Lifeworld Anchoring",
            "icon": "🤝",
            "function": "Models anthropology as advocacy and political practice.",
            "key_concept": "Indigenous rights, community protocols, self-determination"
        },
        {
            "title": "What is Wrong with Us?",
            "author": "Coombes & Dalrymple",
            "layer": "Layer 6: Cultural Pathology",
            "icon": "⚠️",
            "function": "Diagnoses cultural failures and motivates better systems.",
            "key_concept": "Loss of scale, architectural hubris, ethical design"
        },
        {
            "title": "Aardzee / The Left Hand of Darkness",
            "author": "Ursula K. Le Guin",
            "layer": "Layer 7: Imaginative Embodiment",
            "icon": "🗺️",
            "function": "Demonstrates how knowledge can be embodied in navigable worlds.",
            "key_concept": "World-building, maps, thought experiments, multiple perspectives"
        },
        {
            "title": "A Companion to Kierkegaard",
            "author": "Jon Stewart (ed.)",
            "layer": "Layer 3: Existential Commitment",
            "icon": "📖",
            "function": "Scholarly integration of Kierkegaard into modern thought.",
            "key_concept": "Immortality as task, faith as second immediacy"
        }
    ]
    
    for work in works:
        with st.expander(f"{work['icon']} {work['title']} — {work['author']}"):
            st.markdown(f"**Layer:** {work['layer']}")
            st.markdown(f"**Function:** {work['function']}")
            st.markdown(f"**Key Concept:** *{work['key_concept']}*")
    
    st.markdown("---")
    st.markdown("### The Three Mystical Texts (Additional)")
    
    mystical_texts = [
        {
            "title": "The Way of a Pilgrim",
            "tradition": "Hesychasm (Russian Orthodox)",
            "icon": "🚶",
            "contribution": "The Jesus Prayer method, self-acting prayer, breathing practices"
        },
        {
            "title": "The Mountain of Silence",
            "tradition": "Athonite Christianity",
            "icon": "🏔️",
            "contribution": "Father Maximos teachings, Theosis, logismoi, eldership"
        },
        {
            "title": "Secrets of Voyaging (Kitāb al-Isfār)",
            "tradition": "Sufism (Ibn Arabi)",
            "icon": "🕊️",
            "contribution": "The Four Birds framework, kashf (unveiling), spiritual voyaging"
        }
    ]
    
    for text in mystical_texts:
        with st.expander(f"{text['icon']} {text['title']} — {text['tradition']}"):
            st.markdown(f"**Contribution:** {text['contribution']}")
    
    st.markdown("---")
    st.markdown("### How They Work Together")
    
    st.markdown("""
    The 14 texts form a **mutually constraining system**:
    
    1. **Logic (Hurley, Wittgenstein)** provides precision and marks where language fails
    2. **Philosophy (Plato, Kierkegaard)** poses eternal questions and demands lived commitment
    3. **Mysticism (Tyler, Ibn Arabi, Pilgrim, Maximos)** engages the transcendent through practice
    4. **Anthropology (Eriksen, Kirsch)** grounds everything in actual communities
    5. **Ethics (Coombes/Dalrymple)** diagnoses failure and motivates better design
    6. **Imagination (Le Guin)** embodies it all in navigable worlds
    
    **The result is a learning system that is:**
    - ✅ Philosophically rigorous
    - ✅ Culturally respectful
    - ✅ Pedagogically transformative
    - ✅ Alert to power and pathology
    - ✅ Open to the transcendent
    - ✅ Navigable and alive
    """)
    
    st.markdown("""
    <div class="meditation-box" style="text-align: center;">
        <p><em>"The journey made within yourself leads to yourself."</em></p>
        <p>— Ibn Arabi</p>
    </div>
    """, unsafe_allow_html=True)

# === PAGE: SETTINGS ===
elif "Settings" in selected_page:
    st.title("⚙️ Settings")

    st.markdown("### 🎨 Display Settings")

    st.markdown("### 🔊 Audio Settings")
    st.checkbox("Enable audio playback", value=True)
    st.slider("Audio speed", 0.5, 1.5, 1.0)

    st.markdown("### 📊 Learning Settings")
    st.number_input("New words per session", 1, 20, 5)
    st.number_input("Review words per session", 5, 50, 20)

    st.markdown("### 🔄 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Progress"):
            progress_data = {
                'learned_words': list(st.session_state.learned_words),
                'saved_sentences': st.session_state.saved_sentences,
                'srs_data': st.session_state.srs_data
            }
            st.download_button(
                "Download JSON",
                json.dumps(progress_data, ensure_ascii=False, indent=2),
                "bashkir_progress.json",
                "application/json"
            )

    with col2:
        if st.button("Reset All Progress"):
            st.session_state.learned_words = set()
            st.session_state.review_queue = []
            st.session_state.saved_sentences = []
            st.session_state.srs_data = {}
            st.success("Progress reset!")
            st.rerun()

    # === NEW: Your Learning Stage Summary (Pedagogical Framework) ===
    st.markdown("---")
    st.markdown("### 🎯 Your Existential Stage")
    
    words_learned = len(st.session_state.learned_words)
    reviews_done = st.session_state.total_reviews_completed
    truth_unveiled = st.session_state.truth_unveiled
    reflections = len(st.session_state.reflection_journal)
    
    # Determine stage
    if words_learned >= 500 and truth_unveiled:
        stage = "🟣 Religious (Identity Seeker)"
        stage_desc = "You're making Bashkir part of who you are."
    elif words_learned >= 100 or reviews_done >= 200:
        stage = "🟡 Ethical (Committed Learner)"
        stage_desc = "You've chosen to commit. Daily practice is your path."
    else:
        stage = "🔵 Aesthetic (Curious Explorer)"
        stage_desc = "Exploration and curiosity drive you. Beautiful!"
    
    st.markdown(f"""
    <div class="stat-box" style="text-align: left;">
        <h3>{stage}</h3>
        <p>{stage_desc}</p>
        <hr style="border-color: #00AF66;">
        <p><strong>Words Learned:</strong> {words_learned}</p>
        <p><strong>Reviews Completed:</strong> {reviews_done}</p>
        <p><strong>Reflections Written:</strong> {reflections}</p>
        <p><strong>Truth Unveiled:</strong> {"✅ Yes" if truth_unveiled else "❌ Not yet"}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    **Bashkir Memory Palace** v3.0 — *The Eleven Pillars Edition*
    
    A transformative language learning application integrating:
    
    **🔢 Epistemological Framework:**
    - Wittgenstein's limits of language
    - Hurley's formal logic
    - Plato's dialogical inquiry
    
    **🙏 Theological Framework:**
    - Ibn Arabi's Four Birds (Secrets of Voyaging)
    - Hesychastic prayer practice (Way of a Pilgrim)
    - Athonite wisdom (Mountain of Silence)
    
    **⚖️ Existential Framework:**
    - Kierkegaard's three stages (Either/Or, Fear and Trembling)
    - Peter Tyler's mystical pedagogy
    
    **🤝 Anthropological Framework:**
    - Eriksen's comparative anthropology
    - Kirsch's engaged anthropology
    - OCM/eHRAF cultural classifications
    
    **🛠️ Technical Features:**
    - Memory Palace technique (Method of Loci)
    - Spaced Repetition (SM-2 algorithm)
    - BashkortNet semantic network
    - Three Eyes view modes
    - Breathing and contemplative practices
    
    ---
    
    **🤝 Our Commitment to the Bashkir Community:**
    
    *"Knowledge about others must be generated WITH them, not OF them."*  
    — Stuart Kirsch, Engaged Anthropology
    
    This app is developed with respect for Bashkir cultural sovereignty.
    We acknowledge that language preservation is a political act.
    
    ---
    
    *"The journey made within yourself leads to yourself."*  
    — Ibn Arabi, Secrets of Voyaging
    """)

# --- Footer with Rotating Quotes ---
# Select quote based on day of month
quotes = [
    ('"Voyaging has no end, for therein is the joy of the Real."', "Ibn Arabi"),
    ('"Whereof one cannot speak, thereof one must be silent."', "Wittgenstein"),
    ('"The prayer alone filled my consciousness."', "The Pilgrim"),
    ('"Choose, and you shall see what validity there is in it."', "Kierkegaard"),
    ('"Батыр үлмәй, аты қала — The hero does not die, his name remains."', "Bashkir Proverb"),
    ('"What is an Eleimon heart? A heart that burns for all creation."', "Saint Isaac"),
    ('"The journey made within yourself leads to yourself."', "Ibn Arabi"),
    ('"Draw your mind from your head into your heart."', "Gregory of Sinai"),
]

# Rotate based on day
quote_text, quote_author = quotes[datetime.now().day % len(quotes)]

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>🏰 Bashkir Memory Palace — <em>Secrets of Voyaging</em></p>
    <p>🦅 Eagle · 🐦‍⬛ Crow · 🔥🕊️ Anqa · 🕊️ Ringdove</p>
    <p style="margin-top: 15px;"><em>{quote_text}</em></p>
    <p style="font-size: 0.85em;">— {quote_author}</p>
</div>
""", unsafe_allow_html=True)
