# form_types_controller.py

import sqlite3
from models.form_types import FormTypes
from controllers.database_controller import DatabaseController


class FormTypesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `form_types`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `form_types` oraz model zarządzający danymi spotkań.
        """
        self.db_controller = db_controller
        self.form_types_model = FormTypes(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `form_types` w bazie danych.
        """
        try:
            self.form_types_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `form_types`.") from db_error

    def add_form_types(self, form_name: str) -> int:
        """
        Dodaje nowy typ formularza do tabeli `form_types` i zwraca ID nowo dodanego rekordu.

        Args:
            form_name (str): Nazwa typu formularza.

        Returns:
            int: ID nowo dodanego typu formularza.

        Raises:
            ValueError: Jeśli wystąpi błąd walidacji.
            RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            cursor = self.form_types_model.create_new_record(form_name)
            form_type_id = cursor.lastrowid  # Pobranie ID nowo dodanego rekordu
            return form_type_id
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania nowego typu formularza.") from db_error



    def get_all_form_types(self):
        """
        Pobiera wszystkie rekordy z tabeli `form_types`.
        """
        try:
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")
            return self.form_types_model.get_records()
        except Exception as e:
            raise RuntimeError(f"Błąd podczas pobierania typów spotkań: {e}") from e

    def get_form_types_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera typy spotkań na podstawie filtrów i sortowania.
        """
        try:
            return self.form_types_model.get_records(filters=filters, sort_by=sort_by)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania typów spotkań.") from db_error

    def update_form_types(self, form_type_id: int, updates: dict):
        """
        Aktualizuje typ spotkania na podstawie ID.
        """
        try:
            self.form_types_model.update_record(form_type_id, updates)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji typu spotkania.") from db_error

    def delete_form_types(self, form_type_id: int):
        """
        Usuwa typ spotkania na podstawie ID.
        """
        try:
            self.form_types_model.delete_record(form_type_id)
        except RuntimeError as runtime_error:
            raise RuntimeError(f"Błąd: {runtime_error}") from runtime_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania typu spotkania.") from db_error
