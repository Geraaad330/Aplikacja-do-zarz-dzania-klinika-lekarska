# internal_meetings_model_validation.py

import re
import sqlite3
from controllers.database_controller import DatabaseController

def validate_internal_meeting_status(status: str):
    """
    Waliduje wartość `internal_meeting_status`.

    Args:
        status (str): Status spotkania.

    Raises:
        ValueError: Jeśli wartość statusu jest nieprawidłowa.

    Example:
        validate_internal_meeting_status("Zaplanowane")  # Brak błędu
        validate_internal_meeting_status("Nieznany")  # ValueError
    """
    valid_statuses = ["Zaplanowane", "Zakończone", "Odwołane", "Przełożone", "Oczekujące"]
    if status not in valid_statuses:
        raise ValueError(f"Nieprawidłowy status spotkania: {status}. Dozwolone wartości: {', '.join(valid_statuses)}.")

def validate_fk_meeting_type_exists(db_controller: DatabaseController, meeting_type_id: int):
    """
    Sprawdza, czy podany `fk_meeting_type_id` istnieje w tabeli `meeting_types`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        meeting_type_id (int): ID typu spotkania.

    Raises:
        ValueError: Jeśli `meeting_type_id` nie istnieje.

    Example:
        validate_fk_meeting_type_exists(db_controller, 1)  # Brak błędu, jeśli rekord istnieje
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM meeting_types WHERE meeting_type_id = ?"
        cursor = db_controller.connection.execute(query, (meeting_type_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Typ spotkania o ID {meeting_type_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania zależności: {e}") from e

def validate_fk_room_exists(db_controller: DatabaseController, room_id: int):
    """
    Sprawdza, czy podany `fk_room_id` istnieje w tabeli `rooms`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        room_id (int): ID pokoju.

    Raises:
        ValueError: Jeśli `room_id` nie istnieje.

    Example:
        validate_fk_room_exists(db_controller, 1)  # Brak błędu, jeśli rekord istnieje
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM rooms WHERE room_id = ?"
        cursor = db_controller.connection.execute(query, (room_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Pokój o ID {room_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania zależności: {e}") from e

def validate_meeting_date_format(date: str):
    """
    Waliduje format daty w polach `start_meeting_date` i `end_meeting_date`.

    Args:
        date (str): Data w formacie "YYYY-MM-DD HH:MM".

    Raises:
        ValueError: Jeśli format daty jest nieprawidłowy.

    Example:
        validate_meeting_date_format("2025-01-01 10:30")  # Brak błędu
        validate_meeting_date_format("01-01-2025 10:30")  # ValueError
    """
    if not re.fullmatch(r"^\d{4}-\d{2}-\d{2} [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$", date):
        raise ValueError("Data musi być w formacie 'YYYY-MM-DD HH:MM'.")

def validate_notes_length(notes: str):
    """
    Waliduje długość pola `notes`.

    Args:
        notes (str): Notatki.

    Raises:
        ValueError: Jeśli notatki przekraczają maksymalną długość.

    Example:
        validate_notes_length("Krótka notatka.")  # Brak błędu
        validate_notes_length("A" * 501)  # ValueError
    """
    if len(notes) > 500:
        raise ValueError("Notatki nie mogą przekraczać 500 znaków.")


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

    valid_columns = ["meeting_id", "fk_meeting_type_id", "fk_meeting_type_id", "start_meeting_date", "end_meeting_date",
                     "notes", "internal_meeting_status"]

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

    valid_columns = ["meeting_id", "fk_meeting_type_id", "fk_meeting_type_id", "start_meeting_date", "end_meeting_date",
                     "notes", "internal_meeting_status"]


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

