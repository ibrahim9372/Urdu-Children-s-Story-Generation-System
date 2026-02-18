"""
Story Generator — BPE-integrated, optimised, streaming-capable
---------------------------------------------------------------
Generates Urdu stories via an interpolated trigram language model,
using proper BPE encoding for seed tokens and sparse probability
lookups for fast inference.
"""

import random
from typing import Generator, List, Tuple

from tokenizer_utils import decode_token, encode, get_tokenizer
from model_loader import build_indexes, load_ngram_counts

# ---------------------------------------------------------------------------
# Lazy-loaded model state
# ---------------------------------------------------------------------------
_model = None
_loaded = False


def _ensure_loaded() -> None:
    global _model, _loaded
    if not _loaded:
        uni, bi, tri, total = load_ngram_counts()
        _model = build_indexes(uni, bi, tri, total)
        _loaded = True


# ---------------------------------------------------------------------------
# Core probability computation (sparse)
# ---------------------------------------------------------------------------


def _next_token_probs(w1: int, w2: int) -> List[float]:
    """Return interpolated P(w3 | w1, w2) for every token in vocab.

    Uses pre-computed unigram base plus sparse bigram/trigram updates
    so we only touch the vocabulary entries that have non-zero higher-order
    probability — vastly faster than iterating the full vocab.
    """
    m = _model
    l1, l2, _ = m["lambdas"]

    # Start from unigram base (pre-computed λ₃ · P_uni for each token)
    probs = list(m["base_probs"])

    # Sparse bigram update: only tokens that follow w2
    if w2 in m["bigram_next"]:
        c1_ctx = m["uni_counts"].get(w2, 0)
        if c1_ctx > 0:
            for w3, c2 in m["bigram_next"][w2].items():
                idx = m["vocab_index"].get(w3)
                if idx is not None:
                    probs[idx] += l2 * (c2 / c1_ctx)

    # Sparse trigram update: only tokens that follow (w1, w2)
    key = (w1, w2)
    if key in m["trigram_next"]:
        c2_ctx = m["bi_counts"].get(key, 0)
        if c2_ctx > 0:
            for w3, c3 in m["trigram_next"][key].items():
                idx = m["vocab_index"].get(w3)
                if idx is not None:
                    probs[idx] += l1 * (c3 / c2_ctx)

    return probs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _get_eot_ids() -> frozenset:
    tokenizer = get_tokenizer()
    eots = []
    # Find all variants of EOT in vocabulary
    for tid, tstr in tokenizer.vocab.items():
        if tstr in ("<EOT>", "<EOT></w>"):
            eots.append(tid)
    return frozenset(eots)

def generate_story(prefix: str, max_length: int = 150) -> Tuple[str, List[str]]:
    """Generate a complete story continuation (blocking).

    Returns (continuation_text, seed_words).
    """
    _ensure_loaded()
    _eot_ids = _get_eot_ids()

    words = prefix.strip().split()
    if len(words) < 2:
        raise ValueError("Prefix must contain at least 2 Urdu words")

    encoded_prefix = encode(prefix)
    if len(encoded_prefix) < 2:
        raise ValueError("Prefix too short after BPE encoding — please provide more text")

    story_tokens = list(encoded_prefix)
    vocab = _model["vocab"]

    full_text = prefix # Track text for deduplication
    continuation_chunks = []

    for _ in range(max_length):
        w1, w2 = story_tokens[-2], story_tokens[-1]
        probs = _next_token_probs(w1, w2)

        if sum(probs) == 0:
            break

        next_token = random.choices(vocab, weights=probs, k=1)[0]
        story_tokens.append(next_token)

        if next_token in _eot_ids:
            break

        decoded = decode_token(next_token)
        if decoded:
            # Deduplication logic: If we already have a period, don't add another one immediately
            if decoded.strip() == "۔" and full_text.strip().endswith("۔"):
                continue
            
            continuation_chunks.append(decoded)
            full_text += decoded

    cleaned = " ".join("".join(continuation_chunks).split())
    return cleaned, words[:2]


def generate_story_streaming(
    prefix: str, max_length: int = 150
) -> Generator[str, None, None]:
    """Yield decoded text chunks one token at a time (for SSE streaming).

    Yields the continuation only — prefix is not streamed since the user
    already typed it.
    """
    _ensure_loaded()
    _eot_ids = _get_eot_ids()

    words = prefix.strip().split()
    if len(words) < 2:
        raise ValueError("Prefix must contain at least 2 Urdu words")

    encoded_prefix = encode(prefix)
    if len(encoded_prefix) < 2:
        raise ValueError("Prefix too short after BPE encoding — please provide more text")

    story_tokens = list(encoded_prefix)
    vocab = _model["vocab"]
    
    current_text = prefix

    for _ in range(max_length):
        w1, w2 = story_tokens[-2], story_tokens[-1]
        probs = _next_token_probs(w1, w2)

        if sum(probs) == 0:
            break

        next_token = random.choices(vocab, weights=probs, k=1)[0]
        story_tokens.append(next_token)

        if next_token in _eot_ids:
            break

        decoded = decode_token(next_token)
        if decoded:
            # Deduplication logic: prevents double "۔" at the end
            if decoded.strip() == "۔" and current_text.strip().endswith("۔"):
                continue
                
            current_text += decoded
            yield decoded
