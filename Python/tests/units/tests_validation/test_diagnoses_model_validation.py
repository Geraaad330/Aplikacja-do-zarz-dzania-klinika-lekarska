# test_diagnoses_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.appointments_controller import AppointmentsController
from models.diagnoses import Diagnoses
from controllers.patients_controller import PatientController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from validators.diagnoses_model_validation import (
    validate_description,
    validate_icd11_code,
    validate_fk_appointment_exists,
    validate_update_fields,
    validate_filters_and_sorting,
    validate_operator_and_value,
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
        "Diagnoses": Diagnoses(db_controller),
        "appointments": AppointmentsController(db_controller),
        "room_types": RoomTypesController(db_controller),
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


def test_validate_description():
    """
    Testuje walidację opisu diagnozy (`description`).
    """
    # Poprawne dane
    validate_description("Grypa sezonowa")
    validate_description("Zapalenie płuc (ostra faza)")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Opis nie może być pusty."):
        validate_description("")
    with pytest.raises(ValueError, match="Opis nie może być pusty."):
        validate_description(None)
    with pytest.raises(ValueError, match="Opis musi mieć od 3 do 100 znaków."):
        validate_description("AB")
    with pytest.raises(ValueError, match="Opis zawiera niedozwolone znaki."):
        validate_description("Opis!@#")
    with pytest.raises(ValueError, match="Opis zawiera niedozwolone znaki."):
        validate_description("Zapalenie płuc 2023")

def test_validate_icd11_code():
    """
    Testuje walidację kodu ICD-11 (`icd11_code`).
    """
    # Poprawne dane
    validate_icd11_code("A01.0")
    validate_icd11_code("B23")
    validate_icd11_code("C45.1")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Kod ICD-11 nie może być pusty."):
        validate_icd11_code("")
    with pytest.raises(ValueError, match="Kod ICD-11 nie może być pusty."):
        validate_icd11_code(None)
    with pytest.raises(ValueError, match="Kod ICD-11 jest nieprawidłowy."):
        validate_icd11_code("A01-1")
    with pytest.raises(ValueError, match="Kod ICD-11 jest nieprawidłowy."):
        validate_icd11_code("123")
    with pytest.raises(ValueError, match="Kod ICD-11 jest nieprawidłowy."):
        validate_icd11_code("AB123")

def test_validate_fk_appointment_exists(setup_controllers):
    """
    Testuje walidację istnienia `appointment_id` w tabeli `appointments`.
    """
    db_controller = setup_controllers["db_controller"]
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodaj dane do tabeli patients
    patient_id = patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )["patient_id"]

    # Dodaj dane do tabeli employees
    employee_id = employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    service_id = services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )["service_id"]

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    room_id = rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )["room_id"]

    # Dodaj dane do tabeli appointments
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-01 12:00",
        appointment_status="Zarezerwowane"
    )


    # Pobranie ID dodanej wizyty
    appointment_id = appointments_controller.get_appointments()[0]["appointment_id"]

    # Poprawne dane
    validate_fk_appointment_exists(db_controller, appointment_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Wizyta o ID 999 nie istnieje."):
        validate_fk_appointment_exists(db_controller, 999)





def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """
    valid_columns = ["appointment_id", "description", "icd11_code"]

    # Poprawne dane
    validate_update_fields({"description": "Nowy opis"}, valid_columns)
    validate_update_fields({"icd11_code": "A01.0"}, valid_columns)
    validate_update_fields({"appointment_id": 123}, valid_columns)

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
    valid_columns = ["appointment_id", "description", "icd11_code"]

    # Poprawne dane
    filters = [
        {"column": "description", "operator": "LIKE", "value": "Opis%"},
        {"column": "appointment_id", "operator": ">", "value": 1},
        {"column": "icd11_code", "operator": "=", "value": "A01.0"},
        {"column": "description", "operator": "!=", "value": "Błąd opisu"}
    ]
    sort_by = [
        {"column": "icd11_code", "direction": "ASC"},
        {"column": "description", "direction": "DESC"},
    ]

    # Powinno przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting([{"column": "description", "operator": "LIKE"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting([{"column": "invalid_column", "operator": "LIKE", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowy operator w filtrze: INVALID."):
        validate_filters_and_sorting([{"column": "description", "operator": "INVALID", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, [{"column": "description"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, [{"column": "invalid_column", "direction": "ASC"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowy kierunek sortowania: INVALID."):
        validate_filters_and_sorting(None, [{"column": "description", "direction": "INVALID"}], valid_columns)