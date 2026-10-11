"""
AI Provider abstraction with multi-provider fallback support.
"""
import asyncio
from typing import AsyncGenerator, Dict, List, Optional, Any

import httpx
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import AIProviderException
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AIProvider:
    """Abstract AI provider with retry and fallback logic."""

    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self._init_clients()

    def _init_clients(self):
        if settings.OPENAI_API_KEY:
            self.clients["openai"] = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if settings.ANTHROPIC_API_KEY:
            self.clients["anthropic"] = httpx.AsyncClient(
                base_url="https://api.anthropic.com/v1",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        if settings.GOOGLE_API_KEY:
            self.clients["google"] = httpx.AsyncClient(
                base_url="https://generativelanguage.googleapis.com/v1beta",
                timeout=60.0,
            )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False,
        tools: Optional[List[Dict]] = None,
    ) -> str:
        """Execute chat completion with fallback support."""

        providers = self._get_provider_chain(provider)
        last_error = None

        for prov in providers:
            try:
                result = await self._execute_provider(
                    prov,
                    messages=messages,
                    model=model or self._get_default_model(prov),
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                    tools=tools,
                )
                logger.info(f"AI response generated", provider=prov, model=model)
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"AI provider failed, trying fallback", provider=prov, error=str(e))
                await asyncio.sleep(1)

        raise AIProviderException(
            f"All AI providers failed. Last error: {last_error}",
            details={"providers_tried": providers}
        )

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion tokens."""
        prov = provider or settings.DEFAULT_AI_PROVIDER

        if prov == "openai" and "openai" in self.clients:
            async for chunk in self._stream_openai(messages, model, temperature, max_tokens):
                yield chunk
        else:
            # Fallback to non-streaming
            result = await self.chat_completion(messages, model, prov, temperature, max_tokens)
            yield result

    def _get_provider_chain(self, preferred: Optional[str]) -> List[str]:
        """Get ordered list of providers to try."""
        available = list(self.clients.keys())
        if not available:
            raise AIProviderException("No AI providers configured")

        if preferred and preferred in available:
            available.remove(preferred)
            return [preferred] + available

        # Default priority: openai -> anthropic -> google
        priority = ["openai", "anthropic", "google"]
        ordered = [p for p in priority if p in available]
        ordered += [p for p in available if p not in ordered]
        return ordered

    def _get_default_model(self, provider: str) -> str:
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "google": "gemini-1.5-pro",
        }
        return defaults.get(provider, "gpt-4o")

    async def _execute_provider(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        tools: Optional[List[Dict]],
    ) -> str:
        if provider == "openai":
            return await self._call_openai(messages, model, temperature, max_tokens, json_mode, tools)
        elif provider == "anthropic":
            return await self._call_anthropic(messages, model, temperature, max_tokens, json_mode)
        elif provider == "google":
            return await self._call_google(messages, model, temperature, max_tokens)
        else:
            raise AIProviderException(f"Unknown provider: {provider}")

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        tools: Optional[List[Dict]],
    ) -> str:
        client = self.clients["openai"]
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        if tools:
            params["tools"] = tools

        response = await client.chat.completions.create(**params)
        return response.choices[0].message.content or ""

    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> str:
        client = self.clients["anthropic"]

        system_msg = None
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        payload = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            payload["system"] = system_msg

        response = await client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    async def _call_google(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        client = self.clients["google"]

        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        url = f"/models/{model}:generateContent?key={settings.GOOGLE_API_KEY}"
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        client = self.clients["openai"]
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
_ai_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = AIProvider()
    return _ai_provider
