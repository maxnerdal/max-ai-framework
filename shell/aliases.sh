# max-ai-framework shell aliases
# Sourced from ~/.zshrc by setup.sh

# Claude Code: starta session med alla permissions automatiskt godkända.
# OBS: bypass-läge — Claude kan köra vilket kommando som helst utan att fråga.
# Använd bara för betrodda batch-jobb (essä-generering, PDF-läsning etc.)
alias claude-yolo="claude --dangerously-skip-permissions"
