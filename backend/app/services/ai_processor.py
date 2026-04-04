"""
AI Processing Service
Integrates with Groq and Gemini APIs for OCR and text processing
"""
import logging
import asyncio
from typing import Any, Dict

import httpx

from config import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when AI provider request fails after retries."""

    def __init__(self, message: str, provider: str, retryable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


class AIProcessor:
    """Handle AI API calls for image OCR and text processing"""
    
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.nvidia_api_key = settings.NVIDIA_API_KEY
        self.nvidia_enabled = settings.NVIDIA_ENABLED or bool(settings.NVIDIA_API_KEY)

        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.nvidia_url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"

    def _is_provider_available(self, provider: str) -> bool:
        """Check whether provider credentials are configured."""
        provider = provider.lower()
        if provider == "nvidia":
            return self.nvidia_enabled and bool(self.nvidia_api_key)
        if provider == "groq":
            return bool(self.groq_api_key)
        if provider == "gemini":
            return bool(self.gemini_api_key)
        return False

    def _resolve_provider_chain(self, preferred_provider: str | None, strict_provider: bool | None) -> list[str]:
        """Build provider chain for the current request."""
        primary = (preferred_provider or settings.PRIMARY_AI_PROVIDER or "nvidia").lower()
        strict = settings.STRICT_AI_PROVIDER if strict_provider is None else strict_provider
        if strict:
            return [primary]

        # Non-strict chain (explicit order)
        chain = [primary]
        for candidate in ["nvidia", "groq", "gemini"]:
            if candidate not in chain:
                chain.append(candidate)
        return chain

    async def _post_json(
        self,
        url: str,
        *,
        headers: Dict[str, str] | None = None,
        params: Dict[str, str] | None = None,
        payload: Dict[str, Any] | None = None,
        timeout: float | None = None,
        provider: str = "unknown",
    ) -> Dict[str, Any]:
        """Send async JSON request and return parsed JSON response."""
        effective_timeout = timeout or float(settings.AI_REQUEST_TIMEOUT_SECONDS)
        retries = max(0, int(settings.AI_REQUEST_RETRIES))
        backoff = max(0.1, float(settings.AI_RETRY_BACKOFF_SECONDS))
        last_error: Exception | None = None

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=effective_timeout) as client:
                    response = await client.post(url, headers=headers, params=params, json=payload)

                    if response.status_code in {408, 429, 500, 502, 503, 504} and attempt < retries:
                        await asyncio.sleep(backoff * (attempt + 1))
                        continue

                    response.raise_for_status()
                    return response.json()

            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
                last_error = e
                if attempt < retries:
                    await asyncio.sleep(backoff * (attempt + 1))
                    continue
                raise AIServiceError(
                    f"Provider request failed due to transient network issue: {e}",
                    provider=provider,
                    retryable=True,
                )
            except httpx.HTTPStatusError as e:
                last_error = e
                status_code = e.response.status_code
                retryable = status_code in {408, 429, 500, 502, 503, 504}
                raise AIServiceError(
                    f"Provider returned status {status_code}",
                    provider=provider,
                    retryable=retryable,
                )
            except Exception as e:
                last_error = e
                raise AIServiceError(str(e), provider=provider, retryable=False)

        raise AIServiceError(
            f"Provider request failed after retries: {last_error}",
            provider=provider,
            retryable=True,
        )
    
    async def process_image(
        self,
        image_base64: str,
        prompt: str,
        preferred_provider: str | None = None,
        strict_provider: bool | None = None,
    ) -> str:
        """
        Process image with AI vision model
        NVIDIA primary, Groq fallback
        """
        provider_chain = self._resolve_provider_chain(preferred_provider, strict_provider)
        strict = settings.STRICT_AI_PROVIDER if strict_provider is None else strict_provider

        last_error: Exception | None = None
        for provider in provider_chain:
            if not self._is_provider_available(provider):
                continue

            try:
                if provider == "nvidia":
                    return await self._process_with_nvidia(image_base64, prompt)
                if provider == "groq":
                    return await self._process_with_groq(image_base64, prompt)
                if provider == "gemini":
                    return await self._process_with_gemini(image_base64, prompt)
            except Exception as e:
                last_error = e
                if strict:
                    raise
                logger.warning(f"{provider} vision failed: {e}")

        if last_error:
            raise last_error
        raise AIServiceError(
            "No configured AI provider available for image processing",
            provider=",".join(provider_chain),
            retryable=False,
        )

    async def _process_with_nvidia(self, image_base64: str, prompt: str) -> str:
        """Process with NVIDIA NIM OpenAI-compatible API."""
        response_json = await self._post_json(
            self.nvidia_url,
            provider="nvidia",
            headers={
                "Authorization": f"Bearer {self.nvidia_api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": settings.NVIDIA_MODEL_VISION,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "temperature": settings.AI_TEMPERATURE,
                "max_tokens": 2000,
            },
        )
        return response_json["choices"][0]["message"]["content"]
    
    async def _process_with_groq(self, image_base64: str, prompt: str) -> str:
        """Process with Groq API"""
        response_json = await self._post_json(
            self.groq_url,
            provider="groq",
            headers={
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": "llama-3.2-11b-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "max_tokens": 2000,
                "temperature": settings.AI_TEMPERATURE,
            },
        )
        return response_json["choices"][0]["message"]["content"]
    
    async def _process_with_gemini(self, image_base64: str, prompt: str) -> str:
        """Process with Gemini API"""
        response_json = await self._post_json(
            self.gemini_url,
            provider="gemini",
            headers={"Content-Type": "application/json"},
            params={"key": self.gemini_api_key},
            payload={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "image/png", "data": image_base64}},
                        ]
                    }
                ]
            },
        )
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    
    async def process_text(
        self,
        text: str,
        prompt: str,
        preferred_provider: str | None = None,
        strict_provider: bool | None = None,
        model_override: str | None = None,
    ) -> str:
        """
        Process text with AI (for note generation, summarization, etc.)
        """
        provider_chain = self._resolve_provider_chain(preferred_provider, strict_provider)
        strict = settings.STRICT_AI_PROVIDER if strict_provider is None else strict_provider

        last_error: Exception | None = None
        for provider in provider_chain:
            if not self._is_provider_available(provider):
                continue

            try:
                if provider == "nvidia":
                    response_json = await self._post_json(
                        self.nvidia_url,
                        provider="nvidia",
                        headers={
                            "Authorization": f"Bearer {self.nvidia_api_key}",
                            "Content-Type": "application/json",
                        },
                        payload={
                            "model": model_override or settings.NVIDIA_MODEL_TEXT,
                            "messages": [{"role": "user", "content": f"{prompt}\n\n{text}"}],
                            "temperature": settings.AI_TEMPERATURE,
                            "max_tokens": settings.AI_MAX_TOKENS,
                        },
                    )
                    return response_json["choices"][0]["message"]["content"]

                if provider == "groq":
                    response_json = await self._post_json(
                        self.groq_url,
                        provider="groq",
                        headers={"Authorization": f"Bearer {self.groq_api_key}"},
                        payload={
                            "model": "llama-3.1-8b-instant",
                            "messages": [{"role": "user", "content": f"{prompt}\n\n{text}"}],
                            "max_tokens": 3000,
                            "temperature": settings.AI_TEMPERATURE,
                        },
                    )
                    return response_json["choices"][0]["message"]["content"]

                if provider == "gemini":
                    # Gemini text path for non-strict compatibility mode.
                    response_json = await self._post_json(
                        self.gemini_url,
                        provider="gemini",
                        headers={"Content-Type": "application/json"},
                        params={"key": self.gemini_api_key},
                        payload={
                            "contents": [{"parts": [{"text": f"{prompt}\n\n{text}"}]}]
                        },
                    )
                    return response_json["candidates"][0]["content"]["parts"][0]["text"]

            except Exception as e:
                last_error = e
                if strict:
                    raise
                logger.warning(f"{provider} text processing failed: {e}")

        if last_error:
            raise last_error
        raise AIServiceError(
            "No configured AI provider available for text processing",
            provider=",".join(provider_chain),
            retryable=False,
        )

    async def enhance_text_content(
        self,
        text: str,
        depth: str = "deep",
        preferred_provider: str | None = "nvidia",
        strict_provider: bool | None = True,
    ) -> str:
        """
        Verify and deeply enhance extracted text while preserving factual content.
        """
        normalized_depth = depth.lower().strip()
        if normalized_depth not in {"light", "deep"}:
            normalized_depth = "deep"

        prompt = (
            "You are a high-precision text refinement system for OCR/extracted documents.\n"
            "Goal: verify the extracted content, fix OCR noise, normalize formatting, and improve readability.\n"
            "Hard rules:\n"
            "1) Do not omit factual content present in input.\n"
            "2) Preserve equations and technical expressions exactly when possible.\n"
            "3) Resolve broken line wraps and spacing artifacts.\n"
            "4) Return clean plain text only.\n"
            f"Enhancement depth: {normalized_depth}.\n"
            "If uncertain, keep original phrasing instead of hallucinating."
        )

        return await self.process_text(
            text,
            prompt,
            preferred_provider=preferred_provider,
            strict_provider=strict_provider,
            model_override=settings.NVIDIA_MODEL_ENHANCEMENT if preferred_provider == "nvidia" else None,
        )
    
    async def check_ollama_available(self) -> bool:
        """Check if Ollama is available and running"""
        if not settings.OLLAMA_ENABLED:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
