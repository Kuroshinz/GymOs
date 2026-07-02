from __future__ import annotations

import hashlib
import secrets
from typing import Optional


class SecurityManager:
    _instance: Optional["SecurityManager"] = None

    def __new__(cls) -> "SecurityManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._secret_key: Optional[str] = None
        return cls._instance

    def initialize(self, secret_key: str | None = None) -> None:
        self._secret_key = secret_key or secrets.token_hex(32)

    def hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        return f"{salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        salt, stored_hash = hashed.split("$")
        computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
        return computed == stored_hash

    def encrypt(self, data: str) -> str:
        if not self._secret_key:
            raise RuntimeError("SecurityManager not initialized")
        from cryptography.fernet import Fernet
        key = base64.urlsafe_b64encode(hashlib.sha256(self._secret_key.encode()).digest())
        return Fernet(key).encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not self._secret_key:
            raise RuntimeError("SecurityManager not initialized")
        from cryptography.fernet import Fernet
        import base64
        key = base64.urlsafe_b64encode(hashlib.sha256(self._secret_key.encode()).digest())
        return Fernet(key).decrypt(token.encode()).decode()
