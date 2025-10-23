# role_permissions_controller.py

import sqlite3
from models.role_permissions import RolePermissions
from controllers.database_controller import DatabaseController
from controllers.roles_controller import RolesController
from controllers.permissions_controller import PermissionsController


class RolePermissionsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `role_permissions`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `role_permissions` oraz model zarządzający danymi `role_permissions`.
        """
        self.db_controller = db_controller
        self.role_permissions_model = RolePermissions(db_controller)
        self.roles_controller = RolesController(db_controller)
        self.permissions_controller = PermissionsController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `role_permissions` w bazie danych.
        """
        try:
            self.role_permissions_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `role_permissions`.") from db_error

    def add_role_permission_by_ids(self, role_id: int, permission_id: int):
        """
        Dodaje nowy rekord na podstawie `role_id` i `permission_id`.
        """
        try:
            self.role_permissions_model.add_role_permission_by_ids(role_id, permission_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania rekordu do `role_permissions`.") from db_error

    def add_role_permission_by_names(self, role_name: str, permission_name: str):
        """
        Dodaje nowy rekord na podstawie nazw roli i uprawnienia.
        """
        try:
            self.role_permissions_model.add_role_permission_by_names(role_name, permission_name)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania rekordu do `role_permissions` po nazwach.") from db_error

    def get_all_role_permissions(self, filters=None, sort_by=None):
        """
        Pobiera wszystkie rekordy z tabeli `role_permissions` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            return self.role_permissions_model.get_records_with_filters(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów z `role_permissions`.") from db_error

    def get_role_permission_by_ids(self, role_id: int, permission_id: int):
        """
        Pobiera rekord z tabeli `role_permissions` na podstawie `role_id` i `permission_id`.
        """
        try:
            return self.role_permissions_model.get_role_permission_by_ids(role_id, permission_id)
        except KeyError as not_found_error:
            raise KeyError("Nie znaleziono rekordu o podanych wartościach.") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordu z `role_permissions`.") from db_error

    def update_role_permission_by_ids(self, role_permission_id: int, role_id: int = None, permission_id: int = None):
        """
        Aktualizuje rekord w tabeli `role_permissions` na podstawie `role_permission_id`, `role_id` i `permission_id`.
        """
        try:
            self.role_permissions_model.update_role_permission_by_ids(role_permission_id, role_id, permission_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji rekordu w `role_permissions`.") from db_error

    def update_role_permission_by_names(self, role_permission_id: int, role_name: str = None, permission_name: str = None):
        """
        Aktualizuje rekord w tabeli `role_permissions` na podstawie nazw roli i uprawnienia.
        """
        try:
            self.role_permissions_model.update_role_permission_by_names(role_permission_id, role_name, permission_name)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji rekordu w `role_permissions` po nazwach.") from db_error

    def delete_role_permission_by_id(self, role_permission_id: int):
        """
        Usuwa rekord z tabeli `role_permissions` na podstawie `role_permission_id`.
        """
        try:
            self.role_permissions_model.delete_role_permission_by_id(role_permission_id)
        except KeyError as not_found_error:
            raise KeyError("Nie znaleziono rekordu o podanym ID.") from not_found_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordu z `role_permissions`.") from db_error

    def delete_records_by_role_or_permission(self, role_id: int = None, permission_id: int = None):
        """
        Usuwa wszystkie rekordy związane z podanym `role_id` lub `permission_id`.
        """
        try:
            self.role_permissions_model.delete_records_by_role_or_permission(role_id, permission_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordów z `role_permissions`.") from db_error

    def delete_record_by_role_and_permission(self, role_id: int = None, permission_id: int = None):
        """
        Usuwa rekord z tabeli `role_permissions` na podstawie `role_id` i `permission_id`.
        """
        try:
            self.role_permissions_model.delete_record_by_role_and_permission(role_id, permission_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania rekordu z `role_permissions`.") from db_error
