mkdir -p key && echo -n "Enter API key: " && read -s KEY_INPUT && echo "" && echo -n "$KEY_INPUT" > key/raw.txt
pip install -r requirements.txt
echo "alias nova=\"python $(pwd)/src/transpiler.py\"" >> ~/.bashrc && source ~/.bashrc
