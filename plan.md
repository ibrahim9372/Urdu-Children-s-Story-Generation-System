# Urdu Children Story Generation System - General Guide

## Project Objective
Build and deploy an Urdu story generation system using a full workflow from data collection to production-style delivery.

## Folder Guide (Standard Names)
- `Data/` - dataset collection, preprocessing notebooks, and prepared corpus artifacts.
- `Tokenizer/` - custom BPE tokenizer implementation and tokenizer artifacts.
- `Trigram_LM/` - trigram model training, interpolation, and generation logic.
- `Backend/` - FastAPI service exposing generation endpoints.
- `Frontend/` - chat-style UI for user interaction.
- `Deployment/` - Docker, CI/CD, and deployment configuration.

## Current Status Snapshot
- Completed: Phase I dataset collection/preprocessing assets are available in `Data/`.
- Pending: tokenizer implementation, trigram model, backend service, frontend app, deployment automation.

## Phase-by-Phase Implementation Path

### Phase I - Data
- Collect at least 200 Urdu stories.
- Clean and normalize corpus.
- Standardize special tokens (`<EOS>`, `<EOP>`, `<EOT>`).
- Validate quality via segmentation audit and EDA.

### Phase II - Tokenizer
- Implement custom BPE tokenizer from scratch (no prebuilt tokenizer libs).
- Train with vocabulary size = 250.
- Export vocab/merge artifacts and provide encode/decode utilities.

### Phase III - Trigram LM
- Train trigram model using MLE.
- Add interpolation as discussed in class.
- Generate variable-length output until `<EOT>`.

### Phase IV - Backend
- Build FastAPI service for inference.
- Implement `POST /generate` with `prefix` and `max_length` input.
- Load tokenizer + trigram model for runtime generation.

### Phase V - Frontend
- Build a reactive chat-like interface.
- Accept Urdu prompt/prefix and display generated completion.
- Integrate with backend generation API.

### Phase VI - Deployment
- Add Docker setup for backend.
- Add GitHub Actions CI/CD pipeline.
- Deploy frontend on Vercel and backend on a public runtime.

## Working Conventions
- Keep each phase implementation primarily inside its own top-level folder.
- Keep interfaces explicit between phases (artifact files + API contracts).
- Prefer small, testable modules and clear scripts/notebooks over large monolithic files.

## Validation Checklist (High-Level)
- Data quality checks pass and artifacts are reproducible.
- Tokenizer trains and round-trip encode/decode works.
- Trigram model generates coherent story continuations.
- Backend endpoint responds correctly under expected inputs.
- Frontend can send prompts and display generation outputs.
- Deployment pipeline builds and publishes successfully.
