"""
Model Loader — artifact loading & optimised index building
-----------------------------------------------------------
Loads trigram model pickle files and builds sparse lookup indexes
for fast generation.

Fixes addressed:
  - 4A-05: removed dead load_tokenizer_vocab()
  - 3A-02: builds sparse bigram/trigram next-token indexes
"""

import pickle
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ARTIFACTS_DIR = (
    Path(__file__).resolve().parent.parent / "Trigram_LM" / "artifacts"
)

# ---------------------------------------------------------------------------
# Raw count loading
# ---------------------------------------------------------------------------


def load_ngram_counts() -> Tuple[Dict, Dict, Dict, int]:
    """Load pre-computed Counter objects from pickle files."""
    uni_path = ARTIFACTS_DIR / "unigrams.pkl"
    bi_path = ARTIFACTS_DIR / "bigrams.pkl"
    tri_path = ARTIFACTS_DIR / "trigrams.pkl"

    for p in (uni_path, bi_path, tri_path):
        if not p.exists():
            raise FileNotFoundError(
                f"Model artifact not found: {p}. Run ngram_counter.py first."
            )

    with open(uni_path, "rb") as f:
        uni_counts = pickle.load(f)
    with open(bi_path, "rb") as f:
        bi_counts = pickle.load(f)
    with open(tri_path, "rb") as f:
        tri_counts = pickle.load(f)

    total_token_count = sum(uni_counts.values())
    return uni_counts, bi_counts, tri_counts, total_token_count


# ---------------------------------------------------------------------------
# Optimised index building
# ---------------------------------------------------------------------------


def build_indexes(
    uni_counts: Dict,
    bi_counts: Dict,
    tri_counts: Dict,
    total_token_count: int,
    lambdas: Tuple[float, float, float] = (0.8, 0.15, 0.05),
) -> Dict[str, Any]:
    """
    Pre-compute lookup structures for O(sparse) generation instead of O(V).

    Returns a dict with:
      vocab            — ordered list of all unique tokens
      vocab_index      — token → position mapping
      base_probs       — λ₃·P_uni(t) for every token (pre-computed)
      bigram_next      — w → {w_next: count}
      trigram_next     — (w1,w2) → {w3: count}
      uni_counts       — raw unigram counts  (for bigram context denominator)
      bi_counts        — raw bigram  counts  (for trigram context denominator)
      lambdas          — interpolation weights
    """
    l1, l2, l3 = lambdas

    vocab: List[str] = list(uni_counts.keys())
    vocab_index: Dict[str, int] = {t: i for i, t in enumerate(vocab)}

    # Pre-compute unigram base: λ₃ · P_uni(t)
    base_probs: List[float] = [
        l3 * (uni_counts[t] / total_token_count) for t in vocab
    ]

    # Sparse bigram index: w → {w_next: count}
    bigram_next: Dict[str, Dict[str, int]] = defaultdict(dict)
    for (wa, wb), count in bi_counts.items():
        bigram_next[wa][wb] = count

    # Sparse trigram index: (w1,w2) → {w3: count}
    trigram_next: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(dict)
    for (wa, wb, wc), count in tri_counts.items():
        trigram_next[(wa, wb)][wc] = count

    return {
        "vocab": vocab,
        "vocab_index": vocab_index,
        "base_probs": base_probs,
        "bigram_next": dict(bigram_next),
        "trigram_next": dict(trigram_next),
        "uni_counts": uni_counts,
        "bi_counts": bi_counts,
        "lambdas": lambdas,
    }
