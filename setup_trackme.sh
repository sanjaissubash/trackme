#!/usr/bin/env bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
echo "Setting up TrackMe in: $PROJECT_DIR"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Created venv at $VENV_DIR"
else
    echo "Venv already exists at $VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"
pip install -e "$PROJECT_DIR"
ALIAS_LINE="alias trackme='$VENV_DIR/bin/trackme'"
if ! grep -qxF "$ALIAS_LINE" "$HOME/.zshrc"; then
    echo "" >> "$HOME/.zshrc"
    echo "# TrackMe alias added by setup" >> "$HOME/.zshrc"
    echo "$ALIAS_LINE" >> "$HOME/.zshrc"
    echo "Added alias to ~/.zshrc. Run: source ~/.zshrc"
else
    echo "Alias already present in ~/.zshrc"
fi
echo "Setup complete. You can now run 'trackme' from any directory."
