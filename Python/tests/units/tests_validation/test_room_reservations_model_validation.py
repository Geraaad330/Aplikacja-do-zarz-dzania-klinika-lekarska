# test_room_reservations_model_validation.py

import os
import pytest
import sqlite3
from controllers.internal_meetings_controller import InternalMeetingsController
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.meeting_types_controller import MeetingTypesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from controllers.meeting_participants_controller import MeetingParticipantsController
from controllers.appointments_controller import AppointmentsController
from controllers.patients_controller import PatientController
from controllers.services_controller import ServicesController

#pylint: disable=E0401
#pylint: disable=E0611
from validators.room_reservations_model_validation import (
    validate_reservation_date,
    validate_reservation_time,
    validate_fk_room_id_exists,
    validate_fk_appointment_id_exists,
    validate_fk_meeting_id_exists,
    validate_appointment_or_meeting,
    validate_filters_and_sorting,
    validate_operator_and_value,
    validate_update_fields
)

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Fixture konfigurujący testową bazę danych SQLite3.
    Tworzy wymagane tabele i zapewnia czyste środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "db_controller": db_controller,
        "internal_meetings": InternalMeetingsController(db_controller),
        "meeting_types": MeetingTypesController(db_controller),
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller),
        "meeting_participants": MeetingParticipantsController(db_controller),
        "employees": EmployeesController(db_controller),
        "appointments": AppointmentsController(db_controller),
        "patients": PatientController(db_controller),
        "services": ServicesController(db_controller),
    }

    # Tworzenie tabel
    for controller in controllers.values():
        if hasattr(controller, "create_table"):
            controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM internal_meetings")
                db_controller.connection.execute("DELETE FROM meeting_types")
                db_controller.connection.execute("DELETE FROM rooms")
                db_controller.connection.execute("DELETE FROM room_types")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()

def test_validate_reservation_date():
    """
    Testuje walidację formatu daty rezerwacji.
    """
    # Poprawne dane
    validate_reservation_date("2025-01-01")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowy format daty rezerwacji: .*"):
        validate_reservation_date("01-01-2025")
    with pytest.raises(ValueError, match="Nieprawidłowy format daty rezerwacji: .*"):
        validate_reservation_date("2025/01/01")
    with pytest.raises(ValueError, match="Nieprawidłowy format daty rezerwacji: .*"):
        validate_reservation_date("")


def test_validate_reservation_time():
    """
    Testuje walidację formatu czasu rezerwacji.
    """
    # Poprawne dane
    validate_reservation_time("10:00-12:00")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowy format czasu rezerwacji: .*"):
        validate_reservation_time("10:00")
    with pytest.raises(ValueError, match="Nieprawidłowy format czasu rezerwacji: .*"):
        validate_reservation_time("10:00-12")
    with pytest.raises(ValueError, match="Nieprawidłowy format czasu rezerwacji: .*"):
        validate_reservation_time("")


def test_validate_fk_room_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_room_id` w tabeli `rooms`.
    """
    db_controller = setup_controllers["db_controller"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]

    room_types_controller.add_room_type("Gabinet psychiatryczny")

    # Dodanie pokoju
    room = rooms_controller.add_room_by_name(1, 1, "Gabinet psychiatryczny")  # Zwraca obiekt `sqlite3.Row`
    room_id = room["room_id"]  # Wyciągnięcie ID pokoju

    # Poprawne dane
    validate_fk_room_id_exists(db_controller, room_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Pokój o ID .* nie istnieje."):
        validate_fk_room_id_exists(db_controller, 999)


def test_validate_fk_appointment_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_appointment_id` w tabeli `appointments`.
    """
    db_controller = setup_controllers["db_controller"]
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]
    appointments_controller = setup_controllers["appointments"]

    # Dodanie danych testowych
    room_types_controller.add_room_type("Gabinet")
    room = rooms_controller.add_room_by_name(11, 1, "Gabinet")  # Zwraca obiekt `sqlite3.Row`
    room_id = room["room_id"]  # Ekstrakcja ID pokoju

    patient = patients_controller.add_patient(
        "Jan", "Kowalski", "98765432109", "555222333",
        "jan.kowalski@example.com", "Adres 2", "1980-02-02"
    )  # Zwraca obiekt `sqlite3.Row`
    patient_id = patient["patient_id"]  # Ekstrakcja ID pacjenta

    employee_id = employees_controller.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psychiatra", True
    )  # Zwraca ID jako `int`

    service = services_controller.add_service("Konsultacja", 30, 100)  # Zwraca obiekt `sqlite3.Row`
    service_id = service["service_id"]  # Ekstrakcja ID usługi

    # Dodanie wizyty
    appointment = appointments_controller.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 14:30",
        appointment_status="Zarezerwowane",
        notes="Testowa wizyta"
    )
    appointment_id = appointment["appointment_id"]  # Ekstrakcja ID wizyty

    # Poprawne dane
    validate_fk_appointment_id_exists(db_controller, appointment_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Wizyta o ID .* nie istnieje."):
        validate_fk_appointment_id_exists(db_controller, 999)




def test_validate_fk_meeting_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_meeting_id` w tabeli `internal_meetings`.
    """
    db_controller = setup_controllers["db_controller"]
    internal_meetings_controller = setup_controllers["internal_meetings"]
    meeting_types_controller = setup_controllers["meeting_types"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_room_id=1,
        fk_meeting_type_id=1,
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 11:00",
        notes="Spotkanie testowe",
        internal_meeting_status="Zaplanowane",
    )
    meeting_id = meeting["meeting_id"]  # Wyciągnięcie ID spotkania


    # Poprawne dane
    validate_fk_meeting_id_exists(db_controller, meeting_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Spotkanie o ID .* nie istnieje."):
        validate_fk_meeting_id_exists(db_controller, 999)


def test_validate_appointment_or_meeting():
    """
    Testuje walidację zależności między `fk_appointment_id` i `fk_meeting_id`.
    """
    # Poprawne przypadki
    validate_appointment_or_meeting(1, None)  # Tylko `fk_appointment_id` ustawione
    validate_appointment_or_meeting(None, 2)  # Tylko `fk_meeting_id` ustawione

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Co najmniej jedno z pól `fk_appointment_id` lub `fk_meeting_id` musi być ustawione.*"):
        validate_appointment_or_meeting(None, None)  # Oba pola są null

    with pytest.raises(ValueError, match="Oba pola `fk_appointment_id` i `fk_meeting_id` nie mogą być ustawione jednocześnie.*"):
        validate_appointment_or_meeting(1, 2)  # Oba pola są ustawione

    # Graniczne przypadki
    with pytest.raises(ValueError, match="Co najmniej jedno z pól `fk_appointment_id` lub `fk_meeting_id` musi być ustawione.*"):
        validate_appointment_or_meeting(None, None)

    validate_appointment_or_meeting(0, None)  # Przypadek gdy `fk_appointment_id` jest 0
    validate_appointment_or_meeting(None, 0)  # Przypadek gdy `fk_meeting_id` jest 0


# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """
    valid_columns = ["reservation_id", "fk_room_id", "reservation_date", "reservation_time", 
                     "fk_appointment_id", "fk_meeting_id"]
    # Poprawne dane
    validate_update_fields({"reservation_id": "Nowy opis"}, valid_columns)
    validate_update_fields({"fk_room_id": "A01.0"}, valid_columns)
    validate_update_fields({"reservation_date": 123}, valid_columns)
    validate_update_fields({"reservation_time": "Nowy opis"}, valid_columns)
    validate_update_fields({"fk_appointment_id": "A01.0"}, valid_columns)
    validate_update_fields({"fk_meeting_id": 123}, valid_columns)


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
    valid_columns = ["reservation_id", "fk_room_id", "reservation_date", "reservation_time", 
                     "fk_appointment_id", "fk_meeting_id"]

    # Poprawne dane
    filters = [
        {"column": "reservation_id", "operator": "LIKE", "value": "Opis%"},
        {"column": "fk_room_id", "operator": ">", "value": 1},
        {"column": "reservation_date", "operator": "=", "value": "A01.0"},
        {"column": "reservation_time", "operator": "!=", "value": "Błąd opisu"},
        {"column": "fk_appointment_id", "operator": "=", "value": "A01.0"},
        {"column": "fk_meeting_id", "operator": "!=", "value": "Błąd opisu"},
    ]
    sort_by = [
        {"column": "fk_room_id", "direction": "ASC"},
        {"column": "reservation_time", "direction": "DESC"},
    ]

    # Powinno przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting([{"column": "description", "operator": "LIKE"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting([{"column": "invalid_column", "operator": "LIKE", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: description. Dozwolone kolumny: reservation_id, fk_room_id, reservation_date, reservation_time, fk_appointment_id, fk_meeting_id"):
        validate_filters_and_sorting([{"column": "description", "operator": "INVALID", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, [{"column": "description"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, [{"column": "invalid_column", "direction": "ASC"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: description. Dozwolone kolumny: reservation_id, fk_room_id, reservation_date, reservation_time, fk_appointment_id, fk_meeting_id"):
        validate_filters_and_sorting(None, [{"column": "description", "direction": "INVALID"}], valid_columns)