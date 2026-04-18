"""
gmail_client.py — Gmail API wrapper for HOSP automation.

Lists unread emails from hosp@socialstyrelsen.se, extracts portal URLs,
and marks emails as read after successful processing.

Requires a valid token at GMAIL_TOKEN_PATH (created by oauth_flow.py).
"""
import base64
import re
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

HOSP_QUERY = "from:hosp@socialstyrelsen.se is:unread"
PORTAL_URL_RE = re.compile(r'https?://[^\s"<>\']*socialstyrelsen\.se[^\s"<>\']*')


class GmailClient:
    def __init__(self, credentials_path: str, token_path: str):
        self._creds_path = Path(credentials_path).expanduser()
        self._token_path = Path(token_path).expanduser()
        self.__service = None

    def list_unread_hosp(self) -> list[dict]:
        """
        Return a list of unread HOSP emails with portal_url and received datetime.
        Each item: {"id": str, "portal_url": str | None, "received": datetime}
        """
        svc = self._get_service()
        result = svc.users().messages().list(userId="me", q=HOSP_QUERY).execute()
        messages = result.get("messages", [])

        emails = []
        for m in messages:
            msg = svc.users().messages().get(
                userId="me", id=m["id"], format="full"
            ).execute()
            portal_url = self._extract_portal_url(msg)
            received_ms = int(msg.get("internalDate", 0))
            received = datetime.fromtimestamp(received_ms / 1000)
            emails.append({
                "id": m["id"],
                "portal_url": portal_url,
                "received": received,
            })

        return emails

    def mark_as_read(self, message_id: str) -> None:
        svc = self._get_service()
        svc.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()

    def _get_service(self):
        if not hasattr(self, "__service") or self.__service is None:
            creds = None
            if self._token_path.exists():
                creds = Credentials.from_authorized_user_file(str(self._token_path), SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self._token_path.write_text(creds.to_json())
                else:
                    raise RuntimeError(
                        f"Gmail token missing or expired. Run oauth_flow.py first.\n"
                        f"Expected token at: {self._token_path}"
                    )
            self.__service = build("gmail", "v1", credentials=creds)
        return self.__service

    def _extract_portal_url(self, msg: dict) -> str | None:
        body_text = self._extract_body_text(msg.get("payload", {}))
        match = PORTAL_URL_RE.search(body_text)
        return match.group(0) if match else None

    def _extract_body_text(self, payload: dict) -> str:
        parts = payload.get("parts", [])
        if parts:
            return "\n".join(self._extract_body_text(p) for p in parts)
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
        return ""
