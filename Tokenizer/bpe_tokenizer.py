import json
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
from pathlib import Path

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
        self.max_merges  = max_merges
        self.vocab:        Dict[int, str]          = {}
        self.token_to_id:  Dict[str, int]          = {}
        self.merges:       List[Tuple[str, str]]   = []

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
        text = "".join(tokens)
        
        # Replace word-end marker with space
        text = text.replace(self.WORD_END, " ")
        
        # Replace special tokens with user-requested punctuation
        text = text.replace("<EOS>", "-")
        text = text.replace("<EOP>", "\n")
        
        for special in self.SPECIAL_TOKENS:
            if special not in ["<EOS>", "<EOP>"]:
                text = text.replace(f" {special}", special).replace(f"{special} ", special)
        return text.strip()

    def load(self, vocab_path: str | Path, merges_path: str | Path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # JSON keys are always strings, convert them back to integers
        self.vocab        = {int(k): v for k, v in raw.items()}
        self.token_to_id  = {v: k for k, v in self.vocab.items()}

        self.merges = []
        with open(merges_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    self.merges.append((parts[0], parts[1]))
        self.max_merges = len(self.merges)
