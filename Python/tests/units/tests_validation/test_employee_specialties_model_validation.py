# test_employee_specialties_model_validation.py

import os
import pytest
from validators.employee_specialties_model_validation import (
    validate_employee_name,
    validate_specialty_name,
    validate_employee_id,
    validate_specialty_id,
    validate_unique_employee_specialty,
    validate_operator_and_value,
    validate_filters_and_sorting,
    validate_add_employee_specialty_by_names,
)
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.specialties_controller import SpecialtiesController
from models.employee_specialties import EmployeeSpecialties
from models.specialties import Specialties
from models.employees import Employees

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu EmployeeSpecialties.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    employees_controller = EmployeesController(db_controller)
    employees_controller.create_table()

    # Tworzenie tabeli `employees`
    employees_model = Employees(db_controller)
    employees_model.create_table()

    specialties_controller = SpecialtiesController(db_controller)
    specialties_controller.create_table()

    # Tworzenie tabeli `specialties`
    specialties_model = Specialties(db_controller)
    specialties_model.create_table()

    employee_specialties = EmployeeSpecialties(db_controller)
    employee_specialties.create_table()

    yield employees_controller, specialties_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM employees")
        db_controller.connection.execute("DELETE FROM specialties")
        db_controller.connection.execute("DELETE FROM employee_specialties")
    db_controller.close_connection()

def test_validate_employee_name():
    """Testuje walidację imienia i nazwiska pracownika."""
    # Poprawne dane
    validate_employee_name("Jan", "Kowalski")
    validate_employee_name("Maria", "Nowak")
    validate_employee_name("ĄęÓł", "ŹżĆń")
    
    # Niepoprawne dane dla imienia
    with pytest.raises(ValueError, match="Imię musi być ciągiem znaków."):
        validate_employee_name(123, "Kowalski")
    with pytest.raises(ValueError, match="Imię musi mieć od 3 do 100 znaków."):
        validate_employee_name("Jo", "Kowalski")
    with pytest.raises(ValueError, match="Imię zawiera niedozwolone znaki."):
        validate_employee_name("Jan1", "Kowalski")
    with pytest.raises(ValueError, match="Imię nie może być puste."):
        validate_employee_name("", "Kowalski")
    with pytest.raises(ValueError, match="Imię zawiera niedozwolone znaki."):
        validate_employee_name("Pan 2", "Jaweł ")

    # Niepoprawne dane dla nazwiska
    with pytest.raises(ValueError, match="Nazwisko musi być ciągiem znaków."):
        validate_employee_name("Jan", 123)
    with pytest.raises(ValueError, match="Nazwisko musi mieć od 3 do 100 znaków."):
        validate_employee_name("Jan", "A")
    with pytest.raises(ValueError, match="Nazwisko zawiera niedozwolone znaki."):
        validate_employee_name("Jan", "Kowalski!")
    with pytest.raises(ValueError, match="Nazwisko nie może być puste."):
        validate_employee_name("Jan", "")
    with pytest.raises(ValueError, match="Nazwisko zawiera niedozwolone znaki."):
        validate_employee_name("Pan", "Jaweł 2")


def test_validate_specialty_name():
    """Testuje walidację nazwy specjalizacji."""
    # Poprawne dane
    validate_specialty_name("Psychiatra dorosłych")
    validate_specialty_name("Specjalność - Test (Zaawansowany)")
    validate_specialty_name("Specjalność: Dietetyk")
    validate_specialty_name("Psychiatra dzieci, młodzieży.")
    validate_specialty_name("Terapia poznawczo behawioralna /CBT)")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa specjalizacji musi być ciągiem znaków."):
        validate_specialty_name(123)
    with pytest.raises(ValueError, match="Nazwa specjalizacji nie może być pusta."):
        validate_specialty_name("")
    with pytest.raises(ValueError, match="Nazwa specjalizacji musi mieć od 3 do 100 znaków."):
        validate_specialty_name("AB")
    with pytest.raises(ValueError, match="Nazwa specjalizacji musi mieć od 3 do 100 znaków."):
        validate_specialty_name("A" * 101)
    with pytest.raises(ValueError, match="Nazwa specjalizacji zawiera niedozwolone znaki."):
        validate_specialty_name("!@#$%^&*")
    with pytest.raises(ValueError, match="Nazwa specjalizacji zawiera niedozwolone znaki."):
        validate_specialty_name("Dietetyk 50%")  # Zawiera cyfry


def test_validate_add_employee_specialty_by_names():
    """Testuje walidację danych wejściowych do metody add_employee_specialty_by_names."""
    # Poprawne dane
    validate_add_employee_specialty_by_names("Jan", "Kowalski", "Kardiologia")
        # Poprawne dane
    validate_add_employee_specialty_by_names("JaĆn", "ŚKowalski", "Kardiologia ()")
        # Poprawne dane
    validate_add_employee_specialty_by_names("Jan", "Kowalski", "Kardiologia, : /.")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Imię musi mieć od 3 do 100 znaków."):
        validate_add_employee_specialty_by_names("J", "Kowalski", "Kardiologia")
        # Niepoprawne dane
    with pytest.raises(ValueError, match="Imię zawiera niedozwolone znaki."):
        validate_add_employee_specialty_by_names("Jss1dsd", "Kow2alski", "Kardiologia")
        # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwisko zawiera niedozwolone znaki."):
        validate_add_employee_specialty_by_names("Jxzcx", "Kow2alski", "Kardiologia")



def test_validate_employee_id(setup_controllers):
    # Rozpakowanie kontrolerów
    # pylint: disable=W0612
    employees_controller, specialties_controller = setup_controllers

    # Dodanie danych do tabeli employees
    employees_controller.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1 # 1 to wartość kolumny is_medical_staff
    )

    # Poprawny przypadek - ID istnieje
    try:
        validate_employee_id(employees_controller, 1)  # ID = 1 istnieje
    except ValueError:
        pytest.fail("Walidacja ID pracownika nie powinna zgłaszać wyjątku dla istniejącego ID.")

    # Niepoprawny przypadek - ID nie istnieje
    with pytest.raises(ValueError, match="Pracownik o ID 2 nie istnieje."):
        validate_employee_id(employees_controller, 2)  # ID = 2 nie istnieje


def test_validate_specialty_id(setup_controllers):
    """
    Testuje funkcję validate_specialty_id.

    Sprawdza dwa przypadki:
    1. Poprawny ID specjalizacji (specjalizacja istnieje w bazie danych).
    2. Niepoprawny ID specjalizacji (specjalizacja nie istnieje w bazie danych).
    """
    # Rozpakowanie kontrolerów
    # pylint: disable=W0612
    employees_controller, specialties_controller = setup_controllers

    # Dodanie specjalności do tabeli
    specialties_controller.add_specialty("Kardiologia")

    # Poprawny przypadek - ID istnieje
    try:
        validate_specialty_id(specialties_controller, 1)  # ID = 1 istnieje
    except ValueError:
        pytest.fail("Walidacja ID specjalizacji nie powinna zgłaszać wyjątku dla istniejącego ID.")

    # Niepoprawny przypadek - ID nie istnieje
    with pytest.raises(ValueError, match="Specjalizacja o ID 2 nie istnieje."):
        validate_specialty_id(specialties_controller, 2)  # ID = 2 nie istnieje


def test_validate_unique_employee_specialty(setup_controllers):
    # Rozpakowanie kontrolerów
    employees_controller, specialties_controller = setup_controllers
    db_controller = employees_controller.db_controller

    # Dodanie danych do tabeli employees i specialties
    employees_controller.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1
    )
    specialties_controller.add_specialty("Kardiologia")

    # Dodanie danych do tabeli employee_specialties
    db_controller.connection.execute(
        "INSERT INTO employee_specialties (employee_id, specialty_id) VALUES (?, ?)", (1, 1)
    )

    # Sprawdzenie poprawnych danych
    validate_unique_employee_specialty(db_controller, 2, 1)

    # Sprawdzenie istniejącej kombinacji
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i specialty_id=1 już istnieje."):
        validate_unique_employee_specialty(db_controller, 1, 1)



def test_validate_operator_and_value():
    """Testuje walidację operatorów i wartości."""
    # Poprawne dane
    validate_operator_and_value("LIKE", "Zgoda%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", ["Zgoda na leczenie", "Zgoda na przetwarzanie danych osobowych (RODO)"])
    validate_operator_and_value("=", "Szkolenie wewnętrzne")

    # Niepoprawne operatory
    with pytest.raises(ValueError, match="Nieobsługiwany operator: INVALID"):
        validate_operator_and_value("INVALID", "Wartość")
    
    # Niepoprawne wartości
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")
    with pytest.raises(ValueError, match="Operator BETWEEN wymaga krotki zawierającej dwie wartości."):
        validate_operator_and_value("BETWEEN", (1,))
    with pytest.raises(ValueError, match="Wartość dla operatora IN musi być niepustą listą lub krotką."):
        validate_operator_and_value("IN", [])


def test_validate_filters_and_sorting():
    """Testuje walidację filtrów i sortowania."""
    valid_columns = ["employee_specialty_id", "employee_id", "specialty_id"]
    
    # Poprawne dane
    validate_filters_and_sorting(
        filters=[{"column": "employee_id", "operator": "LIKE", "value": "Zgoda%"}],
        sort_by=[("employee_id", "ASC")],
        valid_columns=valid_columns,
    )
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters=[{"column": "employee_id"}], sort_by=None, valid_columns=valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(
            filters=[{"column": "invalid_column", "operator": "=", "value": "Zgoda na leczenie"}],
            sort_by=None,
            valid_columns=valid_columns,
        )
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna sortowania: invalid_column."):
        validate_filters_and_sorting(
            filters=None,
            sort_by=[("invalid_column", "ASC")],
            valid_columns=valid_columns,
        )