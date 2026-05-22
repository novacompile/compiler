"""AI transpiler and executor for .noco files using Groq Cloud."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import requests


def transpile_to_python(source: str) -> str:
    """Sends a raw HTTP POST request to Groq to completely bypass OpenAI SDK routing anomalies."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")

    url = "https://groq.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_instruction = (
        "You are an expert transpiler. Analyze the provided input text, unstructured instructions, or pseudo-code.\n"
        "Infer the core programming logic and intent, then rewrite it entirely into a functional, syntactically correct Python script.\n\n"
        "Ensure all formatting, logic flows, variables, and outputs map accurately to valid Python code.\n"
        "Do not include any Markdown syntax, code block formatting (like ```python), chat preamble, or explanations.\n"
        "Output ONLY raw executable Python text. If you must use quotes, ensure they are properly closed."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": source}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Catch and surface any exact proxy/server status errors clearly
        if response.status_code != 200:
            return f'print("API communication failed with Status {response.status_code}: {response.text}")'
            
        data = response.json()
        raw_python = data["choices"][0]["message"]["content"]
        
        # Clean any accidental markdown code fences if the model adds them anyway
        if raw_python.startswith("```"):
            lines = raw_python.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_python = "\n".join(lines)
            
        return raw_python.strip()

    except Exception as e:
        return f'print("Error connecting directly to Groq endpoint: {str(e)}")'


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run .noco files via direct Groq API connections"
    )
    parser.add_argument("source_file", help="Path to the .noco file")
    args = parser.parse_args()

    if not args.source_file.endswith(".noco"):
        print("Error: Input file must have a .noco extension.", file=sys.stderr)
        sys.exit(1)

    target_path = os.path.abspath(args.source_file)
    try:
        with open(target_path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except FileNotFoundError:
        print(f"Error: File not found at {target_path}", file=sys.stderr)
        sys.exit(1)

    python_code = transpile_to_python(source)

    # Directly execute the clean raw Python script string delivered by the endpoint
    subprocess.run([sys.executable, "-c", python_code])


if __name__ == "__main__":
    main()
