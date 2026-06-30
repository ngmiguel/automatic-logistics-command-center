from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.auth.domain.entities import User
from alcc.auth.infrastructure.repositories import UserRepository
from alcc.auth.infrastructure.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from alcc.auth.presentation.dependencies import get_current_user
from alcc.auth.presentation.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from alcc.shared.infrastructure.database.session import get_db_session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    repo = UserRepository(session)
    existing = await repo.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    await repo.save(user)
    return UserResponse(
        id=user.id, email=user.email, full_name=user.full_name,
        role=user.role, is_active=user.is_active,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    repo = UserRepository(session)
    user = await repo.get_by_email(body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")
    token = create_access_token(user.id, user.email, user.role)
    return TokenResponse(access_token=token, role=user.role, user_id=user.id)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id, email=user.email, full_name=user.full_name,
        role=user.role, is_active=user.is_active,
    )
