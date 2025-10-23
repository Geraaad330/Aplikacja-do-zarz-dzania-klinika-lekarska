# employee_specialties_controller.py

import sqlite3
from models.employee_specialties import EmployeeSpecialties
from controllers.database_controller import DatabaseController


class EmployeeSpecialtiesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `employee_specialties`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler specjalizacji pracowników oraz model zarządzający danymi `employee_specialties`.
        """
        self.db_controller = db_controller
        self.employee_specialties_model = EmployeeSpecialties(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `employee_specialties` w bazie danych.
        """
        try:
            self.employee_specialties_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `employee_specialties`.") from db_error


    def get_specialties_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie specjalizacje powiązane z danym employee_id za pomocą modelu.

        Args:
            employee_id (int): ID pracownika.

        Returns:
            list[int]: Lista ID specjalizacji powiązanych z pracownikiem, jeśli istnieją, w przeciwnym razie pusta lista.
        """
        return self.employee_specialties_model.get_specialties_by_employee_id(employee_id)




    # pylint: disable=W0613
    def get_all_records(self, filters=None): #def get_all_records(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_specialties`.
        """
        try:
            return self.employee_specialties_model.get_records()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów `employee_specialties`.") from db_error

    def get_records_with_names(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `employee_specialties` wraz z imionami, nazwiskami i nazwami specjalizacji.
        """
        # Lista dozwolonych kolumn
        valid_columns = [
            "employee_specialty_id", "employee_id", "specialty_id",
            "first_name", "last_name", "specialty_name"
        ]

        # Walidacja kolumn w filtrach
        if filters:
            for filter_item in filters:
                if filter_item["column"] not in valid_columns:
                    raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}")

        # Budowanie zapytania SQL
        query = """
            SELECT
                es.employee_specialty_id,
                e.first_name,
                e.last_name,
                s.specialty_name,
                es.employee_id,
                es.specialty_id
            FROM
                employee_specialties AS es
            JOIN
                employees AS e ON es.employee_id = e.employee_id
            JOIN
                specialties AS s ON es.specialty_id = s.specialty_id
        """

        where_clause, values = self.db_controller.build_filters(filters)
        if where_clause:
            query += f" WHERE {where_clause}"
        if sort_by:
            query += f" ORDER BY {sort_by}"

        cursor = self.db_controller.connection.execute(query, values)
        return [dict(row) for row in cursor.fetchall()]





    def add_employee_specialty(self, employee_id, specialty_id, is_active):
        """
        Dodaje specjalizację dla pracownika na podstawie ich ID.
        """
        try:
            self.employee_specialties_model.add_employee_specialty(employee_id, specialty_id, is_active)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania specjalizacji pracownika.") from db_error



    def update_record_by_id(self, employee_specialty_id, new_employee_id=None, new_specialty_id=None):
        """
        Aktualizuje rekord `employee_specialties` na podstawie jego ID.
        """
        try:
            self.employee_specialties_model.update_record_by_id(employee_specialty_id, new_employee_id, new_specialty_id)
        except KeyError as not_found_error:
            raise KeyError(f"Nie znaleziono rekordu: {not_found_error}") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji rekordu `employee_specialties`.") from db_error

    def update_record_by_name(self, first_name, last_name, specialty_name, **updates):
        """
        Aktualizuje rekord `employee_specialties` na podstawie imienia, nazwiska i nazwy specjalizacji.
        """
        try:
            self.employee_specialties_model.update_record_by_name_using_names(first_name, last_name, specialty_name, **updates)
        except KeyError as not_found_error:
            raise KeyError(f"Nie znaleziono rekordu: {not_found_error}") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji rekordu `employee_specialties`.") from db_error

    def delete_employee_specialty(self, employee_specialty_id):
        """
        Usuwa rekord `employee_specialties` na podstawie jego ID.
        """
        try:
            self.employee_specialties_model.delete_employee_specialty(employee_specialty_id)
        except KeyError as not_found_error:
            raise KeyError(f"Nie znaleziono rekordu: {not_found_error}") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordu `employee_specialties`.") from db_error

    def delete_record_by_name(self, first_name, last_name, specialty_name):
        """
        Usuwa rekord `employee_specialties` na podstawie imienia, nazwiska i nazwy specjalizacji.
        """
        try:
            self.employee_specialties_model.delete_record_by_name(first_name, last_name, specialty_name)
        except KeyError as not_found_error:
            raise KeyError(f"Nie znaleziono rekordu: {not_found_error}") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordu `employee_specialties` po nazwach.") from db_error
        
    def get_all_employee_specialties(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_specialties`.

        :return: Lista słowników z rekordami.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            return self.employee_specialties_model.get_all_employee_specialties()
        except RuntimeError as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania specjalności pracowników: {db_error}") from db_error

    def get_all_employee_specialty_ids(self):
        """
        Pobiera wszystkie identyfikatory `employee_specialty_id` z tabeli `employee_specialties`.

        :return: Lista identyfikatorów `employee_specialty_id`.
        :raises RuntimeError: Błąd bazy danych podczas pobierania danych.
        """
        try:
            return self.employee_specialties_model.get_all_employee_specialty_ids()
        except RuntimeError as re:
            raise RuntimeError(f"Błąd podczas pobierania identyfikatorów specjalizacji pracowników: {re}") from re
        
    def get_employee_specialty_by_id(self, employee_specialty_id):
        """
        Pobiera dane przypisania specjalizacji do pracownika na podstawie `employee_specialty_id`.

        :param employee_specialty_id: ID przypisania specjalizacji do pracownika.
        :return: Słownik zawierający dane przypisania specjalizacji lub None, jeśli nie znaleziono.
        :raises ValueError: Jeśli `employee_specialty_id` nie jest liczbą całkowitą.
        :raises RuntimeError: Jeśli wystąpił błąd bazy danych.
        """
        try:
            # Konwersja ID na int
            employee_specialty_id = int(employee_specialty_id)
        except ValueError as e:
            raise ValueError("ID przypisania specjalizacji musi być liczbą całkowitą.") from e 

        try:
            record = self.employee_specialties_model.get_employee_specialty_by_id(employee_specialty_id)
            if record is None:
                raise ValueError(f"Nie znaleziono przypisania specjalizacji o ID {employee_specialty_id}.")
            return record
        except RuntimeError as re:
            raise RuntimeError(f"Błąd podczas pobierania danych przypisania specjalizacji: {re}") from re
        

    def update_employee_specialty(self, employee_specialty_id, employee_id=None, specialty_id=None, is_active=None):
        """
        Aktualizuje przypisanie pracownika do specjalności.
        
        :param employee_specialty_id: ID przypisania specjalności do pracownika (wymagane)
        :param employee_id: ID pracownika (opcjonalne)
        :param specialty_id: ID specjalności (opcjonalne)
        :param is_active: Status aktywności (opcjonalne)
        :raises ValueError: Jeśli dane nie zostały podane lub ID nie istnieje.
        :raises RuntimeError: Jeśli wystąpił błąd bazy danych.
        """
        try:
            self.employee_specialties_model.update_employee_specialty(employee_specialty_id, employee_id, specialty_id, is_active)
            return {"success": True, "message": "Przypisanie zostało zaktualizowane."}
        except ValueError as ve:
            return {"success": False, "message": str(ve)}
        except RuntimeError:
            return {"success": False, "message": "Błąd podczas aktualizacji przypisania pracownika do specjalności."}