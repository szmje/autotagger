### AutoTagger

<p align="center">
  <b>Музыкальный теггер с упором на микрожанры RateYourMusic/Discogs, базу MusicBrainz, синхронизированные тексты (.lrc) и стандарты MusicBee.</b>
  <br />
  <i>Music tagger focused on RateYourMusic & Discogs subgenres, MusicBrainz metadata, synced lyrics (.lrc), and clean MusicBee library standards.</i>
</p>
---
<p align="center">
  <b><a href="#-русский">🇷🇺 Читать на русском</a></b> --- <b><a href="#-english">🇬🇧 Read in English</a></b>
</p>
---
## 🇷🇺 Русский
**AutoTagger RYM** — утилита с GUI для нормального тегирования музыкальной библиотеки. Подтягивает официальные метаданные из **MusicBrainz** и **Discogs**, цепляет специфичные жанры с **RateYourMusic (RYM)**, качает тайминги караоке-текстов (`.lrc`), вшивает обложки в хайрезе, чистит мусор из тегов и правильно раскладывает мультидисковые релизы под стандарты **MusicBee** и **foobar2000**.
#### Основной функционал
##### 1. Жанры с RYM и Discogs
-- Парсит релиз с **RateYourMusic** и **Discogs**.
	-- Переключатель источника в GUI:
	-- **RateYourMusic**: нишевые микрожанры (например, `cloud rap; drain; ambient pop`).
	-- **Discogs**: стандартные стили и категории конкретного пресса.
	-- **Объединить**: склеивает оба источника без дублей.
	-- Запись строго в **нижнем регистре (lowercase)** через точку с запятой и пробел:
```
  alternative rock; post-punk; dream pop
```
* Возможность руками поправить жанры прямо в поле перед сохранением + кнопки обновления.
#### 2. Нормальный сплит артистов (`;`)
-- Все совместные треки и релизы приводятся к единому стандарту через `; `:
```
bladee; ecco2k
yung lean; bladee
```
-- Автоматически разбивает коллаборации (`&`, `feat.`, `ft.`, `with`, `/`, `,`), чтобы плееры вроде **MusicBee**, **foobar2000**, **Navidrome** или **Plex** видели каждого исполнителя отдельно, а не создавали кашу.
#### 3. Поиск и вставка прямых ссылок
-- Если релиз редкий или не определился автоматом, можно просто кинуть прямую ссылку:
	-- **RateYourMusic**: `https://rateyourmusic.com/release/album/...`
	-- **Discogs**: `https://www.discogs.com/release/...` или `/master/...`
	-- **MusicBrainz**: `https://musicbrainz.org/release/...`
	-- Ручной поиск сразу по всем базам через диалоговое окно с выбором нужного издания.
#### 4. Выборочная запись тегов
-- У каждого поля свой независимый чекбокс:
	-- `Исполнитель(и) альбома`
	-- `Название альбома`
	-- `Год релиза`
	-- `Жанры (Genre)`
	-- `Названия треков (Title)`
	-- `Номера треков (Track №)`
	-- `Обложка`
	-- `Тексты песен (LRC)`
-- Снятые поля **вообще не перезаписываются**, существующие кастомные теги в файлах остаются нетронутыми.
#### 5. Честная поддержка Multi-Disc (MusicBee Standard)
-- Подхватывает многодисковые издания (2 CD, 3 CD, винилы Side A/B/C/D) из баз или структуры папок (`CD1/`, `CD2/`, `Disc 1/` и т.д.).
-- Логика тегов строго под MusicBee:
-- В тег номера трека (`TRCK` / `tracknumber`) пишется **только номер трека** (`01`, `02`, `10`).
-- Номер диска пишется **отдельно** (`TPOS` / `DISCNUMBER` = `01/02`, `02/02`). Никаких склеек в духе `101`, `102` в номер трека.
	-- Есть тумблер для переименования самих файлов в структуру вида `02-01. Artist - Title.mp3`.
#### 6. Переименование файлов и папок
-- Пресеты масок:
 `01. Artist - Title` (например, `01. bladee - obedient.mp3`)
 `01. Title`
 `01 - Artist - Title`
 `01 - Title`
 `01-05. Artist - Title` (для мультидисков)
 `01-05. Title`
 `Artist - Title`
-- Предпросмотр итоговых имен в реальном времени.
-- Автоматическая зачистка запрещенных символов Windows (`/ \ : * ? " < > |`).
	-- Кнопка «📁 Папку» для быстрого переименования каталога в `Artist - Album (Year)`.
#### 7. Синхронизированные тексты (.lrc + караоке)
-- Подтягивает построчные таймкоды через базу `syncedlyrics` (Musixmatch, Deezer, NetEase и др.).
-- Создает файл `.lrc` рядом с треком (`01. bladee - obedient.lrc`) и параллельно вшивает текст внутрь файла (ID3 `USLT`, FLAC `LYRICS`, MP4 `©lyr`).
-- Автоматически синхронизирует имя `.lrc` при переименовании аудиофайла.
#### 8. Обложки в высоком разрешении
-- Качает оригинальные каверы до 1200x1200 (Deezer, Discogs, iTunes).
-- Складывает `cover.jpg` в папку и вшивает в теги (APIC / Vorbis Picture / MP4 Cover).
#### 9. Вычистка мусора
-- Сносит рекламные комментарии релизеров, спам трекеров, линки на Telegram-каналы и сайты из тегов (`COMM`, `WXXX`, `WCOM`, `TENC`, `COMMENT`, `DESCRIPTION`, `URL`, `©cmt`).
#### 10. Переключение RU / EN
-- Кнопка смены языка вынесена на верхнюю панель. Переключает интерфейс и подсказки на лету без перезапуска.
#### 11. Поддерживаемые форматы
	-- **MP3** (`.mp3` — ID3v2.3 / ID3v2.4)
	-- **FLAC** (`.flac` — Vorbis Comments)
	-- **M4A / ALAC / AAC** (`.m4a`, `.mp4`)
	-- **OGG / OPUS** (`.ogg`, `.opus`)
	-- **WAV / AIFF** (`.wav`, `.aiff`)
---
### Установка и запуск
#### Клонирование и зависимости
Нужен **Python 3.9+**.
```bash
git clone https://github.com/szmje/autotagger.git
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
1. Перетаскиваешь папку с альбомом или файлы напрямую в окно (или жмешь **Выбрать папку...**).
2. Чекнул предпросмотр, выбрал источник жанров и нужные чекбоксы тегов.
3. Жмешь  **ПРИМЕНИТЬ И ЗАПИСАТЬ ТЕГИ**.

---
## 🇬🇧 English
**AutoTagger RYM** — GUI utility designed to tag music libraries properly. Fetches verified metadata from **MusicBrainz** and **Discogs**, scrapes niche subgenres from **RateYourMusic (RYM)**, pulls karaoke-timed lyrics (`.lrc`), embeds high-res covers, cleans promotional junk tags, and handles multi-disc releases according to **MusicBee** and **foobar2000** standards.
#### Main Features
##### 1. RateYourMusic & Discogs Genres
-- Scrapes release info from **RateYourMusic** and **Discogs**.
	-- Source switcher in GUI:
	-- **RateYourMusic**: niche subgenres (e.g. `cloud rap; drain; ambient pop`).
	-- **Discogs**: standard styles and categories of a specific pressing.
	-- **Merge**: combines both sources without duplicates.
	-- Strictly formatted in **lowercase** separated by semicolon and space:
```
  alternative rock; post-punk; dream pop
```
* Ability to manually edit genres directly in the field before saving + refresh buttons.
#### 2. Clean Multi-Artist Splitting (`;`)
-- All collaborative tracks and releases are normalized to a single standard using `; `:
```
bladee; ecco2k
yung lean; bladee
```
-- Automatically splits collaborations (`&`, `feat.`, `ft.`, `with`, `/`, `,`) so players like **MusicBee**, **foobar2000**, **Navidrome**, or **Plex** properly index each artist individually instead of cluttering the library.
#### 3. Search & Direct URL Resolving
-- If a release is rare or not detected automatically, simply paste a direct link:
	-- **RateYourMusic**: `https://rateyourmusic.com/release/album/...`
	-- **Discogs**: `https://www.discogs.com/release/...` or `/master/...`
	-- **MusicBrainz**: `https://musicbrainz.org/release/...`
	-- Manual search across all databases via dialog window to select the exact edition.
#### 4. Selective Tagging
-- Independent checkboxes for each metadata field:
	-- `Album Artist(s)`
	-- `Album Title`
	-- `Year`
	-- `Genres (Genre)`
	-- `Track Titles (Title)`
	-- `Track Numbers (Track №)`
	-- `Cover Art`
	-- `Lyrics (LRC)`
-- Unchecked fields are **not overwritten at all**, preserving existing custom tags in your audio files.
#### 5. Proper Multi-Disc Support (MusicBee Standard)
-- Automatically detects multi-disc releases (2 CD, 3 CD, vinyl Sides A/B/C/D) from databases or folder structure (`CD1/`, `CD2/`, `Disc 1/`, etc.).
-- Tagging logic strictly follows MusicBee standards:
-- Track number tag (`TRCK` / `tracknumber`) receives **only the track number** (`01`, `02`, `10`).
-- Disc number is written **separately** (`TPOS` / `DISCNUMBER` = `01/02`, `02/02`). No glued indices like `101`, `102` in track number.
	-- Toggle to rename files into multi-disc pattern `02-01. Artist - Title.mp3`.
#### 6. File & Folder Renaming
-- Renaming presets:
 `01. Artist - Title` (e.g. `01. bladee - obedient.mp3`)
 `01. Title`
 `01 - Artist - Title`
 `01 - Title`
 `01-05. Artist - Title` (for multi-disc)
 `01-05. Title`
 `Artist - Title`
-- Real-time preview of target filenames.
-- Automatic sanitization of forbidden Windows characters (`/ \ : * ? " < > |`).
	-- «📁 Folder» button to quickly rename directory to `Artist - Album (Year)`.
#### 7. Synced Lyrics (.lrc + Karaoke)
-- Fetches line-by-line timestamps via `syncedlyrics` (Musixmatch, Deezer, NetEase, etc.).
-- Creates an external `.lrc` file alongside the audio file (`01. bladee - obedient.lrc`) and embeds lyrics into tags (ID3 `USLT`, FLAC `LYRICS`, MP4 `©lyr`).
-- Automatically syncs `.lrc` filenames when renaming audio tracks.
#### 8. High-Resolution Artwork
-- Downloads original artwork up to 1200x1200px (Deezer, Discogs, iTunes).
-- Saves `cover.jpg` in the album directory and embeds it directly into audio files (APIC / Vorbis Picture / MP4 Cover).
#### 9. Tag Cleaner
-- Strips promotional release notes, torrent tracker ads, links to Telegram channels and websites (`COMM`, `WXXX`, `WCOM`, `TENC`, `COMMENT`, `DESCRIPTION`, `URL`, `©cmt`).
#### 10. RU / EN Language Switch
-- Language switcher button located right in the top toolbar. Updates interface labels and tooltips on the fly without restarting.
#### 11. Supported Audio Formats
	-- **MP3** (`.mp3` — ID3v2.3 / ID3v2.4)
	-- **FLAC** (`.flac` — Vorbis Comments)
	-- **M4A / ALAC / AAC** (`.m4a`, `.mp4`)
	-- **OGG / OPUS** (`.ogg`, `.opus`)
	-- **WAV / AIFF** (`.wav`, `.aiff`)
---
### Installation & Usage
#### Setup & Dependencies
Requires **Python 3.9+**.
```bash
git clone https://github.com/szmje/autotagger.git
cd autotagger
pip install -r requirements.txt
```
#### Running GUI
On Windows simply double-click:
```text
Run_GUI.bat
```

Or via terminal:
```bash
python main.py
```

How to use:
1. Drag and drop your album folder or audio files into the window (or click **Choose Folder...**).
2. Check the preview, select genre source and desired tag checkboxes.
3. Click  **APPLY AND WRITE TAGS**.
