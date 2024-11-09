from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from errors.errors import ErrBadRequest
from models.user import User
from schemas.auth import (
    UserAuth,
    TokenData,
    Token,
    UserRegisterResponse,
    RegisterUserOpts,
)
from services.auth import AuthService, authenticated

router = APIRouter(prefix="/api/v1/metric", tags=["metric"])


@router.get(
    "/status",
    summary="получение токена",
    response_model=Token,
)
async def status(
):
    return "UP"
