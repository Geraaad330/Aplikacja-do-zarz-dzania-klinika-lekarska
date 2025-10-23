# test_integration_employee_specialties.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.employee_specialties_controller import EmployeeSpecialtiesController
from controllers.employees_controller import EmployeesController
from controllers.specialties_controller import SpecialtiesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu EmployeeSpecialties.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "employees": EmployeesController(db_controller),
        "specialties": SpecialtiesController(db_controller),
        "employee_specialties": EmployeeSpecialtiesController(db_controller)
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    with db_controller.connection:
        db_controller.connection.execute("DELETE FROM employees")
        db_controller.connection.execute("DELETE FROM specialties")
        db_controller.connection.execute("DELETE FROM employee_specialties")




# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_add_employee_specialty_id_valid_data(setup_controllers):
    """
    Testuje dodawanie nowego rekordu z poprawnymi danymi.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych do tabel zależnych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")

    # Dodanie rekordu do tabeli `employee_specialties`
    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Walidacja wyniku
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1


def test_add_employee_specialty_id_invalid_data(setup_controllers):
    """
    Testuje dodawanie nowego rekordu z niepoprawnymi danymi.
    """
    # Tworzenie tabel

    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Próba dodania rekordu z nieistniejącymi ID
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        employee_specialties_controller.add_employee_specialty(employee_id=99, specialty_id=1)



def test_add_employee_specialty_by_names_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie specjalizacji dla pracownika na podstawie ich imienia, nazwiska i nazwy specjalizacji.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych do tabeli employees
    employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Psychiatra",
        is_medical_staff=1
    )

    # Dodanie danych do tabeli specialties
    specialties_controller.add_specialty("Kardiologia")

    # Dodanie danych do tabeli employee_specialties
    employee_specialties_controller.add_employee_specialty_by_names(
        first_name="Jan",
        last_name="Kowalski",
        specialty_name="Kardiologia"
    )

    # Weryfikacja
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1


def test_add_employee_specialty_by_names_invalid_employee(setup_controllers):
    """
    Testuje dodanie specjalizacji dla nieistniejącego pracownika.
    """
    
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych do tabeli specialties
    specialties_controller.add_specialty("Kardiologia")

    # Próba dodania specjalizacji dla nieistniejącego pracownika
    with pytest.raises(KeyError, match="Pracownik .* nie istnieje."):
        employee_specialties_controller.add_employee_specialty_by_names(
            first_name="Adam",
            last_name="Nowak",
            specialty_name="Kardiologia"
        )



def test_add_employee_specialty_by_names_invalid_specialty(setup_controllers):
    """
    Testuje dodanie specjalizacji, która nie istnieje w bazie danych.
    """
    
    employees_controller = setup_controllers["employees"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych do tabeli employees
    employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Psychiatra",
        is_medical_staff=1
    )

    # Próba dodania nieistniejącej specjalizacji
    with pytest.raises(ValueError, match="Specjalizacja .* nie istnieje."):
        employee_specialties_controller.add_employee_specialty_by_names(
            first_name="Jan",
            last_name="Kowalski",
            specialty_name="Neurologia"
        )


def test_add_employee_specialty_by_names_duplicate_data(setup_controllers):
    """
    Testuje dodanie duplikatu specjalizacji dla tego samego pracownika.
    """
    
    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych do tabeli employees
    employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Psychiatra",
        is_medical_staff=1
    )

    # Dodanie danych do tabeli specialties
    specialties_controller.add_specialty("Kardiologia")

    # Dodanie danych do tabeli employee_specialties
    employee_specialties_controller.add_employee_specialty_by_names(
        first_name="Jan",
        last_name="Kowalski",
        specialty_name="Kardiologia"
    )

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Błąd walidacji: Kombinacja employee_id=1 i specialty_id=1 już istnieje."):
        employee_specialties_controller.add_employee_specialty_by_names(
            first_name="Jan",
            last_name="Kowalski",
            specialty_name="Kardiologia"
        )

 # +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_get_records_valid_data(setup_controllers):
    """
    Testuje pobieranie rekordów z tabeli `employee_specialties` przy użyciu poprawnych danych.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Pobranie rekordów bez filtrów
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 1, "Nieprawidłowa liczba rekordów."
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1


def test_get_records_with_filters(setup_controllers):
    """
    Testuje pobieranie rekordów z tabeli `employee_specialties` z filtrami.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Pobranie rekordów z filtrami
    filters = [{"column": "employee_id", "operator": "=", "value": 1}]
    records = employee_specialties_controller.get_all_records(filters=filters)
    assert len(records) == 1, "Nieprawidłowa liczba rekordów po zastosowaniu filtrów."
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1


def test_get_records_with_invalid_filters(setup_controllers):
    """
    Testuje pobieranie rekordów z tabeli `employee_specialties` z niepoprawnymi filtrami.
    """
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Próba użycia niepoprawnych filtrów
    invalid_filters = [{"column": "invalid_column", "operator": "=", "value": 1}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column"):
        employee_specialties_controller.get_records_with_names(filters=invalid_filters)


def test_get_records_with_names_valid_data(setup_controllers):
    """
    Testuje pobieranie rekordów z tabeli `employee_specialties` z nazwami pracowników i specjalizacji.
    """
    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Pobranie rekordów z nazwami
    records = employee_specialties_controller.get_records_with_names()
    assert len(records) == 1
    assert records[0]["first_name"] == "Jan"
    assert records[0]["last_name"] == "Kowalski"
    assert records[0]["specialty_name"] == "Kardiologia"



def test_get_records_with_names_invalid_filters(setup_controllers):
    """
    Testuje pobieranie rekordów z tabeli `employee_specialties` z nazwami z niepoprawnymi filtrami.
    """

    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Próba użycia niepoprawnych filtrów
    invalid_filters = [{"column": "invalid_column", "operator": "=", "value": "value"}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column"):
        employee_specialties_controller.get_records_with_names(filters=invalid_filters)


def test_get_records_with_empty_table(setup_controllers):
    """
    Testuje pobieranie rekordów z pustej tabeli.
    """

    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Pobranie rekordów z pustej tabeli
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 0, "Tabela `employee_specialties` powinna być pusta."



# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_update_record_by_id_valid_data(setup_controllers):
    """
    Testuje poprawną aktualizację rekordu w tabeli `employee_specialties` na podstawie `employee_specialty_id`.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    specialties_controller.add_specialty("Neurologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Aktualizacja rekordu
    employee_specialties_controller.update_record_by_id(
        employee_specialty_id=1, new_employee_id=1, new_specialty_id=2
    )

    # Walidacja wyniku
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 1
    assert records[0]["specialty_id"] == 2


def test_update_record_by_id_invalid_data(setup_controllers):
    """
    Testuje niepoprawną aktualizację rekordu w tabeli `employee_specialties` na podstawie `employee_specialty_id`.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Próba aktualizacji rekordu z nieistniejącym `specialty_id`
    with pytest.raises(ValueError, match="Specjalizacja o ID 99 nie istnieje."):
        employee_specialties_controller.update_record_by_id(
            employee_specialty_id=1, new_employee_id=1, new_specialty_id=99
        )


def test_update_record_by_name_using_names_valid_data(setup_controllers):
    """
    Testuje poprawną aktualizację rekordu w tabeli `employee_specialties` na podstawie nazw.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    employees_controller.add_employee(
        first_name="Maria", last_name="Nowak", email="maria.nowak@example.com",
        phone="987654321", profession="Psycholog kliniczny", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    specialties_controller.add_specialty("Neurologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Aktualizacja rekordu
    employee_specialties_controller.update_record_by_name(
        first_name="Jan",
        last_name="Kowalski",
        specialty_name="Kardiologia",
        new_first_name="Maria",
        new_last_name="Nowak",
        new_specialty_name="Neurologia"

    )

    # Pobranie zaktualizowanego rekordu i weryfikacja
    updated_record = employee_specialties_controller.get_all_records(filters=[
        {"column": "first_name", "operator": "=", "value": "Maria"},
        {"column": "last_name", "operator": "=", "value": "Nowak"},
        {"column": "specialty_name", "operator": "=", "value": "Neurologia"}
    ])
    assert len(updated_record) == 1


def test_update_record_by_name_using_names_invalid_data(setup_controllers):
    """
    Testuje niepoprawną aktualizację rekordu w tabeli `employee_specialties` na podstawie nazw.
    """
    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Próba aktualizacji rekordu z nieistniejącymi nazwami
    with pytest.raises(KeyError, match="Nie znaleziono rekordu: .*"):
        employee_specialties_controller.update_record_by_name(
            first_name="Adam",
            last_name="Nowak",
            specialty_name="Neurologia",
            new_first_name="Jan",
            new_last_name="Kowalski",
            new_specialty_name="Kardiologia"
        )





def test_update_record_by_name_using_id_valid_data(setup_controllers):
    """
    Testuje poprawną aktualizację rekordu w tabeli `employee_specialties` na podstawie nazw.
    """
    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych za pomocą kontrolera
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    specialties_controller.add_specialty("Neurologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Aktualizacja rekordu za pomocą kontrolera
    employee_specialties_controller.update_record_by_name(
        first_name="Jan",
        last_name="Kowalski",
        specialty_name="Kardiologia",
        new_specialty_name="Neurologia"
    )

    # Weryfikacja aktualizacji za pomocą kontrolera
    records = employee_specialties_controller.get_records_with_names(
        filters=[{"column": "specialty_name", "operator": "=", "value": "Neurologia"}]
    )
    assert len(records) == 1
    assert records[0]["first_name"] == "Jan"
    assert records[0]["last_name"] == "Kowalski"







 # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_delete_employee_specialty_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu w tabeli `employee_specialties` za pomocą `employee_specialty_id`.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Usuwanie rekordu
    employee_specialties_controller.delete_employee_specialty(employee_specialty_id=1)

    # Walidacja usunięcia
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 0, "Rekord nie został usunięty."


def test_delete_record_by_name_invalid_data(setup_controllers):
    """
    Testuje niepoprawne usunięcie rekordu w tabeli `employee_specialties` na podstawie nazw.
    """
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie specjalizacji za pomocą kontrolera
    specialties_controller.add_specialty("Kardiologia")

    # Próba usunięcia rekordu z nieistniejącymi nazwami
    with pytest.raises(KeyError, match="Nie znaleziono rekordu: .*"):
        employee_specialties_controller.delete_record_by_name(
            first_name="Adam",
            last_name="Nowak",
            specialty_name="Kardiologia"
        )



def test_delete_record_by_name_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu w tabeli `employee_specialties` za pomocą nazw pracownika i specjalizacji.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Dodanie danych testowych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")

    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Usuwanie rekordu
    employee_specialties_controller.delete_record_by_name(
        first_name="Jan", last_name="Kowalski", specialty_name="Kardiologia"
    )

    # Walidacja usunięcia
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 0, "Rekord nie został usunięty."




 # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_database_disconnection_handling_form_types(setup_controllers):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia w tabeli `employee_specialties`.
    """
    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Rozłączenie bazy danych
    employee_specialties_controller.db_controller.close_connection()

    # Próba dodania danych po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        employee_specialties_controller.add_employee_specialty_by_names(
            first_name="Jan", last_name="Kowalski", specialty_name="Kardiologia"
        )

    # Próba pobrania danych po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        employee_specialties_controller.get_all_records()

    # Przywrócenie połączenia
    employee_specialties_controller.db_controller.connect_to_database()
    for controller in setup_controllers.values():
        controller.create_table()

    # Dodanie danych po przywróceniu połączenia
    employees_controller.add_employee(
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        profession="Psychiatra",
        is_medical_staff=1,
    )
    specialties_controller.add_specialty("Kardiologia")
    employee_specialties_controller.add_employee_specialty_by_names(
        first_name="Jan", last_name="Kowalski", specialty_name="Kardiologia"
    )

    # Pobranie danych po przywróceniu połączenia
    records = employee_specialties_controller.get_records_with_names(
        filters=[{"column": "first_name", "operator": "LIKE", "value": "Jan%"}]
    )
    assert len(records) == 1
    assert records[0]["first_name"] == "Jan"






def test_full_crud_flow(setup_controllers):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """

    employees_controller = setup_controllers["employees"]
    specialties_controller = setup_controllers["specialties"]
    employee_specialties_controller = setup_controllers["employee_specialties"]

    # Tworzenie tabel


    # Dodanie danych
    employees_controller.add_employee(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com",
        phone="123456789", profession="Psychiatra", is_medical_staff=1
    )
    specialties_controller.add_specialty("Kardiologia")
    specialties_controller.add_specialty("Neurologia")

    # Dodanie rekordu
    employee_specialties_controller.add_employee_specialty(employee_id=1, specialty_id=1)

    # Pobranie danych
    records = employee_specialties_controller.get_all_records()
    assert len(records) == 1

    # Aktualizacja danych
    employee_specialties_controller.update_record_by_id(employee_specialty_id=1, new_specialty_id=2)

    # Usunięcie danych
    employee_specialties_controller.delete_employee_specialty(employee_specialty_id=1)
    remaining = employee_specialties_controller.get_all_records()
    assert len(remaining) == 0, "Dane nie zostały usunięte z tabeli."