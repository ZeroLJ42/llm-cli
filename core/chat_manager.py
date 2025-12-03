"""
Chat context management module.
Handles conversation history, context window, and persistent storage.
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from uuid import uuid4
from config.config import MAX_HISTORY_MESSAGES, MAX_CONTEXT_MESSAGES, HISTORY_FILE
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

class ChatManager:
    """Manages chat history and sessions."""

    def __init__(self, history_file: str = HISTORY_FILE):
        self.history_file = history_file
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.load_history()
        
        # Always create a new session on startup
        new_session_name = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.sessions[new_session_name] = []
        self.current_session = new_session_name
        
        # console.print(f"[dim]Started new session: {self.current_session}[/dim]")

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the current session's history.
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.sessions[self.current_session].append(message)
        self._trim_history()

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """
        Get messages formatted for API call (without timestamps).
        
        Returns:
            List of messages with only role and content
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.sessions[self.current_session]
        ]

    def get_context(self) -> List[Dict[str, str]]:
        """Get current context window for the API."""
        # Return last MAX_CONTEXT_MESSAGES messages of the current session
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.sessions[self.current_session][-MAX_CONTEXT_MESSAGES:]
        ]

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.sessions[self.current_session] = []
        self.save_history()
        console.print("[green]Chat history cleared.[/green]")

    def switch_session(self, session_name: str) -> None:
        """Switch to an existing session or create a new one."""
        if session_name not in self.sessions:
            self.sessions[session_name] = []
        self.current_session = session_name
        console.print(f"[green]Switched to session: {session_name}[/green]")

    def delete_session(self, session_name: str) -> None:
        """Delete a session."""
        if session_name not in self.sessions:
            console.print(f"[red]Session '{session_name}' not found.[/red]")
            return
        
        if session_name == self.current_session:
            console.print(f"[red]Cannot delete current session. Switch to another session first.[/red]")
            return

        del self.sessions[session_name]
        self.save_history()
        console.print(f"[green]Session '{session_name}' deleted.[/green]")

    def rename_session(self, old_name: str, new_name: str) -> None:
        """Rename a session."""
        if old_name not in self.sessions:
            console.print(f"[red]Session '{old_name}' not found.[/red]")
            return
        
        if new_name in self.sessions:
            console.print(f"[red]Session '{new_name}' already exists.[/red]")
            return

        self.sessions[new_name] = self.sessions.pop(old_name)
        if self.current_session == old_name:
            self.current_session = new_name
        
        self.save_history()
        console.print(f"[green]Session renamed from '{old_name}' to '{new_name}'.[/green]")

    def list_sessions(self) -> None:
        """List all available sessions."""
        table = Table(title="Available Sessions")
        table.add_column("Name", style="cyan")
        table.add_column("Messages", style="magenta")
        table.add_column("Active", style="green")

        for name in self.sessions:
            active = "✓" if name == self.current_session else ""
            table.add_row(name, str(len(self.sessions[name])), active)
        
        console.print(table)

    def save_history(self) -> None:
        """Save all sessions to file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
        except IOError as e:
            console.print(f"[red]Error saving history: {e}[/red]")

    def load_history(self) -> None:
        """Load all sessions from file if it exists."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.sessions = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                console.print(f"[red]Error loading history: {e}[/red]")
                self.sessions = {"default": []}

    def show_history(self) -> None:
        """Display conversation history."""
        if not self.sessions[self.current_session]:
            console.print("[yellow]No conversation history.[/yellow]")
            return

        console.print(Panel(f"[bold]CONVERSATION HISTORY: {self.current_session}[/bold]", style="blue"))
        
        for i, msg in enumerate(self.sessions[self.current_session], 1):
            role = msg["role"].upper()
            timestamp = msg.get("timestamp", "Unknown")
            content = msg["content"]
            
            color = "green" if role == "ASSISTANT" else "blue"
            console.print(f"\n[bold {color}][{i}] {role} ({timestamp})[/bold {color}]")
            console.print(Markdown(content))
            console.print("-" * 40)
        

    def show_stats(self) -> None:
        """Display conversation statistics."""
        total_messages = len(self.sessions[self.current_session])
        user_messages = sum(1 for msg in self.sessions[self.current_session] if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.sessions[self.current_session] if msg["role"] == "assistant")
        
        table = Table(title="Session Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Messages", str(total_messages))
        table.add_row("User Messages", str(user_messages))
        table.add_row("Assistant Messages", str(assistant_messages))
        
        console.print(table)

    def _trim_history(self) -> None:
        """Keep only the most recent messages if history exceeds maximum."""
        if len(self.sessions[self.current_session]) > MAX_HISTORY_MESSAGES * 2:
            self.sessions[self.current_session] = self.sessions[self.current_session][-MAX_HISTORY_MESSAGES:]
