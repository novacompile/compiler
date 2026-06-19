# Nova Usage Guide

## Command Structure
```bash
nova [OPTIONS] [FILE]
```

## All Flags and Options

| Flag | Description | Example |
|------|-------------|---------|
| **Help Options** | | |
| `-h, --help` | Show help message and exit | `nova --help` |
| `--flags` | Display all available flags with descriptions | `nova --flags` |
| **Mode Options** | | |
| `-c, --chat` | Launch AI chat mode (interactive coding assistant) | `nova -c` |
| `--agent` | Launch agent mode (same as chat mode) | `nova --agent` |
| `--shell` | Launch shell mode (transpile and execute code) - Default | `nova --shell` |
| **Fix Options** | | |
| `-f, --fix FILE` | Scan and fix errors in a file | `nova -f broken.py` |
| `-L, --language LANG` | Specify language for fix operation (auto-detects from extension) | `nova -f broken.js -L javascript` |
| **Translate Options** | | |
| `-T, --translate LANG` | Translate a file to the specified target language | `nova -T python script.js` |
| **Input Options** | | |
| `source_file` | Path to the .no file (or source file for translation) | `nova script.no` |
| `-s, --string TEXT` | Transpile and execute a single string of code | `nova -s "print('Hello')"` |
| `--stdin` | Read input from stdin instead of a file | `echo "print('hi')" | nova --stdin` |
| `-o, --output FILE` | Save generated code to a file instead of executing | `nova script.no -o output.py` |
| **Behavior Options** | | |
| `-n, --no-cache` | Disable cache for this run | `nova -n script.no` |
| `--show-code` | Show generated Python code without executing it | `nova --show-code script.no` |
| `--dry-run` | Show what would be transpiled without executing | `nova --dry-run script.no` |
| `-v, --verbose` | Show detailed output including API calls and cache info | `nova -v script.no` |
| `-q, --quiet` | Suppress all non-error output | `nova -q script.no` |
| `--no-color` | Disable colored output in terminal | `nova --no-color script.no` |
| `-i, --interactive` | Drop into interactive mode after execution (like python -i) | `nova -i script.no` |
| **Model and Performance** | | |
| `--model MODEL` | Groq model to use (default: openai/gpt-oss-120b) | `nova --model llama3-70b-8192 script.no` |
| `-t, --temperature FLOAT` | Temperature for the AI model (0.0-1.0, default: 0.1) | `nova -t 0.2 script.no` |
| `--timeout SECONDS` | API timeout in seconds (default: 30) | `nova --timeout 60 script.no` |
| **Cache Management** | | |
| `--cache-size` | Show size and number of entries in cache | `nova --cache-size` |
| `--cache-ttl SECONDS` | Set cache expiration time in seconds (auto-clear old entries) | `nova --cache-ttl 3600` |
| `--settings` | Open interactive settings menu | `nova --settings` |
| **Environment and Execution** | | |
| `--env KEY=value` | Set environment variables (can be used multiple times) | `nova --env API_KEY=123 script.no` |
| `--interpreter PATH` | Python interpreter to use for execution | `nova --interpreter python3.11 script.no` |
| `--log-file FILE` | Log all transpilations and execution results to a file | `nova --log-file log.txt script.no` |
| **Security** | | |
| `--allow-imports LIST` | Comma-separated list of allowed imports (not yet implemented) | `nova --allow-imports os,sys script.no` |

## Chat/AI Mode Commands

| Command | Description | Example |
|---------|-------------|---------|
| **Permission Management** | | |
| `;edit` | Grant permission to edit files | `;edit` |
| `;all` | Grant all permissions | `;all` |
| `;suno` | Grant extended permissions | `;suno` |
| **File Operations** | | |
| `;read file` | Read file content | `;read config.json` |
| `;run file` | Run file in any supported language | `;run script.py` |
| `;create file "content"` | Create new file with content | `;create test.py "print('Hello')"` |
| `;delete file` | Delete file (requires confirmation) | `;delete old.py` |
| `;rename old new` | Rename file | `;rename old.py new.py` |
| `;mkdir dir` | Create directory | `;mkdir src` |
| `;search "pattern"` | Search files for pattern | `;search "function"` |
| **Code Quality** | | |
| `;lint file` | Lint code (Python only) | `;lint script.py` |
| `;debug file` | Debug code (Python only) | `;debug script.py` |
| `;history file` | Show backup history | `;history script.py` |
| **Package Management** | | |
| `;install package` | Install Python package via pip | `;install requests` |
| **System** | | |
| `;share` | Share all file information with Nova | `;share` |
| `:clear_memory` | Clear AI's persistent memory | `:clear_memory` |
| `:settings` | Open settings menu | `:settings` |
| `exit` or `quit` | Exit chat mode | `exit` |

## Supported Languages

| Language | Extension | Run Support | Translation Support | Lint Support | Debug Support |
|----------|-----------|-------------|---------------------|--------------|---------------|
| Python | `.py` | ✓ | ✓ | ✓ | ✓ |
| JavaScript | `.js` | ✓ | ✓ | ✗ | ✗ |
| TypeScript | `.ts` | ✓ | ✓ | ✗ | ✗ |
| Ruby | `.rb` | ✓ | ✓ | ✗ | ✗ |
| Go | `.go` | ✓ | ✓ | ✗ | ✗ |
| Rust | `.rs` | ✓ | ✓ | ✗ | ✗ |
| C | `.c` | ✓ | ✓ | ✗ | ✗ |
| C++ | `.cpp` | ✓ | ✓ | ✗ | ✗ |
| Java | `.java` | ✓ | ✓ | ✗ | ✗ |
| Bash | `.sh` | ✓ | ✓ | ✗ | ✗ |
| Perl | `.pl` | ✓ | ✓ | ✗ | ✗ |
| Lua | `.lua` | ✓ | ✓ | ✗ | ✗ |
| R | `.r` | ✓ | ✓ | ✗ | ✗ |
| Swift | `.swift` | ✓ | ✓ | ✗ | ✗ |
| PHP | `.php` | ✓ | ✓ | ✗ | ✗ |
| HTML | `.html` | ✓ | ✓ | ✗ | ✗ |
| CSS | `.css` | ✗ | ✓ | ✗ | ✗ |
| JSON | `.json` | ✗ | ✓ | ✗ | ✗ |
| XML | `.xml` | ✗ | ✓ | ✗ | ✗ |
| YAML | `.yml` | ✗ | ✓ | ✗ | ✗ |
| Markdown | `.md` | ✓ | ✓ | ✗ | ✗ |

## Examples

### Basic Usage
```
# Run a .no file
nova script.no

# Start interactive shell
nova

# Execute a single string
nova -s "print('Hello World')"

# Execute with verbose output
nova -v script.no
```

### Fix Mode
```
# Auto-detect language and fix
nova -f broken.py

# Specify language explicitly
nova -f broken.js -L javascript
nova -f broken.go -L go
```

### Translate Mode
```
# Translate JavaScript to Python
nova -T python script.js

# Translate Python to JavaScript
nova -T javascript script.py

# Translate Python to Go
nova -T go script.py
```

### Chat Mode
```
# Start chat mode
nova --agent

# Grant edit permission
you> ;edit

# Read a file
you> ;read config.json

# Run a file
you> ;run script.py

# Create a new file
you> ;create test.py "print('Hello')"

# Search for a pattern
you> ;search "function"

# Fix a file (requires permission)
you> ;edit
you> Fix broken.py
```

### Advanced Examples
```
# Fix with specific model and temperature
nova -f broken.py --model llama3-70b-8192 -t 0.2

# Translate with custom timeout
nova -T go script.py --timeout 60

# Run with environment variables
nova script.no --env API_KEY=123 --env DEBUG=true

# Show code without executing
nova --show-code script.no

# Dry run (show what would happen)
nova --dry-run script.no
```

## Settings Menu
```
nova --settings
```
Options:
1. Clear cache
2. Show cache info
3. Clear AI memory
4. Show AI memory
5. Toggle execution status messages
6. Back

## Memory and Backups
- **AI Memory**: `~/.novacompile/compiler/memory/chat-memory.db`
- **Backups**: `~/.novacompile/compiler/backups/`
- **Backup Format**: `filename.YYYYMMDD_HHMMSS.bak`

## Security Notes
- All file operations restricted to current working directory
- Editing requires explicit permission
- Delete operations require confirmation
- No root privileges or system-level access
- API key stored in `key/raw.txt`
