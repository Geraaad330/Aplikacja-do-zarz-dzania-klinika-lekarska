# test_employee_services_model_validation.py

import os
import pytest
from validators.employee_services_model_validation import (
    validate_employee_name,
    validate_service_name,
    validate_employee_id,
    validate_service_id,
    validate_add_employee_specialty_by_names,
    validate_add_employee_service_by_ids,
    validate_update_record_by_names,
    validate_delete_record_by_id,
    validate_delete_records_by_names,
    validate_unique_employee_service_by_names,
    validate_unique_update_by_names,
    validate_unique_employee_service,
    validate_unique_update_record_by_ids,
    validate_operator_and_value,
    validate_filters_and_sorting
)
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from models.employee_services import EmployeeServices

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu EmployeeServices.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    employees_controller = EmployeesController(db_controller)
    services_controller = ServicesController(db_controller)

    # Tworzenie tabel
    employees_controller.create_table()
    services_controller.create_table()

        # Tworzenie tabeli employee_services
    employee_services_model = EmployeeServices(db_controller)
    employee_services_model.create_table()

    yield  db_controller, employees_controller, services_controller

    # Czyszczenie danych po każdym teście
    with db_controller.connection:
        db_controller.connection.execute("DELETE FROM employees")
        db_controller.connection.execute("DELETE FROM services")
        db_controller.connection.execute("DELETE FROM employee_services")
    db_controller.close_connection()

# +-+-+-+- metody walidacji nazw rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 


def test_validate_employee_name():
    """Testuje walidację imienia i nazwiska pracownika."""
    # Poprawne dane
    validate_employee_name("Jan", "Kowalski")
    validate_employee_name("Anna", "Nowak")
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

def test_validate_service_name():
    """Testuje walidację nazwy usługi."""
    # Poprawne dane
    validate_service_name("Diagnoza i leczenie zaburzeń psychicznych")
    validate_service_name("Farmakoterapia, - (przepisywanie leków psychotropowych)")
    validate_service_name("Wsparcie: w / rozwoju umiejętności społecznych.")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa usługi musi być ciągiem znaków."):
        validate_service_name(123)
    with pytest.raises(ValueError, match="Nazwa usługi nie może być pusta."):
        validate_service_name("")
    with pytest.raises(ValueError, match="Nazwa usługi musi mieć od 3 do 100 znaków."):
        validate_service_name("AB")
    with pytest.raises(ValueError, match="Nazwa usługi musi mieć od 3 do 100 znaków."):
        validate_service_name("A" * 101)
    with pytest.raises(ValueError, match="Nazwa usługi zawiera niedozwolone znaki."):
        validate_service_name("!@#$%^&*")
    with pytest.raises(ValueError, match="Nazwa usługi zawiera niedozwolone znaki."):
        validate_service_name("Dietetyk 50%")  # Zawiera cyfry

# +-+-+-+- metody sprawdzania id -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 


def test_validate_employee_id(setup_controllers):
    """Testuje walidację ID pracownika."""
    _, employees_controller, _ = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)

    # Poprawny przypadek
    validate_employee_id(employees_controller, 1)

    # Niepoprawny przypadek
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        validate_employee_id(employees_controller, 99)


def test_validate_service_id(setup_controllers):
    """Testuje walidację ID usługi."""
    _, _, services_controller = setup_controllers

    # Dodanie danych testowych
    services_controller.add_service("Diagnoza i leczenie zaburzeń psychicznych", 60, 150)

    # Poprawny przypadek
    validate_service_id(services_controller, 1)  # Przekazujemy ID bezpośrednio do walidacji

    # Niepoprawny przypadek
    with pytest.raises(ValueError, match="Usługa o ID 99 nie istnieje."):
        validate_service_id(services_controller, 99)

# +-+-+-+- metody walidacji unikalności -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

# metoda dodawania
def test_validate_unique_employee_service(setup_controllers):
    """Testuje walidację unikalności kombinacji `employee_id` i `service_id`."""
    db_controller, employees_controller, services_controller = setup_controllers


    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    services_controller.add_service("Diagnoza i leczenie zaburzeń psychicznych", 60, 150)

    employees_controller.add_employee("Jorg", "Łazinka", "jorg.lazinka@example.com", "213769111", "Psychoterapeuta", 1)
    services_controller.add_service("Konsultacje psychiatryczne", 90, 200)

    # Dodanie rekordu do tabeli employee_services
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (1, 1))

    # Poprawny przypadek
    validate_unique_employee_service(db_controller, 2, 2)

    # Duplikat
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i service_id=1 już istnieje."):
        validate_unique_employee_service(db_controller, 1, 1)


# metoda dodawania
def test_validate_unique_employee_service_by_names(setup_controllers):
    """
    Testuje walidację unikalności rekordu na podstawie imienia, nazwiska i nazwy usługi.
    """
    db_controller, employees_controller, services_controller = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    services_controller.add_service("Diagnoza i leczenie", 60, 150)

    employees_controller.add_employee("Jorg", "Łazinka", "jorg.lazinka@example.com", "213769111", "Psychoterapeuta", 1)
    services_controller.add_service("Konsultacje psychiatryczne", 90, 200)

    # Dodanie rekordu do tabeli employee_services
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (1, 1))

    # Poprawny przypadek - brak kolizji
    validate_unique_employee_service_by_names(db_controller, employees_controller, services_controller, "Jorg", "Łazinka", "Konsultacje psychiatryczne")

    # Niepoprawny przypadek - rekord już istnieje
    with pytest.raises(ValueError, match="Rekord dla Jan Kowalski i usługi 'Diagnoza i leczenie' już istnieje."):
        validate_unique_employee_service_by_names(db_controller, employees_controller, services_controller, "Jan", "Kowalski", "Diagnoza i leczenie")


def test_validate_unique_update_by_names(setup_controllers):
    """Testuje walidację unikalności aktualizacji rekordu na podstawie nowych nazw."""
    db_controller, employees_controller, services_controller = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psychiatra", 1)
    services_controller.add_service("Diagnoza", 60, 150)
    services_controller.add_service("Terapia", 90, 200)

    # Dodanie rekordów do tabeli
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (1, 1))
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (2, 2))

    # Poprawny przypadek - brak konfliktu
    validate_unique_update_by_names(db_controller, employees_controller, services_controller, 2, 2, "Anna", "Nowak", "Terapia")

    # Niepoprawny przypadek - konflikt unikalności
    with pytest.raises(ValueError, match="Rekord z Jan Kowalski i usługą 'Diagnoza' już istnieje."):
        validate_unique_update_by_names(db_controller, employees_controller, services_controller, 2, 2, "Jan", "Kowalski", "Diagnoza")







def test_validate_unique_update_record_by_ids(setup_controllers):
    """
    Testuje walidację unikalności dla metody `update_record_by_ids`.
    Sprawdza, czy kombinacja `employee_id` i `service_id` jest unikalna z wyłączeniem aktualizowanego rekordu.
    """
    db_controller, employees_controller, services_controller = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    employees_controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Psychiatra", 1)
    services_controller.add_service("Diagnoza", 60, 150)
    services_controller.add_service("Terapia", 90, 200)

    # Dodanie rekordów do tabeli employee_services
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (1, 1))
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (2, 2))

    # Poprawny przypadek - kombinacja jest unikalna
    validate_unique_update_record_by_ids(db_controller, 1, 2, 1)

    # Niepoprawny przypadek - kombinacja już istnieje
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i service_id=1 już istnieje."):
        validate_unique_update_record_by_ids(db_controller, 2, 1, 1)


# +-+-+-+- metody walidacji dodawania rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 


def test_validate_add_employee_service_by_ids(setup_controllers):
    """
    Testuje walidację dodawania rekordu na podstawie `employee_id` i `service_id`.
    """
    db_controller, employees_controller, services_controller = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    services_controller.add_service("Diagnoza", 60, 150)

    # Poprawne wywołanie walidacji
    validate_add_employee_service_by_ids(
        db_controller=db_controller,
        employees_controller=employees_controller,
        services_controller=services_controller,
        employee_id=1,
        service_id=1
    )

    # Przypadek niepoprawny: Nieistniejący `employee_id`
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        validate_add_employee_service_by_ids(
            db_controller=db_controller,
            employees_controller=employees_controller,
            services_controller=services_controller,
            employee_id=99,
            service_id=1
        )

    # Przypadek niepoprawny: Nieistniejący `service_id`
    with pytest.raises(ValueError, match="Usługa o ID 99 nie istnieje."):
        validate_add_employee_service_by_ids(
            db_controller=db_controller,
            employees_controller=employees_controller,
            services_controller=services_controller,
            employee_id=1,
            service_id=99
        )



def test_validate_add_employee_specialty_by_names(setup_controllers):
    """
    Testuje walidację dla metody `validate_add_employee_specialty_by_names`.
    Sprawdza, czy imię, nazwisko i nazwa usługi są poprawne oraz istnieją w bazie danych.
    """
    _, employees_controller, services_controller = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    services_controller.add_service("Diagnoza", 60, 150)

    # Poprawne dane
    validate_add_employee_specialty_by_names(employees_controller, services_controller, "Jan", "Kowalski", "Diagnoza")

    # Niepoprawne imię lub nazwisko
    with pytest.raises(ValueError, match="Imię musi być ciągiem znaków."):
        validate_add_employee_specialty_by_names(employees_controller, services_controller, 123, "Kowalski", "Diagnoza")
    with pytest.raises(ValueError, match="Nazwisko musi być ciągiem znaków."):
        validate_add_employee_specialty_by_names(employees_controller, services_controller, "Jan", 456, "Diagnoza")

    # Niepoprawna nazwa usługi
    with pytest.raises(ValueError, match="Nazwa usługi zawiera niedozwolone znaki."):
        validate_add_employee_specialty_by_names(employees_controller, services_controller, "Jan", "Kowalski", "Diagnoza!")
    with pytest.raises(ValueError, match="Nazwa usługi musi mieć od 3 do 100 znaków."):
        validate_add_employee_specialty_by_names(employees_controller, services_controller, "Jan", "Kowalski", "Di")

    # Usługa nie istnieje
    with pytest.raises(ValueError, match="Usługa 'Nieistniejąca usługa' nie istnieje."):
        validate_add_employee_specialty_by_names(employees_controller, services_controller, "Jan", "Kowalski", "Nieistniejąca usługa")

    # Pracownik nie istnieje
    with pytest.raises(ValueError, match="Pracownik Jan Nowak nie istnieje."):
        validate_add_employee_specialty_by_names(employees_controller, services_controller, "Jan", "Nowak", "Diagnoza")




    # +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_validate_update_record_by_names():
    """Testuje walidację aktualizacji rekordu na podstawie imienia, nazwiska i nazwy usługi."""
    # Poprawne dane
    validate_update_record_by_names("Jan", "Kowalski", "Diagnoza i leczenie zaburzeń psychicznych")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Imię musi być ciągiem znaków."):
        validate_update_record_by_names(123, "Kowalski", "Diagnoza i leczenie zaburzeń psychicznych")
    with pytest.raises(ValueError, match="Nazwa usługi zawiera niedozwolone znaki."):
        validate_update_record_by_names("Jan", "Kowalski", "Terapia!")



    # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



def test_validate_delete_record_by_id(setup_controllers):
    """Testuje walidację usuwania rekordu na podstawie `employee_service_id`."""
    db_controller, employees_controller, services_controller = setup_controllers    

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    services_controller.add_service("Diagnoza i leczenie", 60, 150)
    db_controller.connection.execute("INSERT INTO employee_services (employee_id, service_id) VALUES (?, ?)", (1, 1))

    # Poprawny przypadek
    validate_delete_record_by_id(db_controller, 1)

    # Niepoprawny przypadek
    with pytest.raises(ValueError, match="Rekord o ID 99 nie istnieje w tabeli `employee_services`."):
        validate_delete_record_by_id(db_controller, 99)


def test_validate_delete_records_by_names(setup_controllers):
    """Testuje walidację usuwania rekordów na podstawie imienia, nazwiska i nazwy usługi."""
    _, employees_controller, services_controller = setup_controllers

    # Dodanie danych testowych
    employees_controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychiatra", 1)
    services_controller.add_service("Diagnoza i leczenie", 60, 150)

    # Poprawny przypadek
    validate_delete_records_by_names(employees_controller, services_controller, "Jan", "Kowalski", "Diagnoza i leczenie")

    # Niepoprawny przypadek
    with pytest.raises(ValueError, match="Pracownik Jan Nowak nie istnieje."):
        validate_delete_records_by_names(employees_controller, services_controller, "Jan", "Nowak", "Diagnoza i leczenie")


# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



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
    valid_columns = ["employee_service_id", "employee_id", "service_id"]

    # Poprawne dane
    validate_filters_and_sorting(
        filters=[{"column": "employee_id", "operator": "=", "value": 1}],
        sort_by=None,
        valid_columns=valid_columns,
    )

    # Niepoprawne dane - brak klucza "operator"
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters=[{"column": "employee_id"}], sort_by=None, valid_columns=valid_columns)

