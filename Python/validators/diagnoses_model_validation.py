# diagnoses_model_validation.py

import re
import sqlite3
from controllers.database_controller import DatabaseController


def validate_description(description: str) -> None:
    """
    Waliduje pole `description`.

    Args:
        description (str): Opis diagnozy.

    Raises:
        ValueError: Jeśli wartość jest nieprawidłowa lub pusta.

    Przykład:
        validate_description("Grypa sezonowa")  # Brak błędu
        validate_description("")  # ValueError
    """
    if not description or not description.strip():
        raise ValueError("Opis nie może być pusty.")
    
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż \(\)\-\:\.\,\/\\]+$"
    if not isinstance(description, str):
        raise ValueError("Opis musi być ciągiem znaków.")
    if not description or not description.strip():
        raise ValueError("Opis nie może być pusty.")
    if not 3 <= len(description) <= 100:
        raise ValueError("Opis musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, description):
        raise ValueError("Opis zawiera niedozwolone znaki.")
    if any(char.isdigit() for char in description):
        raise ValueError("Opis nie może zawierać cyfr.")


def validate_icd11_code(icd11_code: str) -> None:
    """
    Waliduje pole `icd11_code`.

    Args:
        icd11_code (str): Kod ICD-11.

    Raises:
        ValueError: Jeśli kod jest nieprawidłowy lub pusty.

    Przykład:
        validate_icd11_code("A01.0")  # Brak błędu
        validate_icd11_code("")  # ValueError
    """
    if not icd11_code or not icd11_code.strip():
        raise ValueError("Kod ICD-11 nie może być pusty.")
    
    pattern = r"^[A-Z0-9]{1,2}[A-Z0-9]{1}\d{2}(\.[A-Z0-9]{1,2})?$"
    if not isinstance(icd11_code, str):
        raise ValueError("Kod ICD-11 musi być ciągiem znaków.")
    if not icd11_code or not icd11_code.strip():
        raise ValueError("Kod ICD-11 nie może być pusty.")
    if not re.fullmatch(pattern, icd11_code):
        raise ValueError("Kod ICD-11 jest nieprawidłowy.")


def validate_fk_appointment_exists(db_controller: DatabaseController, appointment_id: int) -> None:
    """
    Sprawdza, czy podane `appointment_id` istnieje w tabeli `appointments`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        appointment_id (int): ID wizyty.

    Raises:
        ValueError: Jeśli `appointment_id` nie istnieje.
        RuntimeError: Jeśli połączenie z bazą danych jest zamknięte.
    """
    try:
        # Upewnienie się, że połączenie z bazą danych jest aktywne
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM appointments WHERE appointment_id = ?"
        cursor = db_controller.connection.execute(query, (appointment_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Wizyta o ID {appointment_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania zależności: {e}") from e


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

    valid_columns = ["diagnosis_id", "appointment_id", "description", "icd11_code"]

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

    valid_columns = ["diagnosis_id", "appointment_id", "description", "icd11_code"]

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

