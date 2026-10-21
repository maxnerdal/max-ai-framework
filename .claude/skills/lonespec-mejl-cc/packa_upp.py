"""Unpack a Recman payslip zip and print each PDF's first lines of text.

    python3 packa_upp.py <zip> <target directory>

The target directory must not exist, or must be empty: a payslip run that silently mixes in last
month's files would pair the wrong PDF with a consultant. Entry names are flattened to a basename,
so a crafted path inside the archive cannot write outside the target.

Prints the absolute path of every PDF, which is what the Gmail draft attaches, and the opening lines
of its text, which is where the consultant's name stands. Matching is left to the reader: Recman does
not name the files after the person consistently enough to trust a filename.
"""

import sys
import zipfile
from pathlib import Path
from subprocess import run

LINES = 12
"""Lines of text printed per PDF. Enough to carry the name and the period, little enough that no
amount needs to be read out."""


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
    done = run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    if done.returncode != 0:
        return f"(pdftotext misslyckades: {done.stderr.strip()[:200]})"
    lines = [line.strip() for line in done.stdout.splitlines() if line.strip()]
    return "\n".join(f"    {line}" for line in lines[:LINES]) or "    (ingen text — skannad PDF?)"


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
