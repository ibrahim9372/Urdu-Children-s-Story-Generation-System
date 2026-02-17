#!/usr/bin/env python3
"""
Urdu Story Generator: Loader & Generator
-------------------------------------------
Fetches pre-computed counts from pickle files and generates stories.
"""

import pickle
import json
import random
import sys
from pathlib import Path

# --- 1. CONFIGURATION & PATHS ---
BASE_DIR = Path(__file__).parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
UNI_PATH = ARTIFACTS_DIR / "unigrams.pkl"
BI_PATH = ARTIFACTS_DIR / "bigrams.pkl"
TRI_PATH = ARTIFACTS_DIR / "trigrams.pkl"

# Tokenizer paths
TOKENIZER_DIR = BASE_DIR.parent / "Tokenizer"
TOKENIZER_ARTIFACTS = TOKENIZER_DIR / "artifacts"
VOCAB_FILE = TOKENIZER_ARTIFACTS / "final_token.json"
MERGES_FILE = TOKENIZER_ARTIFACTS / "ordered_merges.txt"

# Add Tokenizer to sys.path to import BPETokenizer
sys.path.append(str(TOKENIZER_DIR))
try:
    from bpe_tokenizer import BPETokenizer
except ImportError:
    print("Error: Could not import BPETokenizer. Make sure Tokenizer folder exists.")
    sys.exit(1)

def load_counts():
    """Load the pre-saved Counter objects from pickle files."""
    if not (UNI_PATH.exists() and BI_PATH.exists() and TRI_PATH.exists()):
        raise FileNotFoundError(f"Pickle files not found in {ARTIFACTS_DIR}. Please run the counter script first.")

    with open(UNI_PATH, "rb") as f:
        uni = pickle.load(f)
    with open(BI_PATH, "rb") as f:
        bi = pickle.load(f)
    with open(TRI_PATH, "rb") as f:
        tri = pickle.load(f)
    
    return uni, bi, tri

# Load global counts for use in functions
uni_counts, bi_counts, tri_counts = load_counts()
total_token_count = sum(uni_counts.values())

# Initialize and load tokenizer
tokenizer = BPETokenizer()
if VOCAB_FILE.exists() and MERGES_FILE.exists():
    tokenizer.load(VOCAB_FILE, MERGES_FILE)
else:
    print("Warning: Tokenizer artifacts not found. Generation might fail.")

# --- 2. CORE MATH & GENERATION ---

def get_interpolated_prob(w1, w2, w3, lambdas=(0.8, 0.15, 0.05)):
    l1, l2, l3 = lambdas
    
    # 1. Trigram Probability: P(w3 | w1, w2)
    c3 = tri_counts.get((w1, w2, w3), 0)
    c2_context = bi_counts.get((w1, w2), 0)
    p_tri = c3 / c2_context if c2_context > 0 else 0
    
    # 2. Bigram Probability: P(w3 | w2)
    c2 = bi_counts.get((w2, w3), 0)
    c1_context = uni_counts.get(w2, 0)
    p_bi = c2 / c1_context if c1_context > 0 else 0
    
    # 3. Unigram Probability: P(w3)
    c1 = uni_counts.get(w3, 0)
    p_uni = c1 / total_token_count if total_token_count > 0 else 0
    
    return (l1 * p_tri) + (l2 * p_bi) + (l3 * p_uni)

def generate_story_mle(seed_text, max_length=50):
    # Encode seed text to token IDs
    start_ids = tokenizer.encode(seed_text)
    
    # We need at least 2 tokens context for trigram
    if len(start_ids) < 2:
        if len(start_ids) == 0:
            return ""
        if len(start_ids) == 1:
            start_ids = [start_ids[0], start_ids[0]] # fallback
            
    story_ids = list(start_ids)
    vocab = list(uni_counts.keys()) # These are integer IDs
    
    for _ in range(max_length):
        # Get the last two tokens as our context (Trigram)
        w1, w2 = story_ids[-2], story_ids[-1]
        
        # 1. Calculate Likelihoods using Interpolation
        probs = [get_interpolated_prob(w1, w2, t) for t in vocab]
        
        # 2. Safety Break
        if sum(probs) == 0:
            break
            
        # 3. Maximum Likelihood Choice
        next_id = random.choices(vocab, weights=probs, k=1)[0]
        
        story_ids.append(next_id)
        
        # 4. End of Text check
        token_str = tokenizer.vocab.get(next_id, "")
        if token_str == "<EOT>":
            break
            
    # Decode result back to text
    full_text = tokenizer.decode(story_ids)
    return full_text

# --- 3. RUN ---

if __name__ == "__main__":
    print(f"Successfully loaded {len(uni_counts)} unigrams from artifacts.")
    
    # Test Seeds
    seed_text = "ایک دفعہ"
    print(f"\nSeed text: {seed_text}")
    print("-" * 30)
    
    result = generate_story_mle(seed_text,1000)
    print("Generated Story:")
    print(result)