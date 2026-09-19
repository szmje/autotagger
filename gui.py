import os
import sys
import threading
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

try:
    import windnd
    HAS_WINDND = True
except ImportError:
    HAS_WINDND = False

from tagger.models import TrackMetadata, AlbumMetadata, AudioFileInfo
from tagger.processor import AutoTaggerProcessor
from tagger.scanner import AudioScanner
from tagger.audio import AudioTagEngine
from tagger.url_resolver import AlbumURLResolver
from tagger.searcher import UnifiedAlbumSearcher

STRINGS: Dict[str, Dict[str, str]] = {
    "ru": {
        "title": "AutoTagger RYM — Музыкальный автотеггер (RateYourMusic / Discogs / MusicBrainz)",
        "drop_banner": "🎵 ПЕРЕТАЩИТЕ СЮДА ПАПКИ ИЛИ АУДИОФАЙЛЫ ИЗ ПРОВОДНИКА",
        "btn_choose_folder": "📁 Выбрать папку...",
        "btn_choose_files": "📄 Выбрать файлы...",
        "btn_search_db": "🔍 Найти альбом в базах...",
        "btn_clear": "🔄 Очистить",
        "btn_lang": "🌐 English",
        "url_frame": "Вставка ссылки (RateYourMusic / Discogs / MusicBrainz)",
        "btn_paste": "📋 Вставить",
        "btn_load_url": "🔗 Загрузить по ссылке",
        "albums_header": "Альбомы в очереди:",
        "meta_frame": "Метаданные альбома",
        "no_cover": "Нет обложки",
        "cover_loaded": "Обложка загружена",
        "tag_toolbar": "Теги для записи:",
        "btn_all": "✓ Все",
        "btn_none": "✗ Снять",
        "chk_artist": "Исполнитель(и) альбома (;):",
        "chk_album": "Название альбома:",
        "chk_year": "Год релиза:",
        "genre_box": "Жанры альбома (выбор источника)",
        "chk_genre": "Записывать тег Genre",
        "rb_genre_merged": "Объединить оба",
        "rb_genre_rym": "RateYourMusic:",
        "btn_refetch_rym": "🌐 Обновить RYM",
        "rb_genre_discogs": "Discogs (стили + жанры):",
        "btn_refetch_discogs": "💿 Обновить Discogs",
        "btn_search_online": "🔍 Найти альбом в онлайн-базах...",
        "opts_frame": "Параметры и доп. теги",
        "chk_title": "Записывать названия треков (Title)",
        "chk_track_num": "Записывать номера треков (Track №)",
        "chk_embed_cover": "Вшивать обложку в аудиофайлы",
        "chk_save_cover": "Сохранять cover.jpg в папку",
        "chk_clean_junk": "Очищать рекламу/мусорные теги (promo/comments)",
        "chk_fetch_lyrics": "Искать тексты песен (LRC/караоке)",
        "chk_save_lrc": "Сохранять .lrc файлы рядом с треками",
        "chk_lower_artist": "Имена артистов в нижнем регистре",
        "rename_box": "Переименование файлов",
        "chk_rename_files": "Переименовывать при записи тегов",
        "chk_multi_disc_fmt": "Формат 01-05 (Disc-Track) в именах файлов",
        "lbl_pattern": "Шаблон имени файла:",
        "btn_rename_files": "✏️ Переименовать файлы",
        "btn_rename_folder": "📁 Папку",
        "btn_fetch_lyrics": "🎤 Скачать тексты (LRC) для альбома",
        "tree_header": "Треклист и предпросмотр тегов/имен файлов:",
        "col_num": "№",
        "col_filename": "Текущий файл",
        "col_new_filename": "Новое имя (01. Исполнитель - Название)",
        "col_title": "Название трека",
        "col_artist": "Исполнитель (;)",
        "col_genre": "Жанры RYM (lowercase)",
        "btn_apply": "▶️  ПРИМЕНИТЬ И ЗАПИСАТЬ ТЕГИ",
        "tagging_busy": "⏳ Тегирование выполняется...",
        "ctx_paste": "Вставить",
        "ctx_copy": "Копировать",
        "ctx_cut": "Вырезать",
        "ctx_select_all": "Выделить всё",
        "dialog_choose_folder": "Выберите папку с альбомом или музыкой",
        "dialog_choose_files": "Выберите аудиофайлы",
        "audio_files_type": "Аудиофайлы",
        "tagging_in_progress": "Уже выполняется запись тегов, подождите...",
        "no_albums": "Нет загруженных альбомов для тегирования",
        "tagging_done": "Готово",
        "tagging_success": "Успешно обработано {count} аудиофайлов!\nТеги, жанры с RYM и тексты записаны.",
        "select_album_first": "Сначала выберите альбом",
        "select_album_or_drag": "Сначала выберите или перетащите папку с альбомом",
        "url_empty_prompt": "Вставьте ссылку на альбом (RateYourMusic, Discogs или MusicBrainz)",
        "url_fetch_err": "Не удалось извлечь альбом по указанной ссылке.\nПроверьте адрес или воспользуйтесь поиском.",
        "rename_success": "Успешно переименовано {count} файлов по шаблону '{pat}'!",
        "rename_title": "Переименование",
        "rename_folder_title": "Переименование папки альбома",
        "rename_folder_prompt": "Новое имя папки:",
        "rename_folder_success": "Папка переименована в:\n{folder}",
        "rename_folder_err": "Не удалось переименовать папку: {err}",
        "lyrics_downloaded": "Поиск завершен!\nНайдено текстов: {count} из {total}",
        "lyrics_title": "Тексты песен",
        "warning_title": "Внимание",
        "info_title": "Информация",
        "error_title": "Ошибка",
        "search_dialog_title": "Поиск альбома в онлайн-базах",
        "search_query_lbl": "Поисковый запрос:",
        "search_db_lbl": "Базы данных:",
        "btn_search": "🔍 Искать",
        "btn_searching": "Поиск...",
        "search_results_lbl": "Результаты поиска:",
        "search_col_source": "Источник",
        "search_col_artist": "Исполнитель (;)",
        "search_col_album": "Альбом",
        "search_col_year": "Год",
        "search_col_genres": "Жанры / Стили",
        "btn_apply_release": "✅ Применить выбранный альбом к текущей папке",
        "search_select_warn": "Выберите альбом из списка",
        "preview_no_change": "[не изм.]",
        "preview_no_change_file": "(без изм.)",
        "all_databases": "Все базы (MusicBrainz, Discogs, RYM)",
        "clipboard_title": "Буфер обмена",
        "clipboard_empty": "Буфер обмена пуст",
    },
    "en": {
        "title": "AutoTagger RYM — Music Auto-Tagger (RateYourMusic / Discogs / MusicBrainz)",
        "drop_banner": "🎵 DRAG & DROP FOLDERS OR AUDIO FILES HERE FROM FILE EXPLORER",
        "btn_choose_folder": "📁 Choose Folder...",
        "btn_choose_files": "📄 Choose Files...",
        "btn_search_db": "🔍 Search Album in DBs...",
        "btn_clear": "🔄 Clear",
        "btn_lang": "🌐 Русский",
        "url_frame": "Paste URL (RateYourMusic / Discogs / MusicBrainz)",
        "btn_paste": "📋 Paste",
        "btn_load_url": "🔗 Load from URL",
        "albums_header": "Queued Albums:",
        "meta_frame": "Album Metadata",
        "no_cover": "No cover",
        "cover_loaded": "Cover loaded",
        "tag_toolbar": "Tags to write:",
        "btn_all": "✓ All",
        "btn_none": "✗ None",
        "chk_artist": "Album Artist(s) (;):",
        "chk_album": "Album Title:",
        "chk_year": "Release Year:",
        "genre_box": "Album Genres (Select Source)",
        "chk_genre": "Write Genre Tag",
        "rb_genre_merged": "Merge Both",
        "rb_genre_rym": "RateYourMusic:",
        "btn_refetch_rym": "🌐 Refresh RYM",
        "rb_genre_discogs": "Discogs (Styles + Genres):",
        "btn_refetch_discogs": "💿 Refresh Discogs",
        "btn_search_online": "🔍 Search Album in Online DBs...",
        "opts_frame": "Options & Additional Tags",
        "chk_title": "Write Track Titles (Title)",
        "chk_track_num": "Write Track Numbers (Track №)",
        "chk_embed_cover": "Embed Cover in Audio Files",
        "chk_save_cover": "Save cover.jpg to Folder",
        "chk_clean_junk": "Clean Ads/Junk Tags (promo/comments)",
        "chk_fetch_lyrics": "Search Lyrics (LRC/Karaoke)",
        "chk_save_lrc": "Save .lrc Files Next to Tracks",
        "chk_lower_artist": "Lowercase Artist Names",
        "rename_box": "File Renaming",
        "chk_rename_files": "Rename files when tagging",
        "chk_multi_disc_fmt": "Use 01-05 (Disc-Track) in filenames",
        "lbl_pattern": "Filename Template:",
        "btn_rename_files": "✏️ Rename Files",
        "btn_rename_folder": "📁 Folder",
        "btn_fetch_lyrics": "🎤 Fetch Lyrics (LRC) for Album",
        "tree_header": "Tracklist and Tag/Filename Preview:",
        "col_num": "№",
        "col_filename": "Current File",
        "col_new_filename": "New Filename (01. Artist - Title)",
        "col_title": "Track Title",
        "col_artist": "Artist (;)",
        "col_genre": "RYM Genres (lowercase)",
        "btn_apply": "▶️  APPLY & WRITE TAGS",
        "tagging_busy": "⏳ Tagging in progress...",
        "ctx_paste": "Paste",
        "ctx_copy": "Copy",
        "ctx_cut": "Cut",
        "ctx_select_all": "Select All",
        "dialog_choose_folder": "Select folder with album or music",
        "dialog_choose_files": "Select audio files",
        "audio_files_type": "Audio Files",
        "tagging_in_progress": "Tag writing is already running, please wait...",
        "no_albums": "No albums loaded for tagging",
        "tagging_done": "Done",
        "tagging_success": "Successfully processed {count} audio files!\nTags, RYM genres, and lyrics written.",
        "select_album_first": "Please select an album first",
        "select_album_or_drag": "Select or drag an album folder first",
        "url_empty_prompt": "Paste an album URL (RateYourMusic, Discogs or MusicBrainz)",
        "url_fetch_err": "Failed to extract album from specified URL.\nCheck the address or use the search dialog.",
        "rename_success": "Successfully renamed {count} files using template '{pat}'!",
        "rename_title": "Renaming",
        "rename_folder_title": "Rename Album Folder",
        "rename_folder_prompt": "New folder name:",
        "rename_folder_success": "Folder renamed to:\n{folder}",
        "rename_folder_err": "Failed to rename folder: {err}",
        "lyrics_downloaded": "Search completed!\nFound lyrics: {count} of {total}",
        "lyrics_title": "Lyrics",
        "warning_title": "Warning",
        "info_title": "Information",
        "error_title": "Error",
        "search_dialog_title": "Search Album in Online Databases",
        "search_query_lbl": "Search query:",
        "search_db_lbl": "Databases:",
        "btn_search": "🔍 Search",
        "btn_searching": "Searching...",
        "search_results_lbl": "Search Results:",
        "search_col_source": "Source",
        "search_col_artist": "Artist (;)",
        "search_col_album": "Album",
        "search_col_year": "Year",
        "search_col_genres": "Genres / Styles",
        "btn_apply_release": "✅ Apply Selected Album to Current Folder",
        "search_select_warn": "Select an album from the list",
        "preview_no_change": "[unchanged]",
        "preview_no_change_file": "(unchanged)",
        "all_databases": "All databases (MusicBrainz, Discogs, RYM)",
        "clipboard_title": "Clipboard",
        "clipboard_empty": "Clipboard is empty",
    }
}

class AutoTaggerGUI:
    def __init__(self, root: tk.Tk, initial_paths: Optional[List[str]] = None):
        self.root = root
        self.lang = "ru"
        self.root.title(self.tr("title"))
        self.root.geometry("1150x800")
        self.root.minsize(950, 650)

        # Style configuration
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.scanner = AudioScanner()
        self.audio_engine = AudioTagEngine()
        self.url_resolver = AlbumURLResolver()
        self.searcher = UnifiedAlbumSearcher()
        self.processor = AutoTaggerProcessor(
            on_log=self.log_message,
            on_progress=self.update_progress
        )

        # State
        self.album_groups: Dict[Path, List[AudioFileInfo]] = {}
        self.album_prepared: Dict[Path, Tuple[AlbumMetadata, List[Tuple[AudioFileInfo, TrackMetadata]], Optional[Path]]] = {}
        self.current_folder: Optional[Path] = None
        self.cover_photo: Optional[ImageTk.PhotoImage] = None

        self._setup_clipboard_helpers()
        self._build_ui()

        # Hook drag and drop
        if HAS_WINDND:
            windnd.hook_dropfiles(self.root, func=self.on_drop_files)

        if initial_paths:
            self.root.after(100, lambda: self.load_paths(initial_paths))

    def tr(self, key: str, **kwargs) -> str:
        lang_dict = STRINGS.get(self.lang, STRINGS["ru"])
        raw = lang_dict.get(key, STRINGS["ru"].get(key, key))
        if kwargs:
            try:
                return raw.format(**kwargs)
            except Exception:
                return raw
        return raw

    def toggle_language(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        self._apply_language()

    def _apply_language(self):
        self.root.title(self.tr("title"))
        if hasattr(self, 'drop_label'):
            self.drop_label.config(text=self.tr("drop_banner"))
        if hasattr(self, 'btn_choose_folder'):
            self.btn_choose_folder.config(text=self.tr("btn_choose_folder"))
        if hasattr(self, 'btn_choose_files'):
            self.btn_choose_files.config(text=self.tr("btn_choose_files"))
        if hasattr(self, 'btn_search_db'):
            self.btn_search_db.config(text=self.tr("btn_search_db"))
        if hasattr(self, 'btn_clear'):
            self.btn_clear.config(text=self.tr("btn_clear"))
        if hasattr(self, 'btn_lang'):
            self.btn_lang.config(text=self.tr("btn_lang"))

        if hasattr(self, 'url_frame'):
            self.url_frame.config(text=self.tr("url_frame"))
        if hasattr(self, 'btn_paste'):
            self.btn_paste.config(text=self.tr("btn_paste"))
        if hasattr(self, 'btn_load_url'):
            self.btn_load_url.config(text=self.tr("btn_load_url"))

        if hasattr(self, 'lbl_albums_header'):
            self.lbl_albums_header.config(text=self.tr("albums_header"))
        if hasattr(self, 'meta_frame'):
            self.meta_frame.config(text=self.tr("meta_frame"))

        if hasattr(self, 'cover_label') and not self.cover_photo:
            self.cover_label.config(text=self.tr("no_cover"))

        if hasattr(self, 'lbl_tag_toolbar'):
            self.lbl_tag_toolbar.config(text=self.tr("tag_toolbar"))
        if hasattr(self, 'btn_all_tags'):
            self.btn_all_tags.config(text=self.tr("btn_all"))
        if hasattr(self, 'btn_none_tags'):
            self.btn_none_tags.config(text=self.tr("btn_none"))

        if hasattr(self, 'chk_artist'):
            self.chk_artist.config(text=self.tr("chk_artist"))
        if hasattr(self, 'chk_album'):
            self.chk_album.config(text=self.tr("chk_album"))
        if hasattr(self, 'chk_year'):
            self.chk_year.config(text=self.tr("chk_year"))

        if hasattr(self, 'genre_box'):
            self.genre_box.config(text=self.tr("genre_box"))
        if hasattr(self, 'chk_genre'):
            self.chk_genre.config(text=self.tr("chk_genre"))
        if hasattr(self, 'rb_genre_merged'):
            self.rb_genre_merged.config(text=self.tr("rb_genre_merged"))
        if hasattr(self, 'rb_genre_rym'):
            self.rb_genre_rym.config(text=self.tr("rb_genre_rym"))
        if hasattr(self, 'btn_refetch_rym'):
            self.btn_refetch_rym.config(text=self.tr("btn_refetch_rym"))
        if hasattr(self, 'rb_genre_discogs'):
            self.rb_genre_discogs.config(text=self.tr("rb_genre_discogs"))
        if hasattr(self, 'btn_refetch_discogs'):
            self.btn_refetch_discogs.config(text=self.tr("btn_refetch_discogs"))
        if hasattr(self, 'btn_search_online'):
            self.btn_search_online.config(text=self.tr("btn_search_online"))

        if hasattr(self, 'opts_frame'):
            self.opts_frame.config(text=self.tr("opts_frame"))
        if hasattr(self, 'chk_title'):
            self.chk_title.config(text=self.tr("chk_title"))
        if hasattr(self, 'chk_track_num'):
            self.chk_track_num.config(text=self.tr("chk_track_num"))
        if hasattr(self, 'chk_embed_cover'):
            self.chk_embed_cover.config(text=self.tr("chk_embed_cover"))
        if hasattr(self, 'chk_save_cover'):
            self.chk_save_cover.config(text=self.tr("chk_save_cover"))
        if hasattr(self, 'chk_clean_junk'):
            self.chk_clean_junk.config(text=self.tr("chk_clean_junk"))
        if hasattr(self, 'chk_fetch_lyrics'):
            self.chk_fetch_lyrics.config(text=self.tr("chk_fetch_lyrics"))
        if hasattr(self, 'chk_save_lrc'):
            self.chk_save_lrc.config(text=self.tr("chk_save_lrc"))
        if hasattr(self, 'chk_lower_artist'):
            self.chk_lower_artist.config(text=self.tr("chk_lower_artist"))

        if hasattr(self, 'rename_box'):
            self.rename_box.config(text=self.tr("rename_box"))
        if hasattr(self, 'chk_rename_files'):
            self.chk_rename_files.config(text=self.tr("chk_rename_files"))
        if hasattr(self, 'chk_multi_disc_fmt'):
            self.chk_multi_disc_fmt.config(text=self.tr("chk_multi_disc_fmt"))
        if hasattr(self, 'lbl_pattern'):
            self.lbl_pattern.config(text=self.tr("lbl_pattern"))
        if hasattr(self, 'btn_rename_files'):
            self.btn_rename_files.config(text=self.tr("btn_rename_files"))
        if hasattr(self, 'btn_rename_folder'):
            self.btn_rename_folder.config(text=self.tr("btn_rename_folder"))
        if hasattr(self, 'btn_fetch_lyrics'):
            self.btn_fetch_lyrics.config(text=self.tr("btn_fetch_lyrics"))

        if hasattr(self, 'lbl_tree_header'):
            self.lbl_tree_header.config(text=self.tr("tree_header"))
        if hasattr(self, 'track_tree'):
            self.track_tree.heading("num", text=self.tr("col_num"))
            self.track_tree.heading("filename", text=self.tr("col_filename"))
            self.track_tree.heading("new_filename", text=self.tr("col_new_filename"))
            self.track_tree.heading("title", text=self.tr("col_title"))
            self.track_tree.heading("artist", text=self.tr("col_artist"))
            self.track_tree.heading("genre", text=self.tr("col_genre"))

        if hasattr(self, 'btn_apply'):
            if self.btn_apply["state"] != tk.DISABLED:
                self.btn_apply.config(text=self.tr("btn_apply"))
            else:
                self.btn_apply.config(text=self.tr("tagging_busy"))

        self.refresh_treeview_preview()

    def _setup_clipboard_helpers(self):
        """
        Global keypress handler ensuring Ctrl+V, Ctrl+C, Ctrl+X, Ctrl+A work
        regardless of active keyboard layout (Russian, English, etc.) on Windows.
        """
        def on_control_key(event):
            # Check Control modifier
            is_ctrl = bool(event.state & 4) or bool(event.state & 12) or bool(event.state & 0x20000)
            if not is_ctrl:
                return

            widget = event.widget
            if not isinstance(widget, (tk.Entry, ttk.Entry, tk.Text)):
                return

            # Paste: VK_V = 86, or keysym in ('v', 'V', 'Cyrillic_em', 'Cyrillic_EM')
            if event.keycode == 86 or event.keysym in ('v', 'V', 'Cyrillic_em', 'Cyrillic_EM'):
                try:
                    text = self.root.clipboard_get()
                    if isinstance(widget, (tk.Entry, ttk.Entry)):
                        try:
                            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        except tk.TclError:
                            pass
                        widget.insert(tk.INSERT, text)
                        return "break"
                    elif isinstance(widget, tk.Text):
                        try:
                            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        except tk.TclError:
                            pass
                        widget.insert(tk.INSERT, text)
                        return "break"
                except Exception:
                    pass

            # Copy: VK_C = 67, or keysym in ('c', 'C', 'Cyrillic_es', 'Cyrillic_ES')
            elif event.keycode == 67 or event.keysym in ('c', 'C', 'Cyrillic_es', 'Cyrillic_ES'):
                try:
                    if isinstance(widget, (tk.Entry, ttk.Entry)):
                        text = widget.selection_get()
                    elif isinstance(widget, tk.Text):
                        text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                    else:
                        return
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    return "break"
                except Exception:
                    pass

            # Cut: VK_X = 88, or keysym in ('x', 'X', 'Cyrillic_che', 'Cyrillic_CHE')
            elif event.keycode == 88 or event.keysym in ('x', 'X', 'Cyrillic_che', 'Cyrillic_CHE'):
                try:
                    if isinstance(widget, (tk.Entry, ttk.Entry)):
                        text = widget.selection_get()
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    elif isinstance(widget, tk.Text):
                        text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    else:
                        return
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    return "break"
                except Exception:
                    pass

            # Select All: VK_A = 65, or keysym in ('a', 'A', 'Cyrillic_ef', 'Cyrillic_EF')
            elif event.keycode == 65 or event.keysym in ('a', 'A', 'Cyrillic_ef', 'Cyrillic_EF'):
                try:
                    if isinstance(widget, (tk.Entry, ttk.Entry)):
                        widget.selection_range(0, tk.END)
                        widget.icursor(tk.END)
                        return "break"
                    elif isinstance(widget, tk.Text):
                        widget.tag_add(tk.SEL, "1.0", tk.END)
                        return "break"
                except Exception:
                    pass

        self.root.bind_all("<Control-KeyPress>", on_control_key, add="+")

    def attach_context_menu(self, widget):
        """Attaches a right-click context menu (Paste, Copy, Cut, Select All) to any text/entry widget."""
        menu = tk.Menu(widget, tearoff=0)

        def do_paste():
            try:
                text = self.root.clipboard_get()
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    try:
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    except tk.TclError:
                        pass
                    widget.insert(tk.INSERT, text)
                elif isinstance(widget, tk.Text):
                    try:
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    except tk.TclError:
                        pass
                    widget.insert(tk.INSERT, text)
            except Exception:
                pass

        def do_copy():
            try:
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    text = widget.selection_get()
                elif isinstance(widget, tk.Text):
                    text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    return
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
            except Exception:
                pass

        def do_cut():
            try:
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    text = widget.selection_get()
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                elif isinstance(widget, tk.Text):
                    text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    return
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
            except Exception:
                pass

        def do_select_all():
            try:
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    widget.selection_range(0, tk.END)
                    widget.icursor(tk.END)
                elif isinstance(widget, tk.Text):
                    widget.tag_add(tk.SEL, "1.0", tk.END)
            except Exception:
                pass

        def show_menu(event):
            menu = tk.Menu(widget, tearoff=0)
            menu.add_command(label=f"📋 {self.tr('ctx_paste')} (Ctrl+V)", command=do_paste)
            menu.add_command(label=f"📄 {self.tr('ctx_copy')} (Ctrl+C)", command=do_copy)
            menu.add_command(label=f"✂️ {self.tr('ctx_cut')} (Ctrl+X)", command=do_cut)
            menu.add_separator()
            menu.add_command(label=f"🔘 {self.tr('ctx_select_all')} (Ctrl+A)", command=do_select_all)
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        widget.bind("<Button-3>", show_menu)

    def paste_url_from_clipboard(self):
        """Pastes URL from system clipboard directly into the URL field and logs it."""
        try:
            text = self.root.clipboard_get().strip()
            if text:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, text)
                self.log_message(f"📋 Вставлена ссылка: {text}")
                if any(domain in text.lower() for domain in ["rateyourmusic.com", "discogs.com", "musicbrainz.org"]):
                    self.apply_url()
            else:
                messagebox.showinfo(self.tr("clipboard_title"), self.tr("clipboard_empty"))
        except Exception as e:
            self.log_message(f"⚠️ Буфер обмена пуст или недоступен: {e}")

    def set_all_tags(self, state: bool):
        """Enables or disables all tag checkboxes at once."""
        self.write_artist_var.set(state)
        self.write_album_var.set(state)
        self.write_year_var.set(state)
        self.write_genre_var.set(state)
        self.write_title_var.set(state)
        self.write_track_num_var.set(state)
        self.embed_cover_var.set(state)
        self._on_tag_toggle()

    def _on_tag_toggle(self):
        """Reflects tag checkbox state in entry widgets and table preview."""
        self.artist_entry.configure(state=tk.NORMAL if self.write_artist_var.get() else tk.DISABLED)
        self.album_entry.configure(state=tk.NORMAL if self.write_album_var.get() else tk.DISABLED)
        self.year_entry.configure(state=tk.NORMAL if self.write_year_var.get() else tk.DISABLED)
        g_state = tk.NORMAL if self.write_genre_var.get() else tk.DISABLED
        if hasattr(self, 'genre_entry'):
            self.genre_entry.configure(state=g_state)
        if hasattr(self, 'discogs_genre_entry'):
            self.discogs_genre_entry.configure(state=g_state)
        if hasattr(self, 'rb_genre_rym'):
            self.rb_genre_rym.configure(state=g_state)
        if hasattr(self, 'rb_genre_discogs'):
            self.rb_genre_discogs.configure(state=g_state)
        if hasattr(self, 'rb_genre_merged'):
            self.rb_genre_merged.configure(state=g_state)
        if hasattr(self, 'btn_refetch_rym'):
            self.btn_refetch_rym.configure(state=g_state)
        if hasattr(self, 'btn_refetch_discogs'):
            self.btn_refetch_discogs.configure(state=g_state)
        self.refresh_treeview_preview()

    def get_active_genre_string(self) -> str:
        """Returns the chosen genre string based on the radio button selection (RYM, Discogs, or Merged)."""
        src = self.genre_source_var.get() if hasattr(self, 'genre_source_var') else "rym"
        rym_g = self.genre_entry.get().strip() if hasattr(self, 'genre_entry') else ""
        discogs_g = self.discogs_genre_entry.get().strip() if hasattr(self, 'discogs_genre_entry') else ""

        if src == "discogs":
            return discogs_g or rym_g
        elif src == "merged":
            return self._merge_genre_strings(rym_g, discogs_g)
        else: # "rym"
            return rym_g or discogs_g

    @staticmethod
    def _merge_genre_strings(g1: str, g2: str) -> str:
        """Combines two semicolon-separated genre strings without duplicates."""
        parts1 = [p.strip().lower() for p in g1.split(";") if p.strip()]
        parts2 = [p.strip().lower() for p in g2.split(";") if p.strip()]
        merged = []
        for p in parts1 + parts2:
            if p not in merged:
                merged.append(p)
        return "; ".join(merged)

    def _on_genre_source_changed(self):
        self._update_tracks_genre_from_active_choice()
        self.refresh_treeview_preview()

    def _on_genre_text_edited(self):
        self._update_tracks_genre_from_active_choice()
        self.refresh_treeview_preview()

    def _update_tracks_genre_from_active_choice(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            return
        active_g = self.get_active_genre_string()
        album_meta, matched_pairs, _ = self.album_prepared[self.current_folder]
        for _, trk in matched_pairs:
            trk.genre = active_g

    def _build_ui(self):
        # 1. Top Drop Area & Toolbar
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        self.drop_label = tk.Label(
            top_frame,
            text=self.tr("drop_banner"),
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Segoe UI", 12, "bold"),
            relief=tk.RIDGE,
            padx=15,
            pady=12,
            cursor="hand2"
        )
        self.drop_label.pack(fill=tk.X, pady=(0, 8))
        self.drop_label.bind("<Button-1>", lambda e: self.choose_folder())

        # Buttons row
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 6))

        self.btn_choose_folder = ttk.Button(btn_frame, text=self.tr("btn_choose_folder"), command=self.choose_folder)
        self.btn_choose_folder.pack(side=tk.LEFT, padx=3)

        self.btn_choose_files = ttk.Button(btn_frame, text=self.tr("btn_choose_files"), command=self.choose_files)
        self.btn_choose_files.pack(side=tk.LEFT, padx=3)

        self.btn_search_db = ttk.Button(btn_frame, text=self.tr("btn_search_db"), command=self.open_search_dialog)
        self.btn_search_db.pack(side=tk.LEFT, padx=3)

        self.btn_clear = ttk.Button(btn_frame, text=self.tr("btn_clear"), command=self.clear_all)
        self.btn_clear.pack(side=tk.LEFT, padx=3)

        self.btn_lang = ttk.Button(btn_frame, text=self.tr("btn_lang"), command=self.toggle_language)
        self.btn_lang.pack(side=tk.LEFT, padx=3)

        # URL Input Bar with Paste button and Context menu
        self.url_frame = ttk.LabelFrame(top_frame, text=self.tr("url_frame"), padding="5")
        self.url_frame.pack(fill=tk.X, pady=(0, 4))

        self.url_entry = ttk.Entry(self.url_frame, font=("Segoe UI", 9))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.url_entry.bind("<Return>", lambda e: self.apply_url())
        self.attach_context_menu(self.url_entry)

        self.btn_paste = ttk.Button(self.url_frame, text=self.tr("btn_paste"), command=self.paste_url_from_clipboard)
        self.btn_paste.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_load_url = ttk.Button(self.url_frame, text=self.tr("btn_load_url"), command=self.apply_url)
        self.btn_load_url.pack(side=tk.RIGHT)

        # 2. Middle Paned Window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

        # Left Column: Scrollable container for Albums & Metadata
        left_container = ttk.Frame(main_paned, width=390, padding="2")
        main_paned.add(left_container, weight=1)

        left_canvas = tk.Canvas(left_container, borderwidth=0, highlightthickness=0)
        left_scroll = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=left_canvas.yview)
        left_frame = ttk.Frame(left_canvas, padding="4")

        left_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        left_canvas_win = left_canvas.create_window((0, 0), window=left_frame, anchor="nw")

        def _on_canvas_configure(e):
            left_canvas.itemconfig(left_canvas_win, width=e.width)

        left_canvas.bind("<Configure>", _on_canvas_configure)
        left_canvas.configure(yscrollcommand=left_scroll.set)

        def _on_left_mousewheel(e):
            left_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        left_container.bind("<Enter>", lambda _: left_canvas.bind_all("<MouseWheel>", _on_left_mousewheel))
        left_container.bind("<Leave>", lambda _: left_canvas.unbind_all("<MouseWheel>"))

        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_albums_header = ttk.Label(left_frame, text=self.tr("albums_header"), font=("Segoe UI", 10, "bold"))
        self.lbl_albums_header.pack(anchor=tk.W)
        self.album_listbox = tk.Listbox(left_frame, height=4, font=("Segoe UI", 9))
        self.album_listbox.pack(fill=tk.X, pady=3)
        self.album_listbox.bind("<<ListboxSelect>>", self.on_album_selected)

        # Metadata Editor Frame with Checkboxes
        self.meta_frame = ttk.LabelFrame(left_frame, text=self.tr("meta_frame"), padding="8")
        self.meta_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        # Cover Preview
        self.cover_label = tk.Label(self.meta_frame, text=self.tr("no_cover"), bg="#bdc3c7", width=18, height=7)
        self.cover_label.pack(pady=3)

        # Quick tag selection toolbar
        tag_toolbar = ttk.Frame(self.meta_frame)
        tag_toolbar.pack(fill=tk.X, pady=(2, 4))
        self.lbl_tag_toolbar = ttk.Label(tag_toolbar, text=self.tr("tag_toolbar"), font=("Segoe UI", 9, "bold"))
        self.lbl_tag_toolbar.pack(side=tk.LEFT)
        self.btn_none_tags = ttk.Button(tag_toolbar, text=self.tr("btn_none"), width=7, command=lambda: self.set_all_tags(False))
        self.btn_none_tags.pack(side=tk.RIGHT, padx=1)
        self.btn_all_tags = ttk.Button(tag_toolbar, text=self.tr("btn_all"), width=6, command=lambda: self.set_all_tags(True))
        self.btn_all_tags.pack(side=tk.RIGHT, padx=1)

        # 1. Artist
        self.write_artist_var = tk.BooleanVar(value=True)
        self.chk_artist = ttk.Checkbutton(self.meta_frame, text=self.tr("chk_artist"), variable=self.write_artist_var, command=self._on_tag_toggle)
        self.chk_artist.pack(anchor=tk.W)
        self.artist_entry = ttk.Entry(self.meta_frame, font=("Segoe UI", 9))
        self.artist_entry.pack(fill=tk.X, pady=(0, 4))
        self.attach_context_menu(self.artist_entry)

        # 2. Album
        self.write_album_var = tk.BooleanVar(value=True)
        self.chk_album = ttk.Checkbutton(self.meta_frame, text=self.tr("chk_album"), variable=self.write_album_var, command=self._on_tag_toggle)
        self.chk_album.pack(anchor=tk.W)
        self.album_entry = ttk.Entry(self.meta_frame, font=("Segoe UI", 9))
        self.album_entry.pack(fill=tk.X, pady=(0, 4))
        self.attach_context_menu(self.album_entry)

        # 3. Year
        self.write_year_var = tk.BooleanVar(value=True)
        self.chk_year = ttk.Checkbutton(self.meta_frame, text=self.tr("chk_year"), variable=self.write_year_var, command=self._on_tag_toggle)
        self.chk_year.pack(anchor=tk.W)
        self.year_entry = ttk.Entry(self.meta_frame, font=("Segoe UI", 9))
        self.year_entry.pack(fill=tk.X, pady=(0, 4))
        self.attach_context_menu(self.year_entry)

        # 4. Genre Choice Section (RYM, Discogs, Merged)
        self.write_genre_var = tk.BooleanVar(value=True)
        self.genre_source_var = tk.StringVar(value="rym")

        self.genre_box = ttk.LabelFrame(self.meta_frame, text=self.tr("genre_box"), padding="5")
        self.genre_box.pack(fill=tk.X, pady=(2, 4))

        # Header inside genre_box: Master checkbox and "Merge both" radio button
        top_genre_row = ttk.Frame(self.genre_box)
        top_genre_row.pack(fill=tk.X, pady=(0, 2))
        self.chk_genre = ttk.Checkbutton(
            top_genre_row,
            text=self.tr("chk_genre"),
            variable=self.write_genre_var,
            command=self._on_tag_toggle
        )
        self.chk_genre.pack(side=tk.LEFT)

        self.rb_genre_merged = ttk.Radiobutton(
            top_genre_row,
            text=self.tr("rb_genre_merged"),
            variable=self.genre_source_var,
            value="merged",
            command=self._on_genre_source_changed
        )
        self.rb_genre_merged.pack(side=tk.RIGHT)

        # RateYourMusic selector row & input
        rym_header_row = ttk.Frame(self.genre_box)
        rym_header_row.pack(fill=tk.X, pady=(2, 1))
        self.rb_genre_rym = ttk.Radiobutton(
            rym_header_row,
            text=self.tr("rb_genre_rym"),
            variable=self.genre_source_var,
            value="rym",
            command=self._on_genre_source_changed
        )
        self.rb_genre_rym.pack(side=tk.LEFT)
        self.btn_refetch_rym = ttk.Button(
            rym_header_row,
            text=self.tr("btn_refetch_rym"),
            command=self.refetch_genres
        )
        self.btn_refetch_rym.pack(side=tk.RIGHT)

        self.genre_entry = ttk.Entry(self.genre_box, font=("Segoe UI", 9))
        self.genre_entry.pack(fill=tk.X, pady=(0, 3))
        self.attach_context_menu(self.genre_entry)
        self.genre_entry.bind("<KeyRelease>", lambda e: self._on_genre_text_edited())

        # Discogs selector row & input
        discogs_header_row = ttk.Frame(self.genre_box)
        discogs_header_row.pack(fill=tk.X, pady=(2, 1))
        self.rb_genre_discogs = ttk.Radiobutton(
            discogs_header_row,
            text=self.tr("rb_genre_discogs"),
            variable=self.genre_source_var,
            value="discogs",
            command=self._on_genre_source_changed
        )
        self.rb_genre_discogs.pack(side=tk.LEFT)
        self.btn_refetch_discogs = ttk.Button(
            discogs_header_row,
            text=self.tr("btn_refetch_discogs"),
            command=self.refetch_discogs_genres
        )
        self.btn_refetch_discogs.pack(side=tk.RIGHT)

        self.discogs_genre_entry = ttk.Entry(self.genre_box, font=("Segoe UI", 9))
        self.discogs_genre_entry.pack(fill=tk.X, pady=(0, 2))
        self.attach_context_menu(self.discogs_genre_entry)
        self.discogs_genre_entry.bind("<KeyRelease>", lambda e: self._on_genre_text_edited())

        self.btn_search_online = ttk.Button(self.meta_frame, text=self.tr("btn_search_online"), command=self.open_search_dialog)
        self.btn_search_online.pack(fill=tk.X, pady=(2, 4))

        # Checkboxes & Options Frame
        self.opts_frame = ttk.LabelFrame(self.meta_frame, text=self.tr("opts_frame"), padding="6")
        self.opts_frame.pack(fill=tk.X, pady=4)

        self.write_title_var = tk.BooleanVar(value=True)
        self.chk_title = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_title"), variable=self.write_title_var, command=self._on_tag_toggle)
        self.chk_title.pack(anchor=tk.W)

        self.write_track_num_var = tk.BooleanVar(value=True)
        self.chk_track_num = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_track_num"), variable=self.write_track_num_var, command=self._on_tag_toggle)
        self.chk_track_num.pack(anchor=tk.W)

        self.embed_cover_var = tk.BooleanVar(value=True)
        self.chk_embed_cover = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_embed_cover"), variable=self.embed_cover_var)
        self.chk_embed_cover.pack(anchor=tk.W)

        self.save_cover_var = tk.BooleanVar(value=True)
        self.chk_save_cover = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_save_cover"), variable=self.save_cover_var)
        self.chk_save_cover.pack(anchor=tk.W)

        self.clean_junk_var = tk.BooleanVar(value=True)
        self.chk_clean_junk = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_clean_junk"), variable=self.clean_junk_var)
        self.chk_clean_junk.pack(anchor=tk.W)

        self.fetch_lyrics_var = tk.BooleanVar(value=True)
        self.chk_fetch_lyrics = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_fetch_lyrics"), variable=self.fetch_lyrics_var)
        self.chk_fetch_lyrics.pack(anchor=tk.W)

        self.save_lrc_var = tk.BooleanVar(value=True)
        self.chk_save_lrc = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_save_lrc"), variable=self.save_lrc_var)
        self.chk_save_lrc.pack(anchor=tk.W)

        self.lower_artist_var = tk.BooleanVar(value=False)
        self.chk_lower_artist = ttk.Checkbutton(self.opts_frame, text=self.tr("chk_lower_artist"), variable=self.lower_artist_var, command=self.toggle_artist_casing)
        self.chk_lower_artist.pack(anchor=tk.W)

        # Renaming Pattern Section
        self.rename_box = ttk.LabelFrame(self.meta_frame, text=self.tr("rename_box"), padding="5")
        self.rename_box.pack(fill=tk.X, pady=4)

        self.rename_files_var = tk.BooleanVar(value=True)
        self.chk_rename_files = ttk.Checkbutton(self.rename_box, text=self.tr("chk_rename_files"), variable=self.rename_files_var, command=self.refresh_treeview_preview)
        self.chk_rename_files.pack(anchor=tk.W)

        self.multi_disc_format_var = tk.BooleanVar(value=True)
        self.chk_multi_disc_fmt = ttk.Checkbutton(self.rename_box, text=self.tr("chk_multi_disc_fmt"), variable=self.multi_disc_format_var, command=self.refresh_treeview_preview)
        self.chk_multi_disc_fmt.pack(anchor=tk.W)

        self.lbl_pattern = ttk.Label(self.rename_box, text=self.tr("lbl_pattern"))
        self.lbl_pattern.pack(anchor=tk.W, pady=(3, 1))

        self.pattern_combo = ttk.Combobox(
            self.rename_box,
            values=[
                "01. Artist - Title",
                "01. Title",
                "01 - Artist - Title",
                "01 - Title",
                "01-05. Artist - Title",
                "01-05. Title",
                "Artist - Title"
            ],
            state="readonly"
        )
        self.pattern_combo.current(0)
        self.pattern_combo.pack(fill=tk.X, pady=(0, 4))
        self.pattern_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_treeview_preview())

        btn_row = ttk.Frame(self.rename_box)
        btn_row.pack(fill=tk.X, pady=2)
        self.btn_rename_files = ttk.Button(btn_row, text=self.tr("btn_rename_files"), command=self.rename_current_files_now)
        self.btn_rename_files.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.btn_rename_folder = ttk.Button(btn_row, text=self.tr("btn_rename_folder"), command=self.rename_current_folder_now)
        self.btn_rename_folder.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        self.btn_fetch_lyrics = ttk.Button(self.meta_frame, text=self.tr("btn_fetch_lyrics"), command=self.fetch_lyrics_for_current_album)
        self.btn_fetch_lyrics.pack(fill=tk.X, pady=2)

        # Right Column: Tracklist Table
        right_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(right_frame, weight=3)

        self.lbl_tree_header = ttk.Label(right_frame, text=self.tr("tree_header"), font=("Segoe UI", 10, "bold"))
        self.lbl_tree_header.pack(anchor=tk.W)

        cols = ("num", "filename", "new_filename", "title", "artist", "genre")
        self.track_tree = ttk.Treeview(right_frame, columns=cols, show="headings", selectmode="browse")
        self.track_tree.heading("num", text=self.tr("col_num"))
        self.track_tree.heading("filename", text=self.tr("col_filename"))
        self.track_tree.heading("new_filename", text=self.tr("col_new_filename"))
        self.track_tree.heading("title", text=self.tr("col_title"))
        self.track_tree.heading("artist", text=self.tr("col_artist"))
        self.track_tree.heading("genre", text=self.tr("col_genre"))

        self.track_tree.column("num", width=35, anchor=tk.CENTER)
        self.track_tree.column("filename", width=140)
        self.track_tree.column("new_filename", width=220)
        self.track_tree.column("title", width=160)
        self.track_tree.column("artist", width=140)
        self.track_tree.column("genre", width=200)

        tree_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.track_tree.yview)
        self.track_tree.configure(yscrollcommand=tree_scroll.set)
        self.track_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. Bottom Controls, Progress, Log
        bot_frame = ttk.Frame(self.root, padding="10")
        bot_frame.pack(fill=tk.X)

        self.btn_apply = tk.Button(
            bot_frame,
            text=self.tr("btn_apply"),
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.start_tagging_thread
        )
        self.btn_apply.pack(fill=tk.X, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(bot_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.log_text = tk.Text(bot_frame, height=5, state=tk.DISABLED, bg="#1e272e", fg="#d2dae2", font=("Consolas", 9))
        self.log_text.pack(fill=tk.X)
        self.attach_context_menu(self.log_text)

    def log_message(self, msg: str):
        def _append():
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
        self.root.after(0, _append)

    def update_progress(self, current: int, total: int, msg: str):
        def _prog():
            if total > 0:
                self.progress_bar["maximum"] = total
                self.progress_bar["value"] = current
            self.log_message(f"[{current}/{total}] {msg}")
        self.root.after(0, _prog)

    def on_drop_files(self, file_paths):
        decoded = []
        for p in file_paths:
            if isinstance(p, bytes):
                try:
                    decoded.append(p.decode("utf-8"))
                except Exception:
                    decoded.append(p.decode("cp1251"))
            else:
                decoded.append(str(p))
        self.load_paths(decoded)

    def choose_folder(self):
        folder = filedialog.askdirectory(title=self.tr("dialog_choose_folder"))
        if folder:
            self.load_paths([folder])

    def choose_files(self):
        files = filedialog.askopenfilenames(
            title=self.tr("dialog_choose_files"),
            filetypes=[(self.tr("audio_files_type"), "*.mp3 *.flac *.m4a *.ogg *.opus *.wav")]
        )
        if files:
            self.load_paths(list(files))

    def clear_all(self):
        self.album_groups.clear()
        self.album_prepared.clear()
        self.current_folder = None
        self.album_listbox.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.album_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        if hasattr(self, 'discogs_genre_entry'):
            self.discogs_genre_entry.delete(0, tk.END)
        self.url_entry.delete(0, tk.END)
        for item in self.track_tree.get_children():
            self.track_tree.delete(item)
        self.cover_label.configure(image="", text="Нет обложки")
        self.cover_photo = None
        self.progress_bar["value"] = 0
        self.log_message("🗑️ Список очищен")

    def load_paths(self, paths: List[str]):
        threading.Thread(target=self._scan_and_prepare, args=(paths,), daemon=True).start()

    def _scan_and_prepare(self, paths: List[str]):
        self.log_message("🔍 Сканирование выбранных путей...")
        groups = self.scanner.scan_paths(paths)
        if not groups:
            self.log_message("❌ Аудиофайлы не найдены")
            return

        for folder, files in groups.items():
            self.album_groups[folder] = files
            self.log_message(f"📁 Загрузка альбома: {folder.name} ({len(files)} треков)...")
            
            # Prepare metadata
            album_meta, matched_pairs, cover_path = self.processor.prepare_album(
                folder, files
            )
            self.album_prepared[folder] = (album_meta, matched_pairs, cover_path)

        def _update_ui():
            self.album_listbox.delete(0, tk.END)
            for folder in self.album_groups:
                meta, _, _ = self.album_prepared[folder]
                disc_info = f" [{len(set(t.disc_number for t in meta.tracks))} CD]" if meta.is_multi_disc() else ""
                label = f"{meta.album_artist} - {meta.title}{disc_info}" if meta.title else folder.name
                self.album_listbox.insert(tk.END, label)

            if self.album_groups:
                self.album_listbox.select_set(0)
                first_folder = list(self.album_groups.keys())[0]
                self.display_album(first_folder)

        self.root.after(0, _update_ui)

    def on_album_selected(self, event):
        sel = self.album_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        folders = list(self.album_groups.keys())
        if idx < len(folders):
            self.display_album(folders[idx])

    def display_album(self, folder: Path):
        self.current_folder = folder
        if folder not in self.album_prepared:
            return

        album_meta, matched_pairs, cover_path = self.album_prepared[folder]

        # Update text fields
        self.artist_entry.delete(0, tk.END)
        self.artist_entry.insert(0, album_meta.album_artist)

        self.album_entry.delete(0, tk.END)
        self.album_entry.insert(0, album_meta.title)

        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, album_meta.year or "")

        self.genre_entry.delete(0, tk.END)
        self.genre_entry.insert(0, album_meta.rym_genres_str or "")

        if hasattr(self, 'discogs_genre_entry'):
            self.discogs_genre_entry.delete(0, tk.END)
            self.discogs_genre_entry.insert(0, getattr(album_meta, 'discogs_genres_str', "") or "")

        # Auto-select source if RYM is empty but Discogs is present
        if hasattr(self, 'genre_source_var'):
            if not album_meta.rym_genres_str and getattr(album_meta, 'discogs_genres_str', ""):
                if self.genre_source_var.get() == "rym":
                    self.genre_source_var.set("discogs")

        self._on_tag_toggle()

        # Display cover
        self._display_cover(folder, cover_path)

        # Render track table
        self._render_track_tree()

    def _render_track_tree(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            return

        album_meta, matched_pairs, _ = self.album_prepared[self.current_folder]
        for item in self.track_tree.get_children():
            self.track_tree.delete(item)

        active_genre = self.get_active_genre_string()
        pat = self.pattern_combo.get() if hasattr(self, 'pattern_combo') else "01. Artist - Title"
        is_multi = album_meta.is_multi_disc()
        multi_fmt = self.multi_disc_format_var.get() if hasattr(self, 'multi_disc_format_var') else True

        for f_info, track in matched_pairs:
            if self.rename_files_var.get():
                new_fname = self.processor.renamer.generate_new_filename(
                    track, f_info.extension, pattern=pat, is_multi_disc=is_multi, multi_disc_format=multi_fmt
                )
            else:
                new_fname = f"{self.tr('preview_no_change_file')} {f_info.filename}"

            if self.write_track_num_var.get():
                t_num = f"{track.track_number:02d}"
            else:
                if f_info.existing_track_num:
                    t_num = f"({f_info.existing_track_num:02d})"
                else:
                    t_num = f"({f_info.existing_track_num or '-'})"

            t_title = track.title if self.write_title_var.get() else f"{self.tr('preview_no_change')} {f_info.existing_title or f_info.filename}"
            t_artist = track.artist if self.write_artist_var.get() else f"{self.tr('preview_no_change')} {f_info.existing_artist or '-'}"
            t_genre = (active_genre or track.genre or "-") if self.write_genre_var.get() else f"{self.tr('preview_no_change')} {f_info.existing_genre or '-'}"

            self.track_tree.insert("", tk.END, values=(
                t_num,
                f_info.filename,
                new_fname,
                t_title,
                t_artist,
                t_genre
            ))

    def refresh_treeview_preview(self):
        self._render_track_tree()

    def rename_current_files_now(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            messagebox.showwarning(self.tr("warning_title"), self.tr("select_album_first"))
            return

        album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
        pat = self.pattern_combo.get()
        is_multi = album_meta.is_multi_disc()
        multi_fmt = self.multi_disc_format_var.get() if hasattr(self, 'multi_disc_format_var') else True
        count = 0
        for f_info, track in matched_pairs:
            new_fname = self.processor.renamer.generate_new_filename(
                track, f_info.extension, pattern=pat, is_multi_disc=is_multi, multi_disc_format=multi_fmt
            )
            old_lrc = f_info.path.with_suffix(".lrc")
            ok, final_p, msg = self.processor.renamer.rename_file(f_info.path, new_fname)
            if ok:
                new_lrc = final_p.with_suffix(".lrc")
                if old_lrc.exists() and old_lrc != new_lrc:
                    try:
                        old_lrc.rename(new_lrc)
                    except Exception:
                        pass
                f_info.path = final_p
                f_info.filename = final_p.name
                count += 1
                self.log_message(f"✏️ Переименован: {new_fname}")
            else:
                self.log_message(f"⚠️ {f_info.filename}: {msg}")

        self.display_album(self.current_folder)
        messagebox.showinfo(self.tr("rename_title"), self.tr("rename_success", count=count, pat=pat))

    def fetch_lyrics_for_current_album(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            messagebox.showwarning(self.tr("warning_title"), self.tr("select_album_first"))
            return

        album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
        save_lrc = self.save_lrc_var.get()

        def _worker():
            self.log_message(f"🎤 Запуск поиска текстов песен для альбома '{album_meta.title}'...")
            found_count = 0
            for idx, (f_info, track) in enumerate(matched_pairs):
                self.log_message(f"[{idx+1}/{len(matched_pairs)}] Поиск текста: {track.artist} - {track.title}...")
                lrc_text = self.processor.lyrics_mgr.fetch_lyrics(track.artist, track.title, album=album_meta.title)
                if lrc_text:
                    found_count += 1
                    self.log_message(f"✨ Текст найден: {track.title}")
                    if save_lrc:
                        lrc_path = self.processor.lyrics_mgr.save_lrc_file(f_info.path, lrc_text)
                        if lrc_path:
                            self.log_message(f"💾 Файл сохранен: {lrc_path.name}")
                    # Also embed into audio file directly
                    self.audio_engine.apply_tags(f_info.path, track, lyrics_text=lrc_text)
                else:
                    self.log_message(f"ℹ️ Текст не найден: {track.title}")

            def _done():
                messagebox.showinfo(self.tr("lyrics_title"), self.tr("lyrics_downloaded", count=found_count, total=len(matched_pairs)))
            self.root.after(0, _done)

        threading.Thread(target=_worker, daemon=True).start()

    def rename_current_folder_now(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            messagebox.showwarning(self.tr("warning_title"), self.tr("select_album_first"))
            return

        album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
        ok, new_dir, msg = self.processor.renamer.rename_album_folder(
            self.current_folder, album_meta.album_artist, album_meta.title, album_meta.year
        )
        if ok:
            old_folder = self.current_folder
            files = self.album_groups.pop(old_folder)
            prep = self.album_prepared.pop(old_folder)

            for f_info in files:
                f_info.folder = new_dir
                f_info.path = new_dir / f_info.filename

            self.album_groups[new_dir] = files
            self.album_prepared[new_dir] = prep
            self.current_folder = new_dir

            self.log_message(f"📁 Папка альбома переименована в: {new_dir.name}")
            self.album_listbox.delete(0, tk.END)
            for fldr in self.album_groups:
                m, _, _ = self.album_prepared[fldr]
                disc_info = f" [{len(set(t.disc_number for t in m.tracks))} CD]" if m.is_multi_disc() else ""
                self.album_listbox.insert(tk.END, f"{m.album_artist} - {m.title}{disc_info}")
            self.album_listbox.select_set(0)
            self.display_album(new_dir)
            messagebox.showinfo(self.tr("rename_folder_title"), self.tr("rename_folder_success", folder=new_dir.name))
        else:
            messagebox.showerror(self.tr("error_title"), self.tr("rename_folder_err", err=msg))

    def _display_cover(self, folder: Path, cover_path: Optional[Path]):
        img_path = cover_path or (folder / "cover.jpg")
        if img_path and img_path.exists():
            try:
                img = Image.open(img_path)
                img.thumbnail((140, 140))
                self.cover_photo = ImageTk.PhotoImage(img)
                self.cover_label.configure(image=self.cover_photo, text="")
                return
            except Exception:
                pass
        self.cover_label.configure(image="", text=self.tr("no_cover"))
        self.cover_photo = None

    def toggle_artist_casing(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            return
        album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
        is_lower = self.lower_artist_var.get()

        if is_lower:
            new_artist = album_meta.album_artist.lower()
        else:
            new_artist = album_meta.album_artist

        self.artist_entry.delete(0, tk.END)
        self.artist_entry.insert(0, new_artist)

    def refetch_genres(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            return
        artist = self.artist_entry.get().strip()
        album = self.album_entry.get().strip()

        def _fetch():
            self.log_message(f"🌐 Повторный запрос жанров на RYM для: {artist} - {album}...")
            genres = self.processor.rym.search_yahoo(artist, album)
            if not genres:
                genres = self.processor.rym.search_ddg(artist, album)
            formatted = "; ".join(genres) if genres else ""

            def _update():
                self.genre_entry.delete(0, tk.END)
                self.genre_entry.insert(0, formatted)
                self.log_message(f"✨ Полученные RYM жанры: {formatted or 'Не найдены'}")
                album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
                album_meta.rym_genres_str = formatted
                self._update_tracks_genre_from_active_choice()
                self.refresh_treeview_preview()

            self.root.after(0, _update)

        threading.Thread(target=_fetch, daemon=True).start()

    def refetch_discogs_genres(self):
        if not self.current_folder or self.current_folder not in self.album_prepared:
            return
        artist = self.artist_entry.get().strip()
        album = self.album_entry.get().strip()

        def _fetch():
            self.log_message(f"💿 Повторный запрос жанров/стилей на Discogs для: {artist} - {album}...")
            cache_key = f"{artist} - {album}".strip().lower()
            if hasattr(self.processor.discogs, "cache") and cache_key in self.processor.discogs.cache:
                del self.processor.discogs.cache[cache_key]
            formatted = self.processor.discogs.get_formatted_genres(artist, album)

            def _update():
                if hasattr(self, "discogs_genre_entry"):
                    self.discogs_genre_entry.delete(0, tk.END)
                    self.discogs_genre_entry.insert(0, formatted)
                self.log_message(f"💿 Полученные Discogs жанры: {formatted or 'Не найдены'}")
                album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
                album_meta.discogs_genres_str = formatted
                self._update_tracks_genre_from_active_choice()
                self.refresh_treeview_preview()

            self.root.after(0, _update)

        threading.Thread(target=_fetch, daemon=True).start()

    def apply_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showinfo(self.tr("info_title"), self.tr("url_empty_prompt"))
            return
        if not self.current_folder:
            messagebox.showwarning(self.tr("warning_title"), self.tr("select_album_or_drag"))
            return

        def _resolve():
            self.log_message(f"🔗 Обработка ссылки: {url}...")
            meta = self.url_resolver.resolve_url(url, lowercase_artists=self.lower_artist_var.get())
            if not meta:
                self.log_message("❌ Не удалось получить метаданные по указанной ссылке")
                def _err():
                    messagebox.showerror(self.tr("error_title"), self.tr("url_fetch_err"))
                self.root.after(0, _err)
                return

            self._apply_custom_metadata_to_current(meta)

        threading.Thread(target=_resolve, daemon=True).start()

    def _apply_custom_metadata_to_current(self, meta: AlbumMetadata):
        folder = self.current_folder
        files = self.album_groups[folder]

        # Match files to new tracklist
        raw_matched = self.processor.mb.match_files_to_tracks(files, meta)
        active_genre = meta.rym_genres_str or getattr(meta, 'discogs_genres_str', "")
        matched_pairs = []
        for i, (f, track) in enumerate(raw_matched):
            if not track:
                t_num = f.existing_track_num or (i + 1)
                track = TrackMetadata(
                    title=f.existing_title or f.path.stem,
                    artist=meta.album_artist,
                    track_number=t_num,
                    total_tracks=len(files),
                    year=meta.year,
                    album=meta.title,
                    album_artist=meta.album_artist,
                    genre=active_genre
                )
            else:
                track.genre = active_genre
                if (not track.artist or track.artist.lower() == meta.album_artist.lower()):
                    if f.existing_artist and f.existing_artist.lower() != meta.album_artist.lower():
                        track.artist = self.processor.mb.format_artists(f.existing_artist, lowercase=self.processor.lowercase_artists)
                    else:
                        stem = f.path.stem
                        if " - " in stem:
                            left = stem.split(" - ", 1)[0]
                            left_clean = re.sub(r'^\s*\d+[\s\.\-_]+', '', left).strip()
                            if left_clean and left_clean.lower() != meta.album_artist.lower():
                                track.artist = self.processor.mb.format_artists(left_clean, lowercase=self.processor.lowercase_artists)
            matched_pairs.append((f, track))

        # Cover art
        cover_path = None
        if self.save_cover_var.get():
            if meta.cover_url:
                img_bytes = self.processor.cover_mgr.download_cover_bytes(meta.cover_url)
                if img_bytes:
                    cover_path = folder / "cover.jpg"
                    cover_path.write_bytes(img_bytes)
            if not cover_path or not cover_path.exists():
                cover_path = self.processor.cover_mgr.save_cover_to_folder(
                    folder, meta.album_artist, meta.title, musicbrainz_id=meta.musicbrainz_id
                )

        self.album_prepared[folder] = (meta, matched_pairs, cover_path)

        def _update():
            self.display_album(folder)
            self.log_message(f"✅ Альбом '{meta.title}' успешно обновлен!")
            messagebox.showinfo(self.tr("info_title"), f"{meta.album_artist} — {meta.title} ({meta.year})")

        self.root.after(0, _update)

    def open_search_dialog(self):
        if not self.current_folder:
            messagebox.showwarning(self.tr("warning_title"), self.tr("select_album_or_drag"))
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(self.tr("search_dialog_title"))
        dialog.geometry("800x520")
        dialog.minsize(700, 450)
        dialog.transient(self.root)
        dialog.grab_set()

        # Search bar
        s_frame = ttk.Frame(dialog, padding="10")
        s_frame.pack(fill=tk.X)

        ttk.Label(s_frame, text=self.tr("search_query_lbl")).pack(anchor=tk.W)
        query_frame = ttk.Frame(s_frame)
        query_frame.pack(fill=tk.X, pady=4)

        # Initial query from current album or folder
        album_meta, _, _ = self.album_prepared[self.current_folder]
        init_q = f"{album_meta.album_artist} {album_meta.title}".strip() or self.current_folder.name

        q_entry = ttk.Entry(query_frame, font=("Segoe UI", 10))
        q_entry.insert(0, init_q)
        q_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.attach_context_menu(q_entry)

        btn_search = ttk.Button(query_frame, text=self.tr("btn_search"))
        btn_search.pack(side=tk.RIGHT)

        # Filter
        filter_frame = ttk.Frame(s_frame)
        filter_frame.pack(fill=tk.X, pady=2)
        ttk.Label(filter_frame, text=self.tr("search_db_lbl")).pack(side=tk.LEFT, padx=(0, 6))
        source_combo = ttk.Combobox(filter_frame, values=[self.tr("all_databases"), "Discogs", "MusicBrainz", "RateYourMusic"], state="readonly")
        source_combo.current(0)
        source_combo.pack(side=tk.LEFT)

        # Results table
        r_frame = ttk.Frame(dialog, padding="10")
        r_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(r_frame, text=self.tr("search_results_lbl"), font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)

        cols = ("source", "artist", "album", "year", "genres")
        tree = ttk.Treeview(r_frame, columns=cols, show="headings", selectmode="browse")
        tree.heading("source", text=self.tr("search_col_source"))
        tree.heading("artist", text=self.tr("search_col_artist"))
        tree.heading("album", text=self.tr("search_col_album"))
        tree.heading("year", text=self.tr("search_col_year"))
        tree.heading("genres", text=self.tr("search_col_genres"))

        tree.column("source", width=110)
        tree.column("artist", width=180)
        tree.column("album", width=200)
        tree.column("year", width=55, anchor=tk.CENTER)
        tree.column("genres", width=200)

        s_scroll = ttk.Scrollbar(r_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=s_scroll.set)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        s_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        results_data: List[dict] = []

        def _do_search():
            q = q_entry.get().strip()
            if not q:
                return
            btn_search.configure(state=tk.DISABLED, text=self.tr("btn_searching"))
            tree.delete(*tree.get_children())
            results_data.clear()

            def _worker():
                src_filter = source_combo.get()
                all_res = self.searcher.search_all(q, limit_per_source=6)

                filtered = []
                for r in all_res:
                    s = r.get("source", "")
                    if "Все" in src_filter or "All" in src_filter:
                        filtered.append(r)
                    elif src_filter in s:
                        filtered.append(r)

                def _render():
                    results_data.extend(filtered)
                    for item in filtered:
                        tree.insert("", tk.END, values=(
                            item.get("source"),
                            item.get("artist"),
                            item.get("album"),
                            item.get("year"),
                            item.get("genres")
                        ))
                    btn_search.configure(state=tk.NORMAL, text=self.tr("btn_search"))

                dialog.after(0, _render)

            threading.Thread(target=_worker, daemon=True).start()

        btn_search.configure(command=_do_search)
        q_entry.bind("<Return>", lambda e: _do_search())

        # Select button
        act_frame = ttk.Frame(dialog, padding="10")
        act_frame.pack(fill=tk.X)

        def _choose_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(self.tr("warning_title"), self.tr("search_select_warn"), parent=dialog)
                return
            idx = tree.index(sel[0])
            if idx < len(results_data):
                chosen = results_data[idx]
                dialog.destroy()
                self.log_message(f"Загрузка полных данных выбранного альбома: {chosen.get('display')}...")

                def _fetch_full():
                    meta = self.searcher.get_album_by_candidate(
                        chosen, lowercase_artists=self.lower_artist_var.get()
                    )
                    if meta:
                        self._apply_custom_metadata_to_current(meta)
                    else:
                        self.log_message("❌ Не удалось загрузить подробности релиза")

                threading.Thread(target=_fetch_full, daemon=True).start()

        ttk.Button(act_frame, text=self.tr("btn_apply_release"), command=_choose_selected).pack(fill=tk.X, pady=4)
        tree.bind("<Double-1>", lambda e: _choose_selected())

        # Run initial search
        dialog.after(100, _do_search)

    def start_tagging_thread(self):
        if not self.album_prepared:
            messagebox.showwarning(self.tr("warning_title"), self.tr("no_albums"))
            return

        # Save user edits from entry boxes into current album (if enabled)
        if self.current_folder and self.current_folder in self.album_prepared:
            album_meta, matched_pairs, cover_path = self.album_prepared[self.current_folder]
            if self.write_artist_var.get():
                album_meta.album_artist = self.artist_entry.get().strip()
            if self.write_album_var.get():
                album_meta.title = self.album_entry.get().strip()
            if self.write_year_var.get():
                album_meta.year = self.year_entry.get().strip()
            if self.write_genre_var.get():
                album_meta.rym_genres_str = self.genre_entry.get().strip()
                if hasattr(self, 'discogs_genre_entry'):
                    album_meta.discogs_genres_str = self.discogs_genre_entry.get().strip()

            active_g = self.get_active_genre_string()
            for _, trk in matched_pairs:
                if self.write_album_var.get():
                    trk.album = album_meta.title
                if self.write_artist_var.get():
                    trk.album_artist = album_meta.album_artist
                if self.write_year_var.get():
                    trk.year = album_meta.year
                if self.write_genre_var.get():
                    trk.genre = active_g

        self.btn_apply.configure(state=tk.DISABLED, text=self.tr("tagging_busy"))
        threading.Thread(target=self._execute_tagging, daemon=True).start()

    def _execute_tagging(self):
        total_files = sum(len(pairs) for _, pairs, _ in self.album_prepared.values())
        processed = 0

        save_cover = self.save_cover_var.get()
        embed_cover = self.embed_cover_var.get()
        clean_junk = self.clean_junk_var.get()
        fetch_lrc = self.fetch_lyrics_var.get()
        save_lrc = self.save_lrc_var.get()
        rename_files = self.rename_files_var.get()
        pat = self.pattern_combo.get()

        enabled_tags = {
            "artist": self.write_artist_var.get(),
            "album_artist": self.write_artist_var.get(),
            "album": self.write_album_var.get(),
            "year": self.write_year_var.get(),
            "genre": self.write_genre_var.get(),
            "title": self.write_title_var.get(),
            "track_number": self.write_track_num_var.get(),
            "cover": embed_cover,
            "lyrics": fetch_lrc,
        }

        for folder, (album_meta, matched_pairs, cover_path) in self.album_prepared.items():
            cover_bytes = None
            if embed_cover:
                c_file = cover_path or (folder / "cover.jpg")
                if c_file and c_file.exists():
                    try:
                        cover_bytes = c_file.read_bytes()
                    except Exception:
                        pass

            multi_fmt = self.multi_disc_format_var.get()
            is_multi = album_meta.is_multi_disc()

            for f_info, trk in matched_pairs:
                lrc_text = None
                if fetch_lrc:
                    lrc_text = self.processor.lyrics_mgr.fetch_lyrics(trk.artist, trk.title, album=album_meta.title)
                    if lrc_text and save_lrc:
                        self.processor.lyrics_mgr.save_lrc_file(f_info.path, lrc_text)

                self.audio_engine.apply_tags(
                    f_info.path,
                    trk,
                    cover_image_bytes=cover_bytes,
                    lyrics_text=lrc_text,
                    clean_junk_tags=clean_junk,
                    enabled_tags=enabled_tags,
                    multi_disc_format=multi_fmt
                )

                if rename_files:
                    new_fname = self.processor.renamer.generate_new_filename(
                        trk, f_info.extension, pattern=pat, is_multi_disc=is_multi, multi_disc_format=multi_fmt
                    )
                    old_lrc = f_info.path.with_suffix(".lrc")
                    ok, final_p, msg = self.processor.renamer.rename_file(f_info.path, new_fname)
                    if ok:
                        new_lrc = final_p.with_suffix(".lrc")
                        if old_lrc.exists() and old_lrc != new_lrc:
                            try:
                                old_lrc.rename(new_lrc)
                            except Exception:
                                pass
                        f_info.path = final_p
                        f_info.filename = final_p.name

                processed += 1
                self.update_progress(processed, total_files, f"Записано: {f_info.filename}")

            self.log_message(f"🎉 Альбом '{album_meta.title}' успешно протегирован!")

        self.log_message(f"✅ ВСЕ ТЕГИ УСПЕШНО ЗАПИСАНЫ В {processed} ФАЙЛОВ!")

        def _done():
            self.btn_apply.configure(state=tk.NORMAL, text=self.tr("btn_apply"))
            if self.current_folder:
                self.display_album(self.current_folder)
            messagebox.showinfo(self.tr("tagging_done"), self.tr("tagging_success", count=processed))

        self.root.after(0, _done)


def run_gui(initial_paths: Optional[List[str]] = None):
    root = tk.Tk()
    app = AutoTaggerGUI(root, initial_paths=initial_paths)
    root.mainloop()

if __name__ == "__main__":
    initial = sys.argv[1:] if len(sys.argv) > 1 else None
    run_gui(initial)
