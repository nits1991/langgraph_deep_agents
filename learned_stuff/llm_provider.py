"""Central registry for LLM providers and models.

Keep every model you can access in one place so other scripts can import
them without hardcoding provider/model strings all over the codebase.

Example:
    from learned_stuff.llm_provider import DEFAULT_CHEAP_MODEL, get_model_spec

    spec = get_model_spec("gemini_flash")
    print(spec.provider, spec.model)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal

ProviderName = Literal[
    "ollama",
    "google_genai",
    "nvidia",
    "anthropic",
    "openai",
    "groq",
    "opencode",
]


@dataclass(frozen=True)
class ModelSpec:
    """Description of one model you can use in this project."""

    provider: ProviderName
    model: str
    display_name: str
    notes: str = ""
    kwargs: Dict[str, Any] | None = None

    def with_overrides(self, **kwargs: Any) -> Dict[str, Any]:
        """Return kwargs suitable for init_chat_model or provider constructors."""
        merged = dict(self.kwargs or {})
        merged.update(kwargs)
        merged["model"] = self.model
        merged["provider"] = self.provider
        return merged


# Local, free, and fast options.
OLLAMA_QWEN_2_5_CODER = ModelSpec(
    provider="ollama",
    model="qwen2.5-coder:latest",
    display_name="Ollama Qwen 2.5 Coder",
    notes="Best default for free local coding, completions, and inline edits.",
    kwargs={
        "base_url": "http://localhost:11434",
    },
)

# Free/low-cost cloud options you can swap in when available.
GOOGLE_GEMINI_FLASH = ModelSpec(
    provider="google_genai",
    model="gemini-2.5-flash",
    display_name="Gemini Flash",
    notes="Fast general-purpose model for cheap/fast cloud calls.",
)

GOOGLE_GEMINI_PRO = ModelSpec(
    provider="google_genai",
    model="gemini-2.5-pro",
    display_name="Gemini Pro",
    notes="Better quality, usually slower than Flash.",
)

NVIDIA_LLAMA_31_8B = ModelSpec(
    provider="nvidia",
    model="meta/llama-3.1-8b-instruct",
    display_name="NVIDIA Llama 3.1 8B",
    notes="Good free-tier style choice for summarization or lightweight reasoning.",
)

GROQ_LLAMA_33_70B = ModelSpec(
    provider="groq",
    model="llama-3.3-70b-versatile",
    display_name="Groq Llama 3.3 70B",
    notes="Very fast when you want a stronger hosted model and have access.",
)


# Default aliases used by the rest of the project.
DEFAULT_LOCAL_MODEL = OLLAMA_QWEN_2_5_CODER
DEFAULT_CHEAP_MODEL = GOOGLE_GEMINI_FLASH
DEFAULT_REASONING_MODEL = GOOGLE_GEMINI_PRO


AVAILABLE_MODELS: Dict[str, ModelSpec] = {
    "ollama_qwen2_5_coder": OLLAMA_QWEN_2_5_CODER,
    "gemini_flash": GOOGLE_GEMINI_FLASH,
    "gemini_pro": GOOGLE_GEMINI_PRO,
    "nvidia_llama_3_1_8b": NVIDIA_LLAMA_31_8B,
    "groq_llama_3_3_70b": GROQ_LLAMA_33_70B,
}


def list_models() -> dict[str, ModelSpec]:
    """Return every registered model spec."""
    return dict(AVAILABLE_MODELS)


def get_model_spec(name: str) -> ModelSpec:
    """Look up one registered model by key."""
    try:
        return AVAILABLE_MODELS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown model key: {name!r}") from exc


def get_model_kwargs(name: str, **overrides: Any) -> dict[str, Any]:
    """Return a config dictionary for init_chat_model or direct client setup."""
    return get_model_spec(name).with_overrides(**overrides)


def build_model_factory(name: str) -> Callable[..., dict[str, Any]]:
    """Return a small factory for scripts that want a callable."""

    def factory(**overrides: Any) -> dict[str, Any]:
        return get_model_kwargs(name, **overrides)

    return factory


__all__ = [
    "AVAILABLE_MODELS",
    "DEFAULT_CHEAP_MODEL",
    "DEFAULT_LOCAL_MODEL",
    "DEFAULT_REASONING_MODEL",
    "GOOGLE_GEMINI_FLASH",
    "GOOGLE_GEMINI_PRO",
    "GROQ_LLAMA_33_70B",
    "ModelSpec",
    "NVIDIA_LLAMA_31_8B",
    "OLLAMA_QWEN_2_5_CODER",
    "build_model_factory",
    "get_model_kwargs",
    "get_model_spec",
    "list_models",
]
