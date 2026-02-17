import random
from typing import List, Tuple
from model_loader import load_ngram_counts


uni_counts, bi_counts, tri_counts, total_token_count = None, None, None, None
_is_loaded = False


def _ensure_loaded():
    global uni_counts, bi_counts, tri_counts, total_token_count, _is_loaded
    if not _is_loaded:
        uni_counts, bi_counts, tri_counts, total_token_count = load_ngram_counts()
        _is_loaded = True


def get_interpolated_prob(
    w1: str, w2: str, w3: str, lambdas: Tuple[float, float, float] = (0.8, 0.15, 0.05)
) -> float:
    _ensure_loaded()
    l1, l2, l3 = lambdas

    c3 = tri_counts.get((w1, w2, w3), 0)
    c2_context = bi_counts.get((w1, w2), 0)
    p_tri = c3 / c2_context if c2_context > 0 else 0

    c2 = bi_counts.get((w2, w3), 0)
    c1_context = uni_counts.get(w2, 0)
    p_bi = c2 / c1_context if c1_context > 0 else 0

    c1 = uni_counts.get(w3, 0)
    p_uni = c1 / total_token_count if total_token_count > 0 else 0

    return (l1 * p_tri) + (l2 * p_bi) + (l3 * p_uni)


def generate_story(prefix: str, max_length: int = 150) -> Tuple[str, List[str]]:
    _ensure_loaded()

    words = prefix.strip().split()
    if len(words) < 2:
        raise ValueError("Prefix must contain at least 2 words")

    seed_w1 = words[0]
    seed_w2 = words[1]

    story = [seed_w1 + "</w>", seed_w2 + "</w>"]
    vocab = list(uni_counts.keys())

    for _ in range(max_length):
        w1, w2 = story[-2], story[-1]

        probs = [get_interpolated_prob(w1, w2, t) for t in vocab]

        if sum(probs) == 0:
            break

        next_token = random.choices(vocab, weights=probs, k=1)[0]
        story.append(next_token)

        if next_token == "<EOT>" or next_token == "<EOT></w>":
            break

    raw_output = "".join(story).replace("</w>", " ").replace("<EOT>", "")
    cleaned_story = " ".join(raw_output.split())

    return cleaned_story, [seed_w1, seed_w2]
