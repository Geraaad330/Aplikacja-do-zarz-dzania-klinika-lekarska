# users_accounts_model_validation.py

import re
from datetime import datetime
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.roles_controller import RolesController


# Walidacja first_name i last_name
def validate_name_field(name: str) -> None:
    """
    Waliduje imię lub nazwisko użytkownika.

    :param name: Imię lub nazwisko.
    :raises ValueError: Jeśli dane są nieprawidłowe.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s]+$"
    if not isinstance(name, str):
        raise ValueError("Imię i nazwisko musi być ciągiem znaków.")
    if not name.strip():
        raise ValueError("Imię i nazwisko nie może być puste.")
    if len(name) < 3 or len(name) > 100:
        raise ValueError("Imię i nazwisko musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, name):
        raise ValueError("Imię i nazwisko zawiera niedozwolone znaki.")


# Walidacja role_name
def validate_role_name(role_name: str) -> None:
    """
    Waliduje nazwę roli.

    :param role_name: Nazwa roli.
    :raises ValueError: Jeśli dane są nieprawidłowe.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s():.,/\\-]+$"
    if not isinstance(role_name, str):
        raise ValueError("Nazwa roli musi być ciągiem znaków.")
    if not role_name.strip():
        raise ValueError("Nazwa roli nie może być pusta.")
    if len(role_name) < 3 or len(role_name) > 100:
        raise ValueError("Nazwa roli musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, role_name):
        raise ValueError("Nazwa roli zawiera niedozwolone znaki.")


# Walidacja istnienia role_id i employee_id
def validate_employee_id_exists(employees_controller: EmployeesController, employee_id: int) -> None:
    """
    Sprawdza, czy `employee_id` istnieje w tabeli `employees`.

    :param employees_controller: Kontroler pracowników.
    :param employee_id: ID pracownika.
    :raises ValueError: Jeśli pracownik nie istnieje.
    """
    employee = employees_controller.get_employee(employee_id)
    if not employee:
        raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.")


def validate_role_id_exists(roles_controller: RolesController, role_id: int) -> None:
    """
    Sprawdza, czy `role_id` istnieje w tabeli `roles`.

    :param roles_controller: Kontroler ról.
    :param role_id: ID roli.
    :raises ValueError: Jeśli rola nie istnieje.
    """
    role = roles_controller.get_role_by_column("role_id", role_id)
    if not role:
        raise ValueError(f"Rola o ID {role_id} nie istnieje.")


# Walidacja unikalności
def validate_unique_employee_id(db_controller: DatabaseController, employee_id: int) -> None:
    """
    Sprawdza unikalność `employee_id` w tabeli `users_accounts`.

    :param db_controller: Kontroler bazy danych.
    :param employee_id: ID pracownika.
    :raises ValueError: Jeśli `employee_id` nie jest unikalne.
    """
    query = "SELECT COUNT(*) FROM users_accounts WHERE employee_id = ?"
    cursor = db_controller.connection.execute(query, (employee_id,))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Pracownik o ID {employee_id} już istnieje w tabeli users_accounts.")


def validate_unique_username(db_controller: DatabaseController, username: str) -> None:
    """
    Sprawdza unikalność `username` w tabeli `users_accounts`.

    :param db_controller: Kontroler bazy danych.
    :param username: Nazwa użytkownika.
    :raises ValueError: Jeśli `username` nie jest unikalne.
    """
    query = "SELECT COUNT(*) FROM users_accounts WHERE username = ?"
    cursor = db_controller.connection.execute(query, (username,))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Nazwa użytkownika '{username}' już istnieje w tabeli users_accounts.")


# Walidacja pól datetime
def validate_datetime_field(datetime_value: str) -> None:
    """
    Waliduje pole datetime w formacie `YYYY-MM-DD HH:MM`.
    """


    if not isinstance(datetime_value, str):
        raise ValueError("Pole datetime musi być ciągiem znaków.")
    try:
        datetime.strptime(datetime_value, "%Y-%m-%d %H:%M")
    except ValueError as e:
        raise ValueError(f"Wartość '{datetime_value}' nie jest w formacie YYYY-MM-DD HH:MM.") from e



# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def validate_operator_and_value(operator: str, value=None):
    """
    Waliduje operator i wartość w zapytaniach SQL.

    :param operator: Operator SQL (np. "=", "LIKE").
    :param value: Wartość przypisana operatorowi.
    :raises ValueError: Jeśli operator lub wartość są nieprawidłowe.
    """
    valid_operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN", "IS NULL", "IS NOT NULL"]

    if operator not in valid_operators:
        raise ValueError(f"Nieobsługiwany operator: {operator}.")

    if operator == "LIKE" and (not isinstance(value, str) or not value.strip()):
        raise ValueError("Wartość dla operatora LIKE musi być niepustym ciągiem znaków.")

    if operator == "BETWEEN" and not (isinstance(value, tuple) and len(value) == 2):
        raise ValueError("Operator BETWEEN wymaga krotki zawierającej dwie wartości.")

    if operator == "IN" and not (isinstance(value, (list, tuple)) and len(value) > 0):
        raise ValueError("Wartość dla operatora IN musi być niepustą listą lub krotką.")

    if operator in ["IS NULL", "IS NOT NULL"] and value is not None:
        raise ValueError(f"Operator {operator} nie wymaga przypisanej wartości.")


def validate_filters_and_sorting(filters, sort_by, valid_columns):
    """
    Waliduje filtry i sortowanie używane w zapytaniach SQL.

    :param filters: Lista słowników reprezentujących filtry, gdzie każdy słownik powinien zawierać klucze:
        - "column" (str): Nazwa kolumny, na której zastosowany jest filtr.
        - "operator" (str): Operator SQL (np. '=', 'LIKE', 'IN', 'BETWEEN', 'IS NULL').
        - "value" (opcjonalny): Wartość przypisana do operatora, wymagana dla większości operatorów.
    :param sort_by: Lista krotek reprezentujących sortowanie, gdzie każda krotka zawiera:
        - Nazwa kolumny do sortowania.
        - Kierunek sortowania ('ASC' lub 'DESC').
    :param valid_columns: Lista dozwolonych kolumn (str) w zapytaniach SQL.
    :raises ValueError: Jeśli:
        - Filtr zawiera nieprawidłową kolumnę.
        - Filtr używa nieprawidłowego operatora lub niewłaściwej wartości dla operatora.
        - Sortowanie używa nieprawidłowej kolumny lub kierunku.

    :return: None
    """
    if filters:
        for filter_item in filters:
            if not all(key in filter_item for key in ["column", "operator", "value"]):
                raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")
            if filter_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if filter_item["operator"] not in ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN", "IS NULL", "IS NOT NULL"]:
                raise ValueError(f"Nieprawidłowy operator w filtrze: {filter_item['operator']}.")

    if sort_by:
        for sort_item in sort_by:
            if "column" not in sort_item or "direction" not in sort_item:
                raise ValueError("Każde sortowanie musi zawierać klucze: 'column' i 'direction'.")
            if sort_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w sortowaniu: {sort_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if sort_item["direction"].upper() not in ["ASC", "DESC"]:
                raise ValueError(f"Nieprawidłowy kierunek sortowania: {sort_item['direction']}. Dozwolone wartości: 'ASC', 'DESC'.")


def handle_database_error(db_controller, query: str, params: tuple):
    """
    Obsługuje błędy bazy danych i zgłasza bardziej czytelne komunikaty.

    :param db_controller: Kontroler bazy danych.
    :param query: Zapytanie SQL.
    :param params: Parametry zapytania SQL.
    :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
    """
    try:
        return db_controller.connection.execute(query, params)
    except Exception as e:
        raise RuntimeError(f"Błąd podczas wykonywania zapytania: {query}. Szczegóły: {str(e)}") from e