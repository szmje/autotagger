from typing import List, Dict, Any, Optional
from tagger.musicbrainz import MusicBrainzClient
from tagger.discogs import DiscogsClient
from tagger.rym import RYMGenreFetcher
from tagger.models import AlbumMetadata

class UnifiedAlbumSearcher:
    def __init__(self):
        self.mb = MusicBrainzClient()
        self.discogs = DiscogsClient()
        self.rym = RYMGenreFetcher()

    def search_all(self, query: str, limit_per_source: int = 5) -> List[Dict[str, Any]]:
        """
        Searches MusicBrainz, Discogs, and RateYourMusic for albums matching the query.
        Returns unified list of candidates.
        """
        results = []

        # 1. Discogs Search
        try:
            d_results = self.discogs.search_releases(query=query, limit=limit_per_source)
            for item in d_results:
                title_full = item.get("title", "")
                artist = ""
                album = title_full
                if " - " in title_full:
                    artist, album = title_full.split(" - ", 1)

                styles = item.get("styles", []) or item.get("genres", [])
                results.append({
                    "id": item.get("id"),
                    "source": "Discogs",
                    "artist": artist.strip(),
                    "album": album.strip(),
                    "year": item.get("year", ""),
                    "genres": "; ".join(s.lower() for s in styles[:3]),
                    "display": f"[Discogs] {artist} - {album} ({item.get('year', '')})",
                    "cover_image": item.get("cover_image", ""),
                    "raw": item
                })
        except Exception as e:
            print(f"Unified search Discogs error: {e}")

        # 2. MusicBrainz Search
        try:
            import musicbrainzngs
            res = musicbrainzngs.search_releases(query=query, limit=limit_per_source)
            for r in res.get("release-list", []):
                mb_id = r.get("id")
                title = r.get("title", "")
                artist = self.mb.format_artists(r.get("artist-credit", []))
                date = r.get("date", "")
                year = date[:4] if date else ""
                track_count = r.get("track-count", "")

                results.append({
                    "id": mb_id,
                    "source": "MusicBrainz",
                    "artist": artist,
                    "album": title,
                    "year": year,
                    "genres": "",
                    "display": f"[MusicBrainz] {artist} - {title} ({year})" + (f" [{track_count} tracks]" if track_count else ""),
                    "cover_image": "",
                    "raw": r
                })
        except Exception as e:
            print(f"Unified search MusicBrainz error: {e}")

        # 3. RateYourMusic Search
        try:
            rym_results = self.rym.search_rym_releases(query, limit=limit_per_source)
            for item in rym_results:
                results.append({
                    "id": item.get("url"),
                    "source": "RateYourMusic",
                    "artist": item.get("artist", ""),
                    "album": item.get("album", ""),
                    "year": item.get("year", ""),
                    "genres": item.get("rym_genres_str", ""),
                    "display": f"[RateYourMusic] {item.get('artist')} - {item.get('album')} ({item.get('year', '')})",
                    "cover_image": "",
                    "raw": item
                })
        except Exception as e:
            print(f"Unified search RYM error: {e}")

        return results

    def get_album_by_candidate(self, candidate: Dict[str, Any], lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        source = candidate.get("source")
        cand_id = candidate.get("id")

        if source == "Discogs":
            meta = self.discogs.get_release_by_id(cand_id, lowercase_artists=lowercase_artists)
            if meta:
                rym_g = self.rym.get_formatted_genre_string(meta.album_artist, meta.title)
                if rym_g:
                    meta.rym_genres_str = rym_g
                def_g = meta.rym_genres_str or meta.discogs_genres_str
                for t in meta.tracks:
                    t.genre = def_g
            return meta

        elif source == "MusicBrainz":
            meta = self.mb.get_album_details(cand_id, lowercase_artists=lowercase_artists)
            if meta:
                rym_g = self.rym.get_formatted_genre_string(meta.album_artist, meta.title)
                if rym_g:
                    meta.rym_genres_str = rym_g
                disc_g = self.discogs.get_formatted_genres(meta.album_artist, meta.title)
                if disc_g:
                    meta.discogs_genres_str = disc_g
                def_g = meta.rym_genres_str or meta.discogs_genres_str
                for t in meta.tracks:
                    t.genre = def_g
            return meta

        elif source == "RateYourMusic":
            from tagger.url_resolver import AlbumURLResolver
            resolver = AlbumURLResolver()
            return resolver.resolve_url(cand_id, lowercase_artists=lowercase_artists)

        return None
