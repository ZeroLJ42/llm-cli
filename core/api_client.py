"""
API client module for LLM communication.
Handles API requests and error handling.
"""

from typing import List, Dict, Optional
from openai import OpenAI, APIError
from config.config import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL, MAX_TOKENS
from rich.console import Console

console = Console()

class LLMClient:
    """Client for communicating with LLM API."""

    def __init__(self, api_key: str = OPENAI_API_KEY, base_url: str = OPENAI_BASE_URL):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI/DeepSeek API key
            base_url: API base URL
        """
        if not api_key:
            # Try to get from environment if not passed
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            
        if not api_key:
             console.print("[yellow]Warning: API key not found. Some features may not work.[/yellow]")
             # Don't raise error yet, allow app to start so user can set key
        
        self.client = OpenAI(api_key=api_key or "dummy", base_url=base_url)
        self.model = LLM_MODEL

    def update_config(self, api_key: str = None, base_url: str = None, model: str = None):
        """Update client configuration."""
        if api_key:
            self.client.api_key = api_key
        if base_url:
            self.client.base_url = base_url
        if model:
            self.model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Send a chat request to the LLM.
        
        Args:
            messages: List of message dicts with "role" and "content"
            system_prompt: System message to include at the beginning
            temperature: Sampling temperature (0.0 to 2.0)
            stream: Whether to stream the response
            
        Returns:
            Response text from the LLM
        """
        try:
            # Prepare messages with system prompt
            full_messages = messages
            if system_prompt:
                full_messages = [{"role": "system", "content": system_prompt}] + messages

            # Make API request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=MAX_TOKENS,
                stream=stream
            )

            if stream:
                return self._handle_stream(response)
            else:
                return response.choices[0].message.content

        except APIError as e:
            raise RuntimeError(f"API Error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

    def _handle_stream(self, response) -> str:
        """
        Handle streaming response from API.
        
        Args:
            response: Streaming response object
            
        Returns:
            Complete response text
        """
        full_response = ""
        try:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()  # New line after streaming completes
        except Exception as e:
            console.print(f"\n[red]Stream error: {e}[/red]")
        
        return full_response

    def validate_connection(self) -> bool:
        """Test API connection."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False
