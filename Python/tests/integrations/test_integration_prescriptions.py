# test_integration_prescriptions_controller.py

import os
import sqlite3
import pytest
from controllers.database_controller import DatabaseController
from controllers.diagnoses_controller import DiagnosesController
from controllers.appointments_controller import AppointmentsController
from controllers.patients_controller import PatientController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from controllers.prescriptions_controller import PrescriptionsController

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
        "diagnoses": DiagnosesController(db_controller),
        "appointments": AppointmentsController(db_controller),
        "patients": PatientController(db_controller),
        "employees": EmployeesController(db_controller),
        "services": ServicesController(db_controller),
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller),
        "prescriptions_controller": PrescriptionsController(db_controller),

    }

    # Tworzenie tabel
    # Tworzenie tabel tylko na kontrolerach, które implementują create_table
    for controller in controllers.values():
        if hasattr(controller, "create_table"):
            controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM diagnoses")
                db_controller.connection.execute("DELETE FROM appointments")
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM services")
                db_controller.connection.execute("DELETE FROM rooms")
                db_controller.connection.execute("DELETE FROM room_types")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_add_prescription_with_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie recepty z poprawnymi danymi.
    """

    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

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
    )["appointment_id"]

    # Dodanie recepty
    prescription = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )

    # Weryfikacja dodanego rekordu
    assert prescription["medicine_name"] == "Paracetamol"
    assert prescription["dosage"] == 500.0


def test_add_prescription_with_missing_data(setup_controllers):
    """
    Testuje próbę dodania recepty z brakującymi danymi.
    """

    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Próba dodania recepty z brakującą nazwą leku
    with pytest.raises(ValueError, match="Nazwa leku musi być niepustym ciągiem znaków."):
        prescriptions_controller.add_prescription(
            appointment_id=appointment_id,
            medicine_name="",
            dosage=500.0,
            medicine_price=10.0,
            prescription_code="1234"
        )


def test_add_prescription_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania recepty z nieprawidłowymi danymi.
    """

    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Próba dodania recepty z nieprawidłową dawką
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        prescriptions_controller.add_prescription(
            appointment_id=appointment_id,
            medicine_name="Paracetamol",
            dosage=0.0,
            medicine_price=10.0,
            prescription_code="1234"
        )


def test_add_prescription_without_existing_appointment(setup_controllers):
    """
    Testuje próbę dodania recepty bez istniejącej wizyty.
    """

    prescriptions_controller = setup_controllers["prescriptions_controller"]


    # Próba dodania recepty bez istniejącej wizyty (appointment_id = 999, która nie istnieje)
    with pytest.raises(ValueError, match="Wizyta o ID 999 nie istnieje."):
        prescriptions_controller.add_prescription(
            appointment_id=999,  # Nieistniejące ID wizyty
            medicine_name="Paracetamol",
            dosage=500.0,
            medicine_price=10.0,
            prescription_code="1234"
        )




# +-+-+-+- Testy metod aktualizacji rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_update_prescription_with_valid_data(setup_controllers):
    """
    Testuje aktualizację recepty z poprawnymi danymi.
    """


    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Dodanie recepty
    prescription_id = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )["prescription_id"]


    # Aktualizacja recepty
    prescriptions_controller.update_prescription(
        prescription_id=prescription_id,
        appointment_id=appointment_id,
        medicine_name="Ibuprofen",
        dosage=200.0,
        medicine_price=15.0,
        prescription_code="5678"
    )

    # Weryfikacja
    updated_prescription = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_id", "operator": "=", "value": prescription_id}]
    )[0]
    assert updated_prescription["medicine_name"] == "Ibuprofen"
    assert updated_prescription["dosage"] == 200.0
    assert updated_prescription["medicine_price"] == 15.0
    assert updated_prescription["prescription_code"] == "5678"


def test_update_prescription_with_invalid_data(setup_controllers):
    """
    Testuje próbę aktualizacji recepty z nieprawidłowymi danymi.
    """
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Dodanie recepty
    prescription_id = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )["prescription_id"]

    # Próba aktualizacji z nieprawidłową nazwą leku
    with pytest.raises(ValueError, match="Nazwa leku może zawierać tylko litery i spacje."):
        prescriptions_controller.update_prescription(
            prescription_id=prescription_id,
            medicine_name="1234",
            dosage=200.0,
            medicine_price=15.0,
            prescription_code="5678"
        )

    # Próba aktualizacji z nieprawidłową dawką
    with pytest.raises(ValueError, match="Dawka musi być liczbą zmiennoprzecinkową z przedziału 1-10000."):
        prescriptions_controller.update_prescription(
            prescription_id=prescription_id,
            medicine_name="Ibuprofen",
            dosage=0.0,
            medicine_price=15.0,
            prescription_code="5678"
        )


def test_update_nonexistent_prescription(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    prescriptions_controller = controllers["prescriptions_controller"]

    # Próba aktualizacji nieistniejącego rekordu
    with pytest.raises(RuntimeError, match="Rekord z podanym ID nie istnieje."):
        prescriptions_controller.update_prescription(
            prescription_id=999,  # Nieistniejący ID
            medicine_name="Ibuprofen",
            dosage=200.0,
            medicine_price=15.0,
            prescription_code="5678"
        )


def test_update_prescription_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji recepty bez danych lub z brakującymi danymi.
    """
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Dodanie recepty
    prescription_id = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )["prescription_id"]

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        prescriptions_controller.update_prescription(prescription_id=prescription_id)

    # Próba aktualizacji z brakującymi danymi
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        prescriptions_controller.update_prescription(prescription_id=prescription_id, medicine_name=None)




# +-+-+-+- Testy metod usuwania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_delete_prescription_with_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z appointment_id oraz innych parametrów.
    """
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )
    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Dodanie recepty
    prescription_id = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )["prescription_id"]

    # Usunięcie recepty
    prescriptions_controller.delete_prescription(prescription_id)

    # Weryfikacja, czy rekord został usunięty
    results = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_id", "operator": "=", "value": prescription_id}]
    )
    assert len(results) == 0, "Dane nie zostały usunięte z metody test_delete_prescription_with_valid_data"


def test_delete_prescription_with_invalid_data(setup_controllers):
    """
    Testuje próbę usunięcia rekordu korzystając z nieprawidłowych danych.
    """

    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Dodanie recepty
    prescription_id = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )["prescription_id"]

    # Próba usunięcia z nieprawidłowym ID
    with pytest.raises(RuntimeError, match=f"Rekord z podanym ID {prescription_id + 999} nie istnieje."):
        prescriptions_controller.delete_prescription(prescription_id + 999)


def test_delete_nonexistent_prescription(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu.
    """
    controllers = setup_controllers
    prescriptions_controller = controllers["prescriptions_controller"]

    # Próba usunięcia rekordu, który nie istnieje
    with pytest.raises(RuntimeError, match="Rekord z podanym ID 999 nie istnieje."):
        prescriptions_controller.delete_prescription(999)





# +-+-+-+- Testy metod pobierania, filtrowania, sortowania +-+-+-+-+-+

def test_get_nonexistent_prescription(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    prescriptions_controller = controllers["prescriptions_controller"]

    # Próba pobrania nieistniejącego rekordu
    results = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_id", "operator": "=", "value": 999}]
    )
    assert len(results) == 0, "Rekord nie powinien istnieć."


def test_get_all_prescriptions_controller(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    patients_controller.add_patient(
        first_name="Jana",
        last_name="Kowalskia",
        pesel="12345678909",
        phone="123456780",
        email="jana.kowalski@example.com",
        address="Warszawaa, ul. Testowa 1",
        date_of_birth="1980-01-09"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    employees_controller.add_employee(
        first_name="Annaa",
        last_name="Nowaka",
        email="annaa.nowak@example.com",
        phone="987654329",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    services_controller.add_service(
        service_type="Konsultacja psychologicznaa",
        service_price=100,
        duration_minutes=90
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=18,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyt
    appointment_id_1 = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]
    appointment_id_2 = appointments_controller.add_appointment(
        fk_patient_id=2,
        fk_employee_id=2,
        fk_service_id=2,
        fk_room_id=2,
        appointment_date="2025-01-10 12:00",
        appointment_status="Zakończona",
    )["appointment_id"]

    # Dodanie recept
    prescriptions_controller.add_prescription(
        appointment_id=appointment_id_1,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )
    prescriptions_controller.add_prescription(
        appointment_id=appointment_id_2,
        medicine_name="Ibuprofen",
        dosage=200.0,
        medicine_price=15.0,
        prescription_code="5678"
    )

    # Pobranie wszystkich rekordów
    results = prescriptions_controller.get_prescriptions()
    assert len(results) == 2, "W tabeli powinny znajdować się dwa rekordy."


def test_get_prescriptions_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    prescriptions_controller = controllers["prescriptions_controller"]

    # Próba pobrania rekordów z pustej tabeli
    results = prescriptions_controller.get_prescriptions()
    assert len(results) == 0, "W tabeli nie powinno być żadnych rekordów."


def test_get_prescriptions_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """

    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    patients_controller.add_patient(
        first_name="Jana",
        last_name="Kowalskia",
        pesel="12345678909",
        phone="123456780",
        email="jana.kowalski@example.com",
        address="Warszawaa, ul. Testowa 1",
        date_of_birth="1980-01-09"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    employees_controller.add_employee(
        first_name="Annaa",
        last_name="Nowaka",
        email="annaa.nowak@example.com",
        phone="987654329",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    services_controller.add_service(
        service_type="Konsultacja psychologicznaa",
        service_price=100,
        duration_minutes=90
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=18,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )
    # Dodanie wizyt
    appointment_id_1 = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]
    appointment_id_2 = appointments_controller.add_appointment(
        fk_patient_id=2,
        fk_employee_id=2,
        fk_service_id=2,
        fk_room_id=2,
        appointment_date="2025-01-10 12:00",
        appointment_status="Zakończona",
    )["appointment_id"]

    # Dodanie recept
    prescriptions_controller.add_prescription(
        appointment_id=appointment_id_1,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )
    prescriptions_controller.add_prescription(
        appointment_id=appointment_id_2,
        medicine_name="Ibuprofen",
        dosage=200.0,
        medicine_price=15.0,
        prescription_code="5678"
    )

    # Pobranie rekordów z filtrem po nazwie leku
    results = prescriptions_controller.get_prescriptions(
        filters=[{"column": "medicine_name", "operator": "LIKE", "value": "Parac%"}]
    )
    assert len(results) == 1, "Powinien zostać zwrócony jeden rekord."
    assert results[0]["medicine_name"] == "Paracetamol"

    # Pobranie rekordów z filtrem po dawce
    results = prescriptions_controller.get_prescriptions(
        filters=[{"column": "dosage", "operator": ">", "value": 300.0}]
    )
    assert len(results) == 1, "Powinien zostać zwrócony jeden rekord."
    assert results[0]["dosage"] == 500.0

    # Pobranie rekordów z filtrem po kodzie recepty
    results = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_code", "operator": "=", "value": "5678"}]
    )
    assert len(results) == 1, "Powinien zostać zwrócony jeden rekord."
    assert results[0]["prescription_code"] == "5678"






# +-+-+-+- Testy metod inne +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_database_connection_error(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    controllers = setup_controllers
    prescriptions_controller = controllers["prescriptions_controller"]

    # Zamknięcie połączenia z bazą danych, aby symulować błąd
    controllers["db_controller"].close_connection()

    # Próba wykonania operacji na zamkniętej bazie danych
    with pytest.raises(RuntimeError, match="Połączenie z bazą danych zostało zamknięte."):
        prescriptions_controller.add_prescription(
            appointment_id=1,
            medicine_name="Paracetamol",
            dosage=500.0,
            medicine_price=10.0,
            prescription_code="1234"
        )


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD: dodawanie, pobieranie, aktualizację i usuwanie recepty.
    """

    patients_controller = setup_controllers["patients"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    rooms_controller = setup_controllers["rooms"]
    appointments_controller = setup_controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]
    prescriptions_controller = setup_controllers["prescriptions_controller"]

    # Dodaj dane do tabeli patients
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Testowa 1",
        date_of_birth="1980-01-01"
    )

    # Dodaj dane do tabeli employees
    employees_controller.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )

    # Dodaj dane do tabeli services
    services_controller.add_service(
        service_type="Konsultacja psychologiczna",
        service_price=150,
        duration_minutes=60
    )

    room_types_controller.add_room_type("Gabinet konsultacyjny")

    # Dodaj dane do tabeli rooms
    rooms_controller.add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet konsultacyjny"
    )

    # Dodanie wizyty
    appointment_id = appointments_controller.add_appointment(
        fk_patient_id=1,
        fk_employee_id=1,
        fk_service_id=1,
        fk_room_id=1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )["appointment_id"]

    # Dodanie recepty
    prescription_id = prescriptions_controller.add_prescription(
        appointment_id=appointment_id,
        medicine_name="Paracetamol",
        dosage=500.0,
        medicine_price=10.0,
        prescription_code="1234"
    )["prescription_id"]

    # Pobranie dodanej recepty
    added_prescription = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_id", "operator": "=", "value": prescription_id}]
    )[0]
    assert added_prescription["medicine_name"] == "Paracetamol"
    assert added_prescription["dosage"] == 500.0
    assert added_prescription["medicine_price"] == 10.0
    assert added_prescription["prescription_code"] == "1234"

    # Aktualizacja recepty
    prescriptions_controller.update_prescription(
        prescription_id=prescription_id,
        medicine_name="Ibuprofen",
        dosage=200.0,
        medicine_price=15.0,
        prescription_code="5678"
    )

    # Pobranie zaktualizowanej recepty
    updated_prescription = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_id", "operator": "=", "value": prescription_id}]
    )[0]
    assert updated_prescription["medicine_name"] == "Ibuprofen"
    assert updated_prescription["dosage"] == 200.0
    assert updated_prescription["medicine_price"] == 15.0
    assert updated_prescription["prescription_code"] == "5678"

    # Usunięcie recepty
    prescriptions_controller.delete_prescription(prescription_id)

    # Próba pobrania usuniętej recepty
    results = prescriptions_controller.get_prescriptions(
        filters=[{"column": "prescription_id", "operator": "=", "value": prescription_id}]
    )
    assert len(results) == 0, "Rekord powinien zostać usunięty."
