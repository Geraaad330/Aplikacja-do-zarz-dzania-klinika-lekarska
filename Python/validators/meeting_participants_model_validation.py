# meeting_participants_model_validation.py

import sqlite3
from controllers.database_controller import DatabaseController

def validate_attendance(attendance: str):
    """
    Waliduje wartość `attendance`.

    Args:
        attendance (str): Status obecności (np. 'Obecny', 'Nieobecny', 'Usprawiedliwiony').

    Raises:
        ValueError: Jeśli wartość `attendance` jest nieprawidłowa.

    Example:
        validate_attendance("Obecny")  # Brak błędu
        validate_attendance("Nieznany")  # ValueError
    """
    valid_statuses = ["Obecny", "Nieobecny", "Usprawiedliwiony", ""]
    if attendance not in valid_statuses:
        raise ValueError(f"Nieprawidłowa wartość `attendance`: {attendance}. Dozwolone wartości: {', '.join(valid_statuses)}.")

def validate_participant_role(participant_role: str):
    """
    Waliduje wartość `participant_role`.

    Args:
        participant_role (str): Rola uczestnika (np. 'Organizator', 'Uczestnik').

    Raises:
        ValueError: Jeśli wartość `participant_role` jest nieprawidłowa.

    Example:
        validate_participant_role("Organizator")  # Brak błędu
        validate_participant_role("Nieznany")  # ValueError
    """
    valid_roles = ["Organizator", "Uczestnik",""]
    if participant_role not in valid_roles:
        raise ValueError(f"Nieprawidłowa rola uczestnika: {participant_role}. Dozwolone role: {', '.join(valid_roles)}.")

def validate_fk_meeting_id_exists(db_controller: DatabaseController, meeting_id: int):
    """
    Sprawdza, czy podane `fk_meeting_id` istnieje w tabeli `internal_meetings`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        meeting_id (int): ID spotkania.

    Raises:
        ValueError: Jeśli `fk_meeting_id` nie istnieje.

    Example:
        validate_fk_meeting_id_exists(db_controller, 1)  # Brak błędu
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM internal_meetings WHERE meeting_id = ?"
        cursor = db_controller.connection.execute(query, (meeting_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Spotkanie o ID {meeting_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania istnienia spotkania: {e}") from e

def validate_fk_employee_id_exists(db_controller: DatabaseController, employee_id: int):
    """
    Sprawdza, czy podane `fk_employee_id` istnieje w tabeli `employees`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        employee_id (int): ID pracownika.

    Raises:
        ValueError: Jeśli `fk_employee_id` nie istnieje.

    Example:
        validate_fk_employee_id_exists(db_controller, 1)  # Brak błędu
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM employees WHERE employee_id = ?"
        cursor = db_controller.connection.execute(query, (employee_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania istnienia pracownika: {e}") from e

# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_update_fields(updates: dict, valid_columns: list) -> None:
    """
    Waliduje pola aktualizacji w zapytaniach SQL.

    :param updates: Słownik pól do aktualizacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli pole do aktualizacji jest nieprawidłowe lub słownik jest pusty.
    :example:
    validate_update_fields({"room_type": "Nowa nazwa"}, ["room_type_id", "room_type"])  # Brak błędu
    validate_update_fields({"invalid_column": "value"}, ["room_type_id", "room_type"])  # ValueError
    """

    valid_columns = ["participant_id", "fk_meeting_id", "fk_employee_id", "participant_role", "attendance"]

    if not updates:
        raise ValueError("Nie podano danych do aktualizacji.")
    for column in updates.keys():
        if column not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna do aktualizacji: {column}.")

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

    valid_columns = ["participant_id", "fk_meeting_id", "fk_employee_id", "participant_role", "attendance"]


    if filters:
        for filter_item in filters:
            # Sprawdzanie kluczy w filtrze
            if not all(key in filter_item for key in ["column", "operator", "value"]):
                raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")

            # Sprawdzanie, czy kolumna filtra jest poprawna
            if filter_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")

            # Walidacja operatora i wartości
            #validate_operator_and_value(filter_item["operator"], filter_item.get("value"))

    if sort_by:
        for sort_item in sort_by:
            # Sprawdzanie kluczy w sortowaniu
            if "column" not in sort_item or "direction" not in sort_item:
                raise ValueError("Każde sortowanie musi zawierać klucze: 'column' i 'direction'.")
            
            # Sprawdzanie, czy kolumna sortowania jest poprawna
            if sort_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w sortowaniu: {sort_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")

            # Sprawdzanie, czy kierunek sortowania jest poprawny
            if sort_item["direction"].upper() not in ["ASC", "DESC"]:
                raise ValueError(f"Nieprawidłowy kierunek sortowania: {sort_item['direction']}. Dozwolone wartości: 'ASC', 'DESC'.")
