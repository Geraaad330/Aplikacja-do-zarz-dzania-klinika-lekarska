# diagnoses_controller.py

import sqlite3
from models.diagnoses import Diagnoses
from controllers.database_controller import DatabaseController


class DiagnosesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `diagnoses`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `diagnoses` oraz model zarządzający danymi `diagnoses`.
        """
        self.db_controller = db_controller
        self.diagnoses_model = Diagnoses(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `diagnoses` w bazie danych.
        """
        try:
            self.diagnoses_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `diagnoses`.") from db_error

    def add_diagnosis(self, appointment_id: int, description: str, icd11_code: str) -> bool:
        """
        Dodaje nową diagnozę do tabeli `diagnoses`.

        Args:
            appointment_id (int): ID wizyty.
            description (str): Opis diagnozy.
            icd11_code (str): Kod diagnozy ICD-11.

        Returns:
            bool: True jeśli dodanie się powiodło, False w przeciwnym razie.
        """
        try:
            self.diagnoses_model.add_diagnosis(appointment_id, description, icd11_code)
            return True
        except sqlite3.Error as db_error:
            print(f"[ERROR] Błąd bazy danych podczas dodawania diagnozy: {db_error}")
            return False

    def get_diagnoses(self, filters=None, sort_by=None):
        """
        Pobiera diagnozy z tabeli `diagnoses` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów.
            sort_by (list): Lista parametrów sortowania.

        Returns:
            list[dict]: Lista diagnoz jako słowniki.
        """
        try:
            return self.diagnoses_model.get_diagnoses(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania diagnoz.") from db_error

    def update_diagnosis(
        self,
        diagnosis_id: int,
        fk_appointment_id: int = None,
        description: str = None,
        icd11_code: str = None,
    ) -> bool:
        """
        Aktualizuje rekord w tabeli `diagnoses` za pomocą modelu.

        :param diagnosis_id: ID diagnozy do aktualizacji.
        :param fk_appointment_id: Nowe ID wizyty (opcjonalne). ✅ POPRAWIONE
        :param description: Nowy opis diagnozy (opcjonalne).
        :param icd11_code: Nowy kod ICD-11 diagnozy (opcjonalne).
        :return: True jeśli aktualizacja się powiodła, False w przeciwnym razie.
        """
        if not any([fk_appointment_id, description, icd11_code]):  # ✅ POPRAWIONE
            print("[update_diagnosis] Błąd: Nie podano danych do aktualizacji.")
            return False

        try:
            return self.diagnoses_model.update_diagnosis(
                diagnosis_id=diagnosis_id,
                appointment_id=fk_appointment_id,  # ✅ POPRAWIONE
                description=description,
                icd11_code=icd11_code,
            )
        except sqlite3.OperationalError as op_err:
            print(f"[update_diagnosis] Błąd operacyjny bazy danych: {op_err}")
            return False
        except sqlite3.DatabaseError as db_err:
            print(f"[update_diagnosis] Błąd bazy danych: {db_err}")
            return False
        except ValueError as ve:
            print(f"[update_diagnosis] Błąd wartości: {ve}")
            return False




    def delete_diagnosis(self, diagnosis_id: int) -> bool:
        """
        Usuwa diagnozę na podstawie `diagnosis_id`.

        Args:
            diagnosis_id (int): ID diagnozy.

        Returns:
            bool: True jeśli usunięcie się powiodło, False jeśli nie.
        """
        try:
            return self.diagnoses_model.delete_diagnosis(diagnosis_id)  # Zwracamy wynik metody modelu

        except sqlite3.Error as db_error:
            print(f"[delete_diagnosis] Błąd bazy danych podczas usuwania diagnozy: {db_error}")
            return False  # W przypadku błędu zwracamy False




    def get_diagnoses_by_appointment_ids(self, appointment_ids):
        """
        Pobiera wszystkie diagnozy przypisane do podanych appointment_id za pomocą modelu diagnoses.

        :param appointment_ids: Lista ID wizyt (appointment_id).
        :return: Słownik z appointment_id jako kluczami i listami diagnoz jako wartościami.
        :raises ValueError: W przypadku, gdy lista appointment_ids jest pusta.
        :raises sqlite3.OperationalError: W przypadku błędów operacyjnych w bazie danych.
        :raises sqlite3.DatabaseError: W przypadku ogólnych błędów bazy danych.
        """
        if not appointment_ids:
            raise ValueError("Lista appointment_ids nie może być pusta.")

        try:
            # Wywołanie metody z modelu diagnoses
            diagnoses = self.diagnoses_model.get_diagnoses_by_appointment_ids(appointment_ids)
            # print(f"[DEBUG] Pobrane diagnozy: {diagnoses}")  # Debugowanie
            return diagnoses
        except sqlite3.OperationalError as e:
            print(f"[ERROR] Błąd operacyjny bazy danych: {e}")
            raise sqlite3.OperationalError(f"Błąd operacyjny bazy danych: {e}") from e
        except sqlite3.DatabaseError as e:
            print(f"[ERROR] Błąd bazy danych: {e}")
            raise sqlite3.DatabaseError(f"Błąd bazy danych: {e}") from e
        

    def get_all_diagnoses(self):
        """
        Pobiera wszystkie rekordy z tabeli `diagnoses` za pomocą modelu.

        Returns:
            list: Lista słowników reprezentujących wszystkie rekordy z tabeli `diagnoses`.
        
        Raises:
            RuntimeError: W przypadku błędu bazy danych podczas pobierania rekordów.
        """
        try:
            # Wywołanie metody modelu
            return self.diagnoses_model.get_all_diagnoses()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania wszystkich rekordów z tabeli `diagnoses`.") from db_error
