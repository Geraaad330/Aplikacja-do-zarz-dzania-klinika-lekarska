# patient_forms_model_validation.py

import re
import sqlite3
from controllers.database_controller import DatabaseController


def validate_submission_date(submission_date: str):
    """
    Waliduje format daty zgłoszenia (YYYY-MM-DD).

    Args:
        submission_date (str): Data zgłoszenia.

    Raises:
        ValueError: Jeśli data nie jest w poprawnym formacie.

    Example:
        validate_submission_date("2025-01-13")  # Brak błędu
        validate_submission_date("13-01-2025")  # ValueError
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, submission_date):
        raise ValueError(f"Nieprawidłowy format daty zgłoszenia: {submission_date}. Oczekiwany format: YYYY-MM-DD.")


def validate_fk_patient_id_exists(db_controller: DatabaseController, patient_id: int):
    """
    Sprawdza, czy podane `fk_patient_id` istnieje w tabeli `patients`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        patient_id (int): ID pacjenta.

    Raises:
        ValueError: Jeśli `fk_patient_id` nie istnieje.

    Example:
        validate_fk_patient_id_exists(db_controller, 1)  # Brak błędu
    """
    try:
        query = "SELECT COUNT(*) FROM patients WHERE patient_id = ?"
        cursor = db_controller.connection.execute(query, (patient_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Pacjent o ID {patient_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania istnienia pacjenta: {e}") from e


def validate_fk_form_type_id_exists(db_controller: DatabaseController, form_type_id: int):
    """
    Sprawdza, czy podane `fk_form_type_id` istnieje w tabeli `form_types`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        form_type_id (int): ID typu formularza.

    Raises:
        ValueError: Jeśli `fk_form_type_id` nie istnieje.

    Example:
        validate_fk_form_type_id_exists(db_controller, 1)  # Brak błędu
    """
    try:
        query = "SELECT COUNT(*) FROM form_types WHERE form_type_id = ?"
        cursor = db_controller.connection.execute(query, (form_type_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Typ formularza o ID {form_type_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania istnienia typu formularza: {e}") from e


def validate_non_nullable_fields(fk_patient_id, fk_form_type_id, submission_date):
    """
    Sprawdza, czy wymagane pola nie są `null`.

    Args:
        fk_patient_id (int | None): ID pacjenta.
        fk_form_type_id (int | None): ID typu formularza.
        submission_date (str | None): Data zgłoszenia.

    Raises:
        ValueError: Jeśli któreś z pól jest `null`.

    Example:
        validate_non_nullable_fields(1, 2, "2025-01-13")  # Brak błędu
        validate_non_nullable_fields(None, 2, "2025-01-13")  # ValueError
    """
    if fk_patient_id is None:
        raise ValueError("Pole `fk_patient_id` nie może być null.")
    if fk_form_type_id is None:
        raise ValueError("Pole `fk_form_type_id` nie może być null.")
    if submission_date is None:
        raise ValueError("Pole `submission_date` nie może być null.")


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

    valid_columns = ["patient_form_id", "fk_patient_id", "fk_form_type_id", "submission_date", "content"]

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

    valid_columns = ["patient_form_id", "fk_patient_id", "fk_form_type_id", "submission_date", "content"]

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