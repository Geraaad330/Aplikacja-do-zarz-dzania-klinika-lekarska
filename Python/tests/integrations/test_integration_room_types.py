# test_integration_room_types.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.room_types_controller import RoomTypesController
from models.room_types import RoomTypes

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_room_types_controller")
def setup_room_types_controller_fixture():
    """
    Fixture konfiguruje bazę danych oraz instancję kontrolera `RoomsTypesController`.
    Czyszczenie danych odbywa się przed każdym testem.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    room_types_controller = RoomTypesController(db_controller)
    room_types_controller.create_table()

    # Tworzenie tabeli `room_types`
    room_types_model = RoomTypes(db_controller)
    room_types_model.create_table()

    # Czyszczenie danych przed każdym testem
    db_controller.connection.execute("DELETE FROM room_types")
    db_controller.connection.commit()

    yield room_types_controller

def test_add_room_type_with_valid_data(setup_room_types_controller):
    """
    Testuje dodawanie nowej typu spotkania z poprawnymi danymi.
    """
    controller = setup_room_types_controller
    controller.add_room_type("Gabinet diagnostyczny")

    room_types = controller.get_all_room_types()
    assert len(room_types) == 1
    assert room_types[0]["room_type"] == "Gabinet diagnostyczny"

def test_add_room_type_with_invalid_data(setup_room_types_controller):
    """
    Testuje dodawanie nowej typu spotkania z niepoprawnymi danymi.
    """
    controller = setup_room_types_controller

    with pytest.raises(ValueError, match="Błąd walidacji: Nazwa typu pokoju nie może być pusta."):
        controller.add_room_type("")

    with pytest.raises(ValueError, match="Błąd walidacji: Nazwa typu pokoju musi mieć od 3 do 100 znaków."):
        controller.add_room_type("AB")



def test_update_room_type_with_valid_data(setup_room_types_controller):
    """
    Testuje aktualizację typu spotkania z poprawnymi danymi.
    """
    controller = setup_room_types_controller

    # Dodanie typu spotkania
    controller.add_room_type("Gabinet diagnostyczny")
    room_type_variable = controller.get_all_room_types()[0]

    # Aktualizacja
    updates = {"room_type": "Sala terapii grupowej"}
    controller.update_room_type(room_type_variable["room_type_id"], updates)

    updated_room_type_variable = controller.get_all_room_types()[0]
    assert updated_room_type_variable["room_type"] == "Sala terapii grupowej"

def test_update_room_type_with_invalid_data(setup_room_types_controller):
    """
    Testuje aktualizację typu spotkania z niepoprawnymi danymi.
    """
    controller = setup_room_types_controller

    # Dodanie typu spotkania
    controller.add_room_type("Gabinet diagnostyczny")
    room_type_variable = controller.get_all_room_types()[0]

    with pytest.raises(ValueError, match="Błąd walidacji: Nazwa typu pokoju nie może być pusta."):
        controller.update_room_type(room_type_variable["room_type_id"], {"room_type": ""})


def test_update_nonexistent_room_type_variable(setup_room_types_controller):
    """
    Testuje aktualizację rekordu, który nie istnieje.
    """
    controller = setup_room_types_controller

    updates = {"room_type": "Sala terapii grupowej"}
    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.update_room_type(999, updates)






def test_delete_nonexistent_room_type_variable(setup_room_types_controller):
    """
    Testuje usuwanie rekordu, który nie istnieje.
    """
    controller = setup_room_types_controller

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.delete_room_type(999)


def test_delete_room_type(setup_room_types_controller):
    """
    Testuje usuwanie typu spotkania.
    """
    controller = setup_room_types_controller

    # Dodanie typu spotkania
    controller.add_room_type("Gabinet diagnostyczny")
    room_type_variable = controller.get_all_room_types()[0]

    # Usuwanie
    controller.delete_room_type(room_type_variable["room_type_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM room_types").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_delete_room_type."



def test_full_crud_flow(setup_room_types_controller):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """
    controller = setup_room_types_controller

    # Dodanie typu spotkania
    controller.add_room_type("Gabinet diagnostyczny")
    room_type_variable = controller.get_all_room_types()[0]
    assert room_type_variable["room_type"] == "Gabinet diagnostyczny"

    # Aktualizacja typu spotkania
    updates = {"room_type": "Sala terapii grupowej"}
    controller.update_room_type(room_type_variable["room_type_id"], updates)
    updated_room_type_variable = controller.get_all_room_types()[0]
    assert updated_room_type_variable["room_type"] == "Sala terapii grupowej"

    # Usuwanie typu spotkania
    controller.delete_room_type(updated_room_type_variable["room_type_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM room_types").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_full_crud_flow."


def test_get_room_types_with_filters(setup_room_types_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości filtracji.
    """
    controller = setup_room_types_controller

    # Dodanie danych
    controller.add_room_type("Gabinet psychoterapeutyczny")
    controller.add_room_type("Gabinet psychiatryczny")

    filters = [{"column": "room_type", "operator": "LIKE", "value": "%psych%"}]
    results = controller.get_room_types_with_filters(filters=filters)

    assert len(results) == 2
    assert results[0]["room_type"] == "Gabinet psychoterapeutyczny"


def test_get_room_types_with_sorting(setup_room_types_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości sortowania.
    """
    controller = setup_room_types_controller

    # Dodanie danych
    controller.add_room_type("Sala terapii rodzinnej")
    controller.add_room_type("Sala terapii grupowej")
    controller.add_room_type("Gabinet diagnostyczny")

    # Sortowanie alfabetyczne rosnąco
    results = controller.get_room_types_with_filters(sort_by=[("room_type", "ASC")])
    assert results[0]["room_type"] == "Gabinet diagnostyczny"

    # Sortowanie alfabetyczne malejąco
    results = controller.get_room_types_with_filters(sort_by=[("room_type", "DESC")])
    assert results[0]["room_type"] == "Sala terapii rodzinnej"




def test_database_disconnection_handling_room_types(setup_room_types_controller):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia w tabeli `room_types`.
    """
    controller = setup_room_types_controller

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba dodania typu spotkania po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.add_room_type("Gabinet diagnostyczny")

    # Próba pobrania typu spotkania po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.get_all_room_types()



