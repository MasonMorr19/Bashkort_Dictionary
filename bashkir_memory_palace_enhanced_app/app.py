"""
🏰 Bashkir Memory Palace: Secrets of Voyaging
==============================================
A language learning app integrating Ibn Arabi's mystical framework,
memory palace techniques, and anthropological pedagogy.

The Four Birds guide your journey:
🦅 Eagle (First Intellect) - Civic knowledge at Ufa
🐦⬛ Crow (Universal Body) - Ancestral memory at Shulgan-Tash
🔥🕊️ Anqa (Prime Matter) - Transformation at Yamantau
🕊️ Ringdove (Universal Soul) - Daily life at Beloretsk & Bizhbulyak

Enhanced with retry logic, audio export, and OCM cultural classifications.
"""

import streamlit as st
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

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
st.sidebar.caption("📱 *Tap ✕ to collapse sidebar*")
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
    "✍️ Sentence Builder",
    "🔊 Audio Dictionary",
    "📖 Reading Practice",
    "🔄 Review",
    "🕸️ BashkortNet Explorer",
    "📖 Cultural Context",
    "🌟 Truth Unveiled",
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

    loci_data = load_loci()

    # Locus selection
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Choose Your Destination")

        locus_options = list(loci_data.keys())
        locus_display = {
            "Ufa": "🦅 Өфө – Eagle's Perch",
            "TwoFountains": "⛲ Ике Фонтан – Meeting of Waters",
            "ThreeShihans": "🏔️ Өс Шиһан – Toratau, Yuraktau, Kushtau",
            "Shulgan-Tash": "🐦⬛ Шүлгәнташ – Crow's Archive",
            "Yamantau": "🔥🕊️ Ямантау – Anqa's Ascent",
            "Beloretsk": "🕊️ Белорет – Ringdove's Forge",
            "SevenGirls": "💃 Ете Ҡыҙ – Seven Sisters in the Sky",
            "Bizhbulyak": "🕊️ Бижбуляк – Ringdove's Hearth"
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

            with st.expander(f"📍 Station {station.get('number', '?')}: {station_name}", expanded=True):
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
                                <span class="bashkir-text">{word['bashkir']} {"✅" if is_learned else ""}</span>
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

# === PAGE: GOLDEN LIGHT (Алтын Яҡты) ===
elif "Golden Light" in selected_page:
    # Load data
    golden_data = load_golden_light_data()
    gl_info = golden_data.get('golden_light', {})
    gl_title = gl_info.get('title', {})
    legacy_proverb = gl_info.get('legacy_proverb', {})
    stations = gl_info.get('memory_palace_stations', [])

    st.title("✨ Алтын Яҡты — Golden Light")
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
            if st.button(station.get('icon', '📍'), key=f"gl_station_{idx}", help=station.get('title', '')):
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
                <span style="font-size: 2em;">{current_station.get('icon', '📍')}</span>
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
            if st.button("← Previous Station"):
                st.session_state.gl_station -= 1
                st.rerun()
    with col3:
        if st.session_state.gl_station < len(stations) - 1:
            if st.button("Next Station →"):
                st.session_state.gl_station += 1
                st.rerun()

# === PAGE: INDEPENDENCE (12 Reasons) ===
elif "Independence" in selected_page:
    golden_data = load_golden_light_data()
    independence = golden_data.get('independence', {})
    title_info = independence.get('title', {})
    reasons = independence.get('reasons', [])

    st.title("⚖️ Бәйһеҙлек — Independence")
    st.markdown(f"### {title_info.get('subtitle', '')}")
    st.markdown(f"*By {independence.get('author', '')} — {independence.get('organization', '')}*")

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
            <strong>"Халыҡ көсө — таш тишә"</strong><br>
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
            "arabic": "العقل الأول",
            "english": "First Intellect",
            "symbol": "🦅",
            "color": "eagle",
            "locus": "Ufa",
            "domain": "Civic & Legal Knowledge",
            "description": """The Eagle represents the First Intellect (al-'Aql al-Awwal) —
            the primordial light of knowledge from which all understanding flows.
            At Ufa, we encounter constitutional knowledge, legal rights, and civic identity.
            The Eagle sees the whole landscape from above; it knows the law that governs.""",
            "vocabulary": ["Башҡортостан", "халыҡ", "иркенлек", "тел", "конституция"]
        },
        {
            "name": "Crow",
            "arabic": "الجسم الكلي",
            "english": "Universal Body",
            "symbol": "🐦⬛",
            "color": "crow",
            "locus": "Shulgan-Tash",
            "domain": "Ancestral Memory & Nature",
            "description": """The Crow represents Universal Body (al-Jism al-Kulli) —
            matter infused with spirit, darkness containing light. In the cave's depths,
            we find manifestation: the physical traces of spiritual vision painted on stone.
            The Crow guards what was; it remembers what others forget.""",
            "vocabulary": ["ҡояш", "ай", "таш", "һыу", "йылға", "Ағиҙел"]
        },
        {
            "name": "Anqa",
            "arabic": "الهيولى",
            "english": "Prime Matter",
            "symbol": "🔥🕊️",
            "color": "anqa",
            "locus": "Yamantau",
            "domain": "Potential & Transformation",
            "description": """The Anqa represents Prime Matter (al-Hayūlā) —
            pure potentiality, the 'name without a body.' Like the mythical phoenix,
            it exists in the realm of possibility. At Yamantau ('Bad Mountain'),
            danger and transformation intertwine. From difficulty comes growth.""",
            "vocabulary": ["тау", "ел", "урман", "ҡурҡыныс", "күл", "яман", "ҙур"]
        },
        {
            "name": "Ringdove",
            "arabic": "النفس الكلية",
            "english": "Universal Soul",
            "symbol": "🕊️",
            "color": "ringdove",
            "locus": "Beloretsk & Bizhbulyak",
            "domain": "Daily Life & Community",
            "description": """The Ringdove represents Universal Soul (al-Nafs al-Kulliyya) —
            the receptive, nurturing principle that brings potential into form.
            At Beloretsk, raw ore becomes steel through patient work.
            At Bizhbulyak, family, food, and music create the texture of daily life.""",
            "vocabulary": ["эш", "болат", "оҫта", "бал", "ата", "әсә", "өй", "ҡурай", "ат"]
        }
    ]

    for bird in birds:
        st.markdown(f"""
        <div class="bird-card {bird['color']}-card">
            <h3>{bird['symbol']} {bird['name']} — {bird['english']}</h3>
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
                st.success("✅ Correct!")
            else:
                st.error(f"❌ The correct answer is: {q['correct']}")

# === PAGE: URAL-BATYR EPIC ===
elif "Ural-Batyr" in selected_page:
    st.title("⚔️ Урал-Батыр / Ural-Batyr")
    st.markdown("*The foundational myth of the Bashkir people — 4,576 lines of heroic legend*")

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
            st.markdown("### 🧠 Method of Loci — Memory Palace Technique")
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
                One may seek the light, another may guard the depths. Both are necessary—the hero who
                sacrifices and the guardian who preserves memory in darkness.
                """)

    # Navigation buttons - centered with better spacing
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    with nav_col1:
        if st.session_state.epic_chapter > 0:
            if st.button("← Previous Chapter", key="prev_chapter", use_container_width=True):
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
            if st.button("Next Chapter →", key="next_chapter", use_container_width=True):
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

    st.title("🗺️ Географиә — Geography of Bashkortostan")
    st.markdown(f"*{geo_title.get('bashkir', '')}*")

    # Overview stats
    st.markdown("### 📊 Republic Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <h3>🏛️</h3>
            <p style="font-size: 1.1em; font-weight: bold;">{overview.get('capital', '')}</p>
            <small>Capital</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <h3>📐</h3>
            <p style="font-size: 1.1em; font-weight: bold;">{overview.get('area_km2', ''):,} km²</p>
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
    tab1, tab2, tab3, tab4 = st.tabs(["🏙️ Cities", "⛰️ Landmarks", "📚 Facts", "🗺️ Map"])

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
        st.markdown("### ⛰️ Notable Landmarks")
        st.markdown("*Sacred mountains, rivers, and caves of Bashkortostan*")

        for landmark in landmarks:
            st.markdown(f"""
            <div class="word-card" style="border-left: 5px solid #d4af37;">
                <div style="display: flex; align-items: flex-start; gap: 15px;">
                    <span style="font-size: 2.5em;">{landmark.get('icon', '🏔️')}</span>
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
                    'name': f"{landmark.get('icon', '⛰️')} {landmark.get('name', '')} ({landmark.get('bashkir', '')})",
                    'type': 'landmark'
                })

            df = pd.DataFrame(map_data)

            # Display the map
            st.map(df, latitude='lat', longitude='lon', zoom=6)

            # Legend
            st.markdown("""
            **Map Legend:**
            - 🏙️ Cities
            - ⛰️ Mountains
            - 🎨 Cave (Shulgan-Tash)
            - 🌊 River

            *Map data: OpenStreetMap contributors*
            """)

        except ImportError:
            st.warning("Install pandas for map functionality: `pip install pandas`")
            st.info(f"Map would show area from {map_bounds.get('south')}° to {map_bounds.get('north')}° N, "
                    f"{map_bounds.get('west')}° to {map_bounds.get('east')}° E")

# === PAGE: MEDIA (TV Guide, Real Russia, Transcription) ===
elif "Media" in selected_page:
    st.title("📺 Медиа — Media Center")
    st.markdown("*Watch Bashkir TV, follow Real Russia content, and generate live subtitles*")

    # Create tabs for different media sections
    media_tab1, media_tab2, media_tab3, media_tab4, media_tab5, media_tab6 = st.tabs([
        "📺 TV Guide",
        "🎬 Video Player",
        "🇷🇺 Real Russia",
        "⬇️ Downloads",
        "📸 Scan Text (OCR)",
        "🎤 Live Subtitles"
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
                "name": "БСТ (Bashkir Satellite Television)",
                "description": "Main Bashkir language broadcaster - news, culture, entertainment",
                "stream_url": "https://bst.tv/live",
                "icon": "📡"
            },
            {
                "name": "Курай ТВ (Kuray TV)",
                "description": "Music and cultural programs featuring traditional Bashkir arts",
                "stream_url": "https://kuray.tv",
                "icon": "🎵"
            },
            {
                "name": "Салават Юлаев ТВ",
                "description": "Sports channel - hockey and regional sports coverage",
                "stream_url": "#",
                "icon": "🏒"
            },
            {
                "name": "Тамыр (Tamyr)",
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
            st.markdown("#### 🕐 TV Schedule (Sample)")
            st.markdown("""
            **БСТ Tonight:**
            - 18:00 — Хәбәрҙәр (News)
            - 19:00 — Йырҙар (Songs)
            - 20:00 — Әкиәт (Folk Tales)
            - 21:00 — Документаль (Documentary)
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

    # === VIDEO PLAYER TAB ===
    with media_tab2:
        st.markdown("### 🎬 Video Player with Subtitles")
        st.markdown("*Watch videos with auto-generated Bashkir subtitles*")

        # Import subtitle service
        try:
            from modules.subtitle_service import get_subtitle_service, SubtitleFormat
            subtitle_svc_available = True
        except ImportError:
            subtitle_svc_available = False

        # Video source selection
        video_source = st.radio(
            "Video Source",
            ["📤 Upload Video", "🔗 URL/Stream", "📁 Sample Videos"],
            horizontal=True
        )

        if video_source == "📤 Upload Video":
            uploaded_video = st.file_uploader(
                "Upload a video file",
                type=['mp4', 'mkv', 'avi', 'mov', 'webm'],
                key="video_upload"
            )

            if uploaded_video:
                # Save to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                    f.write(uploaded_video.read())
                    video_path = f.name

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.video(video_path)

                with col2:
                    st.markdown("#### 🎤 Generate Subtitles")

                    if not subtitle_svc_available:
                        st.warning("⚠️ Subtitle service not available. Install: `pip install faster-whisper`")
                    else:
                        sub_language = st.selectbox(
                            "Language",
                            ["Auto-detect", "Russian", "English", "Bashkir (experimental)"],
                            key="vid_sub_lang"
                        )

                        model_size = st.selectbox(
                            "Model Quality",
                            ["base (fast)", "small (balanced)", "medium (accurate)", "large-v3 (best)"],
                            key="vid_model"
                        )

                        if st.button("🎯 Generate Subtitles", use_container_width=True, key="gen_subs"):
                            model = model_size.split(" ")[0]
                            lang_map = {
                                "Auto-detect": "auto",
                                "Russian": "ru",
                                "English": "en",
                                "Bashkir (experimental)": "ba"
                            }

                            with st.spinner(f"Loading {model} model and generating subtitles..."):
                                svc = get_subtitle_service(model_size=model)

                                progress_placeholder = st.empty()

                                def progress_cb(status, prog):
                                    progress_placeholder.progress(prog, text=status)

                                result = svc.transcribe_video(
                                    video_path,
                                    language=lang_map.get(sub_language, "auto"),
                                    progress_callback=progress_cb
                                )

                            if result:
                                st.success(f"✅ Generated {len(result.segments)} subtitle segments!")
                                st.info(f"Detected language: {result.language}")

                                # Show subtitles
                                st.markdown("#### 📜 Subtitles Preview")
                                for seg in result.segments[:10]:
                                    st.markdown(f"**[{seg.start:.1f}s - {seg.end:.1f}s]** {seg.text}")

                                if len(result.segments) > 10:
                                    st.caption(f"... and {len(result.segments) - 10} more segments")

                                # Download options
                                st.markdown("#### ⬇️ Download")
                                dl_cols = st.columns(3)
                                with dl_cols[0]:
                                    st.download_button(
                                        "📄 SRT",
                                        result.to_srt(),
                                        file_name="subtitles.srt",
                                        mime="text/plain"
                                    )
                                with dl_cols[1]:
                                    st.download_button(
                                        "📄 VTT",
                                        result.to_vtt(),
                                        file_name="subtitles.vtt",
                                        mime="text/vtt"
                                    )
                                with dl_cols[2]:
                                    st.download_button(
                                        "📄 TXT",
                                        result.text,
                                        file_name="transcript.txt",
                                        mime="text/plain"
                                    )
                            else:
                                st.error(f"Subtitle generation failed: {svc.init_error}")

        elif video_source == "🔗 URL/Stream":
            st.markdown("#### 🔗 Enter Video URL")
            video_url = st.text_input(
                "Video URL",
                placeholder="https://example.com/video.mp4 or stream URL",
                key="video_url_input"
            )

            if video_url:
                st.markdown("##### Preview")
                try:
                    st.video(video_url)
                except Exception as e:
                    st.warning(f"Cannot preview this URL directly. For streams, use VLC Media Player.")
                    st.code(video_url)
                    st.markdown("**To watch with VLC:**")
                    st.markdown("1. Open VLC Media Player")
                    st.markdown("2. Go to Media → Open Network Stream")
                    st.markdown("3. Paste the URL above")

        else:  # Sample Videos
            st.markdown("#### 📁 Sample Bashkir Content")
            st.info("Sample videos would be loaded from your library here.")

            sample_videos = [
                {"title": "Bashkir Alphabet Song", "duration": "3:45", "level": "Beginner"},
                {"title": "Conversation Practice", "duration": "5:20", "level": "Elementary"},
                {"title": "News Broadcast Sample", "duration": "2:30", "level": "Advanced"}
            ]

            for vid in sample_videos:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{vid['title']}**")
                with col2:
                    st.caption(vid['duration'])
                with col3:
                    st.button("▶️ Play", key=f"play_{vid['title']}")

    # === REAL RUSSIA TAB ===
    with media_tab3:
        st.markdown("### 🇷🇺 Real Russia — Sergey Baklykov")
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
                        <p style="color: rgba(255,255,255,0.8); margin: 5px 0;">Real Russia — Sergey Baklykov</p>
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
                    "preview": "The Southern Urals are magical in winter. Here's what it's like to hike in -20°C...",
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
                        <span>⏰ {entry['date']}</span>
                        <span>👁️ {entry['engagement']}</span>
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
            - 🏔️ Authentic regional content
            - 🗣️ Language learning tips
            - 🍯 Cultural immersion
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
    with media_tab4:
        st.markdown("### ⬇️ Downloadable Content")
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
                    st.caption(f"🕐 {audio['duration']}")
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

    # === LIVE SUBTITLES TAB ===
    with media_tab6:
        st.markdown("### 🎤 Live Subtitles")
        st.markdown("*Real-time speech-to-text for live streams and broadcasts*")

        st.info("""
        🎧 **How it works:** This feature uses faster-whisper to transcribe audio in real-time,
        allowing you to watch Bashkir TV or streams with live-generated subtitles.
        """)

        # Import subtitle service
        try:
            from modules.subtitle_service import get_subtitle_service
            live_sub_available = True
        except ImportError:
            live_sub_available = False

        if not live_sub_available:
            st.warning("⚠️ Subtitle service not available. Please install: `pip install faster-whisper`")
        else:
            # Live transcription mode selection
            live_mode = st.radio(
                "Transcription Mode",
                ["🎙️ Microphone Input", "🔗 Stream URL", "📺 System Audio"],
                horizontal=True,
                help="Choose audio source for live transcription"
            )

            col1, col2 = st.columns([2, 1])

            with col1:
                # Model selection for live
                live_model = st.selectbox(
                    "Whisper Model",
                    ["tiny", "base", "small"],
                    index=1,
                    help="Smaller models = faster but less accurate. For live use 'tiny' or 'base'"
                )

            with col2:
                live_lang = st.selectbox(
                    "Language",
                    ["Auto-detect", "Russian", "Bashkir (experimental)"],
                    help="Auto-detect works well for Russian. Bashkir results may vary."
                )

            # Live subtitle display area
            st.markdown("#### 📺 Subtitle Display")

            subtitle_display = st.empty()

            subtitle_display.markdown("""
            <div style="background: #000; color: #fff; padding: 40px 20px; border-radius: 10px;
                        text-align: center; min-height: 100px; font-size: 1.5em; font-family: Arial, sans-serif;">
                <span style="color: #666;">[ Subtitles will appear here ]</span>
            </div>
            """, unsafe_allow_html=True)

            # Control buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)

            with btn_col1:
                if st.button("▶️ Start Live Transcription", use_container_width=True):
                    st.session_state['live_transcribing'] = True
                    st.toast("Starting live transcription... (simulation)")

                    # Simulated live subtitle demo
                    import time
                    demo_subtitles = [
                        "Һаумыһығыҙ, ҡәҙерле тамашасылар!",
                        "Бүгөн беҙ Башҡортостан тураһында һөйләшәбеҙ.",
                        "Башҡортостан — бик матур ер!",
                        "Унда тауҙар, урмандар, йылғалар бар."
                    ]

                    for sub in demo_subtitles:
                        subtitle_display.markdown(f"""
                        <div style="background: #000; color: #fff; padding: 40px 20px; border-radius: 10px;
                                    text-align: center; min-height: 100px; font-size: 1.5em; font-family: Arial, sans-serif;">
                            {sub}
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(2)

                    subtitle_display.markdown("""
                    <div style="background: #000; color: #0f0; padding: 40px 20px; border-radius: 10px;
                                text-align: center; min-height: 100px; font-size: 1.3em;">
                        ✓ Demo complete — Install faster-whisper for real-time transcription
                    </div>
                    """, unsafe_allow_html=True)

            with btn_col2:
                if st.button("⏹️ Stop", use_container_width=True):
                    st.session_state['live_transcribing'] = False
                    st.toast("Stopped transcription")

            with btn_col3:
                if st.button("📥 Save Transcript", use_container_width=True):
                    st.toast("Transcript saved (feature in development)")

            st.markdown("---")

            # Stream URL input for live streams
            if live_mode == "🔗 Stream URL":
                st.markdown("#### 🔗 Stream Configuration")
                stream_url = st.text_input(
                    "Enter stream URL:",
                    placeholder="https://example.com/stream.m3u8",
                    help="Works with HLS, RTMP, and direct video URLs"
                )

                if stream_url:
                    st.markdown(f"""
                    <div class="word-card" style="background: #1a1a2e;">
                        <p style="color: #fff;"><strong>Stream:</strong> <code>{stream_url}</code></p>
                        <small style="color: #666;">Audio will be extracted and transcribed in real-time</small>
                    </div>
                    """, unsafe_allow_html=True)

            # Subtitle settings
            with st.expander("⚙️ Subtitle Settings"):
                sub_col1, sub_col2 = st.columns(2)

                with sub_col1:
                    st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1)
                    st.selectbox("Position", ["Bottom", "Top"], index=0)

                with sub_col2:
                    st.color_picker("Text Color", "#FFFFFF")
                    st.color_picker("Background Color", "#000000")

                st.checkbox("Show timestamps", value=False)
                st.checkbox("Auto-scroll transcript", value=True)

            # Tips
            with st.expander("💡 Tips for Live Transcription"):
                st.markdown("""
                **Best practices for real-time subtitles:**

                1. **Model Selection:**
                   - Use `tiny` or `base` for minimal latency
                   - Use `small` for better accuracy if you have GPU

                2. **Audio Quality:**
                   - Clear audio with minimal background noise works best
                   - Headphones recommended to prevent feedback

                3. **Language Detection:**
                   - Russian is well-supported by Whisper
                   - Bashkir may be transcribed as Russian (similar sounds)
                   - For best Bashkir results, use larger models

                4. **Performance:**
                   - GPU (CUDA) dramatically improves speed
                   - CPU-only mode works but may have 2-5 second delay

                5. **Use Cases:**
                   - 📺 Watching Bashkir TV (БСТ, Kuray TV)
                   - 🎥 Following YouTube livestreams
                   - 🎤 Transcribing video calls
                   - 📻 Radio broadcast transcription
                """)

    # === SCAN TEXT (OCR) TAB ===
    with media_tab5:
        st.markdown("### 📸 Scan Text (OCR)")
        st.markdown("*Extract Bashkir text from images using Optical Character Recognition*")

        # Import OCR service
        try:
            from modules.ocr_service import get_ocr_service, scan_text_from_image
            ocr_available = True
        except ImportError:
            ocr_available = False

        if not ocr_available:
            st.warning("⚠️ OCR module not available. Please install dependencies: `pip install easyocr Pillow`")
        else:
            ocr_service = get_ocr_service()

            st.info("""
            📷 **How to use:**
            1. Upload an image containing Bashkir/Cyrillic text
            2. The OCR will extract and recognize the text
            3. Matched words will be linked to the dictionary for instant lookup
            """)

            # File uploader
            uploaded_image = st.file_uploader(
                "Upload an image with Bashkir text",
                type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
                help="Supported formats: PNG, JPG, JPEG, WEBP, BMP"
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                preprocess = st.checkbox("Apply image preprocessing", value=True,
                                        help="Enhance contrast and sharpness for better OCR accuracy")

            with col2:
                min_confidence = st.slider("Minimum confidence", 0.1, 0.9, 0.3,
                                          help="Filter out low-confidence text detections")

            if uploaded_image:
                # Display the uploaded image
                st.markdown("#### 📷 Uploaded Image")
                st.image(uploaded_image, use_container_width=True)

                # Process button
                if st.button("🔍 Scan Text", use_container_width=True):
                    with st.spinner("Initializing OCR engine (first run downloads ~100MB model)..."):
                        # Initialize OCR if needed
                        if not ocr_service.is_initialized:
                            success = ocr_service.initialize()
                            if not success:
                                st.error(f"Failed to initialize OCR: {ocr_service.init_error}")
                                st.stop()

                    with st.spinner("Scanning image for text..."):
                        # Run OCR with dictionary matching
                        results = scan_text_from_image(uploaded_image, words_data)

                    if 'error' in results:
                        st.error(results['error'])
                    else:
                        # Display results
                        st.markdown("---")
                        st.markdown("#### 📜 Extracted Text")

                        raw_results = results.get('raw_results', [])
                        if raw_results:
                            # Show all detected text regions
                            full_text = " ".join([r['text'] for r in raw_results])
                            st.markdown(f"""
                            <div class="word-card" style="background: #f9f9f9; font-size: 1.2em;">
                                {full_text}
                            </div>
                            """, unsafe_allow_html=True)

                            # Copy button
                            st.code(full_text, language=None)

                            # Statistics
                            stats = results.get('statistics', {})
                            st.markdown("#### 📊 Scan Statistics")
                            stat_cols = st.columns(4)
                            with stat_cols[0]:
                                st.metric("Text Regions", stats.get('total_regions', 0))
                            with stat_cols[1]:
                                st.metric("Words Found", stats.get('total_words', 0))
                            with stat_cols[2]:
                                st.metric("Dictionary Matches", stats.get('dictionary_matches', 0))
                            with stat_cols[3]:
                                match_rate = stats.get('match_rate', 0) * 100
                                st.metric("Match Rate", f"{match_rate:.1f}%")

                            # Dictionary matches
                            matches = results.get('matches', [])
                            dict_matches = [m for m in matches if m.get('in_dictionary')]

                            if dict_matches:
                                st.markdown("#### 📚 Words Found in Dictionary")
                                st.markdown("*Click on a word to hear its pronunciation*")

                                for match in dict_matches[:20]:  # Limit display
                                    with st.expander(f"🔊 {match['matched_word']} — {match.get('english', '')}"):
                                        st.markdown(f"""
                                        - **Scanned:** {match['scanned_text']}
                                        - **Bashkir:** {match['matched_word']}
                                        - **English:** {match.get('english', 'N/A')}
                                        - **Russian:** {match.get('russian', 'N/A')}
                                        - **Confidence:** {match['confidence']:.0%}
                                        """)
                                        if st.button("🔊 Play", key=f"ocr_play_{match['matched_word']}"):
                                            play_audio(match['matched_word'], slow=True)

                            # Unknown words
                            unknown = [m for m in matches if not m.get('in_dictionary')]
                            if unknown:
                                with st.expander(f"❓ {len(unknown)} words not in dictionary"):
                                    st.markdown(", ".join([m['scanned_text'] for m in unknown[:30]]))
                        else:
                            st.warning("No text detected in the image. Try a clearer image or adjust settings.")

            else:
                # Placeholder when no image uploaded
                st.markdown("""
                <div class="meditation-box" style="text-align: center; padding: 40px;">
                    <span style="font-size: 4em;">📷</span>
                    <h4>Upload an image to scan</h4>
                    <p>Supports photos of books, signs, handwriting, and more</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Tips
            with st.expander("💡 Tips for Best Results"):
                st.markdown("""
                **For accurate OCR:**

                1. **Image quality:** Use clear, well-lit images with good contrast
                2. **Text orientation:** Keep text horizontal when possible
                3. **Font size:** Larger text is recognized more accurately
                4. **Preprocessing:** Enable preprocessing for photos, disable for clean digital text
                5. **Supported scripts:** Cyrillic (Russian/Bashkir) and Latin scripts

                **Common use cases:**
                - 📚 Scanning pages from Bashkir books or textbooks
                - 🪧 Reading signs and labels in Bashkortostan
                - ✍️ Digitizing handwritten notes
                - 📱 Screenshots from Bashkir websites or apps
                """)

# === PAGE: ALPHABET ===
elif "Alphabet" in selected_page:
    golden_data = load_golden_light_data()
    alphabet_data = golden_data.get('alphabet', {})
    alphabet_title = alphabet_data.get('title', {})
    full_alphabet = alphabet_data.get('full_alphabet', [])
    special_letters = alphabet_data.get('special_letters', [])

    st.title("🔤 Башҡорт әлифбаһы — The Bashkir Alphabet")
    st.markdown(f"*{alphabet_data.get('description', '')}*")

    # Full alphabet display
    st.markdown("### 📝 The Complete Alphabet (42 Letters)")

    # Display alphabet in rows
    cols_per_row = 14
    for i in range(0, len(full_alphabet), cols_per_row):
        row_letters = full_alphabet[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, letter in enumerate(row_letters):
            with cols[j]:
                # Highlight special Bashkir letters
                is_special = letter in ['Ә', 'Ө', 'Ү', 'Ғ', 'Ҡ', 'Ң', 'Ҙ', 'Ҫ', 'Һ']
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
                    📝 Example: <span class="bashkir-text" style="font-size: 1.1em;">{letter_info.get('example', '')}</span>
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
    | **Ә** | /æ/ | 'a' in "cat" | әсә (mother) |
    | **Ө** | /ø/ | German 'ö' | өй (house) |
    | **Ү** | /y/ | German 'ü' | үҙ (self) |
    | **Ғ** | /ʁ/ | Arabic 'غ' (gh) | ғаилә (family) |
    | **Ҡ** | /q/ | Deep throat 'k' | ҡыҙ (girl) |
    | **Ң** | /ŋ/ | 'ng' in "sing" | таң (dawn) |
    | **Ҙ** | /ð/ | 'th' in "this" | ҙур (big) |
    | **Ҫ** | /θ/ | 'th' in "think" | ҫәс (hair) |
    | **Һ** | /h/ | 'h' in "house" | һыу (water) |
    """)

# === PAGE: SENTENCE BUILDER (Enhanced with Audio Export and Working Word Bank) ===
elif "Sentence Builder" in selected_page:
    st.title("✍️ Sentence Builder")
    st.markdown("*Create your own Bashkir sentences, hear them spoken, and export audio for poems or stories!*")

    patterns = load_patterns()

    # Pattern templates
    st.markdown("### 📝 Sentence Patterns")

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
    st.markdown("### 🏦 Word Bank")
    st.markdown("*Click words to add them to your sentence. Words are organized by semantic categories.*")

    # Define OCM-based semantic categories for nouns
    nature_ocm = ['131', '132', '133', '134', '137', '138', '139', '221', '222', '231', '232', '233', '234', '235', '241', '242', '243', '244', '245', '246', '251', '252', '253', '254', '255', '256', '257', '258', '259']
    culture_ocm = ['530', '531', '532', '533', '534', '535', '536', '537', '538', '539', '541', '542', '543', '544', '545', '551', '552', '553', '554', '561', '562', '563', '564', '565', '566', '571', '572', '573', '574', '575', '576', '577', '578', '579', '581', '582', '583', '584', '585', '586', '587']
    people_ocm = ['591', '592', '593', '594', '595', '596', '597', '598', '599', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '621', '622', '623', '624', '625', '626', '627', '628', '629']
    places_ocm = ['361', '362', '363', '364', '365', '366', '367', '368', '369', '481', '482', '483', '484', '485', '486', '487', '488', '489', '131', '784']

    # Nature keywords for backup categorization
    nature_keywords = ['тау', 'ҡояш', 'ай', 'йондоҙ', 'һыу', 'йылға', 'күл', 'диңгеҙ', 'урман', 'ағас', 'сәскә', 'үлән', 'ҡош', 'айыу', 'бүре', 'ҡуй', 'ат', 'һыйыр', 'балыҡ', 'йылан', 'ел', 'ҡар', 'боҙ', 'ямғыр', 'болот', 'көн', 'төн', 'яҙ', 'йәй', 'көҙ', 'ҡыш', 'таш', 'туфраҡ', 'ер', 'нур']
    culture_keywords = ['байрам', 'сабантуй', 'туй', 'йола', 'әкиәт', 'риүәйәт', 'йыр', 'моң', 'бейеү', 'ҡурай', 'думбыра', 'ҡубыҙ', 'бал', 'ҡымыҙ', 'буҙа', 'икмәк', 'ит', 'аш', 'сәй', 'тирмә', 'биҙәк', 'ойма', 'көрәш', 'уйын', 'дин', 'мәсьет', 'театр']
    people_keywords = ['ата', 'әсә', 'бала', 'ҡыҙ', 'егет', 'бабай', 'өләсәй', 'туғандар', 'ғаилә', 'халыҡ', 'милләт', 'дуҫ', 'ҡунаҡ', 'уҡытыусы', 'эшсе', 'оҫта', 'батыр', 'граждан', 'президент']
    places_keywords = ['Өфө', 'Башҡортостан', 'ҡала', 'урам', 'мәйҙан', 'өй', 'йорт', 'мәктәп', 'завод', 'магазин', 'банк', 'почта', 'ил', 'дәүләт', 'республика', 'Ағиҙел', 'Шүлгәнташ', 'Ямантау', 'Иремәл', 'Бижбуляк', 'Белорет']

    # Expanded word categories
    word_categories = {
        "👥 Pronouns": [],
        "🌿 Nature": [],
        "🎭 Culture": [],
        "👨‍👩‍👧 People": [],
        "🏛️ Places": [],
        "💭 Concepts": [],
        "🎬 Verbs": [],
        "📝 Adjectives": [],
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
            word_categories["📝 Adjectives"].append(bashkir)
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
                    word_categories["👨‍👩‍👧 People"].append(bashkir)
                    categorized = True
                    break
                elif code in places_ocm:
                    word_categories["🏛️ Places"].append(bashkir)
                    categorized = True
                    break

            # If not categorized by OCM, check keywords
            if not categorized:
                if any(kw in bashkir for kw in nature_keywords) or any(kw in english for kw in ['sun', 'moon', 'star', 'water', 'river', 'lake', 'tree', 'forest', 'bird', 'animal', 'wolf', 'bear', 'fish', 'horse', 'cow', 'sheep', 'snow', 'rain', 'wind', 'day', 'night', 'spring', 'summer', 'autumn', 'winter', 'flower', 'grass', 'mountain', 'stone', 'earth', 'sky']):
                    word_categories["🌿 Nature"].append(bashkir)
                elif any(kw in bashkir for kw in culture_keywords) or any(kw in english for kw in ['festival', 'wedding', 'song', 'dance', 'music', 'honey', 'kumis', 'bread', 'meat', 'tea', 'food', 'tradition', 'legend', 'tale', 'story', 'holiday', 'craft', 'art', 'ornament', 'religion']):
                    word_categories["🎭 Culture"].append(bashkir)
                elif any(kw in bashkir for kw in people_keywords) or any(kw in english for kw in ['father', 'mother', 'child', 'girl', 'boy', 'grandfather', 'grandmother', 'family', 'relative', 'people', 'nation', 'friend', 'guest', 'teacher', 'worker', 'hero', 'citizen', 'president']):
                    word_categories["👨‍👩‍👧 People"].append(bashkir)
                elif any(kw in bashkir for kw in places_keywords) or any(kw in english for kw in ['city', 'street', 'square', 'house', 'home', 'school', 'factory', 'shop', 'bank', 'post', 'country', 'state', 'republic', 'capital', 'village', 'ufa', 'bashkortostan']):
                    word_categories["🏛️ Places"].append(bashkir)
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
                label="⬇️ Download Audio (MP3)",
                data=audio_bytes,
                file_name=f"bashkir_sentence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                mime="audio/mp3"
            )

        # Grammar notes
        st.markdown("### 📖 Grammar Helper")
        st.info("""
        **Bashkir Word Order: Subject - Object - Verb (SOV)**

        Unlike English (I *see* the mountain), Bashkir puts the verb at the END:
        - Мин тауҙы **күрәм** (I mountain **see**)

        **Case Suffixes:**
        - Nominative (subject): no suffix
        - Dative (to/for): -ға/-гә
        - Accusative (object): -ны/-не
        - Ablative (from): -дан/-дән
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
                    if st.button(f"▶️ Play", key=f"play_saved_{idx}"):
                        play_audio(sentence['bashkir'], slow=True)
                with sent_col2:
                    audio_data = generate_audio_with_retry(sentence['bashkir'], slow=True)
                    if audio_data:
                        st.download_button(
                            label="⬇️ Download",
                            data=audio_data,
                            file_name=f"sentence_{idx+1}.mp3",
                            mime="audio/mp3",
                            key=f"download_saved_{idx}"
                        )
                with sent_col3:
                    if st.button(f"🗑️ Remove", key=f"remove_saved_{idx}"):
                        st.session_state.saved_sentences.pop(idx)
                        st.rerun()

# === PAGE: AUDIO DICTIONARY (Enhanced with OCM Categories and OCR) ===
elif "Audio Dictionary" in selected_page:
    st.title("🔊 Audio Dictionary")
    st.markdown("*Listen to all Bashkir words organized by cultural categories (OCM eHRAF 2021)*")

    # Load OCM mapping
    ocm_data = load_ocm_mapping()
    thematic_groups = ocm_data.get('thematic_groups', {})
    ocm_labels = ocm_data.get('ocm_labels', {})

    # Search and Scan tabs
    dict_search_tab, dict_scan_tab = st.tabs(["🔍 Search & Browse", "📸 Quick Scan"])

    with dict_search_tab:
        # Search bar with improved styling
        st.markdown("### 🔍 Search")
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
                with st.expander(f"🔊 {word['bashkir']} — {word.get('english', '')}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        word_ocm_codes = word.get('cultural_context', {}).get('ocm_codes', [])
                        word_ocm_names = [ocm_labels.get(code, code) for code in word_ocm_codes[:3]]

                        st.markdown(f"""
                        <div class="word-card">
                            <span class="bashkir-text" style="font-size: 2em;">{word['bashkir']}</span>
                            <span class="ipa-text" style="font-size: 1.2em;">{word.get('ipa', '')}</span>
                            <div class="english-text" style="font-size: 1.3em; margin: 10px 0;">{word.get('english', '')}</div>
                            <span class="russian-text" style="font-size: 1.1em;">🇷🇺 {word.get('russian', '')}</span>
                            <br><br>
                            <span style="color: #0066B3; font-size: 0.9em;">📚 OCM: {', '.join(word_ocm_names) if word_ocm_names else 'General'}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown("**🔊 Audio:**")
                        if st.button("▶️ Normal", key=f"audio_normal_{word['id']}"):
                            play_audio(word['bashkir'], slow=False)
                        if st.button("🐢 Slow", key=f"audio_slow_{word['id']}"):
                            play_audio(word['bashkir'], slow=True)

                        audio_bytes = generate_audio_with_retry(word['bashkir'], slow=True)
                        if audio_bytes:
                            st.download_button(
                                label="⬇️ Download",
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
                category_tabs = st.tabs(display_names)

                for cat_tab, group_key in zip(category_tabs, group_names):
                    with cat_tab:
                        group_info = thematic_groups[group_key]
                        group_words_list = group_info.get('words', [])
                        group_ocm_codes = group_info.get('ocm_codes', [])

                        # Get OCM labels for this group
                        group_ocm_names = [f"{code}: {ocm_labels.get(code, 'Unknown')}" for code in group_ocm_codes[:5]]

                        st.markdown(f"**OCM Categories:** {', '.join(group_ocm_names[:3])}...")

                        # Find matching words from words_data
                        matching_words = []
                        for word in words_data:
                            word_ocm = word.get('cultural_context', {}).get('ocm_codes', [])
                            if any(code in word_ocm for code in group_ocm_codes):
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
                                                        "⬇️",
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

    # Quick Scan Tab (OCR)
    with dict_scan_tab:
        st.markdown("### 📸 Quick Scan")
        st.markdown("*Scan text from an image and instantly look up words*")

        try:
            from modules.ocr_service import get_ocr_service, scan_text_from_image
            dict_ocr_available = True
        except ImportError:
            dict_ocr_available = False

        if not dict_ocr_available:
            st.warning("⚠️ OCR not available. Install with: `pip install easyocr Pillow`")
        else:
            st.info("📷 Upload a photo with Bashkir text to instantly find words in the dictionary")

            quick_scan_image = st.file_uploader(
                "Upload image",
                type=['png', 'jpg', 'jpeg'],
                key="dict_quick_scan"
            )

            if quick_scan_image:
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.image(quick_scan_image, caption="Uploaded Image", use_container_width=True)

                with col2:
                    if st.button("🔍 Scan & Lookup", use_container_width=True, key="dict_scan_btn"):
                        with st.spinner("Scanning..."):
                            ocr_svc = get_ocr_service()
                            if not ocr_svc.is_initialized:
                                ocr_svc.initialize()

                            scan_results = scan_text_from_image(quick_scan_image, words_data)

                        if 'error' not in scan_results:
                            matches = scan_results.get('matches', [])
                            dict_matches = [m for m in matches if m.get('in_dictionary')]

                            if dict_matches:
                                st.success(f"✅ Found {len(dict_matches)} words!")
                                for m in dict_matches[:10]:
                                    st.markdown(f"**{m['matched_word']}** — {m.get('english', '')}")
                                    if st.button(f"🔊 {m['matched_word']}", key=f"qs_{m['matched_word']}"):
                                        play_audio(m['matched_word'], slow=True)
                            else:
                                st.warning("No dictionary matches found")
                        else:
                            st.error(scan_results.get('error'))
            else:
                st.markdown("""
                <div style="text-align: center; padding: 30px; background: #f5f5f5; border-radius: 10px;">
                    <span style="font-size: 3em;">📷</span>
                    <p>Upload a photo to scan</p>
                </div>
                """, unsafe_allow_html=True)

# === PAGE: READING PRACTICE ===
elif "Reading Practice" in selected_page:
    st.title("📖 Reading Practice")
    st.markdown("*Improve your Bashkir reading with graded texts and vocabulary support*")

    # Import content scraper
    try:
        from modules.content_scraper import get_content_scraper, DifficultyLevel
        reading_available = True
    except ImportError:
        reading_available = False

    if not reading_available:
        st.warning("⚠️ Reading Practice module not available.")
    else:
        scraper = get_content_scraper()
        all_texts = scraper.get_all_texts()

        # Initialize reading progress in session state
        if 'completed_readings' not in st.session_state:
            st.session_state.completed_readings = []
        if 'known_words' not in st.session_state:
            st.session_state.known_words = set(st.session_state.learned_words)

        # Statistics
        stats = scraper.get_reading_stats(st.session_state.completed_readings)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Texts Available", stats['total_texts'])
        with col2:
            st.metric("✅ Completed", stats['completed_texts'])
        with col3:
            st.metric("📝 Words Read", stats['words_read'])
        with col4:
            completion_pct = stats['completion_rate'] * 100
            st.metric("📊 Progress", f"{completion_pct:.0f}%")

        st.markdown("---")

        # Difficulty filter
        st.markdown("### 📊 Select Difficulty")
        difficulty_options = {
            "All Levels": None,
            "🌱 Beginner": DifficultyLevel.BEGINNER,
            "🌿 Elementary": DifficultyLevel.ELEMENTARY,
            "🌳 Intermediate": DifficultyLevel.INTERMEDIATE,
            "🏔️ Advanced": DifficultyLevel.ADVANCED
        }

        selected_difficulty = st.selectbox(
            "Filter by difficulty:",
            list(difficulty_options.keys()),
            key="reading_difficulty"
        )

        difficulty_filter = difficulty_options[selected_difficulty]

        # Filter texts
        if difficulty_filter:
            filtered_texts = scraper.get_texts_by_difficulty(difficulty_filter)
        else:
            filtered_texts = all_texts

        st.markdown(f"**{len(filtered_texts)} texts available**")

        st.markdown("---")

        # Display texts
        st.markdown("### 📖 Reading Texts")

        for text in filtered_texts:
            # Determine completion status
            is_completed = text.id in st.session_state.completed_readings

            # Difficulty badge colors
            diff_colors = {
                DifficultyLevel.BEGINNER: "#4CAF50",
                DifficultyLevel.ELEMENTARY: "#8BC34A",
                DifficultyLevel.INTERMEDIATE: "#FFC107",
                DifficultyLevel.ADVANCED: "#FF9800",
                DifficultyLevel.NATIVE: "#F44336"
            }
            diff_color = diff_colors.get(text.difficulty, "#888")

            with st.expander(
                f"{'✅' if is_completed else '📖'} {text.title} — {text.difficulty.name.title()} ({text.word_count} words)",
                expanded=False
            ):
                # Header with metadata
                meta_cols = st.columns([2, 1, 1])
                with meta_cols[0]:
                    st.markdown(f"**Topics:** {', '.join(text.topics)}")
                with meta_cols[1]:
                    st.markdown(f"""
                    <span style="background: {diff_color}; color: white; padding: 2px 8px;
                                 border-radius: 12px; font-size: 0.8em;">
                        {text.difficulty.name}
                    </span>
                    """, unsafe_allow_html=True)
                with meta_cols[2]:
                    st.markdown(f"**{text.word_count}** words")

                st.markdown("---")

                # The reading text with vocabulary highlighting
                st.markdown("#### 📜 Text")

                # Highlight vocabulary
                highlighted_text = scraper.highlight_vocabulary(
                    text.content,
                    st.session_state.known_words,
                    words_data
                )

                st.markdown(f"""
                <div class="word-card" style="font-size: 1.2em; line-height: 1.8; white-space: pre-wrap;">
                    {highlighted_text}
                </div>
                """, unsafe_allow_html=True)

                # Legend
                st.markdown("""
                <small>
                    <span style="color: #00AF66;">■ Known words</span> |
                    <span style="color: #0066B3;">■ Dictionary words (click to learn)</span> |
                    <span style="color: #888;">■ Unknown words</span>
                </small>
                """, unsafe_allow_html=True)

                st.markdown("---")

                # Vocabulary section
                st.markdown("#### 📚 Vocabulary")
                vocab_list = text.vocabulary if text.vocabulary else []

                if vocab_list:
                    vocab_cols = st.columns(3)
                    for idx, vocab_word in enumerate(vocab_list[:12]):
                        with vocab_cols[idx % 3]:
                            # Find word in dictionary
                            dict_entry = next((w for w in words_data if w['bashkir'].lower() == vocab_word.lower()), None)
                            if dict_entry:
                                st.markdown(f"**{dict_entry['bashkir']}** — {dict_entry.get('english', '')}")
                                if st.button(f"🔊", key=f"read_audio_{text.id}_{vocab_word}"):
                                    play_audio(dict_entry['bashkir'], slow=True)
                            else:
                                st.markdown(f"**{vocab_word}**")
                else:
                    st.info("No vocabulary list for this text.")

                st.markdown("---")

                # Actions
                action_cols = st.columns([1, 1, 1])
                with action_cols[0]:
                    if st.button("🔊 Read Aloud", key=f"read_aloud_{text.id}"):
                        # Read first sentence
                        first_sentence = text.content.split('.')[0] + '.'
                        play_audio(first_sentence, slow=True)

                with action_cols[1]:
                    if not is_completed:
                        if st.button("✅ Mark Complete", key=f"complete_{text.id}"):
                            st.session_state.completed_readings.append(text.id)
                            st.success("Text marked as completed!")
                            st.rerun()
                    else:
                        st.markdown("✅ **Completed**")

                with action_cols[2]:
                    # Add vocabulary to review
                    if vocab_list:
                        if st.button("➕ Add Words to Review", key=f"add_vocab_{text.id}"):
                            added = 0
                            for vocab_word in vocab_list:
                                dict_entry = next((w for w in words_data if w['bashkir'].lower() == vocab_word.lower()), None)
                                if dict_entry and dict_entry['bashkir'] not in st.session_state.learned_words:
                                    st.session_state.learned_words.add(dict_entry['bashkir'])
                                    st.session_state.review_queue.append(dict_entry['bashkir'])
                                    added += 1
                            if added > 0:
                                st.success(f"Added {added} words to review!")
                            else:
                                st.info("All words already in your review list")

        # Tips section
        st.markdown("---")
        with st.expander("💡 Reading Tips"):
            st.markdown("""
            **How to get the most from reading practice:**

            1. **Start with your level:** Begin with texts at or slightly below your level
            2. **Read multiple times:** First for gist, then for detail, then for vocabulary
            3. **Use audio:** Listen while reading to improve pronunciation
            4. **Learn vocabulary:** Add unfamiliar words to your review queue
            5. **Mark progress:** Complete texts to track your reading journey

            **Color coding:**
            - 🟢 **Green** — Words you've already learned
            - 🔵 **Blue** — Words in the dictionary (click to learn)
            - ⚫ **Gray** — Words not yet in the dictionary
            """)

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
        st.markdown("### 📝 Review Session")

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
                    if st.button("👁️ Show Answer", use_container_width=True):
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
                        ("🙂 Good", 4, col3),
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

# === PAGE: BASHKORTNET EXPLORER (Enhanced with OCM and Neo4j) ===
elif "BashkortNet" in selected_page:
    st.title("🕸️ BashkortNet Explorer (Semantic Network)")
    st.markdown("*Explore the semantic network connecting Bashkir words with OCM cultural classifications.*")

    # Load OCM data
    ocm_data = load_ocm_mapping()
    ocm_labels = ocm_data.get('ocm_labels', {})
    bashkir_to_ocm = ocm_data.get('bashkir_to_ocm', {})

    # Import Neo4j service
    try:
        from modules.neo4j_service import get_neo4j_service, Neo4jConfig
        neo4j_module_available = True
    except ImportError:
        neo4j_module_available = False

    # Neo4j integration section
    st.markdown("---")
    st.markdown("### 🗄️ Neo4j Graph Database Integration")

    if not neo4j_module_available:
        st.warning("⚠️ Neo4j module not available. Install with: `pip install neo4j>=5.0.0`")
    else:
        neo4j_service = get_neo4j_service()

        # Connection status
        neo4j_tabs = st.tabs(["📊 Status", "🔗 Connect", "📤 Export", "🔍 Query"])

        with neo4j_tabs[0]:
            st.markdown("#### Connection Status")
            if neo4j_service.is_connected:
                st.success("✅ Connected to Neo4j")

                # Show statistics
                try:
                    stats = neo4j_service.get_graph_statistics()
                    stat_cols = st.columns(4)
                    with stat_cols[0]:
                        st.metric("Total Words", stats.get('total_words', 0))
                    with stat_cols[1]:
                        st.metric("Total Relations", stats.get('total_relations', 0))
                    with stat_cols[2]:
                        by_locus = stats.get('by_locus', {})
                        st.metric("Locations", len(by_locus))
                    with stat_cols[3]:
                        by_rel = stats.get('by_relation', {})
                        st.metric("Relation Types", len(by_rel))
                except Exception as e:
                    st.error(f"Error fetching stats: {e}")
            else:
                st.info("🔌 Not connected to Neo4j database")
                if neo4j_service.connection_error:
                    st.warning(f"Last error: {neo4j_service.connection_error}")

        with neo4j_tabs[1]:
            st.markdown("#### Connect to Neo4j")
            st.markdown("Configure your Neo4j connection settings below.")

            with st.form("neo4j_connection"):
                neo4j_uri = st.text_input("Neo4j URI", value="bolt://localhost:7687",
                                          help="e.g., bolt://localhost:7687 or neo4j+s://xxx.databases.neo4j.io")
                neo4j_user = st.text_input("Username", value="neo4j")
                neo4j_password = st.text_input("Password", type="password", value="")
                neo4j_database = st.text_input("Database", value="neo4j")

                col1, col2 = st.columns(2)
                with col1:
                    connect_btn = st.form_submit_button("🔗 Connect", use_container_width=True)
                with col2:
                    import_btn = st.form_submit_button("📥 Connect & Import Data", use_container_width=True)

            if connect_btn or import_btn:
                config = Neo4jConfig(
                    uri=neo4j_uri,
                    username=neo4j_user,
                    password=neo4j_password,
                    database=neo4j_database
                )
                neo4j_service.config = config

                with st.spinner("Connecting to Neo4j..."):
                    if neo4j_service.connect():
                        st.success("✅ Connected successfully!")

                        if import_btn:
                            with st.spinner("Setting up schema..."):
                                neo4j_service.setup_schema()

                            with st.spinner("Importing vocabulary data..."):
                                words_imported, relations_created = neo4j_service.import_words(words_data)
                                st.success(f"✅ Imported {words_imported} words and {relations_created} relations!")
                    else:
                        st.error(f"❌ Connection failed: {neo4j_service.connection_error}")

        with neo4j_tabs[2]:
            st.markdown("#### Export to Neo4j Format")
            st.markdown("Generate Cypher statements for importing into Neo4j.")

            export_count = st.slider("Number of words to export", 10, len(words_data), min(50, len(words_data)))

            if st.button("📤 Generate Cypher Export", use_container_width=True):
                with st.spinner("Generating Cypher statements..."):
                    if neo4j_module_available:
                        cypher_export = neo4j_service.generate_cypher_export(words_data[:export_count])
                    else:
                        # Fallback generation
                        cypher_statements = ["// Neo4j Cypher statements for BashkortNet"]
                        for word in words_data[:export_count]:
                            bashkir = word['bashkir'].replace('"', '\\"')
                            english = word.get('english', '').replace('"', '\\"')
                            cypher_statements.append(f'MERGE (w:Word {{bashkir: "{bashkir}"}}) SET w.english = "{english}";')
                        cypher_export = "\n".join(cypher_statements)

                st.code(cypher_export[:3000], language="cypher")
                if len(cypher_export) > 3000:
                    st.caption("*Showing first 3000 characters...*")

                st.download_button(
                    "⬇️ Download Full Cypher File",
                    data=cypher_export,
                    file_name="bashkortnet_export.cypher",
                    mime="text/plain"
                )

        with neo4j_tabs[3]:
            st.markdown("#### Query BashkortNet")

            if neo4j_service.is_connected:
                st.markdown("**Find Path Between Words**")
                path_cols = st.columns(2)
                with path_cols[0]:
                    start_word = st.selectbox("Start word", [w['bashkir'] for w in words_data], key="path_start")
                with path_cols[1]:
                    end_word = st.selectbox("End word", [w['bashkir'] for w in words_data], key="path_end")

                if st.button("🔍 Find Path"):
                    path = neo4j_service.find_path(start_word, end_word)
                    if path:
                        st.success(f"Found path with {len(path)} steps:")
                        for step in path:
                            st.markdown(f"**{step['from']}** —[{step['relation']}]→ **{step['to']}**")
                    else:
                        st.warning("No path found between these words")

                st.markdown("---")
                st.markdown("**Search Words**")
                search_query = st.text_input("Search query", placeholder="Enter Bashkir, English, or Russian...")
                if search_query and st.button("🔍 Search"):
                    results = neo4j_service.search_words(search_query)
                    if results:
                        for r in results[:10]:
                            st.markdown(f"**{r.get('bashkir', '?')}** — {r.get('english', '')} ({r.get('russian', '')})")
                    else:
                        st.info("No results found")
            else:
                st.info("Connect to Neo4j to enable graph queries")

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
                    <span class="bashkir-text">{word_data['bashkir']} (Башҡорт теле)</span>
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
                                    'ANT': '↔️ Antonyms',
                                    'ISA': '⬆️ Is a type of',
                                    'HAS_TYPE': '⬇️ Types',
                                    'PART_OF': '🧩 Part of',
                                    'HAS_PART': '🔧 Has parts',
                                    'CULT_ASSOC': '🏛️ Cultural',
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
                        st.write(f"📍 Locus: {memory_palace.get('locus', 'N/A')}")

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
    tab1, tab2, tab3 = st.tabs(["🔍 Browse by Word", "📊 Browse by OCM", "🎨 Thematic Groups"])

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
                st.markdown(f"## {word_data['bashkir']} — {word_data['english']}")

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
                    st.markdown("### ⚠️ Sensitivity Context")
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
    st.title("🌟 Truth Unveiled — Алтын Яҡты")
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
        <h3 style="color: #d4af37; text-align: center;">✨ Алтын Яҡты — Golden Light ✨</h3>
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
    *This is the anchoring proverb of Golden Light—the Ural-Batyr legacy. It reflects the hero's
    ultimate sacrifice and the enduring Bashkir spirit. When Ural poured the waters of life for
    all rather than drinking them himself, he demonstrated this truth: we live on through what we give.*
    """)

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📜 Proverbs", "⏳ Timeline", "🏔️ Cultural Facts", "🔥 The Duality"])

    with tab1:
        st.markdown("### 📜 Bashkir Proverbs — Мәҡәлдәр")
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
        st.markdown("### ⏳ Historical Timeline — Тарих юлы")
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
        st.markdown("### 🏔️ Cultural Facts — Мәҙәниәт")
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
                <h3>🏔️ URAL</h3>
                <p><strong>The Path of Light</strong></p>
                <hr>
                <p><strong>Choice:</strong> Sacrifice for all</p>
                <p><strong>Symbol:</strong> The Mountains</p>
                <p><strong>Legacy:</strong> Eternal protection</p>
                <hr>
                <p style="font-style: italic;">
                "I am not dying—I am becoming something greater. These mountains will be my body,
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
                — Shulgen's final words
                </p>
                <hr>
                <p><strong>Redemption:</strong> Shulgan-Tash cave holds 16,000-year-old paintings.
                The one who fell guards the ancient memory in darkness.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        ---
        ### The Unity of Opposites

        In Bashkir philosophy, Ural and Shulgen are not simply good and evil—they are
        complementary forces. The mountains rise into light; the caves descend into memory.
        Both are necessary.

        **For twins:** You carry both paths within you. One may be called to shine in the world;
        another may be called to preserve and protect from the depths. Neither path is lesser.
        Together, you form something complete—like the mountains and the caves of Bashkortostan.

        *"Батыр үлмәй, аты ҡала"* — The hero doesn't die, his name remains.
        """)

        st.markdown(f"""
        <div class="meditation-box" style="text-align: center; margin-top: 20px;">
            <p style="font-size: 1.1em;">
                🏔️ The Ural Mountains are Ural-Batyr's body.<br>
                🌊 Shulgan-Tash Cave holds Shulgen's memory.<br>
                🌟 Together, they are Bashkortostan.
            </p>
        </div>
        """, unsafe_allow_html=True)

# === PAGE: SETTINGS ===
elif "Settings" in selected_page:
    st.title("⚙️ Settings")

    st.markdown("### 🎨 Display Settings")

    st.markdown("### 🔊 Audio Settings")
    st.checkbox("Enable audio playback", value=True)
    st.slider("Audio speed", 0.5, 1.5, 1.0)


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

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    **Bashkir Memory Palace** v2.0 Enhanced

    A language learning application integrating:
    - Ibn Arabi's mystical framework (Four Birds)
    - Memory Palace technique (Method of Loci)
    - Anthropological pedagogy (OCM/eHRAF 2021 methodology)
    - Spaced Repetition (SM-2 algorithm)
    - BashkortNet semantic network
    - Audio export for sentences and poems

    *"The journey made within yourself leads to yourself."*
    — Ibn Arabi, Secrets of Voyaging
    """)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>🏰 Bashkir Memory Palace — <em>Secrets of Voyaging</em></p>
    <p>🦅 Eagle · 🐦⬛ Crow · 🔥🕊️ Anqa · 🕊️ Ringdove</p>
    <p><em>"Voyaging has no end, for therein is the joy of the Real."</em></p>
</div>
""", unsafe_allow_html=True)
