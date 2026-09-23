# ADR 0012: llama-cpp-python for Optional Local LLM

## Context
The project optionally uses a local LLM for:
- Improving script fluency (transitions, naturalness)
- Grouping related requirements
- Spoken-language rewriting
- NOT for fact generation (validated against source)

The LLM must:
- Run fully offline on CPU
- Support OpenAI-compatible API (for Ollama compatibility)
- Work with small models (phi3:mini, llama3.2:3b, gemma2:2b)
- Be optional (pipeline works without it)

## Alternatives Considered
1. **Ollama Python client**: Requires Ollama service running, not embedded
2. **llama-cpp-python**: Embedded GGUF inference, CPU-optimized, OpenAI-compatible server mode
3. **transformers + accelerate**: Heavy, requires PyTorch, slower on CPU
4. **ctransformers**: Abandoned, compatibility issues
5. **exllama**: GPU-only

## Decision
Use **llama-cpp-python >= 0.2.90** as optional local LLM backend (in `requirements-llm.txt`).

Key usage:
- `Llama.from_pretrained(repo_id, filename, n_gpu_layers=0, n_ctx=4096)` for local GGUF
- Or connect to Ollama via OpenAI-compatible endpoint
- `llm.enabled: false` by default in config.yaml
- Structured prompt with fact constraints
- Post-generation validation against source document

## Consequences
**Positive:**
- Fully offline after model download
- CPU-optimized with GGML/GGUF
- Supports quantization (q4_k_m, etc.) for memory efficiency
- OpenAI-compatible API for Ollama integration
- Small models (~2-4GB) work on modest hardware

**Negative:**
- Large dependency (C++ backend, cmake build)
- Model downloads ~2-4GB
- Optional - not in core requirements
- Compilation can fail on some platforms

**Mitigations:**
- In separate `requirements-llm.txt`
- Clear documentation for installation
- Pipeline works without it (deterministic script)
- Pre-built wheels available for Linux x86_64

## Validation
- Tested with llama-cpp-python 0.2.90
- phi3:mini (2GB) works on 8GB RAM
- Ollama integration functional
- Validation rejects unsupported LLM claims

## References
- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
- GGUF models: https://huggingface.co/models?library=gguf
- Ollama: https://ollama.ai/