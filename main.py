import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def run_cli_tagger(
    paths: list,
    auto_confirm: bool = False,
    lowercase_artists: bool = False,
    override_url: Optional[str] = None,
    rename_files: bool = False,
    rename_folders: bool = False,
    fetch_lyrics: bool = False,
    save_lrc: bool = True,
    clean_junk_tags: bool = True,
    naming_pattern: str = "01. Artist - Title",
    multi_disc_format: bool = True
):
    from tagger.processor import AutoTaggerProcessor

    console.print(Panel.fit(
        "[bold cyan]AutoTagger RYM[/bold cyan] — Автоматический музыкальный теггер\n"
        "[dim]RateYourMusic жанры (lowercase) + Discogs + Мульти-диски (01-05) + Мульти-артисты (;) + Обложки + LRC[/dim]",
        border_style="cyan"
    ))

    def on_log(msg: str):
        console.print(f"[dim]>[/dim] {msg}")

    def on_progress(cur: int, tot: int, msg: str):
        console.print(f"[[bold green]{cur}/{tot}[/bold green]] {msg}")

    processor = AutoTaggerProcessor(
        lowercase_genres=True,
        lowercase_artists=lowercase_artists,
        save_cover_art=True,
        embed_cover_art=True,
        rename_files=rename_files,
        rename_folders=rename_folders,
        fetch_lyrics=fetch_lyrics,
        save_lrc_file=save_lrc,
        clean_junk_tags=clean_junk_tags,
        naming_pattern=naming_pattern,
        multi_disc_format=multi_disc_format,
        on_log=on_log,
        on_progress=on_progress
    )

    if override_url:
        console.print(f"[bold cyan]🔗 Использование прямой ссылки:[/bold cyan] {override_url}")
    if rename_files:
        console.print(f"[bold cyan]✏️ Авто-переименование файлов включено:[/bold cyan] Шаблон: '{naming_pattern}'")
    if rename_folders:
        console.print(f"[bold cyan]📁 Авто-переименование папок включено:[/bold cyan] Исполнитель - Альбом (Год)")
    if fetch_lyrics:
        console.print(f"[bold cyan]🎤 Поиск и сохранение текстов песен (LRC):[/bold cyan] Включено")

    # 1. Preview
    console.print("\n[bold yellow]🔍 Сканирование папок и поиск метаданных...[/bold yellow]")
    groups = processor.scanner.scan_paths(paths)

    if not groups:
        console.print("[bold red]❌ В переданных папках не найдено аудиофайлов![/bold red]")
        return

    table = Table(title="Альбомы в очереди на обработку", header_style="bold magenta")
    table.add_column("Папка", style="cyan")
    table.add_column("Треков", justify="right", style="green")

    for folder, files in groups.items():
        table.add_row(folder.name, str(len(files)))

    console.print(table)

    if not auto_confirm:
        try:
            answer = input("\nНачать тегирование всех найденных альбомов? [Y/n]: ").strip().lower()
            if answer and answer not in ["y", "yes", "д", "да"]:
                console.print("[yellow]Отменено пользователем.[/yellow]")
                return
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Отменено.[/yellow]")
            return

    console.print("\n[bold green]🚀 Запуск тегирования...[/bold green]")
    count = processor.process_paths(paths, override_url=override_url)
    console.print(f"\n[bold green]✅ Завершено! Успешно обработано {count} файлов.[/bold green]")


def main():
    parser = argparse.ArgumentParser(description="Музыкальный автотеггер с RateYourMusic, Discogs и мульти-артистами")
    parser.add_argument("paths", nargs="*", help="Пути к папкам или файлам с аудио")
    parser.add_argument("--gui", action="store_true", help="Принудительно запустить в режиме графического интерфейса (GUI)")
    parser.add_argument("--url", type=str, help="Прямая ссылка на релиз (RateYourMusic, Discogs или MusicBrainz)")
    parser.add_argument("-r", "--rename", action="store_true", help="Переименовать файлы по выбранному шаблону")
    parser.add_argument("--pattern", type=str, default="01. Artist - Title", help="Шаблон имени файла (напр. '01. Artist - Title', '01. Title')")
    parser.add_argument("--rename-folder", action="store_true", help="Переименовать папку альбома по форме 'Исполнитель - Альбом (Год)'")
    parser.add_argument("-y", "--yes", action="store_true", help="Автоматически подтверждать запись без вопроса")
    parser.add_argument("--lower-artists", action="store_true", help="Переводить имена артистов в нижний регистр")
    parser.add_argument("--lyrics", action="store_true", help="Искать и сохранять тексты песен (.lrc и тег)")
    parser.add_argument("--no-lrc", action="store_true", help="Не создавать отдельный файл .lrc (только вшить в теги)")
    parser.add_argument("--no-clean", action="store_true", help="Не очищать мусорные теги (реклама, комменты)")
    parser.add_argument("--no-multi-disc-format", action="store_true", help="Не форматировать треки multi-disc релизов в виде 01-05")

    args = parser.parse_args()

    # If no paths provided or --gui flag passed, launch GUI
    if args.gui or not args.paths:
        from gui import run_gui
        run_gui(initial_paths=args.paths if args.paths else None)
    else:
        # CLI batch processing
        run_cli_tagger(
            args.paths,
            auto_confirm=args.yes,
            lowercase_artists=args.lower_artists,
            override_url=args.url,
            rename_files=args.rename,
            rename_folders=args.rename_folder,
            fetch_lyrics=args.lyrics,
            save_lrc=not args.no_lrc,
            clean_junk_tags=not args.no_clean,
            naming_pattern=args.pattern,
            multi_disc_format=not args.no_multi_disc_format
        )


if __name__ == "__main__":
    main()
