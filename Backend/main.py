from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from generator import generate_story
from schemas import GenerateRequest, GenerateResponse

app = FastAPI(title="Urdu Story Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    try:
        words = request.prefix.strip().split()
        if len(words) < 2:
            raise HTTPException(
                status_code=422, detail="Prefix must contain at least 2 words"
            )

        story, seed_words = generate_story(request.prefix)

        return GenerateResponse(story=story, seed_words=seed_words)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
