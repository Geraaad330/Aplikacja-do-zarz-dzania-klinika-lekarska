# employee_services.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from validators.employee_services_model_validation import (
    validate_add_employee_specialty_by_names,
    validate_unique_employee_service_by_names,
    validate_delete_record_by_id,
    validate_delete_records_by_names
)


def get_valid_columns(db_controller, table_name: str) -> list:
    """
    Pobiera listę kolumn dla podanej tabeli z bazy danych.
    :param db_controller: Obiekt kontrolera bazy danych.
    :param table_name: Nazwa tabeli.
    :return: Lista nazw kolumn.
    """
    db_controller.ensure_connection()
    query = f"PRAGMA table_info({table_name})"
    cursor = db_controller.connection.execute(query)
    return [row["name"] for row in cursor.fetchall()]

class EmployeeServices:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `employee_services` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy EmployeeServices z kontrolerem bazy danych.
        """
        self.db_controller = db_controller
        self.employees_controller = EmployeesController(db_controller)  # Przypisanie kontrolera pracowników
        self.services_controller = ServicesController(db_controller)  # Przypisanie kontrolera usług

    def create_table(self):
        """
        Tworzy tabelę `employee_services` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("employee_services"):
                query = """
                CREATE TABLE IF NOT EXISTS employee_services (
                    employee_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    service_id INTEGER NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
                    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE,
                    UNIQUE (employee_id, service_id)
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    # +-+-+-+- metoy dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    # Create
    def add_employee_service_by_ids(self, employee_id: int, service_id: int, is_active=True):
        """
        Dodaje nowy rekord na podstawie `employee_id` i `service_id`.
        """
        try:
            self.db_controller.ensure_connection()

            query = "INSERT INTO employee_services (employee_id, service_id, is_active) VALUES (?, ?, ?)"
            self.db_controller.connection.execute(query, (employee_id, service_id, is_active))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania rekordu: {e}") from e



    def add_employee_service_by_names(self, first_name: str, last_name: str, service_type: str):
        """
        Dodaje nowy rekord na podstawie imienia, nazwiska pracownika oraz nazwy usługi.
        """
        # Walidacja danych
        validate_add_employee_specialty_by_names(
            self.employees_controller, self.services_controller, first_name, last_name, service_type
        )
        employee_id = self.get_employee_id(first_name, last_name)
        service_id = self.get_service_id(service_type)

        # Walidacja unikalności rekordu
        validate_unique_employee_service_by_names(
            self.db_controller, self.employees_controller, self.services_controller,
            first_name, last_name, service_type
        )

        # Dodanie rekordu do bazy danych
        query = "INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)"
        self.db_controller.connection.execute(query, (employee_id, service_id))
        self.db_controller.connection.commit()


        
    # +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    def get_employee_id(self, first_name: str, last_name: str) -> int:
        """
        Pobiera ID pracownika na podstawie imienia i nazwiska za pomocą kontrolera `EmployeesController`.
        """
        employees = self.employees_controller.filter_employees(first_name=first_name, last_name=last_name)
        if not employees:
            raise KeyError(f"Pracownik {first_name} {last_name} nie istnieje.")
        return employees[0]["employee_id"]

    def get_service_id(self, service_name: str) -> int:
        """
        Pobiera ID usługi na podstawie nazwy za pomocą kontrolera `ServicesController`.
        """
        services = self.services_controller.get_services_with_filters(
            filters=[{"column": "service_type", "operator": "=", "value": service_name}]
        )
        if not services:
            raise ValueError(f"Usługa '{service_name}' nie istnieje.")
        return services[0]["service_id"]


    def get_record_by_id(self, employee_service_id: int) -> dict:
        query = "SELECT * FROM employee_services WHERE employee_service_id = ?"
        cursor = self.db_controller.connection.execute(query, (employee_service_id,))
        record = cursor.fetchone()
        if not record:
            raise KeyError("Nie znaleziono rekordu o podanym ID.")  # Zmieniono, aby regex w testach pasował.
        return dict(record)

    # Read
    def get_all_records(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_services`.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            SELECT es.employee_service_id, es.employee_id, es.service_id, 
                e.first_name || ' ' || e.last_name AS employee_name, 
                s.service_type 
            FROM employee_services es
            LEFT JOIN employees e ON es.employee_id = e.employee_id
            LEFT JOIN services s ON es.service_id = s.service_id
            """
            cursor = self.db_controller.connection.execute(query)
            records = [dict(row) for row in cursor.fetchall()]
            
            # Weryfikacja brakujących zależności
            for record in records:
                if not record["employee_name"] or not record["service_type"]:
                    raise ValueError("Brakujące zależności dla rekordu.")
            
            return records
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e


    def get_record_with_names(self, first_name: str, last_name: str, service_type: str):
        """
        Pobiera rekord na podstawie imienia, nazwiska i typu usługi.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            SELECT
                es.employee_service_id,
                e.first_name || ' ' || e.last_name AS employee_name,
                s.service_type
            FROM employee_services es
            JOIN employees e ON es.employee_id = e.employee_id
            JOIN services s ON es.service_id = s.service_id
            WHERE e.first_name = ? AND e.last_name = ? AND s.service_type = ?
            """
            cursor = self.db_controller.connection.execute(query, (first_name, last_name, service_type))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z nazwami: {e}") from e


    def get_records_with_filters(self, filters=None):
        """
        Pobiera rekordy z tabeli `employee_services` z opcjonalnymi filtrami.

        :param filters: Lista słowników filtrów, np. [{"column": "employee_id", "operator": "=", "value": 1}].
        :return: Lista rekordów pasujących do podanych filtrów.
        """
        query = "SELECT * FROM employee_services"
        params = []

        if filters:
            conditions = []
            for f in filters:
                if f["column"] not in ["employee_id", "service_id"]:
                    raise ValueError(f"Nieprawidłowa kolumna w filtrze: {f['column']}")
                conditions.append(f"{f['column']} {f['operator']} ?")
                params.append(f["value"])

            query += " WHERE " + " AND ".join(conditions)

        cursor = self.db_controller.connection.execute(query, params)
        return cursor.fetchall()


    # +-+-+-+- metody aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


    def update_employee_service(self, employee_service_id, employee_id=None, service_id=None, is_active=None):
        """
        Aktualizuje rekord w tabeli `employee_services`.

        :param employee_service_id: ID rekordu w `employee_services`, który ma być zaktualizowany.
        :param employee_id: (Opcjonalnie) Nowy `employee_id`, jeśli podano.
        :param service_id: (Opcjonalnie) Nowy `service_id`, jeśli podano.
        :param is_active: (Opcjonalnie) Nowy status `is_active`, jeśli podano.
        :raises ValueError: Jeśli `employee_service_id` nie istnieje lub brak danych do aktualizacji.
        :raises sqlite3.Error: Jeśli wystąpi błąd bazy danych.
        """

        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy rekord istnieje
            query = "SELECT * FROM employee_services WHERE employee_service_id = ?"
            cursor = self.db_controller.connection.execute(query, (employee_service_id,))
            existing_record = cursor.fetchone()
            if not existing_record:
                raise ValueError(f"Rekord o ID ({employee_service_id}) nie istnieje w tabeli `employee_services`.")

            # Tworzenie listy aktualizacji
            update_fields = {}
            if employee_id is not None:
                update_fields["employee_id"] = employee_id
            if service_id is not None:
                update_fields["service_id"] = service_id
            if is_active is not None:
                update_fields["is_active"] = is_active

            # Jeśli nie ma zmian, zwróć błąd
            if not update_fields:
                raise ValueError("Brak zmian do aktualizacji.")

            # Budowanie zapytania SQL
            set_clause = ", ".join(f"{key} = ?" for key in update_fields.keys())
            query = f"UPDATE employee_services SET {set_clause} WHERE employee_service_id = ?"
            params = list(update_fields.values()) + [employee_service_id]

            # Wykonanie aktualizacji
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            raise ValueError(f"Błąd integralności danych: {e}") from e
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Ogólny błąd bazy danych: {e}") from e
        
    # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    def delete_record_by_id(self, employee_service_id: int):
        """
        Usuwa rekord z tabeli `employee_services` na podstawie `employee_service_id`.
        """
        try:
            self.db_controller.ensure_connection()
            validate_delete_record_by_id(self.db_controller, employee_service_id)
            query = "DELETE FROM employee_services WHERE employee_service_id = ?"
            self.db_controller.connection.execute(query, (employee_service_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e

    def delete_records_by_names(self, first_name: str, last_name: str, service_type: str):
        """
        Usuwa rekordy na podstawie imienia, nazwiska i typu usługi.
        """
        try:
            validate_delete_records_by_names(self.employees_controller, self.services_controller, first_name, last_name, service_type)
            employee_id = self.get_employee_id(first_name, last_name)
            service_id = self.get_service_id(service_type)

            query = """
            DELETE FROM employee_services
            WHERE employee_id = ? AND service_id = ?
            """
            self.db_controller.connection.execute(query, (employee_id, service_id))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordów: {e}") from e





    def get_all_employee_services(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_services`.

        :return: Lista słowników zawierających dane z tabeli `employee_services`.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        query = "SELECT * FROM employee_services ORDER BY employee_id ASC"

        try:
            cursor = self.db_controller.connection.execute(query)
            records = [dict(row) for row in cursor.fetchall()]
            return records
        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych podczas pobierania usług pracowników: {op_err}") from op_err
        except sqlite3.Error as db_err:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania usług pracowników: {db_err}") from db_err
        

    def get_all_employee_service_ids(self):
        """
        Pobiera wszystkie `employee_service_id` z tabeli `employee_services`.
        
        :return: Lista `employee_service_id`.
        :raises RuntimeError: W przypadku błędów bazy danych.
        """
        query = "SELECT employee_service_id FROM employee_services ORDER BY employee_service_id ASC"
        try:
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query)
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania employee_service_id: {db_error}") from db_error
        except KeyError as ke:
            raise KeyError(f"Błąd klucza podczas pobierania employee_service_id: {ke}") from ke
        except ValueError as ve:
            raise ValueError(f"Błąd wartości w danych employee_service_id: {ve}") from ve