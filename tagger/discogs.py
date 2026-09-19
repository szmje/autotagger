import re
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests
from rapidfuzz import fuzz

from tagger.models import AlbumMetadata, TrackMetadata

DISCOGS_API_URL = "https://api.discogs.com"
HEADERS = {
    "User-Agent": "AutoTaggerRYM/1.0 +https://github.com",
    "Accept": "application/json"
}
CACHE_FILE = Path(__file__).resolve().parent.parent / ".discogs_cache.json"

class DiscogsClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
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

    def get_formatted_genres(self, artist: str, album: str) -> str:
        """
        Searches Discogs for the release and returns styles + genres formatted in lowercase with '; '.
        """
        cache_key = f"{artist} - {album}".strip().lower()
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            results = self.search_releases(f"{artist} {album}".strip(), artist=artist, album=album, limit=2)
            if not results:
                results = self.search_releases(f"{artist} {album}".strip(), limit=2)

            if results:
                styles = [s.strip().lower() for s in results[0].get("styles", []) if s.strip()]
                genres = [g.strip().lower() for g in results[0].get("genres", []) if g.strip()]
                combined = []
                for item in styles + genres:
                    if item not in combined:
                        combined.append(item)
                res = "; ".join(combined)
                self.cache[cache_key] = res
                self._save_cache()
                return res
        except Exception as e:
            print(f"Discogs get_formatted_genres error: {e}")
        return ""

    @staticmethod
    def format_artists(artists_data: List[Dict[str, Any]], lowercase: bool = False) -> str:
        """
        Formats Discogs artist list with '; '.
        Removes trailing parenthetical disambiguation numbers like 'Bladee (2)'.
        """
        names = []
        for a in artists_data:
            name = a.get("name", "").strip()
            # Discogs often has 'Artist (2)', 'Artist (3)' to disambiguate names
            name = re.sub(r'\s*\(\d+\)$', '', name).strip()
            if name and name not in names:
                names.append(name)
        res = "; ".join(names)
        return res.lower() if lowercase else res

    def search_releases(self, query: str, artist: Optional[str] = None, album: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Searches Discogs database for releases.
        """
        url = f"{DISCOGS_API_URL}/database/search"
        params = {"type": "release", "per_page": limit}

        if artist and album:
            params["artist"] = artist
            params["release_title"] = album
        elif query:
            params["q"] = query

        try:
            r = self.session.get(url, params=params, timeout=8)
            if r.status_code == 200:
                results = r.json().get("results", [])
                out = []
                for item in results:
                    # Filter out tracks/artists, keep releases and masters
                    res_type = item.get("type", "release")
                    title = item.get("title", "")
                    year = item.get("year", "")
                    genres = item.get("genre", [])
                    styles = item.get("style", [])
                    cover_img = item.get("cover_image", "")
                    res_url = item.get("resource_url", "")
                    item_id = item.get("id")

                    out.append({
                        "id": item_id,
                        "type": res_type,
                        "title": title,
                        "year": str(year) if year else "",
                        "genres": genres,
                        "styles": styles,
                        "cover_image": cover_img,
                        "resource_url": res_url,
                        "source": "Discogs"
                    })
                return out
        except Exception as e:
            print(f"Discogs search error: {e}")
        return []

    def get_release_by_id(self, release_id: int | str, lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        url = f"{DISCOGS_API_URL}/releases/{release_id}"
        try:
            r = self.session.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                return self._parse_release_json(data, lowercase_artists=lowercase_artists)
        except Exception as e:
            print(f"Discogs get release error: {e}")
        return None

    def get_master_release(self, master_id: int | str, lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        url = f"{DISCOGS_API_URL}/masters/{master_id}"
        try:
            r = self.session.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                main_rel_id = data.get("main_release")
                if main_rel_id:
                    return self.get_release_by_id(main_rel_id, lowercase_artists=lowercase_artists)
                # If no main release, parse master directly
                return self._parse_release_json(data, lowercase_artists=lowercase_artists)
        except Exception as e:
            print(f"Discogs get master error: {e}")
        return None

    @staticmethod
    def _flatten_tracklist(raw_tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Unpacks index tracks and subtracks from Discogs tracklist.
        Discogs releases with continuous mixes or suites often group songs into
        index containers (type_ == 'index') with a 'sub_tracks' array.
        """
        flat = []
        disc_counter = 0

        for t in raw_tracks:
            sub_tracks = t.get("sub_tracks", [])
            t_type = t.get("type_", "")
            h_title = t.get("title", "")
            pos = t.get("position", "").strip()

            disc_clue = None
            m_h = re.search(r'(?:CD|Disc|Disk|Side)\s*(\d+)', h_title, re.I)
            if m_h:
                disc_clue = int(m_h.group(1))
            elif pos and re.match(r'^\d+$', pos):
                disc_clue = int(pos)

            if sub_tracks:
                disc_counter += 1
                effective_disc = disc_clue or disc_counter
                for sub in sub_tracks:
                    sub_copy = dict(sub)
                    sub_pos = sub_copy.get("position", "").strip()
                    if not re.match(r'^(?:CD|Disc|Disk)?\s*\d+[-.:]', sub_pos, re.I):
                        sub_copy["_disc_clue"] = effective_disc
                    flat.append(sub_copy)
            elif t_type in ("heading", "index") and not pos:
                flat.append(t)
            else:
                flat.append(t)

        return flat

    def _enrich_track_artists(
        self,
        data: Dict[str, Any],
        tracks: List[TrackMetadata],
        album_artist: str,
        lowercase_artists: bool = False
    ):
        """
        If all tracks in a release only have generic album_artist (common in DJ mixes
        or compilation sub-tracks on Discogs), attempts to find individual track artists
        from other versions under the same master_id or MusicBrainz.
        """
        if not tracks:
            return

        has_individual = any(t.artist and t.artist.lower() != album_artist.lower() for t in tracks)
        if has_individual:
            return

        master_id = data.get("master_id")
        enriched = False

        # 1. Try other versions in Discogs master release
        if master_id:
            try:
                v_url = f"{DISCOGS_API_URL}/masters/{master_id}/versions?per_page=8"
                v_resp = self.session.get(v_url, timeout=6)
                if v_resp.status_code == 200:
                    versions = v_resp.json().get("versions", [])
                    for v in versions:
                        vid = v.get("id")
                        if vid == data.get("id"):
                            continue
                        r_url = f"{DISCOGS_API_URL}/releases/{vid}"
                        r_resp = self.session.get(r_url, timeout=6)
                        if r_resp.status_code != 200:
                            continue
                        v_data = r_resp.json()
                        flat_v = self._flatten_tracklist(v_data.get("tracklist", []))
                        if not any(item.get("artists") for item in flat_v):
                            continue

                        # We found a version with track artists! Match to our tracks
                        for t in tracks:
                            t_title = t.title.strip().lower()
                            best_art = None
                            best_score = -1.0
                            for v_item in flat_v:
                                v_art_list = v_item.get("artists", [])
                                if not v_art_list:
                                    continue
                                v_title = v_item.get("title", "").strip().lower()
                                score = fuzz.token_sort_ratio(t_title, v_title)
                                if score > best_score:
                                    best_score = score
                                    best_art = self.format_artists(v_art_list, lowercase=lowercase_artists)
                            if best_art and best_score >= 70:
                                t.artist = best_art
                                enriched = True
                        if enriched:
                            break
            except Exception as e:
                print(f"Discogs enrich from master error: {e}")

        # 2. Fallback to MusicBrainz if still no individual artists
        if not enriched:
            try:
                from tagger.musicbrainz import MusicBrainzClient
                mb = MusicBrainzClient()
                mb_meta = mb.search_album(album_artist, data.get("title", ""), lowercase_artists=lowercase_artists)
                if mb_meta and any(mt.artist and mt.artist.lower() != mb_meta.album_artist.lower() for mt in mb_meta.tracks):
                    for t in tracks:
                        t_title = t.title.strip().lower()
                        best_art = None
                        best_score = -1.0
                        for mt in mb_meta.tracks:
                            if not mt.artist or mt.artist.lower() == mb_meta.album_artist.lower():
                                continue
                            score = fuzz.token_sort_ratio(t_title, mt.title.strip().lower())
                            if score > best_score:
                                best_score = score
                                best_art = mt.artist
                        if best_art and best_score >= 70:
                            t.artist = best_art
            except Exception as e:
                print(f"Discogs enrich from MusicBrainz error: {e}")

    def _parse_release_json(self, data: Dict[str, Any], lowercase_artists: bool = False) -> AlbumMetadata:
        title = data.get("title", "")
        album_artist = self.format_artists(data.get("artists", []), lowercase=lowercase_artists)
        year = str(data.get("year", "") or data.get("released", "")[:4])

        # Cover image
        cover_url = None
        images = data.get("images", [])
        if images:
            # Pick primary or first image
            for img in images:
                if img.get("type") == "primary":
                    cover_url = img.get("uri") or img.get("resource_url")
                    break
            if not cover_url and images:
                cover_url = images[0].get("uri") or images[0].get("resource_url")

        # Genres & Styles from Discogs
        discogs_genres = []
        for s in data.get("styles", []):
            clean_s = s.strip().lower()
            if clean_s and clean_s not in discogs_genres:
                discogs_genres.append(clean_s)
        for g in data.get("genres", []):
            clean_g = g.strip().lower()
            if clean_g and clean_g not in discogs_genres:
                discogs_genres.append(clean_g)

        discogs_genres_str = "; ".join(discogs_genres)

        # Tracklist
        raw_tracks = self._flatten_tracklist(data.get("tracklist", []))
        tracks: List[TrackMetadata] = []
        track_num = 1
        current_disc = 1

        for t in raw_tracks:
            # Check headings for Disc indications (e.g. 'CD 1', 'Disc 2')
            if t.get("type_") in ("heading", "index") and not t.get("position"):
                h_title = t.get("title", "")
                m_h = re.search(r'(?:CD|Disc|Disk|Side)\s*(\d+)', h_title, re.I)
                if m_h:
                    current_disc = int(m_h.group(1))
                    track_num = 1
                continue

            pos = t.get("position", "").strip()
            disc_idx = t.get("_disc_clue", current_disc)
            t_idx = track_num

            if pos:
                # Format like "1-1", "CD1-1", "2-05", "1.05"
                m_dt = re.match(r'^(?:CD|Disc|Disk)?\s*(\d+)[-.:](\d+)$', pos, re.I)
                if m_dt:
                    disc_idx = int(m_dt.group(1))
                    t_idx = int(m_dt.group(2))
                else:
                    # Vinyl sides A1, B1, C1, D1 or Cassette sides A-01, B-02
                    m_tape = re.match(r'^([A-Za-z])[-.:]?(\d+)$', pos)
                    if m_tape:
                        side = m_tape.group(1).upper()
                        disc_idx = (ord(side) - ord('A')) // 2 + 1
                        t_idx = int(m_tape.group(2))
                    else:
                        m_single = re.match(r'^\D*(\d+)', pos)
                        if m_single:
                            t_idx = int(m_single.group(1))

            t_title = t.get("title", "").strip()
            if not t_title:
                continue

            t_artists_data = t.get("artists", [])
            if t_artists_data:
                t_artist = self.format_artists(t_artists_data, lowercase=lowercase_artists)
            else:
                t_artist = album_artist

            tracks.append(TrackMetadata(
                title=t_title,
                artist=t_artist,
                track_number=t_idx,
                total_tracks=len(raw_tracks),
                disc_number=disc_idx,
                year=year,
                album=title,
                album_artist=album_artist
            ))
            track_num = t_idx + 1

        # Attempt to enrich missing track-specific artists if needed
        self._enrich_track_artists(data, tracks, album_artist, lowercase_artists=lowercase_artists)

        # Calculate total discs and per-disc track totals
        total_discs = max((t.disc_number for t in tracks), default=1)
        for d in range(1, total_discs + 1):
            d_tracks = [t for t in tracks if t.disc_number == d]
            for t in d_tracks:
                t.total_discs = total_discs
                t.total_tracks = len(d_tracks)

        return AlbumMetadata(
            title=title,
            album_artist=album_artist,
            year=year,
            genres=discogs_genres,
            rym_genres_str="",
            discogs_genres_str=discogs_genres_str,
            tracks=tracks,
            cover_url=cover_url
        )

    def parse_discogs_url(self, url: str, lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        """
        Parses Discogs URL like:
        - https://www.discogs.com/release/30205901-Yung-Lean-Bladee-Psykos
        - https://www.discogs.com/master/3872023-Yung-Lean-Bladee-Psykos
        """
        m_rel = re.search(r'/release/(\d+)', url)
        if m_rel:
            return self.get_release_by_id(m_rel.group(1), lowercase_artists=lowercase_artists)

        m_mas = re.search(r'/master/(\d+)', url)
        if m_mas:
            return self.get_master_release(m_mas.group(1), lowercase_artists=lowercase_artists)

        return None
