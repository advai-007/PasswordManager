from cryptography.fernet import Fernet



def encrypt_password(plain_password: str,key:str) -> str:
    cipher=Fernet(key)
    return cipher.encrypt(plain_password.encode()).decode()

def decrypt_password(encrypted_password: str,key:str) -> str:
    cipher=Fernet(key)
    return cipher.decrypt(encrypted_password.encode()).decode()
