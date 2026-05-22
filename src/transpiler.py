"""AI transpiler and executor for .noco files using Groq Cloud."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from openai import OpenAI
from pydantic import BaseModel, Field

class TranspiledProgram(BaseModel):
    python_code: str = Field(
        description="The complete, working, executable Python script rewritten from the input text."
    )

def transpile_to_python(source: str) -> str:
    """Uses Groq Tool Calling to reliably rewrite text into functional Python code."""
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("Please set the GROQ_API_KEY environment variable.")

    client = OpenAI(
        base_url="https://groq.com",
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    prompt = f"""
    Analyze the following input text, unstructured instructions, or pseudo-code.
    Infer the core programming logic and intent, then rewrite it entirely into a functional, syntactically correct Python script.
    
    Ensure all formatting, logic flows, variables, and outputs map accurately to valid Python code.
    Do not include any Markdown syntax, chat preamble, or explanations.

    Input to Convert:
    \"\"\"
    {source}
    \"\"\"
    """

    tools = [
        {
            "type": "function",
            "function": {
                "name": "submit_python_code",
                "description": "Submits the final compiled and working Python code.",
                "parameters": TranspiledProgram.model_json_schema()
            }
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "submit_python_code"}},
        temperature=0.1,
    )

    try:
        tool_call = response.choices[0].message.tool_calls[0]
        json_string = tool_call.function.arguments
        parsed_data = TranspiledProgram.model_validate_json(json_string)
        return parsed_data.python_code
    except Exception:
        return 'print("Error: The AI was unable to transpile this file into valid Python.")'

def main() -> None:
    parser = argparse.ArgumentParser(description="Run .noco files via Python transpilation")
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

    # Directly run the generated Python script
    subprocess.run([sys.executable, "-c", python_code])

if __name__ == "__main__":
    main()
