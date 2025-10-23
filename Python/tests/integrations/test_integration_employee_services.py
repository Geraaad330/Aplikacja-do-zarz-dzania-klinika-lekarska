# test_integration_employee_services.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.employee_services_controller import EmployeeServicesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"


@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu EmployeeServices.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "employees": EmployeesController(db_controller),
        "services": ServicesController(db_controller),
        "employee_services": EmployeeServicesController(db_controller)
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:  # Upewnij się, że połączenie istnieje
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM employee_services")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM services")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_employee_services.py

# Poprawne dodanie rekordu korzystając z ID
def test_add_record_by_ids_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie rekordu korzystając z ID.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    # Dodanie rekordu
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Weryfikacja
    records = employee_services_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1

# Poprawne dodanie rekordu korzystając z nazw
def test_add_record_by_names_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie rekordu korzystając z nazw.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    # Dodanie rekordu
    employee_services_controller.add_employee_service_by_names("Jan", "Kowalski", "Terapia")

    # Weryfikacja
    records = employee_services_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1

# Próba dodania rekordu z nieprawidłowymi danymi korzystając z ID
def test_add_record_by_ids_invalid_data(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi korzystając z ID.
    """
    employee_services_controller = setup_controllers["employee_services"]
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]

    # Dodanie brakującego pracownika i usługi
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psycholog kliniczny", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)


    # Próba dodania rekordu z nieistniejącym pracownikiem
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        employee_services_controller.add_employee_service_by_ids(employee_id=99, service_id=1)

    # Próba dodania rekordu z nieistniejącą usługą
    with pytest.raises(ValueError, match="Błąd walidacji: Usługa o ID 99 nie istnieje."):
        employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=99)

# Próba dodania rekordu z nieprawidłowymi danymi korzystając z nazw
def test_add_record_by_names_invalid_data(setup_controllers):
    employee_services_controller = setup_controllers["employee_services"]

    with pytest.raises(ValueError, match="Pracownik Nieistniejący Pracownik nie istnieje."):
        employee_services_controller.add_employee_service_by_names(
            first_name="Nieistniejący", last_name="Pracownik", service_type="Nieznana usługa"
        )


# Próba dodania rekordu z duplikatem korzystając z ID
def test_add_record_by_ids_duplicate(setup_controllers):
    """
    Testuje próbę dodania rekordu z duplikatem korzystając z ID.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    # Dodanie rekordu
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Próba dodania tego samego rekordu ponownie
    with pytest.raises(ValueError, match="Błąd walidacji: Kombinacja employee_id=1 i service_id=1 już istnieje."):
        employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

# Próba dodania rekordu z duplikatem korzystając z nazw
def test_add_record_by_names_duplicate(setup_controllers):
    """
    Testuje próbę dodania rekordu z duplikatem korzystając z nazw.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    # Dodanie rekordu
    employee_services_controller.add_employee_service_by_names("Jan", "Kowalski", "Terapia")

    # Próba dodania tego samego rekordu ponownie
    with pytest.raises(ValueError, match="Błąd walidacji: Rekord dla Jan Kowalski i usługi 'Terapia' już istnieje."):
        employee_services_controller.add_employee_service_by_names("Jan", "Kowalski", "Terapia")

# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_employee_services.py

# Testuje pobieranie rekordów z niepoprawnymi filtrami
def test_get_records_invalid_filters(setup_controllers):
    """
    Testuje próbę pobrania rekordów z niepoprawnymi filtrami.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba pobrania z nieprawidłowymi filtrami
    with pytest.raises(ValueError, match="Nieprawidłowe kolumny w filtrach: invalid_column"):
        employee_services_controller.get_all_records(filters={"invalid_column": "value"})


# Testuje pobieranie rekordów z filtrami
def test_get_records_with_filters(setup_controllers):
    """
    Testuje pobieranie rekordów z poprawnymi filtrami.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Pobranie z filtrem
    records = employee_services_controller.get_all_records(filters={"employee_id": 1})
    assert len(records) == 1
    assert records[0]["employee_id"] == 1


# Testuje pobieranie rekordów przy użyciu poprawnych danych
def test_get_records_valid_data(setup_controllers):
    """
    Testuje pobieranie rekordów przy użyciu poprawnych danych.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Pobranie rekordów
    records = employee_services_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1

# Pobranie rekordów z sortowaniem
def test_get_records_with_sorting(setup_controllers):
    """
    Testuje pobranie rekordów z sortowaniem.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    employees_controller.add_employee(
        first_name="Maria", last_name="Nowak", email="maria.nowak@example.com",
        phone="987654321", profession="Psycholog kliniczny", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)
    services_controller.add_service("Konsultacja", 30, 100)

    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)
    employee_services_controller.add_employee_service_by_ids(employee_id=2, service_id=2)

    # Pobranie z sortowaniem
    records = employee_services_controller.get_all_records(sort_by="employee_id", ascending=True)
    assert len(records) == 2
    assert records[0]["employee_id"] == 1
    assert records[1]["employee_id"] == 2

# Poprawne pobieranie istniejącego rekordu korzystając z ID
def test_get_existing_record_by_id(setup_controllers):
    """
    Testuje poprawne pobieranie istniejącego rekordu korzystając z ID.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Pobranie rekordu
    record = employee_services_controller.get_record_by_id(employee_service_id=1)
    assert record["employee_id"] == 1
    assert record["service_id"] == 1

# Próba pobrania nieistniejącego rekordu
def test_get_nonexistent_record(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba pobrania nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanym ID."):
        employee_services_controller.get_record_by_id(employee_service_id=99)

# Pobranie rekordów z pustej bazy
def test_get_records_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy danych.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Pobranie rekordów z pustej bazy
    records = employee_services_controller.get_all_records()
    assert len(records) == 0, "Nie powinno być żadnych rekordów w pustej bazie danych."



# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# Aktualizacja rekordu z poprawnymi danymi korzystając z ID
def test_update_record_by_ids_valid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi korzystając z ID.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)
    services_controller.add_service("Konsultacja", 30, 100)

    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Aktualizacja rekordu
    employee_services_controller.update_record_by_ids(employee_service_id=1, employee_id=1, service_id=2)

    # Weryfikacja
    records = employee_services_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["service_id"] == 2

# Aktualizacja rekordu z poprawnymi danymi korzystając z nazw
# Przykład poprawionego testu
def test_update_record_by_names_valid_data(setup_controllers):
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie brakujących danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    employees_controller.add_employee(
        first_name="Jorg", last_name="Lazinka", email="jorg.lazinka@example.com",
        phone="123456788", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Konsultacja", 30, 100)

    # Dodanie nowych danych, które będą celem aktualizacji
    employees_controller.add_employee(
        first_name="Jaln", last_name="Kowllski", email="jaln.kowllski@example.com",
        phone="123456787", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("NowaUsługa", 45, 120)

    # Dodanie rekordów w tabeli employee_services
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)
    employee_services_controller.add_employee_service_by_ids(employee_id=2, service_id=2)

    # Aktualizacja rekordu do nowych danych
    employee_services_controller.update_record_by_names(
        employee_service_id=1,  # Rekord z employee_id=1, service_id=1
        first_name="Jaln", last_name="Kowllski", service_type="NowaUsługa"  # Kombinacja unikalna i istniejąca
    )




# Próba aktualizacji rekordu z niepoprawnymi danymi korzystając z ID
def test_update_record_by_ids_invalid_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu z niepoprawnymi danymi korzystając z ID.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba aktualizacji rekordu bez istniejących danych
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o ID 99."):
        employee_services_controller.update_record_by_ids(employee_service_id=99, employee_id=1, service_id=1)


# Próba aktualizacji rekordu z brakującymi danymi
def test_update_record_by_ids_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu z brakującymi danymi.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba aktualizacji rekordu bez danych
    with pytest.raises(ValueError, match="Rekord musi zawierać poprawne dane dla employee_id i service_id."):
        employee_services_controller.update_record_by_ids(employee_service_id=1, employee_id=None, service_id=None)


# Próba aktualizacji rekordu z nieistniejącymi danymi korzystając z nazw
def test_update_record_by_names_invalid_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu z niepoprawnymi danymi korzystając z nazw.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba aktualizacji rekordu bez istniejących danych
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanym ID."):
        employee_services_controller.update_record_by_names(
            employee_service_id=99, first_name="Nieistniejący", last_name="Pracownik", service_type="Nieznana usługa"
        )



 # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# Poprawne usunięcie rekordu korzystając z ID
def test_delete_record_by_id_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z ID.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Usunięcie rekordu
    employee_services_controller.delete_record_by_id(employee_service_id=1)

    # Weryfikacja
    records = employee_services_controller.get_all_records()
    assert len(records) == 0, "Rekord nie został poprawnie usunięty."

# Poprawne usunięcie rekordu korzystając z nazw
def test_delete_record_by_names_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z nazw.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    employee_services_controller.add_employee_service_by_names("Jan", "Kowalski", "Terapia")

    # Usunięcie rekordu
    employee_services_controller.delete_records_by_names("Jan", "Kowalski", "Terapia")

    # Weryfikacja
    records = employee_services_controller.get_all_records()
    assert len(records) == 0, "Rekord nie został poprawnie usunięty."

# Próba usunięcia nieistniejącego rekordu korzystając z ID
def test_delete_record_by_id_nonexistent(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z ID.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanym ID."):
        employee_services_controller.delete_record_by_id(employee_service_id=99)

# Próba usunięcia nieistniejącego rekordu korzystając z nazw
def test_delete_record_by_names_nonexistent(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z nazw.
    """
    employee_services_controller = setup_controllers["employee_services"]

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu dla podanych danych."):
        employee_services_controller.delete_records_by_names("Nieistniejący", "Pracownik", "Nieznana usługa")



 # +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# Testuje obsługę błędów bazy danych przy rozłączeniu połączenia
def test_database_disconnection_error_handling(setup_controllers):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia.
    """
    db_controller = setup_controllers["employee_services"].db_controller
    employee_services_controller = setup_controllers["employee_services"]

    # Rozłączenie bazy danych
    db_controller.close_connection()

    # Próba wykonania operacji po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        employee_services_controller.get_all_records()


# Test pełnego przepływu CRUD

def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """
    employees_controller = setup_controllers["employees"]
    services_controller = setup_controllers["services"]
    employee_services_controller = setup_controllers["employee_services"]

    # Dodanie pracownika i usługi
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    services_controller.add_service("Terapia", 60, 150)

    # Dodanie usługi dla pracownika
    employee_services_controller.add_employee_service_by_ids(employee_id=1, service_id=1)

    # Pobranie i weryfikacja dodania
    records = employee_services_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1

    # Aktualizacja usługi
    services_controller.add_service("Konsultacja", 30, 100)
    employee_services_controller.update_record_by_ids(employee_service_id=1, employee_id=1, service_id=2)

    # Weryfikacja aktualizacji
    records = employee_services_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["service_id"] == 2

    # Usunięcie usługi
    employee_services_controller.delete_record_by_id(employee_service_id=1)

    # Weryfikacja usunięcia
    records = employee_services_controller.get_all_records()
    assert len(records) == 0, "Dane nie zostały usunięte z tabeli."
