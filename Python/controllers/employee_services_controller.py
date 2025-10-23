# employee_services_controller.py

import sqlite3
from models.employee_services import EmployeeServices
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController



class EmployeeServicesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `employee_services`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler usług pracowników oraz model zarządzający danymi `employee_services`.
        """
        self.db_controller = db_controller
        self.employee_services_model = EmployeeServices(db_controller)
        self.services_controller = ServicesController(db_controller)
        self.employees_controller = EmployeesController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `employee_services` w bazie danych.
        """
        try:
            self.employee_services_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `employee_services`.") from db_error

    def get_all_records(self, filters=None, sort_by=None, ascending=True):
        """
        Pobiera wszystkie rekordy z tabeli `employee_services` z opcjonalnymi filtrami i sortowaniem.

        :param filters: Słownik filtrów, np. {"employee_id": 1}.
        :param sort_by: Kolumna do sortowania.
        :param ascending: Flaga określająca, czy sortowanie jest rosnące (domyślnie True).
        :return: Lista słowników zawierających dane rekordów.
        """
        valid_columns = ["employee_service_id", "employee_id", "service_id", "first_name", "last_name", "service_type"]

        try:
            self.db_controller.ensure_connection()

            query = "SELECT * FROM employee_services"
            params = []

            # Dodawanie filtrów
            if filters:
                invalid_filters = [key for key in filters.keys() if key not in valid_columns]
                if invalid_filters:
                    raise ValueError(f"Nieprawidłowe kolumny w filtrach: {', '.join(invalid_filters)}")

                conditions = [f"{key} = ?" for key in filters.keys()]
                query += " WHERE " + " AND ".join(conditions)
                params.extend(filters.values())

            # Dodawanie sortowania
            if sort_by:
                if sort_by not in valid_columns:
                    raise ValueError(f"Nieprawidłowa kolumna sortowania: {sort_by}")
                query += f" ORDER BY {sort_by} {'ASC' if ascending else 'DESC'}"

            cursor = self.db_controller.connection.execute(query, params)
            return [dict(record) for record in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania rekordów: {e}") from e


    def get_records_with_names(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `employee_services` wraz z imionami, nazwiskami i nazwami specjalizacji.
        """
        # Lista dozwolonych kolumn
        valid_columns = [
            "employee_service_id", "employee_id", "service_id",
            "first_name", "last_name", "service_type"
        ]

        # Walidacja kolumn w filtrach
        if filters:
            for filter_item in filters:
                if filter_item["column"] not in valid_columns:
                    raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}")

        # Budowanie zapytania SQL
        query = """
            SELECT
                es.employee_service_id,
                e.first_name,
                e.last_name,
                s.service_type,
                es.employee_id,
                es.service_id
            FROM
                employee_services AS es
            JOIN
                employees AS e ON es.employee_id = e.employee_id
            JOIN
                specialties AS s ON es.service_id = s.service_id
        """

        where_clause, values = self.db_controller.build_filters(filters)
        if where_clause:
            query += f" WHERE {where_clause}"
        if sort_by:
            query += f" ORDER BY {sort_by}"

        cursor = self.db_controller.connection.execute(query, values)
        return [dict(row) for row in cursor.fetchall()]

    def get_record_by_id(self, employee_service_id: int) -> dict:
        """
        Pobiera rekord z tabeli `employee_services` na podstawie jego ID.

        :param employee_service_id: ID rekordu w tabeli `employee_services`.
        :return: Słownik zawierający dane rekordu.
        :raises KeyError: Jeśli rekord o podanym ID nie istnieje.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            record = self.employee_services_model.get_record_by_id(employee_service_id)
            if not record:
                raise KeyError(f"Nie znaleziono rekordu o ID {employee_service_id}.")
            return record
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania rekordu o ID {employee_service_id}: {db_error}") from db_error



    def add_employee_service_by_ids(self, employee_id: int, service_id: int, is_active: int):
        """
        Dodaje usługę dla pracownika na podstawie ich ID.
        """
        try:
            self.employee_services_model.add_employee_service_by_ids(employee_id, service_id, is_active)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania usługi pracownika.") from db_error

    def add_employee_service_by_names(self, first_name: str, last_name: str, service_type: str):
        """
        Dodaje usługę dla pracownika na podstawie ich imienia, nazwiska i typu usługi.
        """
        try:
            self.employee_services_model.add_employee_service_by_names(first_name, last_name, service_type)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania usługi pracownika po nazwach.") from db_error





    def delete_record_by_id(self, employee_service_id: int):
        """
        Usuwa rekord `employee_services` na podstawie jego ID.
        """
        try:
            self.employee_services_model.delete_record_by_id(employee_service_id)
        except ValueError as exc :
            raise KeyError ("Nie znaleziono rekordu o podanym ID.") from exc
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordu `employee_services`.") from db_error

    def delete_records_by_names(self, first_name: str, last_name: str, service_type: str):
        """
        Usuwa rekordy `employee_services` na podstawie imienia, nazwiska i nazwy usługi.
        """
        try:
            self.employee_services_model.delete_records_by_names(first_name, last_name, service_type)
        except KeyError as not_found_error:
            raise KeyError("Nie znaleziono rekordu dla podanych danych.") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordów `employee_services` po nazwach.") from db_error

    def get_all_employee_services(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_services`.

        :return: Lista słowników zawierających dane z tabeli `employee_services`.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            return self.employee_services_model.get_all_employee_services()
        except RuntimeError as db_error:
            raise RuntimeError(f"Błąd bazy danych w kontrolerze podczas pobierania usług pracowników: {db_error}") from db_error
        
    def get_all_employee_service_ids(self):
        """
        Pobiera wszystkie `employee_service_id` z bazy danych.

        :return: Lista `employee_service_id`.
        :raises RuntimeError: W przypadku błędów bazy danych.
        """
        try:
            return self.employee_services_model.get_all_employee_service_ids()
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania employee_service_id: {db_error}") from db_error
        except KeyError as ke:
            raise KeyError(f"Błąd klucza w danych employee_service_id: {ke}") from ke
        except ValueError as ve:
            raise ValueError(f"Błąd wartości w danych employee_service_id: {ve}") from ve
        

    def update_employee_service(self, employee_service_id, updates):
        """
        Wywołuje metodę modelu do aktualizacji danych w tabeli `employee_services`.

        :param employee_service_id: ID rekordu do aktualizacji.
        :param updates: Słownik zawierający pola do aktualizacji.
        :raises ValueError: Jeśli `employee_service_id` nie istnieje lub brak zmian.
        :raises sqlite3.Error: Jeśli wystąpi błąd bazy danych.
        """
        try:
            # Wywołanie metody modelu
            self.employee_services_model.update_employee_service(
                employee_service_id,
                updates.get("employee_id"),
                updates.get("service_id"),
                updates.get("is_active")
            )
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas aktualizacji przypisania pracownika do usługi: {db_error}") from db_error