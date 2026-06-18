#!/bin/bash

# Define ANSI colour codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Colour (Resets to terminal default)

# Version file checker logic
if [ -f "version" ]; then
  VERSION_STRING=" | $(cat version | xargs)"
else
  VERSION_STRING=""
fi

echo -e "${CYAN}Nova Setup${VERSION_STRING}${NC}"
echo -e "---\n"

if mkdir -p key && echo -n "Enter API key: " && read -s KEY_INPUT && echo "" && echo -n "$KEY_INPUT" > key/raw.txt; then
  echo -e "${GREEN}Installed API key space ✓${NC}"
else
  echo -e "${RED}ERROR: API key installation failed. Please check that you have have entered a valid input.${NC}"
fi

echo -e "${CYAN}Installing dependencies...${NC}"
if pip install -r requirements.txt -q; then
  echo -e "${GREEN}Installed dependencies ✓${NC}"
else
  echo -e "${RED}ERROR: Package installation failed. Please check your internet connection or requirements.txt file.${NC}"
  exit 1
fi

echo -e "${CYAN}Adding alias...${NC}"
if echo "alias nova=\"python $(pwd)/src/transpiler.py\"" >> ~/.bashrc && source ~/.bashrc; then
  echo -e "${GREEN}Added alias ✓${NC}"
else
  echo -e "${RED}ERROR: Alias installation failed. Please check your permissions.${NC}"
fi
