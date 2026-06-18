"""AI transpiler and executor for .no files using Groq Cloud."""

from __future__ import annotations
from pathlib import Path

import argparse
import hashlib
import json
import os
import subprocess
import sys
import requests


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
    print("Cache cleared successfully.")


def get_cache_key(prompt: str) -> str:
    """Generate a cache key from the prompt."""
    # Use SHA-256 hash of the prompt as cache key
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()


def transpile_to_python(source: str, use_cache: bool = True) -> str:
    """Sends a raw HTTP POST request using an active production Groq model ID."""
    src_dir = Path(__file__).resolve().parent
    file_path = src_dir.parent / "key" / "raw.txt"
    with open(file_path, "r") as file:
        api_key = file.read().strip()
        if not api_key:
            raise ValueError("Please run the setup script (setup.sh) to add API key.")

    # Check cache first
    if use_cache:
        cache = load_cache()
        cache_key = get_cache_key(source)
        if cache_key in cache:
            return cache[cache_key]

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
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": source}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            safe_msg = response.text.replace('"', '\\"')
            return f'print("API Error (Status {response.status_code}): {safe_msg}")'
            
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
            cache[cache_key] = result
            save_cache(cache)

        return result

    except Exception as e:
        return f'print("Error connecting to Groq API endpoint: {str(e)}")'


def execute_python_code(python_code: str) -> int:
    """Run generated Python code in a fresh interpreter process."""
    completed = subprocess.run([sys.executable, "-c", python_code])
    return completed.returncode


def run_shell() -> None:
    """Start an interactive shell that transpiles and executes each submitted block."""
    print("Nova Shell\nSubmit a block, then press Enter on an empty line to run it.")
    print("Type exit or quit to leave.")

    buffer: list[str] = []

    while True:
        prompt = "nova> " if not buffer else "...   "

        try:
            line = input(prompt)
        except EOFError:
            print()
            break

        stripped = line.strip()

        if not buffer and stripped in {"exit", "quit", ":q", ":quit", ":exit", "leave"}:
            break

        if not stripped:
            if not buffer:
                continue

            source = "\n".join(buffer).strip()
            buffer.clear()

            if not source:
                continue

            python_code = transpile_to_python(source)
            execute_python_code(python_code)
            continue

        buffer.append(line)


def run_settings() -> None:
    """Open the settings menu."""
    print("Settings")
    print("========")
    print("1. Clear cache")
    print("2. Back")
    
    while True:
        choice = input("\nSelect an option (1-2): ").strip()
        if choice == "1":
            clear_cache()
            break
        elif choice == "2":
            break
        else:
            print("Invalid option. Please try again.")


def run_single_string(code_string: str, use_cache: bool = True) -> None:
    """Transpile and execute a single string of code."""
    python_code = transpile_to_python(code_string, use_cache=use_cache)
    execute_python_code(python_code)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run .no files via cloud-based AI transpilation"
    )
    parser.add_argument("source_file", nargs="?", help="Path to the .no file")
    parser.add_argument("--settings", action="store_true", help="Open settings menu")
    parser.add_argument("-s", "--string", type=str, help="Transpile and execute a single string of code")
    parser.add_argument("-n", "--no-cache", action="store_true", help="Disable cache for this run")
    args = parser.parse_args()

    # Handle settings
    if args.settings:
        run_settings()
        return

    # Handle single string execution
    if args.string is not None:
        run_single_string(args.string, use_cache=not args.no_cache)
        return

    # Handle file execution
    if args.source_file is None:
        run_shell()
        return

    if not args.source_file.endswith(".no"):
        print("Error: Input file must have a .no extension.", file=sys.stderr)
        sys.exit(1)

    target_path = os.path.abspath(args.source_file)
    try:
        with open(target_path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except FileNotFoundError:
        print(f"Error: File not found at {target_path}", file=sys.stderr)
        sys.exit(1)

    python_code = transpile_to_python(source, use_cache=not args.no_cache)
    execute_python_code(python_code)


if __name__ == "__main__":
    main()
