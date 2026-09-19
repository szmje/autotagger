from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
import re

from tagger.models import TrackMetadata, AlbumMetadata, AudioFileInfo
from tagger.scanner import AudioScanner
from tagger.musicbrainz import MusicBrainzClient
from tagger.discogs import DiscogsClient
from tagger.rym import RYMGenreFetcher
from tagger.coverart import CoverArtManager
from tagger.audio import AudioTagEngine
from tagger.url_resolver import AlbumURLResolver
from tagger.searcher import UnifiedAlbumSearcher
from tagger.renamer import FileRenamer
from tagger.lyrics import LyricsManager

class AutoTaggerProcessor:
    def __init__(
        self,
        lowercase_genres: bool = True,
        lowercase_artists: bool = False,
        save_cover_art: bool = True,
        embed_cover_art: bool = True,
        rename_files: bool = False,
        rename_folders: bool = False,
        fetch_lyrics: bool = False,
        save_lrc_file: bool = True,
        clean_junk_tags: bool = True,
        naming_pattern: str = "01. Artist - Title",
        enabled_tags: Optional[dict] = None,
        multi_disc_format: bool = True,
        on_log: Optional[Callable[[str], None]] = None,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ):
        self.lowercase_genres = lowercase_genres
        self.lowercase_artists = lowercase_artists
        self.save_cover_art = save_cover_art
        self.embed_cover_art = embed_cover_art
        self.rename_files = rename_files
        self.rename_folders = rename_folders
        self.fetch_lyrics = fetch_lyrics
        self.save_lrc_file = save_lrc_file
        self.clean_junk_tags = clean_junk_tags
        self.naming_pattern = naming_pattern
        self.enabled_tags = enabled_tags
        self.multi_disc_format = multi_disc_format
        self.on_log = on_log or (lambda msg: None)
        self.on_progress = on_progress or (lambda cur, tot, msg: None)

        self.scanner = AudioScanner()
        self.mb = MusicBrainzClient()
        self.discogs = DiscogsClient()
        self.rym = RYMGenreFetcher()
        self.cover_mgr = CoverArtManager()
        self.audio_engine = AudioTagEngine()
        self.url_resolver = AlbumURLResolver()
        self.searcher = UnifiedAlbumSearcher()
        self.renamer = FileRenamer()
        self.lyrics_mgr = LyricsManager()

    def log(self, msg: str):
        self.on_log(msg)

    def prepare_album(
        self,
        folder: Path,
        files: List[AudioFileInfo],
        override_artist: Optional[str] = None,
        override_album: Optional[str] = None,
        override_url: Optional[str] = None,
        custom_album_meta: Optional[AlbumMetadata] = None
    ) -> Tuple[AlbumMetadata, List[Tuple[AudioFileInfo, TrackMetadata]], Optional[Path]]:
        """
        Prepares metadata for an album folder without applying tags yet (for preview in GUI/CLI).
        Returns: (AlbumMetadata, list of (AudioFileInfo, TrackMetadata), cover_file_path)
        """
        album_meta = None

        # 0. Custom metadata or direct URL
        if custom_album_meta:
            album_meta = custom_album_meta
            self.log(f"📌 Использованы выбранные метаданные: {album_meta.album_artist} - {album_meta.title}")
        elif override_url:
            self.log(f"🔗 Разрешение ссылки: {override_url}...")
            album_meta = self.url_resolver.resolve_url(override_url, lowercase_artists=self.lowercase_artists)
            if album_meta:
                self.log(f"✅ Успешно загружен альбом по ссылке: {album_meta.album_artist} - {album_meta.title}")
            else:
                self.log(f"⚠️ Не удалось извлечь альбом по ссылке, переход к поиску...")

        if not album_meta:
            clue_artist, clue_album, clue_year = self.scanner.parse_folder_clues(folder, files)
            artist = override_artist or clue_artist
            album = override_album or clue_album

            self.log(f"🔎 Определение альбома для папки: '{folder.name}' (Артист: '{artist}', Альбом: '{album}')")

            # 1. Search MusicBrainz
            if artist and album:
                album_meta = self.mb.search_album(artist, album, lowercase_artists=self.lowercase_artists)

            # 2. Fallback to Discogs search if MusicBrainz didn't find it
            if not album_meta and (artist or album):
                self.log(f"🔎 MusicBrainz не нашел альбом, пробуем Discogs...")
                d_results = self.discogs.search_releases(f"{artist} {album}".strip(), artist=artist, album=album, limit=1)
                if d_results:
                    album_meta = self.discogs.get_release_by_id(d_results[0]["id"], lowercase_artists=self.lowercase_artists)
                    if album_meta:
                        self.log(f"✅ Найдено в Discogs: {album_meta.album_artist} - {album_meta.title} ({album_meta.year})")

        if not album_meta:
            self.log(f"⚠️ MusicBrainz не нашел точного релиза, формируем теги из файлов/папки")
            # Fallback metadata from files and folder name
            tracks: List[TrackMetadata] = []
            for i, f in enumerate(files):
                t_num = f.existing_track_num or (i + 1)
                # Clean title clue from filename
                title_clue = re.sub(r'^\s*\d+[\s\.\-_]+', '', f.path.stem)
                if " - " in title_clue:
                    title_clue = title_clue.split(" - ", 1)[1]
                t_title = f.existing_title or title_clue or f"Track {t_num}"
                t_artist = f.existing_artist or artist or "Unknown Artist"
                # Normalize artist joiners to '; '
                t_artist = self.mb.format_artists(t_artist, lowercase=self.lowercase_artists)

                d_num = f.existing_disc_num or 1
                tracks.append(TrackMetadata(
                    title=t_title,
                    artist=t_artist,
                    track_number=t_num,
                    total_tracks=len(files),
                    disc_number=d_num,
                    total_discs=1,
                    year=clue_year or f.existing_year,
                    album=album or folder.name,
                    album_artist=artist or t_artist
                ))

            total_discs = max((t.disc_number for t in tracks), default=1)
            for t in tracks:
                t.total_discs = total_discs

            album_meta = AlbumMetadata(
                title=album or folder.name,
                album_artist=artist or "Unknown Artist",
                year=clue_year,
                tracks=tracks
            )
            matched_pairs = [(f, tracks[i]) for i, f in enumerate(files)]
        else:
            self.log(f"✅ Метаданные релиза: {album_meta.album_artist} - {album_meta.title} ({album_meta.year})")
            # Match files to tracks
            raw_matched = self.mb.match_files_to_tracks(files, album_meta)
            matched_pairs = []
            for i, (f, track) in enumerate(raw_matched):
                if not track:
                    # Fallback track if not matched
                    t_num = f.existing_track_num or (i + 1)
                    track = TrackMetadata(
                        title=f.existing_title or f.path.stem,
                        artist=album_meta.album_artist,
                        track_number=t_num,
                        total_tracks=len(files),
                        year=album_meta.year,
                        album=album_meta.title,
                        album_artist=album_meta.album_artist
                    )
                else:
                    # If track artist is just generic album artist, but local file has a specific artist
                    if (not track.artist or track.artist.lower() == album_meta.album_artist.lower()):
                        if f.existing_artist and f.existing_artist.lower() != album_meta.album_artist.lower():
                            track.artist = self.mb.format_artists(f.existing_artist, lowercase=self.lowercase_artists)
                        else:
                            stem = f.path.stem
                            if " - " in stem:
                                left = stem.split(" - ", 1)[0]
                                left_clean = re.sub(r'^\s*\d+[\s\.\-_]+', '', left).strip()
                                if left_clean and left_clean.lower() != album_meta.album_artist.lower():
                                    track.artist = self.mb.format_artists(left_clean, lowercase=self.lowercase_artists)
                matched_pairs.append((f, track))

        # 2. Fetch RYM genres & Discogs genres
        self.log(f"🌐 Поиск жанров на RateYourMusic для: {album_meta.album_artist} - {album_meta.title}...")
        rym_genres_str = self.rym.get_formatted_genre_string(album_meta.album_artist, album_meta.title)
        if not rym_genres_str and artist != album_meta.album_artist:
            rym_genres_str = self.rym.get_formatted_genre_string(artist, album_meta.title)

        if rym_genres_str:
            self.log(f"✨ RYM жанры: {rym_genres_str}")
        else:
            self.log(f"ℹ️ Жанры на RYM не найдены")

        self.log(f"🌐 Поиск жанров/стилей на Discogs для: {album_meta.album_artist} - {album_meta.title}...")
        discogs_genres_str = album_meta.discogs_genres_str
        if not discogs_genres_str:
            discogs_genres_str = self.discogs.get_formatted_genres(album_meta.album_artist, album_meta.title)
        if not discogs_genres_str and artist != album_meta.album_artist:
            discogs_genres_str = self.discogs.get_formatted_genres(artist, album_meta.title)

        if discogs_genres_str:
            self.log(f"✨ Discogs жанры/стили: {discogs_genres_str}")
        else:
            self.log(f"ℹ️ Жанры на Discogs не найдены")

        album_meta.rym_genres_str = rym_genres_str
        album_meta.discogs_genres_str = discogs_genres_str

        # Preferred default genre: RYM if present, otherwise Discogs
        active_genre = rym_genres_str or discogs_genres_str
        for _, track in matched_pairs:
            track.genre = active_genre

        # 3. Cover art
        cover_path = None
        if self.save_cover_art:
            self.log(f"🖼️ Поиск и сохранение обложки в папку...")
            cover_path = self.cover_mgr.save_cover_to_folder(
                folder,
                album_meta.album_artist,
                album_meta.title,
                musicbrainz_id=album_meta.musicbrainz_id
            )
            if cover_path and cover_path.exists():
                self.log(f"💾 Обложка сохранена: {cover_path.name}")
            else:
                self.log(f"ℹ️ Обложка не найдена в онлайн-базах")

        return album_meta, matched_pairs, cover_path

    def process_paths(
        self,
        paths: List[str | Path],
        override_url: Optional[str] = None,
        enabled_tags: Optional[dict] = None
    ) -> int:
        """
        Scans given paths, extracts metadata, fetches RYM genres, saves cover art,
        and applies tags to all audio files.
        Returns total number of files tagged.
        """
        active_tags = enabled_tags if enabled_tags is not None else self.enabled_tags
        self.log("🚀 Начало сканирования аудиофайлов...")
        album_groups = self.scanner.scan_paths(paths)

        if not album_groups:
            self.log("❌ Аудиофайлы не найдены в указанных папках")
            return 0

        total_files = sum(len(f_list) for f_list in album_groups.values())
        self.log(f"📁 Найдено альбомов/папок: {len(album_groups)}, всего файлов: {total_files}")

        files_processed = 0

        for folder, files in album_groups.items():
            album_meta, matched_pairs, cover_path = self.prepare_album(folder, files, override_url=override_url)

            # Read cover bytes if embedding is enabled
            cover_bytes = None
            if self.embed_cover_art and (active_tags is None or active_tags.get("cover", True)):
                if cover_path and cover_path.exists():
                    try:
                        cover_bytes = cover_path.read_bytes()
                    except Exception:
                        pass
                elif (folder / "cover.jpg").exists():
                    try:
                        cover_bytes = (folder / "cover.jpg").read_bytes()
                    except Exception:
                        pass

            # Apply tags
            for f_info, track_meta in matched_pairs:
                lyrics_text = None
                if self.fetch_lyrics and (active_tags is None or active_tags.get("lyrics", True)):
                    self.log(f"🎤 Поиск текстов: {track_meta.artist} - {track_meta.title}...")
                    lyrics_text = self.lyrics_mgr.fetch_lyrics(track_meta.artist, track_meta.title, album=album_meta.title)
                    if lyrics_text:
                        self.log(f"✨ Текст найден для: {track_meta.title}")
                        if self.save_lrc_file:
                            lrc_p = self.lyrics_mgr.save_lrc_file(f_info.path, lyrics_text)
                            if lrc_p:
                                self.log(f"💾 Сохранен .lrc: {lrc_p.name}")

                self.audio_engine.apply_tags(
                    f_info.path,
                    track_meta,
                    cover_image_bytes=cover_bytes,
                    lyrics_text=lyrics_text,
                    clean_junk_tags=self.clean_junk_tags,
                    enabled_tags=active_tags,
                    multi_disc_format=self.multi_disc_format
                )
                files_processed += 1
                self.on_progress(
                    files_processed,
                    total_files,
                    f"Тегирование: {f_info.filename}"
                )

                # Rename file if requested
                if self.rename_files:
                    new_fname = self.renamer.generate_new_filename(
                        track_meta,
                        f_info.extension,
                        pattern=self.naming_pattern,
                        is_multi_disc=album_meta.is_multi_disc(),
                        multi_disc_format=self.multi_disc_format
                    )
                    old_lrc = f_info.path.with_suffix(".lrc")
                    ok, final_path, msg = self.renamer.rename_file(f_info.path, new_fname)
                    if ok:
                        # Rename .lrc file if present
                        new_lrc = final_path.with_suffix(".lrc")
                        if old_lrc.exists() and old_lrc != new_lrc:
                            try:
                                old_lrc.rename(new_lrc)
                            except Exception:
                                pass

                        f_info.path = final_path
                        f_info.filename = final_path.name
                        self.log(f"✏️ Переименован: {new_fname}")
                    else:
                        self.log(f"⚠️ Ошибка переименования {f_info.filename}: {msg}")

            # Rename folder if requested
            if self.rename_folders and folder.exists():
                ok, new_dir, msg = self.renamer.rename_album_folder(
                    folder, album_meta.album_artist, album_meta.title, album_meta.year
                )
                if ok:
                    self.log(f"📁 Папка альбома переименована: {new_dir.name}")

            self.log(f"🎉 Завершено тегирование альбома '{album_meta.title}' ({len(files)} файлов)")

        self.log(f"✅ Готово! Успешно обработано {files_processed} файлов.")
        return files_processed
