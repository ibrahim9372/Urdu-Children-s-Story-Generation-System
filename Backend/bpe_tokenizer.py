"""
BPE Tokenizer — encode / decode utilities
------------------------------------------
Loads pre-trained BPE merge rules from Tokenizer/artifacts and provides
encode() / decode() functions for the Backend generation pipeline.

Fixes addressed:
  - 4A-02 / XA-01: BPE encoding integrated into generation pipeline
  - 2A-05:         encode() and decode() API exposed as reusable module
"""

import re
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MERGES_PATH = (
    Path(__file__).resolve().parent.parent / "Tokenizer" / "artifacts" / "ordered_merges.txt"
)

# ---------------------------------------------------------------------------
# Module-level lazy state
# ---------------------------------------------------------------------------
_merges: List[Tuple[str, str]] = []
_loaded = False


def _ensure_loaded() -> None:
    global _merges, _loaded
    if not _loaded:
        _merges = _load_merges(MERGES_PATH)
        _loaded = True


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_merges(path: Path) -> List[Tuple[str, str]]:
    """Load ordered BPE merge rules from the artifacts file."""
    if not path.exists():
        raise FileNotFoundError(f"BPE merge rules not found at {path}")

    merges: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2:
                merges.append((parts[0], parts[1]))
    return merges


def _tokenize_word(word: str, merges: List[Tuple[str, str]]) -> List[str]:
    """Apply BPE merge rules to a single word → list of sub-tokens."""
    tokens = list(word) + ["</w>"]
    for c1, c2 in merges:
        new_tokens: List[str] = []
        i = 0
        while i < len(tokens):
            if (
                i < len(tokens) - 1
                and tokens[i] == c1
                and tokens[i + 1] == c2
            ):
                new_tokens.append(c1 + c2)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return tokens


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def encode(text: str) -> List[str]:
    """
    BPE-encode a text string into a list of sub-tokens.

    Replicates the preprocessing used during tokenizer training:
      • strips non-word / non-whitespace / non-angle-bracket chars
        (same regex as train_bpe.py  get_word_frequencies)
      • splits on whitespace
      • special tokens (<EOS>, <EOP>, <EOT>) kept atomic with </w>
      • regular words BPE-tokenised with learned merges
    """
    _ensure_loaded()

    # Match training-time preprocessing — strip punctuation
    cleaned = re.sub(r"[^\w\s<>]", " ", text)
    words = cleaned.split()

    encoded: List[str] = []
    for word in words:
        if word.startswith("<") and word.endswith(">"):
            encoded.append(word + "</w>")
        else:
            encoded.extend(_tokenize_word(word, _merges))
    return encoded


def decode_token(token: str) -> str:
    """Decode a single BPE token back to a readable text fragment."""
    if token in ("<EOT></w>", "<EOT>"):
        return ""
    if token in ("<EOS></w>", "<EOS>"):
        return "۔ "
    if token in ("<EOP></w>", "<EOP>"):
        return "\n\n"
    if token.endswith("</w>"):
        return token[:-4] + " "
    return token


def decode(tokens: List[str]) -> str:
    """Decode a full list of BPE tokens back to readable text."""
    return "".join(decode_token(t) for t in tokens).strip()
