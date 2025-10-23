# patients_controller.py

import sqlite3
from models.patients import Patients
from validators.patients_model_validation import (
    validate_first_name,
    validate_last_name,
    validate_pesel,
    validate_phone,
    validate_email,
    validate_date_of_birth,
    validate_address,
    validate_filter_criteria  # Dodana funkcja do walidacji kryteriów filtrowania
)


class PatientController:
    """
    Kontroler odpowiedzialny za komunikację między modelami, bazą danych i walidacją.
    Obsługuje logikę biznesową dla pacjentów.
    """

    def __init__(self, db_connection):
        """
        Inicjalizuje kontroler pacjentów oraz model zarządzający danymi pacjentów.
        """
        self.model = Patients(db_connection)  # Komunikacja z modelem Patients
        self.db_connection = db_connection  # Bezpośrednie połączenie z bazą danych

    def create_table(self):
        """
        Tworzy tabelę `users_accounts` w bazie danych.
        """
        try:
            self.model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `users_accounts`.") from db_error


    def add_patient(self, first_name, last_name, pesel, phone, email, address, date_of_birth):
        """
        Dodaje nowego pacjenta do bazy danych z walidacją danych.
        """
        try:
            # Pobranie istniejących PESEL-i dla walidacji
            existing_pesels = self.get_all_existing_pesels()

            # Walidacja danych wejściowych
            validate_first_name(first_name)
            validate_last_name(last_name)
            validate_pesel(pesel, existing_pesels)
            validate_phone(phone)
            validate_email(email)
            validate_date_of_birth(date_of_birth)
            validate_address(address)

            # Użycie połączenia z bazy danych
            self.db_connection.ensure_connection()
            query = """
            INSERT INTO patients (first_name, last_name, pesel, phone, email, address, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (first_name, last_name, pesel, phone, email, address, date_of_birth)
            cursor = self.db_connection.connection.execute(query, params)
            self.db_connection.connection.commit()

            # Pobranie ID dodanego pacjenta
            patient_id = cursor.lastrowid
            return {"patient_id": patient_id, "first_name": first_name, "last_name": last_name}

        except sqlite3.IntegrityError as integrity_error:
            raise ValueError("Błąd integralności danych: PESEL lub email już istnieje.") from integrity_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania pacjenta.") from db_error

    def get_patient_name_by_id(self, patient_id):
        """
        Pobiera imię i nazwisko pacjenta na podstawie ID.
        """
        try:
            # Wywołanie metody z modelu
            return self.model.get_patient_name_by_id(patient_id)
        except sqlite3.Error as db_error:
            print(f"Błąd bazy danych podczas pobierania imienia i nazwiska pacjenta: {db_error}")
            raise RuntimeError(f"Błąd bazy danych: {db_error}") from db_error



    def get_patient_by_id(self, patient_id):
        try:
            result = self.model.get_patient(patient_id)
            # print(f"[kontroler patients] Pobranie pacjenta o ID {patient_id}: {result}")
            return result
        except Exception as e:
            print(f"Błąd pobierania pacjenta: {e}")
            raise

    def get_all_patients(self):
        """
        Pobiera dane wszystkich pacjentów z obsługą wyjątków.
        """
        try:
            return self.model.get_all_patients()
        except Exception as e:
            print(f"Błąd pobierania wszystkich pacjentów: {e}")
            raise

    def update_patient(self,
                    patient_id: int,
                    first_name: str = None,
                    last_name: str = None,
                    pesel: str = None,
                    phone: str = None,
                    email: str = None,
                    address: str = None,
                    date_of_birth: str = None,
                    is_active: str = None) -> None:
        """
        Aktualizuje dane pacjenta w bazie danych z walidacją przekazanych pól.
        Przyjmuje parametry opcjonalne, które można pomijać podczas wywołania.
        """
        try:
            # Budujemy słownik tylko z nie-None wartości
            data_to_update = {}
            if first_name is not None:
                data_to_update['first_name'] = first_name
            if last_name is not None:
                data_to_update['last_name'] = last_name
            if pesel is not None:
                data_to_update['pesel'] = pesel
            if phone is not None:
                data_to_update['phone'] = phone
            if email is not None:
                data_to_update['email'] = email
            if address is not None:
                data_to_update['address'] = address
            if date_of_birth is not None:
                data_to_update['date_of_birth'] = date_of_birth
            if is_active is not None:
                data_to_update['is_active'] = is_active
                

            # Wywołanie metody modelu z użyciem **data_to_update
            return self.model.update_patient(patient_id, **data_to_update)

        except ValueError as e:
            print(f"Błąd walidacji: {e}")
            raise
        except RuntimeError as e:
            print(f"Błąd aktualizacji pacjenta: {e}")
            raise


    def delete_patient(self, patient_id):
        """
        Usuwa pacjenta na podstawie jego ID.
        """
        try:
            return self.model.delete_patient(patient_id)
        except Exception as e:
            print(f"Błąd usuwania pacjenta: {e}")
            raise

    def filter_patients_by_pesel(self, pesel):
        """
        Filtruje pacjentów na podstawie numeru PESEL.
        """
        try:
            return self.model.filter_patients_by_pesel(pesel)
        except Exception as e:
            print(f"Błąd filtrowania pacjentów: {e}")
            raise

    def advanced_filter_patients(self, **criteria):
        """
        Filtrowanie pacjentów na podstawie wielu kryteriów z walidacją.
        """
        try:
            validate_filter_criteria(criteria)
            return self.model.advanced_filter_patients(**criteria)
        except ValueError as e:
            print(f"Błąd walidacji kryteriów filtrowania: {e}")
            raise
        except RuntimeError as e:
            print(f"Błąd filtrowania pacjentów: {e}")
            raise

    def get_all_existing_pesels(self):
        """
        Pobiera wszystkie numery PESEL z bazy danych.
        """
        try:
            return self.model.get_all_existing_pesels()
        except Exception as e:
            print(f"Błąd pobierania numerów PESEL: {e}")
            raise

    def connect_to_database(self):
        """
        Nawiązuje połączenie z bazą danych.
        """
        try:
            if not self.db_connection.is_connected:
                self.db_connection.connect_to_database()
        except Exception as e:
            print(f"Błąd łączenia z bazą danych: {e}")
            raise

    def close_database_connection(self):
        """
        Zamyka połączenie z bazą danych.
        """
        try:
            if self.db_connection.is_connected:
                self.db_connection.close_connection()
        except Exception as e:
            print(f"Błąd zamykania połączenia z bazą danych: {e}")
            raise




    def get_all_patients_details(self):
        """
        Pobiera wszystkie szczegóły pacjentów.
        """
        try:
            return self.model.get_all_patients_details()
        except Exception as e:
            print(f"Błąd podczas pobierania szczegółów pacjentów: {e}")
            raise

    def get_patient_ids_and_names(self):
        """
        Pobiera wszystkie rekordy z kolumn `patient_id`, `first_name`, i `last_name` z modelu.

        Returns:
            list: Lista słowników zawierających `patient_id`, `first_name` i `last_name`.

        Raises:
            RuntimeError: W przypadku błędu bazy danych podczas pobierania danych pacjentów.
        """
        try:
            # Wywołanie metody modelu
            return self.model.get_patient_ids_and_names()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania danych pacjentów.") from db_error

    def add_new_patient(self, first_name, last_name, pesel, phone, email, address, date_of_birth, is_active):
        """
        Dodaje nowego pacjenta, wywołując metodę add_patient modelu patients.
        Przechwytuje błędy bazy danych i podnosi je jako RuntimeError.

        Args:
            first_name (str): Imię pacjenta.
            last_name (str): Nazwisko pacjenta.
            pesel (str): Numer PESEL pacjenta.
            phone (str): Numer telefonu pacjenta.
            email (str): Adres email pacjenta.
            address (str): Adres zamieszkania pacjenta.
            date_of_birth (str): Data urodzenia pacjenta.

        Raises:
            RuntimeError: Błąd związany z bazą danych lub z zapisem pacjenta.
        """
        try:
            self.model.add_patient(
                first_name, last_name, pesel, phone, email, address, date_of_birth, is_active
            )
        except sqlite3.Error as db_error:
            print(f"[PatientsController] Błąd bazy danych podczas dodawania pacjenta: {db_error}")
            raise RuntimeError(f"Błąd bazy danych podczas dodawania pacjenta: {db_error}") from db_error
        except RuntimeError as re:
            # Obsługa innych błędów zgłoszonych w trakcie walidacji lub zapisu
            print(f"[PatientsController] Błąd podczas dodawania pacjenta: {re}")
            raise RuntimeError(f"Błąd podczas dodawania pacjenta: {re}") from re

    def get_last_patient_id(self):
        """
        Pobiera ostatni (najwyższy) patient_id z tabeli patients, wywołując metodę get_last_patient_id modelu patients.
        Przechwytuje błędy bazy danych i podnosi je jako RuntimeError.

        Returns:
            int: Ostatni patient_id lub None, jeśli tabela jest pusta.

        Raises:
            RuntimeError: Błąd związany z bazą danych lub z pobieraniem ostatniego patient_id.
        """
        try:
            last_id = self.model.get_last_patient_id()
            return last_id
        except sqlite3.Error as db_error:
            print(f"[PatientsController] Błąd bazy danych podczas pobierania ostatniego patient_id: {db_error}")
            raise RuntimeError(f"Błąd bazy danych podczas pobierania ostatniego patient_id: {db_error}") from db_error
        except RuntimeError as re:
            # Obsługa innych błędów zgłoszonych w trakcie pobierania ostatniego patient_id
            print(f"[PatientsController] Błąd podczas pobierania ostatniego patient_id: {re}")
            raise RuntimeError(f"Błąd podczas pobierania ostatniego patient_id: {re}") from re
        
    def get_all_pesel_phone_email(self):
        """
        Pobiera listę zawierającą pesel, phone i email dla wszystkich pacjentów.
        
        Returns:
            list[dict]: Lista słowników z kluczami 'pesel', 'phone', 'email'.
        
        Raises:
            Exception: W przypadku błędu bazy danych lub innych błędów.
        """
        try:
            return self.model.get_all_pesel_phone_email()
        except Exception as e:
            print(f"Błąd podczas pobierania pesel, phone, email: {e}")
            raise


    def get_all_patient_ids(self):
        """
        Pobiera wszystkie identyfikatory pacjentów, wywołując metodę z modelu Patients.

        Returns:
            list: Lista wszystkich patient_id w bazie danych.

        Raises:
            RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            return self.model.get_all_patient_ids()
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania patient_id: {db_error}") from db_error
