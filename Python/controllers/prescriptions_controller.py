# prescriptions_controller.py

import sqlite3
from models.prescriptions import Prescriptions
from controllers.database_controller import DatabaseController


class PrescriptionsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `prescriptions`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `prescriptions` oraz model zarządzający danymi `prescriptions`.
        """
        self.db_controller = db_controller
        self.prescriptions_model = Prescriptions(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `prescriptions` w bazie danych.
        """
        try:
            self.prescriptions_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `prescriptions`.") from db_error

    def add_prescription(self, appointment_id: int, medicine_name: str, dosage: float, medicine_price: float, prescription_code: str):
        """
        Dodaje nową receptę do tabeli `prescriptions`.

        Args:
            appointment_id (int): ID wizyty.
            medicine_name (str): Nazwa leku.
            dosage (float): Dawka leku.
            medicine_price (float): Cena leku.
            prescription_code (str): Kod recepty.

        Returns:
            dict: Dodana recepta jako słownik.
        """
        try:
            prescription_id = self.prescriptions_model.add_prescription(
                appointment_id, medicine_name, dosage, medicine_price, prescription_code
            )
            return {"prescription_id": prescription_id, "appointment_id": appointment_id, "medicine_name": medicine_name,
                    "dosage": dosage, "medicine_price": medicine_price, "prescription_code": prescription_code}
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania recepty.") from db_error

    def get_prescriptions(self, filters=None, sort_by=None):
        """
        Pobiera recepty z tabeli `prescriptions` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów.
            sort_by (list): Lista parametrów sortowania.

        Returns:
            list[dict]: Lista recept jako słowniki.
        """
        try:
            return self.prescriptions_model.get_prescriptions(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania recept.") from db_error

    def update_prescription(self, prescription_id: int, **update_data) -> bool:
        """
        Aktualizuje receptę na podstawie `prescription_id`.

        Args:
            prescription_id (int): ID recepty do aktualizacji.
            **update_data: Słownik zawierający pola do aktualizacji.

        Returns:
            bool: True jeśli aktualizacja zakończyła się sukcesem, False w przeciwnym razie.
        """
        if not update_data:
            print("[update_prescription] Błąd: Nie podano danych do aktualizacji.")
            return False

        try:
            return self.prescriptions_model.update_prescription(prescription_id, **update_data)
        except sqlite3.Error as db_error:
            print(f"[update_prescription] Błąd bazy danych: {db_error}")
            return False


    def delete_prescription(self, prescription_id: int) -> bool:
        """
        Usuwa receptę na podstawie `prescription_id`.

        Args:
            prescription_id (int): ID recepty do usunięcia.

        Returns:
            bool: True jeśli usunięcie zakończyło się sukcesem, False w przeciwnym razie.
        """
        try:
            return self.prescriptions_model.delete_prescription(prescription_id)
        except sqlite3.Error as db_error:
            print(f"[delete_prescription] Błąd bazy danych podczas usuwania recepty: {db_error}")
            return False




    def get_prescriptions_by_appointment_ids(self, appointment_ids):
        """
        Pobiera wszystkie recepty przypisane do podanych appointment_ids.

        Args:
            appointment_ids (list): Lista identyfikatorów wizyt.

        Returns:
            list[dict]: Lista recept jako słowniki.

        Raises:
            ValueError: Jeśli lista appointment_ids jest pusta lub niepoprawna.
            RuntimeError: W przypadku błędu bazy danych.
        """
        if not appointment_ids or not isinstance(appointment_ids, list):
            raise ValueError("Nieprawidłowa lista appointment_ids. Oczekiwana lista identyfikatorów wizyt.")

        try:
            prescriptions = self.prescriptions_model.get_prescriptions_by_appointment_ids(appointment_ids)
            
            # Debugowanie pobranych danych
            # for prescription in prescriptions:
            #     print(f"[DEBUG] [controller prescriptions] Pobranie recepty: {prescription['prescription_id']} dla appointment_id: {prescription['appointment_id']}")
            
            return prescriptions
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania recept.") from db_error


    def get_all_prescriptions(self):
        """
        Pobiera wszystkie kolumny i rekordy z tabeli 'prescriptions'.

        Returns:
            list: Lista rekordów pobranych z tabeli 'prescriptions'.

        Raises:
            RuntimeError: Błąd bazy danych podczas pobierania recept.
        """
        try:
            return self.prescriptions_model.get_all_prescriptions()
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania recept: {db_error}") from db_error
