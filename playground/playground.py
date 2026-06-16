"""Interactive CLI Playground for AI transpiler and executor using Groq Cloud."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import requests


def get_input(prompt: str, default: str) -> str:
    """Helper to get user input with a fallback default value."""
    user_val = input(f"{prompt} [{default}]: ").strip()
    return user_val if user_val else default


def transpile_to_python(
    source: str, 
    api_key: str, 
    model: str, 
    temperature: float, 
    system_instruction: str
) -> tuple[str, dict]:
    """Sends custom configuration to Groq Cloud and returns Python code and payload."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": source}
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            safe_msg = response.text.replace('"', '\\"')
            return f'print("API Error (Status {response.status_code}): {safe_msg}")', payload
            
        data = response.json()
        raw_python = data["choices"][0]["message"]["content"]
        
        # Strip potential markdown code blocks if the model ignores system prompts
        clean_lines = []
        for line in raw_python.splitlines():
            if not line.strip().startswith("```"):
                clean_lines.append(line)
        raw_python = "\n".join(clean_lines)
            
        return raw_python.strip(), payload

    except Exception as e:
        return f'print("Error connecting to Groq API endpoint: {str(e)}")', payload


def execute_python_code(python_code: str) -> subprocess.CompletedProcess:
    """Run generated Python code in a isolated subprocess and capture outcomes."""
    return subprocess.run(
        [sys.executable, "-c", python_code],
        capture_output=True,
        text=True
    )


def main() -> None:
    print("=" * 60)
    print("🚀 NOVA AI TRANSPILER CLI PLAYGROUND WIZARD")
    print("=" * 60)

    # 1. API Key setup
    env_key = os.environ.get("GROQ_API_KEY", "")
    if env_key:
        api_key = get_input("Enter Groq API Key", default="FOUND IN ENVIRONMENT")
        if api_key == "FOUND IN ENVIRONMENT":
            api_key = env_key
    else:
        api_key = input("Enter Groq API Key: ").strip()
        if not api_key:
            print("Error: API Key is strictly required.")
            sys.exit(1)

    # 2. Select Model
    print("\nAvailable Models:")
    print("  1) llama3-8b-8192")
    print("  2) llama3-70b-8192")
    print("  3) mixtral-8x7b-32768")
    print("  4) gemma2-9b-it")
    print("  5) openai/gpt-oss-120b")
    model_choice = get_input("Select Model Number or type custom ID", default="1")
    
    model_map = {
        "1": "llama3-8b-8192",
        "2": "llama3-70b-8192",
        "3": "mixtral-8x7b-32768",
        "4": "gemma2-9b-it",
        "5": "openai/gpt-oss-120b"
    }
    selected_model = model_map.get(model_choice, model_choice)

    # 3. Configure Temperature
    try:
        temp_str = get_input("Enter Temperature (0.0 to 2.0)", default="0.1")
        selected_temp = float(temp_str)
    except ValueError:
        print("Invalid number format. Defaulting to 0.1")
        selected_temp = 0.1

    # 4. Customize System Prompt
    default_instruction = (
        "You are an expert transpiler. Analyze the provided input text, unstructured instructions, or pseudo-code.\n"
        "Infer the core programming logic and intent, then rewrite it entirely into a functional, syntactically correct Python script.\n"
        "Output ONLY raw executable Python text without Markdown or explanations."
    )
    print("\n--- System Prompt Options ---")
    print("  1) Keep original strict transpiler rules")
    print("  2) Write custom system prompt inline")
    prompt_choice = get_input("Choose system prompt mode", default="1")
    
    if prompt_choice == "2":
        print("Enter your custom system instructions below (Press Enter on a completely empty line to finish):")
        custom_lines = []
        while True:
            line = input()
            if not line:
                break
            custom_lines.append(line)
        selected_instruction = "\n".join(custom_lines) if custom_lines else default_instruction
    else:
        selected_instruction = default_instruction

    # 5. File Path input
    print("\n--- File Selection ---")
    file_path = input("Enter path to your file (e.g. script.no): ").strip()
    if not file_path:
        print("Error: File path cannot be empty.")
        sys.exit(1)

    target_path = os.path.abspath(file_path)
    try:
        with open(target_path, "r", encoding="utf-8") as handle:
            source_data = handle.read()
    except FileNotFoundError:
        print(f"Error: File not found at {target_path}")
        sys.exit(1)

    # 6. Execute Sandbox Pipeline
    print("\n" + "~" * 60)
    print("⏳ Contacting Groq Cloud endpoint with customized payload...")
    print("~" * 60)

    generated_code, network_payload = transpile_to_python(
        source=source_data,
        api_key=api_key,
        model=selected_model,
        temperature=selected_temp,
        system_instruction=selected_instruction
    )

    # 7. Print Output Report Panel
    print("\n🌐 [INSPECT PAYLOAD SENT]")
    print(json.dumps(network_payload, indent=2))

    print("\n🤖 [GENERATED PYTHON CODE]")
    print("-" * 40)
    print(generated_code)
    print("-" * 40)

    print("\n🖥️ [EXECUTION RESULTS]")
    res = execute_python_code(generated_code)
    print(f"Process Exit Status: {res.returncode}")
    
    if res.stdout:
        print(f"\n--- Console Output (STDOUT) ---\n{res.stdout}")
    if res.stderr:
        print(f"\n--- Error Stream (STDERR) ---\n{res.stderr}")


if __name__ == "__main__":
    main()
