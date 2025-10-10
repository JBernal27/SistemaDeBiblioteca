"""
Middleware y utilidades de autenticación para el sistema de biblioteca.

Este módulo proporciona las herramientas necesarias para:
- Autenticación mediante tokens JWT
- Verificación de roles de usuario
- Protección de endpoints que requieren autenticación
- Manejo de permisos de administrador

Clases:
    JWTBearer: Middleware para manejar la autenticación JWT

Funciones:
    verify_jwt_token: Verifica y decodifica tokens JWT
    get_current_user: Dependency para obtener el usuario actual
    require_admin: Dependency para verificar permisos de administrador
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timezone
from typing import Optional
import os
from models.schemas import TokenData
from common.enums.roles_enum import RolEnum

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class JWTBearer(HTTPBearer):
    """
    Middleware para autenticación JWT usando el esquema Bearer.
    Hereda de HTTPBearer de FastAPI para manejar la autenticación basada en tokens JWT.

    Attributes:
        auto_error (bool): Si es True, genera automáticamente errores HTTP. Por defecto es True.
    """

    def __init__(self, auto_error: bool = True):
        """
        Inicializa el middleware JWT Bearer.

        Args:
            auto_error (bool): Si es True, genera automáticamente errores HTTP.
        """
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )

        if not SECRET_KEY or not ALGORITHM:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: SECRET_KEY or ALGORITHM not set",
            )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
            )

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )

        return credentials


def verify_jwt_token(token: str) -> TokenData:
    """
    Verifica y decodifica un token JWT.

    Args:
        token (str): El token JWT a verificar.

    Returns:
        TokenData: Objeto con la información del usuario extraída del token.

    Raises:
        HTTPException(401): Si el token es inválido o ha expirado.
        HTTPException(500): Si las variables de entorno necesarias no están configuradas.
    """
    try:
        if not SECRET_KEY or not ALGORITHM:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: SECRET_KEY or ALGORITHM not set",
            )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            raise JWTError("Token no tiene fecha de expiración")
        if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise JWTError("Token expirado")

        return TokenData(
            id=payload.get("id"),
            email=payload.get("email"),
            rol=payload.get("rol"),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(JWTBearer()),
) -> TokenData:
    """
    Dependency para obtener el usuario actual a partir del token JWT.
    Se usa como dependencia en los endpoints que requieren autenticación.

    Args:
        credentials (HTTPAuthorizationCredentials): Credenciales de autenticación extraídas del header.
            Inyectado automáticamente por FastAPI.

    Returns:
        TokenData: Información del usuario autenticado.

    Raises:
        HTTPException: Si hay algún problema con la autenticación.
    """
    return verify_jwt_token(credentials.credentials)


def require_admin(user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Dependency para verificar que el usuario actual tiene rol de administrador.
    Se usa como dependencia en los endpoints que requieren permisos de administrador.

    Args:
        user (TokenData): Información del usuario actual, inyectada automáticamente
            por FastAPI usando get_current_user.

    Returns:
        TokenData: La información del usuario si es administrador.

    Raises:
        HTTPException(403): Si el usuario no tiene rol de administrador.
    """
    if user.rol != RolEnum.admin:
        print(user.rol)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    return user
