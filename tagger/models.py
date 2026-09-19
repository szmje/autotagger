from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

@dataclass
class TrackMetadata:
    title: str
    artist: str  # multiple artists joined with '; '
    track_number: int
    total_tracks: Optional[int] = None
    disc_number: int = 1
    total_discs: Optional[int] = None
    year: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    genre: Optional[str] = None  # lowercase RYM genres joined with '; '
    duration_secs: Optional[float] = None

    def formatted_track_num(self, multi_disc: bool = False) -> str:
        if multi_disc or self.disc_number > 1 or (self.total_discs and self.total_discs > 1):
            return f"{self.disc_number:02d}-{self.track_number:02d}"
        return f"{self.track_number:02d}"

@dataclass
class AlbumMetadata:
    title: str
    album_artist: str  # multiple artists joined with '; '
    year: Optional[str] = None
    genres: List[str] = field(default_factory=list)  # lowercase genres
    rym_genres_str: str = ""  # formatted 'synthpop; dance-pop; ...'
    discogs_genres_str: str = ""  # formatted Discogs genres/styles 'pop rock; post-punk; ...'
    tracks: List[TrackMetadata] = field(default_factory=list)
    cover_url: Optional[str] = None
    musicbrainz_id: Optional[str] = None

    def is_multi_disc(self) -> bool:
        if not self.tracks:
            return False
        discs = {t.disc_number for t in self.tracks if t.disc_number is not None}
        return len(discs) > 1 or any(t.disc_number > 1 for t in self.tracks) or any((t.total_discs or 1) > 1 for t in self.tracks)

@dataclass
class AudioFileInfo:
    path: Path
    filename: str
    extension: str
    folder: Path
    # Existing tags before tagging
    existing_title: Optional[str] = None
    existing_artist: Optional[str] = None
    existing_album: Optional[str] = None
    existing_album_artist: Optional[str] = None
    existing_track_num: Optional[int] = None
    existing_disc_num: Optional[int] = None
    existing_year: Optional[str] = None
    existing_genre: Optional[str] = None
    # Matched new metadata
    new_metadata: Optional[TrackMetadata] = None
    match_score: float = 0.0
