# test_integration_users_accounts.py

import os
import sqlite3
import pytest
from controllers.database_controller import DatabaseController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.employees_controller import EmployeesController
from controllers.roles_controller import RolesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla testów UsersAccounts.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "employees": EmployeesController(db_controller),
        "roles": RolesController(db_controller),
        "users_accounts": UsersAccountsController(db_controller)
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM users_accounts")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM roles")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()



# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_users_accounts.py

def test_add_record_with_valid_data_by_ids(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi, korzystając z employee_id i role_id.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")

    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_all_roles()[0]["role_id"]

    # Dodanie użytkownika
    users_accounts_controller.add_user_by_ids(
        employee_id,
        role_id,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Weryfikacja
    users = users_accounts_controller.get_users_with_names()
    assert len(users) == 1
    assert users[0]["username"] == "jankowalski"


def test_add_record_with_valid_data_by_names(setup_controllers):
    """
    Testuje poprawne dodanie rekordu z poprawnymi danymi, korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    # Dodanie użytkownika
    users_accounts_controller.add_user_by_names(
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Weryfikacja
    users = users_accounts_controller.get_users_with_names()
    assert len(users) == 1
    assert users[0]["username"] == "annanowak"


def test_add_record_with_missing_data_by_ids(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi, korzystając z employee_id i role_id.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba dodania z brakującymi danymi
    with pytest.raises(ValueError, match="Błąd integralności: Sprawdź, czy dane są unikalne."):
        users_accounts_controller.add_user_by_ids(
            None, 1, "username", "hashed_password", 1, "2025-01-01 10:00"
        )


def test_add_record_with_missing_data_by_names(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi, korzystając z first_name, last_name i role_name.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba dodania z brakującymi danymi
    with pytest.raises(ValueError, match="Błąd walidacji: Imię i nazwisko musi być ciągiem znaków."):
        users_accounts_controller.add_user_by_names(
            None, "LastName", "RoleName", "username", "hashed_password", 1, "2025-01-01 10:00"
        )


def test_add_record_with_invalid_data_by_ids(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi, korzystając z employee_id i role_id.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba dodania z nieprawidłowymi danymi
    with pytest.raises(ValueError, match="Błąd integralności: Sprawdź, czy dane są unikalne."):
        users_accounts_controller.add_user_by_ids(
            999, 1, "invaliduser", "hashed_password", 1, "2025-01-01 10:00"
        )


def test_add_record_with_invalid_data_by_names(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi, korzystając z first_name, last_name i role_name.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba dodania z nieprawidłowymi danymi
    with pytest.raises(ValueError, match="Błąd walidacji: Pracownik 'Invalid Name' nie istnieje."):
        users_accounts_controller.add_user_by_names(
            "Invalid", "Name", "InvalidRole", "invaliduser", "hashed_password", 1, "2025-01-01 10:00"
        )


def test_add_record_with_duplicate_by_ids(setup_controllers):
    """
    Testuje próbę dodania rekordu z duplikatem, korzystając z employee_id i role_id.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")

    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_all_roles()[0]["role_id"]

    users_accounts_controller.add_user_by_ids(
        employee_id,
        role_id,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Błąd integralności: Sprawdź, czy dane są unikalne."):
        users_accounts_controller.add_user_by_ids(
            employee_id,
            role_id,
            "anotherusername",
            "another_password",
            1,
            "2025-01-02 10:00"
        )


def test_add_record_with_duplicate_by_names(setup_controllers):
    """
    Testuje próbę dodania rekordu z duplikatem, korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    users_accounts_controller.add_user_by_names(
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Nazwa użytkownika 'annanowak' już istnieje w tabeli users_accounts."):
        users_accounts_controller.add_user_by_names(
            "Anna",
            "Nowak",
            "Manager",
            "annanowak",
            "another_password",
            1,
            "2025-01-02 10:00"
        )


def test_add_record_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania rekordu do pustej bazy danych.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba dodania rekordu do pustej bazy
    with pytest.raises(ValueError, match="Błąd integralności: Sprawdź, czy dane są unikalne."):
        users_accounts_controller.add_user_by_ids(
            1, 1, "testuser", "hashed_password", 1, "2025-01-01 10:00"
        )



# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_users_accounts.py


def test_get_record_by_ids(setup_controllers):
    # Przygotowanie kontrolerów
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Psychiatra",
        is_medical_staff=True
    )
    roles_controller.add_role("Admin")

    # Pobranie `employee_id` i `role_id`
    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_all_roles()[0]["role_id"]

    # Dodanie użytkownika
    user_id = users_accounts_controller.add_user_by_ids(
        employee_id=employee_id,
        role_id=role_id,
        username="jankowalski",
        password_hash="hashed_password",
        is_active=1,
        created_at="2025-01-01 10:00"
    )
    print(f"DEBUG: Added user_id: {user_id}")
    assert user_id is not None, "user_id powinien być różny od None."

    # Pobranie użytkownika za pomocą `get_users_with_names`
    users = users_accounts_controller.get_users_with_names(
        filters=[{"column": "ua.user_id", "operator": "=", "value": user_id}]
    )
    print(f"DEBUG: Retrieved users: {users}")

    # Weryfikacja wyników
    assert len(users) == 1, "Powinien zostać zwrócony dokładnie jeden rekord."
    assert users[0]["username"] == "jankowalski"
    assert users[0]["employee_name"] == "Jan Kowalski"
    assert users[0]["role_name"] == "Admin"







def test_get_record_by_names(setup_controllers):
    """
    Testuje poprawne pobranie istniejącego rekordu korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    users_accounts_controller.add_user_by_names(
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Pobranie użytkownika
    users = users_accounts_controller.get_users_with_names(filters=[{"column": "username", "operator": "=", "value": "annanowak"}])
    assert len(users) == 1
    assert users[0]["username"] == "annanowak"


def test_get_nonexistent_record(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba pobrania nieistniejącego użytkownika
    users = users_accounts_controller.get_users_with_names(filters=[{"column": "username", "operator": "=", "value": "nonexistent"}])
    assert len(users) == 0


def test_get_all_records(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    users_accounts_controller.add_user_by_ids(
        employees_controller.get_all_employees()[0]["employee_id"],
        roles_controller.get_all_roles()[0]["role_id"],
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )
    users_accounts_controller.add_user_by_names(
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Pobranie wszystkich użytkowników
    users = users_accounts_controller.get_users_with_names()
    assert len(users) == 2


def test_get_records_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy danych.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Pobranie użytkowników
    users = users_accounts_controller.get_users_with_names()
    assert len(users) == 0


def test_get_records_with_filters_by_ids(setup_controllers):
    users_accounts_controller = setup_controllers["users_accounts"]
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]

    # Dodaj dane testowe
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", True)
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psychiatra", True)
    roles_controller.add_role("Admin")
    roles_controller.add_role("User")

    users_accounts_controller.add_user_by_ids(
        employee_id=1, role_id=1, username="jan_kowalski", password_hash="hashed_pw", is_active=1, created_at="2025-01-01 10:00"
    )
    users_accounts_controller.add_user_by_ids(
        employee_id=2, role_id=2, username="anna_nowak", password_hash="hashed_pw", is_active=1, created_at="2025-01-03 10:00"
    )

    # Pobierz dane
    users = users_accounts_controller.get_users_with_names(
        filters=[{"column": "ua.is_active", "operator": "=", "value": 1}]
    )
    assert len(users) == 2
    assert users[0]["employee_name"] == "Jan Kowalski"
    assert users[1]["employee_name"] == "Anna Nowak"



def test_get_records_with_filters_by_names(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów, korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    users_accounts_controller.add_user_by_names(
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Pobranie użytkowników z filtrem
    users = users_accounts_controller.get_users_with_names(filters=[{"column": "username", "operator": "=", "value": "annanowak"}])
    assert len(users) == 1
    assert users[0]["username"] == "annanowak"


def test_get_service_id_and_name(setup_controllers):
    """
    Testuje próbę pobrania ID i nazwy usługi.
    """
    roles_controller = setup_controllers["roles"]

    # Dodanie danych testowych
    roles_controller.add_role("Manager")

    # Pobranie roli
    role_id = roles_controller.get_all_roles()[0]["role_id"]
    role_name = roles_controller.get_all_roles()[0]["role_name"]
    assert role_id is not None
    assert role_name == "Manager"


def test_missing_dependencies_in_model(setup_controllers):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba dodania użytkownika bez istniejącego pracownika i roli
    with pytest.raises(ValueError, match="Błąd integralności: Sprawdź, czy dane są unikalne."):
        users_accounts_controller.add_user_by_ids(999, 1, "testuser", "hashed_password", 1, "2025-01-01 10:00")



# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_users_accounts.py

def test_update_user_with_valid_data_by_ids(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi, korzystając z employee_id i role_id.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    employee_id_jan = employees_controller.get_all_employees()[0]["employee_id"]
    role_id_admin = roles_controller.get_all_roles()[0]["role_id"]

    users_accounts_controller.add_user_by_ids(
        employee_id_jan,
        role_id_admin,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    user_id = users_accounts_controller.get_users_with_names()[0]["user_id"]

    employee_id_anna = employees_controller.get_all_employees()[1]["employee_id"]
    role_id_manager = roles_controller.get_all_roles()[1]["role_id"]

    # Aktualizacja użytkownika
    users_accounts_controller.update_user_by_ids(
        user_id,
        employee_id_anna,
        role_id_manager,
        "annanowak",
        "new_hashed_password",
        0,
        "2025-01-02 11:00"
    )

    # Weryfikacja
    updated_user = users_accounts_controller.get_users_with_names()[0]
    assert updated_user["username"] == "annanowak"


def test_update_user_with_valid_data_by_names(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi, korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    users_accounts_controller.add_user_by_names(
        "Jan",
        "Kowalski",
        "Admin",
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    user_id = users_accounts_controller.get_users_with_names()[0]["user_id"]

    # Aktualizacja użytkownika
    users_accounts_controller.update_user_by_names(
        user_id,
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "new_hashed_password",
        0,
        "2025-01-02 11:00"
    )

    # Weryfikacja
    updated_user = users_accounts_controller.get_users_with_names()[0]
    assert updated_user["username"] == "annanowak"


def test_update_user_with_invalid_data_by_ids(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi, korzystając z employee_id i role_id.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")

    users_accounts_controller.add_user_by_names(
        "Jan",
        "Kowalski",
        "Admin",
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Próba aktualizacji z nieistniejącymi ID
    with pytest.raises(ValueError, match="Pracownik o ID 999 nie istnieje."):
        users_accounts_controller.update_user_by_ids(
            1, 999, 1, "invaliduser", "invalid_hash", 0, "2025-01-01 10:00"
        )


def test_update_user_with_invalid_data_by_names(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi, korzystając z first_name, last_name i role_name.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba aktualizacji z nieistniejącymi nazwami
    with pytest.raises(ValueError, match="Błąd walidacji: Pracownik 'NonExistent User' nie istnieje."):
        users_accounts_controller.update_user_by_names(
            1, "NonExistent", "User", "InvalidRole", "newuser", "new_hash", 0, "2025-01-01 10:00"
        )


def test_update_nonexistent_user(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba aktualizacji nieistniejącego użytkownika
    with pytest.raises(KeyError, match="Nie znaleziono użytkownika o podanym ID."):
        users_accounts_controller.update_user_by_ids(
            9999, None, None, "nonexistent", "hash", 1, "2025-01-01 10:00"
        )


def test_update_user_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez danych lub z brakującymi danymi.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")

    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_all_roles()[0]["role_id"]

    users_accounts_controller.add_user_by_ids(
        employee_id,
        role_id,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    user_id = users_accounts_controller.get_users_with_names()[0]["user_id"]

    # Próba aktualizacji bez podania danych
    with pytest.raises(ValueError, match="Błąd walidacji: Brak danych do aktualizacji."):
        users_accounts_controller.update_user_by_ids(user_id)


def test_update_user_with_unique_constraint_violation(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu naruszającą ograniczenia unikalności dla username i employee_id.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    employee_id_jan = employees_controller.get_all_employees()[0]["employee_id"]
    role_id_admin = roles_controller.get_all_roles()[0]["role_id"]
    employee_id_anna = employees_controller.get_all_employees()[1]["employee_id"]
    role_id_manager = roles_controller.get_all_roles()[1]["role_id"]

    users_accounts_controller.add_user_by_ids(
        employee_id_jan,
        role_id_admin,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )
    users_accounts_controller.add_user_by_ids(
        employee_id_anna,
        role_id_manager,
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    user_id = users_accounts_controller.get_users_with_names()[0]["user_id"]

    # Próba aktualizacji naruszająca unikalność
    with pytest.raises(ValueError, match="Błąd walidacji: Pracownik o ID 2 już istnieje w tabeli users_accounts."):
        users_accounts_controller.update_user_by_ids(user_id, employee_id_anna, role_id_admin, "annanowak")



# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_users_accounts.py

def test_delete_record_by_ids(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z employee_id i role_id.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")

    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_all_roles()[0]["role_id"]

    users_accounts_controller.add_user_by_ids(
        employee_id,
        role_id,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Weryfikacja dodania
    users = users_accounts_controller.get_users_with_names()
    assert len(users) == 1

    # Usunięcie użytkownika
    user_id = users[0]["user_id"]
    users_accounts_controller.delete_user(user_id)

    # Weryfikacja usunięcia
    users_after_deletion = users_accounts_controller.get_users_with_names()
    assert len(users_after_deletion) == 0, "Rekord nie został usunięty."


def test_delete_record_by_names(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")

    users_accounts_controller.add_user_by_names(
        "Anna",
        "Nowak",
        "Manager",
        "annanowak",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # Weryfikacja dodania
    users = users_accounts_controller.get_users_with_names()
    assert len(users) == 1

    # Usunięcie użytkownika
    user_id = users[0]["user_id"]
    users_accounts_controller.delete_user(user_id)

    # Weryfikacja usunięcia
    users_after_deletion = users_accounts_controller.get_users_with_names()
    assert len(users_after_deletion) == 0, "Rekord nie został usunięty."


def test_delete_nonexistent_record_by_ids(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z employee_id i role_id.
    """
    users_accounts_controller = setup_controllers["users_accounts"]

    # Próba usunięcia nieistniejącego użytkownika
    with pytest.raises(KeyError, match="Nie znaleziono użytkownika o podanym ID."):
        users_accounts_controller.delete_user(9999)


def test_delete_nonexistent_record_by_names(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z first_name, last_name i role_name.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")

    # Próba usunięcia użytkownika, który nie istnieje
    with pytest.raises(KeyError, match="Nie znaleziono użytkownika o podanym ID."):
        users_accounts_controller.delete_user(9999)



# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# test_integration_users_accounts.py

def test_database_connection_errors():
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    db_controller = DatabaseController()
    users_accounts_controller = None

    try:
        db_controller.connect_to_database()
        db_controller.close_connection()  # Celowe zamknięcie połączenia

        users_accounts_controller = UsersAccountsController(db_controller)

        # Próba wykonania operacji przy zamkniętym połączeniu
        with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
            users_accounts_controller.get_users_with_names()
    finally:
        if db_controller.connection:
            db_controller.close_connection()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD dla tabeli users_accounts, walidacji i modelu w różnych kombinacjach.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    # 1. Tworzenie pracownika i roli
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    roles_controller.add_role("Admin")
    employee_id = employees_controller.get_all_employees()[0]["employee_id"]
    role_id = roles_controller.get_all_roles()[0]["role_id"]

    # 2. Dodanie użytkownika za pomocą ID
    users_accounts_controller.add_user_by_ids(
        employee_id,
        role_id,
        "jankowalski",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )

    # 3. Pobranie użytkownika
    users = users_accounts_controller.get_users_with_names(filters=[{"column": "username", "operator": "=", "value": "jankowalski"}])
    assert len(users) == 1
    assert users[0]["username"] == "jankowalski"

    # 4. Aktualizacja użytkownika za pomocą ID
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psycholog kliniczny", 1)
    roles_controller.add_role("Manager")
    employee_id_new = employees_controller.get_all_employees()[1]["employee_id"]
    role_id_new = roles_controller.get_all_roles()[1]["role_id"]

    user_id = users[0]["user_id"]
    users_accounts_controller.update_user_by_ids(
        user_id,
        employee_id_new,
        role_id_new,
        "annanowak",
        "new_hashed_password",
        0,
        "2025-01-02 11:00"
    )

    # 5. Pobranie zaktualizowanego użytkownika
    updated_users = users_accounts_controller.get_users_with_names(filters=[{"column": "username", "operator": "=", "value": "annanowak"}])
    assert len(updated_users) == 1
    assert updated_users[0]["username"] == "annanowak"

    # 6. Usunięcie użytkownika
    users_accounts_controller.delete_user(user_id)

    # 7. Weryfikacja usunięcia
    deleted_users = users_accounts_controller.get_users_with_names(filters=[{"column": "username", "operator": "=", "value": "annanowak"}])
    assert len(deleted_users) == 0, "Rekord nie został poprawnie usunięty."

    # 8. Próba dodania z duplikatem dla `employee_id`
    users_accounts_controller.add_user_by_ids(
        employee_id,
        role_id,
        "newuser",
        "hashed_password",
        1,
        "2025-01-01 10:00"
    )
    with pytest.raises(ValueError, match="Błąd integralności: Sprawdź, czy dane są unikalne."):
        users_accounts_controller.add_user_by_ids(
            employee_id,
            role_id_new,
            "duplicateuser",
            "duplicate_hashed_password",
            1,
            "2025-01-01 10:00"
        )

    # 9. Pobranie wszystkich rekordów
    all_users = users_accounts_controller.get_users_with_names()
    assert len(all_users) == 1
    assert all_users[0]["username"] == "newuser"






