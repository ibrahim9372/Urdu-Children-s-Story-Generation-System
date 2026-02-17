import pickle
import json
from pathlib import Path
from typing import Tuple, Dict, Any


ARTIFACTS_DIR = Path(__file__).parent.parent / "Trigram_LM" / "artifacts"
TOKENIZER_DIR = Path(__file__).parent.parent / "Tokenizer" / "artifacts"


def get_project_path() -> Path:
    return Path(__file__).parent.parent


def load_ngram_counts() -> Tuple[Dict, Dict, Dict, int]:
    uni_path = ARTIFACTS_DIR / "unigrams.pkl"
    bi_path = ARTIFACTS_DIR / "bigrams.pkl"
    tri_path = ARTIFACTS_DIR / "trigrams.pkl"

    if not (uni_path.exists() and bi_path.exists() and tri_path.exists()):
        raise FileNotFoundError(
            "Model artifacts not found. Please run ngram_counter.py first."
        )

    with open(uni_path, "rb") as f:
        uni_counts = pickle.load(f)
    with open(bi_path, "rb") as f:
        bi_counts = pickle.load(f)
    with open(tri_path, "rb") as f:
        tri_counts = pickle.load(f)

    total_token_count = sum(uni_counts.values())

    return uni_counts, bi_counts, tri_counts, total_token_count


def load_tokenizer_vocab() -> Dict[str, Any]:
    tokens_path = TOKENIZER_DIR / "final_token.json"

    if not tokens_path.exists():
        raise FileNotFoundError(
            "Tokenizer artifacts not found. Please run train_bpe.py first."
        )

    with open(tokens_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model():
    return load_ngram_counts()
