# test_integration_diagnoses.py

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


# +-+-+-+- Testy metod dodawania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-



# test_integration_diagnoses.py

# Dodaj poniższe testy do istniejących w pliku `test_integration_diagnoses.py`.

def test_add_diagnosis_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania diagnozy z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # Próba dodania diagnozy z nieprawidłowym kodem ICD-11
    with pytest.raises(ValueError, match="Kod ICD-11 jest nieprawidłowy."):
        diagnoses.add_diagnosis(
            appointment_id=1,
            description="Grypa sezonowa",
            icd11_code="INVALID_CODE",
        )

    # Próba dodania diagnozy z nieprawidłowym opisem
    with pytest.raises(ValueError, match="Opis zawiera niedozwolone znaki."):
        diagnoses.add_diagnosis(
            appointment_id=1,
            description="Grypa!@#",
            icd11_code="J10.1",
        )


def test_add_diagnosis_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania diagnozy do pustej bazy danych bez wymaganych zależności.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
    appointments = controllers["appointments"]
    room_types_controller = setup_controllers["room_types"]

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

    # Dodanie zależności
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

    # Usuń tabelę 'appointments', aby zasymulować jej brak
    controllers["db_controller"].connection.execute("DROP TABLE IF EXISTS appointments")
    controllers["db_controller"].connection.commit()


    # Próba dodania diagnozy bez zależności w tabeli appointments
    with pytest.raises(RuntimeError, match="Błąd podczas sprawdzania zależności: no such table: appointments"):
        diagnoses.add_diagnosis(
            appointment_id=1,
            description="Grypa sezonowa",
            icd11_code="J10.1",
        )



# +-+-+-+- Testy metod aktualizacji rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-



def test_update_diagnosis_with_valid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie wizyty
    appointment_result = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )
    appointment_id = appointment_result["appointment_id"]

    # Dodanie diagnozy
    diagnosis_id = diagnoses.add_diagnosis(
        appointment_id=appointment_id,
        description="Grypa sezonowa",
        icd11_code="J10.1",
    )

    # Aktualizacja diagnozy
    diagnoses.update_diagnosis(
        diagnosis_id=diagnosis_id,
        appointment_id=appointment_id,
        description="Grypa z komplikacjami",
        icd11_code="J10.2",
    )

    # Pobranie zaktualizowanego rekordu
    updated_diagnosis = diagnoses.get_diagnoses(
        filters=[{"column": "appointment_id", "operator": "=", "value": diagnosis_id}]
    )[0]

    # Asercje
    assert updated_diagnosis["description"] == "Grypa z komplikacjami"
    assert updated_diagnosis["icd11_code"] == "J10.2"



def test_update_diagnosis_with_invalid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # Dodanie diagnozy
    diagnosis_id = diagnoses.add_diagnosis(
        appointment_id=1,
        description="Grypa sezonowa",
        icd11_code="J10.1",
    )

    # Próba aktualizacji z niepoprawnym opisem
    with pytest.raises(ValueError, match="Opis zawiera niedozwolone znaki."):
        diagnoses.update_diagnosis(
            diagnosis_id=diagnosis_id,
            appointment_id=1,
            description="Grypa!@#",
            icd11_code="J10.2",
        )

    # Próba aktualizacji z niepoprawnym kodem ICD-11
    with pytest.raises(ValueError, match="Kod ICD-11 jest nieprawidłowy."):
        diagnoses.update_diagnosis(
            diagnosis_id=diagnosis_id,
            appointment_id=1,
            description="Grypa sezonowa",
            icd11_code="INVALID_CODE",
        )



def test_update_nonexistent_diagnosis(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]

    # Próba aktualizacji nieistniejącej diagnozy
    with pytest.raises(RuntimeError, match="Rekord z podanym ID nie istnieje."):
        diagnoses.update_diagnosis(
            diagnosis_id=999,  # Nieistniejące ID
            appointment_id=1,
            description="Nieistniejąca diagnoza",
            icd11_code="J10.1",
        )




def test_update_diagnosis_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu z brakującymi danymi.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
    appointments = controllers["appointments"]

    # Dodanie zależności
    patient_id = controllers["patients"].add_patient(
        "Jan", "Kowalski", "12345678901", "123456789", "jan.kowalski@example.com", "Adres", "1980-01-01"
    )["patient_id"]
    employee_id = controllers["employees"].add_employee(
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="123456789",
        profession="Psycholog kliniczny",
        is_medical_staff=1,
    )
    service_id = controllers["services"].add_service("Masaż", 100, 200)["service_id"]
    room_types_controller = controllers["room_types"]
    room_types_controller.add_room_type("Gabinet")
    room_id = controllers["rooms"].add_room_by_name(11, 1, "Gabinet")["room_id"]

    appointment_result = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowana",
        notes="Notatka testowa",
    )
    appointment_id = appointment_result["appointment_id"]

    diagnosis_id = diagnoses.add_diagnosis(
        appointment_id=appointment_id,
        description="Grypa sezonowa",
        icd11_code="J10.1",
    )

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        diagnoses.update_diagnosis(
            diagnosis_id=diagnosis_id,
        )






# +-+-+-+- Testy metod pobierania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-



def test_get_nonexistent_diagnosis(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]

    # Próba pobrania rekordu o nieistniejącym diagnosis_id
    results = diagnoses.get_diagnoses(filters=[{"column": "appointment_id", "operator": "=", "value": 999}])
    assert len(results) == 0, "Rekord nie powinien istnieć."


def test_get_all_diagnoses(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # Dodanie diagnoz
    diagnoses.add_diagnosis(appointment_id=1, description="Grypa sezonowa", icd11_code="J10.1")
    diagnoses.add_diagnosis(appointment_id=1, description="Zapalenie płuc", icd11_code="J12.2")

    # Pobranie wszystkich rekordów
    results = diagnoses.get_diagnoses()
    assert len(results) == 2, "W bazie powinny znajdować się dwa rekordy."


def test_get_diagnoses_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]

    # Próba pobrania rekordów z pustej tabeli
    results = diagnoses.get_diagnoses()
    assert len(results) == 0, "W bazie nie powinno być żadnych rekordów."


def test_get_diagnoses_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # Dodanie diagnoz
    diagnoses.add_diagnosis(appointment_id=1, description="Grypa sezonowa", icd11_code="J10.1")
    diagnoses.add_diagnosis(appointment_id=1, description="Zapalenie płuc", icd11_code="J12.2")

    # Pobranie rekordów z filtrem
    filters = [
        {"column": "description", "operator": "LIKE", "value": "Grypa%"},
        {"column": "icd11_code", "operator": "=", "value": "J10.1"}
    ]
    results = diagnoses.get_diagnoses(filters=filters)
    assert len(results) == 1, "Powinien zostać zwrócony jeden rekord."
    assert results[0]["description"] == "Grypa sezonowa"
    assert results[0]["icd11_code"] == "J10.1"


def test_missing_dependencies(setup_controllers):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]

    # Próba dodania diagnozy bez odpowiednich zależności
    with pytest.raises(ValueError, match="Wizyta o ID 1 nie istnieje."):
        diagnoses.add_diagnosis(appointment_id=1, description="Brakująca wizyta", icd11_code="J10.1")






# +-+-+-+- Testy metod usuwania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-



def test_delete_diagnosis_with_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z appointment_id, description i icd11_code.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # Dodanie diagnozy
    diagnosis_id = diagnoses.add_diagnosis(
        appointment_id=1,
        description="Grypa sezonowa",
        icd11_code="J10.1",
    )

    # Usunięcie rekordu
    diagnoses.delete_diagnosis(diagnosis_id)

    # Próba pobrania usuniętego rekordu
    results = diagnoses.get_diagnoses(filters=[{"column": "diagnosis_id", "operator": "=", "value": diagnosis_id}])
    assert len(results) == 0, "Rekord powinien zostać usunięty."


def test_delete_diagnosis_with_invalid_data(setup_controllers):
    """
    Testuje próbę usunięcia rekordu korzystając z nieprawidłowych danych w appointment_id, description i icd11_code.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # Dodanie diagnozy
    diagnosis_id = diagnoses.add_diagnosis(
        appointment_id=1,
        description="Grypa sezonowa",
        icd11_code="J10.1",
    )

    # Próba usunięcia rekordu z nieprawidłowym ID
    with pytest.raises(RuntimeError, match=f"Rekord z podanym ID {diagnosis_id + 999} nie istnieje."):
        diagnoses.delete_diagnosis(diagnosis_id + 999)


def test_delete_nonexistent_diagnosis(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]

    # Próba usunięcia rekordu, który nie istnieje
    with pytest.raises(RuntimeError, match="Rekord z podanym ID 999 nie istnieje."):
        diagnoses.delete_diagnosis(999)




# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+










def test_database_connection_error(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]

    # Zamknięcie połączenia z bazą danych, aby symulować błąd
    controllers["db_controller"].close_connection()

    # Próba wykonania operacji na zamkniętej bazie danych
    with pytest.raises(RuntimeError, match="Połączenie z bazą danych zostało zamknięte."):
        diagnoses.add_diagnosis(
            appointment_id=1,
            description="Testowy opis",
            icd11_code="J10.1"
        )



def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD: dodawanie, pobieranie, aktualizację, filtrowanie i usuwanie danych.
    """
    controllers = setup_controllers
    diagnoses = controllers["diagnoses"]
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

    # Dodanie zależności
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

    # 1. Dodanie nowej diagnozy
    diagnosis_id = diagnoses.add_diagnosis(
        appointment_id=1,
        description="Grypa sezonowa",
        icd11_code="J10.1",
    )

    # 2. Pobranie dodanej diagnozy
    fetched_diagnosis = diagnoses.get_diagnoses(
        filters=[{"column": "diagnosis_id", "operator": "=", "value": diagnosis_id}]
    )[0]
    assert fetched_diagnosis["description"] == "Grypa sezonowa"
    assert fetched_diagnosis["icd11_code"] == "J10.1"

    diagnoses.update_diagnosis(
        diagnosis_id=diagnosis_id,
        appointment_id=1,
        description="Grypa z komplikacjami",
        icd11_code="J10.2",
    )

    updated_diagnosis = diagnoses.get_diagnoses(
        filters=[{"column": "diagnosis_id", "operator": "=", "value": diagnosis_id}]
    )[0]
    assert updated_diagnosis["description"] == "Grypa z komplikacjami"
    assert updated_diagnosis["icd11_code"] == "J10.2"

    # 4. Filtrowanie diagnozy
    filtered_results = diagnoses.get_diagnoses(
        filters=[{"column": "description", "operator": "LIKE", "value": "Grypa%"}]
    )
    assert len(filtered_results) == 1
    assert filtered_results[0]["description"] == "Grypa z komplikacjami"

    # 5. Usunięcie diagnozy
    diagnoses.delete_diagnosis(diagnosis_id)
    deleted_results = diagnoses.get_diagnoses(
        filters=[{"column": "diagnosis_id", "operator": "=", "value": diagnosis_id}]
    )
    assert len(deleted_results) == 0, "Rekord powinien zostać usunięty."
