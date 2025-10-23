# test_model_room_types.py

"""
Kiedy testować model bezpośrednio
Cel testów: Sprawdzenie poprawności działania tylko modelu, np. metod CRUD, które bezpośrednio operują na bazie danych.

    # Tworzenie tabeli `room_types`
    room_types_model = roomTypes(db_controller)
    room_types_model.create_table()

Użycie modelu roomTypes bezpośrednio
Na lewym ekranie klasa modelu (roomTypes) jest wywoływana bezpośrednio w każdym teście:

    db_controller = setup_database
    room_types = roomTypes(db_controller)

    room_types.create_new_record("Gabinet diagnostyczny")
    result = room_types.get_records()

Każdy test tworzy nową instancję klasy modelu, ponieważ model jest jedynym źródłem interakcji z tabelą room_types.

Dlaczego musisz wywoływać model w każdym teście?

Brak dedykowanego kontrolera, który zarządzałby modelem.
Model roomTypes jest używany jako jedyna warstwa do zarządzania danymi w tabeli.
Każdy test odpowiada bezpośrednio za inicjalizację obiektu modelu i jego użycie.
"""

import os
import pytest
from controllers.database_controller import DatabaseController
from models.room_types import RoomTypes

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu room_types.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `room_types`
    room_types_model = RoomTypes(db_controller)
    room_types_model.create_table()

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM room_types")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+

def test_create_new_record_success(setup_database):
    """
    Test poprawnego dodania rekordu.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    room_types.create_new_record("Gabinet diagnostyczny")
    result = room_types.get_records()

    assert len(result) == 1, "Rekord nie został poprawnie dodany."
    assert result[0]["room_type"] == "Gabinet diagnostyczny", "Nazwa typu pokoju jest niepoprawna."

    room_types.create_new_record("Gabinet psychoterapeutyczny - Test (Zaawansowany)")
    result = room_types.get_records()

    assert len(result) == 2, "Rekord nie został poprawnie dodany."
    assert result[1]["room_type"] == "Gabinet psychoterapeutyczny - Test (Zaawansowany)", "Nazwa typu pokoju jest niepoprawna."

    room_types.create_new_record("Sala: terapii grupowej")
    result = room_types.get_records()

    assert len(result) == 3, "Rekord nie został poprawnie dodany."
    assert result[2]["room_type"] == "Sala: terapii grupowej", "Nazwa typu pokoju jest niepoprawna."

    room_types.create_new_record("Biuro, recepcji.")
    result = room_types.get_records()

    assert len(result) == 4, "Rekord nie został poprawnie dodany."
    assert result[3]["room_type"] == "Biuro, recepcji.", "Nazwa typu pokoju jest niepoprawna."


def test_create_new_record_invalid_data(setup_database):
    """
    Test próby dodania rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    # Każdy przypadek niepoprawnych danych testowany osobno
    with pytest.raises(ValueError, match="Nazwa typu pokoju musi być ciągiem znaków."):
        room_types.create_new_record(123)

    with pytest.raises(ValueError, match="Nazwa typu pokoju nie może być pusta."):
        room_types.create_new_record("")

    with pytest.raises(ValueError, match="Nazwa typu pokoju musi mieć od 3 do 100 znaków."):
        room_types.create_new_record("AB")

    with pytest.raises(ValueError, match="Nazwa typu pokoju musi mieć od 3 do 100 znaków."):
        room_types.create_new_record("A" * 101)

    with pytest.raises(ValueError, match="Nazwa typu pokoju zawiera niedozwolone znaki."):
        room_types.create_new_record("!@#%&*")

    with pytest.raises(ValueError, match="Nazwa typu pokoju zawiera niedozwolone znaki."):
        room_types.create_new_record("Gabinet diagnostyczny 50%")

        


def test_create_new_record_duplicate(setup_database):
    """
    Test próby dodania rekordu z duplikatem.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    room_types.create_new_record("Gabinet diagnostyczny")

    with pytest.raises(ValueError, match="Typ pokoju o nazwie 'Gabinet diagnostyczny' już istnieje."):
        room_types.create_new_record("Gabinet diagnostyczny")


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

def test_update_record_success(setup_database):
    """
    Test poprawnej aktualizacji rekordu.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    room_types.create_new_record("Gabinet diagnostyczny")
    room_types.update_record(1, {"room_type": "Gabinet diagnostyczny"})

    result = room_types.get_records()
    assert result[0]["room_type"] == "Gabinet diagnostyczny", "Aktualizacja rekordu nie powiodła się."


def test_update_record_invalid_data(setup_database):
    """
    Test próby aktualizacji rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    room_types.create_new_record("Gabinet diagnostyczny")

    with pytest.raises(ValueError, match="Nazwa typu pokoju zawiera niedozwolone znaki."):
        room_types.update_record(1, {"room_type": "G@binet diagn0styczny"})
        
    with pytest.raises(ValueError, match="Nazwa typu pokoju nie może zawierać cyfr."):
        room_types.update_record(1, {"room_type": "123"})

    with pytest.raises(ValueError, match="Nazwa typu pokoju nie może być pusta."):
        room_types.update_record(1, {"room_type": ""})

    with pytest.raises(ValueError, match="Nazwa typu pokoju musi mieć od 3 do 100 znaków."):
        room_types.update_record(1, {"room_type": "AB"})


def test_update_record_nonexistent_id(setup_database):
    """
    Test próby aktualizacji nieistniejącego rekordu.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        room_types.update_record(999, {"room_type": "Gabinet diagnostyczny"})


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+

def test_delete_record_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    room_types.create_new_record("Gabinet diagnostyczny")
    room_types.delete_record(1)

    result = room_types.get_records()
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_record_nonexistent_id(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        room_types.delete_record(999)


# +-+-+-+- Testy metod pobierania i filtrowania -+-+-+-+-+

def test_get_records_empty_database(setup_database):
    """
    Test pobierania rekordów z pustej bazy.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    result = room_types.get_records()
    assert len(result) == 0, "Baza powinna być pusta."


def test_get_records_with_all_filters(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności filtrowania.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    # Dodanie danych testowych
    room_types.create_new_record("Gabinet diagnostyczny")
    room_types.create_new_record("Gabinet psychoterapeutyczny")
    room_types.create_new_record("Gabinet psychiatryczny")
    
    # Test: LIKE
    filters = [{"column": "room_type", "operator": "LIKE", "value": "%GABINET%"}]
    result = room_types.get_records(filters=filters)
    assert len(result) == 3, "Filtracja LIKE nie zwróciła poprawnych wyników."

    # Test: =
    filters = [{"column": "room_type", "operator": "=", "value": "Gabinet diagnostyczny"}]
    result = room_types.get_records(filters=filters)
    assert len(result) == 1, "Filtracja = nie zwróciła poprawnych wyników."
    assert result[0]["room_type"] == "Gabinet diagnostyczny"

    # Test: IN
    filters = [{"column": "room_type", "operator": "IN", "value": ["Gabinet diagnostyczny", "Gabinet psychiatryczny"]}]
    result = room_types.get_records(filters=filters)
    assert len(result) == 2, "Filtracja IN nie zwróciła poprawnych wyników."

    # Test: IS NULL (brak danych null w tabeli, baza powinna zwrócić 0 wyników)
    filters = [{"column": "room_type", "operator": "IS NULL"}]
    result = room_types.get_records(filters=filters)
    assert len(result) == 0, "Filtracja IS NULL nie powinna zwrócić wyników."

    # Test: IS NOT NULL
    filters = [{"column": "room_type", "operator": "IS NOT NULL"}]
    result = room_types.get_records(filters=filters)
    assert len(result) == 3, "Filtracja IS NOT NULL nie zwróciła poprawnych wyników."


def test_get_records_with_all_sorting(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności sortowania.
    """
    db_controller = setup_database
    room_types = RoomTypes(db_controller)

    # Dodanie danych testowych
    room_types.create_new_record("Sala terapii grupowej")
    room_types.create_new_record("Sala terapii rodzinnej")
    room_types.create_new_record("Gabinet psychiatryczny")
    room_types.create_new_record("Gabinet diagnostyczny")
    
    # Test: Sortowanie rosnące
    sort_by = [("room_type", "ASC")]
    result = room_types.get_records(sort_by=sort_by)
    assert result[0]["room_type"] == "Gabinet diagnostyczny", "Sortowanie ASC nie działa poprawnie."
    assert result[-1]["room_type"] == "Sala terapii rodzinnej"

    # Test: Sortowanie malejące
    sort_by = [("room_type", "DESC")]
    result = room_types.get_records(sort_by=sort_by)
    assert result[0]["room_type"] == "Sala terapii rodzinnej", "Sortowanie DESC nie działa poprawnie."
    assert result[-1]["room_type"] == "Gabinet diagnostyczny"

    # Test: Wielokrotne sortowanie (przykład z jedną kolumną i dwoma różnymi kierunkami)
    sort_by = [("room_type", "ASC")]
    result = room_types.get_records(sort_by=sort_by)
    assert result[0]["room_type"] == "Gabinet diagnostyczny", "Wielokrotne sortowanie nie działa poprawnie."

    # Dodanie kolejnego rekordu dla testowania stabilności sortowania
    room_types.create_new_record("Adupa")
    sort_by = [("room_type", "ASC")]
    result = room_types.get_records(sort_by=sort_by)
    assert result[0]["room_type"] == "Adupa", "Sortowanie z dużą ilością rekordów nie działa poprawnie."
