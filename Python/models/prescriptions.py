# prescriptions.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.prescriptions_model_validation import (
    validate_medicine_name,
    validate_fk_appointment_exists,
    validate_dosage,
    validate_medicine_price,
    validate_prescription_code,
    validate_filters_and_sorting,
    validate_operator_and_value
)


class Prescriptions:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `prescriptions` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Prescriptions z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `prescriptions` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("prescriptions"):
                query = """
                CREATE TABLE IF NOT EXISTS prescriptions (
                    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER NOT NULL,
                    medicine_name TEXT NOT NULL CHECK (medicine_name GLOB '[A-Za-z ]*'),
                    dosage REAL NOT NULL CHECK (dosage > 0 AND dosage <= 10000),
                    medicine_price REAL NOT NULL CHECK (medicine_price >= 0),
                    prescription_code TEXT NOT NULL CHECK (LENGTH(prescription_code) = 4 AND prescription_code GLOB '[0-9]*'),
                    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
                    ON DELETE SET NULL ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def add_prescription(self, fk_appointment_id: int, medicine_name: str, dosage: float, medicine_price: float, prescription_code: str):
        """
        Dodaje nowy rekord do tabeli `prescriptions`.

        Args:
            appointment_id (int): ID wizyty.
            medicine_name (str): Nazwa leku.
            dosage (float): Dawka leku (w mg).
            medicine_price (float): Cena leku.
            prescription_code (str): Kod recepty (4 cyfry).

        Returns:
            int: ID nowo dodanej recepty.

        Example:
            >>> prescriptions.add_prescription(1, "Paracetamol", 500, 15.99, "1234")
        """
        try:
            # Walidacja
            validate_fk_appointment_exists(self.db_controller, fk_appointment_id)
            validate_medicine_name(medicine_name)
            validate_dosage(dosage)
            validate_medicine_price(medicine_price)
            validate_prescription_code(prescription_code)

            self.db_controller.ensure_connection()
            query = """
            INSERT INTO prescriptions (fk_appointment_id, medicine_name, dosage, medicine_price, prescription_code)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(query, (fk_appointment_id, medicine_name, dosage, medicine_price, prescription_code))
            self.db_controller.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania recepty: {e}") from e

    def get_prescriptions(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `prescriptions` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów.
            sort_by (list): Lista sortowania.

        Returns:
            list: Lista rekordów w postaci słowników.

        Example:
            >>> prescriptions.get_prescriptions(filters=[{"column": "dosage", "operator": ">", "value": 100}], sort_by=[("medicine_price", "ASC")])
        """
        try:
            validate_filters_and_sorting(filters, sort_by, ["prescription_id", "appointment_id", "medicine_name", "dosage", "medicine_price", "prescription_code"])
            self.db_controller.ensure_connection()

            if filters:
                for filter_item in filters:
                    validate_operator_and_value(filter_item["operator"], filter_item.get("value"))
            
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM prescriptions WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e

    def update_prescription(self, prescription_id: int, **update_data) -> bool:
        """
        Aktualizuje rekord w tabeli `prescriptions` na podstawie `prescription_id`.

        Args:
            prescription_id (int): ID recepty do aktualizacji.
            **update_data: Słownik zawierający pola do aktualizacji.

        Returns:
            bool: True jeśli aktualizacja zakończyła się sukcesem, False w przeciwnym razie.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy recepta istnieje
            query_check = "SELECT 1 FROM prescriptions WHERE prescription_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (prescription_id,))
            if cursor.fetchone() is None:
                print(f"[update_prescription] Recepta o ID {prescription_id} nie istnieje.")
                return False

            # Tworzenie słownika pól do aktualizacji
            fields = {}
            if "fk_appointment_id" in update_data and update_data["fk_appointment_id"] is not None:
                fields["fk_appointment_id"] = update_data["fk_appointment_id"]
            if "medicine_name" in update_data and update_data["medicine_name"] is not None:
                fields["medicine_name"] = update_data["medicine_name"]
            if "dosage" in update_data and update_data["dosage"] is not None:
                fields["dosage"] = update_data["dosage"]
            if "medicine_price" in update_data and update_data["medicine_price"] is not None:
                fields["medicine_price"] = update_data["medicine_price"]
            if "prescription_code" in update_data and update_data["prescription_code"] is not None:
                fields["prescription_code"] = update_data["prescription_code"]

            if not fields:
                print("[update_prescription] Błąd: Brak danych do aktualizacji.")
                return False

            # Aktualizacja danych w tabeli
            set_clause = ", ".join([f"{column} = ?" for column in fields.keys()])
            values = list(fields.values()) + [prescription_id]

            query = f"UPDATE prescriptions SET {set_clause} WHERE prescription_id = ?"
            self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()

            return True  # Aktualizacja zakończona sukcesem
        except sqlite3.Error as e:
            print(f"[update_prescription] Błąd podczas aktualizacji recepty: {e}")
            return False



    def delete_prescription(self, prescription_id: int) -> bool:
        """
        Usuwa rekord z tabeli `prescriptions` na podstawie prescription_id.

        Args:
            prescription_id (int): ID recepty do usunięcia.

        Returns:
            bool: True jeśli usunięcie zakończyło się sukcesem, False w przeciwnym razie.

        Example:
            >>> prescriptions.delete_prescription(1)
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy recepta istnieje
            query_check = "SELECT 1 FROM prescriptions WHERE prescription_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (prescription_id,))
            if cursor.fetchone() is None:
                print(f"[delete_prescription] Recepta o ID {prescription_id} nie istnieje.")
                return False

            # Usunięcie recepty
            query_delete = "DELETE FROM prescriptions WHERE prescription_id = ?"
            self.db_controller.connection.execute(query_delete, (prescription_id,))
            self.db_controller.connection.commit()

            return True  # Sukces
        except sqlite3.Error as e:
            print(f"[delete_prescription] Błąd podczas usuwania recepty: {e}")
            return False







    def get_prescriptions_by_appointment_ids(self, appointment_ids: list):
        """
        Pobiera wszystkie kolumny dla podanych appointment_id.

        Args:
            appointment_ids (list): Lista appointment_id.

        Returns:
            list: Lista słowników zawierających dane recept.

        Debugowanie:
            - Wypisuje które prescription_id zostały pobrane dla którego appointment_id.
        """
        if not appointment_ids:
            raise ValueError("[model prescriptions] Lista appointment_ids nie może być pusta")

        try:
            self.db_controller.ensure_connection()
            query = f"""
            SELECT * FROM prescriptions
            WHERE appointment_id IN ({','.join(['?' for _ in appointment_ids])})
            """
            cursor = self.db_controller.connection.execute(query, appointment_ids)
            results = [dict(row) for row in cursor.fetchall()]

            # Debugowanie
            # for record in results:
            #     print(f"[### MODEL PERSCRIPTION] Pobranie prescription_id: {record['prescription_id']} dla appointment_id: {record['appointment_id']}")

            return results

        except sqlite3.Error as e:
            raise RuntimeError(f"[model prescriptions] Błąd podczas pobierania recept: {e}") from e


    def get_all_prescriptions(self):
        """
        Pobiera wszystkie rekordy z tabeli `prescriptions` wraz z wszystkimi kolumnami.

        Returns:
            list: Lista słowników reprezentujących rekordy z tabeli `prescriptions`.

        Raises:
            RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            self.db_controller.ensure_connection()
            query = "SELECT * FROM prescriptions"
            cursor = self.db_controller.connection.execute(query)
            result = [dict(row) for row in cursor.fetchall()]
            
            # Debugowanie: Wyświetlenie listy pobranych recept
            # print("[### MODEL PRESCRIPTIONS] Pobrano recepty:")
            # for prescription in result:
            #     print(
            #         f"prescription_id: {prescription['prescription_id']}, "
            #         f"appointment_id: {prescription['appointment_id']}, "
            #         f"medicine_name: {prescription['medicine_name']}, "
            #         f"dosage: {prescription['dosage']}, "
            #         f"medicine_price: {prescription['medicine_price']}, "
            #         f"prescription_code: {prescription['prescription_code']}"
            #     )
            
            return result
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z tabeli `prescriptions`: {e}") from e
