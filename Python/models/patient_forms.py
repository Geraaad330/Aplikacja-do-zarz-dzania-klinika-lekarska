# patient_forms.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.patient_forms_model_validation import (
    validate_submission_date,
    validate_fk_patient_id_exists,
    validate_fk_form_type_id_exists,
    validate_non_nullable_fields,
    validate_filters_and_sorting,
    validate_update_fields
)


class PatientForms:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `patient_forms` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `patient_forms` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("patient_forms"):
                query = """
                CREATE TABLE IF NOT EXISTS patient_forms (
                    patient_form_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_patient_id INTEGER NOT NULL,
                    fk_form_type_id INTEGER NOT NULL,
                    submission_date TEXT NOT NULL CHECK (
                        submission_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
                    ),
                    content TEXT,
                    FOREIGN KEY (fk_patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (fk_form_type_id) REFERENCES form_types(form_type_id) ON DELETE RESTRICT ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def add_form(self, fk_patient_id: int, fk_form_type_id: int, submission_date: str, content: str = None):
        """
        Dodaje nowy formularz do tabeli `patient_forms`.

        Args:
            fk_patient_id (int): ID pacjenta.
            fk_form_type_id (int): ID typu formularza.
            submission_date (str): Data zgłoszenia w formacie YYYY-MM-DD.
            content (str | None): Opcjonalna treść formularza.

        Returns:
            int: ID nowo dodanego formularza.

        Raises:
            ValueError: Jeśli dane są nieprawidłowe.
        """
        try:
            self.db_controller.ensure_connection()

            # Walidacja
            validate_non_nullable_fields(fk_patient_id, fk_form_type_id, submission_date)
            validate_submission_date(submission_date)
            validate_fk_patient_id_exists(self.db_controller, fk_patient_id)
            validate_fk_form_type_id_exists(self.db_controller, fk_form_type_id)

            query = """
            INSERT INTO patient_forms (fk_patient_id, fk_form_type_id, submission_date, content)
            VALUES (?, ?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(
                query, (fk_patient_id, fk_form_type_id, submission_date, content)
            )
            self.db_controller.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania formularza: {e}") from e

    def get_forms(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `patient_forms` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów w formacie [{"column": ..., "operator": ..., "value": ...}].
            sort_by (list): Lista sortowania w formacie [{"column": ..., "direction": ...}].

        Returns:
            list: Lista rekordów w formie słowników.
        """
        try:
            self.db_controller.ensure_connection()

            valid_columns = ["patient_form_id", "fk_patient_id", "fk_form_type_id", "submission_date", "content"]
            validate_filters_and_sorting(filters, sort_by, valid_columns)

            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM patient_forms WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania formularzy: {e}") from e

    def update_form(self, patient_form_id: int, updates: dict):
        """
        Aktualizuje rekord w tabeli `patient_forms`.

        Args:
            patient_form_id (int): ID formularza do aktualizacji.
            updates (dict): Słownik zawierający pola i ich nowe wartości.

        Raises:
            ValueError: Jeśli dane są nieprawidłowe.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie istnienia rekordu
            query_check = "SELECT COUNT(*) FROM patient_forms WHERE patient_form_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (patient_form_id,))
            record_exists = cursor.fetchone()[0] > 0

            if not record_exists:
                raise RuntimeError(f"Formularz o ID {patient_form_id} nie istnieje.")

            # Walidacja danych
            valid_columns = ["fk_patient_id", "fk_form_type_id", "submission_date", "content"]
            validate_update_fields(updates, valid_columns)

            if "submission_date" in updates:
                validate_submission_date(updates["submission_date"])
            if "fk_patient_id" in updates:
                validate_fk_patient_id_exists(self.db_controller, updates["fk_patient_id"])
            if "fk_form_type_id" in updates:
                validate_fk_form_type_id_exists(self.db_controller, updates["fk_form_type_id"])

            # Aktualizacja danych
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [patient_form_id]
            query = f"UPDATE patient_forms SET {set_clause} WHERE patient_form_id = ?"
            self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji formularza: {e}") from e

    def delete_form(self, patient_form_id: int):
        """
        Usuwa rekord z tabeli `patient_forms`.

        Args:
            patient_form_id (int): ID formularza do usunięcia.

        Raises:
            ValueError: Jeśli ID jest nieprawidłowe lub rekord nie istnieje.
        """
        if not isinstance(patient_form_id, int):
            raise ValueError(f"Nieprawidłowe ID formularza: {patient_form_id}")

        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie istnienia rekordu
            query_check = "SELECT COUNT(*) FROM patient_forms WHERE patient_form_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (patient_form_id,))
            record_exists = cursor.fetchone()[0] > 0

            if not record_exists:
                raise RuntimeError(f"Formularz o ID {patient_form_id} nie istnieje.")

            # Usunięcie rekordu
            query_delete = "DELETE FROM patient_forms WHERE patient_form_id = ?"
            self.db_controller.connection.execute(query_delete, (patient_form_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania formularza: {e}") from e

