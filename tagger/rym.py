import re
import json
import urllib.parse
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from curl_cffi import requests
from bs4 import BeautifulSoup

CACHE_FILE = Path(__file__).resolve().parent.parent / ".rym_cache.json"

class RYMGenreFetcher:
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

    def _normalize_artist(self, artist: str) -> str:
        # Take primary artist if joined with semicolons or ampersand for search query
        for sep in [";", "&", "feat.", "ft.", "with", "/"]:
            if sep in artist:
                artist = artist.split(sep)[0].strip()
        return artist

    def _clean_genres(self, raw_genres: List[str]) -> List[str]:
        # Words that indicate credits or metadata, not genres
        exclude_words = {
            "vocals", "writer", "producer", "mixing", "mastering", "cover art",
            "featured", "performer", "performers", "rated", "album", "reviews",
            "ratings", "release", "rate your music", "sonemic", "track", "tracks",
            "page", "buy", "lists", "catalog", "year", "label", "credits"
        }
        cleaned = []
        for g in raw_genres:
            # Strip trailing metadata text
            g = re.sub(r'\s+(Rated|Featured|Release|Produced|Members|Reviews|Ratings|Tracklist|Catalog|Track|Writer).*', '', g, flags=re.IGNORECASE)
            # Remove punctuation
            g = g.strip().strip(".,;:!?()[]{}'\"")
            g_lower = g.lower()
            if (
                g_lower
                and 2 < len(g_lower) < 40
                and "..." not in g_lower
                and not any(bad in g_lower for bad in exclude_words)
            ):
                if g_lower not in cleaned:
                    cleaned.append(g_lower)
        return cleaned

    def _extract_from_text(self, text: str) -> List[str]:
        genres = []
        # Pattern 1: Genres: Pop, Rock, Synthpop
        for m in re.finditer(r'Genres:\s*([^\.\n\r]+)', text, re.IGNORECASE):
            raw = m.group(1)
            # Cut if "Rated" or "Featured" or "Release" occurs inside
            raw = re.split(r'\b(Rated|Featured|Release|Produced|Members|Credits)\b', raw, flags=re.IGNORECASE)[0]
            for item in raw.split(','):
                genres.append(item)

        # Pattern 2: (Album, Synthpop, Dance-Pop) - only if no ellipsis
        for m2 in re.finditer(r'\(Album,\s*([^)\n\r.]{3,60})\)', text, re.IGNORECASE):
            raw2 = m2.group(1)
            if "..." not in raw2:
                for item in raw2.split(','):
                    genres.append(item)

        return self._clean_genres(genres)

    def search_yahoo(self, artist: str, album: str) -> List[str]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        queries = [
            f'site:rateyourmusic.com/release/ "{artist}" "{album}"',
            f'site:rateyourmusic.com/release/ {artist} {album}',
            f'site:rateyourmusic.com "{artist}" "{album}"'
        ]
        for q in queries:
            try:
                url = f"https://search.yahoo.com/search?p={urllib.parse.quote(q)}"
                r = requests.get(url, impersonate='chrome124', headers=headers, timeout=9)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    genres = []
                    for div in soup.select('div.algo'):
                        t = div.select_one('h3')
                        comp = div.select_one('.compText')
                        combined = f"{t.get_text(' ') if t else ''} {comp.get_text(' ') if comp else ''}"
                        genres.extend(self._extract_from_text(combined))
                    if genres:
                        return self._clean_genres(genres)
            except Exception:
                continue
        return []

    def search_ddg(self, artist: str, album: str) -> List[str]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        queries = [
            f'site:rateyourmusic.com/release/ "{artist}" "{album}"',
            f'site:rateyourmusic.com/release/ {artist} {album}',
        ]
        for q in queries:
            try:
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
                r = requests.get(url, impersonate='chrome124', headers=headers, timeout=9)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    genres = []
                    for b in soup.select('.result__body'):
                        t = b.select_one('.result__title')
                        s = b.select_one('.result__snippet')
                        combined = f"{t.get_text(' ') if t else ''} {s.get_text(' ') if s else ''}"
                        genres.extend(self._extract_from_text(combined))
                    if genres:
                        return self._clean_genres(genres)
            except Exception:
                continue
        return []

    def get_album_genres(self, artist: str, album: str) -> List[str]:
        cache_key = f"{artist.lower().strip()} - {album.lower().strip()}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        genres = []
        # Try Yahoo first (most reliable snippet format with RYM genres)
        genres = self.search_yahoo(artist, album)
        
        # If not found, try searching with normalized first artist
        if not genres:
            first_artist = self._normalize_artist(artist)
            if first_artist.lower() != artist.lower():
                genres = self.search_yahoo(first_artist, album)

        # Fallback to DuckDuckGo
        if not genres:
            genres = self.search_ddg(artist, album)

        if not genres and first_artist != artist:
            genres = self.search_ddg(first_artist, album)

        if genres:
            self.cache[cache_key] = genres
            self._save_cache()

        return genres

    def get_formatted_genre_string(self, artist: str, album: str) -> str:
        """Returns lowercase RYM genres separated by '; '."""
        genres = self.get_album_genres(artist, album)
        if not genres:
            return ""
        return "; ".join(genres)

    def parse_rym_url(self, url: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Extracts (artist, album, genres_str) from a RateYourMusic release URL.
        e.g. https://rateyourmusic.com/release/album/yung-lean-bladee/psykos/
        """
        m = re.search(r'/release/(?:album|single|mixtape|ep)/([^/]+)/([^/]+)', url)
        if not m:
            return None, None, ""

        artist_slug, album_slug = m.group(1), m.group(2)
        q = f'site:rateyourmusic.com/release/ {artist_slug} {album_slug}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        
        extracted_artist = None
        extracted_album = None
        genres = []

        try:
            r = requests.get(f'https://search.yahoo.com/search?p={urllib.parse.quote(q)}', impersonate='chrome124', headers=headers, timeout=8)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for div in soup.select('div.algo'):
                    t = div.select_one('h3')
                    comp = div.select_one('.compText')
                    combined = f"{t.get_text(' ') if t else ''} {comp.get_text(' ') if comp else ''}"
                    
                    if not extracted_album and t:
                        text = t.get_text(' ')
                        m_title = re.search(r'^(.*?)\s+by\s+(.*?)\s*\(Album', text, re.IGNORECASE)
                        if m_title:
                            extracted_album = m_title.group(1).strip()
                            raw_art = m_title.group(2).strip()
                            # Normalize artists with '; '
                            parts = re.split(r'\s*(?:;|&|feat\.|ft\.|with|,|\/)\s*', raw_art, flags=re.IGNORECASE)
                            extracted_artist = "; ".join(p.strip() for p in parts if p.strip())

                    g_list = self._extract_from_text(combined)
                    if g_list:
                        genres.extend(g_list)
        except Exception:
            pass

        # Fallback to slugs if Yahoo title extraction didn't match
        if not extracted_artist:
            # yung-lean-bladee -> Yung Lean; Bladee
            art_words = artist_slug.replace('-', ' ').split()
            extracted_artist = " ".join(w.capitalize() for w in art_words)
        if not extracted_album:
            extracted_album = " ".join(w.capitalize() for w in album_slug.replace('-', ' ').split())

        clean_g = self._clean_genres(genres)
        return extracted_artist, extracted_album, "; ".join(clean_g)

    def search_rym_releases(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Searches RYM releases via search index.
        """
        q = f'site:rateyourmusic.com/release/ {query}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        results = []

        try:
            r = requests.get(f'https://search.yahoo.com/search?p={urllib.parse.quote(q)}', impersonate='chrome124', headers=headers, timeout=8)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for div in soup.select('div.algo')[:limit]:
                    t = div.select_one('h3')
                    comp = div.select_one('.compText')
                    a_tag = div.select_one('h3 a')
                    url = a_tag.get('href', '') if a_tag else ''

                    if t and comp:
                        title_text = t.get_text(' ')
                        comp_text = comp.get_text(' ')
                        m_title = re.search(r'^(.*?)\s+by\s+(.*?)\s*\(Album', title_text, re.IGNORECASE)
                        
                        album_name = m_title.group(1).strip() if m_title else title_text.split(" - ")[0]
                        artist_name = m_title.group(2).strip() if m_title else ""
                        if artist_name:
                            parts = re.split(r'\s*(?:;|&|feat\.|ft\.|with|,|\/)\s*', artist_name, flags=re.IGNORECASE)
                            artist_name = "; ".join(p.strip() for p in parts if p.strip())

                        # Extract year
                        m_year = re.search(r'\b(19\d\d|20\d\d)\b', comp_text)
                        year = m_year.group(1) if m_year else ""

                        genres = self._clean_genres(self._extract_from_text(f"{title_text} {comp_text}"))

                        results.append({
                            "title": f"{artist_name} - {album_name}" if artist_name else album_name,
                            "album": album_name,
                            "artist": artist_name,
                            "year": year,
                            "genres": genres,
                            "rym_genres_str": "; ".join(genres),
                            "url": url,
                            "source": "RateYourMusic"
                        })
        except Exception as e:
            print(f"RYM search error: {e}")

        return results

