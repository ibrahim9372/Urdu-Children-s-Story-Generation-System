import re
import json
import os
from pathlib import Path
from collections import Counter, defaultdict

# --- 1. SETTINGS & PATHS ---
CORPUS_PATH = Path(__file__).parent.parent / "Data" / "urdu_tokenizer_training.txt"
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
MERGES_FILE = ARTIFACTS_DIR / "ordered_merges.txt"
TOKENS_FILE = ARTIFACTS_DIR / "final_token.json"

# Create directory if it doesn't exist
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# --- 2. LOAD DATA ---
if not os.path.exists(CORPUS_PATH):
    raise FileNotFoundError(f"Could not find corpus at {CORPUS_PATH}")

with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    text = f.read()


# --- 3. BPE UTILITIES ---
def get_word_frequencies(text):
    text = re.sub(r"[^\w\s<>]", " ", text)
    tokens = text.split()
    return Counter(tokens)


def prepare_for_bpe(data):
    bpe_data = {}
    for word, freq in data.items():
        chars = tuple(word) + ("</w>",)
        bpe_data[chars] = freq
    return bpe_data


def get_stats(bpe_counts):
    pairs = defaultdict(int)
    for word_tuple, freq in bpe_counts.items():
        if len(word_tuple) < 2:
            continue
        for i in range(len(word_tuple) - 1):
            pair = (word_tuple[i], word_tuple[i + 1])
            pairs[pair] += freq
    return pairs


def merge_vocab(pair, bpe_counts):
    new_counts = {}
    bigram = pair
    replacement = "".join(pair)
    for word_tuple, freq in bpe_counts.items():
        new_word = []
        i = 0
        while i < len(word_tuple):
            if i < len(word_tuple) - 1 and word_tuple[i : i + 2] == bigram:
                new_word.append(replacement)
                i += 2
            else:
                new_word.append(word_tuple[i])
                i += 1
        new_counts[tuple(new_word)] = freq
    return new_counts


# --- 4. RUN BPE TRAINING ---
print("Starting BPE Training...")
frequencies = get_word_frequencies(text)
current_data = prepare_for_bpe(frequencies)
ordered_merges = []

num_merges = 250  # As per your loop requirement
for i in range(num_merges):
    pairs = get_stats(current_data)
    if not pairs:
        break
    best_pair = max(pairs, key=pairs.get)
    ordered_merges.append(best_pair)
    current_data = merge_vocab(best_pair, current_data)
    if (i + 1) % 50 == 0:
        print(f"Completed {i + 1} merges...")


# --- 5. TRANSLATE CORPUS ---
def tokenize_word(word, merges):
    tokens = list(word) + ["</w>"]
    for pair in merges:
        char1, char2 = pair
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and tokens[i] == char1 and tokens[i + 1] == char2:
                new_tokens.append(char1 + char2)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return tokens


def translate_corpus_to_bpe(raw_text, merges):
    tokenized_corpus = []
    words = raw_text.split()
    for word in words:
        if word.startswith("<") and word.endswith(">"):
            tokenized_corpus.append(word + "</w>")
            continue
        tokenized_corpus.extend(tokenize_word(word, merges))
    return tokenized_corpus


print("Translating corpus to tokens...")
final_token_list = translate_corpus_to_bpe(text, ordered_merges)

# --- 6. SAVE ARTIFACTS ---

# Save Merges as TXT (one pair per line)
with open(MERGES_FILE, "w", encoding="utf-8") as f:
    for pair in ordered_merges:
        f.write(f"{pair[0]} {pair[1]}\n")

# Save Final Token List as JSON
with open(TOKENS_FILE, "w", encoding="utf-8") as f:
    json.dump(final_token_list, f, ensure_ascii=False, indent=4)

print(f"Success!")
print(f"Merges saved to: {MERGES_FILE}")
print(f"Tokens saved to: {TOKENS_FILE}")
print(f"Total tokens in translated corpus: {len(final_token_list)}")
