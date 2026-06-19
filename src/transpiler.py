"""AI transpiler and executor for .no files using Groq Cloud."""

from __future__ import annotations
from pathlib import Path

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import shlex
import sqlite3
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests


# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
BOLD = '\033[1m'
RESET = '\033[0m'


# Global config
CONFIG = {
    "cache_ttl": None,  # None means no expiration
    "model": "openai/gpt-oss-120b",
    "temperature": 0.1,
    "timeout": 30,
    "verbose": False,
    "quiet": False,
    "color": True,
    "interpreter": sys.executable,
    "show_execution_status": True,
}


def get_memory_path() -> Path:
    """Get the path to the memory database in ~/.novacompile/compiler/memory/"""
    home_dir = Path.home()
    memory_dir = home_dir / ".novacompile" / "compiler" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir / "chat-memory.db"


def get_backup_path() -> Path:
    """Get the path to the backup directory in ~/.novacompile/compiler/backups/"""
    home_dir = Path.home()
    backup_dir = home_dir / ".novacompile" / "compiler" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


class Memory:
    """Manages persistent memory for the AI using SQLite."""
    
    def __init__(self):
        self.memory_file = str(get_memory_path())
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables."""
        self.conn = sqlite3.connect(self.memory_file)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp REAL
            )
        ''')
        self.conn.commit()
    
    def store(self, key: str, value: str) -> None:
        """Store a value in memory."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO memory (key, value, timestamp) VALUES (?, ?, ?)",
            (key, value, time.time())
        )
        self.conn.commit()
    
    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve a value from memory."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all(self) -> Dict[str, str]:
        """Get all stored memories."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM memory")
        results = cursor.fetchall()
        return {key: value for key, value in results}
    
    def clear(self) -> None:
        """Clear all memory."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM memory")
        self.conn.commit()
    
    def add_conversation(self, role: str, content: str) -> None:
        """Add a conversation entry."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversation (role, content, timestamp) VALUES (?, ?, ?)",
            (role, content, time.time())
        )
        self.conn.commit()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM conversation ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        return [{"role": role, "content": content} for role, content in reversed(results)]
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


# Global memory instance
memory = Memory()


def format_bold_text(text: str) -> str:
    """Convert **text** to ANSI bold format."""
    if not CONFIG["color"]:
        # If color is disabled, just remove the ** markers
        return re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Replace **text** with bold ANSI codes
    pattern = r'\*\*(.*?)\*\*'
    return re.sub(pattern, f'{BOLD}\\1{RESET}', text)


def error(msg: str) -> None:
    """Print a red error message and exit."""
    if CONFIG["color"]:
        print(f"{RED}ERROR:{RESET} {msg}", file=sys.stderr)
    else:
        print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    """Print a yellow warning message."""
    if CONFIG["quiet"]:
        return
    if CONFIG["color"]:
        print(f"{YELLOW}WARNING:{RESET} {msg}", file=sys.stderr)
    else:
        print(f"WARNING: {msg}", file=sys.stderr)


def info(msg: str) -> None:
    """Print a cyan info message (only in verbose mode)."""
    if CONFIG["quiet"] or not CONFIG["verbose"]:
        return
    if CONFIG["color"]:
        print(f"{CYAN}INFO:{RESET} {msg}", file=sys.stderr)
    else:
        print(f"INFO: {msg}", file=sys.stderr)


def success(msg: str) -> None:
    """Print a green success message."""
    if CONFIG["quiet"] or not CONFIG["show_execution_status"]:
        return
    if CONFIG["color"]:
        print(f"{GREEN}SUCCESS:{RESET} {msg}")
    else:
        print(f"SUCCESS: {msg}")


def verbose_print(msg: str) -> None:
    """Print a message only in verbose mode."""
    if CONFIG["verbose"] and not CONFIG["quiet"]:
        if CONFIG["color"]:
            print(f"{CYAN}{msg}{RESET}")
        else:
            print(msg)


def get_cache_path() -> Path:
    """Get the path to the cache file."""
    src_dir = Path(__file__).resolve().parent
    cache_dir = src_dir.parent / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "cache.json"


def load_cache() -> dict:
    """Load the cache from disk."""
    cache_path = get_cache_path()
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    """Save the cache to disk."""
    cache_path = get_cache_path()
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def clear_cache() -> None:
    """Clear the entire cache."""
    cache_path = get_cache_path()
    if cache_path.exists():
        cache_path.unlink()
    success("Cache cleared successfully.")


def get_cache_size() -> tuple[int, int]:
    """Get cache size in entries and bytes."""
    cache = load_cache()
    size_bytes = 0
    for key, value in cache.items():
        if isinstance(value, dict):
            size_bytes += len(json.dumps(value).encode('utf-8'))
        else:
            size_bytes += len(str(value).encode('utf-8'))
    return len(cache), size_bytes


def get_cache_key(prompt: str) -> str:
    """Generate a cache key from the prompt."""
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()


def clean_old_cache_entries(cache: dict) -> dict:
    """Remove cache entries older than TTL."""
    if CONFIG["cache_ttl"] is None:
        return cache
    
    now = time.time()
    cleaned = {}
    for key, value in cache.items():
        if isinstance(value, dict) and "timestamp" in value:
            if now - value["timestamp"] <= CONFIG["cache_ttl"]:
                cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned


def get_api_key() -> str:
    """Get the API key from the key file."""
    src_dir = Path(__file__).resolve().parent
    file_path = src_dir.parent / "key" / "raw.txt"
    try:
        with open(file_path, "r") as file:
            api_key = file.read().strip()
            if not api_key:
                error("API key not found. Please run setup.sh to add your API key.")
            return api_key
    except FileNotFoundError:
        error(f"API key file not found at {file_path}. Please run setup.sh.")


def get_file_tree(directory: str = ".") -> str:
    """Get a tree representation of all files in the current directory."""
    current_dir = Path(directory).resolve()
    tree_lines = []
    
    for root, dirs, files in os.walk(current_dir):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        rel_path = Path(root).relative_to(current_dir)
        if rel_path == Path('.'):
            tree_lines.append("./")
        else:
            tree_lines.append(f"{rel_path}/")
        
        for file in sorted(files):
            if not file.startswith('.') and not file.endswith('.bak'):
                file_path = Path(root) / file
                try:
                    size = file_path.stat().st_size
                    size_str = f"({size} bytes)" if size < 1024 else f"({size/1024:.1f} KB)"
                    tree_lines.append(f"  {file} {size_str}")
                except:
                    tree_lines.append(f"  {file}")
        
        tree_lines.append("")
    
    return "\n".join(tree_lines)


def read_file_content(filepath: str) -> str:
    """Read the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return "[Binary file - content not displayed]"
    except Exception as e:
        return f"[Error reading file: {str(e)}]"


def edit_file(filepath: str, new_content: str) -> bool:
    """Edit a file with new content. Only allows editing files within current directory."""
    current_dir = Path.cwd().resolve()
    target_path = Path(filepath).resolve()
    
    # Check if the file is within the current directory
    try:
        target_path.relative_to(current_dir)
    except ValueError:
        return False  # File is outside current directory
    
    # Create backup in ~/.novacompile/compiler/backups/
    backup_dir = get_backup_path()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{target_path.name}.{timestamp}.bak"
    backup_path = backup_dir / backup_filename
    
    if target_path.exists():
        try:
            # Read the original content
            with open(target_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Write backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            verbose_print(f"Backup created: {backup_path}")
        except:
            return False
    
    # Write new content directly to the target file
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except:
        return False


def get_all_files_content() -> str:
    """Get content of all files in the current directory."""
    current_dir = Path.cwd()
    files_content = []
    
    for root, dirs, files in os.walk(current_dir):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in sorted(files):
            if not file.startswith('.') and not file.endswith('.bak'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(current_dir)
                content = read_file_content(file_path)
                files_content.append(f"--- {rel_path} ---\n{content}\n")
    
    return "\n".join(files_content)


def transpile_to_python(source: str, use_cache: bool = True) -> str:
    """Sends a raw HTTP POST request using an active production Groq model ID."""
    start_time = time.time()
    api_key = get_api_key()

    # Check cache first
    if use_cache:
        cache = load_cache()
        cache = clean_old_cache_entries(cache)
        cache_key = get_cache_key(source)
        if cache_key in cache:
            info("Using cached response")
            result = cache[cache_key].get("result", "") if isinstance(cache[cache_key], dict) else cache[cache_key]
            return result

    info("Sending request to Groq API...")

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_instruction = (
        "You are an expert transpiler. Analyze the provided input text, unstructured instructions, or pseudo-code.\n"
        "Infer the core programming logic and intent, then rewrite it entirely into a functional, syntactically correct Python script.\n\n"
        "Ensure all formatting, logic flows, variables, and outputs map accurately to valid Python code.\n"
        "Do not include any Markdown syntax, code block formatting (like ```python), chat preamble, or explanations.\n"
        "If the provided input text is ambiguous, make reasonable assumptions to produce a coherent Python script that best captures the likely intent.\n"
        "If the input is empty or contains only whitespace, return an empty string without error.\n"
        "If the input contains multiple distinct instructions or sections, combine them into a single cohesive Python script that integrates all elements logically.\n"
        "If the script mentions any other files, APIs, or external resources, include the correct code to be able to interact with those external entities.\n"
        "If the input contains any text that could simply be a description of the desired output, rather than instructions for how to generate it, do not include that text in the output Python code. Instead, use it as a hint to guide your generation of the Python code.\n"
        "Output ONLY raw executable Python text. If you must use quotes, ensure they are properly closed."
    )

    payload = {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": source}
        ],
        "temperature": CONFIG["temperature"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=CONFIG["timeout"])
        
        if response.status_code != 200:
            safe_msg = response.text.replace('"', '\\"')
            error(f"API Error (Status {response.status_code}): {safe_msg}")
            
        data = response.json()
        raw_python = data["choices"][0]["message"]["content"]
        
        clean_lines = []
        for line in raw_python.splitlines():
            if not line.strip().startswith("```"):
                clean_lines.append(line)
        raw_python = "\n".join(clean_lines)
        
        result = raw_python.strip()

        # Store in cache
        if use_cache:
            cache = load_cache()
            cache_key = get_cache_key(source)
            cache[cache_key] = {
                "result": result,
                "timestamp": time.time()
            }
            cache = clean_old_cache_entries(cache)
            save_cache(cache)
            info("Response cached")

        elapsed = time.time() - start_time
        info(f"Request completed in {elapsed:.2f}s")
        
        return result

    except requests.exceptions.Timeout:
        error(f"API request timed out after {CONFIG['timeout']} seconds. Use --timeout to increase.")
    except requests.exceptions.ConnectionError:
        error("Failed to connect to Groq API. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        error(f"API request failed: {str(e)}")
    except Exception as e:
        error(f"Unexpected error during transpilation: {str(e)}")


def chat_with_ai(user_input: str, chat_history: list = None, permission_granted: bool = False) -> tuple[str, list, bool]:
    """Send a message to the AI in chat mode with tool capabilities."""
    start_time = time.time()
    api_key = get_api_key()

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Check for permission triggers
    new_permission = permission_granted
    processed_input = user_input
    
    # Check for ;edit command
    if ';edit' in user_input.lower():
        new_permission = True
        processed_input = user_input.replace(';edit', '').strip()
        verbose_print("Edit permission granted")
    
    # Check for ;share command
    if ';share' in user_input.lower():
        file_tree = get_file_tree()
        all_content = get_all_files_content()
        share_info = f"\n\n[FILE SYSTEM INFORMATION]\n\nDirectory Structure:\n{file_tree}\n\nFile Contents:\n{all_content}"
        processed_input = processed_input.replace(';share', '').strip()
        processed_input += share_info
        verbose_print("Shared all file information with Nova")
    
    # Get recent conversations for context
    recent_conversations = memory.get_recent_conversations(5)
    memory_context = "\n".join([
        f"{conv['role']}: {conv['content'][:200]}..." 
        for conv in recent_conversations
    ])
    
    # Get stored memories
    stored_memories = memory.get_all()
    memory_summary = "\n".join([f"{k}: {v}" for k, v in stored_memories.items()]) if stored_memories else "No stored memories"

    system_instruction = (
        "You are Nova, an advanced AI coding agent developed by NovaCompile. "
        "Your primary purpose is to assist with programming, software development, and coding tasks. "
        "You are a specialized development assistant that can help with:\n\n"
        
        "1. Writing, reviewing, and debugging code in various programming languages\n"
        "2. Explaining programming concepts and algorithms\n"
        "3. Designing software architecture and solutions\n"
        "4. Optimizing code for performance and efficiency\n"
        "5. Converting code between different languages\n"
        "6. Creating documentation and comments\n"
        "7. Analyzing code for bugs and security issues\n"
        "8. Suggesting best practices and design patterns\n"
        "9. Building full-stack applications\n"
        "10. API design and integration\n\n"
        
        "You have access to the current project directory and can edit files when granted permission. "
        "You are professional, thorough, and precise in your responses. "
        "When providing code, ensure it is complete, functional, and follows best practices. "
        "You can adapt to different programming styles and preferences.\n\n"
        
        f"STORED MEMORIES:\n{memory_summary}\n\n"
        f"RECENT CONVERSATION CONTEXT:\n{memory_context}\n\n"
        
        "TOOL CAPABILITIES:\n"
        "- You can view file information when the user uses ';share'\n"
        "- You can edit files when the user grants permission with ';edit'\n"
        "- You can only edit files within the current working directory\n"
        "- You have persistent memory - you can remember information across sessions\n"
        "- You can store important project information and context\n\n"
        
        "When you need to edit a file, respond with the file path and content in this format:\n"
        "FILE_EDIT: path/to/file\n"
        "```\n"
        "new file content here\n"
        "```\n\n"
        
        "You can also store information in memory using the format:\n"
        "MEMORY_STORE: key=value\n\n"
        
        "Be proactive in helping the user with their coding tasks. "
        "Ask clarifying questions when needed. "
        "Provide explanations alongside code when it would be helpful. "
        "Think step by step when solving complex problems."
    )

    # Initialize chat history if None
    if chat_history is None:
        chat_history = [{"role": "system", "content": system_instruction}]
    
    # Add user message to history
    chat_history.append({"role": "user", "content": processed_input})
    
    payload = {
        "model": CONFIG["model"],
        "messages": chat_history,
        "temperature": CONFIG["temperature"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=CONFIG["timeout"])
        
        if response.status_code != 200:
            safe_msg = response.text.replace('"', '\\"')
            error(f"API Error (Status {response.status_code}): {safe_msg}")
            
        data = response.json()
        assistant_response = data["choices"][0]["message"]["content"]
        
        # Process the response for file edits
        if new_permission:
            assistant_response = process_file_edits(assistant_response)
        
        # Process memory storage
        assistant_response = process_memory_storage(assistant_response)
        
        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": assistant_response})
        
        # Store in conversation memory
        memory.add_conversation("user", processed_input)
        memory.add_conversation("assistant", assistant_response)

        elapsed = time.time() - start_time
        info(f"Request completed in {elapsed:.2f}s")
        
        return assistant_response, chat_history, new_permission

    except requests.exceptions.Timeout:
        error(f"API request timed out after {CONFIG['timeout']} seconds. Use --timeout to increase.")
    except requests.exceptions.ConnectionError:
        error("Failed to connect to Groq API. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        error(f"API request failed: {str(e)}")
    except Exception as e:
        error(f"Unexpected error during chat: {str(e)}")


def process_file_edits(response: str) -> str:
    """Process file edit commands in the AI response."""
    # Look for FILE_EDIT: pattern
    pattern = r'FILE_EDIT:\s*([^\n]+)\n```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    for filepath, content in matches:
        filepath = filepath.strip()
        content = content.strip()
        
        if filepath and content:
            verbose_print(f"Nova is editing: {filepath}")
            
            if edit_file(filepath, content):
                verbose_print(f"Successfully updated {filepath}")
                
                # Replace the edit command in the response with a success message
                response = response.replace(
                    f"FILE_EDIT: {filepath}\n```\n{content}\n```",
                    f"[File '{filepath}' has been updated successfully]"
                )
            else:
                verbose_print(f"Failed to update {filepath} (file may be outside current directory)")
                
                response = response.replace(
                    f"FILE_EDIT: {filepath}\n```\n{content}\n```",
                    f"[Failed to update '{filepath}' - file may be outside current directory]"
                )
    
    return response


def process_memory_storage(response: str) -> str:
    """Process memory storage commands in the AI response."""
    pattern = r'MEMORY_STORE:\s*([^=]+)=([^\n]+)'
    matches = re.findall(pattern, response)
    
    for key, value in matches:
        key = key.strip()
        value = value.strip()
        
        if key and value:
            memory.store(key, value)
            verbose_print(f"Nova stored in memory: {key} = {value}")
            
            response = response.replace(
                f"MEMORY_STORE: {key}={value}",
                f"[Memory stored: {key}]"
            )
    
    return response


def execute_python_code(python_code: str, env_vars: Optional[Dict[str, str]] = None) -> int:
    """Run generated Python code in a fresh interpreter process."""
    if CONFIG["show_code"]:
        print("\n" + "="*50)
        print("Generated Python Code:")
        print("="*50)
        print(python_code)
        print("="*50 + "\n")
        
        if CONFIG["dry_run"]:
            info("Dry run - skipping execution")
            return 0
    
    if CONFIG["dry_run"]:
        return 0
    
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
        info(f"Environment variables set: {', '.join(env_vars.keys())}")
    
    interpreter = CONFIG["interpreter"]
    
    if CONFIG["interactive"]:
        cmd = [interpreter, "-i", "-c", python_code]
    else:
        cmd = [interpreter, "-c", python_code]
    
    try:
        info("Executing Python code...")
        completed = subprocess.run(cmd, env=env)
        if completed.returncode == 0:
            success("Execution completed successfully.")
        else:
            # Always show failures, even if show_execution_status is False
            if CONFIG["color"]:
                print(f"{RED}FAILED:{RESET} Execution completed with exit code: {completed.returncode}")
            else:
                print(f"FAILED: Execution completed with exit code: {completed.returncode}")
        return completed.returncode
    except FileNotFoundError:
        error(f"Python interpreter not found: {interpreter}")
    except subprocess.SubprocessError as e:
        error(f"Failed to execute Python code: {str(e)}")


def run_chat() -> None:
    """Start an interactive AI chat session with tools."""
    if CONFIG["color"]:
        print(f"{BOLD}{CYAN}NOVA CODING AGENT{RESET}")
        print(f"{CYAN}Your AI-powered development assistant by NovaCompile.{RESET}")
        print(f"{CYAN}Memory stored in: ~/.novacompile/compiler/memory/chat-memory.db{RESET}")
        print(f"{CYAN}Backups stored in: ~/.novacompile/compiler/backups/{RESET}")
        print(f"{CYAN}Special commands:{RESET}")
        print(f"{CYAN}  ;edit - Grant permission to edit files{RESET}")
        print(f"{CYAN}  ;share - Share all file information with Nova{RESET}")
        print(f"{CYAN}  :clear_memory - Clear AI's memory{RESET}")
        print(f"{CYAN}  Type 'exit' or 'quit' to leave.{RESET}")
        print(f"{CYAN}  Type ':settings' to open the settings menu.{RESET}\n")
    else:
        print("NOVA CODING AGENT")
        print("Your AI-powered development assistant by NovaCompile.")
        print("Memory stored in: ~/.novacompile/compiler/memory/chat-memory.db")
        print("Backups stored in: ~/.novacompile/compiler/backups/")
        print("Special commands:")
        print("  ;edit - Grant permission to edit files")
        print("  ;share - Share all file information with Nova")
        print("  :clear_memory - Clear AI's memory")
        print("  Type 'exit' or 'quit' to leave.")
        print("  Type ':settings' to open the settings menu.\n")
    
    chat_history = None
    permission_granted = False
    
    # Load previous conversation history
    recent_conv = memory.get_recent_conversations(5)
    if recent_conv:
        verbose_print(f"Loaded {len(recent_conv)} previous conversations from memory")
    
    while True:
        if CONFIG["color"]:
            prompt = f"{GREEN}you> {RESET}"
        else:
            prompt = "you> "

        try:
            user_input = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            print(f"{YELLOW}Use 'exit' or 'quit' to leave{RESET}" if CONFIG["color"] else "Use 'exit' or 'quit' to leave")
            continue

        stripped = user_input.strip()

        # Check for settings command
        if stripped == ":settings":
            run_settings()
            continue

        # Check for exit commands
        if stripped in {"exit", "quit", ":q", ":quit", ":exit", "leave"}:
            memory.close()
            verbose_print("Memory saved to ~/.novacompile/compiler/memory/chat-memory.db")
            if CONFIG["color"]:
                print(f"{CYAN}Goodbye!{RESET}")
            else:
                print("Goodbye!")
            break

        # Check for memory clear
        if stripped == ":clear_memory":
            memory.clear()
            verbose_print("Memory cleared successfully")
            continue

        if not stripped:
            continue
        
        # Send message to AI
        if CONFIG["color"]:
            print(f"{MAGENTA}nova> {RESET}", end="")
        else:
            print("nova> ", end="")
        
        response, chat_history, permission_granted = chat_with_ai(
            stripped, chat_history, permission_granted
        )
        
        # Format bold text in the response
        formatted_response = format_bold_text(response)
        print(formatted_response)
        print()  # Add blank line for readability


def run_shell() -> None:
    """Start an interactive shell that transpiles and executes each submitted block."""
    if CONFIG["color"]:
        print(f"{BOLD}{CYAN}NOVA SHELL{RESET}")
        print(f"{CYAN}Type your code and press Enter to run it.{RESET}")
        print(f"{CYAN}Use '\\' at the end of a line for multi-line input.{RESET}")
        print(f"{CYAN}Type 'exit' or 'quit' to leave.{RESET}")
        print(f"{CYAN}Type ':settings' to open the settings menu.{RESET}\n")
    else:
        print("Nova Shell")
        print("Type your code and press Enter to run it.")
        print("Use '\\' at the end of a line for multi-line input.")
        print("Type 'exit' or 'quit' to leave.")
        print("Type ':settings' to open the settings menu.\n")
    
    buffer: list[str] = []
    in_multiline = False

    while True:
        if in_multiline:
            if CONFIG["color"]:
                prompt = f"{YELLOW}...   {RESET}"
            else:
                prompt = "...   "
        else:
            if CONFIG["color"]:
                prompt = f"{GREEN}nova> {RESET}"
            else:
                prompt = "nova> "

        try:
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            if buffer:
                buffer.clear()
                in_multiline = False
                warn("Cancelled multi-line input")
            else:
                print(f"{YELLOW}Use 'exit' or 'quit' to leave{RESET}" if CONFIG["color"] else "Use 'exit' or 'quit' to leave")
            continue

        stripped = line.strip()

        # Check for settings command
        if not buffer and not in_multiline and stripped == ":settings":
            run_settings()
            continue

        # Check for exit commands
        if not buffer and not in_multiline and stripped in {"exit", "quit", ":q", ":quit", ":exit", "leave"}:
            break

        # Check if we're in multi-line mode or the line ends with \
        if line.endswith('\\'):
            # Remove the trailing \ and add to buffer
            buffer.append(line[:-1])
            in_multiline = True
            continue
        
        # If we have a buffer, add this line and execute
        if buffer:
            buffer.append(line)
            source = "\n".join(buffer).strip()
            buffer.clear()
            in_multiline = False
            
            if not source:
                continue
                
            python_code = transpile_to_python(source)
            execute_python_code(python_code)
            continue
        
        # Single line execution
        if not stripped:
            continue
            
        # Execute single line directly
        python_code = transpile_to_python(stripped)
        execute_python_code(python_code)


def run_settings() -> None:
    """Open the settings menu."""
    if CONFIG["quiet"]:
        return
    
    while True:
        if CONFIG["color"]:
            print(f"\n{BOLD}{MAGENTA}Settings{RESET}")
            print(f"{MAGENTA}========{RESET}")
            print(f"1. Clear cache")
            print(f"2. Show cache info")
            print(f"3. Clear AI memory")
            print(f"4. Show AI memory")
            print(f"5. Toggle execution status messages (currently: {GREEN if CONFIG['show_execution_status'] else RED}{'ON' if CONFIG['show_execution_status'] else 'OFF'}{RESET})")
            print(f"6. Back")
        else:
            print("\nSettings")
            print("========")
            print("1. Clear cache")
            print("2. Show cache info")
            print("3. Clear AI memory")
            print("4. Show AI memory")
            print(f"5. Toggle execution status messages (currently: {'ON' if CONFIG['show_execution_status'] else 'OFF'})")
            print("6. Back")
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == "1":
            clear_cache()
            break
        elif choice == "2":
            entries, size = get_cache_size()
            print(f"Cache contains {entries} entries ({size:,} bytes)")
            break
        elif choice == "3":
            memory.clear()
            if CONFIG["color"]:
                print(f"{GREEN}AI memory cleared successfully!{RESET}")
            else:
                print("AI memory cleared successfully!")
            break
        elif choice == "4":
            memories = memory.get_all()
            if memories:
                print("Stored memories:")
                for key, value in memories.items():
                    print(f"  {key}: {value}")
            else:
                print("No memories stored.")
            break
        elif choice == "5":
            CONFIG["show_execution_status"] = not CONFIG["show_execution_status"]
            status = "ON" if CONFIG["show_execution_status"] else "OFF"
            if CONFIG["color"]:
                print(f"{GREEN}Execution status messages turned {status}{RESET}")
            else:
                print(f"Execution status messages turned {status}")
            break
        elif choice == "6":
            break
        else:
            warn("Invalid option. Please try again.")


def run_single_string(code_string: str, use_cache: bool = True, env_vars: Optional[Dict[str, str]] = None) -> None:
    """Transpile and execute a single string of code."""
    python_code = transpile_to_python(code_string, use_cache=use_cache)
    execute_python_code(python_code, env_vars=env_vars)


def log_to_file(message: str, log_file: Optional[str] = None) -> None:
    """Log a message to a file if logging is enabled."""
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().isoformat()
                f.write(f"[{timestamp}] {message}\n")
        except IOError as e:
            warn(f"Failed to write to log file: {e}")


def parse_env_vars(env_strings: list[str]) -> Dict[str, str]:
    """Parse environment variables from a list of KEY=value strings."""
    env_vars = {}
    if env_strings:
        for env_str in env_strings:
            if "=" in env_str:
                key, value = env_str.split("=", 1)
                env_vars[key] = value
            else:
                warn(f"Invalid env format: {env_str} (expected KEY=value)")
    return env_vars


def read_from_stdin() -> str:
    """Read input from stdin."""
    return sys.stdin.read().strip()


def save_output(python_code: str, output_path: str) -> None:
    """Save the transpiled code to a file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(python_code)
        success(f"Saved transpiled code to: {output_path}")
    except IOError as e:
        error(f"Failed to save output to {output_path}: {e}")


def show_flags() -> None:
    """Display a list of all available flags with descriptions."""
    flags_info = """

NOVA - AVAILABLE FLAGS
---

HELP OPTIONS:
  -h, --help               Show this help message and exit
  --flags                  Display this list of all available flags with descriptions

MODE OPTIONS:
  -c, --chat               Launch Nova in chat mode (AI conversation with tools)
  --agent                  Launch Nova in agent mode (AI coding agent with tools)
  --shell                  Launch Nova in shell mode (transpile and execute code) [default]

CHAT/AGENT MODE TOOLS:
  ;edit                    Grant permission to edit files
  ;share                   Share all file information with Nova
  :clear_memory            Clear AI's memory
  :settings                Open settings menu

INPUT OPTIONS:
  source_file              Path to the .no file to transpile
  -s, --string TEXT        Transpile and execute a single string of code
  --stdin                  Read input from stdin instead of a file
  -o, --output FILE        Save generated code to a file instead of executing

BEHAVIOR OPTIONS:
  -n, --no-cache           Disable cache for this run
  --show-code              Show the generated Python code without executing it
  --dry-run                Show what would be transpiled without executing
  -v, --verbose            Show detailed output including API calls and cache info
  -q, --quiet              Suppress all non-error output
  --no-color               Disable colored output in terminal
  -i, --interactive        Drop into interactive mode after execution (like python -i)

MODEL AND PERFORMANCE:
  --model MODEL            Groq model to use (default: openai/gpt-oss-120b)
  -t, --temperature FLOAT  Temperature for the AI model (0.0-1.0, default: 0.1)
  --timeout SECONDS        API timeout in seconds (default: 30)

CACHE MANAGEMENT:
  --cache-size             Show size and number of entries in cache
  --cache-ttl SECONDS      Set cache expiration time in seconds (auto-clear old entries)
  --settings               Open interactive settings menu

ENVIRONMENT AND EXECUTION:
  --env KEY=value          Set environment variables (can be used multiple times)
  --interpreter PATH       Python interpreter to use for execution
  --log-file FILE          Log all transpilations and execution results to a file

SECURITY:
  --allow-imports LIST     Comma-separated list of allowed imports (not yet implemented)

EXAMPLES:
  nova script.no                          # Run a .no file
  nova -c                                 # Start chat mode
  nova --chat                             # Start chat mode (alternative)
  nova --agent                            # Start agent mode (same as chat)
  nova -c -v                              # Start chat with verbose output
  nova -s "print('Hello')"                # Run a single string
  nova --settings                         # Open settings menu
  nova script.no -v --show-code           # Verbose mode with code preview
  nova script.no --env API_KEY=123        # With environment variables
  echo "print('hi')" | nova --stdin       # Pipe input from stdin
"""
    print(flags_info)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run .no files via cloud-based AI transpilation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    # Help options
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("--flags", action="store_true", help="Display list of all available flags with descriptions")
    
    # Mode options
    parser.add_argument("-c", "--chat", action="store_true", help="Launch Nova in chat mode (AI conversation with tools)")
    parser.add_argument("--agent", action="store_true", help="Launch Nova in agent mode (AI coding agent with tools)")
    parser.add_argument("--shell", action="store_true", help="Launch Nova in shell mode (transpile and execute code)")
    
    # Input options
    parser.add_argument("source_file", nargs="?", help="Path to the .no file")
    parser.add_argument("-s", "--string", type=str, help="Transpile and execute a single string of code")
    parser.add_argument("--stdin", action="store_true", help="Read input from stdin instead of a file")
    parser.add_argument("-o", "--output", type=str, help="Save generated code to a specific file instead of executing")
    
    # Behavior options
    parser.add_argument("-n", "--no-cache", action="store_true", help="Disable cache for this run")
    parser.add_argument("--show-code", action="store_true", help="Show the generated Python code without executing it")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be transpiled without executing")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output including API calls and cache info")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all non-error output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("-i", "--interactive", action="store_true", help="Drop into interactive mode after execution (like python -i)")
    
    # Model and performance
    parser.add_argument("--model", type=str, default="openai/gpt-oss-120b", 
                       help="Groq model to use (default: openai/gpt-oss-120b)")
    parser.add_argument("-t", "--temperature", type=float, default=0.1, 
                       help="Temperature for the AI model (0.0-1.0, default: 0.1)")
    parser.add_argument("--timeout", type=int, default=30, 
                       help="API timeout in seconds (default: 30)")
    
    # Cache management
    parser.add_argument("--cache-size", action="store_true", help="Show size and number of entries in cache")
    parser.add_argument("--cache-ttl", type=int, help="Cache expiration time in seconds (auto-clear old entries)")
    parser.add_argument("--settings", action="store_true", help="Open settings menu")
    
    # Environment and execution
    parser.add_argument("--env", action="append", help="Set environment variables (KEY=value format, can be used multiple times)")
    parser.add_argument("--interpreter", type=str, default=sys.executable, 
                       help="Python interpreter to use for execution")
    
    # Logging
    parser.add_argument("--log-file", type=str, help="Log all transpilations and execution results to a file")
    
    # Security
    parser.add_argument("--allow-imports", type=str, help="Comma-separated list of allowed imports (not implemented yet)")
    
    args = parser.parse_args()
    
    # Handle help and flags
    if args.help:
        parser.print_help()
        print("\nFor a complete list of all available flags with descriptions, use: nova --flags")
        return
    
    if args.flags:
        show_flags()
        return
    
    # Update global config
    CONFIG.update({
        "verbose": args.verbose,
        "quiet": args.quiet,
        "color": not args.no_color,
        "model": args.model,
        "temperature": args.temperature,
        "timeout": args.timeout,
        "interpreter": args.interpreter,
        "show_code": args.show_code or args.dry_run,
        "dry_run": args.dry_run,
        "interactive": args.interactive,
        "cache_ttl": args.cache_ttl,
    })
    
    # Handle cache size display
    if args.cache_size:
        entries, size = get_cache_size()
        print(f"Cache contains {entries} entries ({size:,} bytes)")
        return
    
    # Handle settings
    if args.settings:
        run_settings()
        return
    
    # Handle chat/agent mode - this must be checked before other input methods
    if args.chat or args.agent:
        run_chat()
        return
    
    # Handle stdin
    if args.stdin:
        source = read_from_stdin()
        if not source:
            error("No input from stdin")
        python_code = transpile_to_python(source, use_cache=not args.no_cache)
        if args.output:
            save_output(python_code, args.output)
        else:
            execute_python_code(python_code, env_vars=parse_env_vars(args.env))
        return
    
    # Handle single string execution
    if args.string is not None:
        run_single_string(args.string, use_cache=not args.no_cache, env_vars=parse_env_vars(args.env))
        return
    
    # Handle file execution
    if args.source_file is None:
        run_shell()
        return
    
    if not args.source_file.endswith(".no"):
        error(f"Input file '{args.source_file}' must have a .no extension.")
    
    target_path = os.path.abspath(args.source_file)
    try:
        with open(target_path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except FileNotFoundError:
        error(f"File not found at {target_path}")
    except PermissionError:
        error(f"Permission denied: Cannot read {target_path}")
    except IOError as e:
        error(f"Failed to read file {target_path}: {e}")
    
    if not source.strip():
        error(f"File {args.source_file} is empty")
    
    python_code = transpile_to_python(source, use_cache=not args.no_cache)
    
    if args.log_file:
        log_to_file(f"Transpiled {args.source_file} - Code length: {len(python_code)}", args.log_file)
    
    if args.output:
        save_output(python_code, args.output)
    else:
        execute_python_code(python_code, env_vars=parse_env_vars(args.env))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        if CONFIG["color"]:
            print(f"{YELLOW}Interrupted by user{RESET}", file=sys.stderr)
        else:
            print("Interrupted by user", file=sys.stderr)
        sys.exit(130)
