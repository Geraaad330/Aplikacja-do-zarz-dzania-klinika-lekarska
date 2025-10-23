# users_accounts.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.roles_controller import RolesController
from validators.users_accounts_model_validation import (
    validate_name_field,
    validate_role_name,
    validate_unique_employee_id,
    validate_unique_username,
    validate_datetime_field,
)

class UsersAccounts:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `users_accounts` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy UsersAccounts z kontrolerem bazy danych.
        """
        self.db_controller = db_controller
        self.employees_controller = EmployeesController(db_controller)
        self.roles_controller = RolesController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `users_accounts` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("users_accounts"):
                query = """
                CREATE TABLE IF NOT EXISTS users_accounts (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL UNIQUE,
                    role_id INTEGER NOT NULL,
                    username TEXT NOT NULL UNIQUE CHECK (username GLOB '[a-z0-9_]*'),
                    password_hash TEXT NOT NULL,
                    is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL CHECK (created_at GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]'),
                    last_login TEXT CHECK (last_login GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]' OR last_login IS NULL),
                    expired TEXT CHECK (expired GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]' OR expired IS NULL),
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e


    def add_user_by_ids(
        self,
        employee_id: int,
        role_id: int,
        username: str,
        password_hash: str,
        is_active: int,
        created_at: str,
        last_login: str = None,
        expired: str = None,
    ):
        """
        Dodaje nowego użytkownika na podstawie `employee_id` i `role_id`.
        """
        try:
            # Walidacja kluczy obcych
            employee_exists = self.db_controller.connection.execute(
                "SELECT employee_id FROM employees WHERE employee_id = ?", (employee_id,)
            ).fetchone()
            if not employee_exists:
                raise ValueError(f"Nie znaleziono pracownika o ID {employee_id}.")

            role_exists = self.db_controller.connection.execute(
                "SELECT role_id FROM roles WHERE role_id = ?", (role_id,)
            ).fetchone()
            if not role_exists:
                raise ValueError(f"Nie znaleziono roli o ID {role_id}.")

            # Dodaj rekord do bazy danych
            query = """
            INSERT INTO users_accounts (
                employee_id, role_id, username, password_hash, is_active, created_at, last_login, expired
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                employee_id, role_id, username, password_hash, is_active, created_at, last_login, expired
            )
            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

            return cursor.lastrowid
        except sqlite3.IntegrityError as integrity_error:
            raise ValueError("Błąd integralności: Sprawdź, czy dane są unikalne.") from integrity_error




    def add_user_by_names(self, first_name, last_name, role_name, username, password_hash, is_active, created_at, last_login=None, expired=None):
        try:
            self.db_controller.ensure_connection()
            validate_name_field(first_name)
            validate_name_field(last_name)
            validate_role_name(role_name)
            validate_unique_username(self.db_controller, username)
            validate_datetime_field(created_at)

            # Pobranie ID pracownika i roli
            try:
                employee_id = self.get_employee_id(first_name, last_name)
            except KeyError as exc:
                raise ValueError(f"Pracownik '{first_name} {last_name}' nie istnieje.") from exc
            try:
                role_id = self.get_role_id(role_name)
            except KeyError as exc:
                raise ValueError(f"Rola '{role_name}' nie istnieje.") from exc

            self.add_user_by_ids(employee_id, role_id, username, password_hash, is_active, created_at, last_login, expired)
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas dodawania użytkownika: {e}") from e

    def get_role_id_by_user_id(self, user_id: int) -> int:
        """
        Pobiera role_id przypisany do danego user_id z bazy danych.
        """
        try:
            query = "SELECT role_id FROM users_accounts WHERE user_id = ?"
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query, (user_id,))
            result = cursor.fetchone()

            if result is None:
                # print(f"[DEBUG] Nie znaleziono role_id dla user_id {user_id}.")  # Debugowanie
                raise ValueError(f"Nie znaleziono role_id dla user_id {user_id}.")

            role_id = result["role_id"]
            # print(f"[model users] Pobranie roli zakończone sukcesem: user_id={user_id}, role_id={role_id}")  # Debugowanie
            return role_id  # Wymaga ustawienia row_factory jako dict
        
        except sqlite3.Error as e:
            print(f"[DEBUG] Błąd bazy danych podczas pobierania roli dla user_id {user_id}: {e}")  # Debugowanie
            raise RuntimeError(f"Błąd bazy danych podczas pobierania role_id: {e}") from e
        
    def get_username_by_user_id(self, user_id):
        """
        Pobiera nazwę użytkownika na podstawie ID użytkownika.

        Args:
            user_id (int): ID użytkownika.

        Returns:
            str: Nazwa użytkownika, jeśli istnieje, w przeciwnym razie None.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            SELECT username
            FROM users_accounts
            WHERE user_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (user_id,))
            result = cursor.fetchone()

            if result:
                username = result[0]
                # print(f"model Users: Pobrano username: {username}")  # Debug
                return username
            else:
                print(f"Nie znaleziono użytkownika o ID: {user_id}")  # Debug
                return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania nazwy użytkownika: {e}") from e

    def get_employee_id_by_user_id(self, user_id):
        """
        Pobiera ID pracownika (employee_id) na podstawie ID użytkownika (user_id).

        Args:
            user_id (int): ID użytkownika.

        Returns:
            int: ID pracownika, jeśli istnieje, w przeciwnym razie None.
        """
        try:
            # Upewnij się, że połączenie z bazą danych jest aktywne
            self.db_controller.ensure_connection()

            # Zapytanie SQL do pobrania employee_id
            query = """
            SELECT employee_id
            FROM users_accounts
            WHERE user_id = ?
            """
            # Wykonanie zapytania
            cursor = self.db_controller.connection.execute(query, (user_id,))
            result = cursor.fetchone()

            # Sprawdzenie, czy wynik istnieje
            if result:
                employee_id = result[0]
                # print(f"model Users: Pobrano employee_id: {employee_id}")  # Debug
                return employee_id
            else:
                print(f"Nie znaleziono employee_id dla user_id: {user_id}")  # Debug
                return None

        except sqlite3.Error as e:
            # Obsługa błędu SQL i rzucenie bardziej opisowego wyjątku
            raise RuntimeError(f"Błąd podczas pobierania employee_id dla user_id: {user_id}: {e}") from e




    def get_users_with_names(self, filters=None, sort_by=None):
        try:
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)

            query = f"""
            SELECT
                ua.user_id AS user_id,
                e.first_name || ' ' || e.last_name AS employee_name,
                r.role_name AS role_name,
                ua.username AS username,
                ua.password_hash AS password_hash,
                ua.is_active AS is_active,
                ua.created_at AS created_at,
                ua.last_login AS last_login,
                ua.expired AS expired
            FROM users_accounts ua
            JOIN employees e ON ua.employee_id = e.employee_id
            JOIN roles r ON ua.role_id = r.role_id
            WHERE {query_conditions}
            """
            #print(f"DEBUG: SQL Query: {query}")
            #print(f"DEBUG: Values: {values}")
            cursor = self.db_controller.connection.execute(query, values)
            results = [dict(row) for row in cursor.fetchall()]
            #print(f"DEBUG: Results: {results}")
            #print(f"DEBUG: Employees: {self.employees_controller.get_all_employees()}")
            #print(f"DEBUG: Roles: {self.roles_controller.get_all_roles()}")
            #print(f"DEBUG: Users: {self.get_users_with_filters()}")
            return results
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z nazwami: {e}") from e

    def get_users_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera użytkowników z tabeli `users_accounts` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)

            query = f"""
            SELECT
                user_id,
                employee_id,
                role_id,
                username,
                password_hash,
                is_active,
                created_at,
                last_login,
                expired
            FROM users_accounts
            WHERE {query_conditions}
            """
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e




    def get_employee_id(self, first_name: str, last_name: str) -> int:
        """
        Pobiera ID pracownika na podstawie imienia i nazwiska.

        Przykład:
        get_employee_id("John", "Doe") -> 1
        """
        try:
            employee = self.employees_controller.filter_employees(first_name=first_name, last_name=last_name)
            if not employee:
                raise KeyError(f"Pracownik o imieniu '{first_name}' i nazwisku '{last_name}' nie został znaleziony.")
            return employee[0]["employee_id"]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania ID pracownika: {e}") from e

    def get_role_id(self, role_name: str) -> int:
        """
        Pobiera ID roli na podstawie nazwy.

        Przykład:
        get_role_id("Admin") -> 2
        """
        try:
            role = self.roles_controller.get_role_by_column("role_name", role_name)
            if not role:
                raise KeyError(f"Rola '{role_name}' nie została znaleziona.")
            return role[0]["role_id"]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania ID roli: {e}") from e
        
    def update_user_by_ids(self, user_id, **update_data):
        """
        Aktualizuje dane użytkownika w bazie danych.

        :param user_id: ID użytkownika do aktualizacji.
        :param update_data: Słownik zawierający klucze i wartości do aktualizacji.
        :return: True jeśli aktualizacja się powiodła, False w przeciwnym razie.
        """
        try:
            if not update_data:
                print("[### USERS_ACCOUNTS_CONTROLLER] Brak danych do aktualizacji.")
                return False  # Brak aktualizacji

            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            query = f"UPDATE users_accounts SET {set_clause} WHERE user_id = ?"
            params = list(update_data.values()) + [user_id]

            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

            return cursor.rowcount > 0  # Zwróci True jeśli aktualizacja miała miejsce

        except sqlite3.OperationalError as op_err:
            print(f"[### USERS_ACCOUNTS_CONTROLLER] Błąd operacyjny bazy danych: {op_err}")
            return False
        except sqlite3.DatabaseError as db_err:
            print(f"[### USERS_ACCOUNTS_CONTROLLER] Błąd bazy danych: {db_err}")
            return False



    def update_user_by_names(self, user_id, first_name=None, last_name=None, role_name=None, username=None, password_hash=None, is_active=None, last_login=None, expired=None):
        try:
            updates = []
            params = []

            if first_name and last_name:
                validate_name_field(first_name)
                validate_name_field(last_name)
                try:
                    employee_id = self.get_employee_id(first_name, last_name)
                except KeyError as exc:
                    raise ValueError(f"Pracownik '{first_name} {last_name}' nie istnieje.") from exc
                validate_unique_employee_id(self.db_controller, employee_id)
                updates.append("employee_id = ?")
                params.append(employee_id)
            if role_name:
                validate_role_name(role_name)
                try:
                    role_id = self.get_role_id(role_name)
                except KeyError as exc:
                    raise ValueError(f"Rola '{role_name}' nie istnieje.") from exc
                updates.append("role_id = ?")
                params.append(role_id)
            if username:
                validate_unique_username(self.db_controller, username)
                updates.append("username = ?")
                params.append(username)
            if password_hash:
                updates.append("password_hash = ?")
                params.append(password_hash)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            if last_login:
                validate_datetime_field(last_login)
                updates.append("last_login = ?")
                params.append(last_login)
            if expired:
                validate_datetime_field(expired)
                updates.append("expired = ?")
                params.append(expired)

            if not updates:
                raise ValueError("Brak danych do aktualizacji.")

            params.append(user_id)
            query = f"UPDATE users_accounts SET {', '.join(updates)} WHERE user_id = ?"
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Błąd unikalności: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas aktualizacji użytkownika: {e}") from e




    def delete_user(self, user_id: int):
        """
        Usuwa rekord z tabeli `users_accounts` na podstawie `user_id`.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie istnienia rekordu w tabeli users_accounts
            query_check = "SELECT COUNT(*) FROM users_accounts WHERE user_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (user_id,))
            if cursor.fetchone()[0] == 0:
                raise KeyError(f"Nie znaleziono użytkownika o podanym ID: {user_id}")

            # Usunięcie rekordu
            query_delete = "DELETE FROM users_accounts WHERE user_id = ?"
            self.db_controller.connection.execute(query_delete, (user_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e
   


    def update_last_login(self, user_id: int, last_login: str):
        """
        Aktualizuje kolumnę last_login dla danego użytkownika.
        
        Args:
            user_id (int): ID użytkownika.
            last_login (str): Aktualny czas logowania w formacie YYYY-MM-DD HH:MM.
        """
        try:
            self.db_controller.ensure_connection()
            query = "UPDATE users_accounts SET last_login = ? WHERE user_id = ?"
            self.db_controller.connection.execute(query, (last_login, user_id))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji last_login: {e}") from e
        


    def get_user_by_id(self, user_id):
        """
        Pobiera dane użytkownika na podstawie `user_id`.

        :param user_id: ID użytkownika do pobrania.
        :return: Słownik z danymi użytkownika lub None, jeśli użytkownik nie istnieje.
        """
        try:
            # Sprawdzenie, czy user_id to liczba całkowita
            if not isinstance(user_id, int):
                raise ValueError(f"Nieprawidłowy format `user_id`: {user_id}. Oczekiwano liczby całkowitej.")

            # Pobranie danych użytkownika z bazy danych
            query = """
                SELECT user_id, employee_id, role_id, username, is_active, created_at, last_login, expired
                FROM users_accounts
                WHERE user_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (user_id,))
            user_data = cursor.fetchone()

            if user_data is None:
                return None  # Brak użytkownika w bazie

            return dict(user_data)

        except sqlite3.OperationalError as op_err:
            print(f"[### USERS_ACCOUNTS_MODEL] Błąd operacyjny bazy danych: {op_err}")
            return None
        except sqlite3.DatabaseError as db_err:
            print(f"[### USERS_ACCOUNTS_MODEL] Błąd bazy danych: {db_err}")
            return None
        except ValueError as ve:
            print(f"[### USERS_ACCOUNTS_MODEL] Błąd wartości: {ve}")
            return None
        except TypeError as te:
            print(f"[### USERS_ACCOUNTS_MODEL] Błąd typu danych: {te}")
            return None
        

