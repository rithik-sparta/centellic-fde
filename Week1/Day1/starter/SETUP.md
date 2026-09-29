# Setup guide

*FDE programme, Week 1. Do this once every day uses the same toolchain.*

You need: **Python 3.12**, **uv**, **git**, and **VS Code**. Pick your OS below.

---

## Mac

Open **Terminal**.

```bash
# 1. Install everything
brew install python@3.12 git
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Close and reopen Terminal, then confirm it all worked
python3 --version   # want 3.12.x
uv --version
git --version
```

Don't have Homebrew? Install it first from [brew.sh](https://brew.sh), then run the block above.

Install **VS Code** from [code.visualstudio.com](https://code.visualstudio.com), then in Terminal:

```bash
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
git config --global core.editor "code --wait"
```

---

## Windows

Open **PowerShell as Administrator** (right-click it in the Start menu → *Run as administrator*).

```powershell
winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
winget install --id astral-sh.uv -e --silent --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.VisualStudioCode -e --silent --accept-package-agreements --accept-source-agreements
```

Close PowerShell. From here on, use **Git Bash** (Start menu → *Git Bash*), not PowerShell —
it's what makes your terminal behave like everyone else's on the course.

```bash
python --version   # want 3.12.x
uv --version
git --version
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
git config --global core.editor "code --wait"
```

> If `code` isn't recognised: open VS Code once, press `Ctrl+Shift+P`, run
> **Shell Command: Install 'code' command in PATH**, then reopen Git Bash.

---

## Check it worked

Clone the Day 1 starter project (link from your trainer), then from inside it:

**Mac**
```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python environment_doctor.py
```

**Windows (Git Bash)**
```bash
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe environment_doctor.py
```

You should see:

```
OK   python 3.12
OK   isolated environment at ...
OK   pytest 9.1.1
OK   mypy 2.3.1
OK   ruff 0.16.6

All checks passed. This environment matches the pins.
```

That's it — you're ready. Full instructions for the day's work are in the starter
project's own `README.md`.

---

## If something's wrong

| Problem | Fix |
|---|---|
| A command "not found" right after installing it | Close the terminal completely and open a new one. Installers update your PATH; an already-open terminal doesn't see it |
| `uv pip install` fails, can't reach the internet | Tell your trainer — the network may be blocked and needs a workaround on their end |
| Windows: `python` works but `python3` doesn't | Expected. Windows installs Python as `python`, not `python3`. Use `python` throughout |
| Doctor reports `FAIL isolation` | You're running it with your system Python, not the one in `.venv`. Use the exact path shown above (`.venv/bin/python` or `.venv/Scripts/python.exe`) |
