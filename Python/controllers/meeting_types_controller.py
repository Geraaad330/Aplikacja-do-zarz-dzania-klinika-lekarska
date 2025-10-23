# meeting_types_controller.py

import sqlite3
from models.meeting_types import MeetingTypes
from controllers.database_controller import DatabaseController


class MeetingTypesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `meeting_types`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `meeting_types` oraz model zarządzający danymi spotkań.
        """
        self.db_controller = db_controller
        self.meeting_types_model = MeetingTypes(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `meeting_types` w bazie danych.
        """
        try:
            self.meeting_types_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `meeting_types`.") from db_error


    def get_meeting_type_by_id(self, meeting_type_id: int):
        """
        Pobiera nazwę typu spotkania na podstawie podanego ID.

        Args:
            meeting_type_id (int): ID typu spotkania.

        Returns:
            str: Nazwa typu spotkania.
        """
        try:
            return self.meeting_types_model.get_meeting_type_by_id(meeting_type_id)
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania typu spotkania: {db_error}") from db_error
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error



    def add_meeting_type(self, meeting_type_name):
        """
        Dodaje nowy typ spotkania do tabeli `meeting_types`.
        """
        try:
            self.db_controller.ensure_connection()
            query = "INSERT INTO meeting_types (meeting_type) VALUES (?)"
            cursor = self.db_controller.connection.execute(query, (meeting_type_name,))
            self.db_controller.connection.commit()
            return {"meeting_type_id": cursor.lastrowid}
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania typu spotkania: {e}") from e


    def get_all_meeting_types(self):
        """
        Pobiera wszystkie rekordy z tabeli `meeting_types`.
        """
        try:
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")
            return self.meeting_types_model.get_records()
        except Exception as e:
            raise RuntimeError(f"Błąd podczas pobierania typów spotkań: {e}") from e

    def get_meeting_types_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera typy spotkań na podstawie filtrów i sortowania.
        """
        try:
            return self.meeting_types_model.get_records(filters=filters, sort_by=sort_by)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania typów spotkań.") from db_error

    def update_meeting_type(self, meeting_type_id: int, updates: dict):
        """
        Aktualizuje typ spotkania na podstawie ID.
        """
        try:
            self.meeting_types_model.update_record(meeting_type_id, updates)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji typu spotkania.") from db_error

    def delete_meeting_type(self, meeting_type_id: int):
        """
        Usuwa typ spotkania na podstawie ID.
        """
        try:
            self.meeting_types_model.delete_record(meeting_type_id)
        except RuntimeError as runtime_error:
            raise RuntimeError(f"Błąd: {runtime_error}") from runtime_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania typu spotkania.") from db_error
