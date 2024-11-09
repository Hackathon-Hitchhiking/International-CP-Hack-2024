import uuid

from fastapi import Depends

from models.card import Card
from models.personality_model import PersonalityModel
from repositories.card import CardRepository
from schemas.card import CardSchema, PersonalityModelSchema, ListCardOpts
from services.minio import MinioService


class CardService:
    def __init__(
        self, repo: CardRepository = Depends(), minio: MinioService = Depends()
    ):
        self._repo = repo
        self._minio = minio

    async def create(self, resume: bytes, card: bytes, motivation_letter: str) -> CardSchema:
        id = uuid.uuid4()

        resume_path = self._minio.upload_resume(id, resume)

        video_path = self._minio.upload_video_card(id, card)

        card = await self._repo.create(
            Card(
                id=id,
                video_path=video_path,
                transcription="",  # TODO add the transcription of the video
                resume_path=resume_path,
                motivation_letter=motivation_letter,
            )
        )

        return await self._card_repo_to_schema(card)

    async def get(self, id: uuid.UUID) -> CardSchema:
        card = await self._repo.get(id)

        return await self._card_repo_to_schema(card)

    async def list(self, opts: ListCardOpts) -> list[CardSchema]:
        cards = await self._repo.list(opts.limit, opts.offset)

        return [await self._card_repo_to_schema(card) for card in cards]

    async def _card_repo_to_schema(self, req: Card) -> CardSchema:
        return CardSchema(
            id=req.id,
            video_link=self._minio.get_link(req.video_path),
            transcription=req.transcription,
            resume_link=self._minio.get_link(req.resume_path),
            motivation_letter=req.motivation_letter,
            personality_models=[],
            # personality_models=[await self._personality_mode_repo_ro_schema(repo_pm) for repo_pm in await req.personality_models],
            created_at=req.created_at,
            updated_at=req.updated_at,
        )

    async def _personality_mode_repo_ro_schema(
        self, req: PersonalityModel
    ) -> PersonalityModelSchema:
        return PersonalityModelSchema(
            model=req.model,
            parameter=req.parameter,
            confidence=req.confidence,
            created_at=req.created_at,
            updated_at=req.updated_at,
        )
