# test_integration_meeting_participants.py

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


# +-+-+-+- Testy metod dodawania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

def test_add_participant_with_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")
    # Dodanie spotkania i pracownika
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)

    # Dodanie uczestnika
    participant = meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "Obecny")

    # Weryfikacja
    assert participant["fk_meeting_id"] == meeting_id
    assert participant["fk_employee_id"] == employee_id
    assert participant["participant_role"] == "Organizator"
    assert participant["attendance"] == "Obecny"


def test_add_participant_with_missing_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    with pytest.raises(ValueError, match="Spotkanie o ID None nie istnieje."):
        meeting_participants.add_participant(None, None, None, None)


def test_add_participant_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie poprawnych danych do bazy
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)

    # Próba dodania uczestnika z nieprawidłową rolą
    with pytest.raises(ValueError, match=".*Nieprawidłowa rola uczestnika.*"):
        meeting_participants.add_participant(meeting_id, employee_id, "NieznanaRola", "Obecny")

    # Próba dodania uczestnika z nieprawidłowym statusem obecności
    with pytest.raises(ValueError, match=".*Nieprawidłowa wartość `attendance`.*"):
        meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "NieznanyStatus")


def test_add_participant_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania rekordu do pustej bazy, zapewniając brak wymaganych danych referencyjnych.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    employees = controllers["employees"]
    meeting_types = controllers["meeting_types"]
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types.add_room_type("Konferencyjny")
    rooms.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania i pracownika
    meeting_types.add_meeting_type("Projektowe")
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)

    # Próba dodania uczestnika do nieistniejącego spotkania
    with pytest.raises(ValueError, match=".*Spotkanie o ID .* nie istnieje.*"):
        meeting_participants.add_participant(999, employee_id, "Organizator", "Obecny")




def test_add_meeting_type_valid_data(setup_controllers):
    """
    Testuje dodanie nowego typu spotkania z poprawnymi danymi.
    """
    controllers = setup_controllers
    meeting_types = controllers["meeting_types"]

    # Dodanie typu spotkania
    meeting_type = meeting_types.add_meeting_type("Projektowe")

    # Weryfikacja, że ID zostało zwrócone
    assert meeting_type is not None, "Metoda add_meeting_type zwróciła None."
    assert "meeting_type_id" in meeting_type, "Klucz 'meeting_type_id' nie został zwrócony."
    assert isinstance(meeting_type["meeting_type_id"], int), "ID typu spotkania powinno być liczbą całkowitą."



# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_update_participant_with_valid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie danych do tabel referencyjnych
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)
    participant_id = meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "Obecny")["participant_id"]

    # Aktualizacja uczestnika
    meeting_participants.update_participant(participant_id, fk_meeting_id=meeting_id, fk_employee_id=employee_id, participant_role="Uczestnik", attendance="Nieobecny")

    # Pobranie zaktualizowanego uczestnika
    updated_participant = meeting_participants.get_participants(
        filters=[{"column": "participant_id", "operator": "=", "value": participant_id}]
    )[0]

    # Weryfikacja
    assert updated_participant["participant_role"] == "Uczestnik"
    assert updated_participant["attendance"] == "Nieobecny"


def test_update_participant_with_invalid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]


    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")


    # Dodanie danych do tabel referencyjnych
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)
    participant_id = meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "Obecny")["participant_id"]

    # Próba aktualizacji z niepoprawną rolą
    with pytest.raises(ValueError, match=".*Nieprawidłowa rola uczestnika.*"):
        meeting_participants.update_participant(participant_id, participant_role="NieznanaRola")

    # Próba aktualizacji z niepoprawnym statusem obecności
    with pytest.raises(ValueError, match=".*Nieprawidłowa wartość `attendance`.*"):
        meeting_participants.update_participant(participant_id, attendance="NieznanyStatus")


def test_update_nonexistent_participant(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    # Próba aktualizacji nieistniejącego uczestnika
    with pytest.raises(RuntimeError, match=".*Rekord o participant_id=.* nie istnieje w bazie danych.*"):
        meeting_participants.update_participant(999, participant_role="Uczestnik", attendance="Obecny")



def test_update_participant_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez danych lub z brakującymi danymi.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]

    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")



    # Dodanie danych do tabel referencyjnych
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)
    participant_id = meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "Obecny")["participant_id"]

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        meeting_participants.update_participant(participant_id)

    # Próba aktualizacji z brakującymi danymi
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        meeting_participants.update_participant(participant_id, fk_meeting_id=None)


# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_get_nonexistent_participant(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]



    # Próba pobrania nieistniejącego uczestnika
    participants = meeting_participants.get_participants(
        filters=[{"column": "participant_id", "operator": "=", "value": 999}]
    )

    # Weryfikacja
    assert len(participants) == 0, "Rekord nie powinien istnieć."


def test_get_all_participants(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types = controllers["meeting_types"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    room_types_controller.add_room_type("KonferencyjnyB")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")
    rooms_controller.add_room_by_name(room_number=12, floor=1, room_type_name="KonferencyjnyB")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")
    # Dodanie typu spotkania do tabeli meeting_types
    meeting_type = meeting_types.add_meeting_type("Projektowe")
    meeting_type_id = meeting_type["meeting_type_id"]  # Pobranie właściwego ID typu spotkania

    

    # Dodanie danych do tabel referencyjnych
    meeting_id1 = internal_meetings.add_meeting(
        meeting_type_id, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes1", "Zaplanowane"
    )["meeting_id"]
    employee_id1 = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)
    meeting_participants.add_participant(meeting_id1, employee_id1, "Organizator", "Obecny")

    meeting_id2 = internal_meetings.add_meeting(
        meeting_type_id, 2, "2025-02-01 10:00", "2025-02-01 12:00", "Notes2", "Zaplanowane"
    )["meeting_id"]
    employee_id2 = employees.add_employee("Jane", "Smith", "jane.smith@example.com", "987654321", "Psychiatra", False)
    meeting_participants.add_participant(meeting_id2, employee_id2, "Uczestnik", "Nieobecny")

    # Pobranie wszystkich uczestników
    participants = meeting_participants.get_participants()

    # Weryfikacja
    assert len(participants) == 2, "Powinny być dwa rekordy w bazie."






def test_get_participants_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    # Próba pobrania uczestników z pustej bazy
    participants = meeting_participants.get_participants()

    # Weryfikacja
    assert len(participants) == 0, "Baza powinna być pusta."


def test_get_participants_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]


    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("KonferencyjnyA")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="KonferencyjnyA")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("PlanowanieA")


    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=12, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")


    # Dodanie danych do tabel referencyjnych
    meeting_id1 = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes1", "Zaplanowane")["meeting_id"]
    employee_id1 = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)
    meeting_participants.add_participant(meeting_id1, employee_id1, "Organizator", "Obecny")

    meeting_id2 = internal_meetings.add_meeting(2, 2, "2025-02-01 10:00", "2025-02-01 12:00", "Notes2", "Zaplanowane")["meeting_id"]
    employee_id2 = employees.add_employee("Jane", "Smith", "jane.smith@example.com", "987654321", "Psychiatra", False)
    meeting_participants.add_participant(meeting_id2, employee_id2, "Uczestnik", "Nieobecny")

    # Pobranie uczestników z filtrem po roli
    participants = meeting_participants.get_participants(
        filters=[{"column": "participant_role", "operator": "=", "value": "Organizator"}]
    )

    # Weryfikacja
    assert len(participants) == 1, "Powinien być jeden uczestnik z rolą 'Organizator'."
    assert participants[0]["participant_role"] == "Organizator"

    # Pobranie uczestników z filtrem po obecności
    participants = meeting_participants.get_participants(
        filters=[{"column": "attendance", "operator": "=", "value": "Nieobecny"}]
    )

    # Weryfikacja
    assert len(participants) == 1, "Powinien być jeden uczestnik z obecnością 'Nieobecny'."
    assert participants[0]["attendance"] == "Nieobecny"


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_delete_participant_with_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z participant_id.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie danych do tabel referencyjnych
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)
    participant_id = meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "Obecny")["participant_id"]

    # Usunięcie uczestnika
    meeting_participants.delete_participant(participant_id)

    # Weryfikacja, czy rekord został usunięty
    participants = meeting_participants.get_participants(
        filters=[{"column": "participant_id", "operator": "=", "value": participant_id}]
    )
    assert len(participants) == 0, "Dane nie zostały usunięte z metody delete_participant."


def test_delete_participant_with_invalid_data(setup_controllers):
    """
    Testuje próbę usunięcia rekordu korzystając z nieprawidłowych danych.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    # Próba usunięcia z nieprawidłowym participant_id (np. string)
    with pytest.raises(ValueError, match=".*Nieprawidłowy identyfikator uczestnika.*"):
        meeting_participants.delete_participant("invalid_id")

    # Próba usunięcia z participant_id jako None
    with pytest.raises(ValueError, match=".*Nieprawidłowy identyfikator uczestnika.*"):
        meeting_participants.delete_participant(None)

    # Próba usunięcia z participant_id jako liczba ujemna
    with pytest.raises(ValueError, match=".*Nieprawidłowy identyfikator uczestnika.*"):
        meeting_participants.delete_participant(-1)


def test_delete_nonexistent_participant(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    # Próba usunięcia nieistniejącego uczestnika
    with pytest.raises(RuntimeError, match=".*Rekord o participant_id=.* nie istnieje w bazie danych.*"):
        meeting_participants.delete_participant(999)



# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_database_connection_error(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]

    # Zamknięcie połączenia z bazą danych
    controllers["db_controller"].close_connection()

    # Próba wykonania operacji bez aktywnego połączenia
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        meeting_participants.get_participants()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ danych CRUD między kontrolerem, walidacją, modelem, a bazą danych.
    """
    controllers = setup_controllers
    meeting_participants = controllers["meeting_participants"]
    internal_meetings = controllers["internal_meetings"]
    employees = controllers["employees"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Tworzenie danych referencyjnych
    meeting_id = internal_meetings.add_meeting(1, 1, "2025-01-01 10:00", "2025-01-01 12:00", "Notes", "Zaplanowane")["meeting_id"]
    employee_id = employees.add_employee("John", "Doe", "john.doe@example.com", "123456789", "Psychiatra", True)

    # Dodanie uczestnika
    participant = meeting_participants.add_participant(meeting_id, employee_id, "Organizator", "Obecny")
    participant_id = participant["participant_id"]

    # Weryfikacja dodania
    participants = meeting_participants.get_participants(
        filters=[{"column": "participant_id", "operator": "=", "value": participant_id}]
    )
    assert len(participants) == 1, "Rekord uczestnika powinien istnieć po dodaniu."

    # Aktualizacja uczestnika
    meeting_participants.update_participant(participant_id, participant_role="Uczestnik", attendance="Nieobecny")

    # Weryfikacja aktualizacji
    updated_participant = meeting_participants.get_participants(
        filters=[{"column": "participant_id", "operator": "=", "value": participant_id}]
    )[0]
    assert updated_participant["participant_role"] == "Uczestnik"
    assert updated_participant["attendance"] == "Nieobecny"

    # Pobranie wszystkich uczestników
    all_participants = meeting_participants.get_participants()
    assert len(all_participants) == 1, "Powinien być jeden rekord w bazie."

    # Usunięcie uczestnika
    meeting_participants.delete_participant(participant_id)

    # Weryfikacja usunięcia
    participants_after_deletion = meeting_participants.get_participants(
        filters=[{"column": "participant_id", "operator": "=", "value": participant_id}]
    )
    assert len(participants_after_deletion) == 0, "Rekord uczestnika powinien być usunięty."
