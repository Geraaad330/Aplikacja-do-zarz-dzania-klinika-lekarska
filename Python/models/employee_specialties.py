# employee_specialties.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.specialties_controller import SpecialtiesController
from validators.employee_specialties_model_validation import (
    validate_employee_id,
    validate_specialty_id,
    validate_filters_and_sorting,
    validate_employee_name,
    validate_specialty_name
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

class EmployeeSpecialties:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `employee_specialties` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy `EmployeeSpecialties` z kontrolerem bazy danych.
        """
        self.db_controller = db_controller
        self.employees_controller = EmployeesController(db_controller)
        self.specialties_controller = SpecialtiesController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `employee_specialties` w bazie danych, jeśli jeszcze nie istnieje.

        Przykład:
        employee_specialties.create_table()

        Wynik:
        Utworzona tabela `employee_specialties` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("employee_specialties"):
                query = """
                CREATE TABLE IF NOT EXISTS employee_specialties (
                    employee_specialty_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    specialty_id INTEGER NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
                    FOREIGN KEY (specialty_id) REFERENCES specialties(specialty_id) ON DELETE CASCADE,
                    UNIQUE (employee_id, specialty_id)
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e



    def get_specialties_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie ID specjalizacji powiązane z danym employee_id.

        Args:
            employee_id (int): ID pracownika.

        Returns:
            list[int]: Lista ID specjalizacji powiązanych z pracownikiem, jeśli istnieją, w przeciwnym razie pusta lista.
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            self.db_controller.ensure_connection()

            # Zapytanie SQL
            query = """
            SELECT specialty_id
            FROM employee_specialties
            WHERE employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (employee_id,))
            results = cursor.fetchall()

            if results:
                specialties = [row[0] for row in results]  # Pobiera wszystkie specialty_id
                # print(f"model: employee_specialties: Pobrano ID specjalizacji dla employee_id {employee_id}: {specialties}")  # Debug
                return specialties
            else:
                print(f"Nie znaleziono specjalizacji dla employee_id {employee_id}")  # Debug
                return []

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania specjalizacji dla employee_id {employee_id}: {e}") from e







    # +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+

    def get_records(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `employee_specialties`.

        Może pobierać wszystkie rekordy, jeśli nie podasz filtrów.
        Możesz również ustawić sortowanie wyników.

        Przykład:
            employee_specialties.get_records(
                filters=[{"column": "employee_id", "operator": "=", "value": 1}],
                sort_by=[{"column": "specialty_id", "order": "ASC"}]
            )

        Wynik:
            Lista rekordów zgodnych z zapytaniem.
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy tabela istnieje
            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela `employee_specialties` nie istnieje w bazie danych.")

            # Pobranie kolumn dla tabeli (dynamicznie)
            valid_columns = get_valid_columns(self.db_controller, "employee_specialties")

            # Walidacja filtrów i sortowania
            if filters:
                for filter_item in filters:
                    if filter_item["column"] not in valid_columns:
                        raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}")




            if sort_by:
                for sort_item in sort_by:
                    if sort_item["column"] not in valid_columns:
                        raise ValueError(f"Nieprawidłowa kolumna w sortowaniu: {sort_item['column']}")

            # Budowa zapytania SQL
            query, values = self.db_controller.build_filters(filters, sort_by)

            # Wykonanie zapytania SQL
            cursor = self.db_controller.connection.execute(
                f"SELECT * FROM employee_specialties WHERE {query}", values
            )
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e
        except ValueError as ve:
            raise ValueError(f"Błąd walidacji: {ve}") from ve



    def get_records_with_names(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `employee_specialties` z nazwami pracowników i specjalizacji,
        z możliwością stosowania filtrów i sortowania.

        :param filters: Lista filtrów do zastosowania w zapytaniu SQL.
        :param sort_by: Lista kryteriów sortowania.
        
        Przykład:
        employee_specialties.get_records_with_names(
            filters=[{"column": "employee_name", "operator": "LIKE", "value": "Jan%"}],
            sort_by=[("specialty_name", "ASC")]
        )

        Wynik:
        Lista rekordów z polami `employee_name` i `specialty_name`.
        """
        try:
            self.db_controller.ensure_connection()

            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela 'employee_specialties' nie istnieje w bazie danych.")

            # SPECJALNE NAZWY KOLUMN DLA "PRZETŁUMACZONYCH" specialty_id, employee_id, employee_specialty_id
            valid_columns = ["employee_name", "specialty_name", "employee_specialty_id"]

            # Buduj filtry i sortowanie
            validate_filters_and_sorting(filters, sort_by, valid_columns)
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)

            # Zapytanie SQL z dynamicznymi filtrami
            query = f"""
            SELECT 
                es.employee_specialty_id,
                e.first_name || ' ' || e.last_name AS employee_name,
                s.specialty_name
            FROM 
                employee_specialties es
            JOIN 
                employees e ON es.employee_id = e.employee_id
            JOIN 
                specialties s ON es.specialty_id = s.specialty_id
            WHERE {query_conditions}
            """

            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z nazwami: {e}") from e


    # pobiera tylko ID, a nie przetłumaczone nazwy na podstawie imienia i nazwiska.
    def get_employee_id(self, first_name: str, last_name: str) -> int:
        """
        Pobiera ID pracownika na podstawie imienia i nazwiska za pomocą kontrolera `EmployeesController`.
        """
        employees = self.employees_controller.filter_employees(first_name=first_name, last_name=last_name)
        if not employees:
            raise KeyError(f"Pracownik {first_name} {last_name} nie istnieje.")
        return employees[0]["employee_id"]

    # pobiera tylko ID, a nie przetłumaczone nazwy na podstawie imienia i nazwiska.
    def get_specialty_id(self, specialty_name: str) -> int:
        """
        Pobiera ID specjalizacji na podstawie nazwy za pomocą kontrolera `SpecialtiesController`.
        """
        specialties = self.specialties_controller.get_specialties_with_filters(
            filters=[{"column": "specialty_name", "operator": "=", "value": specialty_name}]
        )
        if not specialties:
            raise ValueError(f"Specjalizacja '{specialty_name}' nie istnieje.")
        return specialties[0]["specialty_id"]


    # +-+-+-+- metoy dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


    def add_employee_specialty(self, employee_id: int, specialty_id: int, is_active=True):
        """
        Dodaje nowy rekord do tabeli `employee_specialties` na podstawie `employee_id` i `specialty_id`.

        Przykład:
        employee_specialties.add_employee_specialty(1, 2)

        Wynik:
        Nowy rekord w tabeli `employee_specialties`.
        """
        try:
            # Dodanie rekordu do bazy danych
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela 'employee_specialties' nie istnieje w bazie danych.")
            query = """
            INSERT INTO employee_specialties (employee_id, specialty_id, is_active) 
            VALUES (?, ?, ?)
            """
            self.db_controller.connection.execute(query, (employee_id, specialty_id, is_active))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania rekordu: {e}") from e


    # +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

    def update_record_by_id(self, employee_specialty_id: int, new_employee_id: int = None, new_specialty_id: int = None):
        """
        Aktualizuje rekord w tabeli `employee_specialties` na podstawie `employee_specialty_id`.

        :param employee_specialty_id: Unikalny identyfikator rekordu.
        :param new_employee_id: Nowe ID pracownika (opcjonalne).
        :param new_specialty_id: Nowe ID specjalizacji (opcjonalne).

        Przykład:
        employee_specialties.update_record_by_id(
            employee_specialty_id=1,
            new_employee_id=2,
            new_specialty_id=3
        )
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy tabela istnieje
            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela 'employee_specialties' nie istnieje w bazie danych.")

            # Przygotowanie nowych wartości
            updates = []
            values = []

            if new_employee_id is not None:
                validate_employee_id(self.employees_controller, new_employee_id)
                updates.append("employee_id = ?")
                values.append(new_employee_id)

            if new_specialty_id is not None:
                validate_specialty_id(self.specialties_controller, new_specialty_id)
                updates.append("specialty_id = ?")
                values.append(new_specialty_id)

            # Jeśli brak nowych wartości, zgłoś błąd
            if not updates:
                raise ValueError("Nie podano nowych wartości do aktualizacji.")

            # Dodanie identyfikatora do warunku WHERE
            values.append(employee_specialty_id)

            # Budowanie zapytania SQL
            query = f"""
            UPDATE employee_specialties
            SET {", ".join(updates)}
            WHERE employee_specialty_id = ?
            """
            cursor = self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()

            # Sprawdzenie, czy rekord został zaktualizowany
            if cursor.rowcount == 0:
                raise KeyError(f"Rekord o ID {employee_specialty_id} nie istnieje.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rekordu: {e}") from e


    def update_record_by_name_using_names(
        self, first_name: str, last_name: str, specialty_name: str,
        new_first_name: str = None, new_last_name: str = None, new_specialty_name: str = None
    ):
        """
        Aktualizuje rekord w tabeli `employee_specialties` na podstawie `first_name`, `last_name` i `specialty_name`.

        :param first_name: Obecne imię pracownika.
        :param last_name: Obecne nazwisko pracownika.
        :param specialty_name: Obecna nazwa specjalizacji.
        :param new_first_name: Nowe imię pracownika (opcjonalne).
        :param new_last_name: Nowe nazwisko pracownika (opcjonalne).
        :param new_specialty_name: Nowa nazwa specjalizacji (opcjonalne).
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy tabela istnieje
            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela `employee_specialties` nie istnieje w bazie danych.")

            # Pobranie ID obecnych wartości
            current_employee_id = self.get_employee_id(first_name, last_name)
            current_specialty_id = self.get_specialty_id(specialty_name)

            # Przygotowanie nowych wartości
            updates = []
            values = []

            # Walidacja nowych wartości i przygotowanie zapytania
            if new_first_name or new_last_name:
                validate_employee_name(new_first_name, new_last_name)
                new_employee_id = self.get_employee_id(new_first_name, new_last_name)
                updates.append("employee_id = ?")
                values.append(new_employee_id)

            if new_specialty_name:
                validate_specialty_name(new_specialty_name)
                new_specialty_id = self.get_specialty_id(new_specialty_name)
                updates.append("specialty_id = ?")
                values.append(new_specialty_id)


            # Jeśli brak nowych wartości, zgłoś błąd
            if not updates:
                raise ValueError("Nie podano nowych wartości do aktualizacji.")

            # Dodanie warunku WHERE
            values.extend([current_employee_id, current_specialty_id])

            # Budowanie zapytania SQL
            query = f"""
            UPDATE employee_specialties
            SET {', '.join(updates)}
            WHERE employee_id = ? AND specialty_id = ?
            """
            cursor = self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()

            # Sprawdzenie, czy rekord został zaktualizowany
            if cursor.rowcount == 0:
                raise KeyError(f"Rekord dla {first_name} {last_name} z {specialty_name} nie istnieje.")

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rekordu: {e}") from e





    def update_record_by_name_using_id(self, first_name: str, last_name: str, specialty_name: str, employee_id: int = None, specialty_id: int = None):
        """
        Aktualizuje rekord w tabeli `employee_specialties` na podstawie `first_name`, `last_name` i `specialty_name`.

        :param first_name: Imię pracownika.
        :param last_name: Nazwisko pracownika.
        :param specialty_name: Nazwa specjalizacji.
        :param employee_id: Nowa wartość dla `employee_id` (opcjonalne).
        :param specialty_id: Nowa wartość dla `specialty_id` (opcjonalne).

        Przykład:
        employee_specialties.update_record_by_name("Jan", "Kowalski", "Kardiologia", employee_id=2)
        """
        try:
            self.db_controller.ensure_connection()

            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela 'employee_specialties' nie istnieje w bazie danych.")

            if not employee_id and not specialty_id:
                raise ValueError("Nie podano wartości do aktualizacji.")
            
            # Walidacja nazw
            validate_employee_name(first_name, last_name)
            validate_specialty_name(specialty_name)

            # Pobranie ID pracownika i specjalizacji na podsatwie imienia, nazwiska, nazwy specjalności
            # zapisuje je jako id oraz na tej podstawie aktualizuje rekord
            current_employee_id = self.get_employee_id(first_name, last_name)
            current_specialty_id = self.get_specialty_id(specialty_name)

            # Budowanie zapytania SQL
            updates = []
            values = []
            if employee_id is not None:
                updates.append("employee_id = ?")
                values.append(employee_id)
            if specialty_id is not None:
                updates.append("specialty_id = ?")
                values.append(specialty_id)

            values.extend([current_employee_id, current_specialty_id])
            query = f"""
            UPDATE employee_specialties
            SET {", ".join(updates)}
            WHERE employee_id = ? AND specialty_id = ?
            """
            cursor = self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()

            if cursor.rowcount == 0:
                raise KeyError(f"Rekord dla {first_name} {last_name} z '{specialty_name}' nie istnieje.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rekordu: {e}") from e
        

    # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


    def delete_employee_specialty(self, employee_specialty_id: int):
        """
        Usuwa rekord z tabeli `employee_specialties` na podstawie `employee_specialty_id`.

        :param employee_specialty_id: ID rekordu w tabeli `employee_specialties`.
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy tabela istnieje
            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela `employee_specialties` nie istnieje w bazie danych.")

            # Sprawdzenie istnienia rekordu
            record = self.get_records(filters=[{"column": "employee_specialty_id", "operator": "=", "value": employee_specialty_id}])
            if not record:
                raise KeyError(f"Rekord o ID {employee_specialty_id} nie istnieje.")

            # Usunięcie rekordu
            query = "DELETE FROM employee_specialties WHERE employee_specialty_id = ?"
            self.db_controller.connection.execute(query, (employee_specialty_id,))
            self.db_controller.connection.commit()

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e



    def delete_record_by_name(self, first_name: str, last_name: str, specialty_name: str):
        """
        Usuwa rekord z tabeli `employee_specialties` na podstawie `first_name`, `last_name` i `specialty_name`.

        :param first_name: Imię pracownika.
        :param last_name: Nazwisko pracownika.
        :param specialty_name: Nazwa specjalizacji.
        """
        try:
            # Sprawdzenie połączenia z bazą danych
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy tabela istnieje
            if not self.db_controller.table_exists("employee_specialties"):
                raise RuntimeError("Tabela `employee_specialties` nie istnieje w bazie danych.")

            # Pobranie ID pracownika i specjalizacji na podstawie podanych wartości
            employee_id = self.get_employee_id(first_name, last_name)
            specialty_id = self.get_specialty_id(specialty_name)

            # Usunięcie rekordu
            query = """
            DELETE FROM employee_specialties
            WHERE employee_id = ? AND specialty_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (employee_id, specialty_id))
            self.db_controller.connection.commit()

            # Sprawdzenie, czy rekord został usunięty
            if cursor.rowcount == 0:
                raise KeyError(f"Rekord dla {first_name} {last_name} z {specialty_name} nie istnieje.")

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e


    def get_all_employee_specialties(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_specialties`.
        
        :return: Lista słowników zawierających rekordy.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        query = "SELECT * FROM employee_specialties ORDER BY employee_specialty_id ASC"
        try:
            cursor = self.db_controller.connection.execute(query)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania rekordów z employee_specialties: {db_error}") from db_error

    def get_all_employee_specialty_ids(self):
        """
        Pobiera wszystkie identyfikatory `employee_specialty_id` z tabeli `employee_specialties`.

        :return: Lista identyfikatorów `employee_specialty_id`.
        :raises RuntimeError: Błąd bazy danych podczas pobierania danych.
        """
        query = "SELECT employee_specialty_id FROM employee_specialties"

        try:
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query)
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {op_err}") from op_err
        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych: {db_err}") from db_err
        
    def get_employee_specialty_by_id(self, employee_specialty_id):
        """
        Pobiera wszystkie dane z tabeli `employee_specialties` na podstawie podanego `employee_specialty_id`.

        :param employee_specialty_id: ID przypisania specjalizacji do pracownika.
        :return: Słownik zawierający dane przypisania specjalizacji lub None, jeśli nie znaleziono.
        :raises ValueError: Jeśli podane ID nie jest liczbą całkowitą.
        :raises RuntimeError: Jeśli wystąpił błąd bazy danych.
        """
        query = """
            SELECT employee_specialty_id, employee_id, specialty_id, is_active
            FROM employee_specialties
            WHERE employee_specialty_id = ?
        """

        try:
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query, (employee_specialty_id,))
            record = cursor.fetchone()
            if record:
                return {
                    "employee_specialty_id": record[0],
                    "employee_id": record[1],
                    "specialty_id": record[2],
                    "is_active": record[3],
                }
            return None  # Zwracamy None, jeśli nie znaleziono rekordu
        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {op_err}") from op_err
        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych: {db_err}") from db_err
        

    def update_employee_specialty(self, employee_specialty_id, employee_id=None, specialty_id=None, is_active=None):
        """
        Aktualizuje rekord w tabeli employee_specialties na podstawie employee_specialty_id.
        
        :param employee_specialty_id: ID przypisania specjalności do pracownika (wymagane)
        :param employee_id: ID pracownika (opcjonalne)
        :param specialty_id: ID specjalności (opcjonalne)
        :param is_active: Status aktywności (opcjonalne)
        :raises ValueError: Jeśli nie podano żadnych wartości do aktualizacji.
        :raises sqlite3.Error: Jeśli wystąpił błąd bazy danych.
        """
        # Sprawdź czy przynajmniej jedna wartość jest różna od None
        if all(v is None for v in [employee_id, specialty_id, is_active]):
            raise ValueError("Brak danych do aktualizacji.")

        query = "UPDATE employee_specialties SET "
        params = []
        updates = []

        if employee_id is not None:
            updates.append("employee_id = ?")
            params.append(employee_id)
            
        if specialty_id is not None:
            updates.append("specialty_id = ?")
            params.append(specialty_id)
            
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(is_active)

        query += ", ".join(updates) + " WHERE employee_specialty_id = ?"
        params.append(employee_specialty_id)

        try:
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.cursor()
            cursor.execute(query, params)
            self.db_controller.connection.commit()

            if cursor.rowcount == 0:
                raise ValueError(f"Nie znaleziono przypisania o ID {employee_specialty_id}.")
                
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji przypisania pracownika do specjalności.") from db_error