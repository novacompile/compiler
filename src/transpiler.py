name: Test Groq Transpiler

on:
  push:
    branches: [ "main" ]
  workflow_dispatch: 

jobs:
  run-compiler:
    runs-on: ubuntu-latest

    steps:
    - name: Check out code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run Transpiler Test via Groq
      env:
        # This securely injects the Groq key you saved in your repository settings
        GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      run: |
        python transpiler.py --text "x = 99; prnt x; display Calculation Successful" -l javascript
