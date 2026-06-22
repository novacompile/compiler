#!/bin/bash

# Target file path
TARGET_DIR="src"
TARGET_FILE="$TARGET_DIR/transpiler.py"
URL="https://githubusercontent.com"

# Ensure the target directory exists
mkdir -p "$TARGET_DIR"

# Download and replace the file
echo "Downloading latest transpiler.py..."
if command -v curl >/dev/null 2>&1; then
    curl -sSL "$URL" -o "$TARGET_FILE"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$TARGET_FILE" "$URL"
else
    echo "Error: Neither curl nor wget is installed."
    exit 1
fi

# Verify success
if [ $? -eq 0 ]; then
    echo "Successfully replaced $TARGET_FILE"
else
    echo "Error: Failed to download the file."
    exit 1
fi
