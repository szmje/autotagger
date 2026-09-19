import os
import re
from pathlib import Path
from typing import Optional
import requests

class CoverArtManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        })

    def search_deezer_cover(self, artist: str, album: str) -> Optional[str]:
        try:
            clean_artist = re.sub(r'[;,&/].*', '', artist).strip()
            query = f"{clean_artist} {album}".strip()
            url = "https://api.deezer.com/search/album"
            r = self.session.get(url, params={"q": query}, timeout=6)
            if r.status_code == 200:
                data = r.json().get("data", [])
                if data:
                    # Return cover_xl (1000x1000) or cover_big (500x500)
                    return data[0].get("cover_xl") or data[0].get("cover_big") or data[0].get("cover_medium")
        except Exception:
            pass
        return None

    def search_itunes_cover(self, artist: str, album: str) -> Optional[str]:
        try:
            clean_artist = re.sub(r'[;,&/].*', '', artist).strip()
            query = f"{clean_artist} {album}".strip()
            url = "https://itunes.apple.com/search"
            r = self.session.get(url, params={"term": query, "entity": "album", "limit": 3}, timeout=6)
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    art = results[0].get("artworkUrl100", "")
                    if art:
                        # Upgrade to 1200x1200 resolution
                        return art.replace("100x100bb", "1200x1200bb")
        except Exception:
            pass
        return None

    def get_cover_url(self, artist: str, album: str, musicbrainz_id: Optional[str] = None) -> Optional[str]:
        # 1. Try Deezer
        url = self.search_deezer_cover(artist, album)
        if url:
            return url
        # 2. Try iTunes
        url = self.search_itunes_cover(artist, album)
        if url:
            return url
        return None

    def download_cover_bytes(self, url: str) -> Optional[bytes]:
        try:
            r = self.session.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 1024:
                return r.content
        except Exception:
            pass
        return None

    def save_cover_to_folder(
        self, folder_path: Path, artist: str, album: str, musicbrainz_id: Optional[str] = None, overwrite: bool = False
    ) -> Optional[Path]:
        """
        Downloads the album cover and saves it to the album folder as cover.jpg.
        Returns the Path to the saved image file, or existing file if already present.
        """
        cover_path = folder_path / "cover.jpg"

        if cover_path.exists() and not overwrite and cover_path.stat().st_size > 1024:
            return cover_path

        url = self.get_cover_url(artist, album, musicbrainz_id)
        if not url:
            return cover_path if cover_path.exists() else None

        img_bytes = self.download_cover_bytes(url)
        if img_bytes:
            try:
                cover_path.write_bytes(img_bytes)
                return cover_path
            except Exception as e:
                print(f"Error saving cover image to {cover_path}: {e}")
                return None
        return None
