# test_model_services.py

import os
import pytest
from controllers.database_controller import DatabaseController
from models.services import Services

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu Services.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `services`
    services_model = Services(db_controller)
    services_model.create_table()

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM services")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+

def test_create_new_record_success(setup_database):
    """
    Test poprawnego dodania rekordu.
    """
    db_controller = setup_database
    services = Services(db_controller)

    services.create_new_record("Usługa A", 60, 100)
    result = services.get_records()

    assert len(result) == 1, "Rekord nie został poprawnie dodany."
    assert result[0]["service_type"] == "Usługa A", "Nazwa usługi jest niepoprawna."
    assert result[0]["duration_minutes"] == 60, "Czas trwania jest niepoprawny."
    assert result[0]["service_price"] == 100, "Cena usługi jest niepoprawna."


def test_create_new_record_invalid_data(setup_database):
    """
    Test próby dodania rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    services = Services(db_controller)

    with pytest.raises(ValueError, match="service_type zawiera niedozwolone znaki."):
        services.create_new_record("Usługa@", 60, 100)

    with pytest.raises(ValueError, match="Czas trwania musi być pomiędzy 1 a 300 minut."):
        services.create_new_record("Usługa B", 0, 100)

    with pytest.raises(ValueError, match="Cena usługi musi być pomiędzy 1 a 500."):
        services.create_new_record("Usługa C", 60, 600)


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

def test_update_record_success(setup_database):
    """
    Test poprawnej aktualizacji rekordu.
    """
    db_controller = setup_database
    services = Services(db_controller)

    services.create_new_record("Usługa A", 60, 100)
    services.update_record(1, {"service_type": "Usługa B", "service_price": 200})

    result = services.get_records()
    assert result[0]["service_type"] == "Usługa B", "Nazwa usługi nie została poprawnie zaktualizowana."
    assert result[0]["service_price"] == 200, "Cena usługi nie została poprawnie zaktualizowana."


def test_update_record_invalid_data(setup_database):
    """
    Test próby aktualizacji rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    services = Services(db_controller)

    services.create_new_record("Usługa A", 60, 100)

    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        services.update_record(1, {})

    with pytest.raises(ValueError, match="service_type zawiera niedozwolone znaki."):
        services.update_record(1, {"service_type": "Usługa@"})


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+

def test_delete_record_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database
    services = Services(db_controller)

    services.create_new_record("Usługa A", 60, 100)
    services.delete_record(1)

    result = services.get_records()
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_record_nonexistent_id(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    services = Services(db_controller)

    with pytest.raises(ValueError, match="Rekord z service_id = 1 nie istnieje w tabeli services."):
        services.delete_record(1)


# +-+-+-+- Testy metod pobierania i filtrowania -+-+-+-+-+

def test_get_records_empty_database(setup_database):
    """
    Test pobierania rekordów z pustej bazy.
    """
    db_controller = setup_database
    services = Services(db_controller)

    result = services.get_records()
    assert len(result) == 0, "Baza powinna być pusta."


def test_get_records_with_filters(setup_database):
    """
    Test pobierania rekordów z różnymi warunkami filtrowania.
    """
    db_controller = setup_database
    services = Services(db_controller)

    # Dodanie danych
    services.create_new_record("Usługa A", 1, 100)
    services.create_new_record("Usługa B", 300, 200)
    services.create_new_record("Usługa C", 180, 300)

    # Filtr: `service_price > 100`
    filters = [{"column": "service_price", "operator": ">", "value": 100}]
    result = services.get_records(filters=filters)
    assert len(result) == 2, "Filtracja z `>` zwróciła niepoprawne wyniki."

    # Filtr: `service_price BETWEEN 100 AND 200`
    filters = [{"column": "service_price", "operator": "BETWEEN", "value": (100, 200)}]
    result = services.get_records(filters=filters)
    assert len(result) == 2, "Filtracja z `BETWEEN` zwróciła niepoprawne wyniki."

    # Filtr: `service_type LIKE '%A%'`
    filters = [{"column": "service_type", "operator": "LIKE", "value": "Usługa A"}]
    result = services.get_records(filters=filters)
    assert len(result) == 1, "Filtracja z `LIKE` zwróciła niepoprawne wyniki."
    assert result[0]["service_type"] == "Usługa A", "Niepoprawny wynik dla `LIKE`."

    # Filtry wielokrotne
    filters = [
        {"column": "service_price", "operator": "<", "value": 300},
        {"column": "duration_minutes", "operator": ">", "value": 60}
    ]
    result = services.get_records(filters=filters)
    assert len(result) == 1, "Filtracja wielokrotna zwróciła niepoprawne wyniki."

    # Filtr: `duration_minutes = 1` (wartość brzegowa)
    filters = [{"column": "duration_minutes", "operator": "=", "value": 1}]
    result = services.get_records(filters=filters)
    assert len(result) == 1, "Filtracja dla wartości minimalnej nie działa poprawnie."

    # Filtr: `duration_minutes = 300` (wartość brzegowa)
    filters = [{"column": "duration_minutes", "operator": "=", "value": 300}]
    result = services.get_records(filters=filters)
    assert len(result) == 1, "Filtracja dla wartości maksymalnej nie działa poprawnie."

    # Filtr: `service_type IN ('Usługa A', 'Usługa C')`
    filters = [{"column": "service_type", "operator": "IN", "value": ["Usługa A", "Usługa C"]}]
    result = services.get_records(filters=filters)
    assert len(result) == 2, "Filtracja z `IN` zwróciła niepoprawne wyniki."




def test_get_records_with_sorting(setup_database):
    """
    Test pobierania rekordów z różnymi warunkami sortowania.
    """
    db_controller = setup_database
    services = Services(db_controller)

    # Dodanie danych
    services.create_new_record("Usługa B", 120, 200)
    services.create_new_record("Usługa A", 120, 100)
    services.create_new_record("Usługa C", 180, 300)

    # Sortowanie rosnące po jednej kolumnie
    sort_by = [("service_price", "ASC")]
    result = services.get_records(sort_by=sort_by)
    assert result[0]["service_price"] == 100, "Sortowanie rosnące po `service_price` nie działa poprawnie."
    assert result[2]["service_price"] == 300, "Sortowanie rosnące po `service_price` nie działa poprawnie."

    # Sortowanie malejące po jednej kolumnie
    sort_by = [("service_price", "DESC")]
    result = services.get_records(sort_by=sort_by)
    assert result[0]["service_price"] == 300, "Sortowanie malejące po `service_price` nie działa poprawnie."

    # Wielokrotne sortowanie
    sort_by = [("service_price", "ASC"), ("service_type", "ASC")]
    result = services.get_records(sort_by=sort_by)
    assert result[0]["service_type"] == "Usługa A", "Wielokrotne sortowanie nie działa poprawnie."

    # Sortowanie malejące po kilku kolumnach
    sort_by = [("duration_minutes", "DESC"), ("service_price", "DESC")]
    result = services.get_records(sort_by=sort_by)
    assert result[0]["duration_minutes"] == 180, "Sortowanie malejące po wielu kolumnach nie działa poprawnie."

    # Sortowanie przy takich samych wartościach
    services.create_new_record("Usługa D", 120, 200)
    sort_by = [("duration_minutes", "ASC"), ("service_type", "ASC")]
    result = services.get_records(sort_by=sort_by)
    assert result[0]["service_type"] == "Usługa A", "Sortowanie przy takich samych wartościach nie działa poprawnie."




def test_create_new_record_empty_values(setup_database):
    """
    Test próby dodania rekordu z pustymi wartościami.
    """
    db_controller = setup_database
    services = Services(db_controller)

    with pytest.raises(ValueError, match="service_type nie może być pusty."):
        services.create_new_record("", 60, 100)

    with pytest.raises(ValueError, match="Czas trwania musi być liczbą całkowitą."):
        services.create_new_record("Usługa Pusta", None, 100)


def test_database_connection_error():
    """
    Test obsługi błędów połączenia z bazą danych.
    """
    db_controller = DatabaseController()

    # Bez połączenia
    services = Services(db_controller)
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        services.create_new_record("Usługa A", 60, 100)


