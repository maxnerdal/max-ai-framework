"""
recman_client.py — recman.io API wrapper for HOSP automation.

Finds candidates by name, uploads PDF to their file section.
Search is by firstName + lastName since the API has no personnummer filter.
"""
import logging
import requests

BASE_URL = "https://api.recman.io/v2"
log = logging.getLogger(__name__)


class RecmanClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def find_candidate(self, first_name: str, last_name: str) -> dict | None:
        """
        Search for a candidate by first and last name.
        Returns the candidate dict (with candidateId) or None.
        Logs a warning and returns None if multiple matches are found.
        """
        resp = requests.get(f"{BASE_URL}/get/", params={
            "key": self.api_key,
            "scope": "candidate",
            "fields": "firstName,lastName",
            "firstName": first_name,
            "lastName": last_name,
            "page": 1,
        })
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            log.warning(f"Candidate search failed: {data}")
            return None

        candidates = list(data.get("data", {}).values())

        if len(candidates) == 0:
            log.warning(f"No candidate found: {first_name} {last_name}")
            return None

        if len(candidates) > 1:
            ids = [c["candidateId"] for c in candidates]
            log.warning(
                f"Multiple candidates found for {first_name} {last_name}: {ids} — skipping. "
                f"Resolve manually in recman."
            )
            return None

        return candidates[0]

    def upload_file(self, candidate_id: str, filename: str, pdf_bytes: bytes) -> bool:
        """
        Upload a PDF to a candidate's Files tab.
        Returns True on success, False on failure.

        scope=candidate, operation=insert, file nested as data.file object.
        """
        import base64
        from datetime import datetime
        payload = {
            "key": self.api_key,
            "scope": "candidate",
            "operation": "insert",
            "data": {
                "candidateId": int(candidate_id),
                "file": {
                    "name": filename,
                    "extension": "pdf",
                    "base64": base64.b64encode(pdf_bytes).decode("ascii"),
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "candidateAccess": 0,
                },
            },
        }
        resp = requests.post(f"{BASE_URL}/post/", json=payload, timeout=60)
        resp.raise_for_status()

        try:
            data = resp.json()
            if data.get("success"):
                file_id = data.get("id") or (data.get("data") or {}).get("fileId")
                log.info(f"File uploaded — fileId={file_id}")
                return True
            log.error(f"Upload failed for candidateId={candidate_id}: {data}")
            return False
        except Exception:
            log.error(f"Unexpected upload response for candidateId={candidate_id}: {resp.text[:200]}")
            return False
