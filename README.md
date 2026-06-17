<div align="center">
  <img src="static/logo.png" width="200px" height="200px" />
  <br /><br />
  <h1>Nova - <span id="version">v1.2.1</span></h1>
  <div>
    <a href="https://github.com/novacompile/compiler/issues"><img alt="GitHub Issues Badge" src="https://img.shields.io/github/issues/novacompile/compiler?style=for-the-badge&link=https%3A%2F%2Fgithub.com%2Fnovacompile%2Fcompiler%2Fissues"></a>
    <a href="https://github.com/novacompile/compiler/releases"><img alt="Version Badge" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnovacompile%2Fcompiler%2Frefs%2Fheads%2Fmain%2F.shields%2Fversion.json&style=for-the-badge&cacheSeconds=300&link=https%3A%2F%2Fgithub.com%2Fnovacompile%2Fcompiler%2Freleases"></a>
    <a href="#"><img alt="GitHub branch check runs" src="https://img.shields.io/github/check-runs/novacompile/compiler/main?style=for-the-badge"></a>
  </div>
  <br />
</div>

NovaCompile is an AI-powered runtime engine and transpiler designed to execute unstructured text, pseudo-code, and custom language files (`.no`) by instantly translating them into production-ready Python code on the fly using Groq Cloud infrastructure.

---

## 🚀 Quick Start Guide

To install a permenant binary global executable, run this [install script](install/global-executable.sh) and ignore step 3.


Follow these three simple steps to configure NovaCompile inside your local workspace or web-shell environment.

### 1. Run Installation Script
Run this installation script to clone the repository and add an alias and install dependencies.

```bash
cd ~
mkdir .novacompile
cd .novacompile
git clone https://github.com/novacompile/compiler.git
cd compiler
bash setup.sh
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
> [!NOTE]
> To make this shortcut permanent across terminal restarts, append the alias line above directly into your `~/.bashrc` or `~/.zshrc` configuration profile - run [this script](setup.sh) for appending to `~/.bashrc`.

---

## 🛠️ Usage and Execution

Once configured, create a custom code file using your preferred pseudo-syntax or simplified structures. 

### 1. Start the Interactive Shell
Launch the shell directly to type Nova code interactively:

```bash
nova
```

If you run the transpiler without a file argument, it starts this shell automatically.

In shell mode, type a block of Nova code, then press Enter on an empty line to transpile and run it. Use `exit` or `quit` to leave.

### 2. Create a Nova File (`script.no`)
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

### 3. Run the Compiler
Execute the file instantly by calling `nova` followed by your custom script target:

```bash
nova script.no
```

If you prefer to run the entrypoint directly, this also works:

```bash
python src/transpiler.py script.no
```


## License

Nova Compiler is under the [MIT License](LICENSE). Make sure that you have read and understood it before reproducing this repo.
