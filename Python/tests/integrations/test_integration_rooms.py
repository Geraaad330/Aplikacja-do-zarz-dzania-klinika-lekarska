# test_integration_rooms.py

import os
import sqlite3
import pytest
from controllers.database_controller import DatabaseController
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
        "rooms": RoomsController(db_controller),
        "room_types": RoomTypesController(db_controller),
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM rooms")
                db_controller.connection.execute("DELETE FROM room_types")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_add_room_with_valid_data_by_ids(setup_controllers):
    """
    Testuje poprawne dodanie pokoju z poprawnymi danymi korzystając z room_number, floor i fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoju z room_number w zakresie 0-100
    rooms.add_room_by_ids(50, 1, room_type_id)

    # Weryfikacja
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 50}])
    assert len(records) == 1
    assert records[0]["room_number"] == 50
    assert records[0]["floor"] == 1


def test_add_room_with_valid_data_by_name(setup_controllers):
    """
    Testuje poprawne dodanie pokoju z poprawnymi danymi korzystając z room_number, floor i room_type (nazwa typu pokoju).
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoju z room_number w zakresie 0-100
    rooms.add_room_by_name(50, 2, "Gabinet")

    # Weryfikacja
    records = rooms.get_rooms_with_room_type_names([{"column": "room_number", "operator": "=", "value": 50}])
    assert len(records) == 1
    assert records[0]["room_number"] == 50
    assert records[0]["floor"] == 2
    assert records[0]["room_type_name"] == "Gabinet"


def test_add_room_with_missing_data_by_ids(setup_controllers):
    """
    Testuje próbę dodania pokoju z brakującymi danymi korzystając z room_number, floor i fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą całkowitą."):
        rooms.add_room_by_ids(None, 1, 1)

def test_add_room_with_missing_data_by_name(setup_controllers):
    """
    Testuje próbę dodania pokoju z brakującymi danymi korzystając z room_number, floor i room_type.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    with pytest.raises(ValueError, match="Błąd walidacji: Piętro musi być liczbą całkowitą."):
        rooms.add_room_by_name(13, None, "Gabinet")

def test_add_room_with_invalid_data_by_ids(setup_controllers):
    """
    Testuje próbę dodania pokoju z nieprawidłowymi danymi korzystając z room_number, floor i fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą całkowitą"):
        rooms.add_room_by_ids("Invalid", 1, 1)

def test_add_room_with_invalid_data_by_name(setup_controllers):
    """
    Testuje próbę dodania pokoju z nieprawidłowymi danymi korzystając z room_number, floor i room_type.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    # Nieprawidłowy numer pokoju, poprawna nazwa typu pokoju
    with pytest.raises(ValueError, match="Błąd walidacji: Numer pokoju musi być liczbą całkowitą."):
        rooms.add_room_by_name("Invalid", 1, "Gabinet")


def test_add_room_with_duplicate_data_by_ids(setup_controllers):
    """
    Testuje próbę dodania pokoju z duplikatem korzystając z room_number, floor i fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoju
    rooms.add_room_by_ids(16, 1, room_type_id)

    # Próba dodania pokoju z tym samym numerem
    with pytest.raises(ValueError, match="Numer pokoju '16' już istnieje w tabeli rooms."):
        rooms.add_room_by_ids(16, 1, room_type_id)

def test_add_room_with_duplicate_data_by_name(setup_controllers):
    """
    Testuje próbę dodania pokoju z duplikatem korzystając z room_number, floor i room_type.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoju
    rooms.add_room_by_name(17, 2, "Gabinet")

    # Próba dodania pokoju z tym samym numerem
    with pytest.raises(ValueError, match="Numer pokoju '17' już istnieje w tabeli rooms."):
        rooms.add_room_by_name(17, 2, "Gabinet")

def test_add_room_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania pokoju do pustej bazy.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]


    # Nie dodajemy żadnego typu pokoju
    with pytest.raises(ValueError, match="Typ pokoju 'Gabinet' nie istnieje."):
        rooms.add_room_by_name(18, 2, "Gabinet")



# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



# test_integration_rooms.py

def test_get_existing_record_by_ids(setup_controllers):
    """
    Testuje poprawne pobieranie istniejącego rekordu korzystając z room_number, floor, fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoju
    rooms.add_room_by_ids(11, 1, room_type_id)

    # Pobranie pokoju
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 11}])
    assert len(records) == 1
    assert records[0]["room_number"] == 11
    assert records[0]["floor"] == 1
    assert records[0]["fk_room_type_id"] == room_type_id


def test_get_existing_record_by_name(setup_controllers):
    """
    Testuje poprawne pobieranie istniejącego rekordu korzystając z room_number, floor i nazwy typu pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoju
    rooms.add_room_by_name(12, 2, "Gabinet")

    # Pobranie pokoju
    records = rooms.get_rooms_with_room_type_names([{"column": "room_number", "operator": "=", "value": 12}])
    assert len(records) == 1
    assert records[0]["room_number"] == 12
    assert records[0]["floor"] == 2
    assert records[0]["room_type_name"] == "Gabinet"



def test_get_nonexistent_record(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    # Poprawiony format filtrów
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 999}])
    assert len(records) == 0



def test_get_all_records(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoi
    rooms.add_room_by_name(13, 1, "Gabinet")
    rooms.add_room_by_name(14, 2, "Gabinet")

    # Pobranie wszystkich rekordów
    records = rooms.get_rooms_with_filters()
    assert len(records) == 2


def test_get_records_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    records = rooms.get_rooms_with_filters()
    assert len(records) == 0


def test_get_records_with_filters_by_ids(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów korzystając z room_number, floor, fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoi
    rooms.add_room_by_ids(15, 0, room_type_id)
    rooms.add_room_by_ids(16, 2, room_type_id)

    # Pobranie rekordów z filtrem
    records = rooms.get_rooms_with_filters([{"column": "floor", "operator": "=", "value": 0}])
    assert len(records) == 1
    assert records[0]["room_number"] == 15



def test_get_records_with_filters_by_name(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów korzystając z room_number, floor i nazwy typu pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoi
    rooms.add_room_by_name(11, 1, "Gabinet")
    rooms.add_room_by_name(12, 2, "Gabinet")

    # Pobranie pokoju z filtrem
    records = rooms.get_rooms_with_room_type_names([{"column": "floor", "operator": "=", "value": 2}])
    assert len(records) == 1
    assert records[0]["room_number"] == 12
    assert records[0]["floor"] == 2
    assert records[0]["room_type_name"] == "Gabinet"





def test_get_room_type_id_by_name(setup_controllers):
    """
    Testuje próbę pobrania ID room_type_id na podstawie nazwy typu pokoju.
    """
    controllers = setup_controllers
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    assert room_type_id is not None
    assert room_type_id > 0


def test_get_missing_dependency(setup_controllers):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    with pytest.raises(ValueError, match="ID typu pokoju '999' nie istnieje w tabeli room_types."):
        rooms.add_room_by_ids(19, 1, 999)




# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_rooms.py

def test_update_room_with_valid_data_by_ids(setup_controllers):
    """
    Testuje aktualizację pokoju z poprawnymi danymi korzystając z room_number, floor i fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoju
    rooms.add_room_by_ids(21, 1, room_type_id)

    # Aktualizacja pokoju
    rooms.update_room_by_ids(1, room_type_id, 31, 2)

    # Weryfikacja
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 31}])
    assert len(records) == 1
    assert records[0]["floor"] == 2



def test_update_room_with_valid_data_by_name(setup_controllers):
    """
    Testuje aktualizację pokoju z poprawnymi danymi korzystając z room_number, floor i nazwy typu pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")
    room_types.add_room_type("Sala konferencyjna")

    # Dodanie pokoju
    rooms.add_room_by_name(12, 1, "Gabinet")

    # Aktualizacja pokoju
    rooms.update_room_by_name(1, "Sala konferencyjna", 22, 2)

    # Weryfikacja
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 22}])
    assert len(records) == 1
    assert records[0]["floor"] == 2
    assert records[0]["room_number"] == 22




def test_update_room_with_invalid_data_by_ids(setup_controllers):
    """
    Testuje aktualizację pokoju z niepoprawnymi danymi korzystając z room_number, floor i fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoju
    rooms.add_room_by_ids(13, 1, room_type_id)

    # Próba aktualizacji z niepoprawnym numerem pokoju
    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą całkowitą."):
        rooms.update_room_by_ids(1, room_type_id, "Invalid", 2)



def test_update_room_with_invalid_data_by_name(setup_controllers):
    """
    Testuje aktualizację pokoju z niepoprawnymi danymi korzystając z room_number, floor i nazwy typu pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")
    room_types.add_room_type("Sala konferencyjna")

    # Dodanie pokoju
    rooms.add_room_by_name(14, 1, "Gabinet")

    # Próba aktualizacji z niepoprawnymi danymi
    with pytest.raises(ValueError, match="Typ pokoju 'InvalidType' nie istnieje."):
        rooms.update_room_by_name(1, "InvalidType", 24, 2)


def test_update_nonexistent_room(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    with pytest.raises(KeyError, match="Pokój o podanym ID nie istnieje."):
        rooms.update_room_by_ids(999, 1, 101, 1)



def test_update_room_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji pokoju z brakującymi danymi.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoju
    rooms.add_room_by_name(16, 1, "Gabinet")

    # Próba aktualizacji z brakującymi danymi
    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą całkowitą."):
        rooms.update_room_by_ids(1, None, None, None)




def test_update_room_with_duplicate_room_number(setup_controllers):
    """
    Testuje próbę aktualizacji pokoju, która narusza unikalność numeru pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoi
    rooms.add_room_by_name(17, 1, "Gabinet")
    rooms.add_room_by_name(18, 1, "Gabinet")

    # Próba aktualizacji numeru pokoju na istniejący
    with pytest.raises(ValueError, match="Numer pokoju '17' już istnieje w tabeli rooms."):
        rooms.update_room_by_ids(2, 1, 17, 2)




# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_rooms.py

def test_delete_existing_record_by_ids(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z room_number, floor, fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # Dodanie pokoju
    rooms.add_room_by_ids(21, 1, room_type_id)

    # Usunięcie pokoju
    rooms.delete_room(1)

    # Weryfikacja
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 21}])
    assert len(records) == 0, "Dane nie zostały usunięte."


def test_delete_existing_record_by_name(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z room_number, floor i nazwy typu pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Gabinet")

    # Dodanie pokoju
    rooms.add_room_by_name(22, 2, "Gabinet")

    # Usunięcie pokoju
    rooms.delete_room(1)

    # Weryfikacja
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 22}])

    assert len(records) == 0, "Dane nie zostały usunięte."


def test_delete_nonexistent_record_by_ids(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z room_number, floor, fk_room_type_id.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]

    with pytest.raises(KeyError, match="Pokój o podanym ID nie istnieje."):
        rooms.delete_room(999)



def test_delete_nonexistent_record_by_name(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z floor i nazwy typu pokoju.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # Dodanie typu pokoju
    room_types.add_room_type("Sala konferencyjna")

    with pytest.raises(KeyError, match="Pokój o podanym ID nie istnieje."):
        rooms.delete_room(1)



# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_rooms.py

def test_database_connection_error():
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    # Utworzenie kontrolera bez połączenia z bazą danych
    db_controller = DatabaseController()
    rooms_controller = RoomsController(db_controller)

    # Próba użycia kontrolera bez otwartego połączenia
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        rooms_controller.get_rooms_with_filters()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ danych między kontrolerem, walidacją, modelem i bazą danych.
    """
    controllers = setup_controllers
    rooms = controllers["rooms"]
    room_types = controllers["room_types"]

    # 1. Tworzenie typu pokoju
    room_types.add_room_type("Konferencyjny")
    room_type_id = room_types.get_all_room_types()[0]["room_type_id"]

    # 2. Dodanie pokoju za pomocą ID
    rooms.add_room_by_ids(31, 1, room_type_id)

    # 3. Weryfikacja dodania
    records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 31}])
    assert len(records) == 1
    assert records[0]["room_number"] == 31
    assert records[0]["floor"] == 1
    assert records[0]["fk_room_type_id"] == room_type_id

    # 4. Aktualizacja pokoju za pomocą ID
    rooms.update_room_by_ids(1, room_type_id, 32, 2)

    # 5. Weryfikacja aktualizacji
    updated_records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 32}])
    assert len(updated_records) == 1
    assert updated_records[0]["room_number"] == 32
    assert updated_records[0]["floor"] == 2

    # 6. Dodanie pokoju za pomocą nazwy typu pokoju
    rooms.add_room_by_name(33, 0, "Konferencyjny")

    # 7. Weryfikacja dodania pokoju
    second_records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 33}])
    assert len(second_records) == 1
    assert second_records[0]["room_number"] == 33
    assert second_records[0]["floor"] == 0

    # 8. Pobranie wszystkich rekordów
    all_records = rooms.get_rooms_with_filters()
    assert len(all_records) == 2

    # 9. Usunięcie pokoju
    rooms.delete_room(1)

    # 10. Weryfikacja usunięcia
    after_delete_records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 32}])
    assert len(after_delete_records) == 0, "Dane nie zostały usunięte: room_id=1."

    # 11. Pobranie rekordu pozostałego w bazie
    remaining_records = rooms.get_rooms_with_filters([{"column": "room_number", "operator": "=", "value": 33}])
    assert len(remaining_records) == 1
    assert remaining_records[0]["room_number"] == 33
