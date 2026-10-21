"""Unpack a Recman payslip zip and print each PDF's first lines of text.

    python3 packa_upp.py <zip> <target directory>

The target directory must not exist, or must be empty: a payslip run that silently mixes in last
month's files would pair the wrong PDF with a consultant. Entry names are flattened to a basename,
so a crafted path inside the archive cannot write outside the target.

Prints the absolute path of every PDF, which is what the Gmail draft attaches, and the three things that
decide who it goes to: the name, the e-mail address and the period. Matching is left to the reader:
Recman does not name the files after the person consistently enough to trust a filename.

The specification also carries the consultant's home address, telephone number and pay, none of which the
mail needs, so they are deliberately not printed. A PDF the patterns do not fit falls back to its opening
lines, since a layout nobody has seen is worth looking at.
"""

import re
import sys
import zipfile
from pathlib import Path
from subprocess import run

FALLBACK_LINES = 6
"""Lines printed for a PDF whose name, address or period could not be found."""

MAIL = re.compile(r"E-post\s+(\S+@\S+)")
PERIOD = re.compile(r"Period:\s*(.+)")


def unpack(archive: Path, target: Path) -> list[Path]:
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"{target} är inte tom. Välj en ny mapp — gamla filer parar fel PDF med fel konsult.")
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with zipfile.ZipFile(archive) as zf:
        for entry in zf.infolist():
            if entry.is_dir():
                continue
            name = Path(entry.filename).name
            if not name or name.startswith("."):
                continue
            out = target / name
            out.write_bytes(zf.read(entry))
            written.append(out)
    return sorted(written)


def text_of(pdf: Path) -> str:
    """Who the PDF belongs to, and for which period. Nothing else is printed."""
    done = run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    if done.returncode != 0:
        return f"    (pdftotext misslyckades: {done.stderr.strip()[:200]})"
    lines = [line.strip() for line in done.stdout.splitlines() if line.strip()]
    if not lines:
        return "    (ingen text — skannad PDF?)"

    name = lines[0]
    mail = MAIL.search(done.stdout)
    period = PERIOD.search(done.stdout)
    if not mail or not period:
        missing = "mejladress" if not mail else "period"
        head = "\n".join(f"    {line}" for line in lines[:FALLBACK_LINES])
        return f"    ({missing} hittades inte — första raderna i stället, titta på filen)\n{head}"
    return (
        f"    namn:   {name}\n"
        f"    mejl:   {mail.group(1)}\n"
        f"    period: {period.group(1).strip()}"
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    files = unpack(Path(sys.argv[1]).expanduser(), Path(sys.argv[2]).expanduser())
    pdfs = [f for f in files if f.suffix.lower() == ".pdf"]
    other = [f for f in files if f not in pdfs]

    print(f"{len(pdfs)} PDF:er uppackade i {Path(sys.argv[2]).expanduser().resolve()}\n")
    for pdf in pdfs:
        print(pdf.resolve())
        print(text_of(pdf))
        print()
    if other:
        print("Annat i zipen (inga PDF:er, ingår inte i utskicket):")
        for f in other:
            print(f"  {f.name}")


if __name__ == "__main__":
    main()
