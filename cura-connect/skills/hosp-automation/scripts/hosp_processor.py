#!/usr/bin/env python3
"""
hosp_processor.py — HOSP automation main script.

For every unread email from hosp@socialstyrelsen.se in max.nerdal@curaconnect.se:
  1. Extract the portal URL from the email body
  2. Open the portal with headless Playwright, accept GDPR
  3. Extract personnummer and full name from #contentContainer
  4. Capture the portal page as a real PDF (page.pdf())
  5. Find the candidate in recman by first + last name
  6. Upload the PDF to the candidate's file section
  7. Mark the Gmail email as read

Runs unattended. Logs to stdout and hosp.log.

Usage:
    python3 hosp_processor.py
"""
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gmail_client import GmailClient
from portal_scraper import PortalScraper
from recman_client import RecmanClient

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.md"
LOG_PATH = Path(__file__).resolve().parents[1] / "hosp.log"
# Pending PDFs saved here when upload fails — retried on next run without re-opening portal
PENDING_DIR = Path(__file__).resolve().parents[1] / "pending"


def load_config(path: Path) -> dict:
    config = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            config[key.strip()] = val.strip()
    return config


def setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_PATH),
        ],
    )


def save_pending(msg_id: str, filename: str, candidate_id: str | None, pdf_bytes: bytes) -> None:
    """
    Save PDF + metadata to disk immediately after scraping.
    Called before any upload attempt — ensures data is never lost if upload fails.
    candidate_id may be None if recman lookup hasn't happened yet.
    """
    PENDING_DIR.mkdir(exist_ok=True)
    (PENDING_DIR / f"{msg_id}.pdf").write_bytes(pdf_bytes)
    (PENDING_DIR / f"{msg_id}.json").write_text(json.dumps({
        "msg_id": msg_id,
        "filename": filename,
        "candidate_id": candidate_id,
    }))


def update_pending_candidate(msg_id: str, candidate_id: str) -> None:
    """Update the candidate_id in an existing pending record."""
    meta_file = PENDING_DIR / f"{msg_id}.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        meta["candidate_id"] = candidate_id
        meta_file.write_text(json.dumps(meta))


def delete_pending(msg_id: str) -> None:
    """Remove pending files after successful upload."""
    (PENDING_DIR / f"{msg_id}.pdf").unlink(missing_ok=True)
    (PENDING_DIR / f"{msg_id}.json").unlink(missing_ok=True)


def retry_pending(recman: RecmanClient, gmail: GmailClient, log: logging.Logger) -> None:
    """
    Retry any previously saved PDFs.
    Handles two cases:
    - candidate_id known: go straight to upload
    - candidate_id None: candidate lookup failed last time, skip (needs manual fix)
    """
    if not PENDING_DIR.exists():
        return
    for meta_file in sorted(PENDING_DIR.glob("*.json")):
        meta = json.loads(meta_file.read_text())
        msg_id = meta["msg_id"]
        pdf_file = PENDING_DIR / f"{msg_id}.pdf"

        if not pdf_file.exists():
            meta_file.unlink(missing_ok=True)
            continue

        candidate_id = meta.get("candidate_id")
        if not candidate_id:
            log.warning(
                f"[{msg_id}] Pending PDF '{meta['filename']}' has no candidate_id — "
                f"find the candidate in recman manually and update pending/{msg_id}.json"
            )
            continue

        log.info(f"[{msg_id}] Retrying upload: {meta['filename']} → candidateId={candidate_id}")
        uploaded = recman.upload_file(candidate_id, meta["filename"], pdf_file.read_bytes())
        if uploaded:
            log.info(f"[{msg_id}] Upload succeeded — marking email as read")
            gmail.mark_as_read(msg_id)
            delete_pending(msg_id)
        else:
            log.error(f"[{msg_id}] Upload failed again — will retry next run")


def main():
    setup_logging()
    log = logging.getLogger(__name__)

    if not CONFIG_PATH.exists():
        log.error(f"config.md not found at {CONFIG_PATH}. Copy config.example.md and fill in values.")
        sys.exit(1)

    config = load_config(CONFIG_PATH)
    gmail = GmailClient(
        credentials_path=config["GMAIL_CREDENTIALS_PATH"],
        token_path=config["GMAIL_TOKEN_PATH"],
    )
    recman = RecmanClient(api_key=config["RECMAN_API_KEY"])

    # First retry any previously failed uploads (portal already consumed — use saved PDF)
    retry_pending(recman, gmail, log)

    log.info("Checking for unread HOSP emails...")
    emails = gmail.list_unread_hosp()
    log.info(f"Found {len(emails)} unread HOSP email(s)")

    if not emails:
        log.info("Nothing to do.")
        return

    with PortalScraper() as scraper:
        for email in emails:
            msg_id = email["id"]
            portal_url = email["portal_url"]
            received = email["received"]

            if not portal_url:
                log.warning(f"[{msg_id}] No portal URL found in email — skipping")
                continue

            log.info(f"[{msg_id}] Opening portal: {portal_url}")

            try:
                result = scraper.process(portal_url)
            except Exception as e:
                log.error(f"[{msg_id}] Portal scraping failed: {e}")
                continue

            pin = result["pin"]
            name = result["name"]
            pdf_bytes = result["pdf_bytes"]
            filename = f"{pin} {name} {received.strftime('%Y-%m-%d')}.pdf"

            log.info(f"[{msg_id}] Extracted — PIN: {pin}  Name: {name}  File: {filename}")

            # Save to disk immediately — portal is now consumed, this is our only copy
            save_pending(msg_id, filename, candidate_id=None, pdf_bytes=pdf_bytes)
            log.info(f"[{msg_id}] PDF saved locally: pending/{msg_id}.pdf")

            candidate = recman.find_candidate(result["first_name"], result["last_name"])
            if not candidate:
                log.error(
                    f"[{msg_id}] Could not find '{name}' in recman — PDF saved locally. "
                    f"Add candidateId to pending/{msg_id}.json manually to retry."
                )
                continue

            candidate_id = candidate["candidateId"]
            log.info(f"[{msg_id}] Found candidate — ID: {candidate_id}")
            update_pending_candidate(msg_id, candidate_id)

            uploaded = recman.upload_file(candidate_id, filename, pdf_bytes)
            if not uploaded:
                log.error(f"[{msg_id}] Upload failed — PDF kept in pending/, will retry next run")
                continue

            log.info(f"[{msg_id}] Uploaded '{filename}' to candidate {candidate_id}")
            gmail.mark_as_read(msg_id)
            log.info(f"[{msg_id}] Marked as read ✓")
            delete_pending(msg_id)

    log.info("Done.")


if __name__ == "__main__":
    main()
