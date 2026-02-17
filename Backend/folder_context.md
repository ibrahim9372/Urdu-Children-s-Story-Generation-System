# Backend - Folder Context

This folder contains Phase IV implementation: FastAPI inference microservice.

## Current Contents
- `main.py`: FastAPI app with `/generate` and `/health` endpoints
- `schemas.py`: Pydantic request/response models
- `model_loader.py`: Model loading utilities
- `generator.py`: Story generation logic
- `requirements.txt`: Python dependencies

## Role in Project
Exposes model inference as a REST API service for frontend consumption.

## Running the Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /health` - Health check
- `POST /generate` - Generate story continuation from Urdu prefix
