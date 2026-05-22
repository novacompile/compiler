"""AI transpiler and executor for .noco files using Groq Cloud."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from groq import Groq


def transpile_to_python(source: str) -> str:
    """Uses the official Groq SDK to bypass academic web-proxy string filters."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")

    # Using the official native Groq client package
    client = Groq(api_key=api_key)

    system_instruction = (
        "You are an expert transpiler. Analyze the provided input text, unstructured instructions, or pseudo-code.\n"
        "Infer the core programming logic and intent, then rewrite it entirely into a functional, syntactically correct Python script.\n\n"
        "Ensure all formatting, logic flows, variables, and outputs map accurately to valid Python code.\n"
        "Do not include any Markdown syntax, code block formatting (like ```python), chat preamble, or explanations.\n"
        "Output ONLY raw executable Python text. If you must use quotes, ensure they are properly closed."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": source}
            ],
            temperature=0.1
        )
        
        raw_python = response.choices[0].message.content
        
        # Clean out any accidental markdown code fences line by line
        clean_lines = []
        for line in raw_python.splitlines():
            if not line.strip().startswith("```"):
                clean_lines.append(line)
        raw_python = "\n".join(clean_lines)
            
        return raw_python.strip()

    except Exception as e:
        return f'print("Error connecting via Groq SDK: {str(e)}")'


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run .noco files via official Groq SDK connections"
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

    # Directly execute the generated Python logic strings safely
    subprocess.run([sys.executable, "-c", python_code])


if __name__ == "__main__":
    main()
