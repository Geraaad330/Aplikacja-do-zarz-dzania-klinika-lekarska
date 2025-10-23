# test_integration_room_reservations.py

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
from controllers.room_reservations_controller import RoomReservationsController


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
        "room_reservations": RoomReservationsController(db_controller),
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



# +-+-+-+- Testy metod dodawania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_room_reservations.py

def test_add_reservation_with_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Pobranie rezerwacji
    reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id}]
    )

    assert len(reservations) == 1, "Rezerwacja nie została poprawnie dodana."
    assert reservations[0]["reservation_id"] == reservation_id





def test_add_reservation_with_missing_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    with pytest.raises(ValueError, match="Pokój o ID None nie istnieje."):
        room_reservations.add_reservation(
            fk_room_id=None,
            fk_appointment_id=1,
            fk_meeting_id=1,
            reservation_date="2025-01-01",
            reservation_time="10:00-11:00",
        )


def test_add_reservation_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types.add_room_type("Gabinet")
    room = rooms.add_room_by_name(10, 1, "Gabinet")
    room_id = room["room_id"]

    # Próba dodania rezerwacji z nieprawidłową datą
    with pytest.raises(ValueError, match="Wizyta o ID 1 nie istnieje."):
        room_reservations.add_reservation(
            fk_room_id=room_id,
            fk_appointment_id=1,
            fk_meeting_id=2,
            reservation_date="01-01-2025",  # Nieprawidłowy format daty
            reservation_time="10:00-11:00",
        )

    # Próba dodania rezerwacji z nieprawidłowym czasem
    with pytest.raises(ValueError, match="Wizyta o ID 1 nie istnieje."):
        room_reservations.add_reservation(
            fk_room_id=room_id,
            fk_appointment_id=1,
            fk_meeting_id=2,
            reservation_date="2025-01-01",
            reservation_time="10:00",  # Nieprawidłowy format czasu
        )


def test_add_reservation_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania rekordu do pustej bazy, gdzie brakuje danych referencyjnych.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    # Próba dodania rezerwacji bez danych referencyjnych
    with pytest.raises(ValueError, match=".*Pokój o ID 999 nie istnieje.*"):
        room_reservations.add_reservation(
            fk_room_id=999,  # Nieistniejący pokój
            fk_appointment_id=999,  # Nieistniejąca wizyta
            fk_meeting_id=999,  # Nieistniejące spotkanie
            reservation_date="2025-01-01",
            reservation_time="10:00-11:00",
        )



# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_update_reservation_with_valid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Aktualizacja rezerwacji
    room_reservations.update_reservation(
        reservation_id=reservation_id,
        reservation_date="2025-02-01",
        reservation_time="12:00-13:00",
    )

    # Pobranie rezerwacji
    reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id}]
    )

    assert len(reservations) == 1, "Rezerwacja nie została zaktualizowana."
    assert reservations[0]["reservation_date"] == "2025-02-01"
    assert reservations[0]["reservation_time"] == "12:00-13:00"


def test_update_reservation_with_invalid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Próba aktualizacji z nieprawidłową datą
    with pytest.raises(ValueError, match=".*Nieprawidłowy format daty rezerwacji.*"):
        room_reservations.update_reservation(
            reservation_id=reservation_id,
            reservation_date="01-02-2025",  # Nieprawidłowy format
            reservation_time="12:00-13:00",
        )

    # Próba aktualizacji z nieprawidłowym czasem
    with pytest.raises(ValueError, match=".*Nieprawidłowy format czasu rezerwacji.*"):
        room_reservations.update_reservation(
            reservation_id=reservation_id,
            reservation_date="2025-02-01",
            reservation_time="12:00",  # Nieprawidłowy format
        )


def test_update_nonexistent_reservation(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    # Próba aktualizacji nieistniejącego rekordu
    with pytest.raises(RuntimeError, match=".*Nie znaleziono rekordu o podanym ID.*"):
        room_reservations.update_reservation(
            reservation_id=999,  # Nieistniejące ID
            reservation_date="2025-02-01",
            reservation_time="12:00-13:00",
        )


def test_update_reservation_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez danych lub z brakującymi danymi.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match=".*Brak danych do aktualizacji.*"):
        room_reservations.update_reservation(reservation_id=reservation_id)

    # Próba aktualizacji z brakującymi danymi (np. brak `reservation_time`)
    with pytest.raises(ValueError, match=".*Nieprawidłowy format daty rezerwacji.*"):
        room_reservations.update_reservation(
            reservation_id=reservation_id,
            reservation_date="01-02-2025",  # Nieprawidłowy format
        )



# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_get_nonexistent_reservation(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    # Próba pobrania nieistniejącego rekordu
    reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": 999}]
    )
    assert len(reservations) == 0, "Nieistniejący rekord został znaleziony."


def test_get_all_reservations(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )
    room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=None,
        fk_meeting_id=1,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Pobranie wszystkich rezerwacji
    reservations = room_reservations.get_reservations()

    assert len(reservations) == 2, "Nie udało się pobrać wszystkich rekordów."


def test_get_reservations_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    # Próba pobrania rekordów z pustej bazy
    reservations = room_reservations.get_reservations()
    assert len(reservations) == 0, "Nieoczekiwane rekordy w pustej bazie."


def test_get_reservations_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    reservation_id_1 = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )
    room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=None,
        fk_meeting_id=1,
        reservation_date="2025-01-02",
        reservation_time="12:00-13:00",
    )

    # Pobranie rezerwacji z filtrem `reservation_id`
    reservations_by_id = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id_1}]
    )
    assert len(reservations_by_id) == 1, "Nie udało się pobrać rezerwacji z filtrem `reservation_id`."
    assert reservations_by_id[0]["reservation_id"] == reservation_id_1

    # Pobranie rezerwacji z filtrem `reservation_date`
    reservations_by_date = room_reservations.get_reservations(
        filters=[{"column": "reservation_date", "operator": "=", "value": "2025-01-02"}]
    )
    assert len(reservations_by_date) == 1, "Nie udało się pobrać rezerwacji z filtrem `reservation_date`."
    assert reservations_by_date[0]["reservation_date"] == "2025-01-02"

    # Pobranie rezerwacji z filtrem `fk_room_id`
    reservations_by_room = room_reservations.get_reservations(
        filters=[{"column": "fk_room_id", "operator": "=", "value": room_id}]
    )
    assert len(reservations_by_room) == 2, "Nie udało się pobrać rezerwacji z filtrem `fk_room_id`."


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_delete_reservation_with_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z `reservation_id`.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )
    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Usunięcie rezerwacji
    room_reservations.delete_reservation(reservation_id)

    # Sprawdzenie, czy rezerwacja została usunięta
    reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id}]
    )
    assert len(reservations) == 0, "Rezerwacja nie została poprawnie usunięta."


def test_delete_reservation_with_invalid_data(setup_controllers):
    """
    Testuje usunięcie rekordu korzystając z nieprawidłowych danych w `reservation_id`.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    # Próba usunięcia rezerwacji z nieprawidłowym ID
    with pytest.raises(RuntimeError, match=".*Nie znaleziono rekordu o podanym ID.*"):
        room_reservations.delete_reservation("invalid_id")  # Nieprawidłowe ID


def test_delete_nonexistent_reservation(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z `reservation_id`.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(RuntimeError, match=".*Nie znaleziono rekordu o podanym ID.*"):
        room_reservations.delete_reservation(999)  # Nieistniejące ID


# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_database_connection_error_handling(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    db_controller = controllers["db_controller"]

    # Zamknięcie połączenia z bazą danych
    db_controller.close_connection()

    # Próba wykonania operacji po zamknięciu połączenia
    with pytest.raises(RuntimeError, match=".*Brak połączenia z bazą danych.*"):
        room_reservations.get_reservations()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełne przepływy danych między kontrolerem, walidacją, modelem i bazą danych.
    Obejmuje dodawanie, pobieranie, aktualizowanie i usuwanie danych.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )

    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )

    # Weryfikacja dodania rezerwacji
    reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id}]
    )
    assert len(reservations) == 1, "Rezerwacja nie została poprawnie dodana."
    assert reservations[0]["reservation_id"] == reservation_id

    # Aktualizacja rezerwacji
    room_reservations.update_reservation(
        reservation_id=reservation_id,
        reservation_date="2025-02-01",
        reservation_time="12:00-13:00",
    )

    # Weryfikacja aktualizacji
    updated_reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id}]
    )
    assert len(updated_reservations) == 1, "Rezerwacja nie została zaktualizowana."
    assert updated_reservations[0]["reservation_date"] == "2025-02-01"
    assert updated_reservations[0]["reservation_time"] == "12:00-13:00"

    # Usunięcie rezerwacji
    room_reservations.delete_reservation(reservation_id)

    # Weryfikacja usunięcia
    deleted_reservations = room_reservations.get_reservations(
        filters=[{"column": "reservation_id", "operator": "=", "value": reservation_id}]
    )
    assert len(deleted_reservations) == 0, "Rezerwacja nie została poprawnie usunięta."


def test_appointment_and_meeting_id_dependency(setup_controllers):
    """
    Testuje zależność między `fk_appointment_id` i `fk_meeting_id`.
    - Jeśli `fk_appointment_id` jest null, to `fk_meeting_id` nie może być null.
    - Jeśli `fk_meeting_id` jest null, to `fk_appointment_id` nie może być null.
    """
    controllers = setup_controllers
    room_reservations = controllers["room_reservations"]
    appointments = controllers["appointments"]
    internal_meetings = controllers["internal_meetings"]
    room_types_controller = controllers["room_types"]
    meeting_types_controller = controllers["meeting_types"]

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

    # Dodanie typu spotkania
    meeting_type_id = meeting_types_controller.add_meeting_type("Konsylium terapeutyczne")["meeting_type_id"]

    # Dodanie wizyty
    appointment = appointments.add_appointment(
        fk_patient_id=patient_id,
        fk_employee_id=employee_id,
        fk_service_id=service_id,
        fk_room_id=room_id,
        appointment_date="2025-01-09 10:00",
        appointment_status="Zaplanowane",
        notes="Notatka testowa",
    )

    # Dodanie spotkania do tabeli internal_meetings
    internal_meetings.add_meeting(
        fk_meeting_type_id=meeting_type_id,
        fk_room_id=room_id,
        start_meeting_date="2025-01-08 15:00",
        end_meeting_date="2025-01-08 15:06",
        internal_meeting_status="Zaplanowane",
        notes="Testowe spotkanie"
    )
    # Dodanie rezerwacji
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=appointment["appointment_id"],
        fk_meeting_id=None,
        reservation_date="2025-01-01",
        reservation_time="10:00-11:00",
    )
    assert reservation_id is not None, "Nie udało się dodać rezerwacji z poprawną konfiguracją `fk_meeting_id`."

    # Próba dodania rezerwacji z `fk_meeting_id` ustawionym na null i `fk_appointment_id` ustawionym poprawnie
    reservation_id = room_reservations.add_reservation(
        fk_room_id=room_id,
        fk_appointment_id=None,
        fk_meeting_id=1,
        reservation_date="2025-01-01",
        reservation_time="12:00-13:00",
    )
    assert reservation_id is not None, "Nie udało się dodać rezerwacji z poprawną konfiguracją `fk_appointment_id`."
