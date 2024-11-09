from typing import List

from fastapi.params import Depends
from loguru import logger

from models.personality_model import PersonalityModel
from repositories.personality_model import PersonalityModelRepository
from schemas.card import PersonalityModelSchema


class PersonalityModelService:
    def __init__(self, repo: PersonalityModelRepository = Depends()):
        self._repo = repo


    async def create(self, opts: PersonalityModel) -> PersonalityModelSchema:
        logger.debug("PersonalityModel - Service - create")
        personality_model = await self._repo.create(opts)

        return self._personality_mode_repo_ro_schema(personality_model)

    async def get_by_card_id(self, card_id) -> List[PersonalityModelSchema]:
        logger.debug("PersonalityModel - Service - get_by_card_id")
        personality_models = await self._repo.get_by_card_id(card_id)

        return [self._personality_mode_repo_ro_schema(personality_model) for personality_model in personality_models]

    def _personality_mode_repo_ro_schema(
            self, req: PersonalityModel
    ) -> PersonalityModelSchema:
        return PersonalityModelSchema(
            model=req.model,
            parameter=req.parameter,
            confidence=req.confidence,
            created_at=req.created_at,
            updated_at=req.updated_at,
        )