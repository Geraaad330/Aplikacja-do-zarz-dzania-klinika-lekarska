# test_integration_services.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.services_controller import ServicesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_services_controller")
def setup_services_controller_fixture():
    """
    Fixture konfiguruje bazę danych oraz instancję kontrolera `ServicesController`.
    Czyszczenie danych odbywa się przed każdym testem.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    services_controller = ServicesController(db_controller)
    services_controller.create_table()

    # Czyszczenie danych przed każdym testem
    db_controller.connection.execute("DELETE FROM services")
    db_controller.connection.commit()

    yield services_controller

    # Czyszczenie tabeli po wszystkich testach
    if db_controller.connection is None:
        db_controller.connect_to_database()
    if db_controller.table_exists("services"):
        db_controller.connection.execute("DROP TABLE services")
    db_controller.close_connection()

def test_add_service_with_valid_data(setup_services_controller):
    """
    Testuje dodawanie nowej usługi z poprawnymi danymi.
    """
    controller = setup_services_controller
    controller.add_service("Usługa A", 120, 200)

    services = controller.get_all_services()
    assert len(services) == 1
    assert services[0]["service_type"] == "Usługa A"
    assert services[0]["duration_minutes"] == 120
    assert services[0]["service_price"] == 200

def test_add_service_with_invalid_data(setup_services_controller):
    """
    Testuje dodawanie nowej usługi z niepoprawnymi danymi.
    """
    controller = setup_services_controller

    with pytest.raises(ValueError, match="service_type nie może być pusty."):
        controller.add_service("", 120, 200)

    with pytest.raises(ValueError, match="Czas trwania musi być pomiędzy 1 a 300 minut."):
        controller.add_service("Usługa B", 0, 200)

    with pytest.raises(ValueError, match="Cena usługi musi być pomiędzy 1 a 500."):
        controller.add_service("Usługa C", 120, 600)

def test_get_services_with_sorting(setup_services_controller):
    """
    Testuje pobieranie usług z sortowaniem.
    """
    controller = setup_services_controller

    # Dodanie danych
    controller.add_service("Usługa A", 120, 200)
    controller.add_service("Usługa B", 180, 300)
    controller.add_service("Usługa C", 60, 100)

    # Sortowanie według ceny malejąco
    results = controller.get_services_with_filters(sort_by=[("service_price", "DESC")])
    assert len(results) == 3
    assert results[0]["service_price"] == 300
    assert results[2]["service_price"] == 100

    # Sortowanie według czasu trwania rosnąco
    results = controller.get_services_with_filters(sort_by=[("duration_minutes", "ASC")])
    assert results[0]["duration_minutes"] == 60
    assert results[2]["duration_minutes"] == 180

def test_update_service_with_valid_data(setup_services_controller):
    """
    Testuje aktualizację usługi z poprawnymi danymi.
    """
    controller = setup_services_controller

    # Dodanie usługi
    controller.add_service("Usługa A", 120, 200)
    service = controller.get_all_services()[0]

    # Aktualizacja
    updates = {"service_price": 250, "duration_minutes": 150}
    controller.update_service(service["service_id"], updates)

    updated_service = controller.get_all_services()[0]
    assert updated_service["service_price"] == 250
    assert updated_service["duration_minutes"] == 150

def test_update_service_with_invalid_data(setup_services_controller):
    """
    Testuje aktualizację usługi z niepoprawnymi danymi.
    """
    controller = setup_services_controller

    # Dodanie usługi
    controller.add_service("Usługa A", 120, 200)
    service = controller.get_all_services()[0]

    # Aktualizacja z niepoprawnymi danymi
    with pytest.raises(ValueError, match="Cena usługi musi być pomiędzy 1 a 500."):
        controller.update_service(service["service_id"], {"service_price": 600})

    with pytest.raises(ValueError, match="Czas trwania musi być pomiędzy 1 a 300 minut."):
        controller.update_service(service["service_id"], {"duration_minutes": 0})

def test_delete_service(setup_services_controller):
    """
    Testuje usuwanie usługi.
    """
    controller = setup_services_controller

    # Dodanie usługi
    controller.add_service("Usługa A", 60, 100)
    service = controller.get_all_services()[0]

    # Usuwanie
    controller.delete_service(service["service_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_delete_service."

def test_get_services_with_filters(setup_services_controller):
    """
    Testuje pobieranie usług z filtrowaniem.
    """
    controller = setup_services_controller

    # Dodanie danych
    controller.add_service("Usługa A", 60, 100)
    controller.add_service("Usługa B", 180, 300)

    # Filtracja
    filters = [{"column": "service_price", "operator": ">", "value": 100}]
    results = controller.get_services_with_filters(filters=filters)

    assert len(results) == 1
    assert results[0]["service_type"] == "Usługa B"

def test_full_crud_flow(setup_services_controller):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """
    controller = setup_services_controller

    # Dodanie usługi
    controller.add_service("Usługa A", 120, 200)
    service = controller.get_all_services()[0]
    assert service["service_type"] == "Usługa A"

    # Aktualizacja usługi
    updates = {"service_price": 250, "duration_minutes": 150}
    controller.update_service(service["service_id"], updates)
    updated_service = controller.get_all_services()[0]
    assert updated_service["service_price"] == 250
    assert updated_service["duration_minutes"] == 150

    # Usuwanie usługi
    controller.delete_service(updated_service["service_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_full_crud_flow."

def test_database_disconnection_handling_services(setup_services_controller):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia w tabeli `services`.
    """
    controller = setup_services_controller

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba dodania usługi po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.add_service("Usługa A", 120, 200)

    # Próba pobrania usług po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.get_all_services()

    # Ponowne połączenie i weryfikacja
    controller.db_controller.connect_to_database()
    controller.create_table()
    controller.add_service("Usługa B", 180, 300)

    services = controller.get_all_services()
    assert len(services) == 1
    assert services[0]["service_type"] == "Usługa B"

    # Czyszczenie danych
    controller.delete_service(services[0]["service_id"])


def test_reconnect_to_database_services(setup_services_controller):
    """
    Testuje ponowne połączenie z bazą danych oraz dodanie rekordu po ponownym połączeniu w tabeli `services`.
    """
    controller = setup_services_controller

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba ponownego połączenia
    controller.db_controller.connect_to_database()
    controller.create_table()

    # Dodanie nowego rekordu po ponownym połączeniu
    controller.add_service("Usługa C", 60, 100)
    services = controller.get_all_services()
    assert len(services) == 1
    assert services[0]["service_type"] == "Usługa C"

    # Czyszczenie danych
    controller.delete_service(services[0]["service_id"])
