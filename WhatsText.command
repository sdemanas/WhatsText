#!/bin/bash
# Double-click this file to run WhatsText. No install, no terminal typing.
cd "$(dirname "$0")"

PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$PYTHON_BIN" ]; then
    echo "Python 3 wasn't found on this Mac."
    echo "Install it from https://www.python.org/downloads/ then double-click this file again."
    read -n 1 -s -r -p "Press any key to close..."
    exit 1
fi

export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
"$PYTHON_BIN" -m whatstext

read -n 1 -s -r -p "Press any key to close..."
