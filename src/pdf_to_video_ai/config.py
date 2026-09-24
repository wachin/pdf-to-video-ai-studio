from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class VozConfig:
    name: str = "es-ES-ElviraNeural"
    rate: str = "+0%"
    volume: str = "+0dB"


class SubtitulosConfig:
    enabled: bool = True
    burn_in: bool = False
    estilo: str = "default"


class OcrConfig:
    habilitado: bool = False
    dpi: int = 300
    idioma: str = "es"


class SalidaConfig:
    codec_video: str = "libx264"
    codec_audio: str = "aac"
    bitrate_audio: str = "192k"
    pix_fmt: str = "yuv420p"


class LogsConfig:
    nivel: str = "INFO"
    formato: str = "json"


class LlmConfig:
    enabled: bool = False
    provider: str = "ollama"
    model: str = "phi3:mini"
    base_url: str = "http://localhost:11434"
    max_tokens: int = 500
    temperature: float = 0.2


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PDF2VIDEO_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    voz: VozConfig = Field(default_factory=lambda: VozConfig())
    idioma: str = "es"
    plantilla: str = "src/templates/default"
    duracion_maxima_seg: int = Field(default=45, ge=10, le=300)
    palabras_por_segundo: float = Field(default=2.8, gt=0.5, le=10.0)
    subtitulos: SubtitulosConfig = Field(default_factory=lambda: SubtitulosConfig())
    orientaciones: list[str] = Field(default_factory=lambda: ["vertical"])
    musica_fondo: str | None = None
    musica_volumen: str = "-20dB"
    ocr: OcrConfig = Field(default_factory=lambda: OcrConfig())
    salida: SalidaConfig = Field(default_factory=lambda: SalidaConfig())
    logs: LogsConfig = Field(default_factory=lambda: LogsConfig())
    llm: LlmConfig = Field(default_factory=lambda: LlmConfig())

    @field_validator("orientaciones", mode="before")
    @classmethod
    def _validate_orientaciones(cls, v):
        if isinstance(v, str):
            return [v.strip() for v in v.split(",")]
        return v

    @field_validator("orientaciones")
    @classmethod
    def _check_orientaciones(cls, v):
        valid = {"vertical", "horizontal"}
        for o in v:
            if o not in valid:
                raise ValueError(f"Invalid orientation: {o}. Valid: {valid}")
        return v

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        # Custom source order: init > env > yaml
        yaml_path = Path(__file__).parent.parent / "config.yaml"
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls, yaml_file=Config._get_yaml_path() if Path("config.yaml").exists() else None),
            env_settings,
        )

    @classmethod
    def _get_yaml_path(cls) -> str | None:
        path = Path(__file__).parent.parent / "config.yaml"
        return str(path) if path.exists() else None


def load_config(path: Path | None = None) -> Config:
    """Load configuration from YAML file with validation."""
    if path is None:
        path = Path(__file__).parent.parent / "config.yaml"
    
    if path.exists():
        # Use pydantic's YAML loading via model_validate
        import yaml
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Config.model_validate(data)
    return Config()