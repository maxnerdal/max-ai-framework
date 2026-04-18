#!/usr/bin/env python3
"""
oauth_flow.py — One-time Gmail OAuth2 setup for HOSP automation.

Run this once after downloading your GCP OAuth credentials JSON.
It opens a browser window for Google sign-in, then saves a refresh token
so hosp_processor.py can run unattended from that point on.

Usage:
    python3 oauth_flow.py
"""
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.md"


def load_config(path: Path) -> dict:
    config = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            config[key.strip()] = val.strip()
    return config


def main():
    if not CONFIG_PATH.exists():
        print(f"ERROR: config.md not found at {CONFIG_PATH}")
        print("Copy config.example.md to config.md and fill in your values.")
        sys.exit(1)

    config = load_config(CONFIG_PATH)
    creds_path = Path(config.get("GMAIL_CREDENTIALS_PATH", "")).expanduser()
    token_path = Path(config.get("GMAIL_TOKEN_PATH", "")).expanduser()

    if not creds_path or not creds_path.exists():
        print(f"ERROR: OAuth credentials file not found: {creds_path}")
        print(
            "Download your credentials JSON from Google Cloud Console:\n"
            "  APIs & Services → Credentials → your Desktop app → Download JSON\n"
            f"  Save it to: {creds_path}"
        )
        sys.exit(1)

    print(f"Opening browser for Google sign-in...")
    print(f"Sign in as: max.nerdal@curaconnect.se\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())

    print(f"\nToken saved to: {token_path}")
    print("Setup complete. You can now run hosp_processor.py.")


if __name__ == "__main__":
    main()
