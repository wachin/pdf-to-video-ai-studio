# ADR 0010: pydantic-settings for Typed Configuration

## Context
The project needs configuration management that:
- Validates types at load time
- Supports environment variable overrides
- Provides IDE autocomplete
- Documents all options with defaults
- Works with YAML config file

## Alternatives Considered
1. **Raw YAML + dict**: No validation, no autocomplete, error-prone
2. **dataclasses + manual validation**: Boilerplate, no env var support
3. **pydantic BaseSettings**: Deprecated in v2, replaced by pydantic-settings
4. **pydantic-settings**: Official successor, type validation, env vars, YAML via pyyaml

## Decision
Use **pydantic-settings >= 2.0** with **PyYAML >= 6.0** for configuration management.

Key usage:
- `BaseSettings` subclass with typed fields
- `model_config = SettingsConfigDict(env_prefix="PDF_TO_VIDEO_AI_", yaml_file="config.yaml")`
- Field types: `Literal`, `List`, `Optional`, nested models
- Environment variable override: `PDF_TO_VIDEO_AI_OCR__HABILITADO=true`
- Validation on load with clear error messages

## Consequences
**Positive:**
- Type-safe configuration with IDE support
- Automatic environment variable mapping
- YAML file support via PyYAML
- Clear validation errors on misconfiguration
- Self-documenting via type hints

**Negative:**
- Additional dependency (but lightweight)
- YAML loading requires custom config source (pydantic-settings doesn't natively support YAML)

**Mitigations:**
- Custom `YamlConfigSettingsSource` implemented in config.py
- Fallback to defaults if config.yaml missing

## Validation
- Tested with pydantic-settings 2.13.5 + PyYAML 6.0.3
- Config loads with type validation
- Env var overrides work
- Nested config sections validated

## References
- pydantic-settings documentation: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- PyYAML: https://pyyaml.org/