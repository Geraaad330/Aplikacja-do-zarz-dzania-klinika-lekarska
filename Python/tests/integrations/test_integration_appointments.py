# test_integration_appointments.py

import os
import sqlite3
import pytest
from controllers.database_controller import DatabaseController
from controllers.appointments_controller import AppointmentsController
from controllers.patients_controller import PatientController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController

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
        "appointments": AppointmentsController(db_controller),
        "patients": PatientController(db_controller),
        "employees": EmployeesController(db_controller),
        "services": ServicesController(db_controller),
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller)
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM appointments")
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM services")
                db_controller.connection.execute("DELETE FROM rooms")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-


def test_add_appointment_with_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie wizyty z poprawnymi danymi.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych zależności
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Weryfikacja
    assert appointment["fk_patient_id"] == patient_id
    assert appointment["fk_employee_id"] == employee_id
    assert appointment["fk_service_id"] == service_id
    assert appointment["fk_room_id"] == room_id
    assert appointment["appointment_status"] == "Zaplanowana"
    assert appointment["notes"] == "Notatka testowa"




def test_add_appointment_with_missing_data(setup_controllers):
    """
    Testuje próbę dodania wizyty z brakującymi danymi.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Próba dodania wizyty bez statusu wizyty
    with pytest.raises(ValueError, match="Status wizyty musi być ciągiem znaków."):
        appointments.add_appointment(
            fk_patient_id=1,
            fk_employee_id=1,
            fk_service_id=1,
            fk_room_id=1,
            appointment_date="2025-01-09 10:00",
            appointment_status=None,
        )


def test_add_appointment_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania wizyty z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]


    # Dodanie wymaganych danych do tabel zależnych
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Konsultacja", 150, 30)["service_id"]
    room_types_controller.add_room_type("Gabinet")

    # Dodanie pokoju bez przekazywania room_type_id
    room_id = controllers["rooms"].add_room_by_name(
        room_number=11,
        floor=1,
        room_type_name="Gabinet"  # Poprawka: użycie room_name zamiast room_type_id
    )["room_id"]

    # Próba dodania wizyty z nieprawidłowymi danymi
    with pytest.raises(ValueError, match="Niepoprawny format daty wizyty."):
        appointments.add_appointment(
            fk_patient_id=patient_id,
            fk_employee_id=employee_id,
            fk_service_id=service_id,
            fk_room_id=room_id,
            appointment_date="2025-01-09 25:00",  # Nieprawidłowa godzina
            appointment_status="NieznanyStatus",  # Nieprawidłowy status
            notes="Test"
        )




def test_add_appointment_with_duplicate_unique_constraints(setup_controllers):
    """
    Testuje próbę dodania wizyty z duplikatami dla UNIQUE (fk_patient_id, appointment_date) i (fk_room_id, appointment_date).
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych zależności
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )

    # Próba dodania wizyty z tym samym `fk_room_id` i `appointment_date`
    with pytest.raises(ValueError, match="Pokój o ID .* jest już zajęty w dniu .*"):
        appointments.add_appointment(
            fk_patient_id=patient_id,
            fk_employee_id=employee_id,
            fk_service_id=service_id,
            fk_room_id=room_id,
            appointment_date="2025-01-09 10:00",
            appointment_status="Zaplanowana",
        )



def test_add_appointment_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania wizyty do pustej bazy (brak wymaganych zależności).
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Próba dodania wizyty do pustej bazy
    with pytest.raises(ValueError, match="Nie istnieje powiązanie z ID pacjenta."):
        appointments.add_appointment(
            fk_patient_id=1,
            fk_employee_id=1,
            fk_service_id=1,
            fk_room_id=1,
            appointment_date="2025-01-09 10:00",
            appointment_status="Zaplanowana",
        )




# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



def test_update_appointment_with_valid_data(setup_controllers):
    """
    Testuje aktualizację wizyty z poprawnymi danymi.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Aktualizacja wizyty
    appointments.update_appointment(
        appointment_id=appointment["appointment_id"],
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_status="Zakończona",
        notes="Zaktualizowana notatka",
    )

    # Weryfikacja
    updated_appointment = appointments.get_appointments(filters=[{"column": "appointment_id", "operator": "=", "value": appointment["appointment_id"]}])[0]
    assert updated_appointment["appointment_status"] == "Zakończona"
    assert updated_appointment["notes"] == "Zaktualizowana notatka"


def test_update_appointment_with_invalid_data(setup_controllers):
    """
    Testuje aktualizację wizyty z niepoprawnymi danymi.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Próba aktualizacji wizyty z niepoprawną datą
    with pytest.raises(ValueError, match="Niepoprawny format daty wizyty."):
        appointments.update_appointment(
            appointment_id=appointment["appointment_id"],
            appointment_date="2025-01-09",
        )

    # Próba aktualizacji wizyty z niepoprawnym statusem
    with pytest.raises(ValueError, match="Status wizyty zawiera niedozwolone znaki."):
        appointments.update_appointment(
            appointment_id=appointment["appointment_id"],
            appointment_status="NiepoprawnyStatus123",
        )


def test_update_nonexistent_appointment(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącej wizyty.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    patients = controllers["patients"]
    employees = controllers["employees"]
    services = controllers["services"]
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie danych testowych
    patient_id = patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Adres",
        date_of_birth="1990-01-01"
    )["patient_id"]

    employee_id = employees.add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        profession="Psychoterapeuta",
        is_medical_staff=1
    )

    service_id = services.add_service(
        service_type="Konsultacja",
        duration_minutes=90,
        service_price=100
    )["service_id"]

    # Dodanie typu pokoju
    room_type_name = "Gabinet"
    # pylint: disable=W0612
    room_type_id = room_types.add_room_type(
        room_type=room_type_name
    )["room_type_id"]

    # Dodanie pokoju z wykorzystaniem nazwy typu pokoju
    room_id = rooms.add_room_by_name(
        room_number=10,
        floor=1,
        room_type_name=room_type_name
    )["room_id"]

    # Próba aktualizacji nieistniejącej wizyty
    with pytest.raises(ValueError, match="Wizyta o podanym ID .* nie istnieje."):
        appointments.update_appointment(
            appointment_id=9999,  # Nieistniejące ID
            fk_patient_id=patient_id,
            fk_employee_id=employee_id,
            fk_service_id=service_id,
            fk_room_id=room_id,
            appointment_date="2025-01-10 10:00",
            appointment_status="Zaplanowana",
            notes="Aktualizacja wizyty"
        )




def test_update_appointment_without_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez danych i z brakującymi danymi.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match="Brak danych do aktualizacji."):
        appointments.update_appointment(
            appointment_id=appointment["appointment_id"]
        )


def test_update_appointment_with_duplicate_unique_constraints(setup_controllers):
    """
    Testuje aktualizację wizyty, która narusza ograniczenia unikalności.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id_1 = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    patient_id_2 = controllers["patients"].add_patient(
        "Piotr", "Nowak", "98765432109", "987654321", "piotr.nowak@example.com", "Adres2", "1990-02-02"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )  # Używamy bezpośrednio zwróconego `employee_id`
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_type = room_types_controller.add_room_type("Gabinet")["room_type_id"]
    # pylint: disable=W0612
    room_type_a = room_types_controller.add_room_type("Gabinet A")["room_type_id"]
    room_id_1 = controllers["rooms"].add_room_by_name(11, room_type, "Gabinet")["room_id"]
    room_id_2 = controllers["rooms"].add_room_by_name(12, room_type, "Gabinet A")["room_id"]

    # Dodanie dwóch wizyt
    appointments.add_appointment(
        fk_patient_id=patient_id_1,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id_1,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
    )
    appointment_2 = appointments.add_appointment(
        fk_patient_id=patient_id_2,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id_2,
        appointment_date="2025-01-09 11:00",
        appointment_status="Zaplanowana",
    )

    # Próba aktualizacji z naruszeniem ograniczeń unikalności
    with pytest.raises(ValueError, match="Pacjent o ID .* ma już wizytę w dniu .*"):
        appointments.update_appointment(
            appointment_id=appointment_2["appointment_id"],
            fk_patient_id=patient_id_1,
            appointment_date="2025-01-09 10:00",
        )




# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



def test_get_nonexistent_appointment(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Próba pobrania rekordu o nieistniejącym ID
    results = appointments.get_appointments(filters=[{"column": "appointment_id", "operator": "=", "value": 9999}])
    assert len(results) == 0, "Oczekiwano braku wyników dla nieistniejącego rekordu."


def test_get_all_appointments(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient("Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01")["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Pobranie wszystkich rekordów
    results = appointments.get_appointments()
    assert len(results) == 1, "Oczekiwano jednego rekordu w bazie."


def test_get_appointments_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Pobranie rekordów z pustej bazy
    results = appointments.get_appointments()
    assert len(results) == 0, "Oczekiwano braku rekordów w pustej bazie."


def test_get_appointments_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient("Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01")["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Pobranie rekordów z filtrem
    results = appointments.get_appointments(filters=[{"column": "appointment_status", "operator": "=", "value": "Zaplanowana"}])
    assert len(results) == 1, "Oczekiwano jednego rekordu pasującego do filtra."
    assert results[0]["appointment_status"] == "Zaplanowana"








def test_get_foreign_keys(setup_controllers):
    """
    Testuje pobranie ID patient_id, employee_id, service_id, room_id.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient("Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01")["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Pobranie ID
    assert appointments.get_patient_id("Jan", "Kowalski") == patient_id
    assert appointments.get_employee_id("Anna", "Nowak") == employee_id
    assert appointments.get_service_id("Masaż") == service_id
    assert appointments.get_room_id(11) == room_id


def test_missing_dependencies_between_tables(setup_controllers):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Próba dodania wizyty bez istniejących zależności
    with pytest.raises(ValueError, match="Nie istnieje powiązanie z ID pacjenta."):
        appointments.add_appointment(
            fk_patient_id=1,
            fk_employee_id=1,
            fk_service_id=1,
            fk_room_id=1,
            appointment_date="2025-01-09 10:00",
            appointment_status="Zaplanowana",
        )







# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_delete_appointment_with_valid_data(setup_controllers):
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Dodanie wymaganych danych
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Usunięcie rekordu
    appointments.delete_appointment(appointment["appointment_id"])

    # Weryfikacja, że rekord został usunięty
    results = appointments.get_appointments(filters=[{"column": "appointment_id", "operator": "=", "value": appointment["appointment_id"]}])
    assert len(results) == 0, f"Dane nie zostały usunięte: {appointment['appointment_id']}"




def test_delete_nonexistent_appointment(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Próba usunięcia rekordu, który nie istnieje
    nonexistent_id = 9999
    with pytest.raises(ValueError, match=f"Wizyta o podanym ID {nonexistent_id} nie istnieje."):
        appointments.delete_appointment(nonexistent_id)




# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



def test_database_connection_error(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]

    # Zamknij połączenie z bazą danych, aby wywołać błąd
    controllers["appointments"].db_controller.close_connection()

    # Próba wykonania operacji na zamkniętej bazie danych
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        appointments.get_appointments()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD: tworzenie, odczyt, aktualizacja i usuwanie wizyty.
    """
    controllers = setup_controllers
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

    # Tworzenie danych powiązanych
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    # 1. Tworzenie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )

    # Weryfikacja dodania wizyty
    assert appointment["fk_patient_id"] == patient_id
    assert appointment["fk_employee_id"] == employee_id
    assert appointment["fk_service_id"] == service_id
    assert appointment["fk_room_id"] == room_id
    assert appointment["appointment_status"] == "Zaplanowana"
    assert appointment["notes"] == "Notatka testowa"

    # 2. Odczyt wizyty
    fetched_appointments = appointments.get_appointments(filters=[{"column": "appointment_id", "operator": "=", "value": appointment["appointment_id"]}])
    assert len(fetched_appointments) == 1
    assert fetched_appointments[0]["appointment_id"] == appointment["appointment_id"]

    # 3. Aktualizacja wizyty
    appointments.update_appointment(
        appointment_id=appointment["appointment_id"],
        appointment_status="Zakończona",
        notes="Zaktualizowana notatka",
    )

    # Weryfikacja aktualizacji wizyty
    updated_appointment = appointments.get_appointments(filters=[{"column": "appointment_id", "operator": "=", "value": appointment["appointment_id"]}])[0]
    assert updated_appointment["appointment_status"] == "Zakończona"
    assert updated_appointment["notes"] == "Zaktualizowana notatka"

    # 4. Usunięcie wizyty
    appointments.delete_appointment(appointment["appointment_id"])

    # Weryfikacja usunięcia wizyty
    deleted_appointments = appointments.get_appointments(filters=[{"column": "appointment_id", "operator": "=", "value": appointment["appointment_id"]}])
    assert len(deleted_appointments) == 0, f"Dane nie zostały usunięte: {appointment['appointment_id']}"
