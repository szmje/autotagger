import re
import musicbrainzngs
from typing import List, Optional, Tuple, Dict, Any
from rapidfuzz import fuzz

from tagger.models import TrackMetadata, AlbumMetadata, AudioFileInfo

# Initialize MusicBrainz
musicbrainzngs.set_useragent("AutoTaggerRYM", "1.0", "user@musicbrainz.org")

class MusicBrainzClient:
    def __init__(self):
        pass

    @staticmethod
    def format_artists(artist_credit: Any, lowercase: bool = False) -> str:
        """
        Converts MusicBrainz artist-credit list into a clean string separated by '; '.
        e.g. [{'artist': {'name': 'Yung Lean'}}, {'artist': {'name': 'Bladee'}}] -> 'Yung Lean; Bladee'
        """
        if not artist_credit:
            return ""
        if isinstance(artist_credit, str):
            # If plain string has joiners, split and rejoin
            parts = re.split(r'\s*(?:;|&|feat\.|ft\.|with|,|\/)\s*', artist_credit, flags=re.IGNORECASE)
            artists = [p.strip() for p in parts if p.strip()]
            res = "; ".join(artists)
            return res.lower() if lowercase else res

        artists = []
        for item in artist_credit:
            if isinstance(item, dict) and "artist" in item:
                name = item["artist"].get("name", "").strip()
                if name and name not in artists:
                    artists.append(name)
            elif isinstance(item, str):
                s = item.strip()
                # If joinphrase contains something like " & ", we ignore and just use clean artist names
                if s and s not in ["&", "feat.", "ft.", "with", "/", ",", ";"]:
                    if s not in artists:
                        artists.append(s)

        res = "; ".join(artists)
        return res.lower() if lowercase else res

    def search_album(self, artist: str, album: str, lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        try:
            # Clean search terms
            clean_artist = re.sub(r'[;,&/].*', '', artist).strip()
            query_artist = clean_artist or artist

            # Search release
            res = musicbrainzngs.search_releases(artist=query_artist, release=album, limit=5)
            release_list = res.get("release-list", [])
            if not release_list:
                # Try searching by release title alone
                res = musicbrainzngs.search_releases(release=album, limit=5)
                release_list = res.get("release-list", [])

            if not release_list:
                return None

            # Pick best match based on artist and album similarity
            best_release = None
            best_score = -1

            for r in release_list:
                r_title = r.get("title", "")
                r_artists = self.format_artists(r.get("artist-credit", []))
                score = (
                    fuzz.token_sort_ratio(album.lower(), r_title.lower()) * 0.6
                    + fuzz.token_sort_ratio(query_artist.lower(), r_artists.lower()) * 0.4
                )
                if score > best_score:
                    best_score = score
                    best_release = r

            if not best_release or best_score < 40:
                # Still fallback to first release if reasonable
                best_release = release_list[0]

            release_id = best_release["id"]
            return self.get_album_details(release_id, lowercase_artists=lowercase_artists)

        except Exception as e:
            print(f"MusicBrainz search error: {e}")
            return None

    def get_album_details(self, release_id: str, lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        try:
            full = musicbrainzngs.get_release_by_id(
                release_id,
                includes=["recordings", "artists", "media"]
            )
            rel = full.get("release", {})
            title = rel.get("title", "")
            album_artist = self.format_artists(rel.get("artist-credit", []), lowercase=lowercase_artists)
            
            # Extract year from date (YYYY-MM-DD)
            raw_date = rel.get("date", "")
            year = raw_date[:4] if raw_date and len(raw_date) >= 4 else ""

            # Mediums & tracks
            medium_list = rel.get("medium-list", [])
            total_discs = len(medium_list)
            tracks: List[TrackMetadata] = []

            for m in medium_list:
                disc_pos = int(m.get("position", 1))
                track_list = m.get("track-list", [])
                total_tracks = len(track_list)

                for t in track_list:
                    pos = int(t.get("position") or t.get("number") or (len(tracks) + 1))
                    rec = t.get("recording", {})
                    track_title = rec.get("title") or t.get("title") or ""
                    
                    # Track artist (if different or credit available)
                    t_credit = t.get("artist-credit") or rec.get("artist-credit") or rel.get("artist-credit")
                    track_artist = self.format_artists(t_credit, lowercase=lowercase_artists)
                    if not track_artist:
                        track_artist = album_artist

                    tracks.append(TrackMetadata(
                        title=track_title,
                        artist=track_artist,
                        track_number=pos,
                        total_tracks=total_tracks,
                        disc_number=disc_pos,
                        total_discs=total_discs,
                        year=year,
                        album=title,
                        album_artist=album_artist
                    ))

            return AlbumMetadata(
                title=title,
                album_artist=album_artist,
                year=year,
                tracks=tracks,
                musicbrainz_id=release_id
            )

        except Exception as e:
            print(f"MusicBrainz get details error: {e}")
            return None

    def match_files_to_tracks(
        self, files: List[AudioFileInfo], album_meta: AlbumMetadata
    ) -> List[Tuple[AudioFileInfo, Optional[TrackMetadata]]]:
        """
        Matches local audio files to the official tracklist.
        Matches by track number first, then falls back to fuzzy title matching.
        """
        matched = []
        unmatched_tracks = list(album_meta.tracks)

        # 1st pass: Match by existing disc number AND track number
        for f in files:
            d_num = f.existing_disc_num
            t_num = f.existing_track_num
            if t_num is None:
                # Try extracting disc-track or track from filename: '01-05 - Title.mp3', '01 - Title.mp3'
                m_dt = re.match(r'^0*(\d+)[-.]0*(\d+)', f.filename)
                if m_dt:
                    if d_num is None:
                        d_num = int(m_dt.group(1))
                    t_num = int(m_dt.group(2))
                else:
                    m = re.match(r'^0*(\d+)', f.filename)
                    if m:
                        t_num = int(m.group(1))

            found = None
            if t_num is not None:
                if d_num is not None:
                    # Match exact disc and track
                    for candidate in unmatched_tracks:
                        if candidate.disc_number == d_num and candidate.track_number == t_num:
                            found = candidate
                            break
                if not found:
                    for candidate in unmatched_tracks:
                        if candidate.track_number == t_num:
                            found = candidate
                            break

            if found:
                f.new_metadata = found
                f.match_score = 100.0
                unmatched_tracks.remove(found)
                matched.append((f, found))
            else:
                matched.append((f, None))

        # 2nd pass: For remaining unmatched files, match by title similarity
        for i, (f, t) in enumerate(matched):
            if t is None and unmatched_tracks:
                # Determine title clue from filename
                # Remove extension and leading track numbers
                clue = re.sub(r'^\s*\d+[\s\.\-_]+', '', f.path.stem)
                # Remove artist prefix if 'Artist - Title'
                if " - " in clue:
                    clue = clue.split(" - ", 1)[1]
                
                clue_to_compare = (f.existing_title or clue).strip()

                best_candidate = None
                best_score = -1.0

                for candidate in unmatched_tracks:
                    score = fuzz.token_sort_ratio(clue_to_compare.lower(), candidate.title.lower())
                    if score > best_score:
                        best_score = score
                        best_candidate = candidate

                if best_candidate and best_score >= 50.0:
                    f.new_metadata = best_candidate
                    f.match_score = best_score
                    matched[i] = (f, best_candidate)
                    unmatched_tracks.remove(best_candidate)

        return matched
