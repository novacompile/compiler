<div align="center">
  <img src="static/logo.png" width="200px" height="200px" />
  <h1>Nova - v1.0.2</h1>
  <hr /><br />
</div>

NovaCompile is an AI-powered runtime engine and transpiler designed to execute unstructured text, pseudo-code, and custom language files (`.no`) by instantly translating them into production-ready Python code on the fly using Groq Cloud infrastructure.

---

## 🚀 Quick Start Guide

Follow these three simple steps to configure NovaCompile inside your local workspace or web-shell environment.

### 1. Set Up Your Environment
NovaCompile requires a connection to the Groq Cloud API. Export your personal API key into your current terminal profile:

```bash
export GROQ_API_KEY="your-actual-groq-api-key-here"
```

### 2. Install Dependencies
The compiler utilizes the lightweight Python `requests` library to manage direct network handshakes and bypass SDK proxy filters:

```bash
pip install requests
```

### 3. Create the `nova` Terminal Shortcut
To run the compiler globally using the custom `nova` keyword instead of typing out the full Python path, register a local workspace shortcut:

```bash
alias nova="python $(pwd)/src/transpiler.py"
```
> 💡 *Note: To make this shortcut permanent across terminal restarts, append the alias line above directly into your `~/.bashrc` or `~/.zshrc` configuration profile.*

---

## 🛠️ Usage and Execution

Once configured, create a custom code file using your preferred pseudo-syntax or simplified structures. 

### 1. Create a Nova File (`script.no`)
Create a file named `script.no` containing your custom logic:

```text
// Define some basic variables
username make "James"
counter is 5

// Run a structural loop
loop 3 times
    add 2 to counter
    display text "User logged in: " and then show username
    print "Current count value is: " + counter
```

### 2. Run the Compiler
Execute the file instantly by calling `nova` followed by your custom script target:

```bash
nova script.no
```
