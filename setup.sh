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

# 1. ~/.claude -> repo/.claude
#    Claude Code global config: agents, commands, hooks, settings
info "Linking ~/.claude"
backup_and_link "$HOME/.claude" "$REPO_DIR/.claude"

# 2. ~/Documents/Claude/Scheduled -> repo/claude-cowork/Scheduled
#    Cowork picks up scheduled tasks from this path
info "Linking ~/Documents/Claude/Scheduled"
mkdir -p "$HOME/Documents/Claude"
backup_and_link "$HOME/Documents/Claude/Scheduled" "$REPO_DIR/claude-cowork/Scheduled"

echo ""
echo "Done. If ~/.claude was backed up, review it and copy anything you want to keep into $REPO_DIR/.claude"
