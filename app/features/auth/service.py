from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.features.auth import schemas as auth_schemas
from app.features.auth.models import User
from app.features.auth.repository import UserRepository
from app.features.auth.utils.google import GoogleClaims
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

    def authenticate_google(self, claims: GoogleClaims) -> User:
        """Resolve the user for a set of verified Google claims.

        The claims must already have been verified by
        `app.features.auth.utils.google.verify_google_id_token`, which
        guarantees the email address belongs to the Google account.

        Args:
            claims: The verified `sub` and `email` from a Google ID token.

        Returns:
            The existing linked user, the existing user newly linked by email,
            or a freshly created user.
        """
        user = self.repository.get_by_google_sub(claims.sub)

        if user:
            logger.info("User authenticated with Google: %s", user.email)
            return user

        # Link to an existing account. Safe because the token verification
        # rejected unverified emails, so Google has proven the holder owns this
        # address. The existing password, if any, is left untouched so both
        # sign-in methods keep working.
        email = claims.email.lower()

        user = self.repository.get_by_email(email)

        if user:
            if user.google_sub and user.google_sub != claims.sub:
                # The address has been reassigned to a different Google account,
                # which is possible on Workspace domains. Control of the address
                # is treated as control of the account, as it would be for a
                # password reset, but the replacement is worth recording.
                logger.warning("Relinking %s to a different Google account", user.email)

            user.google_sub = claims.sub
            self.repository.db.commit()
            self.repository.db.refresh(user)
            logger.info("Linked Google account to existing user: %s", user.email)
            return user

        user = User(email=email, google_sub=claims.sub, password=None)

        logger.info("Creating user from Google sign-in: %s", user.email)
        return self.repository.create(user)
