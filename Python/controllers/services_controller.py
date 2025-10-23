# services_controller.py

import sqlite3
from models.services import Services
from controllers.database_controller import DatabaseController


class ServicesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `services`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler usług oraz model zarządzający danymi usług.
        """
        self.db_controller = db_controller
        self.services_model = Services(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `services` w bazie danych.
        """
        try:
            self.services_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `services`.") from db_error

    def add_service(self, service_type, duration_minutes, service_price, is_active):
        """
        Dodaje nową usługę do tabeli `services`.
        """
        try:
            self.services_model.create_new_record(service_type, duration_minutes, service_price, is_active)

            return {"success": True}  # Upewnij się, że metoda zwraca ten słownik

        except sqlite3.IntegrityError as e:
            return {"success": False, "message": f"Błąd integralności: {e}"}
        except sqlite3.Error as e:
            return {"success": False, "message": f"Błąd bazy danych: {e}"}

    def get_service(self, service_id: int) -> dict:
        """
        Pobiera usługę na podstawie jej ID.

        :param service_id: ID usługi.
        :return: Słownik zawierający dane usługi lub None, jeśli nie znaleziono.
        """
        query = "SELECT * FROM services WHERE service_id = ?"
        try:
            cursor = self.db_controller.connection.execute(query, (service_id,))
            service = cursor.fetchone()
            if service:
                return dict(service)  # Zwracamy rekord jako słownik
            return None
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania usługi: {db_error}") from db_error



    def get_all_services(self):
        """
        Pobiera wszystkie rekordy z tabeli `services`.
        """
        try:
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")
            return self.services_model.get_records()
        except Exception as e:
            raise RuntimeError(f"Błąd podczas pobierania usług: {e}") from e


    def get_services_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera usługi na podstawie filtrów i sortowania.
        """
        try:
            return self.services_model.get_records(filters=filters, sort_by=sort_by)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania usług.") from db_error

    def update_service(self, service_id, updates):
        """
        Aktualizuje usługę na podstawie ID.
        """
        try:
            self.services_model.update_record(service_id, updates)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji usługi.") from db_error

    def delete_service(self, service_id):
        """
        Usuwa usługę na podstawie ID.
        """
        try:
            self.services_model.delete_record(service_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania usługi.") from db_error


    def get_all_service_types(self):
        """
        Pobiera wszystkie dostępne typy usług z bazy danych.
        """
        try:
            return self.services_model.get_all_service_types()
        except KeyError as ke:
            print(f"[ServicesController] Błąd klucza: {ke}")
            return []
        except ValueError as ve:
            print(f"[ServicesController] Błąd wartości: {ve}")
            return []
        except RuntimeError as re:
            print(f"[ServicesController] Błąd bazy danych: {re}")
            return []
        

    def get_all_service_ids(self):
        """
        Pobiera wszystkie `service_id` z bazy danych.

        :return: Lista ID usług.
        :raises RuntimeError: Jeśli wystąpi błąd podczas pobierania danych.
        """
        try:
            return self.services_model.get_all_service_ids()

        except RuntimeError as runtime_error:
            print(f"[ServicesController] Błąd pobierania service_id: {runtime_error}")
            return []     
        

    def get_service_by_id(self, service_id: int):
        """
        Pobiera dane usługi na podstawie `service_id`.

        :param service_id: ID usługi do pobrania.
        :return: Słownik zawierający dane usługi lub None, jeśli nie znaleziono.
        :raises ValueError: Jeśli `service_id` jest niepoprawne.
        :raises RuntimeError: Jeśli wystąpi błąd podczas pobierania danych.
        """
        try:
            return self.services_model.get_service_by_id(service_id)

        except ValueError as validation_error:
            print(f"[ServicesController] Błąd walidacji: {validation_error}")
            return None
        except RuntimeError as runtime_error:
            print(f"[ServicesController] Błąd pobierania usługi: {runtime_error}")
            return None
        
