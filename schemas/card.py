import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel


class PersonalityModelSchema(BaseModel):
    model: str
    parameter: str
    confidence: float

    created_at: datetime
    updated_at: datetime


class CardSchema(BaseModel):
    id: uuid.UUID
    video_link: str

    transcription: str

    resume_link: str

    motivation_letter: str

    personality_models: List[PersonalityModelSchema]

    created_at: datetime
    updated_at: datetime

class ListCardOpts(BaseModel):
    offset: int = 0
    limit: int = 100