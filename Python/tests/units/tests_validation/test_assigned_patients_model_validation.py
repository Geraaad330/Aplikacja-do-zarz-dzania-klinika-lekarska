# test_assigned_patients_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.patients_controller import PatientController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.roles_controller import RolesController
from controllers.employees_controller import EmployeesController
from models.assigned_patients import AssignedPatients
from validators.assigned_patients_model_validation import (
    validate_name,
    validate_user_name,
    validate_patient_exists,
    validate_user_exists,
    validate_unique_assignment,
    validate_operator_and_value,
    validate_filters_and_sorting
)
from models.assigned_patients import get_valid_columns

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Fixture przygotowujący środowisko testowe z tabelami i kontrolerami.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "db_controller": db_controller,
        "patients": PatientController(db_controller),
        "users_accounts": UsersAccountsController(db_controller),
        "roles": RolesController(db_controller),
        "employees": EmployeesController(db_controller),
        "assigned_patients": AssignedPatients(db_controller)
    }

        # Tworzenie tabel
    # Tworzenie tabel dla wszystkich kontrolerów
    for controller in controllers.values():
        if hasattr(controller, "create_table"):
            controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM users_accounts")
                db_controller.connection.execute("DELETE FROM employees")
                db_controller.connection.execute("DELETE FROM roles")
                db_controller.connection.execute("DELETE FROM assigned_patients")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


def test_validate_name():
    """
    Testuje walidację imienia i nazwiska.
    """
    # Poprawne dane
    validate_name("Jan")
    validate_name("Maria Anna")
    validate_name("Maria Żółć")

    # Złe dane
    with pytest.raises(ValueError, match="Nazwa musi być ciągiem znaków."):
        validate_name(123)
    with pytest.raises(ValueError, match="Nazwa nie może być pusta."):
        validate_name("")
    with pytest.raises(ValueError, match="Nazwa musi mieć od 3 do 100 znaków."):
        validate_name("Al")
    with pytest.raises(ValueError, match="Nazwa zawiera niedozwolone znaki."):
        validate_name("Jan123!")


def test_validate_user_name():
    """
    Testuje walidację nazwy użytkownika.
    """
    # Poprawne dane
    validate_user_name("jan.kowalski")
    validate_user_name("maria123")
    validate_user_name("anna-nowak")

    # Złe dane
    with pytest.raises(ValueError, match="Nazwa użytkownika musi być ciągiem znaków."):
        validate_user_name(456)
    with pytest.raises(ValueError, match="Nazwa użytkownika nie może być pusta."):
        validate_user_name("")
    with pytest.raises(ValueError, match="Nazwa użytkownika musi mieć od 3 do 100 znaków."):
        validate_user_name("a")
    with pytest.raises(ValueError, match="Nazwa użytkownika zawiera niedozwolone znaki."):
        validate_user_name("jan@nowak")






def test_validate_user_exists(setup_controllers):
    """
    Testuje, czy walidacja poprawnie wykrywa istniejącego użytkownika.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]

    roles_controller.add_role("Administrator")
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)

    # Dodanie użytkownika za pomocą UsersAccountsController
    users_accounts_controller.add_user_by_ids(
        employee_id=1,  # Odnosi się do pracownika "Jan Kowalski" dodanego wcześniej
        role_id=1,  # Rola "admin" dodana wcześniej
        username="jan.kowalski",
        password_hash="hash",
        is_active=1,
        created_at="2025-01-01 21:37"
    )

    # Poprawna walidacja
    validate_user_exists(users_accounts_controller, "jan.kowalski")

    # Próba walidacji użytkownika, który nie istnieje
    with pytest.raises(ValueError, match="Użytkownik 'maria.nowak' nie istnieje."):
        validate_user_exists(users_accounts_controller, "maria.nowak")


def test_validate_patient_exists(setup_controllers):
    """
    Testuje, czy walidacja poprawnie wykrywa istniejącego pacjenta.
    """

    patients_controller = setup_controllers["patients"]

    # Dodanie pacjenta za pomocą PatientController
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan@kowalski.pl",
        address="ul. Warszawska 1",
        date_of_birth="1985-05-20"
    )

    # Poprawna walidacja
    validate_patient_exists(patients_controller, "Jan", "Kowalski")

    # Próba walidacji pacjenta, który nie istnieje
    with pytest.raises(ValueError, match="Pacjent 'Maria Nowak' nie istnieje."):
        validate_patient_exists(patients_controller, "Maria", "Nowak")


def test_validate_unique_assignment(setup_controllers):
    """
    Testuje unikalność kombinacji pacjenta i użytkownika.
    """
    employees_controller = setup_controllers["employees"]
    roles_controller = setup_controllers["roles"]
    users_accounts_controller = setup_controllers["users_accounts"]
    patients_controller = setup_controllers["patients"]
    assigned_patients_model = setup_controllers["assigned_patients"]

    db_controller = setup_controllers["db_controller"]


    # Dodanie roli
    roles_controller.add_role("admin")

    # Dodanie pracownika
    employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Informatyk",
        is_medical_staff=1
    )

    query = "SELECT COUNT(*) FROM employees"
    cursor = db_controller.connection.execute(query)
    record_count = cursor.fetchone()[0]
    print(f"Liczba rekordów w tabeli 'employees': {record_count}")

    # Dodanie pacjenta
    patient = patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan@kowalski.pl",
        address="ul. Warszawska 1",
        date_of_birth="1985-05-20"
    )

    assert patient is not None, "Metoda add_patient zwróciła None"

    query = "SELECT COUNT(*) FROM patients"
    cursor = db_controller.connection.execute(query)
    record_count = cursor.fetchone()[0]
    print(f"Liczba rekordów w tabeli 'patients': {record_count}")

    # Dodanie użytkownika
    user = users_accounts_controller.add_user_by_ids(
        employee_id=1,
        role_id=1,
        username="jan.kowalski",
        password_hash="hash",
        is_active=1,
        created_at="2025-01-01 21:37"
    )
    #assert user is not None, "Metoda add_user_by_ids zwróciła None"

    query = "SELECT COUNT(*) FROM users_accounts"
    cursor = db_controller.connection.execute(query)
    record_count = cursor.fetchone()[0]
    print(f"Liczba rekordów w tabeli 'users_accounts': {record_count}")



    # Dodanie rekordu do tabeli assigned_patients
    assigned_patients_model.add_record_by_ids(
        fk_patient_id=patient["patient_id"],
        fk_user_id=user["user_id"]
    )
    
    debug_table_contents(db_controller, "assigned_patients")

    query = "SELECT COUNT(*) FROM assigned_patients"
    cursor = db_controller.connection.execute(query)
    record_count = cursor.fetchone()[0]
    print(f"Liczba rekordów w tabeli 'assigned_patients': {record_count}")

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Kombinacja pacjent_id=1 i user_id=1 już istnieje."):
        validate_unique_assignment(
            db_controller=assigned_patients_model.db_controller,
            fk_patient_id=patient["patient_id"],
            fk_user_id=user["user_id"]
        )


def debug_table_contents(db_controller, table_name):
    query = f"SELECT * FROM {table_name}"
    cursor = db_controller.connection.execute(query)
    records = cursor.fetchall()
    print(f"Zawartość tabeli {table_name}:")
    for record in records:
        print(record)


def test_validate_operator_and_value():
    """
    Testuje walidację operatorów i wartości.
    """
    # Poprawne przypadki
    validate_operator_and_value("=", 10)
    validate_operator_and_value("LIKE", "test")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", [1, 2, 3])

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nieobsługiwany operator: <>."):
        validate_operator_and_value("<>")
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")
    with pytest.raises(ValueError, match="Operator BETWEEN wymaga krotki zawierającej dwie wartości."):
        validate_operator_and_value("BETWEEN", (1,))
    with pytest.raises(ValueError, match="Operator IS NULL nie wymaga przypisanej wartości."):
        validate_operator_and_value("IS NULL", 1)


def test_validate_filters_and_sorting_valid(setup_controllers):
    """
    Testuje poprawne przypadki dla validate_filters_and_sorting.
    """
    db_controller = setup_controllers["assigned_patients"].db_controller

    # Pobranie listy kolumn z tabeli assigned_patients
    valid_columns = get_valid_columns(db_controller, "assigned_patients")

    filters = [
        {"column": "fk_patient_id", "operator": "=", "value": 1},
        {"column": "fk_user_id", "operator": ">", "value": 2},
        {"column": "assignment_id", "operator": "IN", "value": [1, 2, 3]},
    ]
    sort_by = [{"column": "assignment_id", "direction": "ASC"}]

    # Walidacja powinna przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)



def test_validate_filters_and_sorting_invalid(setup_controllers):
    """
    Testuje niepoprawne przypadki dla validate_filters_and_sorting.
    """
    db_controller = setup_controllers["assigned_patients"].db_controller

    # Pobranie listy kolumn z tabeli assigned_patients
    valid_columns = get_valid_columns(db_controller, "assigned_patients")

    # Niepoprawny filtr - brak klucza "value"
    filters = [{"column": "fk_patient_id", "operator": "="}]
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Niepoprawna kolumna
    filters = [{"column": "invalid_column", "operator": "=", "value": 1}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Nieobsługiwany operator
    filters = [{"column": "fk_patient_id", "operator": "<>", "value": 1}]
    with pytest.raises(ValueError, match="Nieprawidłowy operator w filtrze: <>."):
        validate_filters_and_sorting(filters, None, valid_columns)

    # Niepoprawne sortowanie - brak klucza "direction"
    sort_by = [{"column": "assignment_id"}]
    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

    # Niepoprawna kolumna w sortowaniu
    sort_by = [{"column": "invalid_column", "direction": "ASC"}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

    # Niepoprawny kierunek sortowania
    sort_by = [{"column": "assignment_id", "direction": "INVALID"}]
    with pytest.raises(ValueError, match="Nieprawidłowy kierunek sortowania: INVALID."):
        validate_filters_and_sorting(None, sort_by, valid_columns)

