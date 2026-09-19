import os
import re
from pathlib import Path
from typing import Tuple, List, Optional
from pathvalidate import sanitize_filename

from tagger.models import TrackMetadata, AudioFileInfo

def make_safe_filename(name: str) -> str:
    """
    Cleans illegal Windows filename characters and trims whitespace/dots.
    """
    # Replace slashes and colons with hyphens for natural readability
    name = re.sub(r'[\/\\:]', ' - ', name)
    # Replace quotes with single quotes
    name = re.sub(r'[\"<>]', '', name)
    # Replace question marks, pipes, asterisks
    name = re.sub(r'[\?\*\|]', '', name)
    # Use pathvalidate sanitize
    clean = sanitize_filename(name, replacement_text="_")
    # Clean up double spaces or double hyphens
    clean = re.sub(r'\s*-\s*-\s*', ' - ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip(' .')
    return clean

RENAME_PRESETS = {
    "01. Artist - Title": "{track}. {artist} - {title}",
    "01. Title": "{track}. {title}",
    "01 - Artist - Title": "{track} - {artist} - {title}",
    "01 - Title": "{track} - {title}",
    "01-05. Artist - Title": "{track}. {artist} - {title}",
    "01-05. Title": "{track}. {title}",
    "Artist - Title": "{artist} - {title}",
    "Track - Title": "{track} {title}"
}

class FileRenamer:
    def __init__(self):
        pass

    @staticmethod
    def generate_new_filename(
        track: TrackMetadata,
        ext: str,
        pattern: str = "01. Artist - Title",
        is_multi_disc: bool = False,
        multi_disc_format: bool = True
    ) -> str:
        """
        Generates filename according to pattern.
        Default pattern: '01. Artist - Title' -> '01. bladee - obedient.mp3'
        Multi-disc pattern: '01-05. bladee - obedient.mp3'
        """
        fmt = RENAME_PRESETS.get(pattern, pattern)

        is_multi = (track.disc_number and track.disc_number > 1) or (track.total_discs and track.total_discs > 1) or is_multi_disc
        if is_multi and multi_disc_format:
            d_num = track.disc_number or 1
            t_num = f"{d_num:02d}-{track.track_number:02d}"
        else:
            t_num = f"{track.track_number:02d}" if track.track_number else "00"

        artist = track.artist or track.album_artist or "Unknown Artist"
        title = track.title or "Track"

        try:
            raw_name = fmt.format(
                track=t_num,
                artist=artist,
                title=title,
                album=track.album or "",
                year=track.year or ""
            )
        except Exception:
            raw_name = f"{t_num}. {artist} - {title}"

        clean_base = make_safe_filename(raw_name)
        if not ext.startswith("."):
            ext = "." + ext
        return f"{clean_base}{ext.lower()}"

    @staticmethod
    def rename_file(old_path: Path, new_filename: str) -> Tuple[bool, Path, str]:
        """
        Safely renames old_path to new_filename in the same directory.
        Handles Windows case-only rename.
        Returns (success: bool, final_path: Path, message: str)
        """
        if not old_path.exists():
            return False, old_path, "Исходный файл не найден"

        parent = old_path.parent
        new_path = parent / new_filename

        # If already exactly same path and name
        if old_path.resolve() == new_path.resolve() and old_path.name == new_filename:
            return True, old_path, "Имя файла уже совпадает"

        try:
            # Case-only rename on Windows:
            if old_path.resolve() == new_path.resolve():
                temp_path = parent / f"__temp_rename_{os.getpid()}_{new_filename}"
                old_path.rename(temp_path)
                temp_path.rename(new_path)
                return True, new_path, "Успешно переименовано"

            # Destination exists check
            if new_path.exists():
                return False, old_path, f"Файл с именем '{new_filename}' уже существует"

            old_path.rename(new_path)
            return True, new_path, "Успешно переименовано"

        except Exception as e:
            return False, old_path, f"Ошибка переименования: {e}"

    @staticmethod
    def rename_album_folder(folder_path: Path, album_artist: str, album: str, year: Optional[str] = None) -> Tuple[bool, Path, str]:
        """
        Renames album folder to 'Artist - Album (Year)' format.
        e.g. 'bladee; yung lean - psykos (2024)'
        """
        if not folder_path.exists() or not folder_path.is_dir():
            return False, folder_path, "Папка не найдена"

        folder_name = f"{album_artist} - {album}"
        if year:
            folder_name += f" ({year})"

        clean_name = make_safe_filename(folder_name)
        parent = folder_path.parent
        new_folder = parent / clean_name

        if folder_path.resolve() == new_folder.resolve() and folder_path.name == clean_name:
            return True, folder_path, "Имя папки уже совпадает"

        try:
            if folder_path.resolve() == new_folder.resolve():
                temp_dir = parent / f"__temp_folder_{os.getpid()}_{clean_name}"
                folder_path.rename(temp_dir)
                temp_dir.rename(new_folder)
                return True, new_folder, "Папка успешно переименована"

            if new_folder.exists():
                return False, folder_path, f"Папка '{clean_name}' уже существует"

            folder_path.rename(new_folder)
            return True, new_folder, "Папка успешно переименована"

        except Exception as e:
            return False, folder_path, f"Ошибка переименования папки: {e}"
