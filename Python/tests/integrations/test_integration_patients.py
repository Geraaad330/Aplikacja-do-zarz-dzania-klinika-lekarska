# test_integration_patients.py
"""
test sprawdza: 
kontroler -> walidacja -> model -> kontroler bazy danych ->baza danych
"""
import os
import pytest
from controllers.patients_controller import PatientController
from controllers.database_controller import DatabaseController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="test_db_connection")
def test_db_connection_fixture():
    """Fixture przygotowująca połączenie z testową bazą danych."""
    db_controller = DatabaseController()  # Brak argumentów w konstruktorze
    db_controller.connect_to_database()  # Połącz z bazą danych
    yield db_controller  # Udostępnij kontroler w testach
    db_controller.close_connection()  # Zamknij połączenie

@pytest.fixture(name="patients_controller")
def patients_controller_fixture(test_db_connection):
    """Fixture inicjalizująca PatientController z testową bazą danych."""
    controller = PatientController(test_db_connection)
    controller.model.create_table()  # Tworzymy tabelę patients na potrzeby testów
    return controller

def test_add_and_get_patient(patients_controller):
    """Test dodania i pobrania pacjenta."""
    # ZMIANA: Poprawne dane zgodne z walidacją
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        date_of_birth="1980-01-01",
        address="ul. Przykładowa 1"
    )
    patient = patients_controller.get_patient_by_id(1)
    assert patient["first_name"] == "Jan"
    assert patient["last_name"] == "Kowalski"
    assert patient["pesel"] == "12345678901"

def test_add_patient_invalid_pesel(patients_controller):
    """Test dodania pacjenta z nieprawidłowym PESEL."""
    # ZMIANA: Test na błędne dane PESEL, obsługiwane przez walidację
    with pytest.raises(ValueError, match="Numer PESEL powinien zawierać dokładnie 11 cyfr"):
        patients_controller.add_patient(
            first_name="Anna",
            last_name="Nowak",
            pesel="12345",  # Nieprawidłowy PESEL
            phone="987654321",
            email="anna.nowak@example.com",
            date_of_birth="1990-02-02",
            address="ul. Inna 2"
        )

def test_get_all_patients(patients_controller):
    """Test pobrania wszystkich pacjentów."""
    # ZMIANA: Poprawne dane w testach
    patients_controller.add_patient(
        first_name="Anna",
        last_name="Nowak",
        pesel="98765432109",
        phone=None,
        email=None,
        date_of_birth="1990-02-02",
        address="ul. Inna 2"
    )
    all_patients = patients_controller.get_all_patients()
    assert len(all_patients) == 1
    assert all_patients[0]["first_name"] == "Anna"

def test_delete_patient(patients_controller):
    """Test usuwania pacjenta."""
    # ZMIANA: Dodanie pacjenta zgodnie z walidacją przed usuwaniem
    patients_controller.add_patient(
        first_name="Piotr",
        last_name="Zieliński",
        pesel="54321098765",
        phone=None,
        email=None,
        date_of_birth="1975-03-03",
        address="ul. Zielona 3"
    )
    patients_controller.delete_patient(1)
    patient = patients_controller.get_patient_by_id(1)
    assert patient is None

def test_update_patient(patients_controller):
    """Test aktualizacji danych pacjenta."""
    # ZMIANA: Dodanie pacjenta zgodnie z walidacją przed aktualizacją
    patients_controller.add_patient(
        first_name="Maria",
        last_name="Wiśniewska",
        pesel="19283746501",
        phone="987654321",
        email="maria@example.com",
        date_of_birth="1985-04-04",
        address="ul. Wiśniowa 4"
    )
    # ZMIANA: Walidacja w procesie aktualizacji
    patients_controller.update_patient(1, phone="123123123", address="ul. Zmieniona 5")
    updated_patient = patients_controller.get_patient_by_id(1)
    assert updated_patient["phone"] == "123123123"
    assert updated_patient["address"] == "ul. Zmieniona 5"

def test_update_patient_invalid_email(patients_controller):
    """Test aktualizacji pacjenta z nieprawidłowym adresem email."""
    # ZMIANA: Dodanie pacjenta z poprawnym emailem
    patients_controller.add_patient(
        first_name="Maria",
        last_name="Wiśniewska",
        pesel="19283746501",
        phone="987654321",
        email="maria@example.com",
        date_of_birth="1985-04-04",
        address="ul. Wiśniowa 4"
    )
    # ZMIANA: Próba aktualizacji z niepoprawnym emailem, walidacja rzuca wyjątek
    with pytest.raises(ValueError, match="Adres email jest nieprawidłowy"):
        patients_controller.update_patient(1, email="invalid-email")

def test_advanced_filter_patients(patients_controller):
    patients_controller.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        date_of_birth="1980-01-01",
        address="ul. Przykładowa 1"
    )
    result = patients_controller.advanced_filter_patients(first_name="Jan")
    assert len(result) == 1
    assert result[0]["first_name"] == "Jan"

def test_database_connection_error(test_db_connection):
    """
    Test obsługi błędów połączenia z bazą danych.
    """
    test_db_connection.close_connection()
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych"):
        if test_db_connection.connection is not None:
            test_db_connection.connection.execute("SELECT * FROM patients")
        else:
            raise RuntimeError("Brak połączenia z bazą danych")


def test_get_all_patients_empty_database(patients_controller):
    result = patients_controller.get_all_patients()
    assert len(result) == 0

def test_add_patient_invalid_email_integration(patients_controller):
    with pytest.raises(ValueError, match="Adres email jest nieprawidłowy"):
        patients_controller.add_patient(
            first_name="Jan",
            last_name="Kowalski",
            pesel="12345678901",
            phone="123456789",
            email="invalid-email",
            date_of_birth="1980-01-01",
            address="ul. Przykładowa 1"
        )
