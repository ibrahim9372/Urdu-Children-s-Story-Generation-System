# Urdu Children's Story Generation System

An NLP system for generating Urdu children's stories using a trigram language model with custom BPE tokenizer.

## Project Structure

- **Data/** - Dataset collection & preprocessing (Phase I)
- **Tokenizer/** - Custom BPE tokenizer, vocab size 250 (Phase II)
- **Trigram_LM/** - Trigram language model with interpolation smoothing (Phase III)
- **Backend/** - FastAPI inference service (Phase IV)
- **Frontend/** - React chat interface (Phase V)
- **Deployment/** - Docker & CI/CD (Phase VI)

## Quick Start

### Frontend
```bash
cd Frontend
npm install
npm run dev
```

### Backend (coming soon)
```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Tech Stack

- Python 3.x - Core ML pipeline
- Custom BPE Tokenizer - Urdu text tokenization
- Trigram Language Model - Story generation with interpolation smoothing
- FastAPI - REST API backend
- React 19 + Vite - Frontend UI
- Tailwind CSS - Styling
