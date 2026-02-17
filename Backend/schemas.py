from pydantic import BaseModel, Field
from typing import List


class GenerateRequest(BaseModel):
    prefix: str = Field(..., min_length=1, description="Urdu text prompt to continue")


class GenerateResponse(BaseModel):
    story: str = Field(..., description="Generated Urdu story continuation")
    seed_words: List[str] = Field(..., description="First two words used as seed")
