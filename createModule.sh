#!/bin/bash
source ./common.sh

# ***** Build distribution files (wheel + sdist) inside the project virtual environment
# Homebrew's system Python is externally managed (PEP 668) and refuses pip installs, so use the venv's interpreter
VENV_PYTHON=./$PYTHON_CLIENT_VIRTUAL_ENV/bin/python3

if [ ! -x "$VENV_PYTHON" ]; then
    echo -e "${MAGENTA}Python virtual environment $PYTHON_CLIENT_VIRTUAL_ENV does not exist, creating ...${RESET}"
    python3 -m venv $PYTHON_CLIENT_VIRTUAL_ENV || exit 1
fi

# Install build tools
$VENV_PYTHON -m pip install --upgrade build || exit 1

# Build distribution files
$VENV_PYTHON -m build
