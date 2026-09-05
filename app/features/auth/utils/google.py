"""Google ID token verification"""

from typing import NamedTuple

from fastapi import HTTPException, status
from google.auth import exceptions as google_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import settings
from app.core.logger import logger


class GoogleClaims(NamedTuple):
    """The subset of verified Google ID token claims that this app uses."""

    sub: str
    email: str


def verify_google_id_token(token: str) -> GoogleClaims:
    """Verify a Google-issued ID token and return its trusted claims.

    Args:
        token (str): The raw ID token as issued by Google.

    Returns:
        GoogleClaims: The verified Google subject identifier and email address.

    Raises:
        HTTPException: 401 if the token is invalid, 400 if the Google account's
            email is not verified, 503 if Google sign-in is not configured or
            Google could not be reached.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured",
        )

    try:
        # Checks the signature against Google's public certs along with the
        # aud, iss and exp claims. Makes an outbound request to fetch the certs.
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )
    except google_exceptions.TransportError as exc:
        # Google's certs could not be fetched. The token itself is not at fault,
        # so this must not be reported as an authentication failure.
        logger.error("Could not reach Google to verify ID token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach Google to verify sign-in",
        )
    except (ValueError, google_exceptions.GoogleAuthError) as exc:
        # GoogleAuthError is not a ValueError subclass, so both are needed.
        logger.warning("Google ID token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    sub = claims.get("sub")
    email = claims.get("email")

    if not sub:
        logger.warning("Verified Google ID token is missing the 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    # An unverified email cannot be trusted to identify an account, since it
    # would otherwise allow claiming a Formbrew account by that address.
    # Compared explicitly because a truthiness check would accept the string
    # "false" as verified.
    if not email or claims.get("email_verified") not in (True, "true"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account email is not verified",
        )

    return GoogleClaims(sub=sub, email=email.lower())
