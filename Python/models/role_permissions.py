# role_permissions.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.roles_controller import RolesController
from controllers.permissions_controller import PermissionsController
from validators.role_permissions_model_validation import (
    validate_role_name,
    validate_permission_name,
    validate_role_exists,
    validate_permission_exists,
    validate_role_id_exists,
    validate_permission_id_exists,
    validate_unique_role_permission,
    validate_unique_role_permission_by_names,
    validate_filters_and_sorting,
    validate_operator_and_value
)

def get_valid_columns(db_controller, table_name: str) -> list:
    """
    Pobiera listę kolumn dla podanej tabeli z bazy danych.
    :param db_controller: Obiekt kontrolera bazy danych.
    :param table_name: Nazwa tabeli.
    :return: Lista nazw kolumn.
    """
    db_controller.ensure_connection()
    query = f"PRAGMA table_info({table_name})"
    cursor = db_controller.connection.execute(query)
    return [row["name"] for row in cursor.fetchall()]

class RolePermissions:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `role_permissions` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy RolePermissions z kontrolerem bazy danych.
        """
        self.db_controller = db_controller
        self.roles_controller = RolesController(db_controller)
        self.permissions_controller = PermissionsController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `role_permissions` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("role_permissions"):
                query = """
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role_permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
                    FOREIGN KEY (permission_id) REFERENCES system_permissions(permission_id) ON DELETE CASCADE,
                    UNIQUE (role_id, permission_id)
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def add_role_permission_by_ids(self, role_id: int, permission_id: int):
        """
        Dodaje nowy rekord na podstawie `role_id` i `permission_id`.
        """
        try:
            if not role_id or not permission_id:
                raise ValueError("Brakujące dane: role_id i permission_id są wymagane.")

            # Walidacja uprawnień przed walidacją ról
            validate_permission_id_exists(self.permissions_controller, permission_id)
            validate_role_id_exists(self.roles_controller, role_id)
            validate_unique_role_permission(self.db_controller, role_id, permission_id)

            self.db_controller.ensure_connection()
            query = "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)"
            self.db_controller.connection.execute(query, (role_id, permission_id))
            self.db_controller.connection.commit()
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error






    def add_role_permission_by_names(self, role_name: str, permission_name: str):
        """
        Dodaje nowy rekord na podstawie nazw roli i uprawnienia.

        Przykład:
        add_role_permission_by_names("Admin", "Read")
        """
        validate_role_name(role_name)
        validate_permission_name(permission_name)
        validate_role_exists(self.roles_controller, role_name)
        validate_permission_exists(self.permissions_controller, permission_name)
        validate_unique_role_permission_by_names(
            self.db_controller, self.roles_controller, self.permissions_controller, role_name, permission_name
        )
        role_id = self.get_role_id(role_name)
        permission_id = self.get_permission_id(permission_name)
        self.add_role_permission_by_ids(role_id, permission_id)



    def get_role_id(self, role_name: str) -> int:
        """
        Pobiera ID roli na podstawie nazwy.

        Przykład:
        get_role_id("Admin") -> 1
        """
        results = self.roles_controller.get_role_by_column("role_name", role_name)
        if not results:
            raise KeyError(f"Rola '{role_name}' nie została znaleziona.")
        return results[0]["role_id"]



    def get_permission_id(self, permission_name: str) -> int:
        """
        Pobiera ID uprawnienia na podstawie nazwy.

        Przykład:
        get_permission_id("Read") -> 2
        """
        results = self.permissions_controller.filter_permissions(permission_names=[permission_name])
        if not results:
            raise KeyError(f"Uprawnienie '{permission_name}' nie zostało znalezione.")
        return results[0]["permission_id"]



    def get_all_role_permissions(self):
        """
        Pobiera wszystkie rekordy z tabeli `role_permissions`.

        Przykład:
        get_all_role_permissions() -> [{"role_id": 1, "permission_id": 2}, ...]
        """
        try:
            self.db_controller.ensure_connection()
            query = "SELECT * FROM role_permissions"
            cursor = self.db_controller.connection.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e

    def get_role_permission_by_ids(self, role_id: int, permission_id: int):
        """
        Pobiera rekord na podstawie `role_id` i `permission_id`.

        Jeśli rekord nie istnieje, zgłasza `KeyError`.

        Przykład:
        get_role_permission_by_ids(1, 2) -> {"role_id": 1, "permission_id": 2}
        """
        try:
            self.db_controller.ensure_connection()
            validate_operator_and_value("=", role_id)
            validate_operator_and_value("=", permission_id)

            query = "SELECT * FROM role_permissions WHERE role_id = ? AND permission_id = ?"
            cursor = self.db_controller.connection.execute(query, (role_id, permission_id))
            record = cursor.fetchone()

            # Jeśli rekord nie istnieje, zgłoś kontrolowany wyjątek
            if not record:
                raise KeyError("Rekord nie istnieje.")
            
            return dict(record)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordu.") from db_error


    def get_records_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `role_permissions` z opcjonalnymi filtrami i sortowaniem.
        """
        # Lista dozwolonych kolumn w tabeli
        valid_columns = ["role_id", "permission_id", "role_permission_id"]

        try:
            # Upewnij się, że połączenie jest aktywne
            self.db_controller.ensure_connection()

            # Walidacja filtrów i sortowania
            validate_filters_and_sorting(filters, sort_by, valid_columns)

            # Konwersja `sort_by` na listę krotek (column, direction)
            if sort_by:
                sort_by = [(item["column"], item["direction"]) for item in sort_by]

            # Przekazanie danych do DatabaseController
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM role_permissions WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych: {db_error}") from db_error
        except Exception as unexpected_error:
            raise RuntimeError(f"Nieoczekiwany błąd: {unexpected_error}") from unexpected_error







    def update_role_permission_by_ids(self, role_permission_id: int, role_id: int = None, permission_id: int = None):
        """
        Aktualizuje rekord na podstawie `role_permission_id`, wpisując nowe wartości `role_id` lub `permission_id`.
        """
        try:
            # Walidacja istnienia ról i uprawnień
            if role_id:
                validate_role_id_exists(self.roles_controller, role_id)
            if permission_id:
                validate_permission_id_exists(self.permissions_controller, permission_id)

            # Sprawdzenie, czy kombinacja już istnieje
            if role_id and permission_id:
                query = """
                SELECT role_permission_id FROM role_permissions
                WHERE role_id = ? AND permission_id = ? AND role_permission_id != ?
                """
                existing_record = self.db_controller.connection.execute(query, (role_id, permission_id, role_permission_id)).fetchone()
                if existing_record:
                    raise ValueError(f"Kombinacja rola={role_id} i uprawnienie={permission_id} już istnieje.")

            self.db_controller.ensure_connection()

            updates = []
            params = []

            # Dodanie wartości do aktualizacji
            if role_id is not None:
                updates.append("role_id = ?")
                params.append(role_id)
            if permission_id is not None:
                updates.append("permission_id = ?")
                params.append(permission_id)

            # Sprawdzenie, czy jest coś do aktualizacji
            if not updates:
                raise ValueError("Nie podano żadnych wartości do aktualizacji.")

            # Budowanie zapytania SQL
            params.append(role_permission_id)
            query = f"UPDATE role_permissions SET {', '.join(updates)} WHERE role_permission_id = ?"
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

        except sqlite3.IntegrityError as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rekordu: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rekordu: {e}") from e


    def update_role_permission_by_names(self, role_permission_id: int, role_name: str = None, permission_name: str = None):
        """
        Aktualizuje rekord w tabeli `role_permissions` na podstawie nazw roli i uprawnienia.
        """
        try:
            # Sprawdzenie istnienia rekordu
            query_check = "SELECT * FROM role_permissions WHERE role_permission_id = ?"
            record = self.db_controller.connection.execute(query_check, (role_permission_id,)).fetchone()

            if not record:
                raise KeyError("Nie znaleziono rekordu o podanym ID.")

            updates = []
            params = []

            if role_name:
                roles = self.roles_controller.get_role_by_column("role_name", role_name)
                if not roles:
                    raise ValueError(f"Rola '{role_name}' nie istnieje.")
                role_id = roles[0]["role_id"]
                updates.append("role_id = ?")
                params.append(role_id)
            else:
                role_id = record["role_id"]

            if permission_name:
                permissions = self.permissions_controller.filter_permissions([permission_name])
                if not permissions:
                    raise ValueError(f"Uprawnienie '{permission_name}' nie istnieje.")
                permission_id = permissions[0]["permission_id"]
                updates.append("permission_id = ?")
                params.append(permission_id)
            else:
                permission_id = record["permission_id"]

            # Walidacja unikalności kombinacji role_id i permission_id
            query_unique_check = """
            SELECT role_permission_id FROM role_permissions
            WHERE role_id = ? AND permission_id = ? AND role_permission_id != ?
            """
            existing_record = self.db_controller.connection.execute(query_unique_check, (role_id, permission_id, role_permission_id)).fetchone()
            if existing_record:
                raise ValueError(f"Kombinacja rola='{role_name}' i uprawnienie='{permission_name}' już istnieje.")

            if not updates:
                raise ValueError("Nie podano żadnych wartości do aktualizacji.")

            params.append(role_permission_id)
            query_update = f"UPDATE role_permissions SET {', '.join(updates)} WHERE role_permission_id = ?"
            self.db_controller.connection.execute(query_update, params)
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as exc:
            raise RuntimeError("Błąd bazy danych: naruszenie unikalności rekordu.") from exc





    def delete_role_permission_by_id(self, role_permission_id: int):
        """
        Usuwa rekord z tabeli `role_permissions` na podstawie `role_permission_id`.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie istnienia rekordu
            query_check = "SELECT * FROM role_permissions WHERE role_permission_id = ?"
            record = self.db_controller.connection.execute(query_check, (role_permission_id,)).fetchone()

            if not record:
                raise KeyError("Nie znaleziono rekordu o podanym ID.")

            query = "DELETE FROM role_permissions WHERE role_permission_id = ?"
            self.db_controller.connection.execute(query, (role_permission_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych: {db_error}") from db_error
        except KeyError as key_error:
            raise KeyError(f"Błąd: {key_error}") from key_error



    def delete_records_by_role_or_permission(self, role_id: int = None, permission_id: int = None):
        """
        Usuwa wszystkie rekordy związane z podanym `role_id` lub `permission_id`.

        :param role_id: ID roli, której rekordy mają zostać usunięte (opcjonalnie).
        :param permission_id: ID uprawnienia, którego rekordy mają zostać usunięte (opcjonalnie).

        Przykład wywołania:
        delete_records_by_role_or_permission(role_id=1)
        delete_records_by_role_or_permission(permission_id=2)

        Przykładowy wynik:
        Wszystkie rekordy z `role_id=1` lub `permission_id=2` zostaną usunięte.
        """
        try:
            self.db_controller.ensure_connection()

            conditions = []
            params = []

            if role_id is not None:
                validate_role_id_exists(self.roles_controller, role_id)
                conditions.append("role_id = ?")
                params.append(role_id)

            if permission_id is not None:
                validate_permission_id_exists(self.permissions_controller, permission_id)
                conditions.append("permission_id = ?")
                params.append(permission_id)

            if not conditions:
                raise ValueError("Musisz podać `role_id` lub `permission_id`.")

            query = f"DELETE FROM role_permissions WHERE {' OR '.join(conditions)}"
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordów: {e}") from e


    def delete_record_by_role_and_permission(self, role_id: int = None, permission_id: int = None):
        """
        Usuwa rekord z tabeli `role_permissions` na podstawie `role_id` i `permission_id`.
        """
        try:
            self.db_controller.ensure_connection()

            if role_id is None and permission_id is None:
                raise ValueError("Musisz podać co najmniej `role_id` lub `permission_id`.")

            conditions = []
            params = []

            if role_id is not None:
                conditions.append("role_id = ?")
                params.append(role_id)
            if permission_id is not None:
                conditions.append("permission_id = ?")
                params.append(permission_id)

            query_check = f"SELECT * FROM role_permissions WHERE {' AND '.join(conditions)}"
            record = self.db_controller.connection.execute(query_check, params).fetchone()

            if not record:
                raise KeyError("Nie znaleziono rekordu o podanych wartościach.")

            query = f"DELETE FROM role_permissions WHERE {' AND '.join(conditions)}"
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych: {db_error}") from db_error
        except KeyError as key_error:
            raise KeyError(f"Błąd: {key_error}") from key_error



