import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError

from app.core.exceptions import AppException
from config import settings


class KeycloakJwtAuthentication(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AppException.Unauthorized(
                    error_message="invalid authentication scheme"
                )
            return self.decode_token(token=credentials.credentials)

    # noinspection PyMethodMayBeStatic
    def decode_token(self, token: str):
        try:
            payload: dict = jwt.decode(
                jwt=token,
                key=settings.jwt_public_key,
                algorithms=settings.jwt_algorithms,
                audience="account",
                issuer=f"{settings.keycloak_uri}/auth/realms/{settings.keycloak_realm}",
            )
            return payload
        except PyJWTError as exc:
            raise AppException.OperationError(error_message=exc.args)
