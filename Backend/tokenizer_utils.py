"""
BPE Tokenizer — encode / decode utilities (Integrated with official BPETokenizer)
--------------------------------------------------------------------------------
Loads pre-trained BPE merge rules and vocabulary from Tokenizer/artifacts 
using the official BPETokenizer class for 100% consistency.
"""

import sys
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Paths & Imports
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
TOKENIZER_DIR = BASE_DIR / "Tokenizer"
ARTIFACTS_DIR = TOKENIZER_DIR / "artifacts"
VOCAB_PATH = ARTIFACTS_DIR / "final_token.json"
MERGES_PATH = ARTIFACTS_DIR / "ordered_merges.txt"

# Add Tokenizer to sys.path to import the official class
sys.path.append(str(TOKENIZER_DIR))
try:
    from bpe_tokenizer import BPETokenizer
except ImportError:
    # Fallback if someone moves the folders
    print(f"Error: BPETokenizer not found in {TOKENIZER_DIR}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Module-level lazy state
# ---------------------------------------------------------------------------
_tokenizer_instance = None


def get_tokenizer():
    """Lazy-load and return the BPETokenizer instance."""
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = BPETokenizer()
        if VOCAB_PATH.exists() and MERGES_PATH.exists():
            _tokenizer_instance.load(VOCAB_PATH, MERGES_PATH)
        else:
            raise FileNotFoundError(
                f"Tokenizer artifacts not found at {ARTIFACTS_DIR}. "
                "Please run Tokenizer/train_bpe.py first."
            )
    return _tokenizer_instance


# ---------------------------------------------------------------------------
# Public API (Integer-ID based)
# ---------------------------------------------------------------------------


def encode(text: str) -> List[int]:
    """
    BPE-encode a text string into a list of integer token IDs.
    Delegates to the official BPETokenizer implementation.
    """
    return get_tokenizer().encode(text)


def decode_token(token_id: int) -> str:
    """
    Decode a single integer token ID back to a readable text fragment.
    Handles space replacement for </w> and specific special token formatting.
    """
    tokenizer = get_tokenizer()
    # Using the underlying dict to get the raw token string
    token = tokenizer.vocab.get(token_id, "<unk>")
    
    # Mirroring the cleanup logic from generator's original needs
    if token in ("<EOT></w>", "<EOT>"):
        return ""
    if token in ("<EOS></w>", "<EOS>"):
        return "۔ "
    if token in ("<EOP></w>", "<EOP>"):
        return "\n\n"
        
    if token.endswith("</w>"):
        return token[:-4] + " "
    return token


def decode(token_ids: List[int]) -> str:
    """
    Decode a full list of integer token IDs back to 100% clean Urdu text.
    Uses the official decode logic which handles punctuation and special tokens.
    """
    return get_tokenizer().decode(token_ids)
