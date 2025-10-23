# employees_controller.py
# Kontroler odpowiedzialny za logikę biznesową dla tabeli `employees`.

import sqlite3
from models.employees import Employees
from controllers.database_controller import DatabaseController


class EmployeesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `employees`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler pracowników oraz model zarządzający danymi pracowników.
        """
        self.db_controller = db_controller
        self.employees_model = Employees(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `employees` w bazie danych.
        """
        try:
            self.employees_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `employees`.") from db_error



    def add_new_employee(self, first_name, last_name, email, phone, profession, is_medical_staff, is_active):
        """
        Dodaje nowego pracownika, przekazując dane do modelu `employees.py`.
        Obsługuje potencjalne błędy związane z bazą danych i unikalnością danych.
        """
        try:
            self.employees_model.add_employee(
                first_name, last_name, email, phone, profession, is_medical_staff, is_active
            )
            print(f"[EmployeesController] Dodano pracownika: {first_name} {last_name} ({email})")
            return {"success": True, "message": "Pracownik został dodany pomyślnie."}

        except ValueError as ve:
            print(f"[EmployeesController] Błąd walidacji: {str(ve)}")
            return {"success": False, "message": str(ve)}

        except RuntimeError as re:
            print(f"[EmployeesController] Błąd bazy danych: {str(re)}")
            return {"success": False, "message": "Błąd systemu podczas dodawania pracownika."}







    def get_employee(self, employee_id: int):
        """
        Pobiera dane pracownika na podstawie ID.
        """
        try:
            return self.employees_model.get_employee_by_id(employee_id)
        except KeyError as exc:
            raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.") from exc # Zmieniono z KeyError na ValueError


    def get_all_employees(self):
        """
        Pobiera wszystkich pracowników.
        """
        try:
            return self.employees_model.get_all_employees()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania pracowników.") from db_error

    def filter_employees(self, **criteria):
        """
        Filtruje pracowników na podstawie podanych kryteriów.
        """
        try:
            return self.employees_model.filter_employees(**criteria)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji kryteriów filtrowania: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas filtrowania pracowników.") from db_error

    def get_sorted_employees(self, order_by="employee_id", ascending=True):
        """
        Pobiera pracowników posortowanych według podanej kolumny i kierunku.
        """
        try:
            return self.employees_model.get_sorted_employees(order_by, ascending)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji kolumny sortowania: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas sortowania pracowników.") from db_error

    def delete_employees_by_criteria(self, **criteria):
        """
        Usuwa pracowników na podstawie podanych kryteriów.
        """
        try:
            self.employees_model.delete_employees_by_criteria(**criteria)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji kryteriów usuwania: {validation_error}") from validation_error
        except KeyError as key_error:
            raise KeyError("Brak pracowników spełniających podane kryteria.") from key_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania pracowników.") from db_error


    def count_column_values(self, column_name):
        """
        Zlicza unikalne wartości w kolumnie.
        """
        try:
            return self.employees_model.count_column_values(column_name)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas liczenia wartości w kolumnie.") from db_error
        


    def get_is_medical_staff_by_employee_id(self, employee_id):
        """
        Pobiera wartość is_medical_staff dla danego employee_id.
        """
        try:
            return self.employees_model.get_is_medical_staff_by_employee_id(employee_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania wartości is_medical_staff.") from db_error


    def get_all_employee_ids(self):
        """
        Pobiera wszystkie wartości employee_id z tabeli employees.
        
        :return: Lista wszystkich employee_id.
        
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            return self.employees_model.get_all_employee_ids()
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania listy employee_id.") from db_error


    def get_all_professions(self):
        """
        Pobiera wszystkie zawody z modelu employees.

        Returns:
            list[str]: Lista unikalnych zawodów.
        """
        try:
            professions = self.employees_model.get_all_professions()
            # print(f"[### EMPLOYEES_CONTROLLER] Lista zawodów: {professions}")
            return professions

        except AttributeError as ae:
            print(f"[### EMPLOYEES_CONTROLLER] Błąd atrybutu: {ae}")
            return []
        except TypeError as te:
            print(f"[### EMPLOYEES_CONTROLLER] Błąd typu danych: {te}")
            return []
        except ValueError as ve:
            print(f"[### EMPLOYEES_CONTROLLER] Błąd wartości: {ve}")
            return []
    
    def get_all_emails_and_phones(self):
        """
        Wywołuje metodę modelu `get_all_emails_and_phones` i zwraca listę emaili i telefonów.
        Obsługuje ewentualne błędy.
        """
        try:
            emails_and_phones = self.employees_model.get_all_emails_and_phones()
            return emails_and_phones

        except RuntimeError as re:
            print(f"[EmployeesController] Błąd systemowy: {str(re)}")
            return []
        


    def update_employee(self, employee_id, **kwargs):
        """
        Aktualizuje dane pracownika na podstawie ID.
        """
        try:
            self.employees_model.update_employee(employee_id, **kwargs)
        except KeyError as key_error:
            raise KeyError(f"Pracownik o ID {employee_id} nie istnieje.") from key_error
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji danych pracownika.") from db_error

    def delete_employee(self, employee_id):
        """
        Usuwa pracownika na podstawie ID.
        """
        try:
            self.employees_model.delete_employee(employee_id)
        except KeyError as key_error:
            raise KeyError(f"Pracownik o ID {employee_id} nie istnieje.") from key_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania pracownika.") from db_error