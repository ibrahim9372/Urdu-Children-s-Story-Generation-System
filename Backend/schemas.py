"""
Pydantic request / response schemas for the /generate endpoint.

Fixes addressed:
  - 4A-03: max_length parameter added
  - 4A-06: Urdu text validation on prefix
"""

import re
from typing import List

from pydantic import BaseModel, Field, field_validator

# Matches at least one character in the Arabic/Urdu Unicode block
_URDU_RE = re.compile(r"[\u0600-\u06FF]")


class GenerateRequest(BaseModel):
    prefix: str = Field(
        ...,
        min_length=1,
        description="Urdu text prompt (must contain Urdu characters)",
    )
    max_length: int = Field(
        150,
        ge=1,
        le=1000,
        description="Maximum number of tokens to generate",
    )

    @field_validator("prefix")
    @classmethod
    def must_contain_urdu(cls, v: str) -> str:
        if not _URDU_RE.search(v):
            raise ValueError(
                "Prefix must contain at least one Urdu character (Unicode U+0600–U+06FF)"
            )
        return v


class GenerateResponse(BaseModel):
    story: str = Field(..., description="Generated Urdu story continuation")
    seed_words: List[str] = Field(..., description="First two words used as seed")
