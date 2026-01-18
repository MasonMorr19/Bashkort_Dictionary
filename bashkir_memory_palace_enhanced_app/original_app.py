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

Enhanced with retry logic and network resilience from Bilingual Audio Dictionary.
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


def generate_audio_with_retry(text: str, slow: bool = True) -> bytes:
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
            tts = gTTS(text=text, lang='ru', slow=slow)
            tts.save(str(cache_file))

            with open(cache_file, 'rb') as f:
                return f.read()

        except Exception as e:
            if attempt >= config.max_retries:
                return None

            delay = config.base_delay * (config.exponential_base ** attempt)
            time.sleep(delay)

    return None


def play_audio(text: str, slow: bool = True):
    """Generate and play audio for Bashkir text with caching and retry logic."""
    if not AUDIO_AVAILABLE:
        st.warning("🔇 Audio unavailable. Install with: `pip install gTTS`")
        return

    audio_bytes = generate_audio_with_retry(text, slow)

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

# Navigation
pages = ["🗺️ Palace", "📚 Four Birds", "✍️ Sentence Builder", 
         "🔄 Review", "🕸️ BashkortNet", "📖 Cultural Context", "⚙️ Settings"]

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
            "Ufa": "🦅 Өфө – Eagle's Perch (Civic)",
            "Shulgan-Tash": "🐦⬛ Шүлгәнташ – Crow's Archive (Ancestry)",
            "Yamantau": "🔥🕊️ Ямантау – Anqa's Ascent (Mystery)",
            "Beloretsk": "🕊️ Белорет – Ringdove's Forge (Labor)",
            "Bizhbulyak": "🕊️ Бижбуляк – Ringdove's Hearth (Home)"
        }
        
        selected_locus = st.selectbox(
            "Select Location",
            locus_options,
            format_func=lambda x: locus_display.get(x, x)
        )
    
    with col2:
        if selected_locus:
            locus = loci_data[selected_locus]
            st.markdown(f"### {locus['symbol']} {locus['bird']}")
            st.markdown(f"*{locus['description']['short']}*")
    
    st.markdown("---")
    
    # Display selected locus
    if selected_locus:
        locus = loci_data[selected_locus]
        
        # Ibn Arabi connection
        with st.expander("🌟 Ibn Arabi's Teaching", expanded=False):
            st.markdown(f"""
            <div class="meditation-box">
            {locus['description']['ibn_arabi_connection']}
            </div>
            """, unsafe_allow_html=True)
        
        # Station walkthrough
        st.markdown("### 🚶 Station Walkthrough")
        
        for station in locus.get('stations', []):
            station_name = station['display_name']
            station_words = station['words']
            
            with st.expander(f"📍 Station {station['number']}: {station_name}", expanded=True):
                # Opening meditation
                st.markdown(f"""
                <div class="meditation-box">
                <strong>🕯️ Opening Meditation:</strong><br>
                {station['opening_meditation']}
                </div>
                """, unsafe_allow_html=True)
                
                # Words in this station
                st.markdown("#### Words at this Station:")
                
                # Create word cards - FIXED HTML RENDERING
                words_at_station = [w for w in words_data if w['bashkir'] in station_words]
                
                cols = st.columns(min(3, len(words_at_station) if words_at_station else 1))
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
                
                # Closing meditation
                st.markdown(f"""
                <div class="meditation-box">
                <strong>🕯️ Closing Meditation:</strong><br>
                {station['closing_meditation']}
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

# === PAGE: SENTENCE BUILDER ===
elif "Sentence Builder" in selected_page:
    st.title("✍️ Sentence Builder")
    st.markdown("*Create your own Bashkir sentences and hear them spoken.*")
    
    patterns = load_patterns()
    
    # Current sentence
    if 'builder_sentence' not in st.session_state:
        st.session_state.builder_sentence = []
    
    # Pattern templates
    st.markdown("### 📝 Sentence Patterns")
    
    pattern_list = patterns.get('patterns', [])[:5]
    
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
    
    # Word bank
    st.markdown("### 🏦 Word Bank")
    st.markdown("Click words to add them to your sentence:")
    
    word_categories = patterns.get('word_bank_categories', {})
    
    tabs = st.tabs(list(word_categories.keys()))
    
    for tab, (category, word_list) in zip(tabs, word_categories.items()):
        with tab:
            cols = st.columns(6)
            for idx, word in enumerate(word_list):
                with cols[idx % 6]:
                    word_data = next((w for w in words_data if w['bashkir'] == word), None)
                    english = word_data.get('english', '?') if word_data else '?'
                    
                    if st.button(f"{word}\n({english})", key=f"word_{category}_{word}"):
                        st.session_state.builder_sentence.append({
                            'word': word,
                            'english': english
                        })
                        st.rerun()
    
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
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔊 Hear Sentence"):
                play_audio(sentence_text, slow=False)
        
        with col2:
            if st.button("💾 Save Sentence"):
                st.session_state.saved_sentences.append({
                    'bashkir': sentence_text,
                    'gloss': gloss_text,
                    'created': datetime.now().isoformat()
                })
                st.success("Sentence saved to your phrasebook!")
        
        with col3:
            if st.button("🗑️ Clear"):
                st.session_state.builder_sentence = []
                st.rerun()
        
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
    
    # Saved sentences
    if st.session_state.saved_sentences:
        st.markdown("---")
        st.markdown("### 📒 Your Phrasebook")
        
        for idx, sentence in enumerate(st.session_state.saved_sentences[-5:]):
            st.markdown(f"""
            <div class="word-card">
                <strong>{sentence['bashkir']}</strong><br>
                <small>{sentence['gloss']}</small>
            </div>
            """, unsafe_allow_html=True)

# === PAGE: REVIEW ===
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
                
                # Progress
                progress = (st.session_state.review_index + 1) / len(st.session_state.review_queue)
                st.progress(progress)
                st.caption(f"Card {st.session_state.review_index + 1} of {len(st.session_state.review_queue)}")
        else:
            st.success("🎉 Review session complete!")
            if st.button("Start New Session"):
                st.session_state.review_index = 0
                st.session_state.show_answer = False
                st.rerun()
    else:
        st.info("No words to review! Visit the Palace to learn new words.")
        if st.button("Go to Palace"):
            st.session_state.current_page = "Palace"
            st.rerun()

# === PAGE: BASHKORTNET ===
elif "BashkortNet" in selected_page:
    st.title("🕸️ BashkortNet Explorer")
    st.markdown("*Explore the semantic network connecting Bashkir words.*")
    
    # Word search
    search_word = st.selectbox(
        "Select a word to explore:",
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
                    <span class="bashkir-text">{word_data['bashkir']}</span>
                    <br>
                    <small>{word_data.get('ipa', '')}</small>
                    <br><br>
                    <strong>{word_data['english']}</strong>
                    <br>
                    <em>{word_data.get('russian', '')}</em>
                    <br><br>
                    <small>POS: {word_data.get('pos', 'noun')}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
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
                                    note = target.get('note', '')
                                    st.markdown(f"- {target_word}" + (f" *({note})*" if note else ""))
                                else:
                                    st.markdown(f"- {target}")
                else:
                    st.info("No relations defined for this word yet.")
                
                # Etymology
                etymology = bashkortnet.get('etymology', {})
                if etymology:
                    st.markdown("### 📚 Etymology")
                    proto = etymology.get('proto_form', '')
                    lang = etymology.get('proto_language', '')
                    st.markdown(f"**Proto-form:** {proto} ({lang})")

# === PAGE: CULTURAL CONTEXT ===
elif "Cultural Context" in selected_page:
    st.title("📖 Cultural Context")
    st.markdown("*Understand the anthropological depth behind each word.*")
    
    # Truth Unveiled toggle
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔓 Truth Unveiled")
    st.session_state.truth_unveiled = st.sidebar.toggle(
        "Show sensitive sources",
        value=st.session_state.truth_unveiled,
        help="Enable to see academic sources that may be politically sensitive"
    )
    
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
            ocm_codes = cultural.get('ocm_codes', [])
            if ocm_codes:
                st.markdown("### 🏷️ OCM Categories")
                ocm_labels = {
                    '131': 'Geography - Mountains',
                    '133': 'Geography - Rivers/Lakes',
                    '222': 'Food Processing',
                    '225': 'Food Storage',
                    '231': 'Domesticated Animals',
                    '325': 'Metallurgy',
                    '341': 'Dwellings',
                    '342': 'Housing',
                    '462': 'Division of Labor',
                    '464': 'Manufacturing',
                    '527': 'Festivals',
                    '533': 'Music',
                    '541': 'Spectacles',
                    '593': 'Family',
                    '594': 'Kinship',
                    '619': 'Government',
                    '648': 'Legal',
                    '669': 'Law',
                    '670': 'Language',
                    '773': 'Mythology',
                    '778': 'Sacred/Taboo',
                    '784': 'Ethnic Movements',
                    '821': 'Astronomy',
                    '824': 'Danger'
                }
                
                for code in ocm_codes:
                    label = ocm_labels.get(code, f"Category {code}")
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
    **Bashkir Memory Palace** v1.0
    
    A language learning application integrating:
    - Ibn Arabi's mystical framework (Four Birds)
    - Memory Palace technique (Method of Loci)
    - Anthropological pedagogy (OCM/eHRAF methodology)
    - Spaced Repetition (SM-2 algorithm)
    - BashkortNet semantic network
    
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
