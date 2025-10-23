# test_rooms_model_validation.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.room_types_controller import RoomTypesController
from models.rooms import Rooms
from validators.rooms_model_validation import (
    validate_room_number,
    validate_floor,
    validate_fk_room_type_id,
    validate_room_type_exists,
    validate_unique_room_number,
    validate_room_type,
    validate_update_fields,
    validate_filters_and_sorting,
    validate_operator_and_value,

)

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Fixture konfigurujący testową bazę danych SQLite3.
    Tworzy wymagane tabele i zapewnia czyste środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()


    roomss_model = Rooms(db_controller)
    roomss_model.create_table() 

    # Tworzenie tabel
    room_types_controller = RoomTypesController(db_controller)
    room_types_controller.create_table()

    yield db_controller, room_types_controller

    # Czyszczenie danych testowych
    with db_controller.connection:
        db_controller.connection.execute("DELETE FROM rooms")
        db_controller.connection.execute("DELETE FROM room_types")
    db_controller.close_connection()

def test_validate_room_type():
    """Testuje walidację nazwy typu pokoju."""
    # Poprawne dane
    validate_room_type("Gabinet diagnostyczny")
    validate_room_type("Gabinet psychoterapeutyczny - Test (Zaawansowany)")
    validate_room_type("Sala: terapii /grupowej")
    validate_room_type("Biuro, recepcji.")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa typu pokoju musi być ciągiem znaków."):
        validate_room_type(123)
    with pytest.raises(ValueError, match="Nazwa typu pokoju nie może być pusta."):
        validate_room_type("")
    with pytest.raises(ValueError, match="Nazwa typu pokoju musi mieć od 3 do 100 znaków."):
        validate_room_type("AB")
    with pytest.raises(ValueError, match="Nazwa typu pokoju musi mieć od 3 do 100 znaków."):
        validate_room_type("A" * 101)
    with pytest.raises(ValueError, match="Nazwa typu pokoju zawiera niedozwolone znaki."):
        validate_room_type("!@#$%^&*")


def test_validate_room_number():
    """
    Testuje walidację numeru pokoju (room_number).
    """
    # Poprawne dane
    validate_room_number(0)
    validate_room_number(50)
    validate_room_number(100)

    # Błędne dane
    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą całkowitą."):
        validate_room_number("50")
    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą w zakresie od 0 do 100."):
        validate_room_number(-1)
    with pytest.raises(ValueError, match="Numer pokoju musi być liczbą w zakresie od 0 do 100."):
        validate_room_number(101)


def test_validate_floor():
    """
    Testuje walidację piętra (floor).
    """
    # Poprawne dane
    validate_floor(0)
    validate_floor(1)
    validate_floor(2)

    # Błędne dane
    with pytest.raises(ValueError, match="Piętro musi być liczbą całkowitą."):
        validate_floor("1")
    with pytest.raises(ValueError, match="Piętro musi być liczbą w zakresie od 0 do 2."):
        validate_floor(-1)
    with pytest.raises(ValueError, match="Piętro musi być liczbą w zakresie od 0 do 2."):
        validate_floor(3)


def test_validate_fk_room_type_id():
    """
    Testuje walidację klucza obcego fk_room_type_id.
    """
    # Poprawne dane
    validate_fk_room_type_id(1)
    validate_fk_room_type_id(999)

    # Błędne dane
    with pytest.raises(ValueError, match="ID typu pokoju \\(fk_room_type_id\\) musi być liczbą całkowitą."):
        validate_fk_room_type_id("1")
    with pytest.raises(ValueError, match="ID typu pokoju \\(fk_room_type_id\\) musi być liczbą całkowitą."):
        validate_fk_room_type_id(1.5)


def test_validate_room_type_exists(setup_database):
    """
    Testuje walidację istnienia typu pokoju w tabeli room_types.
    """
    _, room_types_controller = setup_database

    # Dodanie danych testowych
    room_types_controller.add_room_type("Konferencyjny")
    room_type_id = room_types_controller.get_all_room_types()[0]["room_type_id"]

    # Poprawne dane
    validate_room_type_exists(room_types_controller, room_type_id)

    # Błędne dane
    with pytest.raises(ValueError, match=f"ID typu pokoju '{999}' nie istnieje w tabeli room_types."):
        validate_room_type_exists(room_types_controller, 999)


def test_validate_unique_room_number(setup_database):
    """
    Testuje walidację unikalności numeru pokoju.
    """
    db_controller, room_types_controller = setup_database

    # Dodanie danych testowych
    room_types_controller.add_room_type("Konferencyjny")
    room_type_id = room_types_controller.get_all_room_types()[0]["room_type_id"]
    query = "INSERT INTO rooms (room_number, floor, fk_room_type_id) VALUES (?, ?, ?)"
    db_controller.connection.execute(query, (10, 1, room_type_id))

    # Poprawne dane
    validate_unique_room_number(db_controller, 12)

    # Błędne dane
    with pytest.raises(ValueError, match="Numer pokoju '10' już istnieje w tabeli rooms."):
        validate_unique_room_number(db_controller, 10)




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


def test_validate_filters_and_sorting(setup_database):
    """
    Testuje walidację filtrów i sortowania.
    """
    #pylint: disable=W0612
    db_controller = setup_database


    valid_columns = ["room_type_id", "room_type"]

    # Poprawne przypadki
    filters = [
        {"column": "room_type", "operator": "LIKE", "value": "Psych%"},
        {"column": "room_type_id", "operator": ">", "value": 1},
    ]
    sort_by = [{"column": "room_type", "direction": "ASC"}]

    # Walidacja powinna przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki

    # Niepoprawny filtr - brak klucza "value"
    filters = [{"column": "room_type", "operator": "LIKE"}]
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Niepoprawna kolumna
    filters = [{"column": "invalid_column", "operator": "LIKE", "value": "Psych%"}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Nieobsługiwany operator
    filters = [{"column": "room_type", "operator": "INVALID", "value": "Psych%"}]
    with pytest.raises(ValueError, match="Nieprawidłowy operator w filtrze: INVALID."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Niepoprawny sort_by - brak klucza "direction"
    sort_by = [{"column": "room_type"}]
    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

    # Niepoprawna kolumna w sortowaniu
    sort_by = [{"column": "invalid_column", "direction": "ASC"}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

    # Niepoprawny kierunek sortowania
    sort_by = [{"column": "room_type", "direction": "INVALID"}]
    with pytest.raises(ValueError, match="Nieprawidłowy kierunek sortowania: INVALID. Dozwolone wartości: 'ASC', 'DESC'."):
        validate_filters_and_sorting(None, sort_by, valid_columns)


def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """
    valid_columns = ["room_type_id", "room_type"]

    # Poprawne przypadki
    validate_update_fields({"room_type": "Nowy typ pokoju"}, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "value"}, valid_columns)
