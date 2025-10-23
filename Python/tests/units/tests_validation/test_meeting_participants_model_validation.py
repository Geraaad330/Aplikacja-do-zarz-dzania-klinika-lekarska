# test_meeting_participants_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.internal_meetings_controller import InternalMeetingsController
from controllers.employees_controller import EmployeesController
from controllers.meeting_types_controller import MeetingTypesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from validators.meeting_participants_model_validation import (
    validate_attendance,
    validate_participant_role,
    validate_fk_meeting_id_exists,
    validate_fk_employee_id_exists,
    validate_filters_and_sorting,
    validate_operator_and_value,
    validate_update_fields
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
        "internal_meetings": InternalMeetingsController(db_controller),
        "employees": EmployeesController(db_controller),
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
                db_controller.connection.execute("DELETE FROM internal_meetings")
                db_controller.connection.execute("DELETE FROM employees")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


def test_validate_attendance():
    """
    Testuje walidację `attendance`.
    """
    # Poprawne dane
    validate_attendance("Obecny")
    validate_attendance("Nieobecny")
    validate_attendance("Usprawiedliwiony")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowa wartość `attendance`: .*"):
        validate_attendance("Nieznany")
    with pytest.raises(ValueError, match="Nieprawidłowa wartość `attendance`: .*"):
        validate_attendance("")

def test_validate_participant_role():
    """
    Testuje walidację `participant_role`.
    """
    # Poprawne dane
    validate_participant_role("Organizator")
    validate_participant_role("Uczestnik")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowa rola uczestnika: .*"):
        validate_participant_role("Nieznany")
    with pytest.raises(ValueError, match="Nieprawidłowa rola uczestnika: .*"):
        validate_participant_role("")

def test_validate_fk_meeting_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_meeting_id` w tabeli `internal_meetings`.
    """
    db_controller = setup_controllers["db_controller"]
    internal_meetings_controller = setup_controllers["internal_meetings"]
    meeting_types_controller = setup_controllers["meeting_types"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]

    room_types_controller.add_room_type("Gabinet")

    # Dodanie danych
    rooms_controller.add_room_by_name(11, 1, "Gabinet")


    # Dodanie danych
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie danych
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=1,
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 11:00",
        notes="Spotkanie testowe",
        internal_meeting_status="Zaplanowane",
    )
    meeting_id = meeting["meeting_id"]

    # Poprawne dane
    validate_fk_meeting_id_exists(db_controller, meeting_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Spotkanie o ID .* nie istnieje."):
        validate_fk_meeting_id_exists(db_controller, 999)

def test_validate_fk_employee_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_employee_id` w tabeli `employees`.
    """
    db_controller = setup_controllers["db_controller"]
    employees_controller = setup_controllers["employees"]

    # Dodanie danych
    employee_id = employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Psychiatra",
        is_medical_staff=False,
    )

    # Poprawne dane
    validate_fk_employee_id_exists(db_controller, employee_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Pracownik o ID .* nie istnieje."):
        validate_fk_employee_id_exists(db_controller, 999)




def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """

    valid_columns = ["participant_id", "fk_meeting_id", "fk_employee_id", "participant_role", "attendance"]


    # Poprawne dane
    validate_update_fields({"participant_id": "Nowy opis"}, valid_columns)
    validate_update_fields({"fk_meeting_id": "A01.0"}, valid_columns)
    validate_update_fields({"fk_employee_id": 123}, valid_columns)
    validate_update_fields({"participant_role": "Nowy opis"}, valid_columns)
    validate_update_fields({"attendance": "A01.0"}, valid_columns)

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

    valid_columns = ["participant_id", "fk_meeting_id", "fk_employee_id", "participant_role", "attendance"]

    # Poprawne dane
    filters = [
        {"column": "participant_id", "operator": "LIKE", "value": "Opis%"},
        {"column": "fk_meeting_id", "operator": ">", "value": 1},
        {"column": "fk_employee_id", "operator": "=", "value": "A01.0"},
        {"column": "participant_role", "operator": "!=", "value": "Błąd opisu"},
        {"column": "attendance", "operator": "=", "value": "A01.0"},
    ]
    sort_by = [
        {"column": "fk_meeting_id", "direction": "ASC"},
        {"column": "participant_role", "direction": "DESC"},
    ]

    # Powinno przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting([{"column": "description", "operator": "LIKE"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting([{"column": "invalid_column", "operator": "LIKE", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: description. Dozwolone kolumny: participant_id, fk_meeting_id, fk_employee_id, participant_role, attendance"):
        validate_filters_and_sorting([{"column": "description", "operator": "INVALID", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, [{"column": "description"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, [{"column": "invalid_column", "direction": "ASC"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: description. Dozwolone kolumny: participant_id, fk_meeting_id, fk_employee_id, participant_role, attendance"):
        validate_filters_and_sorting(None, [{"column": "description", "direction": "INVALID"}], valid_columns)