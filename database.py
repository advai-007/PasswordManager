import base64
import os
import sqlite3
from argon2 import PasswordHasher
from crypto_utils import encrypt_password,decrypt_password
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os, base64
from cryptography.hazmat.backends import default_backend
DB_NAME="pwd_manager.db"
ph=PasswordHasher()

# Initialize the database and create tables if they don't exist
def init_db():
    conn =sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pwd_hash TEXT NOT NULL,
        encryption_salt TEXT NOT NULL
    )
               
    """)
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        website_name TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id))
    """)
    conn.commit()
    conn.close()

# User registration
def register_user(username,password):
    hashed=ph.hash(password)
    salt=base64.urlsafe_b64encode(os.urandom(16)).decode()
    try:
        conn=sqlite3.connect(DB_NAME)
        cursor=conn.cursor()
        cursor.execute("INSERT INTO users(username,pwd_hash,encryption_salt) VALUES(?,?,?)",(username,hashed,salt))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# User authentication

def check_user(username,password):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("SELECT id,pwd_hash,encryption_salt FROM users WHERE username=?",(username,))
    user=cursor.fetchone()
    conn.close()
    if user:
        try:
            if ph.verify(user[1],password):
                salt = base64.urlsafe_b64decode(user[2].encode())
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100_000,
                    backend=default_backend()
                )
                key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
                return (user[0], key)
        except:
            return None
    return None

# Fetch user passwords

def get_user_passwords(user_id,session_key):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("""
    SELECT id,website_name,username,password FROM passwords 
    WHERE user_id=?""",(user_id,))
    passwords=cursor.fetchall()
    conn.close()
    return [{"id": r[0], "website": r[1], "username": r[2], "password": decrypt_password(r[3], session_key)} for r in passwords]

# Add a new password entry
def add_password_entry(user_id,website,username,password,session_key):
    try:
        encrypted_pwd=encrypt_password(password,session_key)
        conn=sqlite3.connect(DB_NAME)
        cursor=conn.cursor()
        cursor.execute("""
        INSERT INTO passwords (user_id,website_name,username,password) VALUES(?,?,?,?)
        """,(user_id,website,username,encrypted_pwd))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False
    

def delete_password_entry(password_id, user_id):
    """
    Deletes a password entry from the database.
    It checks both the password ID and the user ID for security.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM passwords 
            WHERE id = ? AND user_id = ?
        """, (password_id, user_id))
        conn.commit()
        # Check if any row was actually deleted
        rows_deleted = cursor.rowcount
        conn.close()
        return rows_deleted > 0
    except sqlite3.Error as e:
        print(f"Database error on deleting password: {e}")
        return False
