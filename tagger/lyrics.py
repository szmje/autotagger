import re
import json
from pathlib import Path
from typing import Optional, Tuple
import syncedlyrics

from tagger.models import TrackMetadata

import sys

if getattr(sys, "frozen", False):
    CACHE_FILE = Path(sys.executable).resolve().parent / ".lyrics_cache.json"
else:
    CACHE_FILE = Path(__file__).resolve().parent.parent / ".lyrics_cache.json"

class LyricsManager:
    def __init__(self):
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def fetch_lyrics(self, artist: str, title: str, album: Optional[str] = None) -> Optional[str]:
        """
        Fetches synced (or plain) lyrics for a track.
        Returns the lyrics string (often in .lrc format with timestamps), or None.
        """
        # Clean artist (take first artist if multiple for better lyrics match)
        first_artist = re.split(r'\s*(?:;|&|feat\.|ft\.|with|,|\/)\s*', artist)[0].strip()
        query = f"{first_artist} {title}".strip()
        cache_key = query.lower()

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # 1. Try synced lyrics first
            lrc = syncedlyrics.search(query, synced_only=True)
            if not lrc:
                # 2. Fallback to plain lyrics
                lrc = syncedlyrics.search(query, synced_only=False)

            if lrc and len(lrc.strip()) > 20:
                self.cache[cache_key] = lrc
                self._save_cache()
                return lrc
        except Exception as e:
            print(f"Error fetching lyrics for {query}: {e}")

        return None

    def save_lrc_file(self, audio_file_path: Path, lyrics_text: str) -> Optional[Path]:
        """
        Saves lyrics_text into a .lrc file next to the audio file.
        e.g. '01. bladee - obedient.lrc'
        """
        if not lyrics_text:
            return None
        lrc_path = audio_file_path.with_suffix(".lrc")
        try:
            lrc_path.write_text(lyrics_text, encoding="utf-8")
            return lrc_path
        except Exception as e:
            print(f"Error saving .lrc file to {lrc_path}: {e}")
            return None
