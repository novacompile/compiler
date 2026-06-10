NOVA - v1.2.0

Nova is an AI-powered runtime engine and transpiler designed to execute unstructured text, pseudo-code, and custom language files (.no) by instantly translating them into production-ready Python code on the fly using Groq Cloud infrastructure.

===============================================================================
QUICK START GUIDE
===============================================================================

Follow these steps to configure NovaCompile inside your local workspace or 
web-shell environment.

1. Clone the Repository
Run this install script to copy the code to your local device:
git clone https://github.com/novacompile/compiler.git

2. Set Up Your Environment
NovaCompile requires a connection to the Groq Cloud API. Export your personal 
API key into your current terminal profile:
export GROQ_API_KEY="your-actual-groq-api-key-here"

3. Install Dependencies
The compiler utilizes the lightweight Python requests library to manage direct 
network handshakes:
pip install requests

4. Create the 'nova' Terminal Shortcut
To run the compiler globally using the 'nova' keyword instead of the full 
Python path, register a local workspace shortcut:
alias nova="python $(pwd)/src/transpiler.py"

*Note: To make this shortcut permanent across terminal restarts, append the 
alias line above directly into your ~/.bashrc or ~/.zshrc configuration profile.


===============================================================================
USAGE AND EXECUTION
===============================================================================

Once configured, create a custom code file using your preferred pseudo-syntax 
or simplified structures.

1. Start the Interactive Shell
Launch the shell directly to type Nova code interactively:
nova

* Note: Running the transpiler without a file argument starts this shell 
  automatically. Type your Nova code block, then press Enter on an empty line 
  to transpile and run it. Use 'exit' or 'quit' to leave.

2. Create a Nova File (script.no)
Create a file named script.no containing your custom logic:

// Define some basic variables
username make "john"
counter is 5

// Run a structural loop
loop 3 times
    add 2 to counter
    display text "User logged in: " and then show username
    print "Current count value is: " + counter

3. Run the Compiler
Execute the file instantly by calling 'nova' followed by your script target:
nova script.no

Alternatively, you can run the entrypoint directly:
python src/transpiler.py script.no


===============================================================================
LICENSE
===============================================================================

Nova compile is under the MIT License. Before you fork this repo, read the 
license first.
