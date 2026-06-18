# Nova - Transpiler Flags and Usage Guide

Nova is an AI-powered transpiler that converts natural language, pseudo-code, or unstructured instructions into executable Python code using Groq Cloud's AI models.

## Quick Start

```bash
# Run a .no file
nova my_script.no

# Interactive shell
nova

# Single string execution
nova -s "print('Hello World')"

# Open settings menu
nova --settings

# See all flags
nova --flags

# Get help
nova --help
```

## Command-Line Flags

### Help Options

| Flag | Description | Example |
|------|-------------|---------|
| `-h, --help` | Show the help message and exit | `nova --help` |
| `--flags` | Display a complete list of all available flags with descriptions | `nova --flags` |

### Input Options

| Flag | Description | Example |
|------|-------------|---------|
| `source_file` | Path to the `.no` file to transpile | `nova script.no` |
| `-s, --string` | Transpile and execute a single string of code | `nova -s "print(random_int(1,10))"` |
| `--stdin` | Read input from stdin instead of a file | `echo "print hello" | nova --stdin` |
| `-o, --output` | Save generated code to a file instead of executing | `nova script.no -o output.py` |

### Behavior Options

| Flag | Description | Example |
|------|-------------|---------|
| `-n, --no-cache` | Disable cache for this run | `nova script.no -n` |
| `--show-code` | Show the generated Python code as well as executing it | `nova script.no --show-code` |
| `--dry-run` | Show what would be transpiled without executing | `nova script.no --dry-run` |
| `-v, --verbose` | Show detailed output including API calls and cache info | `nova -s "print('hi')" -v` |
| `-q, --quiet` | Suppress all non-error output | `nova script.no -q` |
| `--no-color` | Disable colored output in terminal | `nova script.no --no-color` |
| `-i, --interactive` | Drop into interactive mode after execution (like `python -i`) | `nova script.no -i` |

### Model and Performance

| Flag | Description | Example |
|------|-------------|---------|
| `--model` | Groq model to use (default: openai/gpt-oss-120b) | `nova script.no --model llama-3.3-70b-versatile` |
| `-t, --temperature` | Temperature for the AI model (0.0-1.0, default: 0.1) | `nova script.no -t 0.5` |
| `--timeout` | API timeout in seconds (default: 30) | `nova script.no --timeout 60` |

### Cache Management

| Flag | Description | Example |
|------|-------------|---------|
| `--cache-size` | Show size and number of entries in cache | `nova --cache-size` |
| `--cache-ttl` | Set cache expiration time in seconds (auto-clear old entries) | `nova script.no --cache-ttl 3600` |
| `--settings` | Open interactive settings menu | `nova --settings` |

### Environment and Execution

| Flag | Description | Example |
|------|-------------|---------|
| `--env` | Set environment variables (can be used multiple times) | `nova script.no --env API_KEY=123 --env DEBUG=true` |
| `--interpreter` | Python interpreter to use for execution | `nova script.no --interpreter python3.11` |
| `--log-file` | Log all transpilations and execution results to a file | `nova script.no --log-file transpile.log` |

### Security

| Flag | Description | Example |
|------|-------------|---------|
| `--allow-imports` | Comma-separated list of allowed imports (not yet implemented) | `nova script.no --allow-imports=os,sys,json` |

## Usage Examples

### Basic File Transpilation
```bash
# Run a .no file
nova script.no

# Run with verbose output
nova script.no -v

# Show code without executing
nova script.no --show-code
```

### Working with Strings
```bash
# Simple string execution
nova -s "print('Hello World')"

# Generate a random number
nova -s "print(random_number(1, 9))"

# Multi-line string (use quotes)
nova -s "for i in range(5):\n    print(i)"
```

### Cache Management
```bash
# Check cache size
nova --cache-size

# Clear cache via settings
nova --settings

# Set cache TTL to 1 hour
nova script.no --cache-ttl 3600

# Bypass cache
nova script.no -n
```

### Environment Variables
```bash
# Set environment variables
nova script.no --env API_KEY=abc123 --env DEBUG=true

# Use with string execution
nova -s "import os; print(os.environ.get('API_KEY'))" --env API_KEY=test123
```

### Output Options
```bash
# Save transpiled code to a file
nova script.no -o generated.py

# Pipe input from stdin
echo "print('Hello from stdin')" | nova --stdin

# Save stdin output to file
echo "print('Hello')" | nova --stdin -o output.py
```

### Advanced Scenarios
```bash
# Verbose mode with model selection and custom temperature
nova script.no -v --model llama-3.3-70b-versatile -t 0.2

# Interactive mode with environment variables
nova script.no -i --env DEBUG=true

# Dry run to preview code
nova script.no --dry-run

# Log all transpilations
nova script.no --log-file my_log.log

# Set custom Python interpreter
nova script.no --interpreter python3.11

# Get quick help
nova --help

# List all flags
nova --flags
```

## Interactive Shell Commands

When running `nova` without arguments, you enter the interactive shell:

```bash
nova
```

In the shell:
- Type your code or instructions (multi-line supported)
- Press Enter on an empty line to transpile and execute
- Type `exit`, `quit`, `:q`, `:quit`, `:exit`, or `leave` to exit

Example interactive session:
```bash
nova> print a random number between 1 and 10
...   
...   import random
...   print(random.randint(1, 10))
...   
7
nova> exit
```

## Cache Behavior

- Cache is stored in `../cache/cache.json` relative to `transpiler.py`
- Each prompt is hashed using SHA-256 to generate a unique cache key
- Cache entries include timestamps for TTL management
- Use `--cache-ttl` to auto-clear old entries
- Use `-n/--no-cache` to bypass cache for a specific run
- The settings menu (`--settings`) allows manual cache clearing

## Environment Variables

The `--env` flag can be used to pass environment variables to the executed Python code:

```bash
nova script.no --env API_KEY=abc123 --env DB_HOST=localhost
```

Variables are accessible via `os.environ.get('API_KEY')` in your transpiled code.

## Logging

Use `--log-file` to create a log of all transpilation activity:

```bash
nova script.no --log-file transpile.log
```

The log includes timestamps and basic information about each transpilation.

## Performance Tips

1. **Use caching**: Nova automatically caches responses. Enable `--cache-ttl` for auto-cleanup
2. **Choose appropriate model**: `--model llama-3.3-70b-versatile` is faster than `openai/gpt-oss-120b`
3. **Adjust temperature**: Lower temperature (0.0-0.3) for more deterministic outputs
4. **Use `--dry-run`**: Preview code before executing to avoid errors

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| API key not found | Ensure your API key is in `../key/raw.txt` and run the setup script |
| Slow responses | Increase `--timeout` or use a faster model |
| Unexpected code output | Try lower `--temperature` for more deterministic results |
| Cache corruption | Use `--settings` to clear the cache or delete `../cache/cache.json` |
| Execution errors | Use `--show-code` to review the generated Python before running |

## File Structure

```
project/
├── transpiler.py      # Main script
├── key/
│   └── raw.txt        # Groq API key
└── cache/
    └── cache.json     # Response cache (auto-created)
```

## Alias Setup

For convenience, create an alias:

```bash
# Add to your .bashrc or .zshrc
alias nova='python3 /path/to/transpiler.py'
```

Or use a symbolic link:

```bash
chmod +x transpiler.py
ln -s /path/to/transpiler.py /usr/local/bin/nova
```

## Safety Notes

- Nova executes AI-generated Python code directly on your system
- Always review code with `--show-code` or `--dry-run` for unknown inputs
- The `--allow-imports` flag can restrict which modules can be imported
- Use environment variables (`--env`) carefully as they affect execution context
- Consider using a virtual environment or container for untrusted code

## Contributing

This documentation covers all current features. For feature requests or bug reports, please open an issue in the repository.
