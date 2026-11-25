"""Five Hundred Rubber Bands — one-liner entry for make.fun.

Writes the locked final review line to /output/entry.txt.

Why this file is shaped the way it is
--------------------------------------
* The entry text is a *constant*, not built at runtime. The bounty wants
  one exact line, so there is no templating, no randomness and no input
  handling that could drift the wording by a character.
* Validation, writing and verification are three separate functions
  (``validate`` / ``write_entry`` / ``verify_written``) instead of one
  blob in ``main``. Each step can then be reasoned about — and tested —
  on its own, and a failure points at the exact step that broke.
* Verification reads the file back and compares it byte-for-byte with
  the validated text. Writing "succeeded" is not proof; the round-trip
  read is. If disk, encoding or a stray newline corrupts the file, the
  run fails loudly here instead of shipping a malformed entry.
* The output has no trailing newline: the entry must be a single line
  of 1-200 UTF-8 characters, and a newline would be an extra character
  the judges never asked for.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Locked entry text — do not change a single character.
#
# Chosen line (141 characters): a boring object (a bag of 500 rubber
# bands) reviewed in one line — bought in bulk, barely used, the rest
# fused into one giant band in a drawer, outlasting two relationships.
# The humour is the contrast between the object's dullness and the
# deadpan "Five stars" verdict.
# ---------------------------------------------------------------------------
ENTRY_TEXT = (
    "Bought 500 in 2016, used 12. The rest live in a drawer, slowly "
    "fusing into one giant rubber band. Five stars. It outlasted two "
    "relationships."
)

OUTPUT_PATH = Path("/output/entry.txt")

# Bounty limits for the review line, in UTF-8 characters.
MIN_LEN = 1
MAX_LEN = 200

# Character count of the locked line above, pinned so a silent edit to
# ENTRY_TEXT (adding/removing a word) is caught even if it still passes
# the 1-200 range check.
EXPECTED_CHAR_COUNT = 141


def validate(text: str) -> str:
    """Return ``text`` if it is a valid one-liner, else raise ValueError.

    Checks, in order: no leading/trailing whitespace, no embedded
    newline/carriage-return (must be a single line), not blank, length
    inside the bounty range, and exactly the pinned character count.
    Raising — rather than silently trimming or truncating — is deliberate:
    any "fix" applied here would change the judged text.
    """
    if text != text.strip():
        raise ValueError("entry text must not have leading/trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry text must be a single line")
    if not text:
        raise ValueError("entry text must not be blank")
    size = len(text.encode("utf-8"))
    if not MIN_LEN <= size <= MAX_LEN:
        raise ValueError(
            f"entry text must be {MIN_LEN}-{MAX_LEN} UTF-8 characters, got {size}"
        )
    if size != EXPECTED_CHAR_COUNT:
        raise ValueError(
            f"entry text must be exactly {EXPECTED_CHAR_COUNT} characters, "
            f"got {size} — the locked line was edited"
        )
    return text


def write_entry(text: str, path: Path = OUTPUT_PATH) -> int:
    """Write the validated entry to ``path``; return bytes written.

    Creates the output directory if needed and writes UTF-8 with no
    trailing newline, so the file content is exactly the entry line.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.write_text(text, encoding="utf-8")


def verify_written(path: Path, expected_text: str) -> str:
    """Read ``path`` back and prove it matches ``expected_text`` exactly.

    Compares the full string and the raw byte length. Returns the text
    read back, so callers can use the verified on-disk content rather
    than trusting the in-memory copy. Raises AssertionError on mismatch.
    """
    written = path.read_text(encoding="utf-8")
    if written != expected_text:
        raise AssertionError(
            f"round-trip mismatch: file holds {written!r}, "
            f"expected {expected_text!r}"
        )
    raw = path.read_bytes()
    if len(raw) != len(expected_text.encode("utf-8")):
        raise AssertionError(
            f"byte-length mismatch: file is {len(raw)} bytes, "
            f"expected {len(expected_text.encode('utf-8'))}"
        )
    return written


def main() -> None:
    """Validate the locked line, write it, verify it, report it."""
    text = validate(ENTRY_TEXT)
    write_entry(text)
    verified = verify_written(OUTPUT_PATH, text)
    print(f"Wrote {len(verified)} chars to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
