# employees.py
# Moduł odpowiedzialny za zarządzanie tabelą `employees` w bazie danych.

from controllers.database_controller import DatabaseController
from validators.employees_model_validation import (
    validate_search_criteria,
    validate_unique_email,
    validate_unique_phone,
    validate_employee_exists,
)

import sqlite3

class Employees:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `employees`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Employees z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `employees` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            query = """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL CHECK (first_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*'),
                last_name TEXT NOT NULL CHECK (last_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*'),
                email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
                phone TEXT NOT NULL UNIQUE CHECK (LENGTH(phone) = 9 AND phone GLOB '[0-9]*'),
                profession TEXT NOT NULL CHECK (profession IN (
                    'Informatyk', 'Psychiatra', 'Psycholog kliniczny', 'Psychoterapeuta',
                    'Psychopedagog', 'Terapeuta uzależnień', 'Dietetyk kliniczny',
                    'Recepcjonista', 'Księgowy', 'Pracownik obsługi technicznej',
                    'Pracownik obsługi porządkowej')),
                is_medical_staff INTEGER NOT NULL CHECK (is_medical_staff IN (0, 1))
            )
            """
            self.db_controller.connection.execute(query)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}")  from e 


    def add_employee(self, first_name, last_name, email, phone, profession, is_medical_staff, is_active=True):
        """
        Dodaje nowego pracownika do tabeli `employees`.
        """
        try:
            query = """
            INSERT INTO employees (first_name, last_name, email, phone, profession, is_medical_staff, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.db_controller.connection.execute(query, 
                (first_name, last_name, email, phone, profession, is_medical_staff, is_active))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError("Błąd unikalności danych (email lub telefon już istnieje).") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych: {e}") from e






    def filter_employees(self, **criteria):
        """
        Filtruje pracowników na podstawie dowolnych kryteriów.
        Wykonuje poprawnie wszytkie metody testowe z pliku test_model_employees.py
        """
        validate_search_criteria(**criteria)

        query = "SELECT * FROM employees WHERE 1=1"
        params = []
        for key, value in criteria.items():
            query += f" AND {key} = ?"
            params.append(value)

        cursor = self.db_controller.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


    def update_employee(self, employee_id, **data):
        """
        Aktualizuje dane konkretnego pracownika na podstawie ID.
        Wykonuje poprawnie wszytkie metody testowe z pliku test_model_employees.py
        """
        if not data:
            raise ValueError("Brak danych do aktualizacji.")

        validate_employee_exists(self.db_controller, employee_id)

        if "email" in data:
            validate_unique_email(self.db_controller, data["email"])
        if "phone" in data:
            validate_unique_phone(self.db_controller, data["phone"])

        columns = ", ".join([f"{key} = ?" for key in data.keys()])
        params = list(data.values())
        params.append(employee_id)

        try:
            query = f"UPDATE employees SET {columns} WHERE employee_id = ?"
            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

            if cursor.rowcount == 0:
                raise KeyError(f"Pracownik o ID {employee_id} nie istnieje.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji danych: {e}") from e





    def delete_employees_by_criteria(self, **criteria):
        """
        Usuwa wszystkich pracowników spełniających podane kryteria.
        """
        validate_search_criteria(**criteria)

        query = "DELETE FROM employees WHERE 1=1"
        params = []
        for key, value in criteria.items():
            query += f" AND {key} = ?"
            params.append(value)

        try:
            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

            if cursor.rowcount == 0:
                raise KeyError("Brak pracowników spełniających podane kryteria.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania pracowników: {e}") from e




    def get_column_values(self, column_name):
        """
        Pobiera wszystkie wartości z wybranej kolumny w tabeli `employees`.
        
        :param column_name: Nazwa kolumny, której wartości mają zostać pobrane.
        :return: Lista wartości z podanej kolumny.
        :raises ValueError: Jeśli podana kolumna nie istnieje.
        """
        # Sprawdzenie bezpieczeństwa w przypadku dynamicznych nazw kolumn
        valid_columns = [
            "employee_id", "first_name", "last_name", 
            "email", "phone", "profession", "is_medical_staff"
        ]
        if column_name not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna: {column_name}. Dostępne kolumny: {valid_columns}")

        # Budowanie zapytania SQL
        query = f"SELECT {column_name} FROM employees"
        cursor = self.db_controller.connection.execute(query)

        # Pobranie i zwrócenie wartości z kolumny
        return [row[column_name] for row in cursor.fetchall()]


    def get_sorted_employees(self, order_by="employee_id", ascending=True):
        """
        Pobiera listę pracowników posortowaną według podanej kolumny i kierunku.
        
        metoda sortuje liczby i słowa od a do z i odwrotnie

        :param order_by: Nazwa kolumny, według której sortowane będą dane.
                        Domyślnie 'employee_id'.
        :param ascending: Określa kierunek sortowania:
                        True - sortowanie rosnące (ASC),
                        False - sortowanie malejące (DESC).
                        Domyślnie True.
        :return: Lista posortowanych rekordów.
        :raises ValueError: Jeśli nazwa kolumny nie jest prawidłowa.
        """
        # Lista dozwolonych kolumn dla bezpieczeństwa
        valid_columns = [
            "employee_id", "first_name", "last_name", 
            "email", "phone", "profession", "is_medical_staff"
        ]

        if order_by not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna: {order_by}. Dozwolone kolumny: {valid_columns}")

        # Określenie kierunku sortowania
        direction = "ASC" if ascending else "DESC"

        # Budowanie zapytania SQL
        query = f"SELECT * FROM employees ORDER BY {order_by} {direction}"
        
        # Wykonanie zapytania
        cursor = self.db_controller.connection.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def count_column_values(self, column_name):
        """
        Zlicza wystąpienia unikalnych wartości w podanej kolumnie tabeli `employees`.

        :param column_name: Nazwa kolumny, dla której mają być zliczone wartości.
        :return: Słownik, gdzie klucz to unikalna wartość, a wartość to liczba jej wystąpień.
        :raises ValueError: Jeśli podana kolumna nie jest poprawna.
        """
        # Lista dozwolonych kolumn dla bezpieczeństwa
        valid_columns = [
            "first_name", "last_name", "email", "phone", 
            "profession", "is_medical_staff"
        ]

        if column_name not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna: {column_name}. Dostępne kolumny: {valid_columns}")

        # Dynamiczne zapytanie SQL z COUNT i GROUP BY
        query = f"SELECT {column_name}, COUNT(*) as count FROM employees GROUP BY {column_name}"
        cursor = self.db_controller.connection.execute(query)

        # Tworzenie słownika z wynikami
        result = {row[column_name]: row["count"] for row in cursor.fetchall()}
        return result



    def get_is_medical_staff_by_employee_id(self, employee_id):
        """
        Pobiera wartość is_medical_staff dla danego employee_id.
        
        :param employee_id: ID pracownika.
        :return: 1 jeśli pracownik jest personelem medycznym, 0 jeśli nie, lub None jeśli nie znaleziono.
        
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        query = """
        SELECT is_medical_staff
        FROM employees
        WHERE employee_id = ?
        """
        try:
            self.db_controller.ensure_connection()  # Upewniamy się, że połączenie z bazą jest aktywne
            cursor = self.db_controller.connection.execute(query, (employee_id,))
            row = cursor.fetchone()
            
            is_medical_staff = row["is_medical_staff"] if row else None
            
            # Debugowanie: Wyświetlenie pobranej wartości
            print(f"[### MODEL PATIENTS] Pobrano is_medical_staff: {is_medical_staff} dla employee_id: {employee_id}")

            return is_medical_staff
        except Exception as e:
            print(f"[ERROR] Błąd bazy danych podczas pobierania is_medical_staff: {e}")
            raise RuntimeError(f"Problem z dostępem do bazy danych: {str(e)}") from e

    def get_all_employee_ids(self):
        """
        Pobiera wszystkie wartości z kolumny employee_id w tabeli employees.
        
        :return: Lista wszystkich employee_id lub pusta lista, jeśli brak rekordów.
        
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        query = """
        SELECT employee_id
        FROM employees
        """
        try:
            self.db_controller.ensure_connection()  # Upewniamy się, że połączenie z bazą jest aktywne
            cursor = self.db_controller.connection.execute(query)
            rows = cursor.fetchall()

            employee_ids = [row["employee_id"] for row in rows] if rows else []

            # Debugowanie: Wyświetlenie pobranych wartości
            print(f"[### MODEL EMPLOYEES] Pobrano employee_id: {employee_ids}")

            return employee_ids
        except Exception as e:
            print(f"[ERROR] Błąd bazy danych podczas pobierania wszystkich employee_id: {e}")
            raise RuntimeError(f"Problem z dostępem do bazy danych: {str(e)}") from e


    def get_all_employees(self):
        """
        Pobiera wszystkich pracowników z tabeli `employees`.
        """
        query = "SELECT * FROM employees"
        cursor = self.db_controller.connection.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_professions(self):
        """
        Pobiera wszystkie unikalne zawody (profession) z tabeli employees.

        Returns:
            list[str]: Lista unikalnych zawodów.
        """
        try:
            query = "SELECT DISTINCT profession FROM employees"
            cursor = self.db_controller.connection.execute(query)
            professions = [row[0] for row in cursor.fetchall()]

            # print(f"[### EMPLOYEE_MODEL] Pobranie zawodów: {professions}")
            return professions

        except AttributeError as ae:
            print(f"[### EMPLOYEE_MODEL] Błąd atrybutu: {ae}")
            return []
        except TypeError as te:
            print(f"[### EMPLOYEE_MODEL] Błąd typu danych: {te}")
            return []
        except ValueError as ve:
            print(f"[### EMPLOYEE_MODEL] Błąd wartości: {ve}")
            return []
        
    def get_all_emails_and_phones(self):
        """
        Pobiera wszystkie adresy e-mail i numery telefonów przypisane do pracowników.
        Zwraca listę słowników z kluczami 'email' i 'phone'.
        """
        try:
            query = "SELECT email, phone FROM employees"
            cursor = self.db_controller.connection.execute(query)
            results = [{"email": row["email"], "phone": row["phone"]} for row in cursor.fetchall()]

            # print(f"[### EMPLOYEE_MODEL] Pobranie emaili i telefonów: {results}")
            return results

        except sqlite3.Error as e:
            print(f"[### EMPLOYEE_MODEL] Błąd bazy danych: {str(e)}")
            return []
        
    def get_employee_by_id(self, employee_id):
        """
        Pobiera konkretnego pracownika na podstawie klucza głównego.
        """
        query = "SELECT * FROM employees WHERE employee_id = ?"
        cursor = self.db_controller.connection.execute(query, (employee_id,))
        row = cursor.fetchone()
        if row is None:
            raise KeyError(f"Pracownik o ID {employee_id} nie istnieje.")
        return dict(row)
    
    def delete_employee(self, employee_id):
        """
        Usuwa pracownika na podstawie klucza głównego.
        """
        validate_employee_exists(self.db_controller, employee_id)

        try:
            query = "DELETE FROM employees WHERE employee_id = ?"
            cursor = self.db_controller.connection.execute(query, (employee_id,))
            self.db_controller.connection.commit()

            if cursor.rowcount == 0:
                raise KeyError(f"Pracownik o ID {employee_id} nie istnieje.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania pracownika: {e}") from e
