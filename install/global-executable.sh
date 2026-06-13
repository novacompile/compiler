#!/bin/bash

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run this script with sudo:${NC}"
    echo -e "${CYAN}sudo bash $0${NC}"
    exit 1
fi

TMP_FILE=$(mktemp)

echo "Downloading the latest version of Nova..."
if ! curl -sSL -o "$TMP_FILE" https://raw.githubusercontent.com/novacompile/compiler/refs/heads/main/bin/nova; then
    echo -e "${RED}Error: Download failed. Check your internet connection.${NC}"
    rm -f "$TMP_FILE"
    exit 1
fi

TARGET_DIR="/usr/local/bin"
TARGET_BIN="$TARGET_DIR/nova"

mkdir -p "$TARGET_DIR"
mv -f "$TMP_FILE" "$TARGET_BIN"
chmod +x "$TARGET_BIN"

echo -e "${GREEN}Nova has been installed globally as '${CYAN}nova${GREEN}'. You can now run '${CYAN}nova${GREEN}' from any directory.${NC}"