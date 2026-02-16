#!/usr/bin/env python3
"""
Urdu Story Generator: Loader & Generator
-------------------------------------------
Fetches pre-computed counts from pickle files and generates stories.
"""

import os
import pickle
import json
import random
import numpy as np
from pathlib import Path

# --- 1. CONFIGURATION & PATHS ---
ARTIFACTS_DIR = Path(r"D:\NLP\current_git\Urdu-Children-s-Story-Generation-System\trigram\artifacts")
UNI_PATH = ARTIFACTS_DIR / "unigrams.pkl"
BI_PATH = ARTIFACTS_DIR / "bigrams.pkl"
TRI_PATH = ARTIFACTS_DIR / "trigrams.pkl"

def load_counts():
    """Load the pre-saved Counter objects from pickle files."""
    if not (UNI_PATH.exists() and BI_PATH.exists() and TRI_PATH.exists()):
        raise FileNotFoundError("Pickle files not found in trigram/artifacts. Please run the counter script first.")

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

def generate_story_mle(seed_w1, seed_w2, max_length=150):
    # Initialize story with your seed words + word-end markers
    # Using the marker ensures it matches your trained BPE counts
    story = [seed_w1 + "</w>", seed_w2 + "</w>"]
    vocab = list(uni_counts.keys())
    
    for _ in range(max_length):
        # Get the last two tokens as our context (Trigram)
        w1, w2 = story[-2], story[-1]
        
        # 1. Calculate Likelihoods using Interpolation
        # This combines Trigram, Bigram, and Unigram probabilities
        probs = [get_interpolated_prob(w1, w2, t) for t in vocab]
        
        # 2. Safety Break
        # If the context (w1, w2) was never seen in training, 
        # interpolation falls back to unigram. If even that fails, we stop.
        if sum(probs) == 0:
            break
            
        # 3. Maximum Likelihood Choice
        # We use random.choices with weights to pick the next token.
        # This follows the probability distribution strictly.
        next_token = random.choices(vocab, weights=probs, k=1)[0]
        
        story.append(next_token)
        
        # 4. End of Text check
        if next_token == '<EOT>' or next_token == '<EOT></w>':
            break
            
    # Clean up the BPE markers and special tokens for the final Urdu string
    raw_output = "".join(story).replace('</w>', ' ').replace('<EOT>', '')
    
    # Return cleaned string (removes extra internal spaces)
    return " ".join(raw_output.split())
# --- 3. RUN ---

if __name__ == "__main__":
    print(f"Successfully loaded {len(uni_counts)} unigrams from artifacts.")
    
    # Test Seeds
    s1, s2 = "ایک", "دفعہ"
    print(f"\nSeed words: {s1} {s2}")
    print("-" * 30)
    
    result = generate_story_mle(s1, s2)
    print(result)