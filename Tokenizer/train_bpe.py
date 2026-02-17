"""
BPE Tokenizer Training Script for Urdu Children Stories
Trains tokenizer with a fixed cap of 191 merge operations.
Vocab size = special tokens + unique characters + 191 merges.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


# ── Paths ──────────────────────────────────────────────────────────────────────
# Use relative paths from this script's location
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "Data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

# Hardcoded path as requested by User
CORPUS_PATH = Path(r"C:\Users\hassa\OneDrive\Desktop\sem6\NLP\Assignement 1\urdu_tokenizer_training2.txt")

# If not found (e.g. on another machine), warn but try to proceed if possible or fail
if not CORPUS_PATH.exists():
    print(f"Warning: Corpus not found at {CORPUS_PATH}")

MERGES_FILE   = ARTIFACTS_DIR / "ordered_merges.txt"
TOKENS_FILE   = ARTIFACTS_DIR / "final_token.json"
CORPUS_ENCODED_FILE = ARTIFACTS_DIR / "corpus_encoded.json"

MAX_MERGES = 191   # hard cap on merge operations


# ── BPE Tokenizer ──────────────────────────────────────────────────────────────
class BPETokenizer:
    """
    Byte Pair Encoding Tokenizer implementation.
    Handles Urdu text tokenization using BPE algorithm with word-end markers
    for proper subword segmentation.
    """

    SPECIAL_TOKENS = {
        "<EOS>": 0,
        "<EOP>": 1,
        "<EOT>": 2,
        "<unk>": 3,
    }
    WORD_END = "</w>"

    def __init__(self, max_merges: int = 250):
        """
        Args:
            max_merges: Maximum number of BPE merge operations to perform.
                        Vocab size will be chars + special tokens + max_merges.
        """
        self.max_merges  = max_merges
        self.vocab:        Dict[int, str]          = {}
        self.token_to_id:  Dict[str, int]          = {}
        self.merges:       List[Tuple[str, str]]   = []

    # ── Training ───────────────────────────────────────────────────────────────

    def train(self, corpus: str) -> Dict:
        print(f"Training BPE tokenizer with max_merges={self.max_merges}")

        word_frequencies = self._pretokenize(corpus)
        print(f"Pre-tokenized into {len(word_frequencies)} unique words")

        self._initialize_vocab(word_frequencies)
        print(f"Initial vocabulary size (chars + special tokens): {len(self.vocab)}")
        print(f"Performing up to {self.max_merges} merge operations...")

        for i in range(self.max_merges):
            pair_frequencies = self._count_pairs(word_frequencies)

            if not pair_frequencies:
                print(f"  No more pairs to merge at iteration {i}. Stopping early.")
                break

            best_pair = max(pair_frequencies, key=lambda p: pair_frequencies[p])
            best_freq = pair_frequencies[best_pair]

            self.merges.append(best_pair)
            word_frequencies = self._merge_pair(word_frequencies, best_pair)

            new_token = best_pair[0] + best_pair[1]
            new_id = len(self.vocab)
            self.vocab[new_id]          = new_token
            self.token_to_id[new_token] = new_id

            if (i + 1) % 50 == 0:
                print(f"  Merge {i+1:>3}/{self.max_merges} | merged {best_pair!r} (freq={best_freq}) → '{new_token}'")

        print(f"\nTraining complete!")
        print(f"  Merges performed : {len(self.merges)}")
        print(f"  Final vocab size : {len(self.vocab)}")

        return {
            "vocab_size":    len(self.vocab),
            "num_merges":    len(self.merges),
            "unique_words":  len(word_frequencies),
        }

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _pretokenize(self, text: str) -> Dict[Tuple[str, ...], int]:
        words = text.split()
        word_frequencies: Counter = Counter()
        for word in words:
            if word in self.SPECIAL_TOKENS:
                word_frequencies[(word,)] += 1
            else:
                chars = tuple(word) + (self.WORD_END,)
                word_frequencies[chars] += 1
        return dict(word_frequencies)

    def _initialize_vocab(self, word_frequencies: Dict[Tuple[str, ...], int]):
        for token, token_id in self.SPECIAL_TOKENS.items():
            self.vocab[token_id]       = token
            self.token_to_id[token]    = token_id

        unique_chars: Set[str] = set()
        for word in word_frequencies:
            for char in word:
                if char != self.WORD_END:
                    unique_chars.add(char)

        # Also add WORD_END itself so it lives in vocab
        unique_chars.add(self.WORD_END)

        for char in sorted(unique_chars):
            if char not in self.token_to_id:
                new_id = len(self.vocab)
                self.vocab[new_id]       = char
                self.token_to_id[char]   = new_id

    def _count_pairs(self, word_frequencies: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, str], int]:
        pair_frequencies: Dict[Tuple[str, str], int] = defaultdict(int)
        for word, freq in word_frequencies.items():
            for i in range(len(word) - 1):
                pair_frequencies[(word[i], word[i + 1])] += freq
        return pair_frequencies

    def _merge_pair(self, word_frequencies: Dict[Tuple[str, ...], int], pair: Tuple[str, str]) -> Dict[Tuple[str, ...], int]:
        new_wf: Dict[Tuple[str, ...], int] = {}
        for word, freq in word_frequencies.items():
            new_wf[self._merge_word(word, pair)] = freq
        return new_wf

    def _merge_word(self, word: Tuple[str, ...], pair: Tuple[str, str]) -> Tuple[str, ...]:
        merged_token = pair[0] + pair[1]
        result, i = [], 0
        while i < len(word):
            if i < len(word) - 1 and word[i] == pair[0] and word[i+1] == pair[1]:
                result.append(merged_token)
                i += 2
            else:
                result.append(word[i])
                i += 1
        return tuple(result)

    # ── Encode / Decode ────────────────────────────────────────────────────────

    def encode(self, text: str) -> List[int]:
        words = text.split()
        tokens_list = []
        for word in words:
            if word in self.SPECIAL_TOKENS:
                tokens_list.append([word])
            else:
                tokens_list.append(list(word) + [self.WORD_END])

        for pair in self.merges:
            tokens_list = self._apply_merge(tokens_list, pair)

        token_ids = []
        for tokens in tokens_list:
            for token in tokens:
                token_ids.append(
                    self.token_to_id.get(token, self.SPECIAL_TOKENS["<unk>"])
                )
        return token_ids

    def _apply_merge(self, tokens_list: List[List[str]], pair: Tuple[str, str]) -> List[List[str]]:
        merged_token = pair[0] + pair[1]
        for tokens in tokens_list:
            i = 0
            while i < len(tokens) - 1:
                if tokens[i] == pair[0] and tokens[i+1] == pair[1]:
                    tokens[i] = merged_token
                    del tokens[i+1]
                else:
                    i += 1
        return tokens_list

    def decode(self, token_ids: List[int]) -> str:
        tokens = [self.vocab.get(tid, "<unk>") for tid in token_ids]
        result_parts = []
        for token in tokens:
            if token == self.WORD_END:
                result_parts.append(" ")
            else:
                result_parts.append(token)
        text = "".join(result_parts)
        for special in self.SPECIAL_TOKENS:
            text = text.replace(f" {special}", special).replace(f"{special} ", special)
        return text.strip()

    # ── Save / Load ────────────────────────────────────────────────────────────

    def save(self, vocab_path: str | Path, merges_path: str | Path):
        vocab_path  = Path(vocab_path)
        merges_path = Path(merges_path)
        vocab_path.parent.mkdir(parents=True, exist_ok=True)
        merges_path.parent.mkdir(parents=True, exist_ok=True)

        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump(self.vocab, f, ensure_ascii=False, indent=2)

        with open(merges_path, "w", encoding="utf-8") as f:
            for pair in self.merges:
                f.write(f"{pair[0]} {pair[1]}\n")

        print(f"Saved vocabulary  → {vocab_path}  ({len(self.vocab)} tokens)")
        print(f"Saved merge rules → {merges_path} ({len(self.merges)} merges)")

    def load(self, vocab_path: str | Path, merges_path: str | Path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.vocab        = {int(k): v for k, v in raw.items()}
        self.token_to_id  = {v: k for k, v in self.vocab.items()}

        self.merges = []
        with open(merges_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    self.merges.append((parts[0], parts[1]))

        self.max_merges = len(self.merges)
        print(f"Loaded {len(self.vocab)} tokens and {len(self.merges)} merges")

    def get_stats(self) -> Dict:
        return {
            "vocab_size":      len(self.vocab),
            "num_merges":      len(self.merges),
            "special_tokens":  len(self.SPECIAL_TOKENS),
            "regular_tokens":  len(self.vocab) - len(self.SPECIAL_TOKENS),
        }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # 1. Read corpus
    corpus_path = Path(CORPUS_PATH)
    print(f"Reading corpus from: {corpus_path}")
    if not corpus_path.exists():
        print(f"Error: Corpus file not found at {corpus_path}")
        return

    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = f.read()
    print(f"Corpus size: {len(corpus):,} characters | "
          f"{len(corpus.split()):,} whitespace-tokens\n")

    # 2. Train
    tokenizer = BPETokenizer(max_merges=MAX_MERGES)
    stats = tokenizer.train(corpus)

    # 3. Save artifacts
    print()
    tokenizer.save(TOKENS_FILE, MERGES_FILE)
    
    # Save encoded corpus for Trigram LM training
    print("Encoding corpus for Trigram LM training...")
    encoded_corpus = tokenizer.encode(corpus)
    with open(CORPUS_ENCODED_FILE, "w", encoding="utf-8") as f:
        json.dump(encoded_corpus, f)
    print(f"Saved encoded corpus -> {CORPUS_ENCODED_FILE} ({len(encoded_corpus)} tokens)")

    # 4. Quick smoke-test on a sample sentence
    sample = corpus.split("\n")[0][:80]   # first 80 chars of first line
    if sample.strip():
        encoded  = tokenizer.encode(sample)
        decoded  = tokenizer.decode(encoded)
        print(f"\nSmoke-test")
        print(f"  Original : {sample!r}")
        print(f"  Encoded  : {encoded[:20]}{'...' if len(encoded)>20 else ''}")
        print(f"  Decoded  : {decoded!r}")
        ratio = len(sample) / max(len(encoded), 1)
        print(f"  Compression ratio (chars/tokens): {ratio:.2f}")

    print("\nFinal stats:", stats)


if __name__ == "__main__":
    main()