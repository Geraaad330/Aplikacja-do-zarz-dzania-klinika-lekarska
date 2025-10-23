# test_integration_internal_meetings.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.internal_meetings_controller import InternalMeetingsController
from controllers.meeting_types_controller import MeetingTypesController
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
        "internal_meetings": InternalMeetingsController(db_controller),
        "meeting_types": MeetingTypesController(db_controller),
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller),
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


def test_add_meeting_with_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie projektowe",
        internal_meeting_status="Zaplanowane"
    )

    # Weryfikacja poprawności danych
    assert meeting["internal_meeting_status"] == "Zaplanowane"
    assert meeting["notes"] == "Spotkanie projektowe"


def test_add_meeting_with_missing_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    with pytest.raises(ValueError, match="Typ spotkania o ID None nie istnieje."):
        internal_meetings_controller.add_meeting(
            fk_meeting_type_id=None,
            fk_room_id=None,
            start_meeting_date="2025-01-01 10:00",
            end_meeting_date=None,
            notes=None,
            internal_meeting_status="Zaplanowane"
        )


def test_add_meeting_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Próba dodania spotkania z nieprawidłowym statusem
    with pytest.raises(ValueError, match=".*Nieprawidłowy status spotkania.*"):
        internal_meetings_controller.add_meeting(
            fk_meeting_type_id=1,
            fk_room_id=room["room_id"],
            start_meeting_date="2025-01-01 10:00",
            end_meeting_date="2025-01-01 12:00",
            notes="Spotkanie projektowe.",
            internal_meeting_status="NieznanyStatus"
        )


def test_add_meeting_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania rekordu do pustej bazy danych.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    # Próba dodania spotkania bez wcześniej dodanych typów spotkań i pokoi
    with pytest.raises(ValueError, match=".*Typ spotkania o ID 1 nie istnieje.*"):
        internal_meetings_controller.add_meeting(
            fk_meeting_type_id=1,
            fk_room_id=1,
            start_meeting_date="2025-01-01 10:00",
            end_meeting_date="2025-01-01 12:00",
            notes="Spotkanie projektowe.",
            internal_meeting_status="Zaplanowane"
        )


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_update_meeting_with_valid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie do aktualizacji.",
        internal_meeting_status="Zaplanowane"
    )

    # Aktualizacja spotkania
    internal_meetings_controller.update_meeting(
        meeting_id=meeting["meeting_id"],
        notes="Zaktualizowane notatki",
        internal_meeting_status="Zakończone",
        start_meeting_date="2025-01-02 10:00",
        end_meeting_date="2025-01-02 12:00"
    )

    # Weryfikacja danych po aktualizacji
    updated_meeting = internal_meetings_controller.get_meetings(
        filters=[{"column": "meeting_id", "operator": "=", "value": meeting["meeting_id"]}]
    )[0]
    assert updated_meeting["notes"] == "Zaktualizowane notatki"
    assert updated_meeting["internal_meeting_status"] == "Zakończone"
    assert updated_meeting["start_meeting_date"] == "2025-01-02 10:00"
    assert updated_meeting["end_meeting_date"] == "2025-01-02 12:00"


def test_update_meeting_with_invalid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie do aktualizacji.",
        internal_meeting_status="Zaplanowane"
    )

    # Próba aktualizacji z nieprawidłowym statusem
    with pytest.raises(ValueError, match=".*Nieprawidłowy status spotkania.*"):
        internal_meetings_controller.update_meeting(
            meeting_id=meeting["meeting_id"],
            internal_meeting_status="NieznanyStatus"
        )


def test_update_nonexistent_meeting(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    # Próba aktualizacji rekordu, który nie istnieje
    with pytest.raises(RuntimeError, match="Rekord z podanym ID 999 nie istnieje."):
        internal_meetings_controller.update_meeting(
            meeting_id=999,
            notes="Aktualizacja nieistniejącego rekordu"
        )


def test_update_meeting_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez danych lub z brakującymi danymi.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju i pokoju
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")

    # Dodanie typu spotkania
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie do aktualizacji.",
        internal_meeting_status="Zaplanowane"
    )

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match=".*Nie podano danych do aktualizacji.*"):
        internal_meetings_controller.update_meeting(
            meeting_id=meeting["meeting_id"]
        )



# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_get_nonexistent_meeting(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    # Próba pobrania rekordu, który nie istnieje
    result = internal_meetings_controller.get_meetings(
        filters=[{"column": "meeting_id", "operator": "=", "value": 999}]
    )
    assert len(result) == 0, "Nieoczekiwany rekord został zwrócony."


def test_get_all_meetings(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju, pokoju i typu spotkania
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie dwóch spotkań
    internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie pierwsze.",
        internal_meeting_status="Zaplanowane"
    )
    internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-02 14:00",
        end_meeting_date="2025-01-02 16:00",
        notes="Spotkanie drugie.",
        internal_meeting_status="Zakończone"
    )

    # Pobranie wszystkich rekordów
    result = internal_meetings_controller.get_meetings()
    assert len(result) == 2, "Nie wszystkie rekordy zostały pobrane."


def test_get_meetings_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    # Próba pobrania wszystkich rekordów z pustej bazy
    result = internal_meetings_controller.get_meetings()
    assert len(result) == 0, "Baza danych nie jest pusta."


def test_get_meetings_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju, pokoju i typu spotkania
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie dwóch spotkań
    internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie pierwsze.",
        internal_meeting_status="Zaplanowane"
    )
    internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-02 14:00",
        end_meeting_date="2025-01-02 16:00",
        notes="Spotkanie drugie.",
        internal_meeting_status="Zakończone"
    )

    # Pobranie z filtrem na podstawie statusu
    result = internal_meetings_controller.get_meetings(
        filters=[{"column": "internal_meeting_status", "operator": "=", "value": "Zaplanowane"}]
    )
    assert len(result) == 1, "Nieprawidłowa liczba rekordów została zwrócona dla statusu 'Zaplanowane'."
    assert result[0]["notes"] == "Spotkanie pierwsze."

    # Pobranie z wieloma filtrami
    result = internal_meetings_controller.get_meetings(
        filters=[
            {"column": "internal_meeting_status", "operator": "=", "value": "Zakończone"},
            {"column": "notes", "operator": "LIKE", "value": "drugie"}
        ]
    )
    assert len(result) == 1, "Nieprawidłowa liczba rekordów została zwrócona dla złożonego filtra."
    assert result[0]["notes"] == "Spotkanie drugie."



# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_delete_meeting_with_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu na podstawie poprawnych danych.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Dodanie typu pokoju, pokoju i typu spotkania
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie do usunięcia.",
        internal_meeting_status="Zaplanowane"
    )

    # Usunięcie spotkania
    internal_meetings_controller.delete_meeting(meeting_id=meeting["meeting_id"])

    # Weryfikacja, czy rekord został usunięty
    result = internal_meetings_controller.get_meetings(
        filters=[{"column": "meeting_id", "operator": "=", "value": meeting["meeting_id"]}]
    )
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_meeting_with_invalid_data(setup_controllers):
    """
    Testuje próbę usunięcia rekordu na podstawie nieprawidłowych danych.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    # Próba usunięcia z nieprawidłowym meeting_id
    with pytest.raises(RuntimeError, match="Rekord z podanym ID invalid nie istnieje."):
        internal_meetings_controller.delete_meeting(meeting_id="invalid")


def test_delete_nonexistent_meeting(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]

    # Próba usunięcia rekordu, który nie istnieje
    with pytest.raises(RuntimeError, match="Rekord z podanym ID 999 nie istnieje."):
        internal_meetings_controller.delete_meeting(meeting_id=999)



# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_database_connection_error():
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """


    db_controller = DatabaseController()
    db_controller.database_path = "/nonexistent/path/to/database.db"  # Nieprawidłowa ścieżka


    # Próba nawiązania połączenia z bazą danych
    with pytest.raises(RuntimeError, match=".*Błąd podczas łączenia z bazą danych.*"):
        db_controller.connect_to_database()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD, pokrywający wszystkie metody modelu `internal_meetings`.
    """
    controllers = setup_controllers
    internal_meetings_controller = controllers["internal_meetings"]
    meeting_types_controller = controllers["meeting_types"]
    rooms_controller = controllers["rooms"]
    room_types_controller = controllers["room_types"]

    # Tworzenie wymaganych typów i rekordów
    room_types_controller.add_room_type("Konferencyjny")
    room = rooms_controller.add_room_by_name(room_number=11, floor=1, room_type_name="Konferencyjny")
    meeting_types_controller.add_meeting_type("Planowanie")

    # Dodanie spotkania
    meeting = internal_meetings_controller.add_meeting(
        fk_meeting_type_id=1,
        fk_room_id=room["room_id"],
        start_meeting_date="2025-01-01 10:00",
        end_meeting_date="2025-01-01 12:00",
        notes="Spotkanie testowe CRUD.",
        internal_meeting_status="Zaplanowane"
    )

    # Weryfikacja dodania
    assert meeting["internal_meeting_status"] == "Zaplanowane"
    assert meeting["notes"] == "Spotkanie testowe CRUD."

    # Aktualizacja spotkania
    internal_meetings_controller.update_meeting(
        meeting_id=meeting["meeting_id"],
        notes="Zaktualizowane notatki",
        internal_meeting_status="Zakończone"
    )

    # Weryfikacja aktualizacji
    updated_meeting = internal_meetings_controller.get_meetings(
        filters=[{"column": "meeting_id", "operator": "=", "value": meeting["meeting_id"]}]
    )[0]
    assert updated_meeting["notes"] == "Zaktualizowane notatki"
    assert updated_meeting["internal_meeting_status"] == "Zakończone"

    # Pobranie wszystkich rekordów
    all_meetings = internal_meetings_controller.get_meetings()
    assert len(all_meetings) == 1, "Nieprawidłowa liczba rekordów po dodaniu i aktualizacji."

    # Usunięcie spotkania
    internal_meetings_controller.delete_meeting(meeting_id=meeting["meeting_id"])

    # Weryfikacja usunięcia
    remaining_meetings = internal_meetings_controller.get_meetings(
        filters=[{"column": "meeting_id", "operator": "=", "value": meeting["meeting_id"]}]
    )
    assert len(remaining_meetings) == 0, "Rekord nie został usunięty."

    # Próba pobrania rekordów z pustej bazy
    empty_meetings = internal_meetings_controller.get_meetings()
    assert len(empty_meetings) == 0, "Baza danych nie jest pusta po usunięciu wszystkich rekordów."
