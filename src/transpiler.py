"""Local Rule-Based Transpiler and Executor for .noco files."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def transpile_locally(source: str) -> str:
    """Parses rules locally on the server without triggering academic network blocks."""
    lines = source.splitlines()
    python_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Look for custom variable declaration syntax: "x is 5" or "x make 10"
        if " is " in stripped:
            left, right = stripped.split(" is ", 1)
            python_lines.append(f"{left.strip()} = {right.strip()}")
            continue
        elif " make " in stripped:
            left, right = stripped.split(" make ", 1)
            python_lines.append(f"{left.strip()} = {right.strip()}")
            continue
        elif " assign " in stripped:
            left, right = stripped.split(" assign ", 1)
            python_lines.append(f"{left.strip()} = {right.strip()}")
            continue

        # Look for custom loop structures: "loop 3 times"
        if stripped.startswith("loop ") and " times" in stripped:
            try:
                times = stripped.replace("loop ", "").replace(" times", "").strip()
                python_lines.append(f"for _ in range({times}):")
            except ValueError:
                pass
            continue

        # Check for generic indents or variable logic adjustments
        if stripped.startswith("add ") and " to " in stripped:
            # Format: add 2 to x -> x += 2
            content = stripped.replace("add ", "")
            value, var_name = content.split(" to ", 1)
            python_lines.append(f"  {var_name.strip()} += {value.strip()}")
            continue

        # Check for variable outputs or terminal display calls
        if stripped.startswith("shw ") or stripped.startswith("prnt "):
            var_target = stripped.split(" ", 1)[1]
            python_lines.append(f"print({var_target.strip()})")
            continue
        elif stripped.startswith("display text "):
            # Custom handler for compound text/variable outputs
            content = stripped.replace("display text ", "")
            if " and then show " in content:
                text_part, var_part = content.split(" and then show ", 1)
                python_lines.append(f"  print({text_part.strip()} + str({var_part.strip()}))")
            else:
                python_lines.append(f"print({content.strip()})")
            continue

        # Fallback tracking for pre-formated standard patterns
        python_lines.append(stripped)

    return "\n".join(python_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run local network-free .noco syntax compilers"
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

    # Compile the file rules strictly without making web calls
    python_code = transpile_locally(source)

    # Safely execute the resulting script logic mapping string
    subprocess.run([sys.executable, "-c", python_code])


if __name__ == "__main__":
    main()
