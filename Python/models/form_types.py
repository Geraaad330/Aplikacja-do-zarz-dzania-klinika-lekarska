# form_types.py

# # form_types.py# form_types.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.form_types_model_validation import (
    validate_form_name,
    validate_unique_form_name,
    validate_filters_and_sorting,
    validate_update_fields,
   #validate_operator_and_value -->> jest wywoływana w validate_filters_and_sorting
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


class FormTypes:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `form_types` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy form_types z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `form_types` w bazie danych, jeśli jeszcze nie istnieje.
        
        Przykład:
        form_types.create_table()
        
        Wynik:
        Utworzona tabela `form_types` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("form_types"):
                query = """
                CREATE TABLE IF NOT EXISTS form_types (
                    form_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (form_name GLOB '*[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def create_new_record(self, form_name: str) -> sqlite3.Cursor:
        """
        Tworzy nowy rekord w tabeli `form_types` i zwraca kursor.

        Przykład:
            form_types.create_new_record("Zgoda na leczenie")

        Wynik:
            Nowy rekord w tabeli `form_types`.

        Returns:
            sqlite3.Cursor: Kursor pozwalający na pobranie lastrowid.

        Raises:
            ValueError: Jeśli wystąpi błąd walidacji danych.
            RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("form_types"):
                raise RuntimeError("Tabela 'form_types' nie istnieje w bazie danych.")

            # Walidacja nazwy formularza
            validate_form_name(form_name)
            validate_unique_form_name(self.db_controller, form_name)

            query = "INSERT INTO form_types (form_name) VALUES (?)"
            cursor = self.db_controller.connection.execute(query, (form_name,))
            self.db_controller.connection.commit()
            return cursor  # Zwracamy kursor

        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            raise ValueError(f"Błąd podczas dodawania rekordu: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas dodawania rekordu: {e}") from e


    def get_records(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `form_types`.

        Przykład:
        form_types.get_records(filters=[{"column": "form_name", "operator": "LIKE", "value": "Psych%"}])

        Wynik:
        Lista rekordów zgodnych z zapytaniem.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("form_types"):
                raise RuntimeError("Tabela 'form_types' nie istnieje w bazie danych.")
            valid_columns = get_valid_columns(self.db_controller, "form_types")  # Pobierz kolumny dynamicznie
            validate_filters_and_sorting(filters, sort_by, valid_columns)
            query, values = self.db_controller.build_filters(filters, sort_by)
            cursor = self.db_controller.connection.execute(f"SELECT * FROM form_types WHERE {query}", values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e




    def update_record(self, form_type_id: int, updates: dict):
        """
        Aktualizuje rekord w tabeli `form_types` na podstawie ID.
        """
        try:
            if not updates:
                raise ValueError("Nie podano danych do aktualizacji.")

            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM form_types WHERE form_type_id = ?"
            cursor = self.db_controller.connection.execute(query, (form_type_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {form_type_id} nie istnieje.")

            # Walidacja danych aktualizacji za pomocą validate_update_fields
            valid_columns = get_valid_columns(self.db_controller, "form_types")
            validate_update_fields(updates, valid_columns)


            # Walidacja danych aktualizacji
            valid_columns = get_valid_columns(self.db_controller, "form_types")
            for column, value in updates.items():
                if column not in valid_columns:
                    raise ValueError(f"Nieprawidłowa kolumna: {column}")
                if column == "form_name":
                    validate_form_name(value)

            # Aktualizacja rekordu
            set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
            query = f"UPDATE form_types SET {set_clause} WHERE form_type_id = ?"
            params = list(updates.values()) + [form_type_id]
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizowania rekordu: {e}") from e




    def delete_record(self, form_type_id: int):
        """
        Usuwa rekord z tabeli `form_types` na podstawie ID.

        :param form_type_id: ID specjalności do usunięcia.
        :raises RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM form_types WHERE form_type_id = ?"
            cursor = self.db_controller.connection.execute(query, (form_type_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {form_type_id} nie istnieje.")

            # Usunięcie rekordu
            query = "DELETE FROM form_types WHERE form_type_id = ?"
            
            self.db_controller.connection.execute(query, (form_type_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e
