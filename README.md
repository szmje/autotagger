# AutoTagger RYM 🎵

<p align="center">
  <b>Универсальный музыкальный автотеггер с поддержкой жанров RateYourMusic, Discogs, базы MusicBrainz, синхронизированных текстов (.lrc) и стандартов MusicBee.</b>
  <br />
  <i>Universal music auto-tagger with RateYourMusic & Discogs genres, MusicBrainz metadata, synced karaoke lyrics (.lrc), and full MusicBee compatibility.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat" alt="Cross-Platform" />
  <img src="https://img.shields.io/badge/GUI-Tkinter%20%2B%20windnd-blue?style=flat" alt="Tkinter GUI" />
  <img src="https://img.shields.io/badge/Tagging-Mutagen-orange?style=flat" alt="Mutagen" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT" />
</p>

---

<p align="center">
  <b><a href="#-русский">🇷🇺 Читать на русском</a></b> &nbsp;•&nbsp; <b><a href="#-english">🇬🇧 Read in English</a></b>
</p>

---

## 🇷🇺 Русский

**AutoTagger RYM** — мощный инструмент с графическим интерфейсом (GUI) и командной строкой (CLI) для идеального наведения порядка в музыкальной коллекции. Программа автоматически определяет альбомы, загружает официальные метаданные из **MusicBrainz** и **Discogs**, подтягивает нишевые жанры и стили с **RateYourMusic (RYM)**, скачивает синхронизированные караоке-тексты песен (`.lrc`), сохраняет и вшивает обложки высокого разрешения, переименовывает аудиофайлы по выбранному шаблону и гарантирует 100% совместимость с аудиоплеерами (**MusicBee**, **foobar2000**, **AIMP**, мобильные плееры).

---

### ✨ Ключевые возможности

#### 1. 🏷️ Жанры с RateYourMusic и Discogs (на выбор)
- Автоматически находит альбом на **RateYourMusic** и **Discogs**.
- Доступен гибкий переключатель источника жанров в GUI:
  - 🔘 **RateYourMusic**: знаменитые специфичные микрожанры с RYM (например, `cloud rap; drain; ambient pop`).
  - 🔘 **Discogs**: полные стили и жанровые категории конкретного издания.
  - 🔘 **Объединить оба**: комбинирует теги из обеих баз без дубликатов.
- Жанры записываются **строго в нижнем регистре (lowercase)** и разделяются точкой с запятой и пробелом:
  ```text
  alternative rock; post-punk; dream pop
  ```
- Поля ввода с возможностью быстрого ручного редактирования перед записью, а также кнопки **«🌐 Обновить RYM»** и **«💿 Обновить Discogs»**.

#### 2. 👥 Идеальное форматирование совместных артистов (`; `)
- Если у альбома или трека несколько исполнителей, они автоматически форматируются через точку с запятой:
  ```text
  bladee; ecco2k
  yung lean; bladee
  ```
- Любые коллаборации (`&`, `feat.`, `ft.`, `with`, `/`, `,`) приводятся к строгому музыкальному стандарту `; `, что обеспечивает корректное разделение исполнителей в библиотеках **MusicBee**, **foobar2000**, **Navidrome** и **Plex**.

#### 3. 🔍 Поиск по базам и вставка прямых ссылок
- Если альбом редкий или не распознался автоматически:
  - Вставьте прямую ссылку на страницу релиза:
    - **RateYourMusic**: `https://rateyourmusic.com/release/album/...`
    - **Discogs**: `https://www.discogs.com/release/...` или `/master/...`
    - **MusicBrainz**: `https://musicbrainz.org/release/...`
  - **Универсальная вставка (RU / EN)**: горячие клавиши `Ctrl+V`, `Ctrl+C`, `Ctrl+X`, `Ctrl+A` работают на любой раскладке клавиатуры (русской или английской). Также доступны кнопка **«📋 Вставить»** и контекстное меню правой кнопки мыши (ПКМ).
  - Диалоговое окно **«🔍 Найти альбом в базах...»** для ручного поиска сразу по всем источникам с мгновенным применением к выбранной папке.

#### 4. 🎛️ Чекбоксы выборочной записи тегов
- Рядом с каждым полем метаданных есть независимый чекбокс:
  - `Исполнитель(и) альбома`
  - `Название альбома`
  - `Год релиза`
  - `Жанры (Genre)`
  - `Названия треков (Title)`
  - `Номера треков (Track №)`
  - `Вшивание обложки`
  - `Тексты песен (LRC)`
- Быстрые кнопки **«✓ Все»** и **«✗ Снять»**.
- Если снять галочку с поля, существующий тег в файле **не перезаписывается и остаётся нетронутым** (идеально, если у вас уже есть свои кастомные теги).

#### 5. 💿 Полная поддержка Multi-Disc релизов (MusicBee Friendly)
- Автоматически распознаёт многодисковые релизы (2 CD, 3 CD, винилы Side A/B/C/D, DJ-миксы со сложными sub-tracks) из баз данных или структуры папок (`CD1/`, `CD2/`, `Disc 1/`, `Disc 2/`).
- Объединяет треки в единый альбом со сквозным правильным порядком.
- **Строгий стандарт MusicBee**:
  - В тег номера трека (`TRCK` / `tracknumber`) записывается **только порядковый номер трека** (`01`, `02`, `10`).
  - Номер диска пишется **строго отдельно** в тег диска (`TPOS` / `DISCNUMBER` = `01/02`, `02/02`).
  - Это исключает ошибки группировки и сохраняет гибкость настройки масок в MusicBee.
- Опция **«Формат 01-05 (Disc-Track) в именах файлов»** позволяет при желании переименовывать сами файлы на диске как `02-01. Artist - Title.mp3`.

#### 6. ✏️ Переименование файлов и папок
- Предустановленные шаблоны:
  - `01. Artist - Title` (например, `01. bladee - obedient.mp3`)
  - `01. Title`
  - `01 - Artist - Title`
  - `01 - Title`
  - `01-05. Artist - Title` (для мультидисковых релизов)
  - `01-05. Title`
  - `Artist - Title`
- Столбец предпросмотра нового имени в реальном времени.
- Автоматическая безопасная замена недопустимых символов файловой системы Windows (`/ \ : * ? " < > |`).
- Кнопка «📁 Папку» для переименования директории альбома в `Исполнитель - Альбом (Год)`.

#### 7. 🎤 Синхронизированные тексты песен (LRC + караоке)
- Поиск построчных синхронизированных таймкодов караоке через базу `syncedlyrics` (Musixmatch, Deezer, NetEase и др.).
- Автоматическое создание файла `.lrc` рядом с треком (`01. bladee - obedient.lrc`).
- Вшивание текста внутрь аудиофайла (ID3 `USLT`, FLAC `LYRICS`, MP4 `©lyr`).
- Синхронное автоматическое переименование `.lrc` при переименовании аудиофайла.

#### 8. 🖼️ Обложки альбомов в высоком разрешении
- Поиск оригинального арта высокого разрешения (до 1200x1200) на Deezer, Discogs, iTunes.
- Сохранение `cover.jpg` в папку с релизом.
- Вшивание обложки внутрь треков (ID3 APIC, FLAC Picture, MP4 Cover).

#### 9. 🧹 Очистка мусорных тегов и рекламы
- Удаляет спам-комментарии трекеров, рекламу каналов Telegram, ссылки на сайты и баннеры (`COMM`, `WXXX`, `WCOM`, `TENC`, `COMMENT`, `DESCRIPTION`, `URL`, `©cmt`).

#### 10. 🌐 Двуязычный интерфейс (RU / EN в 1 клик)
- Кнопка переключения языка расположена в верхней панели управления (справа от «Очистить»).
- Мгновенное переключение всего интерфейса, кнопок, подсказок, чекбоксов, таблиц и всплывающих окон между **Русским** и **English** без перезапуска приложения.

#### 11. 🎼 Поддерживаемые форматы аудио
- **MP3** (`.mp3` — ID3v2.3 / ID3v2.4)
- **FLAC** (`.flac` — Vorbis Comments)
- **M4A / ALAC / AAC** (`.m4a`, `.mp4`)
- **OGG Vorbis / OPUS** (`.ogg`, `.opus`)
- **WAV / AIFF** (`.wav`, `.aiff`)

---

### 🚀 Быстрый старт

#### Установка зависимостей
Убедитесь, что у вас установлен **Python 3.9+**.
```bash
git clone https://github.com/your-repo/autotagger.git
cd autotagger
pip install -r requirements.txt
```

#### Запуск графического интерфейса (GUI)
Дважды кликните по файлу:
```text
Run_GUI.bat
```
В открывшемся окне:
1. Перетащите папку с альбомом или аудиофайлы из Проводника прямо в окно программы (или нажмите **📁 Выбрать папку...**).
2. Проверьте предпросмотр метаданных, при желании выберите чекбоксы тегов и источник жанров.
3. Нажмите кнопку **▶️ ПРИМЕНИТЬ И ЗАПИСАТЬ ТЕГИ**.

---

## 🇬🇧 English

**AutoTagger RYM** is a comprehensive, modern music tagging application (GUI & CLI) designed to organize your music library to perfection. It retrieves verified official metadata from **MusicBrainz** and **Discogs**, fetches niche and descriptive subgenres from **RateYourMusic (RYM)**, downloads synchronized karaoke lyrics (`.lrc`), embeds high-resolution cover artwork, renames audio files according to customizable templates, and ensures flawless compatibility with audiophile players (**MusicBee**, **foobar2000**, **AIMP**, and mobile music players).

---

### ✨ Key Features

#### 1. 🏷️ RateYourMusic & Discogs Genres (Selectable Source)
- Automatically matches albums against **RateYourMusic** and **Discogs**.
- Flexible genre source selector:
  - 🔘 **RateYourMusic**: distinctive subgenres from RYM (e.g., `cloud rap; drain; ambient pop`).
  - 🔘 **Discogs**: full styles and release genre classifications from Discogs.
  - 🔘 **Merge Both**: combines genres from both databases with automatic deduplication.
- Genres are saved **strictly in lowercase**, separated by a semicolon and space:
  ```text
  alternative rock; post-punk; dream pop
  ```
- Editable entry fields with dedicated **"🌐 Refresh RYM"** and **"💿 Refresh Discogs"** buttons.

#### 2. 👥 Proper Multi-Artist Formatting (`; `)
- Releases and tracks with multiple artists are consistently formatted using `; `:
  ```text
  bladee; ecco2k
  yung lean; bladee
  ```
- Any joint conjunctions (`&`, `feat.`, `ft.`, `with`, `/`, `,`) are automatically normalized into clean semicolon-separated artists. This ensures seamless multi-artist splitting in **MusicBee**, **foobar2000**, **Navidrome**, and **Plex**.

#### 3. 🔍 Direct Database Search & URL Resolver
- For rare, unlisted, or ambiguous albums:
  - Paste a direct link into the URL bar:
    - **RateYourMusic**: `https://rateyourmusic.com/release/album/...`
    - **Discogs**: `https://www.discogs.com/release/...` or `/master/...`
    - **MusicBrainz**: `https://musicbrainz.org/release/...`
  - **Layout-Independent Shortcuts**: `Ctrl+V`, `Ctrl+C`, `Ctrl+X`, and `Ctrl+A` work flawlessly regardless of whether your keyboard is set to Russian, English, or any other layout. Includes a dedicated **"📋 Paste"** button and right-click context menu.
  - Built-in **"🔍 Search Album in DBs..."** dialog to search across all databases and apply any release in a single click.

#### 4. 🎛️ Selective Tagging Checkboxes
- Individual toggles for every tag category:
  - `Album Artist(s)`
  - `Album Title`
  - `Release Year`
  - `Genre`
  - `Track Titles`
  - `Track Numbers`
  - `Embed Cover`
  - `Lyrics (LRC)`
- Quick action buttons: **"✓ All"** and **"✗ None"**.
- Unchecked tags are **left completely untouched** in your audio files (ideal if you already have custom personal tags).

#### 5. 💿 Native Multi-Disc Support (MusicBee Compliant)
- Automatically groups multi-disc releases (2 CD, 3 CD, vinyl Sides A/B/C/D, DJ mixes with nested subtracks) from database metadata or folder structure (`CD1/`, `CD2/`, `Disc 1/`, etc.).
- Continuous sequential sorting and track pairing.
- **Strict MusicBee Tagging Standard**:
  - The track number tag (`TRCK` / `tracknumber`) stores **only the track number** (`01`, `02`, `10`).
  - The disc number is written **separately** (`TPOS` / `DISCNUMBER` = `01/02`, `02/02`).
  - This prevents tag corruption and keeps MusicBee's custom sorting rules intact.
- Optional **"Use 01-05 (Disc-Track) in filenames"** toggle allows naming physical files as `02-01. Artist - Title.mp3` when desired.

#### 6. ✏️ Flexible File & Folder Renaming
- Built-in filename templates:
  - `01. Artist - Title` (e.g., `01. bladee - obedient.mp3`)
  - `01. Title`
  - `01 - Artist - Title`
  - `01 - Title`
  - `01-05. Artist - Title` (for multi-disc releases)
  - `01-05. Title`
  - `Artist - Title`
- Real-time preview column in the tracklist tree.
- Automatic sanitation of Windows-reserved characters (`/ \ : * ? " < > |`).
- Dedicated "📁 Folder" button to rename album directories into `Artist - Album (Year)`.

#### 7. 🎤 Synchronized Karaoke Lyrics (.lrc)
- Automatically retrieves synchronized timestamped lyrics via `syncedlyrics` (Musixmatch, Deezer, NetEase, etc.).
- Generates external `.lrc` files alongside your tracks (`01. bladee - obedient.lrc`).
- Embeds lyrics into audio tags (ID3 `USLT`, FLAC `LYRICS`, MP4 `©lyr`).
- Automatically renames associated `.lrc` files whenever audio files are renamed.

#### 8. 🖼️ High-Resolution Cover Art
- Downloads official artwork in up to 1200x1200 resolution from Deezer, Discogs, or iTunes.
- Saves `cover.jpg` directly into the album directory.
- Embeds the cover image into track tags (ID3 APIC, FLAC Picture, MP4 Cover).

#### 9. 🧹 Junk & Tracker Ad Cleaner
- Strips junk tags, torrent tracker comments, Telegram channel ads, and promotional URLs (`COMM`, `WXXX`, `WCOM`, `TENC`, `COMMENT`, `DESCRIPTION`, `URL`, `©cmt`).

#### 10. 🌐 Instant Bilingual GUI (RU / EN Toggle)
- Language switch button located on the top toolbar (directly next to "Clear").
- Instant switching between **Русский** and **English** for all labels, buttons, headers, dialogs, and messages without needing an application restart.

#### 11. 🎼 Supported Audio Formats
- **MP3** (`.mp3` — ID3v2.3 / ID3v2.4)
- **FLAC** (`.flac` — Vorbis Comments)
- **M4A / ALAC / AAC** (`.m4a`, `.mp4`)
- **OGG Vorbis / OPUS** (`.ogg`, `.opus`)
- **WAV / AIFF** (`.wav`, `.aiff`)

---

### 🚀 Quick Start

#### Requirements & Installation
Make sure you have **Python 3.9+** installed.
```bash
git clone https://github.com/your-repo/autotagger.git
cd autotagger
pip install -r requirements.txt
```

#### Launching the Graphical User Interface (GUI)
Double-click:
```text
Run_GUI.bat
```
Inside the application window:
1. Drag and drop your album folder or audio files directly into the window (or click **📁 Choose Folder...**).
2. Inspect the metadata preview, select tags to write, and choose your preferred genre source.
3. Click **▶️ APPLY & WRITE TAGS**.

---

## 📁 Repository Structure / Структура проекта

```text
autotagger/
├── .gitignore              # Git ignore rules (caches, virtualenvs, temp files)
├── gui.py                  # Tkinter GUI with Drag & Drop and instant i18n
├── main.py                 # Application entry point (CLI and GUI dispatcher)
├── requirements.txt        # Python package dependencies
├── Run_GUI.bat             # Windows batch launcher for the GUI
├── tagger/
│   ├── audio.py            # Audio tag reader/writer (Mutagen engine)
│   ├── coverart.py         # High-resolution cover art fetcher
│   ├── discogs.py          # Discogs API client, subtrack unpacker & genre extractor
│   ├── lyrics.py           # Synced lyrics (.lrc) fetcher and manager
│   ├── models.py           # TrackMetadata and AlbumMetadata data structures
│   ├── musicbrainz.py      # MusicBrainz API integration
│   ├── processor.py        # Central processing coordinator
│   ├── renamer.py          # Track and directory renaming engine
│   ├── rym.py              # RateYourMusic parser and scraper
│   ├── scanner.py          # Folder crawler and multi-disc detector
│   ├── searcher.py         # Multi-database unified searcher
│   └── url_resolver.py     # URL parser for RYM, Discogs, and MusicBrainz
└── scratch/                # Unit tests and verification scripts
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
