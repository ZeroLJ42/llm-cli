import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# System Prompt
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant")

# Context Management
MAX_CONTEXT_MESSAGES = 20  # Keep last N messages in context for API
MAX_HISTORY_MESSAGES = 1000  # Keep last N messages in local storage
MAX_TOKENS = 4096  # Max tokens for API response

# UI Configuration
HISTORY_FILE = ".chat_history"  # Local file to store chat history
DEFAULT_INPUT_FILE = "input.txt"  # Default file for @ input
STREAMING_MODE = True  # Enable streaming by default
CONFIRM_BEFORE_SEND = True  # Show content and ask confirmation before sending
