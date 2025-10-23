from controllers.database_controller import DatabaseController
import sqlite3
from typing import List
from validators.patients_model_validation import (
    validate_first_name,
    validate_last_name,
    validate_pesel,
    validate_phone,
    validate_email,
    validate_date_of_birth,
    validate_address,
    validate_patient_update,
    validate_filter_criteria
)

class Patients:
    def __init__(self, db_controller: DatabaseController):
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę patients w bazie danych, jeśli jeszcze nie istnieje.
        """
        query = """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Klucz główny z AUTOINCREMENT
            first_name TEXT NOT NULL CHECK (
                first_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*' -- może zawierać tylko małe i duże litery z polskimi znakami. Nie może zawirać innych znaków ANI SPACJI
            ),
            last_name TEXT NOT NULL CHECK (
                last_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*' -- może zawierać tylko małe i duże litery z polskimi znakami. Nie może zawirać innych znaków ANI SPACJI
            ),
            pesel TEXT NOT NULL UNIQUE CHECK (
                LENGTH(pesel) = 11 AND pesel GLOB '[0-9]*' -- może zawierać tylko dokładnie 11 cyfr. Nie może zawirać innych znaków
            ),
            phone TEXT NOT NULL UNIQUE CHECK (
                LENGTH(phone) = 9 AND phone GLOB '[0-9]*' -- może zawierać tylko dokładnie 9 cyfr. Nie może zawirać innych znaków
            ),
            email TEXT NOT NULL UNIQUE CHECK (
                email LIKE '%@%' AND email LIKE '%.%' -- Musi zawierać znak '@' i '.', może zawierać cyfry, małe i duże litery
            ),
            address TEXT, -- Dowolny tekst, brak dodatkowych ograniczeń
            date_of_birth TEXT NOT NULL CHECK (
                date_of_birth GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]' -- Format daty YYYY-MM-DD
            ),
            is_active BOOLEAN DEFAULT TRUE
        )
        """
        self.db_controller.connection.execute(query)
        self.db_controller.connection.commit()

    def add_patient(self, first_name, last_name, pesel, phone, email, address, date_of_birth, is_active=True):
        """
        Dodaje nowego pacjenta do tabeli patients z walidacją danych.
        """
        # Walidacja danych wejściowych
        validate_first_name(first_name)
        validate_last_name(last_name)
        validate_pesel(pesel, self.get_all_existing_pesels())
        validate_phone(phone)
        validate_email(email)
        validate_date_of_birth(date_of_birth)
        address = validate_address(address)  # Czyszczenie i walidacja adresu

        query = """
        INSERT INTO patients (first_name, last_name, pesel, phone, email, address, date_of_birth, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.safe_execute(
                query, (first_name, last_name, pesel, phone, email, address, date_of_birth, is_active)
            )
        except RuntimeError as e:
            raise RuntimeError(f"Nie udało się dodać pacjenta: {e}") from e





    def get_patient(self, patient_id):
        try:
            query = "SELECT * FROM patients WHERE patient_id = ?"
            cursor = self.db_controller.connection.execute(query, (patient_id,))
            row = cursor.fetchone()
            result = dict(row) if row else None
            # print(f"[model patients] Wynik zapytania dla patient_id {patient_id}: {result}")
            return result
        except Exception as e:
            print(f"Błąd zapytania do bazy danych: {e}")
            raise

    def filter_patients_by_pesel(self, pesel):
        """
        Filtrowanie pacjentów na podstawie numeru PESEL.
        """
        query = "SELECT * FROM patients WHERE pesel = ?"
        cursor = self.db_controller.connection.execute(query, (pesel,))
        return [dict(row) for row in cursor.fetchall()]

    def update_patient(self, patient_id, **kwargs):
        """
        Aktualizuje dane pacjenta na podstawie przekazanych kluczy-wartości z walidacją.
        """
        # Pobranie istniejących PESEL-i
        existing_pesels = self.get_all_existing_pesels()

        # Walidacja danych do aktualizacji
        if "address" in kwargs:  # Czyszczenie adresu przed walidacją
            kwargs["address"] = validate_address(kwargs["address"])
        validate_patient_update(kwargs, existing_pesels)

        columns = ", ".join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values()) + [patient_id]
        query = f"UPDATE patients SET {columns} WHERE patient_id = ?"
        try:
            cursor = self.safe_execute(query, values)
            return cursor.rowcount
        except RuntimeError as e:
            raise RuntimeError(f"Nie udało się zaktualizować pacjenta: {e}") from e


    def delete_patient(self, patient_id):
        """
        Usuwa pacjenta z bazy danych na podstawie ID.
        """
        query = "DELETE FROM patients WHERE patient_id = ?"
        cursor = self.db_controller.connection.execute(query, (patient_id,))
        self.db_controller.connection.commit()
        return cursor.rowcount

    def search_patients(self, first_name=None, last_name=None):
        """
        Wyszukuje pacjentów na podstawie imienia i/lub nazwiska.
        """
        query = "SELECT * FROM patients WHERE 1=1"
        params = []
        if first_name:
            query += " AND first_name LIKE ?"
            params.append(f"%{first_name}%")
        if last_name:
            query += " AND last_name LIKE ?"
            params.append(f"%{last_name}%")
        cursor = self.db_controller.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def advanced_filter_patients(self, **criteria):
        """
        Filtrowanie pacjentów na podstawie wielu kryteriów z walidacją.
        """
        # Walidacja kryteriów filtrowania
        validate_filter_criteria(criteria)

        query = "SELECT * FROM patients WHERE 1=1"
        params = []

        if 'first_name' in criteria:
            query += " AND first_name LIKE ?"
            params.append(f"%{criteria['first_name']}%")
        if 'last_name' in criteria:
            query += " AND last_name LIKE ?"
            params.append(f"%{criteria['last_name']}%")
        if 'pesel' in criteria:
            query += " AND pesel = ?"
            params.append(criteria['pesel'])
        if 'phone' in criteria:
            query += " AND phone LIKE ?"
            params.append(f"%{criteria['phone']}%")
        if 'email' in criteria:
            query += " AND email LIKE ?"
            params.append(f"%{criteria['email']}%")
        if 'address' in criteria:
            query += " AND address LIKE ?"
            params.append(f"%{criteria['address']}%")
        if 'date_of_birth' in criteria:
            query += " AND date_of_birth = ?"
            params.append(criteria['date_of_birth'])

        try:
            cursor = self.safe_execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except RuntimeError as e:
            raise RuntimeError(f"Nie udało się przefiltrować pacjentów: {e}") from e



    def get_all_patients(self):
        """
        Zwraca listę wszystkich pacjentów.
        """
        query = "SELECT * FROM patients"
        cursor = self.db_controller.connection.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def get_all_existing_pesels(self) -> List[str]:
        """
        Zwraca listę wszystkich numerów PESEL pacjentów.
        """
        query = "SELECT pesel FROM patients"  # Zapytanie SQL pobierające tylko PESEL
        cursor = self.db_controller.connection.execute(query)
        return [row['pesel'] for row in cursor.fetchall()]  # Zwrócenie listy numerów PESEL


    def safe_execute(self, query, params=()):
        """
        Wykonuje zapytanie do bazy danych z obsługą wyjątków.
        """
        try:
            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
            return cursor
        except Exception as e:
            self.db_controller.connection.rollback()
            print(f"Błąd podczas wykonywania zapytania: {e}")
            raise RuntimeError(f"Zapytanie nie powiodło się: {e}") from e
        


    def get_all_patients_details(self) -> list:
        """
        Wykonuje zapytanie do bazy danych z obsługą wyjątków.
        """

        query = """
        SELECT patient_id, first_name, last_name, pesel, phone, email, address, date_of_birth, is_active
        FROM patients
        """

        try:
            cursor = self.db_controller.connection.execute(query)
            patients = []
            for row in cursor.fetchall():
                # print(f"[DEBUG] Pobieranie wiersza: {row}")  # Logowanie każdego wiersza
                patient = {
                    "patient_id": row["patient_id"],  # Upewnij się, że patient_id istnieje
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "pesel": row["pesel"],
                    "phone": row["phone"],
                    "email": row["email"],
                    "address": row["address"],
                    "date_of_birth": row["date_of_birth"],
                    "is_active": row["is_active"],
                }
                patients.append(patient)
            # print(f"[DEBUG] Pobranie danych pacjentów: {patients}")
            return patients
        except KeyError as ke:
            print(f"[ERROR] Brak klucza w danych pacjentów: {ke}")
            raise
        except sqlite3.Error as e:
            print(f"[ERROR] Błąd bazy danych podczas pobierania pacjentów: {e}")
            raise RuntimeError(f"Błąd bazy danych: {e}") from e





    def get_patient_ids_and_names(self):
        """
        Pobiera wszystkie rekordy z kolumn `patient_id`, `first_name`, i `last_name`.

        Returns:
            list: Lista słowników zawierających `patient_id`, `first_name` i `last_name`.
        
        Raises:
            RuntimeError: W przypadku błędu bazy danych.
        """
        query = "SELECT patient_id, first_name, last_name FROM patients"
        try:
            cursor = self.db_controller.connection.execute(query)
            result = [dict(row) for row in cursor.fetchall()]
            
            # Debugowanie: Wyświetlenie listy pacjentów w postaci listy stringów
            print("[###MODEL PATIENTS] Pobrano listę pacjentów:")
            for patient in result:
                print(f"patient_id: {patient['patient_id']}, first_name: {patient['first_name']}, last_name: {patient['last_name']}")
            
            return result
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania danych pacjentów: {e}") from e
        


    def get_patient_name_by_id(self, patient_id):
        """
        Pobiera imię i nazwisko pacjenta na podstawie jego ID.
        """
        query = "SELECT first_name, last_name FROM patients WHERE patient_id = ?"
        cursor = self.db_controller.connection.execute(query, (patient_id,))
        row = cursor.fetchone()

        if row:
            first_name = row["first_name"]
            last_name = row["last_name"]
            return f"{first_name} {last_name}"

        return None


    def get_last_patient_id(self):
        """
        Pobiera ostatni (najwyższy) patient_id z tabeli patients.
        
        Returns:
            int: Ostatni patient_id lub None, jeśli tabela jest pusta.
            
        Raises:
            RuntimeError: W przypadku błędu bazy danych.
        """
        query = "SELECT MAX(patient_id) AS last_id FROM patients"
        try:
            cursor = self.safe_execute(query)
            row = cursor.fetchone()
            last_id = row["last_id"] if row else None
            
            # Debugowanie - wyświetl pobrany ID
            # print(f"[### MODEL PATIENTS] Ostatni patient_id w bazie: {last_id}")
            
            return last_id
        except Exception as e:
            print(f"Błąd podczas pobierania ostatniego patient_id: {str(e)}")
            raise RuntimeError(f"Problem z dostępem do bazy danych: {str(e)}") from e
        

    def get_all_pesel_phone_email(self):
        """
        Pobiera listę słowników zawierających 'pesel', 'phone' i 'email' dla wszystkich pacjentów.
        
        Returns:
            list[dict]: Lista słowników, gdzie każdy słownik ma klucze:
                        'pesel', 'phone', 'email'.
        
        Raises:
            RuntimeError: W przypadku błędu w bazie danych.
        """
        query = """
            SELECT pesel, phone, email
            FROM patients
        """
        try:
            # Jeśli masz metodę self.safe_execute(query), użyj jej:
            cursor = self.safe_execute(query)
            
            results = []
            for row in cursor.fetchall():
                record = {
                    "pesel": row["pesel"],
                    "phone": row["phone"],
                    "email": row["email"]
                }
                results.append(record)
            
            return results
        except Exception as e:
            print(f"[MODEL PATIENTS] Błąd podczas pobierania pesel, phone, email: {str(e)}")
            raise RuntimeError(f"Problem z dostępem do bazy danych: {str(e)}") from e


    def get_all_patient_ids(self):
        """
        Pobiera wszystkie identyfikatory pacjentów z tabeli patients.

        Returns:
            list: Lista wszystkich patient_id w bazie danych.
            
        Raises:
            RuntimeError: W przypadku błędu bazy danych.
        """
        query = "SELECT patient_id FROM patients"
        try:
            cursor = self.db_controller.connection.execute(query)
            return [row["patient_id"] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania patient_id: {e}") from e
