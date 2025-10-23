# test_prescriptions_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.patients_controller import PatientController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.rooms_controller import RoomsController
from controllers.diagnoses_controller import DiagnosesController
from controllers.appointments_controller import AppointmentsController
from controllers.room_types_controller import RoomTypesController
from validators.prescriptions_model_validation import (
    validate_medicine_name,
    validate_fk_appointment_exists,
    validate_dosage,
    validate_medicine_price,
    validate_prescription_code,
    validate_update_fields,
    validate_operator_and_value,
    validate_filters_and_sorting
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
        "patients": PatientController(db_controller),
        "employees": EmployeesController(db_controller),
        "services": ServicesController(db_controller),
        "rooms": RoomsController(db_controller),
        "Diagnoses": DiagnosesController(db_controller),
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


def test_validate_medicine_name():
    """
    Testuje walidację `medicine_name`.
    """
    # Poprawne dane
    validate_medicine_name("Paracetamol")
    validate_medicine_name("Aspirin")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa leku musi być niepustym ciągiem znaków."):
        validate_medicine_name("")
    with pytest.raises(ValueError, match="Nazwa leku musi być niepustym ciągiem znaków."):
        validate_medicine_name(None)
    with pytest.raises(ValueError, match="Nazwa leku musi mieć od 3 do 100 znaków."):
        validate_medicine_name("AB")
    with pytest.raises(ValueError, match="Nazwa leku może zawierać tylko litery i spacje."):
        validate_medicine_name("Paracetamol123")
    with pytest.raises(ValueError, match="Nazwa leku może zawierać tylko litery i spacje."):
        validate_medicine_name("Par@cetamol")


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


    # Pobranie ID dodanej wizyty
    appointment_id = appointments_controller.get_appointments()[0]["appointment_id"]

    # Poprawne dane
    validate_fk_appointment_exists(db_controller, appointment_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Wizyta o ID 999 nie istnieje."):
        validate_fk_appointment_exists(db_controller, 999)


    # Pobranie ID dodanej wizyty
    appointment_id = db_controller.connection.execute("SELECT appointment_id FROM appointments").fetchone()["appointment_id"]

    # Poprawne dane
    validate_fk_appointment_exists(db_controller, appointment_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Wizyta o ID 999 nie istnieje."):
        validate_fk_appointment_exists(db_controller, 999)


def test_validate_dosage():
    """
    Testuje walidację `dosage`.
    """
    # Poprawne dane
    validate_dosage(500.054)
    validate_dosage(1.5)
    validate_dosage(10000)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        validate_dosage(0)
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        validate_dosage(-5)
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        validate_dosage(10001)
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        validate_dosage("jfslkdj")


def test_validate_medicine_price():
    """
    Testuje walidację `medicine_price`.
    """
    # Poprawne dane
    validate_medicine_price(10.99)
    validate_medicine_price(0.01)
    validate_medicine_price(1000.0)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Cena leku musi być liczbą większą niż 0."):
        validate_medicine_price(0)
    with pytest.raises(ValueError, match="Cena leku musi być liczbą większą niż 0."):
        validate_medicine_price(-1)
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        validate_dosage("jfslkdj")


def test_validate_prescription_code():
    """
    Testuje walidację `prescription_code`.
    """
    # Poprawne dane
    validate_prescription_code("1234")
    validate_prescription_code("0001")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Kod recepty musi składać się dokładnie z 4 cyfr."):
        validate_prescription_code("123")
    with pytest.raises(ValueError, match="Kod recepty musi składać się dokładnie z 4 cyfr."):
        validate_prescription_code("12345")
    with pytest.raises(ValueError, match="Kod recepty musi składać się dokładnie z 4 cyfr."):
        validate_prescription_code("12a4")





def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """
    valid_columns = ["prescription_id", "appointment_id", "medicine_name", "dosage", "medicine_price", "prescription_code"]

    # Poprawne dane
    validate_update_fields({"prescription_id": "Nowy opis"}, valid_columns)
    validate_update_fields({"appointment_id": "A01.0"}, valid_columns)
    validate_update_fields({"medicine_name": 123}, valid_columns)
    validate_update_fields({"dosage": "Nowy opis"}, valid_columns)
    validate_update_fields({"medicine_price": "A01.0"}, valid_columns)
    validate_update_fields({"prescription_code": 123}, valid_columns)

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
    valid_columns = ["prescription_id", "appointment_id", "medicine_name", "dosage", "medicine_price", "prescription_code"]

    # Poprawne dane
    filters = [
        {"column": "prescription_id", "operator": "LIKE", "value": "Opis%"},
        {"column": "appointment_id", "operator": ">", "value": 1},
        {"column": "medicine_name", "operator": "=", "value": "A01.0"},
        {"column": "dosage", "operator": "!=", "value": "Błąd opisu"},
        {"column": "medicine_price", "operator": "=", "value": "A01.0"},
        {"column": "prescription_code", "operator": "!=", "value": "Błąd opisu"},
    ]
    sort_by = [
        {"column": "appointment_id", "direction": "ASC"},
        {"column": "medicine_price", "direction": "DESC"},
    ]

    # Powinno przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting([{"column": "description", "operator": "LIKE"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting([{"column": "invalid_column", "operator": "LIKE", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: description. Dozwolone kolumny: prescription_id, appointment_id, medicine_name, dosage, medicine_price, prescription_code"):
        validate_filters_and_sorting([{"column": "description", "operator": "INVALID", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, [{"column": "description"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, [{"column": "invalid_column", "direction": "ASC"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: description. Dozwolone kolumny: prescription_id, appointment_id, medicine_name, dosage, medicine_price, prescription_code"):
        validate_filters_and_sorting(None, [{"column": "description", "direction": "INVALID"}], valid_columns)