"""Internationalization using gettext. Code/UI in English, catalogs in locales/."""
from __future__ import annotations

import gettext
import locale
import os
from pathlib import Path

# Default domain
DOMAIN = "pdf_to_video_ai"

# Global translation function
_translator = None


def _identity(s: str) -> str:
    return s


def _get_locales_dir() -> str:
    """Get locales directory path, works both in development and installed package."""
    try:
        from importlib import resources
        return str(resources.files("pdf_to_video_ai") / "locales")
    except Exception:
        # Fallback for development (editable install or running from source)
        return str(Path(__file__).parent / "locales")


def init_i18n(lang: str | None = None) -> None:
    """Initialize gettext with the given language."""
    global _translator

    if lang is None:
        # Try environment, then system locale
        lang = os.environ.get("PDF_TO_VIDEO_AI_LANG") or os.environ.get("LANG") or os.environ.get("LC_MESSAGES") or locale.getdefaultlocale()[0]

    if not lang:
        lang = "en"

    # Normalize: en_US.UTF-8 -> en
    lang_code = lang.split("_")[0].split(".")[0].lower()

    try:
        # Try to load compiled .mo file
        locales_dir = Path(_get_locales_dir())
        translation = gettext.translation(
            DOMAIN,
            localedir=str(locales_dir),
            languages=[lang_code],
            fallback=True
        )
        _translator = translation.gettext
    except Exception:
        # Fallback to identity
        _translator = _identity


def _(s: str) -> str:
    """Translate a string. Call init_i18n() first for actual translations."""
    if _translator is None:
        init_i18n()
    return _translator(s)


def get_available_languages() -> list[str]:
    """Return list of available language codes from locales directory."""
    locales_dir = Path(_get_locales_dir())
    if not locales_dir.exists():
        return ["en"]
    langs = []
    for item in locales_dir.iterdir():
        if item.is_dir() and (item / "LC_MESSAGES" / f"{DOMAIN}.mo").exists():
            langs.append(item.name)
    return ["en"] + sorted(langs)