"""Best-effort AI-style syntax-correcting compiler/transpiler."""

from __future__ import annotations

import argparse
import difflib
import re
from typing import Iterable, List, Tuple


SUPPORTED_LANGUAGES = ("python", "javascript", "typescript", "go", "rust", "java", "cpp")


Statement = Tuple[str, str, str]


def list_languages() -> List[str]:
    return list(SUPPORTED_LANGUAGES)


def _is_print_like(token: str) -> bool:
    token = token.strip().lower()
    if token == "print":
        return True
    return bool(difflib.get_close_matches(token, ["print"], n=1, cutoff=0.75))


def _literalize(expr: str) -> str:
    expr = expr.strip()
    if not expr:
        return '""'
    if expr.startswith(("'", '"')) and expr.endswith(("'", '"')) and len(expr) >= 2:
        return expr
    if re.fullmatch(r"-?\d+(\.\d+)?", expr):
        return expr
    if expr in {"True", "False", "true", "false", "None", "null"}:
        return expr
    if any(ch in expr for ch in ("+", "-", "*", "/", "(", ")", "[", "]", "{", "}", ".")):
        return expr
    if " " in expr:
        return f'"{expr}"'
    return expr


def _extract_statements(source: str) -> List[Statement]:
    statements: List[Statement] = []
    raw_lines = [part.strip() for line in source.splitlines() for part in line.split(";")]
    for line in raw_lines:
        if not line:
            continue

        first_word = re.match(r"([A-Za-z_]+)", line)
        if first_word and _is_print_like(first_word.group(1)):
            expr = line[first_word.end() :].strip(" :()")
            statements.append(("print", _literalize(expr), ""))
            continue

        assign = re.match(
            r"^(?:let|var|const)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]{1,3}\s*(.+)$",
            line,
            re.IGNORECASE,
        )
        if assign:
            statements.append(("assign", assign.group(1), _literalize(assign.group(2))))
            continue

        statements.append(("print", _literalize(line), ""))

    return statements or [("print", '"<empty input>"', "")]


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
    statements = _extract_statements(source)
    body = _emit_body(statements, language)
    return _wrap_program(body, language)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI syntax-correcting compiler/transpiler")
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
        with open(args.source_file, "r", encoding="utf-8") as handle:
            source = handle.read()
    else:
        parser.error("Provide source_file or --text")

    print(compile_code(source, args.language))


if __name__ == "__main__":
    main()
