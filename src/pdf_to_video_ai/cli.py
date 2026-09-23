from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path

from .config import load_config
from .i18n import _, init_i18n


def cmd_generate(args: argparse.Namespace) -> None:
    carpeta = Path(args.carpeta)
    salida = Path(args.salida)
    cfg = load_config(Path(args.config) if args.config else None)
    from .pipeline import process_folder
    out = process_folder(carpeta, salida, cfg)
    print(_("Pipeline completed for {name}").format(name=carpeta.name))
    print(_("Output dir: {path}").format(path=salida))
    print(_("Markdown: {path}").format(path=out))


def cmd_lote(args: argparse.Namespace) -> None:
    raiz = Path(args.raiz)
    salida = Path(args.salida)
    cfg = load_config(Path(args.config) if args.config else None)

    # Find scholarship folders (directories with PDF/DOCX/HTML files)
    exts = {".pdf", ".docx", ".doc", ".html", ".htm", ".txt"}
    folders = []
    for item in sorted(raiz.iterdir()):
        if item.is_dir():
            # Check if it contains supported files
            has_content = any(f.is_file() and f.suffix.lower() in exts
                             for f in item.rglob("*"))
            if has_content:
                folders.append(item)

    if not folders:
        print(_("No scholarship folders found in {path}").format(path=raiz))
        return

    print(_("Found {count} scholarship folders").format(count=len(folders)))
    for i, folder in enumerate(folders, 1):
        out_dir = salida / folder.name
        print(_("[{current}/{total}] Processing: {name}").format(current=i, total=len(folders), name=folder.name))
        try:
            from .pipeline import process_folder
            process_folder(folder, out_dir, cfg)
            print(_("  Done: {path}").format(path=out_dir))
        except Exception as e:
            print(_("  ERROR: {error}").format(error=e))


def cmd_validar(args: argparse.Namespace) -> None:
    carpeta = Path(args.carpeta)
    cfg = load_config(Path(args.config) if args.config else None)
    from .validation import validate_document, validate_script, validate_script_facts, write_validation_report

    salida = Path(args.salida) if hasattr(args, 'salida') and args.salida else carpeta.parent / "salidas" / carpeta.name
    doc_json = salida / "document.json"
    script_json = salida / "script.json"

    if not doc_json.exists():
        print(_("Document JSON not found at {path}").format(path=doc_json))
        return

    doc_issues = validate_document(doc_json)
    script_issues = validate_script(script_json) if script_json.exists() else []
    fact_issues = validate_script_facts(script_json, doc_json) if script_json.exists() else []
    all_issues = doc_issues + script_issues + fact_issues
    write_validation_report(all_issues, salida / "validation_report")
    print(_("Validation completed: {count} issues").format(count=len(all_issues)))
    for issue in all_issues:
        print(_("  [{level}] {code}: {message}").format(level=issue.level.upper(), code=issue.code, message=issue.message))


def cmd_version(_args: argparse.Namespace) -> None:
    from . import __version__
    print(__version__)


def main() -> None:
    # First pass: parse --lang before full initialization
    import os
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--lang", help=argparse.SUPPRESS)
    pre_parser.add_argument("-h", "--help", action="store_true", dest="show_help")
    pre_args, _unused = pre_parser.parse_known_args()

    # Initialize i18n with --lang override or environment
    target_lang = pre_args.lang or os.environ.get("PDF_TO_VIDEO_AI_LANG") or os.environ.get("LANG")
    init_i18n(target_lang)

    # Now create the real parser with translated strings
    parser = argparse.ArgumentParser(prog="pdf-to-video-ai", description=_("Generate narrated videos for scholarships"), add_help=False)
    parser.add_argument("--config", help=_("Path to config.yaml"))
    parser.add_argument("--lang", help=_("Force language (e.g., en, es)"))
    parser.add_argument("-h", "--help", action="help", help=_("Show this help message and exit"))
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generar", help=_("Generate video for a folder"))
    gen.add_argument("carpeta", help=_("Path to scholarship folder"))
    gen.add_argument("--salida", default="salidas", help=_("Output directory"))
    gen.set_defaults(func=cmd_generate)

    lote = sub.add_parser("lote", help=_("Batch generate for all scholarships"))
    lote.add_argument("raiz", help=_("Root folder with scholarship folders"))
    lote.add_argument("--salida", default="salidas", help=_("Output directory"))
    lote.set_defaults(func=cmd_lote)

    val = sub.add_parser("validar", help=_("Validate content"))
    val.add_argument("carpeta", help=_("Path to scholarship folder"))
    val.add_argument("--salida", help=_("Output directory (optional)"))
    val.set_defaults(func=cmd_validar)

    ver = sub.add_parser("version", help=_("Show version"))
    ver.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()