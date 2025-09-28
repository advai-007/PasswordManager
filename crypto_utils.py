from cryptography.fernet import Fernet




KEY = b'w8YQQvDGwurFJbbsDuG_Zng-1uVrR7LhTQx2jJsRALg='  # Replace with Fernet.generate_key() output
cipher = Fernet(KEY)

def encrypt_password(plain_password: str) -> str:
    return cipher.encrypt(plain_password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return cipher.decrypt(encrypted_password.encode()).decode()
