# ADR 0011: Babel/gettext for Internationalization

## Context
The project needs internationalization for:
- CLI messages (Spanish/English)
- Separation of UI language from narration language
- Portable locale files (.mo) for distribution
- Standard tooling for translation workflow

## Alternatives Considered
1. **Custom i18n dict**: Simple but not scalable, no plural forms, no tooling
2. **gettext (stdlib)**: Standard but requires .mo compilation, locale dir management
3. **Babel + gettext**: Babel provides message extraction, compilation, locale management; gettext provides runtime

## Decision
Use **Babel >= 2.0** with **gettext (stdlib)** for internationalization.

Key usage:
- `babel.cfg` for message extraction patterns
- `pybabel extract -F babel.cfg -o locale/messages.pot src/`
- `pybabel init -i locale/messages.pot -d locale -l es` for Spanish catalog
- `pybabel compile -d locale` to generate .mo files
- `gettext.translation("messages", localedir="locale", languages=[lang])` at runtime
- `_()` function for marking translatable strings
- Separate `PDF_TO_VIDEO_AI_LANG` / `--lang` for UI vs `config.idioma` for narration

## Consequences
**Positive:**
- Industry standard i18n workflow
- Portable .mo files (no .po at runtime)
- Plural forms support
- Context support (pgettext)
- Babel handles extraction/compilation
- Clear separation: UI language ≠ narration language

**Negative:**
- Build step for .mo compilation
- Requires gettext tools on build machine (pybabel)

**Mitigations:**
- .mo files committed to repo for zero-build deployment
- pybabel only needed for adding new languages

## Validation
- Tested with Babel 2.13.0
- Spanish catalog (es/LC_MESSAGES/messages.mo) working
- CLI `--lang es|en` switches UI language
- Narration language independent (config.yaml)

## References
- Babel documentation: https://babel.pocoo.org/
- gettext documentation: https://docs.python.org/3/library/gettext.html
- babel.cfg in project root