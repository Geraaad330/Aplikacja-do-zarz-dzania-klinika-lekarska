# appointments_model_validation.py

import re
# from datetime import datetime
from controllers.database_controller import DatabaseController


def validate_appointment_status(status: str) -> None:
    """
    Waliduje pole `appointment_status`.

    :param status: Status wizyty.
    :raises ValueError: Jeśli status nie spełnia wymagań.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s\(\)\-\:\.\,\/\\]+$"
    if not isinstance(status, str):
        raise ValueError("Status wizyty musi być ciągiem znaków.")
    if not 3 <= len(status) <= 100:
        raise ValueError("Status wizyty musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, status):
        raise ValueError("Status wizyty zawiera niedozwolone znaki.")
    if any(char.isdigit() for char in status):
        raise ValueError("Status wizyty nie może zawierać cyfr.")


# def validate_date_format(date_value: str) -> None:
#     """
#     Waliduje pole `appointment_date` w formacie `YYYY-MM-DD HH:MM`.

#     :param date_value: Wartość daty do walidacji.
#     :raises ValueError: Jeśli wartość nie jest poprawna.
#     """
#     if not isinstance(date_value, str):
#         raise ValueError("Data wizyty musi być ciągiem znaków.")
#     try:
#         datetime.strptime(date_value, "%Y-%m-%d %H:%M")
#     except ValueError as e:
#         raise ValueError("Niepoprawny format daty wizyty.") from e


def validate_date_format(date_value: str) -> None:
    """
    Waliduje pole `appointment_date`, przyjmując wyłącznie format `YYYY-MM-DD HH:MM-HH:MM`.

    :param date_value: Wartość daty do walidacji.
    :raises ValueError: Jeśli wartość nie jest zgodna z oczekiwanym formatem.
    """
    if not isinstance(date_value, str):
        raise ValueError("Data wizyty musi być ciągiem znaków.")

    # Wyrażenie regularne dla formatu YYYY-MM-DD HH:MM-HH:MM
    pattern = r"^\d{4}-\d{2}-\d{2} [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$"

    if not re.match(pattern, date_value):
        raise ValueError("Niepoprawny format daty wizyty. Oczekiwany format: YYYY-MM-DD HH:MM-HH:MM")







def validate_unique_room_date(db_controller: DatabaseController, room_id: int, appointment_date: str) -> None:
    """
    Waliduje unikalność kombinacji (fk_room_id, appointment_date).
    """
    query = """
    SELECT COUNT(*) FROM appointments
    WHERE fk_room_id = ? AND appointment_date = ?
    """
    cursor = db_controller.connection.execute(query, (room_id, appointment_date))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Pokój o ID {room_id} jest już zajęty w dniu {appointment_date}.")




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

