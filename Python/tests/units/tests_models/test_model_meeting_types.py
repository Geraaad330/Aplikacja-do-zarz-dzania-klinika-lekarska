# test_model_meeting_types.py

"""
Kiedy testować model bezpośrednio
Cel testów: Sprawdzenie poprawności działania tylko modelu, np. metod CRUD, które bezpośrednio operują na bazie danych.

    # Tworzenie tabeli `meeting_types`
    meeting_types_model = MeetingTypes(db_controller)
    meeting_types_model.create_table()

Użycie modelu MeetingTypes bezpośrednio
Na lewym ekranie klasa modelu (MeetingTypes) jest wywoływana bezpośrednio w każdym teście:

    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    meeting_types.create_new_record("Konsylium terapeutyczne")
    result = meeting_types.get_records()

Każdy test tworzy nową instancję klasy modelu, ponieważ model jest jedynym źródłem interakcji z tabelą meeting_types.
Dlaczego musisz wywoływać model w każdym teście?

Brak dedykowanego kontrolera, który zarządzałby modelem.
Model MeetingTypes jest używany jako jedyna warstwa do zarządzania danymi w tabeli.
Każdy test odpowiada bezpośrednio za inicjalizację obiektu modelu i jego użycie.
"""



import os
import pytest
from controllers.database_controller import DatabaseController
from models.meeting_types import MeetingTypes

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu meeting_types.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `meeting_types`
    meeting_types_model = MeetingTypes(db_controller)
    meeting_types_model.create_table()

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM meeting_types")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+

def test_create_new_record_success(setup_database):
    """
    Test poprawnego dodania rekordu.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    meeting_types.create_new_record("Konsylium terapeutyczne")
    result = meeting_types.get_records()

    assert len(result) == 1, "Rekord nie został poprawnie dodany."
    assert result[0]["meeting_type"] == "Konsylium terapeutyczne", "Nazwa typu spotkania jest niepoprawna."

    meeting_types.create_new_record("Superwizja ()")
    result = meeting_types.get_records()

    assert len(result) == 2, "Rekord nie został poprawnie dodany."
    assert result[1]["meeting_type"] == "Superwizja ()", "Nazwa typu spotkania jest niepoprawna."

    meeting_types.create_new_record("Szkolenie, wewnętrzne.")
    result = meeting_types.get_records()

    assert len(result) == 3, "Rekord nie został poprawnie dodany."
    assert result[2]["meeting_type"] == "Szkolenie, wewnętrzne.", "Nazwa typu spotkania jest niepoprawna."

    meeting_types.create_new_record("Spotkanie: zespołu/ interdyscyplinarnego")
    result = meeting_types.get_records()

    assert len(result) == 4, "Rekord nie został poprawnie dodany."
    assert result[3]["meeting_type"] == "Spotkanie: zespołu/ interdyscyplinarnego", "Nazwa typu spotkania jest niepoprawna."


def test_create_new_record_invalid_data(setup_database):
    """
    Test próby dodania rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    # Każdy przypadek niepoprawnych danych testowany osobno
    with pytest.raises(ValueError, match="Nazwa typu spotkania musi być ciągiem znaków."):
        meeting_types.create_new_record(123)

    with pytest.raises(ValueError, match="Nazwa typu spotkania nie może być pusta."):
        meeting_types.create_new_record("")

    with pytest.raises(ValueError, match="Nazwa typu spotkania musi mieć od 3 do 100 znaków."):
        meeting_types.create_new_record("AB")

    with pytest.raises(ValueError, match="Nazwa typu spotkania musi mieć od 3 do 100 znaków."):
        meeting_types.create_new_record("A" * 101)

    with pytest.raises(ValueError, match="Nazwa typu spotkania zawiera niedozwolone znaki."):
        meeting_types.create_new_record("!@#%&*")

    with pytest.raises(ValueError, match="Nazwa typu spotkania zawiera niedozwolone znaki."):
        meeting_types.create_new_record("Dietetyk 50%")

        


def test_create_new_record_duplicate(setup_database):
    """
    Test próby dodania rekordu z duplikatem.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    meeting_types.create_new_record("Konsylium terapeutyczne")

    with pytest.raises(ValueError, match="Typ spotkania o nazwie 'Konsylium terapeutyczne' już istnieje."):
        meeting_types.create_new_record("Konsylium terapeutyczne")


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

def test_update_record_success(setup_database):
    """
    Test poprawnej aktualizacji rekordu.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    meeting_types.create_new_record("Konsylium terapeutyczne")
    meeting_types.update_record(1, {"meeting_type": "Superwizja"})

    result = meeting_types.get_records()
    assert result[0]["meeting_type"] == "Superwizja", "Aktualizacja rekordu nie powiodła się."


def test_update_record_invalid_data(setup_database):
    """
    Test próby aktualizacji rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    meeting_types.create_new_record("Konsylium terapeutyczne")

    with pytest.raises(ValueError, match="Nazwa typu spotkania zawiera niedozwolone znaki."):
        meeting_types.update_record(1, {"meeting_type": "Superwizj@"})


def test_update_record_nonexistent_id(setup_database):
    """
    Test próby aktualizacji nieistniejącego rekordu.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        meeting_types.update_record(999, {"meeting_type": "Superwizja"})


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+

def test_delete_record_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    meeting_types.create_new_record("Konsylium terapeutyczne")
    meeting_types.delete_record(1)

    result = meeting_types.get_records()
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_record_nonexistent_id(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        meeting_types.delete_record(999)


# +-+-+-+- Testy metod pobierania i filtrowania -+-+-+-+-+

def test_get_records_empty_database(setup_database):
    """
    Test pobierania rekordów z pustej bazy.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    result = meeting_types.get_records()
    assert len(result) == 0, "Baza powinna być pusta."


def test_get_records_with_all_filters(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności filtrowania.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    # Dodanie danych testowych
    meeting_types.create_new_record("Konsylium terapeutyczne")
    meeting_types.create_new_record("Superwizja")
    meeting_types.create_new_record("Szkolenie wewnętrzne")
    meeting_types.create_new_record("Spotkanie zespołu interdyscyplinarnego")
    
    # Test: LIKE
    filters = [{"column": "meeting_type", "operator": "LIKE", "value": "%S%"}]
    result = meeting_types.get_records(filters=filters)
    assert len(result) == 4, "Filtracja LIKE nie zwróciła poprawnych wyników."

    # Test: =
    filters = [{"column": "meeting_type", "operator": "=", "value": "Konsylium terapeutyczne"}]
    result = meeting_types.get_records(filters=filters)
    assert len(result) == 1, "Filtracja = nie zwróciła poprawnych wyników."
    assert result[0]["meeting_type"] == "Konsylium terapeutyczne"

    # Test: IN
    filters = [{"column": "meeting_type", "operator": "IN", "value": ["Konsylium terapeutyczne", "Spotkanie zespołu interdyscyplinarnego"]}]
    result = meeting_types.get_records(filters=filters)
    assert len(result) == 2, "Filtracja IN nie zwróciła poprawnych wyników."

    # Test: IS NULL (brak danych null w tabeli, baza powinna zwrócić 0 wyników)
    filters = [{"column": "meeting_type", "operator": "IS NULL"}]
    result = meeting_types.get_records(filters=filters)
    assert len(result) == 0, "Filtracja IS NULL nie powinna zwrócić wyników."

    # Test: IS NOT NULL
    filters = [{"column": "meeting_type", "operator": "IS NOT NULL"}]
    result = meeting_types.get_records(filters=filters)
    assert len(result) == 4, "Filtracja IS NOT NULL nie zwróciła poprawnych wyników."


def test_get_records_with_all_sorting(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności sortowania.
    """
    db_controller = setup_database
    meeting_types = MeetingTypes(db_controller)

    # Dodanie danych testowych
    meeting_types.create_new_record("Spotkanie zespołu interdyscyplinarnego")
    meeting_types.create_new_record("Szkolenie wewnętrzne")
    meeting_types.create_new_record("Superwizja")
    meeting_types.create_new_record("Konsylium terapeutyczne")
    
    # Test: Sortowanie rosnące
    sort_by = [("meeting_type", "ASC")]
    result = meeting_types.get_records(sort_by=sort_by)
    assert result[0]["meeting_type"] == "Konsylium terapeutyczne", "Sortowanie ASC nie działa poprawnie."
    assert result[-1]["meeting_type"] == "Szkolenie wewnętrzne"

    # Test: Sortowanie malejące
    sort_by = [("meeting_type", "DESC")]
    result = meeting_types.get_records(sort_by=sort_by)
    assert result[0]["meeting_type"] == "Szkolenie wewnętrzne", "Sortowanie DESC nie działa poprawnie."
    assert result[-1]["meeting_type"] == "Konsylium terapeutyczne"

    # Test: Wielokrotne sortowanie (przykład z jedną kolumną i dwoma różnymi kierunkami)
    sort_by = [("meeting_type", "ASC")]
    result = meeting_types.get_records(sort_by=sort_by)
    assert result[0]["meeting_type"] == "Konsylium terapeutyczne", "Wielokrotne sortowanie nie działa poprawnie."

    # Dodanie kolejnego rekordu dla testowania stabilności sortowania
    meeting_types.create_new_record("Adupa")
    sort_by = [("meeting_type", "ASC")]
    result = meeting_types.get_records(sort_by=sort_by)
    assert result[0]["meeting_type"] == "Adupa", "Sortowanie z dużą ilością rekordów nie działa poprawnie."
