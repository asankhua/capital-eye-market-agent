"""
Groq LLM Provider – Uses Groq API for AI analysis.

Provides a consistent interface for all agents using Groq models.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from groq import Groq

from backend.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
)

logger = logging.getLogger("market_analyst.llm_provider")

# ── Provider Interface ───────────────────────────────────────────


class LLMProvider:
    """Unified interface for LLM operations."""

    def __init__(self):
        self.provider = LLM_PROVIDER.lower()
        self._groq_client = None

        if self.provider == "groq":
            self._init_groq()
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")

        logger.info("LLM Provider initialized: %s", self.provider)

    def _init_groq(self):
        """Initialize Groq client."""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        self._groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client configured with model: %s", GROQ_MODEL)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            The generated text response
        """
        return self._generate_groq(prompt, system_prompt)

    def _generate_groq(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Groq API."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self._groq_client.chat.completions.create(
                messages=messages,
                model=GROQ_MODEL,
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Groq generation failed: %s", e)
            raise

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict[str, Any]:
        """
        Generate a JSON response and parse it.

        Args:
            prompt: The user prompt (should request JSON output)
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON as dict
        """
        text = self.generate(prompt, system_prompt)
        return self._parse_json_response(text)

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any]:
        """Parse LLM JSON response, handling potential markdown fences."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)


# ── Global Provider Instance ─────────────────────────────────────

_provider_instance: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Get or create the global LLM provider instance."""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = LLMProvider()
    return _provider_instance


def reset_provider():
    """Reset the provider (useful for testing)."""
    global _provider_instance
    _provider_instance = None
    logger.info("LLM provider reset")
