import sqlite3
from argon2 import PasswordHasher
from crypto_utils import encrypt_password,decrypt_password
DB_NAME="pwd_manager.db"
ph=PasswordHasher()

def init_db():
    conn =sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pwd_hash TEXT NOT NULL)
               
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


def register_user(username,password):
    hashed=ph.hash(password)
    try:
        conn=sqlite3.connect(DB_NAME)
        cursor=conn.cursor()
        cursor.execute("INSERT INTO users(username,pwd_hash) VALUES(?,?)",(username,hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def check_user(username,password):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("SELECT id,pwd_hash FROM users WHERE username=?",(username,))
    user=cursor.fetchone()
    conn.close()
    if user:
        try:
            if ph.verify(user[1],password):
                return user
        except:
            return None
    return None

def get_user_passwords(user_id):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("""
    SELECT id,website_name,username,password FROM passwords 
    WHERE user_id=?""",(user_id,))
    passwords=cursor.fetchall()
    conn.close()
    return [{"id": r[0], "website": r[1], "username": r[2], "password": decrypt_password(r[3])} for r in passwords]

def add_password_entry(user_id,website,username,password):
    try:
        encrypted_pwd=encrypt_password(password)
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
