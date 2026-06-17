echo -n "enter api key: " && read -s GROQ_API_KEY && export GROQ_API_KEY
pip install -r requirements.txt
echo "alias nova=\"python $(pwd)/src/transpiler.py\"" >> ~/.bashrc && source ~/.bashrc
