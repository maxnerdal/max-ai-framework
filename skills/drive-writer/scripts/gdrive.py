#!/usr/bin/env python3
"""
Google Drive helper for file operations not available via the gdrive MCP.
Uses the Drive API v3 with OAuth credentials (same auth as the gdrive MCP server).

Usage:
  python gdrive.py copy <file_id> <new_name> <parent_folder_id>

  Copies a Google Doc into a new folder with a new name.
  Prints the new file's ID and URL to stdout as JSON.

Example:
  python gdrive.py copy 1aBcD... "CV - Spotify - Backend Engineer" 1xYz...

Auth: Uses the same OAuth credentials as the gdrive MCP server:
  - OAuth client: ~/.config/claude/gcp-oauth.keys.json
  - OAuth tokens: ~/.config/claude/.gdrive-server-credentials.json
"""

import sys
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

OAUTH_KEYS_PATH = Path.home() / ".config" / "claude" / "gcp-oauth.keys.json"
TOKENS_PATH = Path.home() / ".config" / "claude" / ".gdrive-server-credentials.json"
DRIVE_API = "https://www.googleapis.com/drive/v3"


def get_access_token():
    tokens = json.loads(TOKENS_PATH.read_text())
    oauth_keys = json.loads(OAUTH_KEYS_PATH.read_text())
    client = oauth_keys.get("installed", oauth_keys.get("web", {}))

    data = urlencode({
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()

    req = Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    resp = json.loads(urlopen(req).read())
    return resp["access_token"]


def drive_request(method, url, body=None):
    token = get_access_token()
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    resp = urlopen(req).read()
    return json.loads(resp)


def copy_file(file_id, new_name, parent_folder_id):
    """Copy a Drive file into a folder with a new name."""
    url = f"{DRIVE_API}/files/{file_id}/copy"
    body = {
        "name": new_name,
        "parents": [parent_folder_id],
    }
    result = drive_request("POST", url, body)
    file_id = result["id"]
    url = f"https://docs.google.com/document/d/{file_id}/edit"
    return {"id": file_id, "url": url, "name": new_name}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "copy":
        if len(sys.argv) != 5:
            print("Usage: python gdrive.py copy <file_id> <new_name> <parent_folder_id>")
            sys.exit(1)
        _, _, file_id, new_name, parent_folder_id = sys.argv
        result = copy_file(file_id, new_name, parent_folder_id)
        print(json.dumps(result))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
