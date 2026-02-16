"""
Urdu BPE Tokenizer Package

A custom Byte Pair Encoding tokenizer for Urdu children stories.
Implements BPE from scratch without external tokenization libraries.
"""

from .bpe_tokenizer import BPETokenizer

__version__ = "1.0.0"
__all__ = ["BPETokenizer"]
