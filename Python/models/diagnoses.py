# diagnoses.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.diagnoses_model_validation import (
    validate_description,
    validate_fk_appointment_exists,
    validate_operator_and_value,
    validate_filters_and_sorting,
)


class Diagnoses:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `diagnoses` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Diagnoses z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `diagnoses` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("diagnoses"):
                query = """
                CREATE TABLE IF NOT EXISTS diagnoses (
                    diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    icd11_code TEXT NOT NULL,
                    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def add_diagnosis(self, fk_appointment_id: int, description: str, icd11_code: str) -> bool:
        """
        Dodaje nowy rekord do tabeli `diagnoses`.

        Args:
            fk_appointment_id (int): ID wizyty.
            description (str): Opis diagnozy.
            icd11_code (str): Kod diagnozy według ICD-11.

        Returns:
            bool: True jeśli dodanie się powiodło, False w przeciwnym razie.
        """
        try:
            # Walidacja danych wejściowych
            validate_fk_appointment_exists(self.db_controller, fk_appointment_id)
            validate_description(description)

            # Wstawianie rekordu
            self.db_controller.ensure_connection()
            query = """
            INSERT INTO diagnoses (fk_appointment_id, description, icd11_code)
            VALUES (?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(query, (fk_appointment_id, description, icd11_code))
            self.db_controller.connection.commit()

            # Sprawdzenie, czy rekord został dodany
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[ERROR] Błąd podczas dodawania diagnozy: {e}")
            return False


    def get_diagnoses(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `diagnoses` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów.
            sort_by (list): Lista sortowania.
        """
        try:
            # Walidacja
            validate_filters_and_sorting(filters, sort_by, ["diagnosis_id", "appointment_id", "description", "icd11_code"])

            # Dodatkowa walidacja operatorów i wartości
            if filters:
                for filter_item in filters:
                    validate_operator_and_value(filter_item["operator"], filter_item["value"])

            # Pobieranie rekordów
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM diagnoses WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e

    def update_diagnosis(
        self,
        diagnosis_id: int,
        appointment_id: int = None,
        description: str = None,
        icd11_code: str = None,
    ):
        """
        Aktualizuje rekord w tabeli `diagnoses` na podstawie diagnosis_id.

        Args:
            diagnosis_id (int): ID diagnozy do aktualizacji.
            appointment_id (int, opcjonalnie): Nowy ID wizyty.
            description (str, opcjonalnie): Nowy opis diagnozy.
            icd11_code (str, opcjonalnie): Nowy kod diagnozy ICD-11.

        Raises:
            RuntimeError: Jeśli rekord z podanym ID nie istnieje lub wystąpi błąd aktualizacji.
            ValueError: Jeśli nie podano żadnych danych do aktualizacji.
        """
        try:
            # Sprawdzenie, czy rekord istnieje
            self.db_controller.ensure_connection()
            query_check = "SELECT 1 FROM diagnoses WHERE diagnosis_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (diagnosis_id,))
            if cursor.fetchone() is None:
                raise RuntimeError("Rekord z podanym ID nie istnieje.")

            # Tworzenie słownika tylko z podanymi argumentami
            fields = {}
            if appointment_id is not None:
                fields["fk_appointment_id"] = appointment_id  # ✅ POPRAWIONE
            if description is not None:
                fields["description"] = description
            if icd11_code is not None:
                fields["icd11_code"] = icd11_code

            # Sprawdzenie, czy podano dane do aktualizacji
            if not fields:
                raise ValueError("Nie podano danych do aktualizacji.")

            # Budowanie zapytania aktualizującego
            set_clause = ", ".join([f"{column} = ?" for column in fields.keys()])
            values = list(fields.values()) + [diagnosis_id]

            query = f"UPDATE diagnoses SET {set_clause} WHERE diagnosis_id = ?"
            self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()
            return True  # ✅ Zwracamy True w przypadku sukcesu
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji diagnozy: {e}") from e




    def delete_diagnosis(self, diagnosis_id: int) -> bool:
        """
        Usuwa rekord z tabeli `diagnoses` na podstawie diagnosis_id.

        Args:
            diagnosis_id (int): ID diagnozy do usunięcia.

        Returns:
            bool: True jeśli usunięcie się powiodło, False jeśli nie.
        """
        try:
            self.db_controller.ensure_connection()

            # Usunięcie rekordu
            query_delete = "DELETE FROM diagnoses WHERE diagnosis_id = ?"
            self.db_controller.connection.execute(query_delete, (diagnosis_id,))
            self.db_controller.connection.commit()
            
            print(f"[delete_diagnosis] Diagnoza o ID {diagnosis_id} została usunięta.")
            return True  # Zwracamy True jeśli usunięcie było udane

        except sqlite3.Error as e:
            print(f"[delete_diagnosis] Błąd podczas usuwania diagnozy: {e}")
            return False  # Zwracamy False w przypadku błędu




    def get_diagnoses_by_appointment_ids(self, appointment_ids):
        """
        Args:
            appointment_ids (list): Lista appointment_id do wyszukania.

        Returns:
            list: Lista zawierająca wszystkie wiersze z tabeli diagnoses.
        """
        if not appointment_ids:
            return []

        try:
            self.db_controller.ensure_connection()
            query = f"""
            SELECT *
            FROM diagnoses
            WHERE appointment_id IN ({','.join(['?'] * len(appointment_ids))})
            """
            cursor = self.db_controller.connection.execute(query, appointment_ids)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                diagnosis_data = dict(row)  # Przekształcamy sqlite3.Row na słownik
                result.append(diagnosis_data)

            # Debugowanie: Wyświetlenie pełnej listy pobranych danych
            # print("[###MODEL DIAGNOSES] Lista pobranych diagnoz:")
            # for diagnosis in result:
            #     print(
            #         f"appointment_id: {diagnosis['appointment_id']}, "
            #         f"diagnosis_id: {diagnosis['diagnosis_id']}, "
            #         f"description: {diagnosis['description']}, "
            #         f"icd11_code: {diagnosis['icd11_code']}"
            #     )

            return result
        except sqlite3.Error as e:
            print(f"[model diagnoses] Błąd SQLite: {e}")
            return []


    def get_all_diagnoses(self):
        """
        Pobiera wszystkie rekordy z tabeli `diagnoses` wraz z wszystkimi kolumnami.

        Returns:
            list: Lista słowników reprezentujących rekordy z tabeli `diagnoses`.

        Raises:
            RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            self.db_controller.ensure_connection()
            query = "SELECT * FROM diagnoses"
            cursor = self.db_controller.connection.execute(query)
            result = [dict(row) for row in cursor.fetchall()]
            
            # Debugowanie: Wyświetlenie listy pobranych diagnoz w formie listy wierszy
            # print("[### MODEL DIAGNOSES] Pobrano diagnozy:")
            # for diagnosis in result:
            #     print(
            #         f"diagnosis_id: {diagnosis['diagnosis_id']}, "
            #         f"fk_appointment_id: {diagnosis['fk_appointment_id']}, "
            #         f"description: {diagnosis['description']}, "
            #         f"icd11_code: {diagnosis['icd11_code']}"
            #     )
            
            return result
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z tabeli `diagnoses`: {e}") from e


