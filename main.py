#!/usr/bin/env python3
"""
LLM CLI Tool - Interactive terminal chat with LLM API.
Features:
  - Terminal-based interactive chat
  - Conversation context management
  - Chat history persistence
  - Command system for utility functions
"""

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
from core.chat_manager import ChatManager
from core.api_client import LLMClient
from config.config import SYSTEM_PROMPT, DEFAULT_INPUT_FILE, CONFIRM_BEFORE_SEND

console = Console()

class LLMCLIApp:
    """Main LLM CLI Application."""

    def __init__(self):
        """Initialize the application."""
        self.chat_manager = ChatManager()
        self.llm_client = None
        self.system_prompt = SYSTEM_PROMPT
        self.streaming = True  # Default streaming enabled
        self._initialize_client()
        self.prompt_session = PromptSession(style=PromptStyle.from_dict({
            'prompt': '#00aa00 bold',
        }))

    def _initialize_client(self) -> None:
        """Initialize LLM API client."""
        try:
            self.llm_client = LLMClient()
            console.print("[green]✓ LLM client initialized successfully[/green]")
        except Exception as e:
            console.print(f"[red]✗ Initialization error: {e}[/red]")
            # We don't exit here, as we might want to configure it later

    def print_welcome(self) -> None:
        """Print welcome message and help."""
        welcome_msg = """
# LLM CLI - Interactive Chat Tool

Type your message and press Enter to chat.

**Commands:**
- `/help`          - Show this help message
- `/history`       - Show conversation history
- `/stats`         - Show conversation statistics
- `/clear`         - Clear conversation history
- `/system <msg>`  - Set system prompt
- `/stream`        - Toggle streaming mode (default: on)
- `/session`       - Manage sessions (list/switch/new/delete/rename)
- `/config`        - Configure API key, Base URL, Model
- `/exit`          - Exit and auto-save

**Input tips:**
- `@filename`      - Load from file (shows content first)
- `@`              - Load from default (input.txt)
"""
        console.print(Panel(Markdown(welcome_msg), title="Welcome", border_style="cyan"))

    def handle_command(self, command: str) -> bool:
        """
        Handle CLI commands.
        
        Args:
            command: Command string
            
        Returns:
            True if command was handled, False otherwise
        """
        command = command.strip()
        
        if not command.startswith("/"):
            return False

        cmd_parts = command.split(maxsplit=1)
        cmd = cmd_parts[0].lower()

        if cmd == "/help":
            self.print_welcome()
        elif cmd == "/history":
            self.chat_manager.show_history()
        elif cmd == "/stats":
            self.chat_manager.show_stats()
        elif cmd == "/clear":
            self.chat_manager.clear_history()
        elif cmd == "/system":
            if len(cmd_parts) > 1:
                self.system_prompt = cmd_parts[1]
                console.print("[green]System prompt updated.[/green]")
            else:
                console.print(f"Current system prompt: {self.system_prompt}")
        elif cmd == "/stream":
            self.streaming = not self.streaming
            status = "enabled" if self.streaming else "disabled"
            console.print(f"[green]Streaming mode {status}[/green]")
        elif cmd == "/session":
            if len(cmd_parts) > 1:
                parts = cmd_parts[1].split(maxsplit=1)
                subcommand = parts[0]
                
                if subcommand == "list":
                    self.chat_manager.list_sessions()
                elif subcommand == "switch":
                    if len(parts) > 1:
                        self.chat_manager.switch_session(parts[1])
                    else:
                        console.print("[red]Usage: /session switch <name>[/red]")
                elif subcommand == "new":
                     if len(parts) > 1:
                        self.chat_manager.switch_session(parts[1])
                     else:
                        from uuid import uuid4
                        self.chat_manager.switch_session(f"session_{uuid4().hex[:8]}")
                elif subcommand == "delete":
                    if len(parts) > 1:
                        self.chat_manager.delete_session(parts[1])
                    else:
                        console.print("[red]Usage: /session delete <name>[/red]")
                elif subcommand == "rename":
                    if len(parts) > 1:
                        names = parts[1].split()
                        if len(names) == 2:
                            self.chat_manager.rename_session(names[0], names[1])
                        else:
                            console.print("[red]Usage: /session rename <old> <new>[/red]")
                    else:
                         console.print("[red]Usage: /session rename <old> <new>[/red]")
                else:
                    console.print(f"[red]Unknown session subcommand: {subcommand}[/red]")
            else:
                self.chat_manager.list_sessions()
        elif cmd == "/config":
             self._handle_config_command()
        elif cmd == "/exit" or cmd == "/quit":
            return self._confirm_exit()
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")

        return True

    def _handle_config_command(self):
        """Handle configuration command."""
        console.print("[bold]Current Configuration:[/bold]")
        console.print(f"API Key: {self.llm_client.client.api_key[:8]}..." if self.llm_client and self.llm_client.client.api_key else "API Key: Not set")
        console.print(f"Base URL: {self.llm_client.client.base_url}")
        console.print(f"Model: {self.llm_client.model}")
        
        console.print("\n[yellow]Enter new values (leave empty to keep current):[/yellow]")
        
        new_key = self.prompt_session.prompt("API Key: ", is_password=True).strip()
        new_url = self.prompt_session.prompt("Base URL: ").strip()
        new_model = self.prompt_session.prompt("Model: ").strip()
        
        if self.llm_client:
            self.llm_client.update_config(
                api_key=new_key if new_key else None,
                base_url=new_url if new_url else None,
                model=new_model if new_model else None
            )
            console.print("[green]Configuration updated.[/green]")
        else:
             # If client wasn't initialized, try to initialize now
             try:
                 # Update env vars temporarily or pass to init
                 self.llm_client = LLMClient(
                     api_key=new_key,
                     base_url=new_url or "https://api.deepseek.com"
                 )
                 if new_model:
                     self.llm_client.model = new_model
                 console.print("[green]Client initialized with new configuration.[/green]")
             except Exception as e:
                 console.print(f"[red]Failed to initialize client: {e}[/red]")

    def _confirm_exit(self) -> bool:
        """Auto-save history and exit."""
        # Always save
        self.chat_manager.save_history()
        console.print("[green]Chat history saved.[/green]")
        return True

    def send_message(self, user_input: str) -> None:
        """
        Send user message to LLM and get response.
        
        Args:
            user_input: User message text
        """
        if not self.llm_client:
             console.print("[red]LLM client not initialized. Use /config to set up API key.[/red]")
             return

        # Add user message to history
        self.chat_manager.add_message("user", user_input)

        # Get context for API
        messages = self.chat_manager.get_context()

        # Show thinking indicator
        console.print("\n[cyan]🤔 Thinking...[/cyan]\n")

        try:
            # Get response from LLM
            response = self.llm_client.chat(
                messages=messages,
                system_prompt=self.system_prompt,
                stream=self.streaming
            )

            # Add assistant response to history
            self.chat_manager.add_message("assistant", response)

            # Display response (if not streamed)
            if not self.streaming:
                console.print("[bold green]Assistant:[/bold green]")
                console.print(Markdown(response))
                console.print()

            # Auto-save history periodically
            # Use the session-based message count
            if len(self.chat_manager.sessions[self.chat_manager.current_session]) % 4 == 0:
                self.chat_manager.save_history()

        except RuntimeError as e:
            console.print(f"[red]✗ Error: {e}[/red]\n")

    def _read_file(self, filepath: str) -> str:
        """
        Read text from a file.
        
        Args:
            filepath: Path to the file (empty means use DEFAULT_INPUT_FILE)
            
        Returns:
            File content or empty string if failed
        """
        # Use default file if no filepath provided
        if not filepath:
            filepath = DEFAULT_INPUT_FILE
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Show content and ask for confirmation
            if CONFIRM_BEFORE_SEND:
                console.print(f"\n[yellow]File content ({filepath}):[/yellow]")
                console.print(Panel(content, border_style="cyan"))
                
                confirm = self.prompt_session.prompt("Send this? (y/n): ").strip().lower()
                if confirm not in ('y', 'yes'):
                    console.print("[yellow]Cancelled[/yellow]")
                    return ""
            
            console.print(f"[green]✓ Loaded from {filepath}[/green]")
            return content
        except FileNotFoundError:
            console.print(f"[red]✗ File not found: {filepath}[/red]")
            return ""
        except Exception as e:
            console.print(f"[red]✗ Error reading file: {e}[/red]")
            return ""

    def run(self) -> None:
        """Main application loop."""
        self.print_welcome()

        while True:
            try:
                # Get user input
                user_input = self.prompt_session.prompt("You: ").strip()

                if not user_input:
                    continue

                # Handle file input (@filename)
                if user_input.startswith("@"):
                    user_input = self._read_file(user_input[1:])
                    if not user_input:
                        continue

                # Handle commands
                if self.handle_command(user_input):
                    if user_input.lower().startswith("/exit") or user_input.lower().startswith("/quit"):
                        break
                    continue

                # Send message to LLM
                self.send_message(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type /exit to quit.[/yellow]")
                continue
            except EOFError:
                break
        
        # Save history on exit
        self.chat_manager.save_history()
        console.print("[green]Goodbye![/green]")


def main():
    """Entry point."""
    app = LLMCLIApp()
    app.run()


if __name__ == "__main__":
    main()
