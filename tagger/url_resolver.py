import re
from typing import Optional, Tuple
from tagger.models import AlbumMetadata
from tagger.musicbrainz import MusicBrainzClient
from tagger.discogs import DiscogsClient
from tagger.rym import RYMGenreFetcher
from tagger.coverart import CoverArtManager

class AlbumURLResolver:
    def __init__(self):
        self.mb = MusicBrainzClient()
        self.discogs = DiscogsClient()
        self.rym = RYMGenreFetcher()
        self.cover_mgr = CoverArtManager()

    def resolve_url(self, url: str, lowercase_artists: bool = False) -> Optional[AlbumMetadata]:
        url = url.strip()

        meta = None

        # 1. Discogs URL
        if "discogs.com" in url:
            meta = self.discogs.parse_discogs_url(url, lowercase_artists=lowercase_artists)
            if meta:
                # Also try to fetch RYM genres for this release
                rym_genres = self.rym.get_formatted_genre_string(meta.album_artist, meta.title)
                if rym_genres:
                    meta.rym_genres_str = rym_genres
                # Ensure cover image
                if not meta.cover_url:
                    meta.cover_url = self.cover_mgr.get_cover_url(meta.album_artist, meta.title)

        # 2. MusicBrainz URL
        elif "musicbrainz.org/release/" in url:
            m = re.search(r'/release/([a-f0-9\-]{36})', url)
            if m:
                mbid = m.group(1)
                meta = self.mb.get_album_details(mbid, lowercase_artists=lowercase_artists)
                if meta:
                    meta.rym_genres_str = self.rym.get_formatted_genre_string(meta.album_artist, meta.title)
                    meta.discogs_genres_str = self.discogs.get_formatted_genres(meta.album_artist, meta.title)
                    meta.cover_url = self.cover_mgr.get_cover_url(meta.album_artist, meta.title, musicbrainz_id=mbid)

        # 3. RateYourMusic URL
        elif "rateyourmusic.com/release/" in url:
            art, alb, rym_genres = self.rym.parse_rym_url(url)
            if art and alb:
                # Fetch official tracklist from MusicBrainz or Discogs using parsed artist & album
                meta = self.mb.search_album(art, alb, lowercase_artists=lowercase_artists)
                if not meta:
                    discogs_results = self.discogs.search_releases(f"{art} {alb}", artist=art, album=alb, limit=1)
                    if discogs_results:
                        meta = self.discogs.get_release_by_id(discogs_results[0]["id"], lowercase_artists=lowercase_artists)

                if meta:
                    meta.rym_genres_str = rym_genres or self.rym.get_formatted_genre_string(art, alb)
                    if not meta.discogs_genres_str:
                        meta.discogs_genres_str = self.discogs.get_formatted_genres(art, alb)
                    if not meta.cover_url:
                        meta.cover_url = self.cover_mgr.get_cover_url(meta.album_artist, meta.title)
                else:
                    # Return basic AlbumMetadata without tracks if online DBs don't have tracklist
                    d_genres = self.discogs.get_formatted_genres(art, alb)
                    return AlbumMetadata(
                        title=alb,
                        album_artist=art,
                        rym_genres_str=rym_genres,
                        discogs_genres_str=d_genres,
                        cover_url=self.cover_mgr.get_cover_url(art, alb)
                    )

        if meta:
            # Set default track genres to RYM or Discogs
            default_g = meta.rym_genres_str or meta.discogs_genres_str
            for t in meta.tracks:
                t.genre = default_g
            return meta

        return None
