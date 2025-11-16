"""
Local LLM Client using Ollama
100% FREE - No API keys required!
"""

import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

from src.core.config import get_settings

settings = get_settings()


class LocalLLMClient:
    """
    Client for local LLM inference using Ollama.
    Completely free, no API keys needed!
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize local LLM client.

        Args:
            base_url: Ollama server URL (default: from settings)
            model: Model name (default: from settings)
        """
        self.base_url = base_url or settings.ollama_url
        self.model = model or settings.ollama_model
        self.timeout = httpx.Timeout(settings.ai_timeout, connect=10.0)

        logger.info(f"Initialized Local LLM Client - Model: {self.model}, URL: {self.base_url}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> str:
        """
        Generate chat completion using local LLM.

        Args:
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response

        Returns:
            str: Generated response
        """
        # Convert messages to Ollama prompt format
        prompt = self._messages_to_prompt(messages)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")

            except httpx.HTTPError as e:
                logger.error(f"Local LLM request failed: {e}")
                # Fallback to simple response
                return self._fallback_response(messages)

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt."""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Simple fallback when LLM is unavailable."""
        logger.warning("Using fallback response - LLM unavailable")
        return "# Local LLM is currently unavailable. Using fallback response."

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings using local model.

        Args:
            text: Text to embed

        Returns:
            List[float]: Embedding vector
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": settings.ollama_embedding_model,
                        "prompt": text,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("embedding", [0.0] * 768)  # Default 768-dim

            except httpx.HTTPError as e:
                logger.error(f"Local embedding generation failed: {e}")
                # Return zero vector as fallback
                return [0.0] * 768

    async def list_models(self) -> List[str]:
        """
        List available local models.

        Returns:
            List[str]: Available model names
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                result = response.json()
                models = [m["name"] for m in result.get("models", [])]
                return models

            except httpx.HTTPError as e:
                logger.error(f"Failed to list models: {e}")
                return []

    async def pull_model(self, model_name: str) -> bool:
        """
        Download a model from Ollama library.

        Args:
            model_name: Name of model to download

        Returns:
            bool: Success status
        """
        logger.info(f"Pulling model: {model_name}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(3600.0)) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name, "stream": False},
                )
                response.raise_for_status()
                logger.info(f"Successfully pulled model: {model_name}")
                return True

            except httpx.HTTPError as e:
                logger.error(f"Failed to pull model {model_name}: {e}")
                return False

    async def is_available(self) -> bool:
        """
        Check if Ollama server is available.

        Returns:
            bool: True if available
        """
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
            except Exception:
                return False


# Singleton instance
_llm_client: Optional[LocalLLMClient] = None


def get_local_llm() -> LocalLLMClient:
    """Get singleton instance of local LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LocalLLMClient()
    return _llm_client
