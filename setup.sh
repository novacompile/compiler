#!/bin/bash

# Define ANSI colour codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Colour (Resets to terminal default)

# Resolve the absolute path of the script directory, avoiding pwd bugs
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Dynamic version header logic
VERSION_FILE="$SCRIPT_DIR/version"
if [ -f "$VERSION_FILE" ]; then
  # Read file content and remove trailing whitespaces/newlines
  VERSION_STRING=" | $(cat "$VERSION_FILE" | xargs)"
else
  VERSION_STRING=""
fi

echo -e "${CYAN}Nova Setup${VERSION_STRING}${NC}"
echo -e "---\n"

# Step 1: Create Key File
if mkdir -p "$SCRIPT_DIR/key" && echo -n "Enter API key: " && read -s KEY_INPUT && echo "" && echo -n "$KEY_INPUT" > "$SCRIPT_DIR/key/raw.txt"; then
  echo -e "${GREEN}Installed API key space ✓${NC}"
else
  echo -e "${RED}ERROR: API key installation failed. Please check that you have entered a valid input.${NC}"
fi

# Step 2: Install Dependencies
echo -e "${CYAN}Installing dependencies...${NC}"
if pip install -r "$SCRIPT_DIR/requirements.txt" -q; then
  echo -e "${GREEN}Installed dependencies ✓${NC}"
else
  echo -e "${RED}ERROR: Package installation failed. Please check your internet connection or requirements.txt file.${NC}"
  exit 1
fi

# Step 3: Add Alias
echo -e "${CYAN}Adding alias...${NC}"
# Append the alias safely using the permanent script location directory path
if echo "alias nova=\"python $SCRIPT_DIR/src/transpiler.py\"" >> ~/.bashrc; then
  echo -e "${GREEN}Added alias ✓${NC}"
  echo -e "${CYAN}--> To start using 'nova' immediately, run:${NC} source ~/.bashrc"
else
  echo -e "${RED}ERROR: Alias installation failed. Please check your permissions.${NC}"
fi
