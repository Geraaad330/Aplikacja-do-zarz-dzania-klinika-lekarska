# test_integration_form_types.py

"""
W testach integracyjnych nie ma potrzeby testowania wszystkich możliwych przypadków poprawnych i niepoprawnych danych — 
ich celem nie jest pełna walidacja danych, lecz sprawdzenie, czy przepływ informacji między różnymi komponentami systemu 
(np. kontrolerami, modelami, bazą danych) działa poprawnie.

Dobre praktyki programowania w kontekście testów integracyjnych:
Skupienie na przepływie danych i integracji:

Testy integracyjne mają za zadanie upewnić się, że różne warstwy aplikacji (np. kontrolery, modele, baza danych) współpracują 
ze sobą bez problemów.To oznacza, że wystarczy przetestować jeden reprezentatywny przypadek z poprawnymi danymi i jeden z 
niepoprawnymi. Dzięki temu możesz sprawdzić, czy:

    Dane przechodzą poprawnie przez wszystkie warstwy systemu.
    Obsługa błędów działa zgodnie z oczekiwaniami.

Pełna walidacja w testach jednostkowych:

    Testy jednostkowe (np. dla funkcji walidacji) są odpowiedzialne za sprawdzenie wszystkich możliwych przypadków poprawnych i 
    niepoprawnych danych. 
    Testy jednostkowe są szybkie, izolowane i pozwalają łatwo znaleźć źródło problemu, dlatego to one powinny pokrywać wszystkie 
    przypadki brzegowe i złożone scenariusze.

"""


import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.form_types_controller import FormTypesController
from models.form_types import FormTypes

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_form_types_controller")
def setup_form_types_controller_fixture():
    """
    Kod definiuje fixture w testach wykorzystujących bibliotekę pytest. Fixture o nazwie setup_form_types_controller_fixture służy do:
        Skonfigurowania bazy danych i utworzenia tabeli form_types.
        Zainicjalizowania kontrolera FormTypesController oraz jego środowiska przed każdym testem.
        Wyczyszczenia danych w tabeli form_types przed rozpoczęciem testów, aby zapewnić niezależność testów.
    Dekorator @pytest.fixture:
        Deklaruje funkcję jako fixture w pytest. Fixture pozwala przygotować dane lub środowisko testowe, które może być później wielokrotnie używane w różnych testach.
        Parametr name="setup_form_types_controller" definiuje, że fixture będzie dostępny pod tą nazwą w testach.
    Funkcja setup_form_types_controller_fixture:
        Jest to właściwa implementacja fixture. Wszystko, co jest w tej funkcji, zostanie wykonane za każdym razem, gdy fixture będzie używane w testach.
    """
    # DatabaseController() tworzy nową instancję kontrolera bazy danych.
    # connect_to_database() nawiązuje połączenie z bazą danych. Może to być lokalna baza (np. SQLite) lub zewnętrzna (np. MySQL/PostgreSQL).
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # FormTypesController to obiekt kontrolera, który zarządza danymi w tabeli form_types.
    # Kontroler ten korzysta z db_controller jako źródła połączenia z bazą danych.
    form_types_controller = FormTypesController(db_controller)
    form_types_controller.create_table()

    # Tworzenie tabeli `form_types`
    # FormTypes to model, który reprezentuje tabelę form_types w bazie danych.
    # create_table() zapewnia, że tabela form_types istnieje (tworzy ją, jeśli nie istnieje).
    form_types_model = FormTypes(db_controller)
    form_types_model.create_table()

    # Czyszczenie danych przed każdym testem
    db_controller.connection.execute("DELETE FROM form_types")
    db_controller.connection.commit()

    yield form_types_controller

# def ... (setup_form_types_controller) -> setup_form_types_controller w nawiasie przygotowuje środowisko testowe:
# Tworzy połączenie z bazą danych. Tworzy tabelę form_types. Czyści tabelę przed każdym testem, zapewniając niezależność testów.
def test_add_form_types_with_valid_data(setup_form_types_controller):
    """
    Testuje dodawanie nowej typu spotkania z poprawnymi danymi.
    """
    # controller to dowolna nazwa zmiennej
    # controller przypisuje narzędzie setup_form_types_controller, które pozwala zarządzać tabelą w bazie danych.
    # Obiekt controller pozwala wykonywać operacje na tabeli form_types w bazie danych (np. dodawanie, pobieranie, aktualizowanie rekordów).
    controller = setup_form_types_controller
    # teraz za pomocą metody controller możemy wykonywać operacje na bazie danych dzięki przypisaniu controller = setup_form_types_controller
    controller.add_form_types("Zgoda na leczenie")

    # przypisujemy do form_types wynik pobrania danych get_all_form_types() dzięki metodzie controller przypisaną do etup_form_types_controller
    form_types = controller.get_all_form_types()
    assert len(form_types) == 1
    assert form_types[0]["form_name"] == "Zgoda na leczenie"

def test_add_form_types_with_invalid_data(setup_form_types_controller):
    """
    Testuje dodawanie nowej typu spotkania z niepoprawnymi danymi.
    """
    controller = setup_form_types_controller

    with pytest.raises(ValueError, match="Błąd walidacji: Nazwa formularza nie może być pusta."):
        controller.add_form_types("")

    with pytest.raises(ValueError, match="Nazwa formularza musi mieć od 3 do 100 znaków."):
        controller.add_form_types("AB")



def test_update_form_types_with_valid_data(setup_form_types_controller):
    """
    Testuje aktualizację typu spotkania z poprawnymi danymi.
    """
    controller = setup_form_types_controller

    # Dodanie typu spotkania
    controller.add_form_types("Zgoda na leczenie")
    form_types_variable = controller.get_all_form_types()[0]

    # Aktualizacja
    updates = {"form_name": "Zgoda na przetwarzanie danych osobowych (RODO)"}
    controller.update_form_types(form_types_variable["form_type_id"], updates)

    updated_form_types_variable = controller.get_all_form_types()[0]
    assert updated_form_types_variable["form_name"] == "Zgoda na przetwarzanie danych osobowych (RODO)"

def test_update_form_types_with_invalid_data(setup_form_types_controller):
    """
    Testuje aktualizację typu spotkania z niepoprawnymi danymi.
    """
    controller = setup_form_types_controller

    # Dodanie typu spotkania
    controller.add_form_types("Zgoda na leczenie")
    form_types_variable = controller.get_all_form_types()[0]

    with pytest.raises(ValueError, match="Nazwa formularza nie może być pusta."):
        controller.update_form_types(form_types_variable["form_type_id"], {"form_name": ""})


def test_update_nonexistent_form_types_variable(setup_form_types_controller):
    """
    Testuje aktualizację rekordu, który nie istnieje.
    """
    controller = setup_form_types_controller

    updates = {"form_name": "Zgoda na przetwarzanie danych osobowych (RODO)"}
    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.update_form_types(999, updates)






def test_delete_nonexistent_form_types_variable(setup_form_types_controller):
    """
    Testuje usuwanie rekordu, który nie istnieje.
    """
    controller = setup_form_types_controller

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.delete_form_types(999)


def test_delete_form_types(setup_form_types_controller):
    """
    Testuje usuwanie typu spotkania.
    """
    controller = setup_form_types_controller

    # Dodanie typu spotkania
    controller.add_form_types("Zgoda na leczenie")
    form_types_variable = controller.get_all_form_types()[0]

    # Usuwanie
    controller.delete_form_types(form_types_variable["form_type_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM form_types").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_delete_form_types."



def test_full_crud_flow(setup_form_types_controller):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """
    controller = setup_form_types_controller

    # Dodanie typu spotkania
    controller.add_form_types("Zgoda na leczenie")
    form_types_variable = controller.get_all_form_types()[0]
    assert form_types_variable["form_name"] == "Zgoda na leczenie"

    # Aktualizacja typu spotkania
    updates = {"form_name": "Zgoda na przetwarzanie danych osobowych (RODO)"}
    controller.update_form_types(form_types_variable["form_type_id"], updates)
    updated_form_types_variable = controller.get_all_form_types()[0]
    assert updated_form_types_variable["form_name"] == "Zgoda na przetwarzanie danych osobowych (RODO)"

    # Usuwanie typu spotkania
    controller.delete_form_types(updated_form_types_variable["form_type_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM form_types").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_full_crud_flow."


def test_get_form_types_with_filters(setup_form_types_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości filtracji.
    """
    controller = setup_form_types_controller

    # Dodanie danych
    controller.add_form_types("Zgoda na udostępnienie danych medycznych")
    controller.add_form_types("Zgoda na uczestnictwo w badaniach klinicznych")

    filters = [{"column": "form_name", "operator": "LIKE", "value": "%zgoda%"}]
    results = controller.get_form_types_with_filters(filters=filters)

    assert len(results) == 2
    assert results[0]["form_name"] == "Zgoda na udostępnienie danych medycznych"


def test_get_form_types_with_sorting(setup_form_types_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości sortowania.
    """
    controller = setup_form_types_controller

    # Dodanie danych
    controller.add_form_types("Zgoda na nagrywanie sesji terapeutycznych")
    controller.add_form_types("Zgoda na przetwarzanie danych osobowych (RODO)")
    controller.add_form_types("Zgoda na leczenie")

    # Sortowanie alfabetyczne rosnąco
    results = controller.get_form_types_with_filters(sort_by=[("form_name", "ASC")])
    assert results[0]["form_name"] == "Zgoda na leczenie"

    # Sortowanie alfabetyczne malejąco
    results = controller.get_form_types_with_filters(sort_by=[("form_name", "DESC")])
    assert results[0]["form_name"] == "Zgoda na przetwarzanie danych osobowych (RODO)"




def test_database_disconnection_handling_form_types(setup_form_types_controller):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia w tabeli `form_types`.
    """
    controller = setup_form_types_controller

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba dodania typu spotkania po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.add_form_types("Zgoda na leczenie")

    # Próba pobrania typu spotkania po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.get_all_form_types()



