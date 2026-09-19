import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from tagger.audio import SUPPORTED_EXTENSIONS, AudioTagEngine
from tagger.models import AudioFileInfo

class AudioScanner:
    def __init__(self):
        self.audio_engine = AudioTagEngine()

    def scan_paths(self, input_paths: List[str | Path]) -> Dict[Path, List[AudioFileInfo]]:
        """
        Scans given paths (files or directories) and groups found audio files by folder.
        """
        album_groups: Dict[Path, List[AudioFileInfo]] = {}

        for p_str in input_paths:
            path = Path(p_str).resolve()
            if not path.exists():
                continue

            if path.is_file():
                if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    folder = path.parent
                    if folder not in album_groups:
                        album_groups[folder] = []
                    info = self.audio_engine.read_file_info(path)
                    album_groups[folder].append(info)

            elif path.is_dir():
                # Walk recursively
                for root, _, files in os.walk(path):
                    root_path = Path(root)
                    audio_in_dir = []
                    for f in files:
                        p = root_path / f
                        if p.suffix.lower() in SUPPORTED_EXTENSIONS:
                            info = self.audio_engine.read_file_info(p)
                            audio_in_dir.append(info)
                    if audio_in_dir:
                        # If current folder is CD1 / Disc 1, group into parent album folder
                        if re.match(r'^(?:CD|Disc|Disk)\s*\d+$', root_path.name, re.IGNORECASE) and root_path.parent != root_path:
                            target_folder = root_path.parent
                        else:
                            target_folder = root_path
                        if target_folder not in album_groups:
                            album_groups[target_folder] = []
                        album_groups[target_folder].extend(audio_in_dir)

        # Sort files in each folder by disc number, then track number, then filename
        for folder in album_groups:
            album_groups[folder].sort(key=lambda x: (
                x.existing_disc_num if x.existing_disc_num is not None else 1,
                x.existing_track_num if x.existing_track_num is not None else 9999,
                x.filename.lower()
            ))

        return album_groups

    @staticmethod
    def parse_folder_clues(folder_path: Path, sample_files: List[AudioFileInfo]) -> Tuple[str, str, Optional[str]]:
        """
        Extracts (artist, album, year) clues from folder name or audio tags.
        Normalizes multiple artists with '; '.
        """
        name = folder_path.name.strip()

        # Check if parent is a disc folder (e.g. 'CD 1', 'Disc 1')
        if re.match(r'^(CD|Disc)\s*\d+$', name, re.IGNORECASE):
            # Use grandparent folder name for album clues
            name = folder_path.parent.name.strip()

        artist = ""
        album = ""
        year = None

        # Try regex patterns on folder name:
        # 1. Artist - Album (Year) or Artist - Album [Year]
        m = re.match(r'^(.*?)\s*-\s*(.*?)\s*[\(\[]\s*(\d{4})\s*[\)\]]$', name)
        if m:
            artist, album, year = m.group(1), m.group(2), m.group(3)
        else:
            # 2. (Year) Artist - Album or [Year] Artist - Album
            m2 = re.match(r'^[\(\[]\s*(\d{4})\s*[\)\]]\s*(.*?)\s*-\s*(.*)$', name)
            if m2:
                year, artist, album = m2.group(1), m2.group(2), m2.group(3)
            else:
                # 3. Artist - Album
                m3 = re.match(r'^(.*?)\s*-\s*(.*)$', name)
                if m3:
                    artist, album = m3.group(1), m3.group(2)
                else:
                    # 4. Folder name is just album name
                    album = name

        # If artist or album missing, check tags in sample_files
        if not artist or not album:
            for f in sample_files:
                if not artist and (f.existing_album_artist or f.existing_artist):
                    artist = f.existing_album_artist or f.existing_artist or ""
                if not album and f.existing_album:
                    album = f.existing_album
                if not year and f.existing_year:
                    year = f.existing_year[:4]

        # Clean artist: replace joiners '&', 'feat.', 'with' with ';'
        if artist:
            # Remove any trailing junk
            artist = re.sub(r'\s*(?:;|&|feat\.|ft\.|with|,|\/)\s*', '; ', artist, flags=re.IGNORECASE)
            # Normalize double semicolons or spaces
            artist = re.sub(r'(?:;\s*)+', '; ', artist).strip('; ')

        album = album.strip()
        return artist, album, year
