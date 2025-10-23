# test_integration_meeting_types.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.meeting_types_controller import MeetingTypesController
from models.meeting_types import MeetingTypes

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_meeting_types_controller")
def setup_meeting_types_controller_fixture():
    """
    Fixture konfiguruje bazę danych oraz instancję kontrolera `MeetingTypesController`.
    Czyszczenie danych odbywa się przed każdym testem.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    meeting_types_controller = MeetingTypesController(db_controller)
    meeting_types_controller.create_table()

    # Tworzenie tabeli `meeting_types`
    meeting_types_model = MeetingTypes(db_controller)
    meeting_types_model.create_table()

    # Czyszczenie danych przed każdym testem
    db_controller.connection.execute("DELETE FROM meeting_types")
    db_controller.connection.commit()

    yield meeting_types_controller

def test_add_meeting_type_with_valid_data(setup_meeting_types_controller):
    """
    Testuje dodawanie nowej typu spotkania z poprawnymi danymi.
    """
    controller = setup_meeting_types_controller
    controller.add_meeting_type("Konsylium terapeutyczne")

    meeting_types = controller.get_all_meeting_types()
    assert len(meeting_types) == 1
    assert meeting_types[0]["meeting_type"] == "Konsylium terapeutyczne"

def test_add_meeting_type_with_invalid_data(setup_meeting_types_controller):
    """
    Testuje dodawanie nowej typu spotkania z niepoprawnymi danymi.
    """
    controller = setup_meeting_types_controller

    with pytest.raises(ValueError, match="Nazwa typu spotkania nie może być pusta."):
        controller.add_meeting_type("")

    with pytest.raises(ValueError, match="Nazwa typu spotkania musi mieć od 3 do 100 znaków."):
        controller.add_meeting_type("AB")



def test_update_meeting_type_with_valid_data(setup_meeting_types_controller):
    """
    Testuje aktualizację typu spotkania z poprawnymi danymi.
    """
    controller = setup_meeting_types_controller

    # Dodanie typu spotkania
    controller.add_meeting_type("Konsylium terapeutyczne")
    meeting_type_variable = controller.get_all_meeting_types()[0]

    # Aktualizacja
    updates = {"meeting_type": "Superwizja"}
    controller.update_meeting_type(meeting_type_variable["meeting_type_id"], updates)

    updated_meeting_type_variable = controller.get_all_meeting_types()[0]
    assert updated_meeting_type_variable["meeting_type"] == "Superwizja"

def test_update_meeting_type_with_invalid_data(setup_meeting_types_controller):
    """
    Testuje aktualizację typu spotkania z niepoprawnymi danymi.
    """
    controller = setup_meeting_types_controller

    # Dodanie typu spotkania
    controller.add_meeting_type("Konsylium terapeutyczne")
    meeting_type_variable = controller.get_all_meeting_types()[0]

    with pytest.raises(ValueError, match="Nazwa typu spotkania nie może być pusta."):
        controller.update_meeting_type(meeting_type_variable["meeting_type_id"], {"meeting_type": ""})


def test_update_nonexistent_meeting_type_variable(setup_meeting_types_controller):
    """
    Testuje aktualizację rekordu, który nie istnieje.
    """
    controller = setup_meeting_types_controller

    updates = {"meeting_type": "Superwizja"}
    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.update_meeting_type(999, updates)






def test_delete_nonexistent_meeting_type_variable(setup_meeting_types_controller):
    """
    Testuje usuwanie rekordu, który nie istnieje.
    """
    controller = setup_meeting_types_controller

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.delete_meeting_type(999)


def test_delete_meeting_type(setup_meeting_types_controller):
    """
    Testuje usuwanie typu spotkania.
    """
    controller = setup_meeting_types_controller

    # Dodanie typu spotkania
    controller.add_meeting_type("Konsylium terapeutyczne")
    meeting_type_variable = controller.get_all_meeting_types()[0]

    # Usuwanie
    controller.delete_meeting_type(meeting_type_variable["meeting_type_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM meeting_types").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_delete_meeting_type."



def test_full_crud_flow(setup_meeting_types_controller):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """
    controller = setup_meeting_types_controller

    # Dodanie typu spotkania
    controller.add_meeting_type("Konsylium terapeutyczne")
    meeting_type_variable = controller.get_all_meeting_types()[0]
    assert meeting_type_variable["meeting_type"] == "Konsylium terapeutyczne"

    # Aktualizacja typu spotkania
    updates = {"meeting_type": "Superwizja"}
    controller.update_meeting_type(meeting_type_variable["meeting_type_id"], updates)
    updated_meeting_type_variable = controller.get_all_meeting_types()[0]
    assert updated_meeting_type_variable["meeting_type"] == "Superwizja"

    # Usuwanie typu spotkania
    controller.delete_meeting_type(updated_meeting_type_variable["meeting_type_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM meeting_types").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_full_crud_flow."


def test_get_meeting_types_with_filters(setup_meeting_types_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości filtracji.
    """
    controller = setup_meeting_types_controller

    # Dodanie danych
    controller.add_meeting_type("Szkolenie wewnętrzne")
    controller.add_meeting_type("Superwizja")

    filters = [{"column": "meeting_type", "operator": "LIKE", "value": "%SZ%"}]
    results = controller.get_meeting_types_with_filters(filters=filters)

    assert len(results) == 1
    assert results[0]["meeting_type"] == "Szkolenie wewnętrzne"


def test_get_meeting_types_with_sorting(setup_meeting_types_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości sortowania.
    """
    controller = setup_meeting_types_controller

    # Dodanie danych
    controller.add_meeting_type("Szkolenie wewnętrzne")
    controller.add_meeting_type("Superwizja")
    controller.add_meeting_type("Konsylium terapeutyczne")

    # Sortowanie alfabetyczne rosnąco
    results = controller.get_meeting_types_with_filters(sort_by=[("meeting_type", "ASC")])
    assert results[0]["meeting_type"] == "Konsylium terapeutyczne"

    # Sortowanie alfabetyczne malejąco
    results = controller.get_meeting_types_with_filters(sort_by=[("meeting_type", "DESC")])
    assert results[0]["meeting_type"] == "Szkolenie wewnętrzne"




def test_database_disconnection_handling_meeting_types(setup_meeting_types_controller):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia w tabeli `meeting_types`.
    """
    controller = setup_meeting_types_controller

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba dodania typu spotkania po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.add_meeting_type("Konsylium terapeutyczne")

    # Próba pobrania typu spotkania po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.get_all_meeting_types()



