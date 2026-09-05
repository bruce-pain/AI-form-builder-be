from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.features.auth import schemas as auth_schemas
from app.features.auth.models import User
from app.features.auth.repository import UserRepository
from app.features.auth.utils.password import hash_password, verify_password


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, schema: auth_schemas.RegisterRequest) -> User:
        schema.email = schema.email.lower()
        if self.repository.get_by_email(schema.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists!",
            )

        schema.password = hash_password(password=schema.password)

        user = User(**schema.model_dump())

        logger.info("Creating user with email: %s", user.email)
        return self.repository.create(user)

    def authenticate(self, schema: auth_schemas.LoginRequest) -> User:
        schema.email = schema.email.lower()
        user = self.repository.get_by_email(schema.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email",
            )

        # A user with no password set (e.g. one created through a social login)
        # must never authenticate via this endpoint.
        if not user.password or not verify_password(schema.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password",
            )

        logger.info("User authenticated with email: %s", user.email)
        return user
