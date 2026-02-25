from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

pwd_context = PasswordHash((Argon2Hasher(),))

class PasswordManager:
    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed_password: str):
        try:
            pwd_context.verify(password, hashed_password)
            return True
        except:
            return False

    @staticmethod
    def needs_rehash(hashed_password: str):
        return pwd_context.needs_rehash(hashed_password)
