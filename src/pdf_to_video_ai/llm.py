from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class LlmConfig:
    enabled: bool = False
    provider: str = "ollama"  # "ollama" | "llama-cpp" | "transformers"
    model: str = "phi3:mini"   # "phi3:mini", "llama3.2:3b", "mistral:7b"
    base_url: str = "http://localhost:11434"
    max_tokens: int = 500
    temperature: float = 0.2


def is_llm_available(config: LlmConfig) -> bool:
    """Check if the configured local LLM service is reachable."""
    if not config.enabled:
        return False
    if config.provider == "ollama":
        try:
            import urllib.request
            req = urllib.request.Request(f"{config.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False
    return False


def enhance_script_block(text: str, config: LlmConfig, system_prompt: Optional[str] = None) -> str:
    """
    Enhance a narrative block using a local LLM to improve fluency.
    Enforces strict rules: no inventing data, keep factual accuracy.
    """
    if not config.enabled or not is_llm_available(config):
        return text

    if system_prompt is None:
        system_prompt = (
            "Eres un redactor profesional de guiones informativos en español. "
            "Reescribe el siguiente texto para que sea natural, fluido y fácil de entender al ser escuchado en un video. "
            "REGLAS ESTRICTAS: "
            "1. NO inventes fechas, montos, requisitos, nombres ni datos que no estén en el texto original. "
            "2. Mantén exactamente los mismos datos factuales. "
            "3. Hazlo conciso y directo, estilo narrador de noticias o redes sociales. "
            "4. Devuelve ÚNICAMENTE el texto narrativo mejorado, sin explicaciones ni saludos."
        )

    prompt = f"Texto original:\n{text}\n\nTexto narrado mejorado:"

    if config.provider == "ollama":
        return _call_ollama(prompt, system_prompt, config)

    return text


def _call_ollama(prompt: str, system_prompt: str, config: LlmConfig) -> str:
    try:
        import urllib.request
        data = {
            "model": config.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            }
        }
        req = urllib.request.Request(
            f"{config.base_url}/api/generate",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            enhanced = res_data.get("response", "").strip()
            return enhanced if enhanced else prompt
    except Exception as e:
        print(f"Local LLM call failed: {e}")
        return prompt


def generate_intro_outro(doc_title: str, deadline: Optional[str], institution: Optional[str], config: LlmConfig) -> tuple[str, str]:
    """Generate professional intro and outro sentences using LLM (or fallback)."""
    if not config.enabled or not is_llm_available(config):
        # Fallback deterministic intro/outro
        intro = f"Atención ecuatorianos, hoy te presentamos la beca {doc_title}."
        if institution:
            intro += f" Ofrecida por {institution}."
        outro = "Revisa los requisitos y postula a tiempo. Síguenos para más oportunidades de becas."
        return intro, outro

    prompt = (
        f"Genera exactamente 2 frases para un video corto de redes sociales sobre una beca para ecuatorianos:\n"
        f"Título: {doc_title}\n"
        f"Institución: {institution or 'No especificada'}\n"
        f"Fecha límite: {deadline or 'Próximamente'}\n\n"
        f"Formato de respuesta:\n"
        f"INTRO: [Frase de bienvenida llamativa de 15 palabras máx]\n"
        f"CIERRE: [Llamado a la acción de 15 palabras máx]"
    )

    resp = _call_ollama(prompt, "Eres un redactor de guiones para videos de TikTok/Reels de becas. Sé muy conciso.", config)
    intro = f"Conoce la beca {doc_title}."
    outro = "No te pierdas esta oportunidad. Síguenos para más becas."

    for line in resp.splitlines():
        if line.startswith("INTRO:"):
            intro = line.replace("INTRO:", "").strip()
        elif line.startswith("CIERRE:"):
            outro = line.replace("CIERRE:", "").strip()

    return intro, outro
