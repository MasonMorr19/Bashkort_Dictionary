"""
Memory Palace — Ufa Layer (Nested Hearth Architecture)
=======================================================
Geographic memory palace mapping physical locations in Ufa, Bashkortostan
to vocabulary stations for language learning.

Architecture:
    Bizhbulyak (personal anchor) → **Ufa (cultural hearth)** → Universal (anthropological layer)

This module covers the Ufa layer. Each physical location becomes a locus in the
memory palace where Bashkir vocabulary is stored. The whole structure exports to
Knight Lab StoryMapJS for the anthropological StoryMap project
"The Knowledge Bridge: Bashkortostan ↔ America."

Features:
- Dataclass-based station model with parent/child relationships
- Pre-populated stations at real Ufa landmarks
- Guided walking tour through stations in geographic order
- Vocabulary attachment to any station
- Knight Lab StoryMapJS JSON export
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ── Theme enum ──────────────────────────────────────────────────────────────

VALID_THEMES = {
    "mythology", "commerce", "food", "historic_trade", "performance",
    "hockey", "hero_identity", "language_history", "artifacts",
    "sacred_islam", "history_colonialism", "politics",
}


# ── Data models ─────────────────────────────────────────────────────────────

@dataclass
class VocabularyWord:
    """A Bashkir vocabulary word attached to a memory palace station."""
    bashkir: str
    russian: str = ""
    english: str = ""
    mnemonic: str = ""

    def to_dict(self) -> Dict:
        return {
            "bashkir": self.bashkir,
            "russian": self.russian,
            "english": self.english,
            "mnemonic": self.mnemonic,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VocabularyWord":
        return cls(
            bashkir=data["bashkir"],
            russian=data.get("russian", ""),
            english=data.get("english", ""),
            mnemonic=data.get("mnemonic", ""),
        )


@dataclass
class KnightLabSlide:
    """Metadata formatted for Knight Lab StoryMapJS export."""
    title: str
    text: str
    media_url: str = ""
    media_caption: str = ""
    location_lat: float = 0.0
    location_lon: float = 0.0
    zoom: int = 15

    def to_dict(self) -> Dict:
        slide: Dict = {
            "text": {
                "headline": self.title,
                "text": self.text,
            },
            "location": {
                "lat": self.location_lat,
                "lon": self.location_lon,
                "zoom": self.zoom,
            },
        }
        if self.media_url:
            slide["media"] = {
                "url": self.media_url,
                "caption": self.media_caption,
            }
        return slide


@dataclass
class Station:
    """A memory palace station — a real place in Ufa.

    Each station holds Bashkir vocabulary words, a mnemonic note tying the
    place to language learning, and metadata for StoryMapJS export.
    """
    id: str
    name_en: str
    name_local: str
    address: str
    lat: float
    lng: float
    theme: str
    mnemonic_note: str = ""
    parent_station_id: Optional[str] = None
    vocabulary_words: List[VocabularyWord] = field(default_factory=list)
    knightlab_slide: Optional[KnightLabSlide] = None

    def __post_init__(self) -> None:
        if self.knightlab_slide is None:
            self.knightlab_slide = KnightLabSlide(
                title=self.name_en,
                text=self._build_slide_text(),
                location_lat=self.lat,
                location_lon=self.lng,
            )

    def _build_slide_text(self) -> str:
        """Generate default StoryMapJS slide text from station data."""
        parts = [f"<b>{self.name_local}</b>"]
        if self.address:
            parts.append(f"<br>{self.address}")
        if self.mnemonic_note:
            parts.append(f"<p><em>{self.mnemonic_note}</em></p>")
        if self.vocabulary_words:
            words = ", ".join(w.bashkir for w in self.vocabulary_words)
            parts.append(f"<p><strong>Vocabulary:</strong> {words}</p>")
        return "".join(parts)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name_en": self.name_en,
            "name_local": self.name_local,
            "address": self.address,
            "lat": self.lat,
            "lng": self.lng,
            "theme": self.theme,
            "mnemonic_note": self.mnemonic_note,
            "parent_station_id": self.parent_station_id,
            "vocabulary_words": [w.to_dict() for w in self.vocabulary_words],
            "knightlab_slide": self.knightlab_slide.to_dict() if self.knightlab_slide else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Station":
        vocab = [VocabularyWord.from_dict(w) for w in data.get("vocabulary_words", [])]
        kl = data.get("knightlab_slide")
        knightlab = None
        if kl:
            knightlab = KnightLabSlide(
                title=kl["text"]["headline"],
                text=kl["text"]["text"],
                media_url=kl.get("media", {}).get("url", ""),
                media_caption=kl.get("media", {}).get("caption", ""),
                location_lat=kl["location"]["lat"],
                location_lon=kl["location"]["lon"],
                zoom=kl["location"].get("zoom", 15),
            )
        return cls(
            id=data["id"],
            name_en=data["name_en"],
            name_local=data["name_local"],
            address=data.get("address", ""),
            lat=data["lat"],
            lng=data["lng"],
            theme=data["theme"],
            mnemonic_note=data.get("mnemonic_note", ""),
            parent_station_id=data.get("parent_station_id"),
            vocabulary_words=vocab,
            knightlab_slide=knightlab,
        )


# ── Memory Palace ───────────────────────────────────────────────────────────

class MemoryPalaceUfa:
    """Geographic memory palace for Ufa, Bashkortostan.

    The Ufa layer of the Nested Hearth Architecture maps real landmarks
    to vocabulary stations.  Stations can be walked in geographic order,
    queried by theme, and exported to Knight Lab StoryMapJS JSON.
    """

    def __init__(self, stations: Optional[List[Station]] = None) -> None:
        self._stations: Dict[str, Station] = {}
        for s in (stations or []):
            self._stations[s.id] = s

    # ── Station access ──────────────────────────────────────────────────

    @property
    def stations(self) -> List[Station]:
        """All stations sorted by id."""
        return sorted(self._stations.values(), key=lambda s: s.id)

    def get_station(self, station_id: str) -> Optional[Station]:
        """Look up a station by its id."""
        return self._stations.get(station_id)

    def get_station_by_name(self, name: str) -> Optional[Station]:
        """Look up a station by English or local name (case-insensitive)."""
        lower = name.lower()
        for s in self._stations.values():
            if s.name_en.lower() == lower or s.name_local.lower() == lower:
                return s
        return None

    def get_children(self, parent_id: str) -> List[Station]:
        """Return sub-stations whose parent_station_id matches *parent_id*."""
        return [s for s in self._stations.values() if s.parent_station_id == parent_id]

    def get_stations_by_theme(self, theme: str) -> List[Station]:
        """Return all stations matching a given theme."""
        return [s for s in self._stations.values() if s.theme == theme]

    # ── Vocabulary management ───────────────────────────────────────────

    def add_vocabulary(
        self,
        station_name: str,
        bashkir_word: str,
        russian_word: str = "",
        english_word: str = "",
        mnemonic: str = "",
    ) -> bool:
        """Attach a new vocabulary word to a station.

        Args:
            station_name: English name of the target station.
            bashkir_word: The Bashkir word to add.
            russian_word: Russian translation.
            english_word: English translation.
            mnemonic: Personal memory hook for this word at this station.

        Returns:
            True if the word was added, False if the station was not found.
        """
        station = self.get_station_by_name(station_name)
        if station is None:
            return False
        station.vocabulary_words.append(
            VocabularyWord(
                bashkir=bashkir_word,
                russian=russian_word,
                english=english_word,
                mnemonic=mnemonic,
            )
        )
        # Refresh the KnightLab slide text to include new vocabulary
        if station.knightlab_slide:
            station.knightlab_slide.text = station._build_slide_text()
        return True

    # ── Walking tour ────────────────────────────────────────────────────

    def _walking_order(self) -> List[Station]:
        """Return stations in a logical south-to-north walking route.

        The route follows a geographic walk through Ufa:
        Monument Druzhby (south, river) → Congress Hall → Salavat Yulaev
        Monument → Seven Girls Fountain (and sub-stations) → National Museum
        → Museum of Archaeology → Ufa Arena (northeast) → Lala Tulpan Mosque
        (far northeast).
        """
        order = [
            "monument_druzhby",
            "congress_hall",
            "salavat_yulaev_monument",
            "seven_girls_fountain",
            "oufa_america",
            "barakat_restaurant",
            "gostiny_dvor",
            "bashkir_opera_ballet",
            "national_museum",
            "museum_archaeology",
            "ufa_arena",
            "lala_tulpan_mosque",
        ]
        ordered: List[Station] = []
        for sid in order:
            if sid in self._stations:
                ordered.append(self._stations[sid])
        # Append any stations not explicitly ordered
        remaining = [s for s in self._stations.values() if s.id not in order]
        remaining.sort(key=lambda s: s.lat)
        ordered.extend(remaining)
        return ordered

    def walk_palace(self, start_station: Optional[str] = None) -> str:
        """Return a guided walk through the memory palace.

        Prints each station with its Bashkir vocabulary in geographic order
        (south to north, following a logical walking route through Ufa).

        Args:
            start_station: Optional English name of a station to start from.
                If None, the walk starts from the southernmost station.

        Returns:
            The full guided-walk text.
        """
        route = self._walking_order()
        if start_station:
            start_idx = None
            lower = start_station.lower()
            for i, s in enumerate(route):
                if s.name_en.lower() == lower or s.name_local.lower() == lower:
                    start_idx = i
                    break
            if start_idx is not None:
                route = route[start_idx:] + route[:start_idx]

        lines: List[str] = []
        lines.append("=" * 68)
        lines.append("  MEMORY PALACE OF UFA — Nested Hearth Architecture (Ufa Layer)")
        lines.append("  The Knowledge Bridge: Bashkortostan ↔ America")
        lines.append("=" * 68)
        lines.append("")

        for i, station in enumerate(route, 1):
            indent = "    " if station.parent_station_id else ""
            prefix = f"  ↳ Sub-station {i}" if station.parent_station_id else f"  Station {i}"

            lines.append(f"{indent}{prefix}: {station.name_en}")
            lines.append(f"{indent}  ({station.name_local})")
            lines.append(f"{indent}  Theme: {station.theme}")
            if station.address:
                lines.append(f"{indent}  Address: {station.address}")
            lines.append(f"{indent}  Coords: {station.lat:.4f}°N, {station.lng:.4f}°E")

            if station.mnemonic_note:
                lines.append(f"{indent}  Note: {station.mnemonic_note}")

            if station.vocabulary_words:
                lines.append(f"{indent}  Vocabulary:")
                for w in station.vocabulary_words:
                    parts = [f"    {w.bashkir}"]
                    if w.russian:
                        parts.append(f" / {w.russian}")
                    if w.english:
                        parts.append(f" — {w.english}")
                    if w.mnemonic:
                        parts.append(f"  [{w.mnemonic}]")
                    lines.append(f"{indent}  {''.join(parts)}")
            else:
                lines.append(f"{indent}  (no vocabulary attached yet)")

            lines.append("")

        lines.append("=" * 68)
        lines.append("  End of walk. Review your vocabulary and revisit weak stations.")
        lines.append("=" * 68)

        text = "\n".join(lines)
        print(text)
        return text

    # ── KnightLab StoryMapJS export ─────────────────────────────────────

    def export_to_knightlab_json(self, filepath: Optional[str] = None) -> Dict:
        """Export the memory palace to Knight Lab StoryMapJS JSON format.

        Args:
            filepath: Optional path to write the JSON file. If None, only
                the dict is returned.

        Returns:
            The StoryMapJS-compatible dict.
        """
        route = self._walking_order()

        # Overview slide
        overview_slide: Dict = {
            "type": "overview",
            "text": {
                "headline": "The Knowledge Bridge: Bashkortostan ↔ America",
                "text": (
                    "A geographic memory palace through Ufa, capital of "
                    "Bashkortostan. Each station is a real landmark where "
                    "Bashkir vocabulary is anchored to place, history, and "
                    "personal mnemonic. Part of the Nested Hearth Architecture: "
                    "Bizhbulyak (personal anchor) → Ufa (cultural hearth) → "
                    "Universal (anthropological layer)."
                ),
            },
            "location": {
                "lat": 54.7350,
                "lon": 55.9580,
            },
        }

        slides = [overview_slide]
        for station in route:
            if station.knightlab_slide:
                slide = station.knightlab_slide.to_dict()
            else:
                slide = {
                    "text": {
                        "headline": station.name_en,
                        "text": station.mnemonic_note or station.name_local,
                    },
                    "location": {
                        "lat": station.lat,
                        "lon": station.lng,
                        "zoom": 15,
                    },
                }
            slides.append(slide)

        storymap: Dict = {"storymap": {"slides": slides}}

        if filepath:
            out = Path(filepath)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(storymap, f, ensure_ascii=False, indent=2)

        return storymap

    # ── Serialization ───────────────────────────────────────────────────

    def to_dict(self) -> Dict:
        """Serialize the entire palace to a plain dict."""
        return {
            "palace": "ufa",
            "architecture": "nested_hearth",
            "layer": "cultural_hearth",
            "stations": [s.to_dict() for s in self.stations],
        }

    def save(self, filepath: str) -> None:
        """Persist the palace to a JSON file."""
        out = Path(filepath)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "MemoryPalaceUfa":
        """Load a palace from a previously saved JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        stations = [Station.from_dict(s) for s in data.get("stations", [])]
        return cls(stations=stations)


# ── Default palace ──────────────────────────────────────────────────────────

def _build_default_palace() -> MemoryPalaceUfa:
    """Construct the pre-populated Ufa memory palace."""

    stations: List[Station] = []

    # ── Seven Girls Fountain ────────────────────────────────────────────
    stations.append(Station(
        id="seven_girls_fountain",
        name_en="Seven Girls Fountain",
        name_local="Ете ҡыҙ фонтаны",
        address="Lenina Ave, Theatre Square, Ufa",
        lat=54.7248,
        lng=55.9440,
        theme="mythology",
        mnemonic_note=(
            "Seven sisters chose death over captivity — became stars. "
            "Gaskarov choreographed their legend into dance. "
            "Fountain opened 2015 for BRICS summit."
        ),
    ))

    # Sub-station: Oufa America
    stations.append(Station(
        id="oufa_america",
        name_en="Oufa America",
        name_local="Oufa America",
        address="Verkhnetorgovaya pl. 4, ent.1, fl.4, office 410",
        lat=54.7234,
        lng=55.9430,
        theme="commerce",
        parent_station_id="seven_girls_fountain",
        mnemonic_note=(
            "Physical bridge — American goods imported to the heart of Ufa. "
            "Upper TRADE Square. Entrance 1, Floor 4, Office 410 — the 4s repeat."
        ),
    ))

    # Sub-station: Barakat Restaurant
    stations.append(Station(
        id="barakat_restaurant",
        name_en="Barakat Restaurant",
        name_local="Барakat ресторан",
        address="Verkhnetorgovaya pl. 3",
        lat=54.7237,
        lng=55.9428,
        theme="food",
        parent_station_id="seven_girls_fountain",
    ))

    # Sub-station: Gostiny Dvor
    stations.append(Station(
        id="gostiny_dvor",
        name_en="Gostiny Dvor",
        name_local="Гостиный двор",
        address="Verkhnetorgovaya area",
        lat=54.7240,
        lng=55.9445,
        theme="historic_trade",
        parent_station_id="seven_girls_fountain",
    ))

    # Sub-station: Bashkir Opera & Ballet Theatre
    stations.append(Station(
        id="bashkir_opera_ballet",
        name_en="Bashkir Opera & Ballet Theatre",
        name_local="Башҡорт опера һәм балет театры",
        address="Theatre Square",
        lat=54.7252,
        lng=55.9435,
        theme="performance",
        parent_station_id="seven_girls_fountain",
        mnemonic_note=(
            "Rudolf Nureyev bas-relief here. "
            "Gaskarov's Seven Girls dance originated here."
        ),
    ))

    # ── Ufa Arena ───────────────────────────────────────────────────────
    stations.append(Station(
        id="ufa_arena",
        name_en="Ufa Arena",
        name_local="Өфө-Арена",
        address="Lenina st. 114, Ufa",
        lat=54.7332,
        lng=55.9783,
        theme="hockey",
        mnemonic_note=(
            "8,522 seats. Home of Salavat Yulaev since 2007. "
            "Kuznetsov's bird celly in green. "
            "Alexei Vasilevskiy guards this net."
        ),
    ))

    # ── Salavat Yulaev Monument ─────────────────────────────────────────
    stations.append(Station(
        id="salavat_yulaev_monument",
        name_en="Salavat Yulaev Monument",
        name_local="Салауат Юлаев һәйкәле",
        address="Salavat Yulaev Square, Belaya River bluff",
        lat=54.7192,
        lng=55.9243,
        theme="hero_identity",
        mnemonic_note=(
            "9-meter bronze on horseback, 1967. Only 3 points of support. "
            "Overlooks Agidel (Belaya) River. "
            "The hero who fought Catherine the Great."
        ),
    ))

    # ── National Museum of Bashkortostan ────────────────────────────────
    stations.append(Station(
        id="national_museum",
        name_en="National Museum of Bashkortostan",
        name_local="Башҡортостан Милли музейы",
        address="near Sovetskaya, Ufa",
        lat=54.7223,
        lng=55.9477,
        theme="language_history",
        mnemonic_note=(
            "Salavat Yulaev's saber and saddle. Burzyan bee exhibit. "
            "Geological and archaeological finds. "
            "Ibn Fadlan recorded first info about region in 922 AD."
        ),
    ))

    # ── Museum of Archaeology & Ethnography ─────────────────────────────
    stations.append(Station(
        id="museum_archaeology",
        name_en="Museum of Archaeology & Ethnography",
        name_local="Археология һәм этнография музейы",
        address="Ufa",
        lat=54.7270,
        lng=55.9500,
        theme="artifacts",
        mnemonic_note=(
            "Traditional garb, handicrafts, fossils. "
            "525m from Verkhnetorgovaya Square."
        ),
    ))

    # ── Lala Tulpan Mosque ──────────────────────────────────────────────
    stations.append(Station(
        id="lala_tulpan_mosque",
        name_en="Lala Tulpan Mosque",
        name_local="Ләлә Тюльпан мәсете",
        address="Ufa",
        lat=54.7505,
        lng=56.0175,
        theme="sacred_islam",
        mnemonic_note=(
            "Tulip-shaped 53m twin minarets. One of Russia's largest mosques. "
            "Holds 1000 worshippers. Built 1998. Modern Islamic architecture."
        ),
    ))

    # ── Monument Druzhby ────────────────────────────────────────────────
    stations.append(Station(
        id="monument_druzhby",
        name_en="Monument Druzhby",
        name_local="Дуҫлыҡ монументы",
        address="Ufa",
        lat=54.7138,
        lng=55.9225,
        theme="history_colonialism",
        mnemonic_note=(
            "Built on site of former Ufa Kremlin (16th century fortress). "
            "Spire commemorates 'voluntary accession' to Russia — contested framing. "
            "Overlooks Belaya River."
        ),
    ))

    # ── Congress Hall ───────────────────────────────────────────────────
    stations.append(Station(
        id="congress_hall",
        name_en="Congress Hall",
        name_local="Конгресс-холл",
        address="Ufa",
        lat=54.7197,
        lng=55.9245,
        theme="politics",
        mnemonic_note="Near Salavat Yulaev monument. Modern political/conference center.",
    ))

    return MemoryPalaceUfa(stations=stations)


def get_default_palace() -> MemoryPalaceUfa:
    """Return the pre-populated Ufa memory palace.

    This is the main entry point. Call this to get a fully loaded palace
    with all default stations, then use ``add_vocabulary`` and
    ``walk_palace`` to interact with it.
    """
    return _build_default_palace()
