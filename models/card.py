import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from models.BaseModel import EntityMeta


class Card(EntityMeta):
    __tablename__ = "card"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    video_path: Mapped[str] = mapped_column(nullable=True)
    transcription: Mapped[str] = mapped_column(nullable=True)

    resume_path: Mapped[str] = mapped_column(nullable=True)# pdf

    motivation_letter: Mapped[str] = mapped_column(nullable=True)

    # OCEAN
    # MBTI
    # RIASEC

    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=False
    )
