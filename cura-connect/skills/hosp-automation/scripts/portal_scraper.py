"""
portal_scraper.py — Playwright scraper for the Socialstyrelsen HOSP portal.

Opens a portal URL, accepts the GDPR notice, extracts personnummer and full name
from #contentContainer, and captures the page as a real PDF using page.pdf().
This is the programmatic equivalent of printer → Save as PDF.
"""
import re
from playwright.sync_api import sync_playwright, Page

# Matches Swedish personnummer: YYYYMMDD-NNNN or YYMMDD-NNNN
PIN_RE = re.compile(r'\b(\d{6,8}[-–]\d{4})\b')

# Matches capitalized Swedish full names (at least two words)
NAME_RE = re.compile(r'\b([A-ZÅÄÖ][a-zåäö]+(?:[ -][A-ZÅÄÖ][a-zåäö]+)+)\b')

# Buttons to click in order when accepting GDPR / opening the message
GDPR_BUTTONS = ["Öppna meddelandet", "Fortsätt", "Acceptera", "OK", "Jag förstår"]


class PortalScraper:
    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        return self

    def __exit__(self, *args):
        self._browser.close()
        self._pw.stop()

    def process(self, portal_url: str) -> dict:
        """
        Navigate to portal_url, accept GDPR, extract PIN + name, capture PDF.

        Returns:
            {
                "pin":        "19980414-0060",
                "name":       "Emma Pettersson",
                "first_name": "Emma",
                "last_name":  "Pettersson",
                "pdf_bytes":  b"...",
            }
        """
        page = self._browser.new_page()
        try:
            page.goto(portal_url, wait_until="networkidle", timeout=30_000)
            self._click_gdpr_buttons(page)

            text = page.locator("#contentContainer").inner_text(timeout=10_000)
            pin, first_name, last_name = self._parse(text)

            pdf_bytes = page.pdf(format="A4", print_background=True)

            return {
                "pin": pin,
                "name": f"{first_name} {last_name}",
                "first_name": first_name,
                "last_name": last_name,
                "pdf_bytes": pdf_bytes,
            }
        finally:
            page.close()

    def _click_gdpr_buttons(self, page: Page) -> None:
        for label in GDPR_BUTTONS:
            try:
                btn = page.get_by_text(label, exact=False)
                if btn.is_visible(timeout=3_000):
                    btn.click()
                    page.wait_for_load_state("networkidle", timeout=10_000)
            except Exception:
                pass

    def _parse(self, text: str) -> tuple[str, str, str]:
        pin_match = PIN_RE.search(text)
        if not pin_match:
            raise ValueError(
                f"Could not find personnummer in portal text.\n"
                f"First 500 chars:\n{text[:500]}"
            )
        pin = pin_match.group(1)

        name_matches = NAME_RE.findall(text)
        if not name_matches:
            raise ValueError(
                f"Could not find a name in portal text.\n"
                f"First 500 chars:\n{text[:500]}"
            )

        # Longest match is most likely the full name
        full_name = max(name_matches, key=len)
        parts = full_name.split()
        first_name = parts[0]
        # Use only the last word as lastName — recman doesn't store middle names
        last_name = parts[-1]

        return pin, first_name, last_name
