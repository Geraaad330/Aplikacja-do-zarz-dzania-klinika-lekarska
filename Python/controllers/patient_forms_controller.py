# patient_forms_controller.py

import sqlite3
from models.patient_forms import PatientForms
from controllers.database_controller import DatabaseController


class PatientFormsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `patient_forms`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `patient_forms` oraz model zarządzający danymi `patient_forms`.

        Args:
            db_controller (DatabaseController): Instancja kontrolera bazy danych.
        """
        self.db_controller = db_controller
        self.patient_forms_model = PatientForms(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `patient_forms` w bazie danych.
        """
        try:
            self.patient_forms_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `patient_forms`.") from db_error

    def add_form(self, fk_patient_id, fk_form_type_id, submission_date, content=None):
        """
        Dodaje nowy formularz do tabeli `patient_forms`.

        Args:
            fk_patient_id (int): ID pacjenta.
            fk_form_type_id (int): ID typu formularza.
            submission_date (str): Data zgłoszenia w formacie YYYY-MM-DD.
            content (str | None): Opcjonalna treść formularza.

        Returns:
            int: ID nowo dodanego formularza.
        """
        try:
            return self.patient_forms_model.add_form(
                fk_patient_id, fk_form_type_id, submission_date, content
            )
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania formularza.") from db_error

    def get_forms(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `patient_forms` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów w formacie [{"column": ..., "operator": ..., "value": ...}].
            sort_by (list): Lista sortowania w formacie [{"column": ..., "direction": ...}].

        Returns:
            list[dict]: Lista formularzy jako słowniki.
        """
        try:
            return self.patient_forms_model.get_forms(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania formularzy.") from db_error

    def update_form(self, form_id, updates):
        """
        Aktualizuje formularz na podstawie `form_id`.

        Args:
            form_id (int): ID formularza do aktualizacji.
            updates (dict): Słownik zawierający pola i ich nowe wartości.

        Returns:
            None
        """
        try:
            self.patient_forms_model.update_form(form_id, updates)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji formularza.") from db_error

    def delete_form(self, form_id):
        """
        Usuwa formularz na podstawie `form_id`.

        Args:
            form_id (int): ID formularza do usunięcia.

        Returns:
            None
        """
        try:
            self.patient_forms_model.delete_form(form_id)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania formularza.") from db_error
