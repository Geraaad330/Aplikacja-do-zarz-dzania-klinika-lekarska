import sqlite3
import bcrypt
from datetime import datetime

# Ścieżka do bazy danych
DB_PATH = "klinika.db"

def hash_password(password: str) -> str:
    """Haszowanie hasła przy użyciu bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Weryfikacja hasła."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(email: str, password: str, role_id: int, employee_id: int):
    """Rejestracja nowego użytkownika."""
    hashed_password = hash_password(password)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users_accounts (employee_id, role_id, username, password_hash, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (employee_id, role_id, email, hashed_password, created_at))
            conn.commit()
            print("Użytkownik został zarejestrowany.")
        except sqlite3.IntegrityError as e:
            print(f"Błąd rejestracji: {e}")

def login_user(email: str, password: str):
    """Logowanie użytkownika."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, password_hash, role_id, is_active
            FROM users_accounts
            WHERE username = ?
        """, (email,))
        user = cursor.fetchone()
        if not user:
            return "Nie znaleziono użytkownika."
        
        user_id, hashed_password, role_id, is_active = user
        if not verify_password(password, hashed_password):
            return "Nieprawidłowe hasło."
        
        if is_active == 0:
            return "Konto jest nieaktywne."
        
        # Pobranie uprawnień użytkownika
        cursor.execute("""
            SELECT sp.permission_name
            FROM role_permissions rp
            JOIN system_permissions sp ON rp.permission_id = sp.permission_id
            WHERE rp.role_id = ?
        """, (role_id,))
        permissions = [row[0] for row in cursor.fetchall()]
        
        return {"user_id": user_id, "role_id": role_id, "permissions": permissions}

# Przykład użycia
# Rejestracja nowego użytkownika (tylko do testów)
# register_user("test@example.com", "BezpieczneHaslo123", 1, 1)

# Logowanie użytkownika
result = login_user("test@example.com", "BezpieczneHaslo123")
print(result)
