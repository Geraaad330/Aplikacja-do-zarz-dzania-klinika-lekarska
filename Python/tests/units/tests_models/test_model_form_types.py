# test_model_form_types.py

"""
Kiedy testować model bezpośrednio
Cel testów: Sprawdzenie poprawności działania tylko modelu, np. metod CRUD, które bezpośrednio operują na bazie danych.

    # Tworzenie tabeli `form_types`
    form_types_model = FormTypes(db_controller)
    form_types_model.create_table()

Użycie modelu FormTypes bezpośrednio
Na lewym ekranie klasa modelu (FormTypes) jest wywoływana bezpośrednio w każdym teście:

    db_controller = setup_database
    form_types = FormTypes(db_controller)

    form_types.create_new_record("Zgoda na leczenie")
    result = form_types.get_records()

Każdy test tworzy nową instancję klasy modelu, ponieważ model jest jedynym źródłem interakcji z tabelą form_types.

Dlaczego musisz wywoływać model w każdym teście?

Brak dedykowanego kontrolera, który zarządzałby modelem.
Model FormTypes jest używany jako jedyna warstwa do zarządzania danymi w tabeli.
Każdy test odpowiada bezpośrednio za inicjalizację obiektu modelu i jego użycie.
"""

import os
import pytest
from controllers.database_controller import DatabaseController
from models.form_types import FormTypes

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    2. Wykonanie fixture: Pytest wywołuje funkcję setup_database_fixture przed rozpoczęciem kodu testu:

    Kod fixture:
        Tworzy db_controller i nawiązuje połączenie z bazą.
        Tworzy tabelę form_types.
        Zwraca db_controller (za pomocą yield), co pozwala testowi korzystać z tego obiektu.

    3. Wykonanie testu: Dopiero po zakończeniu kodu przed yield, pytest przekazuje wynik fixture (db_controller) do testu:
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `form_types`
    form_types_model = FormTypes(db_controller)
    form_types_model.create_table()

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM form_types")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+

# 1. TEST WIDZI FUNKCJĘ def test_create_new_record_success(setup_database): I PRZECHODZI DO fixture o nazwie setup_database.
# Kiedy używasz setup_database jako argument funkcji testowej, pytest automatycznie uruchamia tę fixture przed wykonaniem testu
# i zwraca wynik (w tym przypadku obiekt db_controller).

# 3. Wykonanie testu: Dopiero po zakończeniu kodu przed yield, pytest przekazuje wynik fixture (db_controller) do testu:
# Test może teraz używać db_controller dostarczonego przez fixture.
def test_create_new_record_success(setup_database): 
    """
    Test poprawnego dodania rekordu.
    """
    # DLACZEGO W KAŻDYM TEŚCIE JEST form_types = FormTypes(db_controller) INACZEJ NIŻ W TEŚCIE INTEGRACYJNYM
    # Skupia się na testowaniu jednego konkretnego modelu (np. FormTypes).
    # Operuje bezpośrednio na bazie danych za pomocą metod modelu, pomijając inne części systemu.
    # Fixture setup_database zapewnia czyste środowisko bazodanowe, ale jest ono ograniczone do testowanej tabeli i jej operacji.

    # pylint: disable=W0105
    """ 
    db_controller = setup_database # to jest "przejście" do fixture do kodu db_controler i wykonanie 
    Gdy w teście wywołujesz db_controller = setup_database, pytest automatycznie wykonuje fixture setup_database_fixture, 
    która tworzy obiekt DatabaseController i nawiązuje połączenie z bazą danych.
    """
    db_controller = setup_database 
    # pylint: disable=W0105
    """ 
    Tworzenie obiektu FormTypes:

    FormTypes(db_controller) tworzy nową instancję klasy FormTypes.
    W konstruktorze (metodzie __init__) klasy FormTypes obiekt db_controller zostaje zapisany wewnątrz tej instancji, aby umożliwić komunikację z bazą danych.
    Przekazanie db_controller:

    db_controller to obiekt DatabaseController, który zarządza połączeniem z bazą danych. Dzięki temu klasa FormTypes może wykonywać operacje SQL na tabeli form_types.
    Przypisanie do form_types:

    Nowo utworzona instancja FormTypes jest przypisana do zmiennej form_types, co pozwala później wywoływać metody tej klasy, np.:
    python
    Skopiuj kod
    form_types.create_new_record("Zgoda na leczenie")
    form_types.get_records()
    """
    form_types = FormTypes(db_controller) 

    form_types.create_new_record("Zgoda na leczenie")
    result = form_types.get_records()

    assert len(result) == 1, "Rekord nie został poprawnie dodany."
    assert result[0]["form_name"] == "Zgoda na leczenie", "Nazwa formularza jest niepoprawna."


    form_types.create_new_record("Zgoda na przetwarzanie danych osobowych: - (RODO)")
    result = form_types.get_records()

    assert len(result) == 2, "Rekord nie został poprawnie dodany."
    assert result[1]["form_name"] == "Zgoda na przetwarzanie danych osobowych: - (RODO)", "Nazwa formularza jest niepoprawna."


    form_types.create_new_record("Zgoda, na / udostępnienie, danych medycznych.")
    result = form_types.get_records()

    assert len(result) == 3, "Rekord nie został poprawnie dodany."
    assert result[2]["form_name"] == "Zgoda, na / udostępnienie, danych medycznych.", "Nazwa formularza jest niepoprawna."


def test_create_new_record_invalid_data(setup_database):
    """
    Test próby dodania rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    # Każdy przypadek niepoprawnych danych testowany osobno
    with pytest.raises(ValueError, match="Nazwa formularza musi być ciągiem znaków."):
        form_types.create_new_record(123)

    with pytest.raises(ValueError, match="Nazwa formularza nie może być pusta."):
        form_types.create_new_record("")

    with pytest.raises(ValueError, match="Nazwa formularza musi mieć od 3 do 100 znaków."):
        form_types.create_new_record("AB")

    with pytest.raises(ValueError, match="Nazwa formularza musi mieć od 3 do 100 znaków."):
        form_types.create_new_record("A" * 101)

    with pytest.raises(ValueError, match="Nazwa formularza zawiera niedozwolone znaki."):
        form_types.create_new_record("!@#%&*")

    with pytest.raises(ValueError, match="Nazwa formularza zawiera niedozwolone znaki."):
        form_types.create_new_record("Zgoda na leczenie 50%")

        


def test_create_new_record_duplicate(setup_database):
    """
    Test próby dodania rekordu z duplikatem.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    form_types.create_new_record("Zgoda na leczenie")

    with pytest.raises(ValueError, match="Formularz o nazwie 'Zgoda na leczenie' już istnieje."):
        form_types.create_new_record("Zgoda na leczenie")


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

def test_update_record_success(setup_database):
    """
    Test poprawnej aktualizacji rekordu.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    form_types.create_new_record("Zgoda na leczenie")
    form_types.update_record(1, {"form_name": "Zgoda na nagrywanie sesji terapeutycznych"})

    result = form_types.get_records()
    assert result[0]["form_name"] == "Zgoda na nagrywanie sesji terapeutycznych", "Aktualizacja rekordu nie powiodła się."


def test_update_record_invalid_data(setup_database):
    """
    Test próby aktualizacji rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    form_types.create_new_record("Zgoda na leczenie")

    with pytest.raises(ValueError, match="Nazwa formularza zawiera niedozwolone znaki."):
        form_types.update_record(1, {"form_name": "G@binet diagn0styczny"})
        
    with pytest.raises(ValueError, match="Nazwa formularza nie może zawierać cyfr."):
        form_types.update_record(1, {"form_name": "123"})

    with pytest.raises(ValueError, match="Nazwa formularza nie może być pusta."):
        form_types.update_record(1, {"form_name": ""})

    with pytest.raises(ValueError, match="Nazwa formularza musi mieć od 3 do 100 znaków."):
        form_types.update_record(1, {"form_name": "AB"})


def test_update_record_nonexistent_id(setup_database):
    """
    Test próby aktualizacji nieistniejącego rekordu.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        form_types.update_record(999, {"form_name": "Zgoda na leczenie"})


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+

def test_delete_record_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database # uruchomienie fixture
    form_types = FormTypes(db_controller)

    form_types.create_new_record("Zgoda na leczenie")
    form_types.delete_record(1)

    result = form_types.get_records()
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_record_nonexistent_id(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        form_types.delete_record(999)


# +-+-+-+- Testy metod pobierania i filtrowania -+-+-+-+-+

def test_get_records_empty_database(setup_database):
    """
    Test pobierania rekordów z pustej bazy.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    result = form_types.get_records()
    assert len(result) == 0, "Baza powinna być pusta."


def test_get_records_with_all_filters(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności filtrowania.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    # Dodanie danych testowych
    form_types.create_new_record("Zgoda na leczenie")
    form_types.create_new_record("Zgoda na przetwarzanie danych osobowych (RODO)")
    form_types.create_new_record("Zgoda na udostępnienie danych medycznych")
    
    # Test: LIKE
    filters = [{"column": "form_name", "operator": "LIKE", "value": "Zgoda na%"}]
    result = form_types.get_records(filters=filters)
    assert len(result) == 3, "Filtracja LIKE nie zwróciła poprawnych wyników."

    # Test: =
    filters = [{"column": "form_name", "operator": "=", "value": "Zgoda na leczenie"}]
    result = form_types.get_records(filters=filters)
    assert len(result) == 1, "Filtracja = nie zwróciła poprawnych wyników."
    assert result[0]["form_name"] == "Zgoda na leczenie"

    # Test: IN
    filters = [{"column": "form_name", "operator": "IN", "value": ["Zgoda na leczenie", "Zgoda na udostępnienie danych medycznych"]}]
    result = form_types.get_records(filters=filters)
    assert len(result) == 2, "Filtracja IN nie zwróciła poprawnych wyników."

    # Test: IS NULL (brak danych null w tabeli, baza powinna zwrócić 0 wyników)
    filters = [{"column": "form_name", "operator": "IS NULL"}]
    result = form_types.get_records(filters=filters)
    assert len(result) == 0, "Filtracja IS NULL nie powinna zwrócić wyników."

    # Test: IS NOT NULL
    filters = [{"column": "form_name", "operator": "IS NOT NULL"}]
    result = form_types.get_records(filters=filters)
    assert len(result) == 3, "Filtracja IS NOT NULL nie zwróciła poprawnych wyników."


def test_get_records_with_all_sorting(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności sortowania.
    """
    db_controller = setup_database
    form_types = FormTypes(db_controller)

    # Dodanie danych testowych
    form_types.create_new_record("Zgoda na przetwarzanie danych osobowych (RODO)")
    form_types.create_new_record("Zgoda na udostępnienie danych medycznych")
    form_types.create_new_record("Zgoda na uczestnictwo w badaniach klinicznych")
    form_types.create_new_record("Zgoda na leczenie")
    
    # Test: Sortowanie rosnące
    sort_by = [("form_name", "ASC")]
    result = form_types.get_records(sort_by=sort_by)
    assert result[0]["form_name"] == "Zgoda na leczenie", "Sortowanie ASC nie działa poprawnie."
    assert result[-1]["form_name"] == "Zgoda na udostępnienie danych medycznych"

    # Test: Sortowanie malejące
    sort_by = [("form_name", "DESC")]
    result = form_types.get_records(sort_by=sort_by)
    assert result[0]["form_name"] == "Zgoda na udostępnienie danych medycznych", "Sortowanie DESC nie działa poprawnie."
    assert result[-1]["form_name"] == "Zgoda na leczenie"

    # Test: Wielokrotne sortowanie (przykład z jedną kolumną i dwoma różnymi kierunkami)
    sort_by = [("form_name", "ASC")]
    result = form_types.get_records(sort_by=sort_by)
    assert result[0]["form_name"] == "Zgoda na leczenie", "Wielokrotne sortowanie nie działa poprawnie."

    # Dodanie kolejnego rekordu dla testowania stabilności sortowania
    form_types.create_new_record("Adupa")
    sort_by = [("form_name", "ASC")]
    result = form_types.get_records(sort_by=sort_by)
    assert result[0]["form_name"] == "Adupa", "Sortowanie z dużą ilością rekordów nie działa poprawnie."
