# prescriptions_model_validation.py

import re
import sqlite3
from controllers.database_controller import DatabaseController



def validate_medicine_name(medicine_name: str) -> None:
    """
    Waliduje pole `medicine_name`.

    Args:
        medicine_name (str): Nazwa leku.

    Raises:
        ValueError: Jeśli wartość jest nieprawidłowa, pusta, zawiera niedozwolone znaki lub nie spełnia wymagań długości.

    Przykład:
        validate_medicine_name("Paracetamol")  # Brak błędu
        validate_medicine_name("123")  # ValueError
    """
    if not isinstance(medicine_name, str) or not medicine_name.strip():
        raise ValueError("Nazwa leku musi być niepustym ciągiem znaków.")
    if not 3 <= len(medicine_name) <= 100:
        raise ValueError("Nazwa leku musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(r"^[A-Za-z ]+$", medicine_name):
        raise ValueError("Nazwa leku może zawierać tylko litery i spacje.")


def validate_fk_appointment_exists(db_controller: DatabaseController, appointment_id: int) -> None:
    """
    Sprawdza, czy podane `appointment_id` istnieje w tabeli `appointments`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        appointment_id (int): ID wizyty.

    Raises:
        ValueError: Jeśli `appointment_id` nie istnieje.
        RuntimeError: Jeśli połączenie z bazą danych jest zamknięte.

    Przykład:
        validate_fk_appointment_exists(db_controller, 1)  # Brak błędu, jeśli rekord istnieje
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM appointments WHERE appointment_id = ?"
        cursor = db_controller.connection.execute(query, (appointment_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Wizyta o ID {appointment_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania zależności: {e}") from e


def validate_dosage(dosage: float) -> None:
    """
    Waliduje pole `dosage`.

    Args:
        dosage (float): Dawka leku.

    Raises:
        ValueError: Jeśli dawka jest nieprawidłowa.

    Przykład:
        validate_dosage(500.0)  # Brak błędu
        validate_dosage(0)  # ValueError
    """
    if not isinstance(dosage, (int, float)) or dosage <= 0 or dosage > 10000:
        raise ValueError("Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000.")


def validate_medicine_price(medicine_price: float) -> None:
    """
    Waliduje pole `medicine_price`.

    Args:
        medicine_price (float): Cena leku.

    Raises:
        ValueError: Jeśli cena jest nieprawidłowa.

    Przykład:
        validate_medicine_price(10.99)  # Brak błędu
        validate_medicine_price(-5)  # ValueError
    """
    if not isinstance(medicine_price, (int, float)) or medicine_price <= 0:
        raise ValueError("Cena leku musi być liczbą większą niż 0.")


def validate_prescription_code(prescription_code: str) -> None:
    """
    Waliduje pole `prescription_code`.

    Args:
        prescription_code (str): Kod recepty.

    Raises:
        ValueError: Jeśli kod jest nieprawidłowy.

    Przykład:
        validate_prescription_code("1234")  # Brak błędu
        validate_prescription_code("12A4")  # ValueError
    """
    if not isinstance(prescription_code, str) or not re.fullmatch(r"^\d{4}$", prescription_code):
        raise ValueError("Kod recepty musi składać się dokładnie z 4 cyfr.")


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

    valid_columns = ["prescription_id", "appointment_id", "medicine_name", "dosage", "medicine_price", "prescription_code"]

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

    valid_columns = ["prescription_id", "appointment_id", "medicine_name", "dosage", "medicine_price", "prescription_code"]


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

