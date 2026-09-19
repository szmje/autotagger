# AutoTagger RYM 🎵

<p align="center">
  <b>Музыкальный теггер с упором на микрожанры RateYourMusic/Discogs, базу MusicBrainz, синхронизированные тексты (.lrc) и стандарты MusicBee.</b>
  <br />
  <i>Music tagger focused on RateYourMusic & Discogs subgenres, MusicBrainz metadata, synced lyrics (.lrc), and clean MusicBee library standards.</i>
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

**AutoTagger RYM** — утилита с GUI и CLI для нормального тегирования музыкальной библиотеки. Подтягивает официальные метаданные из **MusicBrainz** и **Discogs**, цепляет специфичные жанры с **RateYourMusic (RYM)**, качает тайминги караоке-текстов (`.lrc`), вшивает обложки в хайрезе, чистит мусор из тегов и правильно раскладывает мультидисковые релизы под стандарты **MusicBee** и **foobar2000**.

---

### Основные фичи

#### 1. Жанры с RYM и Discogs
- Парсит релиз с **RateYourMusic** и **Discogs**.
- Переключатель источника в GUI:
  - **RateYourMusic**: нишевые микрожанры (например, `cloud rap; drain; ambient pop`).
  - **Discogs**: стандартные стили и категории конкретного пресса.
  - **Объединить**: склеивает оба источника без дублей.
- Запись строго в **нижнем регистре (lowercase)** через точку с запятой и пробел:
  ```text
  alternative rock; post-punk; dream pop

```

* Возможность руками поправить жанры прямо в поле перед сохранением + кнопки обновления.

#### 2. Нормальный сплит артистов (`; `)

* Все совместные треки и релизы приводятся к единому стандарту через `; `:
```text
bladee; ecco2k
yung lean; bladee

```


* Автоматически разбивает коллаборации (`&`, `feat.`, `ft.`, `with`, `/`, `,`), чтобы плееры вроде **MusicBee**, **foobar2000**, **Navidrome** или **Plex** видели каждого исполнителя отдельно, а не создавали кашу.

#### 3. Поиск и вставка прямых ссылок

* Если релиз редкий или не определился автоматом, можно просто кинуть прямую ссылку:
* **RateYourMusic**: `https://rateyourmusic.com/release/album/...`
* **Discogs**: `https://www.discogs.com/release/...` или `/master/...`
* **MusicBrainz**: `https://musicbrainz.org/release/...`


* Хоткеи `Ctrl+V`, `Ctrl+C`, `Ctrl+X`, `Ctrl+A` работают на любой раскладке (RU/EN), плюс есть кнопка вставки и контекстное меню по ПКМ.
* Ручной поиск сразу по всем базам через диалоговое окно с выбором нужного издания.

#### 4. Выборочная запись тегов

* У каждого поля свой независимый чекбокс:
* `Исполнитель(и) альбома`
* `Название альбома`
* `Год релиза`
* `Жанры (Genre)`
* `Названия треков (Title)`
* `Номера треков (Track №)`
* `Обложка`
* `Тексты песен (LRC)`


* Снятые поля **вообще не перезаписываются**, существующие кастомные теги в файлах остаются нетронутыми.

#### 5. Честная поддержка Multi-Disc (MusicBee Standard)

* Подхватывает многодисковые издания (2 CD, 3 CD, винилы Side A/B/C/D) из баз или структуры папок (`CD1/`, `CD2/`, `Disc 1/` и т.д.).
* Логика тегов строго под MusicBee:
* В тег номера трека (`TRCK` / `tracknumber`) пишется **только номер трека** (`01`, `02`, `10`).
* Номер диска пишется **отдельно** (`TPOS` / `DISCNUMBER` = `01/02`, `02/02`). Никаких склеек в духе `101`, `102` в номер трека.


* Есть тумблер для переименования самих файлов в структуру вида `02-01. Artist - Title.mp3`.

#### 6. Переименование файлов и папок

* Пресеты масок:
* `01. Artist - Title` (например, `01. bladee - obedient.mp3`)
* `01. Title`
* `01 - Artist - Title`
* `01 - Title`
* `01-05. Artist - Title` (для мультидисков)
* `01-05. Title`
* `Artist - Title`


* Предпросмотр итоговых имен в реальном времени.
* Автоматическая зачистка запрещенных символов Windows (`/ \ : * ? " < > |`).
* Кнопка «📁 Папку» для быстрого переименования каталога в `Artist - Album (Year)`.

#### 7. Синхронизированные тексты (.lrc + караоке)

* Подтягивает построчные таймкоды через базу `syncedlyrics` (Musixmatch, Deezer, NetEase и др.).
* Создает файл `.lrc` рядом с треком (`01. bladee - obedient.lrc`) и параллельно вшивает текст внутрь файла (ID3 `USLT`, FLAC `LYRICS`, MP4 `©lyr`).
* Автоматически синхронизирует имя `.lrc` при переименовании аудиофайла.

#### 8. Обложки в высоком разрешении

* Качает оригинальные каверы до 1200x1200 (Deezer, Discogs, iTunes).
* Складывает `cover.jpg` в папку и вшивает в теги (APIC / Vorbis Picture / MP4 Cover).

#### 9. Вычистка мусора

* Сносит рекламные комментарии релизеров, спам трекеров, линки на Telegram-каналы и сайты из тегов (`COMM`, `WXXX`, `WCOM`, `TENC`, `COMMENT`, `DESCRIPTION`, `URL`, `©cmt`).

#### 10. Переключение RU / EN

* Кнопка смены языка вынесена на верхнюю панель. Переключает интерфейс и подсказки на лету без перезапуска.

#### 11. Поддерживаемые форматы

* **MP3** (`.mp3` — ID3v2.3 / ID3v2.4)
* **FLAC** (`.flac` — Vorbis Comments)
* **M4A / ALAC / AAC** (`.m4a`, `.mp4`)
* **OGG / OPUS** (`.ogg`, `.opus`)
* **WAV / AIFF** (`.wav`, `.aiff`)

---

### Установка и запуск

#### Клонирование и зависимости

Нужен **Python 3.9+**.

```bash
git clone [https://github.com/szmje/autotagger.git](https://github.com/szmje/autotagger.git)
cd autotagger
pip install -r requirements.txt

```

#### Запуск GUI

На Windows достаточно кликнуть:

```text
Run_GUI.bat

```

Либо через консоль:

```bash
python main.py

```

Как пользоваться:

1. Перетаскиваешь папку с альбомом или файлы напрямую в окно (или жмешь **📁 Выбрать папку...**).
2. Чекнул предпросмотр, выбрал источник жанров и нужные чекбоксы тегов.
3. Жмешь **▶️ ПРИМЕНИТЬ И ЗАПИСАТЬ ТЕГИ**.

---

## 🇬🇧 English

**AutoTagger RYM** is a clean GUI/CLI utility designed to tag music libraries properly. It fetches verified metadata from **MusicBrainz** and **Discogs**, scrapes niche subgenres from **RateYourMusic (RYM)**, pulls synchronized karaoke lyrics (`.lrc`), embeds high-res covers, cleans promotional junk tags, and handles multi-disc releases according to **MusicBee** and **foobar2000** standards.

---

### Key Features

#### 1. RateYourMusic & Discogs Genres

* Scrapes release data from both **RateYourMusic** and **Discogs**.
* Source selector:
* **RateYourMusic**: specific niche subgenres (e.g., `cloud rap; drain; ambient pop`).
* **Discogs**: official master/release style classifications.
* **Merge Both**: merges tags from both platforms without duplicates.


* All genres are strictly normalized to **lowercase** and separated by `; `:
```text
alternative rock; post-punk; dream pop

```


* Editable tag box prior to writing, plus quick refresh buttons.

#### 2. Clean Multi-Artist Splitting (`; `)

* Joint tracks and features are formatted strictly using `; `:
```text
bladee; ecco2k
yung lean; bladee

```


* Normalizes all conjunction variants (`&`, `feat.`, `ft.`, `with`, `/`, `,`) so players like **MusicBee**, **foobar2000**, **Navidrome**, and **Plex** properly index each artist separately.

#### 3. Direct URL Resolving & Fast Search

* Paste URLs directly when dealing with obscure editions:
* **RateYourMusic**: `https://rateyourmusic.com/release/album/...`
* **Discogs**: `https://www.discogs.com/release/...` or `/master/...`
* **MusicBrainz**: `https://musicbrainz.org/release/...`


* Shortcuts (`Ctrl+V`, `Ctrl+C`, `Ctrl+X`, `Ctrl+A`) work regardless of active keyboard layout.
* Cross-database search window to quickly look up releases without opening a browser.

#### 4. Selective Tagging

* Independent toggles for each metadata category:
* `Album Artist(s)`
* `Album Title`
* `Year`
* `Genres`
* `Track Titles`
* `Track Numbers`
* `Cover Art`
* `Lyrics (LRC)`


* Unchecked fields are **ignored completely**, leaving your existing tags untouched.

#### 5. Proper Multi-Disc Handling (MusicBee Compliant)

* Auto-detects multi-disc releases (2 CD, 3 CD, vinyl Sides A/B/C/D) via metadata or folder layouts (`CD1/`, `CD2/`, `Disc 1/`, etc.).
* Follows the clean MusicBee tagging standard:
* `TRCK` / `tracknumber` stores **only the sequential track index** (`01`, `02`, `10`).
* Disc number goes strictly into `TPOS` / `DISCNUMBER` (`01/02`, `02/02`).


* Optional file renaming mask: `02-01. Artist - Title.mp3`.

#### 6. File & Folder Renamer

* Preset templates:
* `01. Artist - Title` (e.g., `01. bladee - obedient.mp3`)
* `01. Title`
* `01 - Artist - Title`
* `01 - Title`
* `01-05. Artist - Title` (multi-disc)
* `01-05. Title`
* `Artist - Title`


* Real-time filename preview column.
* Automatically strips invalid OS characters (`/ \ : * ? " < > |`).
* Single-click folder renaming to `Artist - Album (Year)`.

#### 7. Synced Lyrics (.lrc)

* Fetches timestamped lyrics via `syncedlyrics` (Musixmatch, Deezer, NetEase, etc.).
* Saves external `.lrc` files next to audio files and embeds synchronized lyrics tags (ID3 `USLT`, FLAC `LYRICS`, MP4 `©lyr`).
* Automatically syncs `.lrc` file names during track renaming.

#### 8. High-Res Artwork

* Downloads official artwork up to 1200x1200px (Deezer, Discogs, iTunes).
* Saves `cover.jpg` in the album directory and embeds it directly into audio files.

#### 9. Tag Cleaner

* Cleans spam comments, torrent tracker URLs, Telegram promotion tags, and encoder notes (`COMM`, `WXXX`, `WCOM`, `TENC`, `COMMENT`, `DESCRIPTION`, `URL`, `©cmt`).

#### 10. Instant RU / EN Toggle

* Real-time language switch directly from the top toolbar without app restarts.

#### 11. Audio Formats

* **MP3** (`.mp3` — ID3v2.3 / ID3v2.4)
* **FLAC** (`.flac` — Vorbis Comments)
* **M4A / ALAC / AAC** (`.m4a`, `.mp4`)
* **OGG / OPUS** (`.ogg`, `.opus`)
* **WAV / AIFF** (`.wav`, `.aiff`)

---

### Installation & Usage

#### Setup

Requires **Python 3.9+**.

```bash
git clone [https://github.com/szmje/autotagger.git](https://github.com/szmje/autotagger.git)
cd autotagger
pip install -r requirements.txt

```

#### Running GUI

On Windows:

```text
Run_GUI.bat

```

Or via terminal:

```bash
python main.py

```

1. Drag and drop your album folder or audio files into the window (or click **📁 Choose Folder...**).
2. Review metadata preview, pick the genre source, and select tags to write.
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

```
