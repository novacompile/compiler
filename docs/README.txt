Nova - v2.3.0

NovaCompile is an AI-powered runtime engine and transpiler designed to execute 
unstructured text, pseudo-code, and custom language files (.no) by instantly 
translating them into production-ready Python code on the fly using Groq Cloud 
infrastructure.

================================================================================
QUICK START GUIDE
================================================================================

To install a permanent binary global executable, run this install script:
install/global-executable.sh
And ignore steps 1 and 3.

Follow these three simple steps to configure NovaCompile inside your local 
workspace or web-shell environment.

Step 1: Run Installation Script
-------------------------------------------------------------------------------
Run this installation script to clone the repository to get Nova on your device.

cd ~
mkdir .novacompile
cd .novacompile
git clone https://github.com/novacompile/compiler.git
cd compiler

Step 2: Get a Groq API Key
-------------------------------------------------------------------------------
Go to console.groq.com and sign up for an account. Click API Keys, then create 
API key.

WARNING: Remember to copy the key and put it in a safe and secure place straight 
away after creating it.

Step 3: Setup Your Environment
-------------------------------------------------------------------------------
Run the setup script to install the dependencies through pip, create a permanent 
alias, and install your API key.

bash setup.sh

NOTE: To make this shortcut permanent across terminal restarts, the setup script 
appends the alias directly into your ~/.bashrc configuration profile.

================================================================================
USAGE AND EXECUTION
================================================================================

Once configured, create a custom code file using your preferred pseudo-syntax or 
simplified structures.

1. Start the Interactive Shell
-------------------------------------------------------------------------------
Launch the shell directly to type Nova code interactively:

nova

If you run the transpiler without a file argument, it starts this shell 
automatically.

In shell mode, type a block of Nova code, then press Enter on an empty line to 
transpile and run it. Use exit or quit to leave.

2. Create a Nova File
-------------------------------------------------------------------------------
Create a file with the .no suffix (e.g. script.no) containing your custom logic, 
for example:

// Define some basic variables
username is "john"
counter is 5

// Run a structural loop
loop 3 times
    add 2 to counter
    display text "User logged in: " and then show username
    print "Current count value is: " + counter

3. Run the Compiler
-------------------------------------------------------------------------------
Execute the file instantly by calling nova followed by your custom script target:

nova [filename].no

If you prefer to run the entrypoint directly, this also works:

python src/transpiler.py [filename].no

WARNING: To be able to run the entrypoint directly, you must be inside the root 
directory of compiler (by default it is ~/.novacompile/compiler)

================================================================================
LICENSE
================================================================================

Nova Compiler is under the MIT License (LICENSE). Make sure that you have read 
and understood it before reproducing this repo.
