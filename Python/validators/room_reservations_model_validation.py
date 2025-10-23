# room_reservations_model_validation.py

import re
import sqlite3
from controllers.database_controller import DatabaseController


def validate_reservation_date(reservation_date: str):
    """
    Waliduje format daty rezerwacji (YYYY-MM-DD).

    Args:
        reservation_date (str): Data rezerwacji.

    Raises:
        ValueError: Jeśli data nie jest w poprawnym formacie.

    Example:
        validate_reservation_date("2025-01-01")  # Brak błędu
        validate_reservation_date("01-01-2025")  # ValueError
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, reservation_date):
        raise ValueError(f"Nieprawidłowy format daty rezerwacji: {reservation_date}. Oczekiwany format: YYYY-MM-DD.")


def validate_reservation_time(reservation_time: str):
    """
    Waliduje format czasu rezerwacji (H:MM-HH:MM lub HH:MM-HH:MM).

    Args:
        reservation_time (str): Czas rezerwacji.

    Raises:
        ValueError: Jeśli czas nie jest w poprawnym formacie.

    Example:
        validate_reservation_time("10:00-12:00")  # Brak błędu
        validate_reservation_time("8:00-9:00")    # Brak błędu
        validate_reservation_time("10:00")        # ValueError
    """
    pattern = r"^\d{1,2}:\d{2}-\d{1,2}:\d{2}$"
    if not re.match(pattern, reservation_time):
        raise ValueError(f"Nieprawidłowy format czasu rezerwacji: {reservation_time}. Oczekiwany format: H:MM-HH:MM.")


def validate_fk_room_id_exists(db_controller: DatabaseController, room_id: int):
    """
    Sprawdza, czy podane `fk_room_id` istnieje w tabeli `rooms`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        room_id (int): ID pokoju.

    Raises:
        ValueError: Jeśli `fk_room_id` nie istnieje.

    Example:
        validate_fk_room_id_exists(db_controller, 1)  # Brak błędu
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM rooms WHERE room_id = ?"
        cursor = db_controller.connection.execute(query, (room_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Pokój o ID {room_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania istnienia pokoju: {e}") from e

def validate_fk_appointment_id_exists(db_controller: DatabaseController, appointment_id: int):
    """
    Sprawdza, czy podane `fk_appointment_id` istnieje w tabeli `appointments`.

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        appointment_id (int): ID wizyty.

    Raises:
        ValueError: Jeśli `fk_appointment_id` nie istnieje.

    Example:
        validate_fk_appointment_id_exists(db_controller, 1)  # Brak błędu
    """
    try:
        if db_controller.connection is None:
            raise RuntimeError("Połączenie z bazą danych zostało zamknięte.")

        query = "SELECT COUNT(*) FROM appointments WHERE appointment_id = ?"
        cursor = db_controller.connection.execute(query, (appointment_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Wizyta o ID {appointment_id} nie istnieje.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Błąd podczas sprawdzania istnienia wizyty: {e}") from e

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


def validate_appointment_or_meeting(fk_appointment_id, fk_meeting_id):
    """
    Sprawdza, czy co najmniej jedno z pól `fk_appointment_id` lub `fk_meeting_id` nie jest `null`.

    Args:
        fk_appointment_id (int | None): ID wizyty, może być `null`.
        fk_meeting_id (int | None): ID spotkania, może być `null`.

    Raises:
        ValueError: Jeśli oba pola są `null` lub oba są różne od `null`.

    Example:
        validate_appointment_or_meeting(1, None)  # Brak błędu
        validate_appointment_or_meeting(None, 2)  # Brak błędu
        validate_appointment_or_meeting(None, None)  # ValueError
        validate_appointment_or_meeting(1, 2)  # ValueError
    """
    if fk_appointment_id is None and fk_meeting_id is None:
        raise ValueError(
            "Co najmniej jedno z pól `fk_appointment_id` lub `fk_meeting_id` musi być ustawione (nie null)."
        )
    if fk_appointment_id is not None and fk_meeting_id is not None:
        raise ValueError(
            "Oba pola `fk_appointment_id` i `fk_meeting_id` nie mogą być ustawione jednocześnie."
        )


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

    valid_columns = ["reservation_id", "fk_room_id", "reservation_date", "reservation_time", 
                     "fk_appointment_id", "fk_meeting_id"]

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

    valid_columns = ["reservation_id", "fk_room_id", "reservation_date", "reservation_time", 
                     "fk_appointment_id", "fk_meeting_id"]


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