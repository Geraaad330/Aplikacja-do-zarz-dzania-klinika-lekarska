# test_model_patients.py
# Testy dla modelu Patients przy użyciu pytest i bazy danych SQLite w pamięci.

import os
import pytest
from controllers.database_controller import DatabaseController
from models.patients import Patients

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """Konfiguracja testowej bazy danych"""
    db_controller = DatabaseController()
    db_controller.connect_to_database()
    patients = Patients(db_controller)
    patients.create_table()
    yield patients
    db_controller.close_connection()


def test_create_table(setup_database):
    """
    Test sprawdzający, czy tabela została utworzona.
    """
    patients = setup_database
    result = patients.db_controller.connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='patients';"
    )
    assert result.fetchone() is not None

def test_add_patient_valid_data(setup_database):
    """
    Test dodawania pacjenta z poprawnymi danymi.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )
    result = patients.get_all_patients()
    assert len(result) == 1
    assert result[0]["first_name"] == "Jan"

def test_add_patient_invalid_pesel(setup_database):
    """
    Test dodawania pacjenta z nieprawidłowym PESEL.
    """
    patients = setup_database
    with pytest.raises(ValueError, match="Numer PESEL powinien zawierać dokładnie 11 cyfr"):
        patients.add_patient(
            first_name="Jan",
            last_name="Kowalski",
            pesel="123",  # Nieprawidłowy PESEL
            phone="123456789",
            email="jan.kowalski@example.com",
            address="Warszawa, ul. Przykładowa 1",
            date_of_birth="01.01.1990"
        )

def test_update_patient_invalid_email(setup_database):
    """
    Test aktualizacji pacjenta z nieprawidłowym adresem email.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Anna",
        last_name="Nowak",
        pesel="98765432109",
        phone="987654321",
        email="anna.nowak@example.com",
        address="Kraków, ul. Testowa 2",
        date_of_birth="1980-02-02"
    )
    with pytest.raises(ValueError, match="Adres email jest nieprawidłowy"):
        patients.update_patient(1, email="invalid-email")  # Nieprawidłowy email

def test_delete_nonexistent_patient(setup_database):
    """
    Test usuwania pacjenta, który nie istnieje.
    """
    patients = setup_database
    deleted_count = patients.delete_patient(1)  # Pacjent o ID=1 nie istnieje
    assert deleted_count == 0

def test_get_patient_nonexistent(setup_database):
    """
    Test pobierania pacjenta, który nie istnieje.
    """
    patients = setup_database
    patient = patients.get_patient(1)  # Pacjent o ID=1 nie istnieje
    assert patient is None

def test_get_all_patients(setup_database):
    """
    Test pobierania wszystkich pacjentów.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Karol",
        last_name="Lewandowski",
        pesel="12345678901",
        phone="444555666",
        email="karol.l@example.com",
        address="Katowice, ul. Średnia 8",
        date_of_birth="1990-07-07"
    )
    patients.add_patient(
        first_name="Agnieszka",
        last_name="Nowakowska",
        pesel="78901234567",
        phone="777888999",
        email="agnieszka.n@example.com",
        address="Lublin, ul. Duża 9",
        date_of_birth="1988-08-08"
    )
    result = patients.get_all_patients()
    assert len(result) == 2

def test_add_duplicate_pesel(setup_database):
    """
    Test dodawania pacjenta z istniejącym już numerem PESEL.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )
    with pytest.raises(ValueError, match="Numer PESEL musi być unikalny"):
        patients.add_patient(
            first_name="Anna",
            last_name="Nowak",
            pesel="12345678901",  # Duplikat PESEL
            phone="987654321",
            email="anna.nowak@example.com",
            address="Kraków, ul. Testowa 2",
            date_of_birth="1985-05-15"
        )


def test_filter_patients_by_pesel(setup_database):
    """
    Test filtrowania pacjentów na podstawie numeru PESEL.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )
    result = patients.filter_patients_by_pesel("12345678901")
    assert len(result) == 1
    assert result[0]["pesel"] == "12345678901"


def test_search_patients(setup_database):
    """
    Test wyszukiwania pacjentów na podstawie imienia i nazwiska.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )
    result = patients.search_patients(first_name="Jan", last_name="Kowalski")
    assert len(result) == 1
    assert result[0]["first_name"] == "Jan"
    assert result[0]["last_name"] == "Kowalski"

def test_advanced_filter_patients(setup_database):
    """
    Test zaawansowanego filtrowania pacjentów na podstawie wielu kryteriów.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )
    patients.add_patient(
        first_name="Anna",
        last_name="Nowak",
        pesel="98765432109",
        phone="987654321",
        email="anna.nowak@example.com",
        address="Kraków, ul. Testowa 2",
        date_of_birth="1985-05-15"
    )
    result = patients.advanced_filter_patients(first_name="Anna", address="Kraków")
    assert len(result) == 1
    assert result[0]["first_name"] == "Anna"
    assert "Kraków" in result[0]["address"]

def test_safe_execute_with_error(setup_database):
    """
    Test działania safe_execute przy błędnym zapytaniu SQL.
    """
    patients = setup_database
    with pytest.raises(RuntimeError, match="Zapytanie nie powiodło się"):
        patients.safe_execute("INSERT INTO non_existing_table VALUES (?)", ("Test",))

def test_update_patient_address(setup_database):
    """
    Test aktualizacji adresu pacjenta.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )
    updated_rows = patients.update_patient(1, address="Nowy adres 123")
    assert updated_rows == 1
    patient = patients.get_patient(1)
    assert patient["address"] == "Nowy adres 123"

def test_advanced_filter_patients_invalid_key(setup_database):
    """
    Test zaawansowanego filtrowania pacjentów z nieobsługiwanym kryterium.
    """
    patients = setup_database
    patients.add_patient(
        first_name="Jan",
        last_name="Kowalski",
        pesel="12345678901",
        phone="123456789",
        email="jan.kowalski@example.com",
        address="Warszawa, ul. Przykładowa 1",
        date_of_birth="1990-01-01"
    )

    # Próba filtrowania za pomocą nieobsługiwanego kryterium
    with pytest.raises(ValueError, match="Nieobsługiwane kryterium filtrowania: invalid_key"):
        patients.advanced_filter_patients(invalid_key="test")
