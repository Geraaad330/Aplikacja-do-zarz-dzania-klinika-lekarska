# roles_controller.py
# Kontroler odpowiedzialny za logikę biznesową dla tabeli `roles`.

import sqlite3
from models.roles import Roles
from controllers.database_controller import DatabaseController


class RolesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `roles`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler ról oraz model zarządzający danymi ról.
        """
        self.db_controller = db_controller
        self.roles_model = Roles(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `roles` w bazie danych.
        """
        try:
            self.roles_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `roles`.") from db_error

    def add_role(self, role_name: str) -> bool:
        """
        Dodaje nową rolę do tabeli `roles`.

        :param role_name: Nazwa roli do dodania.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            success = self.roles_model.create_new_record(role_name)
            return success  # Zwraca True, jeśli dodanie było udane
        except ValueError as validation_error:
            print(f"[RolesController_add_role] Błąd walidacji: {validation_error}")
            return False
        except sqlite3.Error as db_error:
            print(f"[RolesController_add_role] Błąd bazy danych podczas dodawania nowej roli: {db_error}")
            return False


    def get_role_name_by_user_id(self, user_id):
        """
        Pobiera nazwę roli użytkownika na podstawie jego ID.
        """
        try:
            query = """
            SELECT r.role_name
            FROM roles r
            JOIN users_accounts u ON r.role_id = u.role_id
            WHERE u.user_id = ?
            """
            self.db_controller.ensure_connection()
            result = self.db_controller.connection.execute(query, (user_id,)).fetchone()
            if result:
                return result["role_name"]  # Zwraca nazwę roli
            else:
                return "Brak przypisanej roli"
        except AttributeError as ae:
            print(f"Błąd atrybutu: {ae}")
        except TypeError as te:
            print(f"Błąd typu danych: {te}")
        except ValueError as ve:
            print(f"Błąd wartości w wyniku zapytania: {ve}")




    def get_all_roles(self):
        """
        Pobiera wszystkie role z tabeli `roles`.
        """
        try:
            return self.roles_model.get_all_records()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania wszystkich ról.") from db_error

    def get_role_by_column(self, column_name, value):
        """
        Pobiera role na podstawie kolumny i wartości.
        """
        try:
            return self.roles_model.get_records_by_column(column_name, value)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania ról.") from db_error

    def update_role(self, role_id: int, role_name: str) -> bool:
        """
        Aktualizuje nazwę roli w tabeli 'roles'.

        :param role_id: ID roli do aktualizacji.
        :param role_name: Nowa nazwa roli.
        :return: True, jeśli aktualizacja się powiodła, False w przypadku błędu.
        """
        try:
            if not role_name:
                print("[RolesController_update_role] Brak nowej nazwy roli do aktualizacji.")
                return False  # Brak danych do aktualizacji

            success = self.roles_model.update_record(role_id, role_name)
            return success  # Zwraca True, jeśli aktualizacja była udana

        except sqlite3.IntegrityError:
            print("[RolesController_update_role] Błąd: Nazwa roli już istnieje w bazie danych.")
            return False  # Duplikacja nazwy roli

        except sqlite3.Error as db_error:
            print(f"[RolesController_update_role] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd



    def delete_role_by_id(self, role_id) -> bool:
        """
        Usuwa rolę na podstawie ID.

        :param role_id: ID roli do usunięcia.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            success = self.roles_model.delete_record_by_id(role_id)
            return success  # Zwraca True jeśli usunięcie było udane

        except ValueError as validation_error:
            print(f"[RolesController_delete_role_by_id] Błąd walidacji: {validation_error}")
            return False  # Błąd walidacji

        except sqlite3.Error as db_error:
            print(f"[RolesController_delete_role_by_id] Błąd bazy danych: {db_error}")
            return False  # Błąd bazy danych


    def filter_roles(self, column_name, operator, values):
        """
        Filtruje role na podstawie operatora i wartości.
        """
        try:
            return self.roles_model.filter_records(column_name, operator, values)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas filtrowania ról.") from db_error

    def sort_roles(self, column_name, ascending=True, filter_column=None, filter_value=None):
        """
        Sortuje role według wybranej kolumny z opcjonalnym filtrowaniem.
        """
        try:
            return self.roles_model.sort_records(column_name, ascending, filter_column, filter_value)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas sortowania ról.") from db_error

    def count_roles(self, column_name=None, pattern=None):
        """
        Zlicza role w tabeli `roles`, opcjonalnie z filtrem LIKE.
        """
        try:
            return self.roles_model.count_records(column_name, pattern)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas zliczania ról.") from db_error


    def ensure_table_exists(self):
        """
        Upewnia się, że tabela `roles` istnieje w bazie danych.
        """
        if not self.db_controller.table_exists("roles"):
            self.create_table()

    def get_role_by_id(self, role_id: int) -> dict:
        """
        Pobiera dane roli z modelu `roles` na podstawie `role_id`.

        :param role_id: ID roli do pobrania.
        :return: Słownik z danymi roli lub komunikat błędu.
        """
        try:
            # Sprawdzenie, czy `role_id` to liczba całkowita
            if not isinstance(role_id, int):
                raise ValueError(f"Nieprawidłowy format `role_id`: {role_id}. Oczekiwano liczby całkowitej.")

            # Pobranie danych roli z modelu
            role_data = self.roles_model.get_role_by_id(role_id)

            if not role_data:
                return {"error": f"Rola o ID {role_id} nie została znaleziona."}

            return role_data

        except ValueError as ve:
            print(f"[RolesController_get_role_by_id] Błąd wartości: {ve}")
            return {"error": f"Błąd wartości: {ve}"}

        except TypeError as te:
            print(f"[RolesController_get_role_by_id] Błąd typu danych: {te}")
            return {"error": f"Błąd typu danych: {te}"}
