# test_internal_meetings_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.meeting_types_controller import MeetingTypesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from validators.internal_meetings_model_validation import (
    validate_internal_meeting_status,
    validate_fk_meeting_type_exists,
    validate_fk_room_exists,
    validate_meeting_date_format,
    validate_notes_length,
    validate_operator_and_value,
    validate_filters_and_sorting,
    validate_update_fields,

)

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_database_fixture():
    """
    Fixture konfigurujący testową bazę danych SQLite3.
    Tworzy wymaganą tabelę i zapewnia czyste środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "db_controller": db_controller,
        "meeting_types": MeetingTypesController(db_controller),
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller),
    }

    # Tworzenie tabel
    for controller in controllers.values():
        if hasattr(controller, "create_table") and callable(controller.create_table):
            controller.create_table()

    yield controllers

    # Czyszczenie danych testowych
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM meeting_types")
                db_controller.connection.execute("DELETE FROM rooms")
                db_controller.connection.execute("DELETE FROM room_types")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


def test_validate_internal_meeting_status():
    """
    Testuje walidację `internal_meeting_status`.
    """
    # Poprawne dane
    validate_internal_meeting_status("Zaplanowane")
    validate_internal_meeting_status("Zakończone")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowy status spotkania: .*"):
        validate_internal_meeting_status("Nieznany")
    with pytest.raises(ValueError, match="Nieprawidłowy status spotkania: .*"):
        validate_internal_meeting_status("")

def test_validate_fk_meeting_type_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_meeting_type_id` w tabeli `meeting_types`.
    """
    db_controller = setup_controllers["db_controller"]
    meeting_types_controller = setup_controllers["meeting_types"]

    # Dodanie danych
    meeting_types_controller.add_meeting_type("Planowanie")

    # Pobranie ID
    meeting_type_id = db_controller.connection.execute(
        "SELECT meeting_type_id FROM meeting_types"
    ).fetchone()["meeting_type_id"]

    # Poprawne dane
    validate_fk_meeting_type_exists(db_controller, meeting_type_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Typ spotkania o ID .* nie istnieje."):
        validate_fk_meeting_type_exists(db_controller, 999)


def test_validate_fk_room_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_room_id` w tabeli `rooms`.
    """
    db_controller = setup_controllers["db_controller"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]

    room_types_controller.add_room_type("Gabinet")

    # Dodanie danych
    rooms_controller.add_room_by_name(11, 1, "Gabinet")

    # Pobranie ID
    room_id = db_controller.connection.execute(
        "SELECT room_id FROM rooms"
    ).fetchone()["room_id"]

    # Poprawne dane
    validate_fk_room_exists(db_controller, room_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Pokój o ID .* nie istnieje."):
        validate_fk_room_exists(db_controller, 999)


def test_validate_meeting_date_format():
    """
    Testuje walidację `start_meeting_date` i `end_meeting_date`.
    """
    # Poprawne dane
    validate_meeting_date_format("2025-01-01 10:30")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Data musi być w formacie 'YYYY-MM-DD HH:MM'."):
        validate_meeting_date_format("01-01-2025 10:30")
    with pytest.raises(ValueError, match="Data musi być w formacie 'YYYY-MM-DD HH:MM'."):
        validate_meeting_date_format("2025/01/01 10:30")
    with pytest.raises(ValueError, match="Data musi być w formacie 'YYYY-MM-DD HH:MM'."):
        validate_meeting_date_format("2025-01-01")


def test_validate_notes_length():
    """
    Testuje walidację długości pola `notes`.
    """
    # Poprawne dane
    validate_notes_length("Krótka notatka.")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Notatki nie mogą przekraczać 500 znaków."):
        validate_notes_length("A" * 501)











def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """
    valid_columns = ["meeting_id", "fk_meeting_type_id", "fk_meeting_type_id", "start_meeting_date", "end_meeting_date",
                     "notes", "internal_meeting_status"]

    # Poprawne dane
    validate_update_fields({"meeting_id": "Nowy opis"}, valid_columns)
    validate_update_fields({"fk_meeting_type_id": "A01.0"}, valid_columns)
    validate_update_fields({"fk_meeting_type_id": 123}, valid_columns)
    validate_update_fields({"start_meeting_date": "Nowy opis"}, valid_columns)
    validate_update_fields({"end_meeting_date": "A01.0"}, valid_columns)
    validate_update_fields({"notes": 123}, valid_columns)
    validate_update_fields({"internal_meeting_status": 123}, valid_columns)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "wartość"}, valid_columns)


def test_validate_operator_and_value():
    """
    Testuje walidację operatorów i wartości w zapytaniach SQL.
    """
    # Poprawne przypadki
    validate_operator_and_value("=", "Opis diagnozy")
    validate_operator_and_value("LIKE", "Opis%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", [1, 2, 3])
    validate_operator_and_value("IS NULL", None)
    validate_operator_and_value("IS NOT NULL", None)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nieobsługiwany operator: <>."):
        validate_operator_and_value("<>", "Niepoprawny operator")

    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")

    with pytest.raises(ValueError, match="Operator BETWEEN wymaga krotki zawierającej dwie wartości."):
        validate_operator_and_value("BETWEEN", (1,))

    with pytest.raises(ValueError, match="Wartość dla operatora IN musi być niepustą listą lub krotką."):
        validate_operator_and_value("IN", [])


def test_validate_filters_and_sorting():
    """
    Testuje walidację filtrów i sortowania w zapytaniach SQL.
    """
    valid_columns = ["meeting_id", "fk_meeting_type_id", "fk_meeting_type_id", "start_meeting_date", "end_meeting_date",
                     "notes", "internal_meeting_status"]

    # Poprawne dane
    filters = [
        {"column": "meeting_id", "operator": "LIKE", "value": "Opis%"},
        {"column": "fk_meeting_type_id", "operator": ">", "value": 1},
        {"column": "fk_meeting_type_id", "operator": "=", "value": "A01.0"},
        {"column": "start_meeting_date", "operator": "!=", "value": "Błąd opisu"},
        {"column": "end_meeting_date", "operator": "=", "value": "A01.0"},
        {"column": "notes", "operator": "!=", "value": "Błąd opisu"},
        {"column": "internal_meeting_status", "operator": "!=", "value": "Błąd opisu"},
    ]
    sort_by = [
        {"column": "fk_meeting_type_id", "direction": "ASC"},
        {"column": "internal_meeting_status", "direction": "DESC"},
    ]

    # Powinno przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting([{"column": "description", "operator": "LIKE"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting([{"column": "invalid_column", "operator": "LIKE", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: description. Dozwolone kolumny: meeting_id, fk_meeting_type_id, fk_meeting_type_id, start_meeting_date, end_meeting_date, notes, internal_meeting_status"):
        validate_filters_and_sorting([{"column": "description", "operator": "INVALID", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, [{"column": "description"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, [{"column": "invalid_column", "direction": "ASC"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: description. Dozwolone kolumny: meeting_id, fk_meeting_type_id, fk_meeting_type_id, start_meeting_date, end_meeting_date, notes, internal_meeting_status"):
        validate_filters_and_sorting(None, [{"column": "description", "direction": "INVALID"}], valid_columns)