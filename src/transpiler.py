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
    """Uses Groq Structured Outputs to reliably rewrite text into functional Python code."""
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("Please set the GROQ_API_KEY environment variable.")

    client = OpenAI(
        base_url="https://groq.com",
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    system_instruction = f"""
    You are an expert transpiler. Analyze the provided input text, unstructured instructions, or pseudo-code.
    Infer the core programming logic and intent, then rewrite it entirely into a functional, syntactically correct Python script.
    
    Ensure all formatting, logic flows, variables, and outputs map accurately to valid Python code.
    Do not include any Markdown syntax, chat preamble, backticks, or explanations.
    
    You MUST respond with a JSON object that matches this schema:
    {TranspiledProgram.model_json_schema()}
    """

    # Using standard chat completion with json_object format to fix the 405 error
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": source},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    try:
        json_string = response.choices[0].message.content
        parsed_data = TranspiledProgram.model_validate_json(json_string)
        return parsed_data.python_code
    except Exception as e:
        return f'print("Error parsing the AI response. Details: {str(e)}")'


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run .noco files via Python transpilation"
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

    # Directly run the generated Python script
    subprocess.run([sys.executable, "-c", python_code])


if __name__ == "__main__":
    main()
