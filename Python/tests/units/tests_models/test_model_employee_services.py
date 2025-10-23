# test_model_employee_services.py

"""
Testuje model EmployeeServices, weryfikując operacje CRUD
oraz walidacje przy użyciu testowej bazy SQLite w pamięci.
"""

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from models.employee_services import EmployeeServices
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguruje testową bazę danych.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabel
    employees_controller = EmployeesController(db_controller)
    employees_controller.create_table()

    services_controller = ServicesController(db_controller)
    services_controller.create_table()

    employee_services_model = EmployeeServices(db_controller)
    employee_services_model.create_table()

    yield db_controller

   # Czyszczenie danych po każdym teście
    if db_controller.connection:
        if db_controller.table_exists("employee_services"):
            db_controller.connection.execute("DELETE FROM employee_services")
        if db_controller.table_exists("employees"):
            db_controller.connection.execute("DELETE FROM employees")
        if db_controller.table_exists("services"):
            db_controller.connection.execute("DELETE FROM services")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_add_employee_service_by_ids_valid_data(setup_database):
    """
    Testuje poprawne dodanie rekordu korzystając z ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 100)
    """)

    # Dodanie rekordu
    employee_services_model.add_employee_service_by_ids(1, 1)

    # Walidacja
    records = employee_services_model.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1


def test_add_employee_service_by_names_valid_data(setup_database):
    """
    Testuje poprawne dodanie rekordu korzystając z nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 100)
    """)

    # Dodanie rekordu
    employee_services_model.add_employee_service_by_names("Jan", "Kowalski", "Terapia")

    # Walidacja
    records = employee_services_model.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1


def test_add_employee_service_by_ids_missing_data(setup_database):
    """
    Testuje próbę dodania rekordu z brakującymi danymi korzystając z ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie usługi do bazy danych
    db_controller.connection.execute("""
        INSERT INTO services (service_id, service_type, duration_minutes, service_price)
        VALUES (1, 'Terapia', 60, 100)
    """)

    # Brak pracownika
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        employee_services_model.add_employee_service_by_ids(99, 1)

    # Dodanie pracownika do bazy danych
    db_controller.connection.execute("""
        INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
        VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)

    # Brak usługi
    with pytest.raises(ValueError, match="Usługa o ID 99 nie istnieje."):
        employee_services_model.add_employee_service_by_ids(1, 99)





def test_add_employee_service_by_names_missing_data(setup_database):
    """
    Testuje próbę dodania rekordu z brakującymi danymi korzystając z nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie usługi
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150)
    """)

    # Próba dodania bez pracownika
    with pytest.raises(ValueError, match="Pracownik Jan Kowalski nie istnieje."):
        employee_services_model.add_employee_service_by_names("Jan", "Kowalski", "Terapia")




def test_add_employee_service_duplicate_data(setup_database):
    """
    Testuje próbę dodania duplikatu rekordu korzystając z ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 100)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i service_id=1 już istnieje."):
        employee_services_model.add_employee_service_by_ids(1, 1)


def test_add_employee_service_empty_database(setup_database):
    """
    Testuje próbę dodania rekordu do pustej bazy.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Próba dodania bez pracownika i usługi
    with pytest.raises(ValueError, match="Pracownik o ID 1 nie istnieje."):
        employee_services_model.add_employee_service_by_ids(1, 1)




# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_update_record_by_ids_valid_data(setup_database):
    """
    Testuje poprawną aktualizację rekordu na podstawie ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Aktualizacja rekordu
    employee_services_model.update_record_by_ids(1, 2, 2)

    # Walidacja
    records = employee_services_model.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 2
    assert records[0]["service_id"] == 2


def test_update_record_by_ids_invalid_data(setup_database):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Próba aktualizacji z błędnym `employee_id`
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        employee_services_model.update_record_by_ids(1, 99, 1)

    # Próba aktualizacji z błędnym `service_id`
    with pytest.raises(ValueError, match="Usługa o ID 99 nie istnieje."):
        employee_services_model.update_record_by_ids(1, 1, 99)


def test_update_record_by_names_valid_data(setup_database):
    """
    Testuje poprawną aktualizację rekordu na podstawie nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Aktualizacja rekordu na podstawie nazw
    employee_services_model.update_record_by_names(
        "Jan", "Kowalski", "Terapia", new_first_name="Maria", new_last_name="Nowak", new_service_type="Konsultacja"
    )

    # Walidacja
    records = employee_services_model.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 2
    assert records[0]["service_id"] == 2


def test_update_nonexistent_record(setup_database):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Próba aktualizacji nieistniejącego rekordu
    with pytest.raises(ValueError, match="Rekord o ID 99 nie istnieje."):
        employee_services_model.update_record_by_ids(99, 1, 1)


def test_update_record_with_missing_data(setup_database):
    """
    Testuje próbę aktualizacji rekordu z brakującymi danymi.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

        # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)


    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Brak danych do aktualizacji
    with pytest.raises(ValueError, match="Pracownik o ID None nie istnieje."):
        employee_services_model.update_record_by_ids(1, None, None)


def test_update_record_with_unique_constraint_violation(setup_database):
    """
    Testuje, czy metoda zgłasza wyjątek, gdy dane naruszają ograniczenia unikalności.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1), (2, 2, 2)
    """)

    # Próba aktualizacji, która narusza unikalność
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i service_id=1 już istnieje."):
        employee_services_model.update_record_by_ids(2, 1, 1)



# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_delete_record_by_id_valid_data(setup_database):
    """
    Testuje poprawne usunięcie rekordu korzystając z ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

            # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Usunięcie rekordu
    employee_services_model.delete_record_by_id(1)

    # Walidacja
    records = employee_services_model.get_all_records()
    assert len(records) == 0


def test_delete_record_by_names_valid_data(setup_database):
    """
    Testuje poprawne usunięcie rekordu korzystając z nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Usunięcie rekordu
    employee_services_model.delete_records_by_names("Jan", "Kowalski", "Terapia")

    # Walidacja
    records = employee_services_model.get_all_records()
    assert len(records) == 0


def test_delete_nonexistent_record_by_id(setup_database):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(ValueError, match="Rekord o ID 99 nie istnieje."):
        employee_services_model.delete_record_by_id(99)


def test_delete_nonexistent_record_by_names(setup_database):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(ValueError, match="Pracownik Jan Kowalski nie istnieje."):
        employee_services_model.delete_records_by_names("Jan", "Kowalski", "Terapia")



# +-+-+-+- Testy metod pobierania i filtracji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_get_record_by_id_valid_data(setup_database):
    """
    Testuje poprawne pobieranie istniejącego rekordu korzystając z ID, używając istniejącej metody get_all_records.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)


    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 100)
    """)

    # Dodanie danych testowych
    employee_services_model.add_employee_service_by_ids(1, 1)

    # Pobranie wszystkich rekordów
    records = employee_services_model.get_all_records()

    # Filtrowanie po ID
    record = next((r for r in records if r["employee_service_id"] == 1), None)

    # Walidacja
    assert record is not None
    assert record["employee_id"] == 1
    assert record["service_id"] == 1



def test_get_record_by_names_valid_data(setup_database):
    """
    Testuje poprawne pobieranie istniejącego rekordu korzystając z nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150)
    """)
    db_controller.connection.execute("""
    INSERT INTO employee_services (employee_service_id, employee_id, service_id)
    VALUES (1, 1, 1)
    """)

    # Pobranie rekordu
    record = employee_services_model.get_record_with_names("Jan", "Kowalski", "Terapia")

    # Walidacja
    assert len(record) == 1
    assert record[0]["employee_name"] == "Jan Kowalski"
    assert record[0]["service_type"] == "Terapia"


def test_get_all_records_valid_data(setup_database):
    """
    Testuje poprawne pobranie wszystkich rekordów z bazy.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
        INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
        VALUES
            (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
            (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)

    db_controller.connection.execute("""
        INSERT INTO services (service_id, service_type, duration_minutes, service_price)
        VALUES
            (1, 'Terapia', 60, 150),
            (2, 'Konsultacja', 30, 50)
    """)

    db_controller.connection.execute("""
        INSERT INTO employee_services (employee_service_id, employee_id, service_id)
        VALUES
            (1, 1, 1),
            (2, 2, 2)
    """)

    # Pobranie wszystkich rekordów
    records = employee_services_model.get_all_records()

    # Walidacja
    assert len(records) == 2
    assert records[0]["employee_id"] == 1
    assert records[0]["service_id"] == 1
    assert records[1]["employee_id"] == 2
    assert records[1]["service_id"] == 2



def test_get_all_records_empty_database(setup_database):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    # Pobranie wszystkich rekordów
    records = employee_services_model.get_all_records()

    # Walidacja
    assert len(records) == 0


def test_get_records_with_filtering_by_id(setup_database):
    """
    Testuje pobranie rekordu z filtrowaniem korzystając z ID.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

            # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)


    # Dodanie danych testowych
    employee_services_model.add_employee_service_by_ids(1, 1)

    # Pobranie rekordów i filtrowanie
    records = employee_services_model.get_all_records()
    filtered_records = [r for r in records if r["employee_id"] == 1]

    # Walidacja
    assert len(filtered_records) == 1
    assert filtered_records[0]["employee_id"] == 1



def test_get_records_with_filtering_by_names(setup_database):
    """
    Testuje pobranie rekordu z filtrowaniem korzystając z nazw.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 100)
    """)

    # Dodanie danych testowych
    employee_services_model.add_employee_service_by_names("Jan", "Kowalski", "Terapia")

    # Pobranie rekordów za pomocą nazw
    records = employee_services_model.get_record_with_names("Jan", "Kowalski", "Terapia")

    # Walidacja
    assert len(records) == 1
    assert records[0]["employee_name"] == "Jan Kowalski"
    assert records[0]["service_type"] == "Terapia"



def test_get_records_with_sorting(setup_database):
    """
    Testuje poprawne pobranie rekordów z sortowaniem.
    """
    db_controller = setup_database
    employee_services_model = EmployeeServices(db_controller)

            # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1),
           (2, 'Maria', 'Nowak', 'maria.nowak@example.com', '987654321', 'Psycholog kliniczny', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150), (2, 'Konsultacja', 30, 50)
    """)

    # Dodanie danych testowych
    employee_services_model.add_employee_service_by_ids(1, 1)
    employee_services_model.add_employee_service_by_ids(2, 2)

    # Pobranie wszystkich rekordów
    records = employee_services_model.get_all_records()

    # Sortowanie w teście
    sorted_records = sorted(records, key=lambda x: x["employee_id"], reverse=False)

    # Walidacja
    assert len(sorted_records) == 2
    assert sorted_records[0]["employee_id"] == 1
    assert sorted_records[1]["employee_id"] == 2



def test_get_records_with_missing_dependencies(setup_database):
    """
    Testuje próbę pobrania rekordów z brakującymi zależnościami.
    """
    db_controller = setup_database

    # Dodanie danych pracowników i usług
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO services (service_id, service_type, duration_minutes, service_price)
    VALUES (1, 'Terapia', 60, 150)
    """)

    # Próba dodania rekordu z brakującymi zależnościami
    with pytest.raises(sqlite3.IntegrityError):
        db_controller.connection.execute("""
        INSERT INTO employee_services (employee_service_id, employee_id, service_id)
        VALUES (1, 99, 99)
        """)
