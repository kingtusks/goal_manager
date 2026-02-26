from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()
class PasswordManager:
    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed_password: str):
        try:
            return pwd_context.verify(password, hashed_password)
        except Exception as e:
            print(f"verification failed: {e}")
            return False

