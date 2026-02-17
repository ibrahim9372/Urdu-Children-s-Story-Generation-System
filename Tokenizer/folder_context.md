# Tokenizer - Folder Context

This folder contains Phase II implementation: custom BPE tokenizer (vocab size 250).

## Current Contents
- `train_bpe.py`: BPE training script with encode/decode utilities
- `artifacts/ordered_merges.txt`: BPE merge operations
- `artifacts/final_token.json`: token vocabulary and translation table

## Role in Project
Consumes prepared corpus from `Data/` and produces tokenizer artifacts for trigram model training and inference.
