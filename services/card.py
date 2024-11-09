import io
import uuid

from fastapi import Depends
from loguru import logger

from models.card import Card
from repositories.card import CardRepository
from schemas.card import CardSchema, ListCardOpts
from services.MLSerivce import MlService
from services.minio import MinioService
from services.personality_model import PersonalityModelService


class CardService:
    def __init__(
        self,
        repo: CardRepository = Depends(),
        minio: MinioService = Depends(),
        personality_model_service: PersonalityModelService = Depends(),
        ml_service: MlService = Depends(),
    ):
        self._repo = repo
        self._minio = minio
        self._personality_model_service = personality_model_service
        self._ml = ml_service

    async def create(
        self, resume: bytes, card: bytes, motivation_letter: str
    ) -> CardSchema:
        logger.debug("Card - Service - create")
        id = uuid.uuid4()

        transcribe = self._ml.transcript_video(card)

        resume_path = self._minio.upload_resume(id, resume)

        video_path = self._minio.upload_video_card(id, io.BytesIO(card))

        card = await self._repo.create(
            Card(
                id=id,
                video_path=video_path,
                transcription=transcribe,
                resume_path=resume_path,
                motivation_letter=motivation_letter,
            )
        )

        return await self._card_repo_to_schema(card)

    async def get(self, id: uuid.UUID) -> CardSchema:
        logger.debug("Card - Service - get")
        card = await self._repo.get(id)

        return await self._card_repo_to_schema(card)

    async def list(self, opts: ListCardOpts) -> list[CardSchema]:
        logger.debug("Card - Service - list")
        cards = await self._repo.list(opts.limit, opts.offset)

        return [await self._card_repo_to_schema(card) for card in cards]

    async def _card_repo_to_schema(self, req: Card) -> CardSchema:
        return CardSchema(
            id=req.id,
            video_link=self._minio.get_link(req.video_path),
            transcription=req.transcription,
            resume_link=self._minio.get_link(req.resume_path),
            motivation_letter=req.motivation_letter,
            personality_models=await self._personality_model_service.get_by_card_id(
                req.id
            ),
            created_at=req.created_at,
            updated_at=req.updated_at,
        )
