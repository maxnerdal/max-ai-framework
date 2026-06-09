#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

info()    { echo "[->] $1"; }
success() { echo "[ok] $1"; }
warn()    { echo "[!]  $1"; }

# Back up an existing path and create a symlink in its place.
# Safe to run multiple times — skips if symlink already correct.
backup_and_link() {
  local link="$1"
  local target="$2"

  if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then
    success "$link already linked correctly, skipping"
    return
  fi

  if [ -L "$link" ]; then
    warn "$link is a symlink pointing to $(readlink "$link") — replacing"
    rm "$link"
  elif [ -e "$link" ]; then
    local backup="${link}.backup_${TIMESTAMP}"
    warn "$link exists — backing up to $backup"
    mv "$link" "$backup"
  fi

  mkdir -p "$(dirname "$link")"
  ln -s "$target" "$link"
  success "$link -> $target"
}

echo ""
echo "max-ai-framework setup"
echo "Repo: $REPO_DIR"
echo ""

# Symlink the repo-controlled bits of ~/.claude/ individually.
# We do NOT symlink the whole ~/.claude/ — Claude Code writes runtime files
# (projects/, sessions/, mcp.json, settings.json, ...) into ~/.claude/ that
# should not land in the repo.
info "Linking ~/.claude/CLAUDE.md, agents/, commands/, rules/"
backup_and_link "$HOME/.claude/CLAUDE.md" "$REPO_DIR/.claude/CLAUDE.md"
backup_and_link "$HOME/.claude/agents"    "$REPO_DIR/.claude/agents"
backup_and_link "$HOME/.claude/commands"  "$REPO_DIR/.claude/commands"
backup_and_link "$HOME/.claude/rules"     "$REPO_DIR/.claude/rules"

# Source shell aliases from ~/.zshrc if not already done.
ZSHRC="$HOME/.zshrc"
SOURCE_LINE="source $REPO_DIR/shell/aliases.sh"
if [ -f "$ZSHRC" ] && grep -qF "$SOURCE_LINE" "$ZSHRC"; then
  success "$ZSHRC already sources shell/aliases.sh, skipping"
else
  info "Adding shell/aliases.sh source to $ZSHRC"
  {
    echo ""
    echo "# max-ai-framework shell aliases"
    echo "$SOURCE_LINE"
  } >> "$ZSHRC"
  success "Sourced shell/aliases.sh from $ZSHRC"
fi

echo ""
echo "Done. Any pre-existing files were backed up with timestamped paths — see warnings above."
