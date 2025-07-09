# 🛠️ Installation Troubleshooting Guide

## Problem: Pandas Build Error

If you're getting a pandas build error like:
```
ERROR: Failed building wheel for pandas
ERROR: Could not build wheels for pandas, which is required to install pyproject.toml-based projects
```

## 🔧 Solutions (Try in Order)

### Solution 1: Install System Dependencies (Recommended)

First, install system-level dependencies that pandas needs:

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install python3-dev build-essential

# For CentOS/RHEL/Fedora
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# For macOS (using Homebrew)
brew install gcc
```

### Solution 2: Use Pre-compiled Wheels

Install pandas separately first with pre-compiled wheels:

```bash
pip install --only-binary=:all: pandas
pip install -r requirements.txt
```

### Solution 3: Install with Specific Options

```bash
# Option A: Force binary installation
pip install --only-binary=:all: -r requirements.txt

# Option B: Use conda instead of pip
conda install pandas numpy
pip install -r requirements.txt

# Option C: Install with specific flags
pip install --no-cache-dir --force-reinstall pandas
pip install -r requirements.txt
```

### Solution 4: Use Virtual Environment with Updated Tools

```bash
# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

### Solution 5: Alternative Installation Method

If all above fails, try installing packages one by one:

```bash
pip install --only-binary=:all: pandas
pip install --only-binary=:all: numpy
pip install --only-binary=:all: torch
pip install gradio
pip install transformers
pip install pandasai
pip install langchain-groq
pip install mysql-connector-python
pip install tabulate
pip install langchain_openai
pip install python-dotenv
```

### Solution 6: Use Conda Environment (Most Reliable)

```bash
# Install Miniconda if you don't have it
# Then create conda environment
conda create -n mychat-env python=3.9
conda activate mychat-env

# Install packages via conda
conda install pandas numpy pytorch -c pytorch
conda install -c conda-forge gradio transformers

# Install remaining packages via pip
pip install pandasai langchain-groq mysql-connector-python tabulate langchain_openai python-dotenv
```

## 🚀 Quick Fix Commands

Try these commands in order until one works:

```bash
# 1. Update system and install dev tools
sudo apt update && sudo apt install python3-dev build-essential

# 2. Create fresh environment
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# 3. Install with binary only
pip install --only-binary=:all: -r requirements.txt
```

## 🔍 Common Issues and Solutions

### Issue: "Microsoft Visual C++ 14.0 is required" (Windows)
- Install Visual Studio Build Tools
- Or use conda instead of pip

### Issue: "gcc: error trying to exec 'cc1plus'" (Linux)
- Install gcc and g++: `sudo apt install gcc g++`

### Issue: "fatal error: Python.h: No such file or directory"
- Install python3-dev: `sudo apt install python3-dev`

## ✅ Verification

After successful installation, verify with:

```bash
python -c "import pandas; print('Pandas version:', pandas.__version__)"
python -c "import gradio; print('Gradio version:', gradio.__version__)"
```

## 🆘 Still Having Issues?

If none of the above solutions work:

1. **Check Python version**: Ensure you're using Python 3.8+
2. **Use Docker**: Consider using a pre-built Docker image
3. **Try different Python version**: Some packages work better with specific Python versions
4. **Contact support**: Share your exact error message and system details 