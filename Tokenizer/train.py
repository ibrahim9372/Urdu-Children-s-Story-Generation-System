"""
BPE Tokenizer Training Script

Trains a BPE tokenizer on the Urdu stories corpus.
Supports configurable data fraction for experimentation.

Usage:
    python train.py                      # Train on full corpus (default)
    python train.py --data-fraction 0.1  # Train on 10% of corpus
    python train.py --vocab-size 300      # Custom vocabulary size
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bpe_tokenizer import BPETokenizer


def load_corpus(corpus_path: str, data_fraction: float = 1.0) -> str:
    """
    Load corpus from file, optionally using only a fraction.

    Args:
        corpus_path: Path to corpus file
        data_fraction: Fraction of data to use (0.0 to 1.0)

    Returns:
        Corpus text
    """
    print(f"Loading corpus from {corpus_path}")

    with open(corpus_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)

    if data_fraction < 1.0:
        num_lines = int(total_lines * data_fraction)
        # Use random sampling for reproducibility, but seed it
        random.seed(42)
        selected_lines = random.sample(lines, num_lines)
        print(f"Using {num_lines} lines ({data_fraction * 100:.1f}% of {total_lines})")
        corpus = "".join(selected_lines)
    else:
        print(f"Using full corpus: {total_lines} lines")
        corpus = "".join(lines)

    return corpus


def main():
    parser = argparse.ArgumentParser(
        description="Train BPE tokenizer on Urdu stories corpus"
    )
    parser.add_argument(
        "--data-fraction",
        type=float,
        default=1.0,
        help="Fraction of corpus to use (0.0 to 1.0). Default: 1.0 (full corpus)",
    )
    parser.add_argument(
        "--vocab-size",
        type=int,
        default=250,
        help="Target vocabulary size. Default: 250",
    )
    parser.add_argument(
        "--corpus-path",
        type=str,
        default="Data/urdu_tokenizer_training.txt",
        help="Path to training corpus",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="Tokenizer/artifacts",
        help="Output directory for artifacts",
    )

    args = parser.parse_args()

    # Validate arguments
    if not 0.0 < args.data_fraction <= 1.0:
        print("Error: data-fraction must be between 0.0 and 1.0")
        sys.exit(1)

    if args.vocab_size < 10:
        print("Error: vocab-size must be at least 10")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load corpus
    corpus = load_corpus(args.corpus_path, args.data_fraction)

    print(f"\n{'=' * 50}")
    print(f"Training BPE Tokenizer")
    print(f"{'=' * 50}")
    print(f"Vocabulary size: {args.vocab_size}")
    print(f"Data fraction: {args.data_fraction}")
    print(f"Corpus size: {len(corpus):,} characters")
    print(f"Output directory: {output_dir}")
    print(f"{'=' * 50}\n")

    # Initialize tokenizer
    tokenizer = BPETokenizer(vocab_size=args.vocab_size)

    # Train
    start_time = time.time()
    stats = tokenizer.train(corpus)
    training_time = time.time() - start_time

    print(f"\nTraining completed in {training_time:.2f} seconds")
    print(f"Statistics: {stats}")

    # Save artifacts
    vocab_path = output_dir / "vocabulary.json"
    merges_path = output_dir / "merges.txt"

    tokenizer.save(str(vocab_path), str(merges_path))

    # Save training config for reference
    config = {
        "vocab_size": args.vocab_size,
        "data_fraction": args.data_fraction,
        "corpus_path": args.corpus_path,
        "training_time_seconds": training_time,
        "stats": stats,
    }

    config_path = output_dir / "training_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\n{'=' * 50}")
    print("Training Complete!")
    print(f"{'=' * 50}")
    print(f"Vocabulary: {vocab_path}")
    print(f"Merges: {merges_path}")
    print(f"Config: {config_path}")

    # Quick verification
    print(f"\n--- Verification ---")

    # Test encoding
    test_text = "بچہ کھیل رہا ہے"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)

    print(f"Test encode: '{test_text}' -> {encoded}")
    print(f"Test decode: {encoded} -> '{decoded}'")

    # Round-trip check
    round_trip_ok = test_text.replace(" ", "") in decoded.replace(" ", "").replace(
        "<EOS>", ""
    ).replace("<EOP>", "").replace("<EOT>", "")
    print(f"Round-trip OK: {round_trip_ok}")

    # Show vocabulary sample
    print(f"\nVocabulary sample (first 20 tokens):")
    for tid in range(min(20, len(tokenizer.vocab))):
        print(f"  {tid}: {tokenizer.vocab[tid]}")


if __name__ == "__main__":
    main()
