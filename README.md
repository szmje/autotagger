# autotagger

музыкальный теггер с упором на микрожанры rateyourmusic и discogs, официальную базу musicbrainz, синхронизированные тексты (.lrc) и стандарты библиотек musicbee и foobar2000.

собирается в один .exe через pyinstaller, работает автономно без установленного python.

[english](#autotagger-english)

---

## что умеет

- жанры с rateyourmusic и discogs: микрожанры (напр. `cloud rap; drain; ambient pop`), стили конкретного издания или склейка обоих источников без дублей. запись строго в нижнем регистре через точку с запятой.
- сплит артистов: совместные треки приводятся к виду `bladee; ecco2k`, автоматически разбивает `feat.`, `ft.`, `with`, `&`, чтобы musicbee, plex, navidrome и foobar2000 индексировали каждого исполнителя отдельно.
- поиск по базам и прямые ссылки: автопоиск по всем каталогам либо вставка прямых ссылок на rym, discogs или musicbrainz.
- выборочная запись тегов: независимые чекбоксы на каждое поле (артист, альбом, год, жанр, название, номер трека, обложка, тексты песен). снятые поля не перезаписываются и сохраняют исходные данные в файле.
- multi-disc по стандарту musicbee: правильная нумерация треков (`01`, `02`) и отдельный тег диска (`01/02`), без склейки в `101`, `102`.
- переименование файлов и папок: готовые шаблоны имен, предпросмотр в реальном времени, очистка запрещенных символов windows, кнопка переименования папки в `artist - album (year)`.
- синхронизированные тексты: построчные таймкоды через syncedlyrics, сохранение в .lrc рядом с файлом и вшивание в теги (uslt / lyrics).
- обложки в высоком разрешении: загрузка оригиналов до 1200x1200 и вшивание в теги.
- очистка мусора: удаление рекламы, спама, ссылок на каналы и лишних комментариев релизеров.
- переключение ru / en на лету.
- сохранение конфигурации: выбранные чекбоксы, шаблон переименования и язык сохраняются в `config.json`.
- форматы: mp3, flac, m4a, ogg, opus, wav, aiff.

---

## готовый бинарник

готовый `autotagger.exe` лежит в [релизах](../../releases/latest).

запуск gui:
дважды кликнуть по `autotagger.exe`.

запуск через консоль:
```powershell
.\autotagger.exe "d:\music\album"
```

---

## аргументы cli

```text
использование: autotagger.exe [пути ...] [параметры]

опции:
  -h, --help            справка
  --gui                 принудительный запуск интерфейса
  --url url             прямая ссылка на релиз (rym / discogs / musicbrainz)
  -r, --rename          переименовать файлы по шаблону
  --pattern pattern     шаблон имени (по дефолту "01. artist - title")
  --rename-folder       переименовать папку в "artist - album (year)"
  -y, --yes             автоматически подтверждать запись
  --lower-artists       переводить имена артистов в нижний регистр
  --lyrics              искать и сохранять тексты песен (.lrc и тег)
  --no-lrc              не создавать отдельный файл .lrc
  --no-clean            не очищать мусорные теги
  --no-multi-disc-format не форматировать мультидиски как 01-05
```

---

## запуск из исходников

нужен python 3.10+.

установка зависимостей:
```bash
pip install -r requirements.txt
```

запуск gui:
```bash
python main.py
```
(или через `run_gui.bat`)

сборка в exe:
```bash
pyinstaller --clean autotagger.spec
```
бинарник появится в `dist/autotagger.exe`.

---

# autotagger (english)

music tagger focused on rateyourmusic and discogs subgenres, musicbrainz metadata, synced lyrics (.lrc), and clean musicbee and foobar2000 library standards.

standalone windows .exe available, runs without python installed.

[на русском](#autotagger)

---

## features

- rym & discogs genres: niche subgenres (e.g. `cloud rap; drain; ambient pop`), release styles, or merged without duplicates. formatted strictly in lowercase separated by semicolons.
- multi-artist splitting: collaborative tracks normalized to `bladee; ecco2k`, automatically splits `feat.`, `ft.`, `with`, `&` so musicbee, foobar2000, plex, and navidrome index each artist individually.
- search & direct url: auto-search across databases or direct link input for rym, discogs, and musicbrainz.
- selective tagging: independent checkboxes for each field (artist, album, year, genre, title, track number, artwork, lyrics). unchecked tags are left untouched.
- proper multi-disc support (musicbee standard): clean track numbers (`01`, `02`) and separate disc tag (`01/02`), no glued `101`, `102` track numbers.
- renaming: filename presets, real-time preview, automatic windows forbidden character cleanup, quick folder rename to `artist - album (year)`.
- synced lyrics: timestamped lyrics via syncedlyrics, saved as .lrc files and embedded into audio tags (uslt / lyrics).
- high-resolution artwork: downloads covers up to 1200x1200 and embeds them into audio files.
- tag cleaner: removes junk tags, promo links, and release comments.
- ru / en language switch on the fly.
- persistent config: stores chosen checkboxes, patterns, and language in `config.json`.
- supported formats: mp3, flac, m4a, ogg, opus, wav, aiff.

---

## standalone binary

prebuilt `autotagger.exe` is available in [releases](../../releases/latest).

running gui:
double-click `autotagger.exe`.

running via cli:
```powershell
.\autotagger.exe "d:\music\album"
```

---

## cli arguments

```text
usage: autotagger.exe [paths ...] [options]

options:
  -h, --help            show help message
  --gui                 force gui launch
  --url url             direct release url (rym / discogs / musicbrainz)
  -r, --rename          rename files according to pattern
  --pattern pattern     naming pattern (default "01. artist - title")
  --rename-folder       rename album folder to "artist - album (year)"
  -y, --yes             auto-confirm tagging without prompt
  --lower-artists       lowercase artist names
  --lyrics              fetch and embed lyrics (.lrc file and tag)
  --no-lrc              do not create standalone .lrc file
  --no-clean            do not clean junk tags
  --no-multi-disc-format do not format multi-disc tracks as 01-05
```

---

## running from source

requires python 3.10+.

install dependencies:
```bash
pip install -r requirements.txt
```

run gui:
```bash
python main.py
```
(or click `run_gui.bat`)

build exe:
```bash
pyinstaller --clean autotagger.spec
```
binary will appear in `dist/autotagger.exe`.
