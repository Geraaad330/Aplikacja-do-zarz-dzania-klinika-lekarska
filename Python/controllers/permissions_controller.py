# permissions_controller.py
# Kontroler odpowiedzialny za logikę biznesową dla tabeli `system_permissions`.

import sqlite3
from models.permissions import Permissions
from controllers.database_controller import DatabaseController


class PermissionsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `system_permissions`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler uprawnień oraz model zarządzający danymi uprawnień.
        """
        self.db_controller = db_controller
        self.permissions_model = Permissions(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `system_permissions` w bazie danych.
        """
        try:
            self.permissions_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `system_permissions`.") from db_error

    def add_permission(self, permission_name: str):
        """
        Dodaje nowe uprawnienie do tabeli `system_permissions`.

        :param permission_name: Nazwa uprawnienia.
        :raises ValueError: Jeśli nazwa jest nieprawidłowa.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            self.permissions_model.add_permission(permission_name)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania nowego uprawnienia.") from db_error



    def get_all_permissions(self):
        """
        Pobiera wszystkie uprawnienia z tabeli.
        """
        try:
            return self.permissions_model.get_all_permissions()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania uprawnień.") from db_error

    def filter_permissions(self, permission_names=None, name_pattern=None):
        """
        Filtruje uprawnienia na podstawie listy nazw lub wzorca.
        """
        try:
            return self.permissions_model.filter_permissions(permission_names, name_pattern)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas filtrowania uprawnień.") from db_error

    def get_sorted_permissions(self, order_by="permission_name", ascending=True):
        """
        Pobiera posortowane uprawnienia według wskazanej kolumny i kierunku.
        """
        try:
            return self.permissions_model.get_sorted_permissions(order_by, ascending)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji kolumny sortowania: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas sortowania uprawnień.") from db_error

    def count_permissions(self, name_pattern=None):
        """
        Zlicza uprawnienia, opcjonalnie z filtrem LIKE.
        """
        try:
            return self.permissions_model.count_permissions(name_pattern)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji wzorca filtrowania: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas zliczania uprawnień.") from db_error

    def count_permissions_by_name(self, permission_names):
        """
        Zlicza uprawnienia na podstawie listy nazw.
        """
        try:
            return self.permissions_model.count_permissions_by_name(permission_names)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji listy nazw: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas zliczania uprawnień po nazwach.") from db_error
