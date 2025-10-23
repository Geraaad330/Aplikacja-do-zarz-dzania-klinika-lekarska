# assigned_patients_controller.py

import sqlite3
from models.assigned_patients import AssignedPatients
from controllers.database_controller import DatabaseController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.patients_controller import PatientController


class AssignedPatientsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `assigned_patients`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `assigned_patients` oraz model zarządzający danymi `assigned_patients`.
        """
        self.db_controller = db_controller
        self.assigned_patients_model = AssignedPatients(db_controller)
        self.users_accounts_controller = UsersAccountsController(db_controller)
        self.patients_controller = PatientController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `assigned_patients` w bazie danych.
        """
        try:
            self.assigned_patients_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `assigned_patients`.") from db_error

    def add_record_by_ids(self, fk_patient_id: int, fk_employee_id: int, is_active: int) -> bool:
        """
        Dodaje nowy rekord na podstawie ID pacjenta i użytkownika.

        :param fk_patient_id: ID pacjenta.
        :param fk_employee_id: ID pracownika.
        :param is_active: Status aktywności.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            # Sprawdzenie, czy podane wartości nie są puste
            if fk_patient_id is None or fk_employee_id is None:
                raise ValueError("Błąd integralności: fk_patient_id i fk_employee_id nie mogą być puste.")

            # Dodanie rekordu do bazy
            self.assigned_patients_model.add_record_by_ids(fk_patient_id, fk_employee_id, is_active)
            
            return True  # Dodanie zakończone sukcesem

        except sqlite3.IntegrityError as integrity_error:
            print(f"[AssignedPatientsController_add_record_by_ids] Błąd integralności bazy danych: {integrity_error}")
            return False  # Wystąpił błąd integralności

        except sqlite3.DatabaseError as db_error:
            print(f"[AssignedPatientsController_add_record_by_ids] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd bazy danych

        except ValueError as ve:
            print(f"[AssignedPatientsController_add_record_by_ids] Błąd wartości: {ve}")
            return False  # Wystąpił błąd wartości

        except TypeError as te:
            print(f"[AssignedPatientsController_add_record_by_ids] Błąd typu danych: {te}")
            return False  # Wystąpił błąd typu danych



    def add_record_by_names(self, patient_first_name: str, patient_last_name: str, user_name: str):
        """
        Dodaje nowy rekord na podstawie nazw pacjenta i użytkownika.
        """
        try:
            self.assigned_patients_model.add_record_by_names(patient_first_name, patient_last_name, user_name)
        except KeyError as not_found_error:
            raise RuntimeError("Nie znaleziono użytkownika lub pacjenta o podanych nazwach.") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania rekordu do `assigned_patients` po nazwach.") from db_error

    def get_records_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `assigned_patients` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            return self.assigned_patients_model.get_records_with_filters(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów z `assigned_patients`.") from db_error

    def get_record_by_patient_and_user_ids(self, fk_patient_id: int, fk_employee_id: int):
        """
        Pobiera rekord na podstawie ID pacjenta i użytkownika.
        """
        try:
            return self.assigned_patients_model.get_record_by_patient_and_user_ids(fk_patient_id, fk_employee_id)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordu z `assigned_patients`.") from db_error



    def update_record_by_ids(self, assignment_id: int, **update_data) -> bool:
        """
        Aktualizuje rekord przypisania pacjenta do pracownika na podstawie `assignment_id` oraz dostarczonych wartości.

        :param assignment_id: ID przypisania do aktualizacji.
        :param update_data: Słownik zawierający klucze i wartości do aktualizacji.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            if not update_data:
                print("[AssignedPatientsController_update_record_by_ids] Brak danych do aktualizacji.")
                return False  # Brak aktualizacji

            success = self.assigned_patients_model.update_record_by_ids(assignment_id, **update_data)
            return success  # Zwróci True jeśli aktualizacja miała miejsce

        except sqlite3.Error as db_error:
            print(f"[AssignedPatientsController_update_record_by_ids] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd



    def delete_record_by_id(self, assignment_id: int) -> bool:
        """
        Usuwa rekord na podstawie assignment_id.

        :param assignment_id: ID przypisania do usunięcia.
        :return: True, jeśli usunięcie się powiodło, False w przypadku błędu.
        """
        try:
            self.db_controller.ensure_connection()
            
            query = "DELETE FROM assigned_patients WHERE assignment_id = ?"
            cursor = self.db_controller.connection.execute(query, (assignment_id,))
            self.db_controller.connection.commit()

            return cursor.rowcount > 0  # Zwraca True, jeśli rekord został usunięty

        except sqlite3.Error as e:
            print(f"[### ASSIGNED_PATIENTS_MODEL] Błąd podczas usuwania rekordu: {e}")
            return False  # Zwraca False w przypadku błędu



    def delete_record_by_names(self, patient_first_name: str = None, patient_last_name: str = None, user_name: str = None):
        """
        Usuwa rekord na podstawie nazw pacjenta i/lub użytkownika.
        """
        try:
            self.assigned_patients_model.delete_record_by_names(patient_first_name, patient_last_name, user_name)
        except KeyError as not_found_error:
            raise KeyError("Nie znaleziono użytkownika lub pacjenta o podanych nazwach.") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordu z `assigned_patients`.") from db_error



    def get_assigned_patients_by_employee_id(self, fk_employee_id: int) -> list:
        """
        Pobiera listę przypisanych pacjentów na podstawie podanego user_id.
        """
        try:
            # Pobranie przypisanych pacjentów z modelu
            assigned_patients = self.assigned_patients_model.get_assigned_patients_by_employee_id(fk_employee_id)
            

            if not assigned_patients:
                # print(f"[DEBUG] Brak przypisanych pacjentów dla user_id {user_id}")  # Debugowanie
                raise ValueError(f"Brak przypisanych pacjentów dla user_id {fk_employee_id}")

            return assigned_patients

        except sqlite3.Error as db_error:
            print(f"[DEBUG] Błąd bazy danych podczas pobierania przypisanych pacjentów: {db_error}")  # Debugowanie
            raise RuntimeError(f"Błąd bazy danych podczas pobierania przypisanych pacjentów: {db_error}") from db_error
        except ValueError as ve:
            print(f"[DEBUG] Błąd danych wejściowych: {ve}")  # Debugowanie
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve


    def get_all_assigned_patients(self):
        """
        Pobiera wszystkie przypisane rekordy pacjentów poprzez model.
        """
        try:
            assigned_patients = self.assigned_patients_model.get_all_assigned_patients()

            if not assigned_patients:
                print("[AssignedPatientsController] Brak przypisanych pacjentów w bazie.")
                return []

            return assigned_patients

        except RuntimeError as re:
            print(f"[AssignedPatientsController] Błąd podczas pobierania danych: {str(re)}")
            return []


    # assigned_patients_controller.py
    def get_employee_id_by_assignment_id(self, assignment_id: int) -> int:
        """
        Pobiera ID pracownika na podstawie ID przypisania pacjenta.
        
        :param assignment_id: ID przypisania do weryfikacji
        :return: ID powiązanego pracownika
        :raises RuntimeError: Błąd operacji bazodanowej
        :raises ValueError: Nieprawidłowe ID przypisania
        """
        try:
            if not isinstance(assignment_id, int) or assignment_id <= 0:
                raise ValueError("Nieprawidłowy format ID przypisania")

            employee_id = self.assigned_patients_model.get_employee_id_by_assignment_id(assignment_id)
            return employee_id

        except sqlite3.Error as db_error:
            error_msg = f"Błąd bazy danych przy pobieraniu pracownika: {str(db_error)}"
            print(f"[controller assigned_patients] {error_msg}")
            raise RuntimeError(error_msg) from db_error
            
        except ValueError as ve:
            error_msg = f"Błąd danych wejściowych: {str(ve)}"
            print(f"[controller assigned_patients] {error_msg}")
            raise ValueError(error_msg) from ve
        
    def get_assigned_patient_by_id(self, assignment_id):
        """
        Pobiera dane przypisanego pacjenta na podstawie `assignment_id`.

        :param assignment_id: ID przypisania pacjenta.
        :return: Słownik z danymi przypisania lub komunikat błędu.
        """
        try:
            # Sprawdzenie, czy assignment_id to liczba całkowita
            if not isinstance(assignment_id, int):
                raise ValueError(f"Nieprawidłowy format `assignment_id`: {assignment_id}. Oczekiwano liczby całkowitej.")

            # Pobranie danych przypisania pacjenta z modelu
            assigned_patient_data = self.assigned_patients_model.get_assigned_patient_by_id(assignment_id)

            if assigned_patient_data is None:
                return f"Przypisanie pacjenta o ID {assignment_id} nie zostało znalezione."

            return assigned_patient_data

        except ValueError as ve:
            print(f"[### ASSIGNED_PATIENTS_CONTROLLER] Błąd wartości: {ve}")
            return f"Błąd wartości: {ve}"
        except TypeError as te:
            print(f"[### ASSIGNED_PATIENTS_CONTROLLER] Błąd typu danych: {te}")
            return f"Błąd typu danych: {te}"
        

    def delete_assign_with_patient(self, assignment_id: int = None, fk_patient_id: int = None, fk_employee_id: int = None):
        """
        Usuwa rekord z tabeli assigned_patients na podstawie assignment_id lub fk_patient_id i fk_employee_id.
        """
        try:
            if assignment_id:
                self.assigned_patients_model.delete_record_by_assignment_id(assignment_id)
            elif fk_patient_id and fk_employee_id:
                self.assigned_patients_model.delete_record_by_ids(fk_patient_id, fk_employee_id)
            else:
                raise ValueError("Musisz podać assignment_id lub fk_patient_id i fk_employee_id.")
        except ValueError as e:
            raise e  # Bezpośrednie przekazanie ValueError
        except Exception as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e