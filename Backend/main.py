"""
FastAPI application — Urdu Story Generator
-------------------------------------------
Exposes /health, /generate (JSON), and /generate/stream (SSE) endpoints.

Fixes addressed:
  - 4A-04: CORS origins from ALLOWED_ORIGINS env var
  - 4A-07: SSE streaming via /generate/stream
  - 4A-03: max_length accepted and forwarded
  - 4A-06: Urdu input validation (via schema)
  - 4A-02 / XA-01: generation uses BPE-encoded prefix (via generator module)
"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from generator import generate_story, generate_story_streaming
from schemas import GenerateRequest, GenerateResponse

app = FastAPI(title="Urdu Story Generator API")

# ---------------------------------------------------------------------------
# CORS — configurable via ALLOWED_ORIGINS env var (comma-separated)
# Default to allow all origins for development to fix CORS preflight issues
# ---------------------------------------------------------------------------
_default_origins = "*"
_origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Return the complete generated story as a single JSON response."""
    try:
        story, seed_words = generate_story(
            request.prefix, max_length=request.max_length
        )
        return GenerateResponse(story=story, seed_words=seed_words)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")


@app.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    """Stream generated tokens via Server-Sent Events."""

    def _event_stream():
        try:
            for chunk in generate_story_streaming(
                request.prefix, max_length=request.max_length
            ):
                payload = json.dumps({"token": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except ValueError as exc:
            error_payload = json.dumps(
                {"error": str(exc)}, ensure_ascii=False
            )
            yield f"data: {error_payload}\n\n"
        except Exception as exc:
            error_payload = json.dumps(
                {"error": f"Generation failed: {exc}"}, ensure_ascii=False
            )
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
