# test_integration_assigned_patients.py

import os
import re
import sqlite3
import pytest
from controllers.database_controller import DatabaseController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.patients_controller import PatientController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.employees_controller import EmployeesController
from controllers.roles_controller import RolesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla AssignedPatients.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "assigned_patients": AssignedPatientsController(db_controller),
        "patients": PatientController(db_controller),
        "users_accounts": UsersAccountsController(db_controller),
        "employees": EmployeesController(db_controller),
        "roles": RolesController(db_controller)
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM assigned_patients")
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM users_accounts")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM roles")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_add_record_with_valid_data_by_ids(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Anna", "Kowalska", "12345678901", "555123123", "anna.kowalska@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Anna", "Kowalska", "anna.kowalska@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("Admin")
    patient_id = patients.get_all_patients()[0]["patient_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "anna_kowalska", "hashed_password", 1, "2025-01-01 10:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie rekordu
    assigned_patients.add_record_by_ids(patient_id, user_id)

    # Weryfikacja
    records = assigned_patients.get_records_with_filters()
    assert len(records) == 1
    assert records[0]["fk_patient_id"] == patient_id
    assert records[0]["fk_user_id"] == user_id


def test_add_record_with_valid_data_by_names(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi korzystając z first_name, last_name i username.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Jan", "Kowalski", "98765432109", "555222333", "jan.kowalski@example.com", "Adres 2", "1980-02-02")
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555222333", "Psychoterapeuta", 1)
    roles.add_role("User")
    users_accounts.add_user_by_names("Jan", "Kowalski", "User", "jan_kowalski", "hashed_password", 1, "2025-01-02 11:00")

    # Dodanie rekordu
    assigned_patients.add_record_by_names("Jan", "Kowalski", "jan_kowalski")

    # Weryfikacja
    records = assigned_patients.get_records_with_filters()
    assert len(records) == 1
    assert records[0]["fk_patient_id"] == patients.get_all_patients()[0]["patient_id"]
    assert records[0]["fk_user_id"] == users_accounts.get_users_with_names()[0]["user_id"]


def test_add_record_with_missing_data_by_ids(setup_controllers):
    """
    Próba dodania rekordu z brakującymi danymi dla metody dodawania korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(ValueError, match="Błąd integralności: fk_patient_id i fk_user_id nie mogą być puste."):
        assigned_patients.add_record_by_ids(None, None)



def test_add_record_with_missing_data_by_names(setup_controllers):
    """
    Próba dodania rekordu z brakującymi danymi dla metody dodawania korzystając z first_name, last_name i username.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(ValueError, match=re.escape("Nazwa musi być ciągiem znaków.")):
        assigned_patients.add_record_by_names(None, None, None)




def test_add_record_with_invalid_data_by_ids(setup_controllers):
    """
    Próba dodania rekordu z nieprawidłowymi danymi dla metody korzystającej z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(RuntimeError, match="Błąd integralności danych:"):
        assigned_patients.add_record_by_ids(999, 999)


def test_add_record_with_invalid_data_by_names(setup_controllers):
    """
    Próba dodania rekordu z nieprawidłowymi danymi dla metody korzystającej z first_name, last_name i username.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(ValueError, match="Pacjent 'Invalid Name' nie istnieje."):
        assigned_patients.add_record_by_names("Invalid", "Name", "invalid_user")





def test_add_record_with_duplicate_by_ids(setup_controllers):
    """
    Próba dodania rekordu z duplikatem korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Jan", "Kowalski", "12345678901", "555123123", "jan.kowalski@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("Admin")
    patient_id = patients.get_all_patients()[0]["patient_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "jan_kowalski", "hashed_password", 1, "2025-01-01 10:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie rekordu
    assigned_patients.add_record_by_ids(patient_id, user_id)

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Kombinacja pacjent_id=1 i user_id=1 już istnieje."):
        assigned_patients.add_record_by_ids(patient_id, user_id)



def test_add_record_with_duplicate_by_names(setup_controllers):
    """
    Próba dodania rekordu z duplikatem korzystając z first_name, last_name i username.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Anna", "Nowak", "98765432109", "555222333", "anna.nowak@example.com", "Adres 2", "1980-02-02")
    employees.add_employee("Anna", "Nowak", "anna.nowak@example.com", "555222333", "Psychoterapeuta", 1)
    roles.add_role("User")
    users_accounts.add_user_by_names("Anna", "Nowak", "User", "anna_nowak", "hashed_password", 1, "2025-01-02 11:00")

    # Dodanie rekordu
    assigned_patients.add_record_by_names("Anna", "Nowak", "anna_nowak")

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Kombinacja pacjent_id=1 i user_id=1 już istnieje."):
        assigned_patients.add_record_by_names("Anna", "Nowak", "anna_nowak")



def test_add_record_to_empty_database(setup_controllers):
    """
    Próba dodania rekordu do pustej bazy danych.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(RuntimeError, match="Błąd integralności danych: FOREIGN KEY constraint failed"):
        assigned_patients.add_record_by_ids(1, 1)


# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_get_record_by_ids(setup_controllers):
    """
    Testuje poprawne pobranie istniejącego rekordu korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Anna", "Kowalska", "12345678901", "555123123", "anna.kowalska@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Anna", "Kowalska", "anna.kowalska@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("Admin")
    patient_id = patients.get_all_patients()[0]["patient_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "anna_kowalska", "hashed_password", 1, "2025-01-01 10:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie rekordu
    assigned_patients.add_record_by_ids(patient_id, user_id)

    # Pobranie rekordu
    record = assigned_patients.get_record_by_patient_and_user_ids(patient_id, user_id)
    assert record is not None
    assert record["fk_patient_id"] == patient_id
    assert record["fk_user_id"] == user_id


def test_get_record_by_names(setup_controllers):
    """
    Testuje poprawne pobranie istniejącego rekordu korzystając z first_name, last_name i username.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Jan", "Kowalski", "98765432109", "555222333", "jan.kowalski@example.com", "Adres 2", "1980-02-02")
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555222333", "Psychoterapeuta", 1)
    roles.add_role("User")
    users_accounts.add_user_by_names("Jan", "Kowalski", "User", "jan_kowalski", "hashed_password", 1, "2025-01-02 11:00")

    # Dodanie rekordu
    assigned_patients.add_record_by_names("Jan", "Kowalski", "jan_kowalski")

    # Pobranie rekordu
    records = assigned_patients.get_records_with_filters(filters=[{"column": "u.username", "operator": "=", "value": "jan_kowalski"}])

    # Assercja wyników
    assert len(records) == 1
    assert records[0]["fk_user_id"] == users_accounts.get_users_with_names()[0]["user_id"]



def test_get_nonexistent_record(setup_controllers):
    """
    Próba pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    record = assigned_patients.get_record_by_patient_and_user_ids(999, 999)
    assert record is None


def test_get_records_from_empty_database(setup_controllers):
    """
    Pobranie rekordów z pustej bazy danych.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    records = assigned_patients.get_records_with_filters()
    assert len(records) == 0


def test_get_records_with_filters_by_ids(setup_controllers):
    """
    Pobranie rekordów z użyciem filtrów korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Anna", "Nowak", "12345678901", "555444333", "anna.nowak@example.com", "Adres 3", "1990-03-03")
    employees.add_employee("Anna", "Nowak", "anna.nowak@example.com", "555444333", "Psycholog kliniczny", 1)
    roles.add_role("Manager")
    patient_id = patients.get_all_patients()[0]["patient_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "anna_nowak", "hashed_password", 1, "2025-01-03 12:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie rekordu
    assigned_patients.add_record_by_ids(patient_id, user_id)

    # Pobranie z filtrami
    records = assigned_patients.get_records_with_filters(filters=[{"column": "fk_patient_id", "operator": "=", "value": patient_id}])
    assert len(records) == 1
    assert records[0]["fk_patient_id"] == patient_id
    assert records[0]["fk_user_id"] == user_id


def test_missing_dependencies_between_tables(setup_controllers):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie pacjenta i pracownika
    patients.add_patient("Jan", "Kowalski", "12345678901", "555111222", "jan.kowalski@example.com", "Adres 1", "1980-01-01")
    patient_id = patients.get_all_patients()[0]["patient_id"]

    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555111222", "Psychiatra", 1)
    roles.add_role("Admin")
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "jan_kowalski", "hashed_password", 1, "2025-01-01 10:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Usunięcie pacjenta
    patients.delete_patient(patient_id)

    # Próba dodania rekordu do assigned_patients z brakującym pacjentem
    with pytest.raises(RuntimeError, match="Błąd integralności danych: FOREIGN KEY constraint failed"):
        assigned_patients.add_record_by_ids(patient_id, user_id)



# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_update_record_with_valid_data_by_ids(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Anna", "Kowalska", "12345678901", "555123123", "anna.kowalska@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Anna", "Kowalska", "anna.kowalska@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("User")
    patient_id_1 = patients.get_all_patients()[0]["patient_id"]
    employee_id_1 = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id_1, role_id, "anna_kowalska", "hashed_password", 1, "2025-01-01 10:00")
    user_id_1 = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie unikalnego pracownika i pacjenta dla drugiego użytkownika
    employees.add_employee("Jan", "Nowak", "jan.nowak@example.com", "555222333", "Psychoterapeuta", 1)
    employee_id_2 = employees.get_all_employees()[1]["employee_id"]

    patients.add_patient("Jan", "Nowak", "98765432109", "555222333", "jan.nowak@example.com", "Adres 2", "1980-02-02")
    patient_id_2 = patients.get_all_patients()[1]["patient_id"]
    users_accounts.add_user_by_ids(employee_id_2, role_id, "jan_nowak", "hashed_password", 1, "2025-01-02 11:00")
    user_id_2 = users_accounts.get_users_with_names()[1]["user_id"]

    # Dodanie rekordu do assigned_patients
    assigned_patients.add_record_by_ids(patient_id_1, user_id_1)
    assigned_patients.add_record_by_ids(patient_id_2, user_id_2)

    # Aktualizacja rekordu na nowe unikalne wartości
    assignment_id = assigned_patients.get_records_with_filters()[0]["assignment_id"]
    assigned_patients.update_record_by_ids(assignment_id, fk_patient_id=patient_id_2, fk_user_id=user_id_1)

    # Weryfikacja aktualizacji
    updated_record = assigned_patients.get_records_with_filters(filters=[{"column": "assignment_id", "operator": "=", "value": assignment_id}])[0]
    assert updated_record["fk_patient_id"] == patient_id_2
    assert updated_record["fk_user_id"] == user_id_1




def test_update_record_with_valid_data_by_names(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi, korzystając z first_name, last_name i username.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Jan", "Kowalski", "12345678901", "555123123", "jan.kowalski@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("Admin")
    employee_id_1 = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id_1, role_id, "jan_kowalski", "hashed_password", 1, "2025-01-01 10:00")

    # Dodanie unikalnego pracownika i pacjenta dla drugiego użytkownika
    patients.add_patient("Anna", "Nowak", "98765432109", "555222333", "anna.nowak@example.com", "Adres 2", "1980-02-02")
    employees.add_employee("Anna", "Nowak", "anna.nowak@example.com", "555222333", "Psychoterapeuta", 1)
    employee_id_2 = employees.get_all_employees()[1]["employee_id"]
    users_accounts.add_user_by_ids(employee_id_2, role_id, "anna_nowak", "hashed_password", 1, "2025-01-02 11:00")

    # Dodanie rekordu do assigned_patients
    assigned_patients.add_record_by_names("Jan", "Kowalski", "jan_kowalski")
    assigned_patients.add_record_by_names("Anna", "Nowak", "anna_nowak")

    # Aktualizacja rekordu na unikalne wartości
    assignment_id = assigned_patients.get_records_with_filters()[0]["assignment_id"]
    assigned_patients.update_record_by_names(assignment_id, "Anna", "Nowak", "jan_kowalski")  # Unikalne wartości

    # Weryfikacja aktualizacji
    updated_record = assigned_patients.get_records_with_filters(filters=[{"column": "assignment_id", "operator": "=", "value": assignment_id}])[0]
    assert updated_record["fk_patient_id"] == patients.get_all_patients()[1]["patient_id"]
    assert updated_record["fk_user_id"] == users_accounts.get_users_with_names()[0]["user_id"]



def test_update_record_with_invalid_data_by_ids(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi, korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555123123", "Psychoterapeuta", 1)
    employee_id = employees.get_all_employees()[0]["employee_id"]

    roles.add_role("Admin")
    role_id = roles.get_all_roles()[0]["role_id"]

    patients.add_patient("Jan", "Kowalski", "12345678901", "555123123", "jan.kowalski@example.com", "Adres 1", "1990-01-01")

    # Dodanie użytkownika
    users_accounts.add_user_by_ids(employee_id, role_id, "jan_kowalski", "hashed_password", 1, "2025-01-01 10:00")



def test_update_nonexistent_record(setup_controllers):
    """
    Próba aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    # Próba aktualizacji
    with pytest.raises(KeyError, match="Nie znaleziono rekordu do aktualizacji."):
        assigned_patients.update_record_by_ids(9999, fk_patient_id=1, fk_user_id=1)  # ID 9999 nie istnieje



def test_update_record_with_missing_data(setup_controllers):
    """
    Próba aktualizacji rekordu bez danych lub z brakującymi danymi.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Jan", "Kowalski", "12345678901", "555123123", "jan.kowalski@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555123123", "Psychoterapeuta", 1)  # Dodanie pracownika
    roles.add_role("Admin")  # Dodanie roli
    role_id = roles.get_all_roles()[0]["role_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]

    # Dodanie użytkownika
    users_accounts.add_user_by_ids(employee_id, role_id, "jan_kowalski", "hashed_password", 1, "2025-01-01 10:00")

    # Dodanie rekordu do assigned_patients
    patients_data = patients.get_all_patients()[0]
    users_data = users_accounts.get_users_with_names()[0]
    assigned_patients.add_record_by_ids(patients_data["patient_id"], users_data["user_id"])

    # Próba aktualizacji rekordu bez danych
    assignment_id = assigned_patients.get_records_with_filters()[0]["assignment_id"]  # Pobranie istniejącego ID
    with pytest.raises(ValueError, match="Nie podano wartości do aktualizacji."):
        assigned_patients.update_record_by_ids(assignment_id)




# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_delete_record_by_ids(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Anna", "Kowalska", "12345678901", "555123123", "anna.kowalska@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Anna", "Kowalska", "anna.kowalska@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("Admin")
    patient_id = patients.get_all_patients()[0]["patient_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "anna_kowalska", "hashed_password", 1, "2025-01-01 10:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie i usunięcie rekordu
    assigned_patients.add_record_by_ids(patient_id, user_id)
    assigned_patients.delete_record_by_id(fk_patient_id=patient_id, fk_user_id=user_id)

    # Weryfikacja usunięcia
    records = assigned_patients.get_records_with_filters(filters=[{"column": "fk_patient_id", "operator": "=", "value": patient_id}])
    assert len(records) == 0, f"Rekord nie został usunięty dla fk_patient_id={patient_id}, fk_user_id={user_id}"



def test_delete_record_by_names(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z first_name, last_name i username zamiast fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # Dodanie danych testowych
    patients.add_patient("Jan", "Kowalski", "98765432109", "555222333", "jan.kowalski@example.com", "Adres 2", "1980-02-02")
    employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "555222333", "Psychoterapeuta", 1)
    roles.add_role("User")
    users_accounts.add_user_by_names("Jan", "Kowalski", "User", "jan_kowalski", "hashed_password", 1, "2025-01-02 11:00")

    # Dodanie i usunięcie rekordu
    assigned_patients.add_record_by_names("Jan", "Kowalski", "jan_kowalski")
    assigned_patients.delete_record_by_names(patient_first_name="Jan", patient_last_name="Kowalski", user_name="jan_kowalski")

    # Weryfikacja
    records = assigned_patients.get_records_with_filters()
    assert len(records) == 0, "Dane nie zostały usunięte z metody delete_record_by_names."


def test_delete_nonexistent_record_by_ids(setup_controllers):
    """
    Próba usunięcia nieistniejącego rekordu korzystając z fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(ValueError, match="Nie znaleziono rekordu do usunięcia."):
        assigned_patients.delete_record_by_id(fk_patient_id=9999, fk_user_id=9999)  # Nieistniejące ID




def test_delete_nonexistent_record_by_names(setup_controllers):
    """
    Próba usunięcia nieistniejącego rekordu korzystając z first_name, last_name i username zamiast fk_patient_id i fk_user_id.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]

    with pytest.raises(KeyError, match="Nie znaleziono użytkownika lub pacjenta"):
        assigned_patients.delete_record_by_names(patient_first_name="Invalid", patient_last_name="Name", user_name="invalid_user")


# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_database_connection_error_handling():
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """

    db_controller = DatabaseController()
    assigned_patients = AssignedPatientsController(db_controller)

    # Zamknij połączenie przed próbą użycia
    db_controller.close_connection()

    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        assigned_patients.get_records_with_filters()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełne przepływy CRUD między kontrolerem, walidacją, modelem i bazą danych.
    """
    controllers = setup_controllers
    assigned_patients = controllers["assigned_patients"]
    patients = controllers["patients"]
    users_accounts = controllers["users_accounts"]
    employees = controllers["employees"]
    roles = controllers["roles"]

    # **Tworzenie danych**
    # Dodanie pacjenta i pracownika "Anna Kowalska"
    patients.add_patient("Anna", "Kowalska", "12345678901", "555123123", "anna.kowalska@example.com", "Adres 1", "1990-01-01")
    employees.add_employee("Anna", "Kowalska", "anna.kowalska@example.com", "555123123", "Psychiatra", 1)
    roles.add_role("Admin")
    patient_id = patients.get_all_patients()[0]["patient_id"]
    employee_id = employees.get_all_employees()[0]["employee_id"]
    role_id = roles.get_all_roles()[0]["role_id"]
    users_accounts.add_user_by_ids(employee_id, role_id, "anna_kowalska", "hashed_password", 1, "2025-01-01 10:00")
    user_id = users_accounts.get_users_with_names()[0]["user_id"]

    # Dodanie rekordu do assigned_patients
    assigned_patients.add_record_by_ids(patient_id, user_id)
    records = assigned_patients.get_records_with_filters()
    assert len(records) == 1
    assert records[0]["fk_patient_id"] == patient_id
    assert records[0]["fk_user_id"] == user_id

    # **Dodanie nowego pracownika i pacjenta dla aktualizacji**
    patients.add_patient("Jan", "Nowak", "98765432109", "555222333", "jan.nowak@example.com", "Adres 2", "1980-02-02")
    employees.add_employee("Jan", "Nowak", "jan.nowak@example.com", "555222333", "Psychoterapeuta", 1)
    roles.add_role("User")
    users_accounts.add_user_by_names("Jan", "Nowak", "User", "jan_nowak", "hashed_password", 1, "2025-01-02 11:00")
    new_patient_id = patients.get_all_patients()[1]["patient_id"]
    new_user_id = users_accounts.get_users_with_names()[1]["user_id"]
    assignment_id = records[0]["assignment_id"]

    # **Aktualizacja rekordu**
    assigned_patients.update_record_by_ids(assignment_id, fk_patient_id=new_patient_id, fk_user_id=new_user_id)
    updated_record = assigned_patients.get_records_with_filters()[0]
    assert updated_record["fk_patient_id"] == new_patient_id
    assert updated_record["fk_user_id"] == new_user_id

    # **Filtrowanie rekordów**
    filtered_records = assigned_patients.get_records_with_filters(filters=[{"column": "fk_user_id", "operator": "=", "value": new_user_id}])
    assert len(filtered_records) == 1
    assert filtered_records[0]["fk_patient_id"] == new_patient_id

    # **Usuwanie rekordu**
    assigned_patients.delete_record_by_id(assignment_id)

    # Weryfikacja usunięcia
    records_after_delete = assigned_patients.get_records_with_filters()
    assert len(records_after_delete) == 0



