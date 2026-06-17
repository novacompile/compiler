echo -n "enter api key: " && read -s KEY_INPUT && echo "export GROQ_API_KEY=\"\$KEY_INPUT\"" >> ~/.bashrc && source ~/.bashrc
pip install -r requirements.txt
echo "alias nova=\"python $(pwd)/src/transpiler.py\"" >> ~/.bashrc && source ~/.bashrc
