# users_accounts_controller.py

import sqlite3
from models.users_accounts import UsersAccounts
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.roles_controller import RolesController


class UsersAccountsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `users_accounts`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `users_accounts` oraz model zarządzający danymi `users_accounts`.
        """
        self.db_controller = db_controller
        self.users_accounts_model = UsersAccounts(db_controller)
        self.employees_controller = EmployeesController(db_controller)
        self.roles_controller = RolesController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `users_accounts` w bazie danych.
        """
        try:
            self.users_accounts_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `users_accounts`.") from db_error

    def add_user_by_ids(
        self,
        employee_id: int,
        role_id: int,
        username: str,
        password_hash: str,
        is_active: int,
        created_at: str,
        last_login: str = None,
        expired: str = None,
    ) -> bool:
        """
        Dodaje nowego użytkownika do tabeli `users_accounts`.

        :param employee_id: ID przypisanego pracownika.
        :param role_id: ID przypisanej roli.
        :param username: Nazwa użytkownika.
        :param password_hash: Zhashowane hasło użytkownika.
        :param is_active: Status aktywności konta (1 = aktywne, 0 = nieaktywne).
        :param created_at: Data utworzenia konta w formacie "YYYY-MM-DD HH:MM".
        :param last_login: Data ostatniego logowania (opcjonalna).
        :param expired: Data wygaśnięcia konta (opcjonalna).
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            success = self.users_accounts_model.add_user_by_ids(
                employee_id,
                role_id,
                username,
                password_hash,
                is_active,
                created_at,
                last_login,
                expired
            )
            return success is not None  # True jeśli użytkownik został dodany

        except sqlite3.IntegrityError as integrity_error:
            print(f"[UsersAccountsController_add_user] Błąd integralności: {integrity_error}")
            return False  # Wystąpił błąd integralności

        except sqlite3.Error as db_error:
            print(f"[UsersAccountsController_add_user] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd




    def add_user_by_names(
        self,
        first_name: str,
        last_name: str,
        role_name: str,
        username: str,
        password_hash: str,
        is_active: int,
        created_at: str,
        last_login: str = None,
        expired: str = None,
    ):
        """
        Dodaje nowego użytkownika na podstawie imienia, nazwiska i roli.
        """
        try:
            self.users_accounts_model.add_user_by_names(
                first_name, last_name, role_name, username, password_hash, is_active, created_at, last_login, expired
            )
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania użytkownika po nazwach.") from db_error



    def get_username_by_user_id(self, user_id):
        """
        Pobiera nazwę użytkownika na podstawie user_id za pomocą modelu.
        """
        return self.users_accounts_model.get_username_by_user_id(user_id)


    def get_employee_id_by_user_id(self, user_id):
        """
        Pobiera ID pracownika na podstawie user_id za pomocą modelu.
        """
        return self.users_accounts_model.get_employee_id_by_user_id(user_id)

    def get_role_id_by_user_id(self, user_id: int) -> int:
        """
        Pobiera role_id przypisany do danego user_id za pomocą modelu.
        """
        return self.users_accounts_model.get_role_id_by_user_id(user_id)


    def get_users_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera użytkowników z tabeli `users_accounts` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            return self.users_accounts_model.get_users_with_filters(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów.") from db_error

    def get_users_with_names(self, filters=None, sort_by=None):
        """
        Pobiera użytkowników z tabeli `users_accounts`, zastępując ID nazwami.
        """
        try:
            return self.users_accounts_model.get_users_with_names(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów z nazwami.") from db_error


    def update_user_by_ids(self, user_id: int, **update_data) -> bool:
        """
        Aktualizuje dane użytkownika w tabeli `users_accounts`.

        :param user_id: ID użytkownika do aktualizacji.
        :param update_data: Słownik zawierający klucze i wartości do aktualizacji.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            if not update_data:
                print("[UsersAccountsController_update_user] Brak danych do aktualizacji.")
                return False  # Brak aktualizacji

            success = self.users_accounts_model.update_user_by_ids(user_id, **update_data)
            return success  # Zwróci True jeśli aktualizacja miała miejsce

        except sqlite3.Error as db_error:
            print(f"[UsersAccountsController_update_user] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd



    def update_user_by_names(
        self,
        user_id: int,
        first_name: str = None,
        last_name: str = None,
        role_name: str = None,
        username: str = None,
        password_hash: str = None,
        is_active: int = None,
        last_login: str = None,
        expired: str = None,
    ):
        """
        Aktualizuje użytkownika na podstawie `user_id`, używając imienia, nazwiska i roli.
        """
        try:
            self.users_accounts_model.update_user_by_names(
                user_id, first_name, last_name, role_name, username, password_hash, is_active, last_login, expired
            )
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji użytkownika po nazwach.") from db_error

    def delete_user(self, user_id: int) -> bool:
        """
        Usuwa użytkownika z tabeli `users_accounts` na podstawie `user_id`.

        :param user_id: ID użytkownika do usunięcia.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.users_accounts_model.delete_user(user_id)
            return True  # Usunięcie zakończone sukcesem
        except sqlite3.Error as db_error:
            print(f"[UsersAccountsController_delete_user] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd



    def get_user_by_id(self, user_id):
        """
        Pobiera dane użytkownika na podstawie `user_id`.

        :param user_id: ID użytkownika do pobrania.
        :return: Słownik z danymi użytkownika lub komunikat błędu.
        """
        try:
            # Sprawdzenie, czy user_id to liczba całkowita
            if not isinstance(user_id, int):
                raise ValueError(f"Nieprawidłowy format `user_id`: {user_id}. Oczekiwano liczby całkowitej.")

            # Pobranie danych użytkownika z modelu
            user_data = self.users_accounts_model.get_user_by_id(user_id)

            if user_data is None:
                return f"Użytkownik o ID {user_id} nie został znaleziony."

            return user_data

        except ValueError as ve:
            print(f"[### USERS_ACCOUNTS_CONTROLLER] Błąd wartości: {ve}")
            return f"Błąd wartości: {ve}"
        except TypeError as te:
            print(f"[### USERS_ACCOUNTS_CONTROLLER] Błąd typu danych: {te}")
            return f"Błąd typu danych: {te}"