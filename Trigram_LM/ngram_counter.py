#!/usr/bin/env python3
"""
Token Counter and Saver
-----------------------
This script computes unigram, bigram, and trigram counts from a list of tokens
and saves the counts as pickle files into the 'trigram/artifacts' folder.
"""

import os
import pickle
from collections import Counter
from typing import List, Tuple, Union
import pathlib 
from pathlib import Path
import json

# Folder where token counts will be saved
BASE_DIR = Path(__file__).parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

# Path to the tokenizer artifacts (relative to this script)
TOKENIZER_ARTIFACTS = BASE_DIR.parent / "Tokenizer" / "artifacts"
ENCODED_CORPUS_FILE = TOKENIZER_ARTIFACTS / "corpus_encoded.json"


def ensure_dir(directory: str) -> None:
    """Ensure that the given directory exists."""
    os.makedirs(directory, exist_ok=True)


def get_unigram_counts(tokens: List[str]) -> Counter:
    """
    Count occurrences of each unigram token.
    
    Args:
        tokens (List[str]): List of tokens.
    
    Returns:
        Counter: Frequency of each unigram token.
    """
    return Counter(tokens)


def get_bigram_counts(tokens: List[str]) -> Counter:
    """
    Count occurrences of each bigram (pair of tokens).
    
    Args:
        tokens (List[str]): List of tokens.
    
    Returns:
        Counter: Frequency of each bigram tuple.
    """
    bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    return Counter(bigrams)


def get_trigram_counts(tokens: List[str]) -> Counter:
    """
    Count occurrences of each trigram (triple of tokens).
    
    Args:
        tokens (List[str]): List of tokens.
    
    Returns:
        Counter: Frequency of each trigram tuple.
    """
    trigrams = [(tokens[i], tokens[i + 1], tokens[i + 2]) for i in range(len(tokens) - 2)]
    return Counter(trigrams)


def save_pickle(obj: Union[Counter, dict], filename: str) -> None:
    """
    Save a Python object (Counter or dict) as a pickle file.
    
    Args:
        obj (Counter | dict): Object to save.
        filename (str): File path to save the pickle.
    """
    with open(filename, "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved: {filename}")


def save_all_counts(tokens: List[str]) -> None:
    """
    Compute unigram, bigram, and trigram counts and save them to the artifacts folder.
    
    Args:
        tokens (List[str]): List of tokens to process.
    """
    ensure_dir(ARTIFACTS_DIR)

    uni_counts = get_unigram_counts(tokens)
    bi_counts = get_bigram_counts(tokens)
    tri_counts = get_trigram_counts(tokens)

    save_pickle(uni_counts, os.path.join(ARTIFACTS_DIR, "unigrams.pkl"))
    save_pickle(bi_counts, os.path.join(ARTIFACTS_DIR, "bigrams.pkl"))
    save_pickle(tri_counts, os.path.join(ARTIFACTS_DIR, "trigrams.pkl"))

    print(f"Total tokens processed: {len(tokens)}")
    print(f"Unique unigrams: {len(uni_counts)}")
    print(f"Unique bigrams: {len(bi_counts)}")
    print(f"Unique trigrams: {len(tri_counts)}")


if __name__ == "__main__":
    tokens_path = ENCODED_CORPUS_FILE
    all_tokens = None

    if tokens_path.exists():
        with open(tokens_path, "r", encoding="utf-8") as f:
            # Load the list of token IDs (the encoded corpus)
            all_tokens = json.load(f)
    else:
        print(f"Could not find token path: {tokens_path}\\nExiting")
        SystemExit(0)

    # Safety check
    if all_tokens is None:
        raise ValueError("Error: corpus_encoded.json was not loaded properly.")

    # Convert IDs to strings if they are ints, though they should be consistent
    # The counter functions expect a list of tokens (or IDs)
    # If they are IDs (integers), Counter works fine. 
    # If we want to save them as strings, we can convert.
    # Let's keep them as is (likely integers from the tokenizer).
    
    save_all_counts(all_tokens)
