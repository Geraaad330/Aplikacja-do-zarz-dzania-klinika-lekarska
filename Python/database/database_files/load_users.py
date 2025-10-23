import sqlite3
import bcrypt
from datetime import datetime


def load_user_data_from_file(file_path):
    """
    Wczytuje dane użytkowników z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi użytkowników.
    :return: Lista słowników z danymi użytkowników.
    """
    user_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 5:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                username = columns[0]
                password = columns[1]
                role_id = int(columns[2])
                employee_id = int(columns[3])
                is_active = int(columns[4])

                user_records.append({
                    "username": username,
                    "password": password,
                    "role_id": role_id,
                    "employee_id": employee_id,
                    "is_active": is_active,
                })
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return user_records


def clear_users(controller):
    """
    Usuwa wszystkich użytkowników z tabeli `users_accounts` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM users_accounts")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'users_accounts'")
        controller.connection.commit()
        print("Wszyscy użytkownicy zostali usunięci z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")


def add_users_to_database(user_data, controller):
    """
    Dodaje listę użytkowników do bazy danych.

    :param user_data: Lista słowników z danymi użytkowników.
    :param controller: Obiekt kontrolera bazy danych.
    """
    for user in user_data:
        try:
            hashed_password = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            expired_at = "2026-01-01 00:00"

            query = """
                INSERT INTO users_accounts (username, password_hash, role_id, employee_id, is_active, created_at, expired)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            controller.connection.execute(query, (
                user["username"],
                hashed_password,
                user["role_id"],
                user["employee_id"],
                user["is_active"],
                created_at,
                expired_at,
            ))
            controller.connection.commit()
            print(f"Użytkownik {user['username']} został dodany pomyślnie.")
        except sqlite3.IntegrityError as e:
            print(f"Błąd integralności: {e} - Użytkownik {user['username']} nie został dodany.")


if __name__ == "__main__":
    from controllers.database_controller import DatabaseController

    # Ścieżka do pliku z danymi użytkowników
    users_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\users_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usunięcie istniejących użytkowników
    clear_users(db_controller)

    # Wczytanie użytkowników z pliku
    user_list = load_user_data_from_file(users_file)

    # Dodanie użytkowników do bazy danych
    add_users_to_database(user_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
