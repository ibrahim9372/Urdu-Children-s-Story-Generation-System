# Data - Folder Context

This folder contains Phase I assets for dataset acquisition and preprocessing.

## Current Contents
- `01-data-collection.ipynb`: scraping pipeline notebook.
- `01-cleaning.ipynb`: cleaning and normalization pipeline.
- `02-segmentation-audit.ipynb`: segmentation consistency checks.
- `03-tokenizer.ipynb`: tokenizer training text generation from cleaned stories.
- `04-dataset-eda.ipynb`: data quality and distribution analysis.
- `urdu_stories_final.json`: scraped raw story dataset.
- `urdu_stories_final_preprocessed.json`: cleaned/normalized dataset.
- `urdu_tokenizer_training.txt`: line-wise corpus prepared for tokenizer training.

## Role in Project
This folder is the single source of truth for corpus preparation before tokenizer/model training.
