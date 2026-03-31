#!/usr/bin/env python3
"""
Google Sheets helper for job-tracker.
Uses the Sheets API v4 with OAuth credentials (same auth as the gdrive MCP server),
since the gdrive MCP's update_file writes plain text into a single cell, not rows/columns.

Usage:
  python sheets.py read   <sheet_id>
  python sheets.py write  <sheet_id> <rows_json>
  python sheets.py append <sheet_id> <row_json>

rows_json: JSON array of arrays  e.g. '[["Company","Role",...],["Spotify","Dev",...]]'
row_json:  JSON array             e.g. '["Spotify","Backend Dev","https://...","Found","Medium","2026-04-15","","",""]'

Auth: Uses the same OAuth credentials as the gdrive MCP server:
  - OAuth client: ~/.config/claude/gcp-oauth.keys.json
  - OAuth tokens: ~/.config/claude/.gdrive-server-credentials.json
"""

import sys
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote

OAUTH_KEYS_PATH = Path.home() / ".config" / "claude" / "gcp-oauth.keys.json"
TOKENS_PATH = Path.home() / ".config" / "claude" / ".gdrive-server-credentials.json"
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"
_sheet_name_cache = {}


def get_access_token():
    """Get a valid access token, refreshing if needed."""
    tokens = json.loads(TOKENS_PATH.read_text())
    oauth_keys = json.loads(OAUTH_KEYS_PATH.read_text())
    client = oauth_keys.get("installed", oauth_keys.get("web", {}))

    # Always refresh to ensure we have a valid token
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


def sheets_request(method, url, body=None):
    """Make an authenticated request to the Sheets API."""
    token = get_access_token()
    req = Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    if body is not None:
        resp = urlopen(req, json.dumps(body).encode())
    else:
        resp = urlopen(req)
    return json.loads(resp.read())


def get_sheet_name(sheet_id):
    """Auto-detect the name of the first sheet tab."""
    if sheet_id in _sheet_name_cache:
        return _sheet_name_cache[sheet_id]
    url = f"{SHEETS_API}/{sheet_id}?fields=sheets.properties"
    result = sheets_request("GET", url)
    name = result["sheets"][0]["properties"]["title"]
    _sheet_name_cache[sheet_id] = name
    return name


def _q(name):
    """Quote and URL-encode a sheet name for use in Sheets API URLs."""
    quoted = f"'{name}'" if " " in name else name
    return quote(quoted, safe="!:'")  # safe chars per Sheets API


def read_sheet(sheet_id):
    """Read all values from the first sheet."""
    name = get_sheet_name(sheet_id)
    url = f"{SHEETS_API}/{sheet_id}/values/{_q(name)}"
    result = sheets_request("GET", url)
    rows = result.get("values", [])
    print(json.dumps(rows))


def write_sheet(sheet_id, rows):
    """Overwrite entire sheet with provided rows (2D array)."""
    name = get_sheet_name(sheet_id)
    # Clear first
    clear_url = f"{SHEETS_API}/{sheet_id}/values/{_q(name)}:clear"
    sheets_request("POST", clear_url)

    # Write
    update_url = f"{SHEETS_API}/{sheet_id}/values/{_q(name)}!A1?valueInputOption=RAW"
    sheets_request("PUT", update_url, {"values": rows})
    print(f"OK: wrote {len(rows)} rows")


def append_row(sheet_id, row):
    """Append a single row to the sheet."""
    name = get_sheet_name(sheet_id)
    url = f"{SHEETS_API}/{sheet_id}/values/{_q(name)}!A:I:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS"
    sheets_request("POST", url, {"values": [row]})
    print("OK: appended row")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    sheet_id = sys.argv[2]

    if command == "read":
        read_sheet(sheet_id)

    elif command == "write":
        if len(sys.argv) < 4:
            print("ERROR: write requires rows_json argument", file=sys.stderr)
            sys.exit(1)
        rows = json.loads(sys.argv[3])
        write_sheet(sheet_id, rows)

    elif command == "append":
        if len(sys.argv) < 4:
            print("ERROR: append requires row_json argument", file=sys.stderr)
            sys.exit(1)
        row = json.loads(sys.argv[3])
        append_row(sheet_id, row)

    else:
        print(f"ERROR: unknown command '{command}'", file=sys.stderr)
        sys.exit(1)
