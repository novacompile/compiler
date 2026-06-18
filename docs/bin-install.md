# Install Binary Executable

Run [this installation script](../install/global-executable.sh), to install **Nova** as a global executable or use this to directly install the binary file to `usr/local/bin/nova`: 

```bash
curl -fsSL https://githubusercontent.com -o nova && \
sudo install -m 755 nova /usr/local/bin/nova && \
rm nova
```

Or, if you prefer to install it locally, run this script to install it to `~/.local/bin/nova`:

```bash
curl -fsSL https://raw.githubusercontent.com/novacompile/compiler/refs/heads/main/install/global-executable.sh
mkdir -p ~/.local/bin
mv global-executable.sh ~/.local/bin/novacompile
chmod +x ~/.local/bin/novacompile
```
