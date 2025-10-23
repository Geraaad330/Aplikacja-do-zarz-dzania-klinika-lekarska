# meeting_types.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.meeting_types_model_validation import (
    validate_meeting_type,
    validate_unique_meeting_type,
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


class MeetingTypes:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `meeting_types` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy meeting_types z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `meeting_types` w bazie danych, jeśli jeszcze nie istnieje.
        
        Przykład:
        meeting_types.create_table()
        
        Wynik:
        Utworzona tabela `meeting_types` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("meeting_types"):
                query = """
                CREATE TABLE IF NOT EXISTS meeting_types (
                    meeting_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (meeting_type GLOB '*[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:+.,/%\\*]*')
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e


    def get_meeting_type_by_id(self, meeting_type_id: int) -> str:
        """
        Pobiera nazwę typu spotkania na podstawie podanego ID.
        """
        try:
            # Upewnij się, że połączenie z bazą danych jest aktywne
            self.db_controller.ensure_connection()

            # Sprawdzenie istnienia rekordu
            query = "SELECT meeting_type FROM meeting_types WHERE meeting_type_id = ?"
            cursor = self.db_controller.connection.execute(query, (meeting_type_id,))
            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(f"Rekord o ID {meeting_type_id} nie istnieje.")

            # Debugowanie: Wyświetl pobrane dane
            # print(f"MODEL MEETING TYPES Debug: Pobrany typ spotkania: {result['meeting_type']} dla meeting_type_id: {meeting_type_id}")

            return result["meeting_type"]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania typu spotkania: {e}") from e


    def create_new_record(self, meeting_type: str):
        """
        Tworzy nowy rekord w tabeli `meeting_types`.

        Przykład:
        meeting_types.create_new_record("Konsylium terapeutyczne")

        Wynik:
        Nowy rekord w tabeli `meeting_types`.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("meeting_types"):
                raise RuntimeError("Tabela 'meeting_types' nie istnieje w bazie danych.")
            validate_meeting_type(meeting_type)
            validate_unique_meeting_type(self.db_controller, meeting_type)
            query = "INSERT INTO meeting_types (meeting_type) VALUES (?)"
            self.db_controller.connection.execute(query, (meeting_type,))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            raise ValueError(f"Błąd podczas dodawania rekordu: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas dodawania rekordu: {e}") from e

    def get_records(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `meeting_types`.

        Przykład:
        meeting_types.get_records(filters=[{"column": "meeting_type", "operator": "LIKE", "value": "Psych%"}])

        Wynik:
        Lista rekordów zgodnych z zapytaniem.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("meeting_types"):
                raise RuntimeError("Tabela 'meeting_types' nie istnieje w bazie danych.")
            valid_columns = get_valid_columns(self.db_controller, "meeting_types")  # Pobierz kolumny dynamicznie
            validate_filters_and_sorting(filters, sort_by, valid_columns)
            query, values = self.db_controller.build_filters(filters, sort_by)
            cursor = self.db_controller.connection.execute(f"SELECT * FROM meeting_types WHERE {query}", values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e




    def update_record(self, meeting_type_id: int, updates: dict):
        """
        Aktualizuje rekord w tabeli `meeting_types` na podstawie ID.
        """
        try:
            if not updates:
                raise ValueError("Nie podano danych do aktualizacji.")

            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM meeting_types WHERE meeting_type_id = ?"
            cursor = self.db_controller.connection.execute(query, (meeting_type_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {meeting_type_id} nie istnieje.")

            # Walidacja danych aktualizacji za pomocą validate_update_fields
            valid_columns = get_valid_columns(self.db_controller, "meeting_types")
            validate_update_fields(updates, valid_columns)


            # Walidacja danych aktualizacji
            valid_columns = get_valid_columns(self.db_controller, "meeting_types")
            for column, value in updates.items():
                if column not in valid_columns:
                    raise ValueError(f"Nieprawidłowa kolumna: {column}")
                if column == "meeting_type":
                    validate_meeting_type(value)

            # Aktualizacja rekordu
            set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
            query = f"UPDATE meeting_types SET {set_clause} WHERE meeting_type_id = ?"
            params = list(updates.values()) + [meeting_type_id]
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizowania rekordu: {e}") from e




    def delete_record(self, meeting_type_id: int):
        """
        Usuwa rekord z tabeli `meeting_types` na podstawie ID.

        :param meeting_type_id: ID specjalności do usunięcia.
        :raises RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM meeting_types WHERE meeting_type_id = ?"
            cursor = self.db_controller.connection.execute(query, (meeting_type_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {meeting_type_id} nie istnieje.")

            # Usunięcie rekordu
            query = "DELETE FROM meeting_types WHERE meeting_type_id = ?"
            
            self.db_controller.connection.execute(query, (meeting_type_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e