# test_appointments_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.patients_controller import PatientController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from models.appointments import Appointments
from validators.appointments_model_validation import (
    validate_appointment_status,
    validate_date_format,
    validate_fk_existence,
    validate_unique_room_date,
    validate_unique_patient_date,
    validate_update_fields,
    validate_operator_and_value,
    validate_filters_and_sorting
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
        "patients": PatientController(db_controller),
        "employees": EmployeesController(db_controller),
        "services": ServicesController(db_controller),
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller),
        "appointments": Appointments(db_controller)
    }

    # Tworzenie tabel w kontrolerach
    for controller in controllers.values():
        if hasattr(controller, "create_table") and callable(controller.create_table):
            controller.create_table()

    yield controllers

    # Czyszczenie danych testowych
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM services")
                db_controller.connection.execute("DELETE FROM rooms")
                db_controller.connection.execute("DELETE FROM appointments")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


def test_validate_appointment_status():
    """Testuje walidację pola `appointment_status`."""
    # Poprawne dane
    validate_appointment_status("Zarezerwowane")
    validate_appointment_status("Odwołane")
    validate_appointment_status("Planowana konsultacja")

    # Błędne dane
    with pytest.raises(ValueError, match="Status wizyty musi być ciągiem znaków."):
        validate_appointment_status(123)
    with pytest.raises(ValueError, match="Status wizyty musi mieć od 3 do 100 znaków."):
        validate_appointment_status("OK")
    with pytest.raises(ValueError, match="Status wizyty zawiera niedozwolone znaki."):
        validate_appointment_status("!!!@#")


def test_validate_date_format():
    """Testuje walidację pola `appointment_date`."""
    # Poprawne dane
    validate_date_format("2025-01-09 14:30")
    validate_date_format("2023-12-25 09:00")

    # Błędne dane
    with pytest.raises(ValueError, match="Wartość .* nie jest w formacie YYYY-MM-DD HH:MM."):
        validate_date_format("2025-01-09")
    with pytest.raises(ValueError, match="Wartość .* nie jest w formacie YYYY-MM-DD HH:MM."):
        validate_date_format("09-01-2025 14:30")


def test_validate_fk_existence(setup_controllers):

    db_controller = setup_controllers["db_controller"]
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]
    appointments_model = setup_controllers["appointments"]

    # Dodanie danych testowych
    room_type = room_types_controller.add_room_type("Gabinet")
    room = rooms_controller.add_room_by_name(11, 1, "Gabinet")
    patient = patients_controller.add_patient("Jan", "Kowalski", "98765432109", "555222333", "jan.kowalski@example.com", "Adres 2", "1980-02-02")
    employee = employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psychiatra", True)
    service = services_controller.add_service("Konsultacja", 30, 100)

    assert room_type is not None, "Typ pokoju nie został dodany."
    assert room is not None, "Pokój nie został dodany."
    assert patient is not None, "Pacjent nie został dodany."
    assert employee is not None, "Pracownik nie został dodany."
    assert service is not None, "Usługa nie została dodana."

    # Dodanie wizyty
    appointments_model.add_appointment(
        fk_patient_id=patient["patient_id"],
        fk_employee_id=employee["employee_id"],
        fk_service_id=service["service_id"],
        fk_room_id=room["room_id"],
        appointment_date="2025-01-09 14:30",
        appointment_status="Zarezerwowane",
        notes="Testowa wizyta"
    )



    # Test niepoprawnych danych
    with pytest.raises(ValueError, match="Pacjent o ID .* nie istnieje."):
        validate_fk_existence(db_controller, patient_id=999)
    with pytest.raises(ValueError, match="Pracownik o ID .* nie istnieje."):
        validate_fk_existence(db_controller, employee_id=999)
    with pytest.raises(ValueError, match="Usługa o ID .* nie istnieje."):
        validate_fk_existence(db_controller, service_id=999)
    with pytest.raises(ValueError, match="Pokój o ID .* nie istnieje."):
        validate_fk_existence(db_controller, room_id=999)


def test_validate_unique_room_date(setup_controllers):
    """Testuje unikalność `room_id` i `appointment_date` z użyciem modelu Appointments."""
    
    db_controller = setup_controllers["db_controller"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]
    appointments_model = setup_controllers["appointments"]

    # Dodanie typu pokoju
    room_type = room_types_controller.add_room_type("Gabinet")
    assert room_type is not None, "Typ pokoju nie został dodany."

    # Dodanie pokoju
    room = rooms_controller.add_room_by_name(11, 1, "Gabinet")
    assert room is not None, "Pokój nie został dodany."

    # Dodanie danych testowych do innych tabel
    patient = setup_controllers["patients"].add_patient("Jan", "Kowalski", "12345678901", "123456789", "jan@example.com", "Warszawa", "1990-01-01")
    employee = setup_controllers["employees"].add_employee("Anna", "Nowak", "anna@example.com", "987654321", "Psychoterapeuta", True)
    service = setup_controllers["services"].add_service("Konsultacja", 30, 100)

    # Dodanie wizyty
    appointments_model.add_appointment(
        fk_patient_id=patient["patient_id"],
        fk_employee_id=employee["employee_id"],
        fk_service_id=service["service_id"],
        fk_room_id=room["room_id"],
        appointment_date="2025-01-09 14:30",
        appointment_status="Zarezerwowane",
        notes="Testowa wizyta"
    )

    # Walidacja unikalności
    with pytest.raises(ValueError, match="Pokój o ID .* jest już zajęty w dniu .*"):
        validate_unique_room_date(db_controller, room["room_id"], "2025-01-09 14:30")


def test_validate_unique_patient_date(setup_controllers):
    """
    Testuje unikalność `patient_id` i `appointment_date` z użyciem modelu Appointments.
    """
    db_controller = setup_controllers["db_controller"]
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    room_types_controller = setup_controllers["room_types"]
    appointments_model = setup_controllers["appointments"]

    # Dodanie typu pokoju
    room_type = room_types_controller.add_room_type("Gabinet")
    assert room_type is not None, "Typ pokoju nie został poprawnie dodany."

    # Dodanie pokoju
    room = rooms_controller.add_room_by_name(11, 1, "Gabinet")
    assert room is not None, "Pokój nie został poprawnie dodany."

    # Dodanie pacjenta
    patient = patients_controller.add_patient("Jan", "Kowalski", "12345678901", "123456789", "jan@example.com", "Warszawa", "1990-01-01")
    assert patient is not None, "Pacjent nie został poprawnie dodany."

    # Dodanie pracownika
    employee = employees_controller.add_employee("Anna", "Nowak", "anna@example.com", "987654321", "Psychiatra", True)
    assert employee is not None, "Pracownik nie został poprawnie dodany."

    # Dodanie usługi
    service = services_controller.add_service("Konsultacja", 30, 100)
    assert service is not None, "Usługa nie została poprawnie dodana."

    # Dodanie wizyty
    appointments_model.add_appointment(
        fk_patient_id=patient["patient_id"],
        fk_employee_id=employee["employee_id"],
        fk_service_id=service["service_id"],
        fk_room_id=room["room_id"],
        appointment_date="2025-01-09 14:30",
        appointment_status="Zarezerwowane",
        notes="Testowa wizyta"
    )

    # Sprawdzenie unikalności
    with pytest.raises(ValueError, match="Pacjent o ID .* ma już wizytę w dniu .*"):
        validate_unique_patient_date(db_controller, patient["patient_id"], "2025-01-09 14:30")








def test_validate_operator_and_value():
    """
    Testuje walidację operatorów i wartości.
    """
    # Poprawne przypadki
    validate_operator_and_value("=", "Psychologia")
    validate_operator_and_value("LIKE", "Psych%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", [1, 2, 3])

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nieobsługiwany operator: <>."):
        validate_operator_and_value("<>")
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")
    with pytest.raises(ValueError, match="Operator BETWEEN wymaga krotki zawierającej dwie wartości."):
        validate_operator_and_value("BETWEEN", (1,))
    with pytest.raises(ValueError, match="Wartość dla operatora IN musi być niepustą listą lub krotką."):
        validate_operator_and_value("IN", [])


def test_validate_filters_and_sorting():
    """
    Testuje walidację filtrów i sortowania dla tabeli `appointments`.
    """
    valid_columns = [
        "appointment_id", "fk_patient_id", "fk_employee_id", "fk_service_id", 
        "fk_room_id", "appointment_date", "appointment_status", "notes"
    ]

    # Poprawne przypadki
    filters = [
        {"column": "appointment_status", "operator": "LIKE", "value": "Zarezerwowane%"},
        {"column": "fk_room_id", "operator": ">", "value": 1},
    ]
    sort_by = [{"column": "appointment_date", "direction": "ASC"}]

    # Walidacja powinna przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki

    # Niepoprawny filtr - brak klucza "value"
    filters = [{"column": "appointment_status", "operator": "LIKE"}]
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Niepoprawna kolumna
    filters = [{"column": "invalid_column", "operator": "LIKE", "value": "Zarezerwowane%"}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Nieobsługiwany operator
    filters = [{"column": "appointment_status", "operator": "INVALID", "value": "Zarezerwowane%"}]
    with pytest.raises(ValueError, match="Nieprawidłowy operator w filtrze: INVALID."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Niepoprawny sort_by - brak klucza "direction"
    sort_by = [{"column": "appointment_status"}]
    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

    # Niepoprawna kolumna w sortowaniu
    sort_by = [{"column": "invalid_column", "direction": "ASC"}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

    # Niepoprawny kierunek sortowania
    sort_by = [{"column": "appointment_status", "direction": "INVALID"}]
    with pytest.raises(ValueError, match="Nieprawidłowy kierunek sortowania: INVALID. Dozwolone wartości: 'ASC', 'DESC'."):
        validate_filters_and_sorting(None, sort_by, valid_columns)



def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji dla tabeli `appointments`.
    """
    valid_columns = [
        "appointment_id", "fk_patient_id", "fk_employee_id", "fk_service_id", 
        "fk_room_id", "appointment_date", "appointment_status", "notes"
    ]

    # Poprawne przypadki
    validate_update_fields({"appointment_status": "Zrealizowane"}, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "value"}, valid_columns)
