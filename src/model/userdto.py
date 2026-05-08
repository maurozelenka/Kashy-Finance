"""Clase DTO para el modelo de Usuario con soporte para Flask-Login."""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class UserDto(UserMixin):
    """Representa a un usuario de la plataforma."""

    def __init__(self, email: str, password: str):
        self._email = email
        self._password_hash = generate_password_hash(password)
        self._avatar_path = None
        self._language = "es"
        self._theme = "dark"
        
    @property
    def email(self) -> str:
        """Devuelve el email del usuario."""
        return self._email

    def set_password(self, password: str):
        self._password_hash = generate_password_hash(password)

    @property
    def avatar_path(self) -> str:
        return getattr(self, "_avatar_path", None)

    @avatar_path.setter
    def avatar_path(self, value: str):
        self._avatar_path = value

    @property
    def language(self) -> str:
        return getattr(self, "_language", "es")

    @language.setter
    def language(self, value: str):
        self._language = value

    @property
    def theme(self) -> str:
        return getattr(self, "_theme", "dark")

    @theme.setter
    def theme(self, value: str):
        self._theme = value

    def check_password(self, password: str) -> bool:
        """Comprueba si la contraseña coincide con el hash."""
        return check_password_hash(self._password_hash, password)

    def get_id(self):
        """Requerido por Flask-Login. Retorna el OID como string."""
        oid = getattr(self, "__oid__", None) or getattr(self, "_oid", None)
        print(f"DEBUG: get_id para {getattr(self, '_email', 'anon')} -> {oid}")
        return str(oid) if oid else None

    @staticmethod
    def current_user(srp, email: str):
        """Busca un usuario por su email en Sirope."""
        for user in srp.filter(UserDto, lambda u: u.email == email):
            return user
        return None
