# max-ai-framework shell aliases
# Sourced from ~/.zshrc by setup.sh

# Claude Code: starta session med alla permissions automatiskt godkända.
# OBS: bypass-läge — Claude kan köra vilket kommando som helst utan att fråga.
# Använd bara för betrodda batch-jobb (essä-generering, PDF-läsning etc.)
alias claude-yolo="claude --dangerously-skip-permissions"

# Google Cloud: logga in utan att gcloud väljer webbläsare åt dig.
#
# Av sig själv öppnar gcloud den webbläsarprofil som är standard, och det är den privata.
# Att i stället peka ut Cura-profilen vore samma fel spegelvänt den dagen datorn har både
# privata och arbetskonton i Google Cloud. --no-launch-browser lämnar valet åt dig: den
# skriver ut en länk att klistra in i vilken webbläsare och profil du vill, och tar emot
# koden tillbaka i terminalen.
#
#     gclogin                              väljer konto på sidan
#     gclogin max.nerdal@curaconnect.se    förvalt konto
#     gclogin --update-adc                 även Application Default Credentials
gclogin() {
    gcloud auth login --no-launch-browser "$@"
}
