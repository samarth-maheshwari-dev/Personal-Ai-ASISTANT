"""
Ollama Router - The ONLY AI gateway for JARVIS.
Tries cloud proxies first, then offline models, best quality last.
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"


class ModelTier(Enum):
    CLOUD = "cloud"
    OFFLINE = "offline"


@dataclass
class ModelConfig:
    name: str
    tier: ModelTier
    timeout: int = 30
    options: Optional[Dict[str, Any]] = None


MODELS = [
    ModelConfig("minimax-m3:cloud", ModelTier.CLOUD, timeout=30),
    ModelConfig("nemotron-3-super:cloud", ModelTier.CLOUD, timeout=30),
    ModelConfig("gemma4:e2b", ModelTier.OFFLINE, timeout=120),
    ModelConfig("qwen2.5:3b", ModelTier.OFFLINE, timeout=60),
    ModelConfig("phi3:mini", ModelTier.OFFLINE, timeout=60),
]

MAX_RETRIES = 2


class OllamaRouter:
    """
    Single gateway for all AI requests.
    Tries cloud proxies first, falls back to offline models, best quality last.
    """

    def __init__(self, url: str = OLLAMA_URL):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._health_cache = None
        self._health_cache_time = 0
        self._installed_models = None

    def _is_ollama_running(self) -> bool:
        """Quick health check - cache for 30 seconds."""
        import time
        now = time.time()
        if self._health_cache is not None and now - self._health_cache_time < 30:
            return self._health_cache

        try:
            r = self.session.get(f"{self.url}/api/tags", timeout=3)
            self._health_cache = r.status_code == 200
            self._health_cache_time = now
            return self._health_cache
        except:
            self._health_cache = False
            self._health_cache_time = now
            return False

    def _get_available_models(self) -> List[str]:
        """Get list of actually installed models from Ollama (cached)."""
        if self._installed_models is not None:
            return self._installed_models
        try:
            r = self.session.get(f"{self.url}/api/tags", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self._installed_models = [m['name'] for m in data.get('models', [])]
                return self._installed_models
        except:
            pass
        return []

    def _build_payload(self, model: str, prompt: str, system: str, options: Optional[Dict] = None) -> Dict:
        """Build request payload for Ollama API."""
        full_prompt = system + "\n\n" + prompt if system else prompt
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1000,
            }
        }
        if options:
            payload["options"].update(options)
        return payload

    def _try_model(self, model: ModelConfig, prompt: str, system: str) -> Optional[str]:
        """Try a single model, return response or None on failure."""
        if model.tier == ModelTier.OFFLINE:
            available = self._get_available_models()
            if available and model.name not in available:
                return None

        payload = self._build_payload(model.name, prompt, system, model.options)

        try:
            response = self.session.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=model.timeout
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "").strip()
                if text:
                    return text
                return None
            if response.status_code == 410:
                return None
            return None
        except:
            return None

    def handle(self, prompt: str, system: str = "", model_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point - handles AI request.
        Tries models in priority order, using first that responds.
        Implements automatic fallback, retries, and recovery.
        """
        if not self._is_ollama_running():
            return {
                "reply": "I'm having trouble connecting to any model right now. Please try again.",
                "provider": "none",
                "tier": "none",
                "error": "Ollama not running"
            }

        models_to_try = list(MODELS)

        if model_hint:
            for m in MODELS:
                if m.name == model_hint:
                    models_to_try.insert(0, models_to_try.pop(models_to_try.index(m)))
                    break

        errors = []

        for model in models_to_try:
            result = self._try_model(model, prompt, system)
            if result:
                return {
                    "reply": result,
                    "provider": model.name,
                    "tier": model.tier.value
                }
            errors.append(model.name)

        # All models failed -- retry the last model (phi3:mini) with retries
        last_model = models_to_try[-1] if models_to_try else None
        if last_model:
            for attempt in range(MAX_RETRIES):
                result = self._try_model(last_model, prompt, system)
                if result:
                    return {
                        "reply": result,
                        "provider": last_model.name,
                        "tier": last_model.tier.value
                    }
                errors.append(f"{last_model.name} (retry {attempt + 1})")

        # Attempt recovery: clear caches and retry the first model once
        self._health_cache = None
        self._health_cache_time = 0
        self._installed_models = None

        if self._is_ollama_running():
            first_model = models_to_try[0] if models_to_try else None
            if first_model:
                result = self._try_model(first_model, prompt, system)
                if result:
                    return {
                        "reply": result,
                        "provider": first_model.name,
                        "tier": first_model.tier.value
                    }

        # Generate detailed error log
        error_details = "; ".join(errors)
        logger.error(f"All models failed. Attempted: {error_details}")

        return {
            "reply": "I'm having trouble connecting right now. Please try again.",
            "provider": "none",
            "tier": "none",
            "error": f"all models failed after retries: {error_details}"
        }

    def handle_chat(self, messages: List[Dict], system: str = "") -> Dict[str, Any]:
        """
        Handle chat with message history.
        Converts messages to prompt format for Ollama.
        """
        prompt_parts = []
        if system:
            prompt_parts.append(f"System: {system}")
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.title()}: {content}")
        prompt = "\n".join(prompt_parts)
        return self.handle(prompt, "")


_default_router = None


def get_router() -> OllamaRouter:
    """Get or create default router instance."""
    global _default_router
    if _default_router is None:
        _default_router = OllamaRouter()
    return _default_router


def handle(prompt: str, system: str = "", model_hint: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for simple requests."""
    return get_router().handle(prompt, system, model_hint)


def handle_chat(messages: List[Dict], system: str = "") -> Dict[str, Any]:
    """Convenience function for chat with history."""
    return get_router().handle_chat(messages, system)

