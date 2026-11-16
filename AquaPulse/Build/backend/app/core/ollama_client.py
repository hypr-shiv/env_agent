import json
import logging
import socket
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from app.core.config import settings

logger = logging.getLogger("aquapulse.ollama")

class OllamaClient:
    """
    Client for interacting with local Ollama Llama 3.2:3b instance.
    Includes health monitoring, structured JSON generation, and fallback handling.
    """
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS
        
        parsed = urlparse(self.base_url)
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 11434

    def is_reachable(self) -> bool:
        """Fast non-blocking probe to avoid socket hangs when offline or sandboxed."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                s.connect((self.host, self.port))
                return True
        except Exception:
            return False

    async def check_health(self) -> Dict[str, Any]:
        """Verify if Ollama service is reachable and if target model is present."""
        if not self.is_reachable():
            return {
                "status": "offline",
                "base_url": self.base_url,
                "note": "Ollama service offline. Agents will operate using cached Palghar regional datasets & deterministic synthesis fallback.",
                "suggestion": f"To connect live Ollama, run: 'ollama serve' followed by 'ollama pull {self.model}'"
            }

        import httpx
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    has_model = any(self.model in m for m in models)
                    return {
                        "status": "connected",
                        "base_url": self.base_url,
                        "available_models": models,
                        "target_model": self.model,
                        "model_ready": has_model
                    }
                return {"status": "error", "message": f"HTTP {res.status_code}"}
        except Exception as e:
            logger.info(f"Ollama connection check: {e}")
            return {
                "status": "offline",
                "base_url": self.base_url,
                "note": "Ollama service unreachable",
                "error": str(e)
            }

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_format: bool = False,
        temperature: float = 0.2
    ) -> str:
        """Generates completion from Ollama. Falls back cleanly if daemon is unreachable."""
        if not self.is_reachable():
            return self._fallback_response(prompt, json_format)

        import httpx
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_format:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    logger.error(f"Ollama returned {response.status_code}: {response.text}")
                    return self._fallback_response(prompt, json_format)
        except Exception as e:
            logger.warning(f"Ollama request error: {e}. Utilizing defensive fallback.")
            return self._fallback_response(prompt, json_format)

    async def generate_vision(
        self,
        prompt: str,
        image_base64: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        """Multimodal generation for Vision models (PaliGemma, Gemma, Llama-Vision)."""
        target_model = model or "paligemma"
        if not self.is_reachable():
            return ""

        import httpx
        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    logger.warning(f"Ollama vision returned {response.status_code}: {response.text}")
                    return ""
        except Exception as e:
            logger.warning(f"Ollama vision request error: {e}")
            return ""

    def _fallback_response(self, prompt: str, json_format: bool) -> str:
        """Deterministic fallback when Ollama is offline during testing or cold start."""
        if json_format:
            return json.dumps({
                "intent": "general_coastal_query",
                "target_agents": ["weather", "fisheries"],
                "reasoning": "Default regional coastal query routing (Ollama offline fallback)",
                "location": "Palghar"
            })
        return "AquaPulse Local Knowledge Engine: The request was processed using regional cached datasets for Palghar, Maharashtra."

ollama_client = OllamaClient()
