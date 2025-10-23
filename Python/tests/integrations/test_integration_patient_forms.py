# test_integration_patient_forms.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.patient_forms_controller import PatientFormsController
from controllers.patients_controller import PatientController
from controllers.form_types_controller import FormTypesController


# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Fixture konfigurujący testową bazę danych SQLite3.
    Tworzy wymagane tabele i zapewnia czyste środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "db_controller": db_controller,
        "patient_forms": PatientFormsController(db_controller),
        "patients": PatientController(db_controller),
        "form_types": FormTypesController(db_controller),
    }

    # Tworzenie tabel
    for controller in controllers.values():
        if hasattr(controller, "create_table"):
            controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM patient_forms")
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM form_types")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_add_form_with_valid_data(setup_controllers):
    """
    Testuje poprawne dodanie formularza z poprawnymi danymi.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Jan", last_name="Kowalski", pesel="12345678901",
        phone="123456789", email="jan.kowalski@example.com", address="Warszawa",
        date_of_birth="1980-01-01"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Zgoda na leczenie")

    # Dodanie formularza
    patient_form_id = patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-01-13",
        content="Treść formularza"
    )

    # Weryfikacja dodania formularza
    forms = patient_forms.get_forms(
        filters=[{"column": "patient_form_id", "operator": "=", "value": patient_form_id}]
    )
    assert len(forms) == 1, "Formularz nie został poprawnie dodany."
    assert forms[0]["patient_form_id"] == patient_form_id


def test_add_form_with_missing_data(setup_controllers):
    """
    Testuje próbę dodania formularza z brakującymi danymi.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba dodania formularza bez wymaganych danych
    with pytest.raises(ValueError, match="Pole `fk_patient_id` nie może być null."):
        patient_forms.add_form(
            fk_patient_id=None,
            fk_form_type_id=1,
            submission_date="2025-01-13",
            content="Brakujące dane"
        )


def test_add_form_with_invalid_data(setup_controllers):
    """
    Testuje próbę dodania formularza z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba dodania formularza z nieprawidłową datą
    with pytest.raises(ValueError, match="Nieprawidłowy format daty zgłoszenia: .*"):
        patient_forms.add_form(
            fk_patient_id=1,
            fk_form_type_id=1,
            submission_date="13-01-2025",  # Nieprawidłowy format daty
            content="Nieprawidłowe dane"
        )


def test_add_form_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania formularza do pustej bazy.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba dodania formularza bez danych referencyjnych
    with pytest.raises(ValueError, match="Pacjent o ID .* nie istnieje."):
        patient_forms.add_form(
            fk_patient_id=999,  # Nieistniejący pacjent
            fk_form_type_id=1,  # Nieistniejący typ formularza
            submission_date="2025-01-13",
            content="Brakujące dane referencyjne"
        )


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_update_form_with_valid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Anna", last_name="Nowak", pesel="98765432109",
        phone="987654321", email="anna.nowak@example.com", address="Kraków",
        date_of_birth="1990-05-10"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Plan leczenia")

    # Dodanie formularza
    patient_form_id = patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-02-01",
        content="Pierwsza treść formularza"
    )

    # Aktualizacja formularza
    updates = {
        "fk_patient_id": patient_id,
        "fk_form_type_id": form_type_id,
        "submission_date": "2025-03-01",
        "content": "Zaktualizowana treść"
    }
    patient_forms.update_form(patient_form_id, updates)

    # Weryfikacja aktualizacji
    updated_form = patient_forms.get_forms(
        filters=[{"column": "patient_form_id", "operator": "=", "value": patient_form_id}]
    )[0]
    assert updated_form["submission_date"] == "2025-03-01"
    assert updated_form["content"] == "Zaktualizowana treść"


def test_update_form_with_invalid_data(setup_controllers):
    """
    Testuje aktualizację rekordu z nieprawidłowymi danymi.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Krzysztof", last_name="Lis", pesel="11223344556",
        phone="123123123", email="krzysztof.lis@example.com", address="Łódź",
        date_of_birth="1985-03-15"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Zgoda na zabieg")

    # Dodanie formularza
    patient_form_id = patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-04-01",
        content="Treść do aktualizacji"
    )

    # Próba aktualizacji z nieprawidłową datą
    updates = {
        "submission_date": "01-04-2025"  # Nieprawidłowy format daty
    }
    with pytest.raises(ValueError, match="Nieprawidłowy format daty zgłoszenia: .*"):
        patient_forms.update_form(patient_form_id, updates)


def test_update_nonexistent_form(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba aktualizacji rekordu, który nie istnieje
    updates = {
        "submission_date": "2025-05-01",
        "content": "Nieistniejący rekord"
    }
    with pytest.raises(RuntimeError, match="Formularz o ID .* nie istnieje."):
        patient_forms.update_form(999, updates)  # Nieistniejące ID


def test_update_form_with_missing_data(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez danych i z brakującymi danymi.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Michał", last_name="Kowal", pesel="55443322119",
        phone="555666777", email="michal.kowal@example.com", address="Poznań",
        date_of_birth="1992-08-22"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Dokumentacja medyczna")

    # Dodanie formularza
    patient_form_id = patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-06-01",
        content="Treść do brakującej aktualizacji"
    )

    # Próba aktualizacji bez danych
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        patient_forms.update_form(patient_form_id, {})


# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_get_nonexistent_form(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba pobrania rekordu o ID, który nie istnieje
    forms = patient_forms.get_forms(filters=[{"column": "patient_form_id", "operator": "=", "value": 999}])
    assert len(forms) == 0, "Nieistniejący rekord został znaleziony."


def test_get_all_forms(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy danych.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Jan", last_name="Nowak", pesel="12345678901",
        phone="123456789", email="jan.nowak@example.com", address="Warszawa",
        date_of_birth="1980-01-01"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Plan leczenia")

    # Dodanie formularzy
    patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-01-01",
        content="Formularz 1"
    )
    patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-01-02",
        content="Formularz 2"
    )

    # Pobranie wszystkich rekordów
    all_forms = patient_forms.get_forms()
    assert len(all_forms) == 2, "Nieprawidłowa liczba rekordów w bazie."


def test_get_forms_from_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy danych.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Pobranie wszystkich rekordów z pustej bazy
    forms = patient_forms.get_forms()
    assert len(forms) == 0, "Pusta baza danych zawiera rekordy."


def test_get_forms_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id_1 = patients.add_patient(
        first_name="Anna", last_name="Kowalska", pesel="98765432101",
        phone="987654321", email="anna.kowalska@example.com", address="Kraków",
        date_of_birth="1990-02-01"
    )["patient_id"]

    patient_id_2 = patients.add_patient(
        first_name="Piotr", last_name="Wiśniewski", pesel="12312312345",
        phone="123123123", email="piotr.wisniewski@example.com", address="Gdańsk",
        date_of_birth="1985-07-07"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Dokumentacja")

    # Dodanie formularzy
    form_1 = patient_forms.add_form(
        fk_patient_id=patient_id_1,
        fk_form_type_id=form_type_id,
        submission_date="2025-03-01",
        content="Formularz dla Anny"
    )
    form_2 = patient_forms.add_form(
        fk_patient_id=patient_id_2,
        fk_form_type_id=form_type_id,
        submission_date="2025-03-02",
        content="Formularz dla Piotra"
    )

    # Pobranie formularza dla Anny
    forms = patient_forms.get_forms(filters=[{"column": "fk_patient_id", "operator": "=", "value": patient_id_1}])
    assert len(forms) == 1, "Nie znaleziono formularza dla pacjenta Anna."
    assert forms[0]["patient_form_id"] == form_1

    # Pobranie formularza z określoną datą
    forms = patient_forms.get_forms(filters=[{"column": "submission_date", "operator": "=", "value": "2025-03-02"}])
    assert len(forms) == 1, "Nie znaleziono formularza z określoną datą."
    assert forms[0]["patient_form_id"] == form_2



# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_delete_form_with_valid_data(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu z poprawnymi danymi.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Dodanie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Adam", last_name="Nowak", pesel="12345678901",
        phone="123456789", email="adam.nowak@example.com", address="Warszawa",
        date_of_birth="1990-01-01"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Plan leczenia")

    # Dodanie formularza
    patient_form_id = patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-01-01",
        content="Treść formularza do usunięcia"
    )

    # Usunięcie formularza
    patient_forms.delete_form(patient_form_id)

    # Weryfikacja usunięcia
    forms = patient_forms.get_forms(filters=[{"column": "patient_form_id", "operator": "=", "value": patient_form_id}])
    assert len(forms) == 0, f"Dane nie zostały usunięte z metody delete_form: {patient_form_id}"


def test_delete_form_with_invalid_data(setup_controllers):
    """
    Testuje próbę usunięcia rekordu korzystając z nieprawidłowych danych.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba usunięcia rekordu z nieprawidłowym ID
    with pytest.raises(ValueError, match="Nieprawidłowe ID formularza: .*"):
        patient_forms.delete_form("invalid_id")  # Nieprawidłowy typ ID



def test_delete_nonexistent_form(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Próba usunięcia rekordu, który nie istnieje
    with pytest.raises(RuntimeError, match="Formularz o ID .* nie istnieje."):
        patient_forms.delete_form(999)  # Nieistniejący ID


# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_database_connection_error(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    controllers = setup_controllers
    patient_forms = controllers["patient_forms"]

    # Zamknięcie połączenia z bazą danych
    controllers["db_controller"].close_connection()

    # Próba wykonania operacji na zamkniętej bazie danych
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        patient_forms.get_forms()


def test_full_crud_flow(setup_controllers):
    """
    Testuje pełen przepływ danych (CRUD) między kontrolerem, walidacją, modelem i bazą danych.
    """
    controllers = setup_controllers
    patients = controllers["patients"]
    form_types = controllers["form_types"]
    patient_forms = controllers["patient_forms"]

    # Tworzenie danych referencyjnych
    patient_id = patients.add_patient(
        first_name="Marek", last_name="Zieliński", pesel="98765432101",
        phone="987654321", email="marek.zielinski@example.com", address="Łódź",
        date_of_birth="1980-03-15"
    )["patient_id"]

    form_type_id = form_types.add_form_types("Zgoda na zabieg")

    # C - Dodawanie nowego formularza
    patient_form_id = patient_forms.add_form(
        fk_patient_id=patient_id,
        fk_form_type_id=form_type_id,
        submission_date="2025-05-10",
        content="Pierwszy formularz"
    )
    forms = patient_forms.get_forms(filters=[{"column": "patient_form_id", "operator": "=", "value": patient_form_id}])
    assert len(forms) == 1, "Formularz nie został poprawnie dodany."
    assert forms[0]["content"] == "Pierwszy formularz"

    # R - Pobieranie danych
    all_forms = patient_forms.get_forms()
    assert len(all_forms) == 1, "Nieprawidłowa liczba formularzy w bazie danych."
    assert all_forms[0]["patient_form_id"] == patient_form_id

    # U - Aktualizacja formularza
