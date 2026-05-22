# compiler
Central compiler for Nova

## AI syntax-correcting compiler (Python)

This repository includes a small Python-based compiler-style CLI that tries to
recover from malformed syntax and transpile intent into a target language.

### Supported target languages

- python
- javascript
- typescript
- go
- rust
- java
- cpp

### Usage

List supported languages:

```bash
python ai_compiler.py --list-languages
```

Compile from a file:

```bash
python ai_compiler.py input.txt --language javascript
```

Compile from inline text:

```bash
python ai_compiler.py --text "prnit hello world" --language python
```
