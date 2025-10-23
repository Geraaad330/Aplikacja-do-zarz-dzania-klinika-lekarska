# test_users_accounts_model_validation.py

import os
import pytest
from models.users_accounts import UsersAccounts
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.roles_controller import RolesController
from validators.users_accounts_model_validation import (
    validate_name_field,
    validate_role_name,
    validate_employee_id_exists,
    validate_role_id_exists,
    validate_unique_employee_id,
    validate_unique_username,
    validate_datetime_field,
)

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Fixture do konfiguracji bazy danych testowej.
    Tworzy tabele i zapewnia środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabel
    employees_controller = EmployeesController(db_controller)
    roles_controller = RolesController(db_controller)
    employees_controller.create_table()
    roles_controller.create_table()

    users_model = UsersAccounts(db_controller)
    users_model.create_table() 

    yield db_controller, employees_controller, roles_controller

    # Czyszczenie bazy danych
    with db_controller.connection:
        db_controller.connection.execute("DELETE FROM employees")
        db_controller.connection.execute("DELETE FROM roles")
        db_controller.connection.execute("DELETE FROM users_accounts")
    db_controller.close_connection()


def test_validate_name_field():
    """
    Testuje walidację pola imienia i nazwiska.
    """
    # Poprawne dane
    validate_name_field("Jan Kowalski")
    validate_name_field("Maria Żółć")

    # Błędne dane
    with pytest.raises(ValueError, match="Imię i nazwisko musi być ciągiem znaków."):
        validate_name_field(123)
    with pytest.raises(ValueError, match="Imię i nazwisko nie może być puste."):
        validate_name_field("")
    with pytest.raises(ValueError, match="Imię i nazwisko musi mieć od 3 do 100 znaków."):
        validate_name_field("Jo")
    with pytest.raises(ValueError, match="Imię i nazwisko zawiera niedozwolone znaki."):
        validate_name_field("Jan123!")


def test_validate_role_name():
    """
    Testuje walidację pola nazwy roli.
    """
    # Poprawne dane
    validate_role_name("Administrator")
    validate_role_name("Admin: test")
    validate_role_name("Admin, test.")
    validate_role_name("Admin: (test)")

    # Błędne dane
    with pytest.raises(ValueError, match="Nazwa roli musi być ciągiem znaków."):
        validate_role_name(123)
    with pytest.raises(ValueError, match="Nazwa roli nie może być pusta."):
        validate_role_name("")
    with pytest.raises(ValueError, match="Nazwa roli musi mieć od 3 do 100 znaków."):
        validate_role_name("Ad")
    with pytest.raises(ValueError, match="Nazwa roli zawiera niedozwolone znaki."):
        validate_role_name("Admin@123")


def test_validate_employee_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `employee_id`.
    """
    _, employees_controller, _ = setup_controllers
    employees_controller.add_employee("Jan", "Kowalski", "jan@example.com", "123456789", "Psychiatra", 1)
    employee_id = employees_controller.get_all_employees()[0]["employee_id"]

    # Poprawne dane
    validate_employee_id_exists(employees_controller, employee_id)

    # Błędne dane
    with pytest.raises(ValueError, match="Pracownik o ID 999 nie istnieje."):
        validate_employee_id_exists(employees_controller, 999)


def test_validate_role_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `role_id`.
    """
    _, _, roles_controller = setup_controllers
    roles_controller.add_role("Manager")
    role_id = roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"]

    # Poprawne dane
    validate_role_id_exists(roles_controller, role_id)

    # Błędne dane
    with pytest.raises(ValueError, match="Rola o ID 999 nie istnieje."):
        validate_role_id_exists(roles_controller, 999)


def test_validate_unique_employee_id(setup_controllers):
    """
    Testuje unikalność `employee_id`.
    """
    db_controller, employees_controller, roles_controller = setup_controllers

    # Dodanie danych testowych do tabel employees i roles
    employees_controller.add_employee("Jan", "Kowalski", "jan@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Manager")

    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"]

    # Dodanie danych do tabeli users_accounts za pomocą modelu
    users_model = UsersAccounts(db_controller)
    users_model.add_user_by_ids(
        employee_id=employee_id,
        role_id=role_id,
        username="janek",
        password_hash="hash",
        is_active=1,
        created_at="2025-01-01 10:00",
    )

    # Poprawne dane
    validate_unique_employee_id(db_controller, 999)

    # Błędne dane
    with pytest.raises(ValueError, match=f"Pracownik o ID {employee_id} już istnieje w tabeli users_accounts."):
        validate_unique_employee_id(db_controller, employee_id)



def test_validate_unique_username(setup_controllers):
    """
    Testuje unikalność `username`.
    """
    db_controller, employees_controller, roles_controller = setup_controllers

    # Dodanie danych testowych do tabel employees i roles
    employees_controller.add_employee("Anna", "Nowak", "anna@example.com", "987654321", "Psychiatra", 1)
    roles_controller.add_role("Administrator")

    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_role_by_column("role_name", "Administrator")[0]["role_id"]

    # Dodanie użytkownika do tabeli users_accounts za pomocą modelu
    users_model = UsersAccounts(db_controller)
    users_model.add_user_by_ids(
        employee_id=employee_id,
        role_id=role_id,
        username="admin",
        password_hash="hash",
        is_active=1,
        created_at="2025-01-01 10:00",
    )

    # Poprawne dane
    validate_unique_username(db_controller, "new_user")

    # Błędne dane
    with pytest.raises(ValueError, match="Nazwa użytkownika 'admin' już istnieje w tabeli users_accounts."):
        validate_unique_username(db_controller, "admin")


def test_validate_datetime_field():
    """
    Testuje walidację pola datetime.
    """
    # Poprawne dane
    validate_datetime_field("2025-01-01 10:00")
    validate_datetime_field("1900-08-21 01:00")
    validate_datetime_field("1999-01-01 23:59")
    validate_datetime_field("1988-12-31 10:00")

    # Błędne dane
    with pytest.raises(ValueError, match="Pole datetime musi być ciągiem znaków."):
        validate_datetime_field(123)
    with pytest.raises(ValueError, match="Wartość '2025-18-01 10:00' nie jest w formacie YYYY-MM-DD HH:MM."):
        validate_datetime_field("2025-18-01 10:00")
    with pytest.raises(ValueError, match="Wartość '2025.13.01 10:00' nie jest w formacie YYYY-MM-DD HH:MM."):
        validate_datetime_field("2025.13.01 10:00")
    with pytest.raises(ValueError, match="Wartość '01-01-2025 10.00' nie jest w formacie YYYY-MM-DD HH:MM."):
        validate_datetime_field("01-01-2025 10.00")
    with pytest.raises(ValueError, match="Wartość '01-01-999 10.00' nie jest w formacie YYYY-MM-DD HH:MM."):
        validate_datetime_field("01-01-999 10.00")                    
