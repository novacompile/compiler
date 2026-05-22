"""AI syntax-correcting compiler/transpiler using Groq Cloud (Located in src/)."""

from __future__ import annotations

import argparse
import os
from typing import Iterable, List, Literal, Tuple
from openai import OpenAI
from pydantic import BaseModel, Field

SUPPORTED_LANGUAGES = ("python", "javascript", "typescript", "go", "rust", "java", "cpp")

Statement = Tuple[str, str, str]


class ParsedStatement(BaseModel):
    kind: Literal["assign", "print"] = Field(
        description="The intent of the line. 'assign' for variables, 'print' for outputs."
    )
    left: str = Field(
        description="The variable name for an assignment, or the literal value/variable to print."
    )
    right: str = Field(
        description="The value being assigned to a variable. Leave completely empty for print statements."
    )


class ProgramAST(BaseModel):
    statements: List[ParsedStatement] = Field(
        description="The sequential list of statements extracted from the input text."
    )


def list_languages() -> List[str]:
    return list(SUPPORTED_LANGUAGES)


def _extract_statements_ml(source: str) -> List[Statement]:
    """Uses Groq to understand user intent and parse messy text into clean structured data structures."""
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("Please set the GROQ_API_KEY environment variable.")

    client = OpenAI(
        base_url="https://groq.com",
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    prompt = f"""
    You are the parsing frontend of a compiler. Analyze the following poorly formatted, 
    broken, or pseudo-code text line by line. Infer the user's true intent.
    
    Extract every variable assignment or print operation. 
    Fix typos in keywords (e.g., 'prnt', 'shw', 'display' should become 'print').
    Ensure values are formatted correctly as standard programming literals (e.g., wrap raw text strings in quotes).

    Input Code to Parse:
    \"\"\"
    {source}
    \"\"\"
    """

    response = client.beta.chat.completions.parse(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format=ProgramAST,
        temperature=0.1,
    )

    try:
        parsed_data = response.choices.message.parsed
        if not parsed_data:
            return [("print", '"<Failed to parse input via Groq>"', "")]
        
        statements: List[Statement] = []
        for stmt in parsed_data.statements:
            statements.append((stmt.kind, stmt.left, stmt.right))
        return statements
    except Exception:
        return [("print", '"<Structural parsing exception occurred>"', "")]


def _emit_body(statements: Iterable[Statement], language: str) -> List[str]:
    lines: List[str] = []
    for kind, left, right in statements:
        if kind == "assign":
            if language == "python":
                lines.append(f"{left} = {right}")
            elif language in {"javascript", "typescript"}:
                lines.append(f"let {left} = {right};")
            elif language == "go":
                lines.append(f"{left} := {right}")
            elif language == "rust":
                lines.append(f"let mut {left} = {right};")
            elif language == "java":
                lines.append(f"var {left} = {right};")
            elif language == "cpp":
                lines.append(f"auto {left} = {right};")
        else:
            if language == "python":
                lines.append(f"print({left})")
            elif language in {"javascript", "typescript"}:
                lines.append(f"console.log({left});")
            elif language == "go":
                lines.append(f"fmt.Println({left})")
            elif language == "rust":
                lines.append(f'println!("{{:?}}", {left});')
            elif language == "java":
                lines.append(f"System.out.println({left});")
            elif language == "cpp":
                lines.append(f"std::cout << {left} << std::endl;")
    return lines


def _wrap_program(body: List[str], language: str) -> str:
    if language == "go":
        return "package main\n\nimport \"fmt\"\n\nfunc main() {\n    " + "\n    ".join(body) + "\n}"
    if language == "rust":
        return "fn main() {\n    " + "\n    ".join(body) + "\n}"
    if language == "java":
        return (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        "
            + "\n        ".join(body)
            + "\n    }\n}"
        )
    if language == "cpp":
        return (
            "#include <iostream>\n\nint main() {\n    "
            + "\n    ".join(body)
            + "\n    return 0;\n}"
        )
    return "\n".join(body)


def compile_code(source: str, language: str) -> str:
    language = language.lower().strip()
    if language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES)
        raise ValueError(f"Unsupported language '{language}'. Supported languages: {supported}")
    
    statements = _extract_statements_ml(source)
    body = _emit_body(statements, language)
    return _wrap_program(body, language)


def main() -> None:
    parser = argparse.ArgumentParser(description="Groq-powered syntax-correcting compiler")
    parser.add_argument("source_file", nargs="?", help="Optional source file path")
    parser.add_argument("--text", help="Inline source text to compile")
    parser.add_argument("-l", "--language", help="Target language")
    parser.add_argument("--list-languages", action="store_true", help="List supported languages")
    args = parser.parse_args()

    if args.list_languages:
        print("\n".join(list_languages()))
        return

    if not args.language:
        parser.error("--language is required unless --list-languages is used")

    if args.text is not None:
        source = args.text
    elif args.source_file:
        # Use absolute path checking so it resolves correctly even when called from the root folder
        target_path = os.path.abspath(args.source_file)
        with open(target_path, "r", encoding="utf-8") as handle:
            source = handle.read()
    else:
        parser.error("Provide source_file or --text")

    print(compile_code(source, args.language))


if __name__ == "__main__":
    main()
