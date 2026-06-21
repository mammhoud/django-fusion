"""
AI integrations for craftsai — pure Python, no Django required.

Provides base class and implementations for AI service integrations.
API keys are read from environment variables.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict

logger = logging.getLogger(__name__)


class AIIntegration(ABC):
    """
    Base class for AI integrations.

    Provides interface for AI service integrations.
    """

    def __init__(self, api_key: str = None, **kwargs):
        """
        Initialize AI integration.

        Args:
            api_key: API key for the service (falls back to env var)
            **kwargs: Additional configuration
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response from prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Generated response
        """

    @abstractmethod
    def stream(self, prompt: str, **kwargs):
        """
        Stream response from prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """

    def validate_config(self) -> bool:
        """
        Validate integration configuration.

        Returns:
            True if configuration is valid
        """
        if not self.api_key:
            logger.error("API key not configured")
            return False
        return True


class OpenAIIntegration(AIIntegration):
    """
    OpenAI integration — pure Python, no Django required.

    API key read from OPENAI_API_KEY env var if not provided.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", **kwargs):
        """
        Initialize OpenAI integration.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (default: gpt-3.5-turbo)
            **kwargs: Additional configuration
        """
        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        super().__init__(resolved_key, **kwargs)
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI."""
        if not self.validate_config():
            raise ValueError("OpenAI API key not configured")

        try:
            import openai
            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            return response.choices[0].message.content

        except ImportError:
            logger.error("openai package not installed")
            raise

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def stream(self, prompt: str, **kwargs):
        """Stream response using OpenAI."""
        if not self.validate_config():
            raise ValueError("OpenAI API key not configured")

        try:
            import openai
            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                **kwargs
            )

            for chunk in response:
                if "choices" in chunk:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]

        except ImportError:
            logger.error("openai package not installed")
            raise

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class ClaudeIntegration(AIIntegration):
    """
    Claude integration — pure Python, no Django required.

    API key read from ANTHROPIC_API_KEY env var if not provided.
    """

    def __init__(self, api_key: str = None, model: str = "claude-2", **kwargs):
        """
        Initialize Claude integration.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name (default: claude-2)
            **kwargs: Additional configuration
        """
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        super().__init__(resolved_key, **kwargs)
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Claude."""
        if not self.validate_config():
            raise ValueError("Anthropic API key not configured")

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            return response.content[0].text

        except ImportError:
            logger.error("anthropic package not installed")
            raise

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def stream(self, prompt: str, **kwargs):
        """Stream response using Claude."""
        if not self.validate_config():
            raise ValueError("Anthropic API key not configured")

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            with client.messages.stream(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except ImportError:
            logger.error("anthropic package not installed")
            raise

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


class AIIntegrationRegistry:
    """
    Registry for AI integrations.

    Manages registration and retrieval of AI integrations.
    """

    _integrations: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, integration_class: type):
        """Register an AI integration."""
        cls._integrations[name] = integration_class
        logger.info(f"Registered AI integration: {name}")

    @classmethod
    def get(cls, name: str, **kwargs) -> AIIntegration:
        """Get an AI integration instance."""
        if name not in cls._integrations:
            raise ValueError(f"Unknown AI integration: {name}")

        integration_class = cls._integrations[name]
        return integration_class(**kwargs)

    @classmethod
    def list_integrations(cls) -> list:
        """List all registered integrations."""
        return list(cls._integrations.keys())


# Register default integrations
AIIntegrationRegistry.register("openai", OpenAIIntegration)
AIIntegrationRegistry.register("claude", ClaudeIntegration)
