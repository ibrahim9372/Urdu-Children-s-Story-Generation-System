"""
BPE Tokenizer Implementation for Urdu Children Stories
Implements Byte Pair Encoding from scratch without external tokenization libraries.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class BPETokenizer:
    """
    Byte Pair Encoding Tokenizer implementation.

    Handles Urdu text tokenization using BPE algorithm with word-end markers
    for proper subword segmentation.
    """

    # Special tokens with reserved IDs
    SPECIAL_TOKENS = {
        "<EOS>": 0,  # End of sentence
        "<EOP>": 1,  # End of paragraph
        "<EOT>": 2,  # End of story
        "<unk>": 3,  # Unknown token
    }

    # Word-end marker for BPE
    WORD_END = "</w>"

    def __init__(self, vocab_size: int = 250):
        """
        Initialize BPE Tokenizer.

        Args:
            vocab_size: Target vocabulary size (including special tokens)
        """
        self.vocab_size = vocab_size
        self.vocab: Dict[int, str] = {}  # token_id -> token_string
        self.token_to_id: Dict[str, int] = {}  # token_string -> token_id
        self.merges: List[Tuple[str, str]] = []  # List of merge operations

    def train(self, corpus: str) -> Dict:
        """
        Train the BPE tokenizer on the given corpus.

        Args:
            corpus: Raw text corpus to train on

        Returns:
            Training statistics dictionary
        """
        print(f"Training BPE tokenizer with vocab_size={self.vocab_size}")

        # Step 1: Pre-tokenize corpus into words
        word_frequencies = self._pretokenize(corpus)
        print(f"Pre-tokenized into {len(word_frequencies)} unique words")

        # Step 2: Initialize vocabulary with characters and special tokens
        self._initialize_vocab(word_frequencies)
        print(f"Initial vocabulary size: {len(self.vocab)}")

        # Step 3: Iteratively merge most frequent pairs
        num_merges = self.vocab_size - len(self.vocab)
        print(f"Performing {num_merges} merge operations...")

        for i in range(num_merges):
            # Count all pairs in the corpus
            pair_frequencies = self._count_pairs(word_frequencies)

            if not pair_frequencies:
                print(f"Warning: No more pairs to merge at iteration {i}")
                break

            # Find most frequent pair
            best_pair = max(pair_frequencies.keys(), key=lambda p: pair_frequencies[p])

            # Record the merge
            self.merges.append(best_pair)

            # Merge the pair in all words
            word_frequencies = self._merge_pair(word_frequencies, best_pair)

            # Add merged token to vocabulary
            new_token = best_pair[0] + best_pair[1]
            new_id = len(self.vocab)
            self.vocab[new_id] = new_token
            self.token_to_id[new_token] = new_id

            if (i + 1) % 50 == 0:
                print(f"  Completed {i + 1}/{num_merges} merges")

        print(f"Training complete! Final vocabulary size: {len(self.vocab)}")

        return {
            "vocab_size": len(self.vocab),
            "num_merges": len(self.merges),
            "unique_words": len(word_frequencies),
        }

    def _pretokenize(self, text: str) -> Dict[Tuple[str, ...], int]:
        """
        Split text into words with word-end markers.

        Args:
            text: Input text

        Returns:
            Dictionary mapping word tuples to frequencies
        """
        # Split on whitespace first
        words = text.split()

        # Add word-end markers and convert to character tuples
        word_frequencies = Counter()
        for word in words:
            # Handle special tokens - don't add </w> marker
            if word in self.SPECIAL_TOKENS:
                word_frequencies[(word,)] += 1
            else:
                # Add </w> to mark end of word
                chars = tuple(word) + (self.WORD_END,)
                word_frequencies[chars] += 1

        return dict(word_frequencies)

    def _initialize_vocab(self, word_frequencies: Dict[Tuple[str, ...], int]):
        """
        Initialize vocabulary with all unique characters and special tokens.
        """
        # Add special tokens first
        for token, token_id in self.SPECIAL_TOKENS.items():
            self.vocab[token_id] = token
            self.token_to_id[token] = token_id

        # Collect all unique characters from the corpus
        unique_chars: Set[str] = set()
        for word in word_frequencies.keys():
            for char in word:
                if char != self.WORD_END:  # Don't add </w> as standalone char
                    unique_chars.add(char)

        # Add characters to vocabulary
        for char in sorted(unique_chars):
            if char not in self.token_to_id:
                new_id = len(self.vocab)
                self.vocab[new_id] = char
                self.token_to_id[char] = new_id

    def _count_pairs(
        self, word_frequencies: Dict[Tuple[str, ...], int]
    ) -> Dict[Tuple[str, str], int]:
        """
        Count all adjacent pair frequencies in the corpus.

        Args:
            word_frequencies: Dictionary of word frequencies

        Returns:
            Dictionary of pair frequencies
        """
        pair_frequencies: Dict[Tuple[str, str], int] = defaultdict(int)

        for word, freq in word_frequencies.items():
            for i in range(len(word) - 1):
                pair = (word[i], word[i + 1])
                pair_frequencies[pair] += freq

        return pair_frequencies

    def _merge_pair(
        self, word_frequencies: Dict[Tuple[str, ...], int], pair: Tuple[str, str]
    ) -> Dict[Tuple[str, ...], int]:
        """
        Merge all occurrences of a pair in the corpus.

        Args:
            word_frequencies: Current word frequencies
            pair: Pair to merge

        Returns:
            Updated word frequencies
        """
        new_word_frequencies: Dict[Tuple[str, ...], int] = {}
        merged_token = pair[0] + pair[1]

        for word, freq in word_frequencies.items():
            # Merge the pair in this word
            new_word = self._merge_word(word, pair)
            new_word_frequencies[new_word] = freq

        return new_word_frequencies

    def _merge_word(
        self, word: Tuple[str, ...], pair: Tuple[str, str]
    ) -> Tuple[str, ...]:
        """
        Merge a specific pair in a single word.

        Args:
            word: Word as tuple of tokens
            pair: Pair to merge

        Returns:
            New word with pair merged
        """
        merged_token = pair[0] + pair[1]
        result = []
        i = 0

        while i < len(word):
            # Check if current position matches the pair
            if i < len(word) - 1 and word[i] == pair[0] and word[i + 1] == pair[1]:
                result.append(merged_token)
                i += 2
            else:
                result.append(word[i])
                i += 1

        return tuple(result)

    def encode(self, text: str) -> List[int]:
        """
        Encode text into token IDs.

        Args:
            text: Input text to encode

        Returns:
            List of token IDs
        """
        # Pre-tokenize into words
        words = text.split()

        # Convert each word to character sequence with </w> marker
        tokens_list = []
        for word in words:
            if word in self.SPECIAL_TOKENS:
                tokens_list.append([word])
            else:
                tokens = list(word) + [self.WORD_END]
                tokens_list.append(tokens)

        # Apply merges in order
        for pair in self.merges:
            tokens_list = self._apply_merge(tokens_list, pair)

        # Convert tokens to IDs
        token_ids = []
        for tokens in tokens_list:
            for token in tokens:
                token_id = self.token_to_id.get(token, self.SPECIAL_TOKENS["<unk>"])
                token_ids.append(token_id)

        return token_ids

    def _apply_merge(
        self, tokens_list: List[List[str]], pair: Tuple[str, str]
    ) -> List[List[str]]:
        """
        Apply a merge operation to encoded tokens.
        """
        merged_token = pair[0] + pair[1]

        for tokens in tokens_list:
            i = 0
            while i < len(tokens) - 1:
                if tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                    tokens[i] = merged_token
                    del tokens[i + 1]
                else:
                    i += 1

        return tokens_list

    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text.

        Args:
            token_ids: List of token IDs

        Returns:
            Decoded text
        """
        # Convert IDs to tokens
        tokens = [self.vocab.get(tid, "<unk>") for tid in token_ids]

        # Remove </w> markers and join
        result_parts = []
        for token in tokens:
            if token == self.WORD_END:
                result_parts.append(" ")
            elif token in self.SPECIAL_TOKENS:
                result_parts.append(token)
            else:
                result_parts.append(token)

        # Clean up and return
        text = "".join(result_parts)
        # Fix spacing around special tokens
        for special in self.SPECIAL_TOKENS:
            text = text.replace(f" {special}", special)
            text = text.replace(f"{special} ", special)

        return text.strip()

    def save(self, vocab_path: str, merges_path: str):
        """
        Save vocabulary and merge rules to files.

        Args:
            vocab_path: Path to save vocabulary JSON
            merges_path: Path to save merges text file
        """
        # Save vocabulary as JSON
        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump(self.vocab, f, ensure_ascii=False, indent=2)

        # Save merges as text file (one per line: "token_a token_b")
        with open(merges_path, "w", encoding="utf-8") as f:
            for pair in self.merges:
                f.write(f"{pair[0]} {pair[1]}\n")

        print(f"Saved vocabulary to {vocab_path}")
        print(f"Saved {len(self.merges)} merges to {merges_path}")

    def load(self, vocab_path: str, merges_path: str):
        """
        Load vocabulary and merge rules from files.

        Args:
            vocab_path: Path to vocabulary JSON file
            merges_path: Path to merges text file
        """
        # Load vocabulary
        with open(vocab_path, "r", encoding="utf-8") as f:
            self.vocab = json.load(f)

        # Rebuild token_to_id reverse mapping
        self.token_to_id = {v: k for k, v in self.vocab.items()}

        # Load merges
        self.merges = []
        with open(merges_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 2:
                        self.merges.append((parts[0], parts[1]))

        self.vocab_size = len(self.vocab)
        print(
            f"Loaded vocabulary ({len(self.vocab)} tokens) and {len(self.merges)} merges"
        )

    def get_stats(self) -> Dict:
        """
        Get tokenizer statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            "vocab_size": len(self.vocab),
            "num_merges": len(self.merges),
            "special_tokens": len(self.SPECIAL_TOKENS),
            "regular_tokens": len(self.vocab) - len(self.SPECIAL_TOKENS),
        }

    def encode_with_stats(self, text: str) -> Tuple[List[int], Dict]:
        """
        Encode text and return statistics.

        Args:
            text: Input text

        Returns:
            Tuple of (token_ids, stats_dict)
        """
        token_ids = self.encode(text)

        # Count token types
        unique_tokens = len(set(token_ids))

        stats = {
            "num_tokens": len(token_ids),
            "unique_tokens": unique_tokens,
            "compression_ratio": len(text) / max(len(token_ids), 1),
        }

        return token_ids, stats


if __name__ == "__main__":
    # Quick test
    tokenizer = BPETokenizer(vocab_size=50)

    # Simple test corpus
    test_corpus = "بچہ کھیل رہا ہے بچہ پڑھ رہا ہے لڑکا کھیل رہا ہے"

    tokenizer.train(test_corpus)
    print(f"\nVocabulary: {tokenizer.vocab}")

    # Test encoding
    test_text = "بچہ کھیل رہا ہے"
    encoded = tokenizer.encode(test_text)
    print(f"\nEncoded '{test_text}': {encoded}")

    decoded = tokenizer.decode(encoded)
    print(f"Decoded: {decoded}")
