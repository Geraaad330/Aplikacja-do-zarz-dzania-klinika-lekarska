# services.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.services_model_validation import (
    validate_service_type,
    validate_duration_minutes,
    validate_service_price,
    validate_operator_and_value,
    validate_record_existence,
)

class Services:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `services` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Services z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `services` w bazie danych, jeśli jeszcze nie istnieje.
        
        Przykład:
        services.create_table()
        
        Wynik:
        Utworzona tabela `services` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("services"):
                query = r"""
                CREATE TABLE IF NOT EXISTS services (
                    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(service_type) > 0),
                    duration_minutes INTEGER NOT NULL CHECK (duration_minutes BETWEEN 1 AND 300),
                    service_price INTEGER NOT NULL CHECK (service_price BETWEEN 1 AND 500)
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def create_new_record(self, service_type: str, duration_minutes: int, service_price: int, is_active=True):
        """
        Tworzy nowy rekord w tabeli `services`.
        
        Przykład:
        services.create_new_record("Usługa A", 60, 100)
        
        Wynik:
        Nowy rekord w tabeli `services`.
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")

            # Walidacja danych wejściowych
            validate_service_type(service_type)
            validate_duration_minutes(duration_minutes)
            validate_service_price(service_price)

            # Tworzenie nowego rekordu
            query = """
            INSERT INTO services (service_type, duration_minutes, service_price, is_active)
            VALUES (?, ?, ?, ?)
            """
            self.db_controller.connection.execute(query, (service_type, duration_minutes, service_price, is_active))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            raise ValueError(f"Błąd integralności podczas dodawania rekordu: {e}") from e
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Błąd operacyjny podczas dodawania rekordu: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Ogólny błąd bazy danych podczas dodawania rekordu: {e}") from e

    def get_records(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `services`.
        """
        try:
                # Sprawdzanie połączenia z bazą danych
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")
            # Walidacja filtrów i sortowania
            if filters:
                for filter_item in filters:
                    operator = filter_item["operator"]
                    value = filter_item.get("value")
                    validate_operator_and_value(operator, value)
            
            # Budowanie zapytania przy użyciu build_filters z DatabaseController
            query, values = self.db_controller.build_filters(filters, sort_by)
            cursor = self.db_controller.connection.execute(f"SELECT * FROM services WHERE {query}", values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e


    def update_record(self, service_id: int, updates: dict):
        """
        Aktualizuje rekord na podstawie ID.
        
        Przykład:
        updates = {"service_type": "Nowa usługa", "service_price": 120}
        services.update_record(1, updates)
        
        Wynik:
        Zaktualizowany rekord w tabeli `services`.
        """
        if not updates:
            raise ValueError("Nie podano danych do aktualizacji.")
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("services"):
                raise RuntimeError("Tabela 'services' nie istnieje w bazie danych.")

            set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
            query = f"UPDATE services SET {set_clause} WHERE service_id = ?"
            params = list(updates.values()) + [service_id]
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizowania rekordu: {e}") from e

    def delete_record(self, service_id: int):
        """
        Usuwa rekord na podstawie ID.
        
        Przykład:
        services.delete_record(1)
        
        Wynik:
        Usunięty rekord z tabeli `services`.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("services"):
                raise RuntimeError("Tabela 'services' nie istnieje w bazie danych.")
            
            validate_record_existence(self.db_controller, "services", "service_id", service_id)


            query = "DELETE FROM services WHERE service_id = ?"
            self.db_controller.connection.execute(query, (service_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e



    def get_all_service_types(self):
        """
        Pobiera wszystkie unikalne typy usług (service_type) z bazy danych.
        Zwraca listę stringów.
        """
        query = "SELECT DISTINCT service_type FROM services ORDER BY service_type ASC"
        try:
            cursor = self.db_controller.connection.execute(query)  # Poprawiona linia
            service_types = [row[0] for row in cursor.fetchall()]
            return service_types
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania typów usług: {db_error}") from db_error


    def get_all_service_ids(self):
        """
        Pobiera wszystkie `service_id` z tabeli `services`.

        :return: Lista ID usług.
        :raises RuntimeError: Jeśli wystąpi błąd podczas wykonywania zapytania.
        """
        query = "SELECT service_id FROM services ORDER BY service_id ASC"

        try:
            # Sprawdzanie połączenia z bazą danych
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")

            cursor = self.db_controller.connection.execute(query)
            service_ids = [row[0] for row in cursor.fetchall()]
            return service_ids

        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {op_err}") from op_err
        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania service_id: {db_err}") from db_err

    def get_service_by_id(self, service_id: int):
        """
        Pobiera wszystkie kolumny dla danego `service_id` z tabeli `services`.

        :param service_id: ID usługi do pobrania.
        :return: Słownik zawierający dane usługi lub None, jeśli nie znaleziono.
        :raises ValueError: Jeśli `service_id` nie jest poprawną liczbą całkowitą.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        query = "SELECT * FROM services WHERE service_id = ?"

        try:
            # Sprawdzanie połączenia z bazą danych
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")

            if not isinstance(service_id, int) or service_id <= 0:
                raise ValueError("ID usługi musi być liczbą całkowitą większą od zera.")

            cursor = self.db_controller.connection.execute(query, (service_id,))
            service_data = cursor.fetchone()

            if service_data:
                # Konwersja danych na słownik
                column_names = [desc[0] for desc in cursor.description]
                return dict(zip(column_names, service_data))

            return None  # Zwracamy None, jeśli usługa nie została znaleziona.

        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {op_err}") from op_err
        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania usługi: {db_err}") from db_err
        