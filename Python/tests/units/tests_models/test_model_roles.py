# test_model_roles.py

import os
import pytest
from controllers.database_controller import DatabaseController
from models.roles import Roles

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu Roles.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `roles`
    roles_model = Roles(db_controller)
    roles_model.create_table()

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM roles")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+

def test_create_new_record_success(setup_database):
    """
    Test poprawnego dodania rekordu.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    result = roles.get_all_records()

    assert len(result) == 1, "Rekord nie został poprawnie dodany."
    assert result[0]["role_name"] == "Administrator", "Nazwa roli jest niepoprawna."


def test_create_new_record_duplicate(setup_database):
    """
    Test próby dodania rekordu z duplikatem.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")

    with pytest.raises(ValueError, match="Nazwa roli 'Administrator' już istnieje w bazie danych."):
        roles.create_new_record("Administrator")


def test_create_new_record_invalid_name(setup_database):
    """
    Test próby dodania rekordu z nieprawidłową nazwą.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    with pytest.raises(ValueError, match="role_name musi być ciągiem znaków."):
        roles.create_new_record(123)

    with pytest.raises(ValueError, match="role_name musi mieć długość od 3 do 50 znaków."):
        roles.create_new_record("AB")

def test_create_new_record_empty_database(setup_database):
    """
    Test dodania rekordu do pustej bazy danych.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    result = roles.get_all_records()

    assert len(result) == 1, "Rekord nie został poprawnie dodany do pustej bazy."
    assert result[0]["role_name"] == "Administrator", "Niepoprawna nazwa roli."

def test_create_new_record_missing_data(setup_database):
    """
    Test próby dodania rekordu z brakującymi danymi.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    with pytest.raises(ValueError, match="role_name nie może być pusty."):
        roles.create_new_record("")


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

def test_update_record_success(setup_database):
    """
    Test poprawnej aktualizacji rekordu.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    roles.update_record(1, {"role_name": "Manager"})

    result = roles.get_all_records()
    assert result[0]["role_name"] == "Manager", "Nazwa roli nie została poprawnie zaktualizowana."


def test_update_record_nonexistent_id(setup_database):
    """
    Test próby aktualizacji nieistniejącego rekordu.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    with pytest.raises(ValueError, match="Rekord z role_id = 1 nie istnieje w tabeli roles."):
        roles.update_record(1, {"role_name": "Manager"})


def test_update_record_invalid_data(setup_database):
    """
    Test próby aktualizacji rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")

    with pytest.raises(ValueError, match="role_name musi być ciągiem znaków."):
        roles.update_record(1, {"role_name": 123})

    with pytest.raises(ValueError, match="role_name musi mieć długość od 3 do 50 znaków."):
        roles.update_record(1, {"role_name": "Ad"})

    with pytest.raises(ValueError, match=r"role_name może zawierać tylko litery \(w tym polskie znaki\)."):
        roles.update_record(1, {"role_name": "Admin123"})



def test_update_multiple_fields(setup_database):
    """
    Test aktualizacji wielu pól jednocześnie.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    roles.update_record(1, {"role_name": "Manager"})

    result = roles.get_all_records()
    assert result[0]["role_name"] == "Manager", "Aktualizacja wielu pól nie powiodła się."

def test_update_unique_constraint_violation(setup_database):
    """
    Test naruszenia ograniczenia unikalności podczas aktualizacji.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    roles.create_new_record("Manager")

    with pytest.raises(ValueError, match="Nazwa roli już istnieje w bazie danych."):
        roles.update_record(2, {"role_name": "Administrator"})


def test_update_record_no_data(setup_database):
    """
    Test próby aktualizacji rekordu bez danych.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")

    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        roles.update_record(1, {})



# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+

def test_delete_record_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    roles.delete_record_by_id(1)

    result = roles.get_all_records()
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_record_nonexistent_id(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    with pytest.raises(ValueError, match="Rekord z role_id = 1 nie istnieje w tabeli roles."):
        roles.delete_record_by_id(1)


# +-+-+-+- Testy metod pobierania, filtrowania i sortowania -+-+-+-+-+

def test_get_all_records_empty(setup_database):
    """
    Test pobrania rekordów z pustej bazy.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    result = roles.get_all_records()
    assert len(result) == 0, "Baza powinna być pusta."


def test_get_records_by_column_success(setup_database):
    """
    Test poprawnego pobrania rekordów na podstawie kolumny.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    result = roles.get_records_by_column("role_name", "Administrator")

    assert len(result) == 1, "Nie znaleziono odpowiednich rekordów."
    assert result[0]["role_name"] == "Administrator", "Niepoprawne dane rekordu."


def test_filter_records_success(setup_database):
    """
    Test filtrowania rekordów za pomocą operatora.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    roles.create_new_record("Manager")

    result = roles.filter_records("role_name", "LIKE", "%Admin%")
    assert len(result) == 1, "Filtrowanie zwróciło niepoprawną liczbę rekordów."
    assert result[0]["role_name"] == "Administrator", "Niepoprawne dane po filtrowaniu."


def test_sort_records_success(setup_database):
    """
    Test sortowania rekordów.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Manager")
    roles.create_new_record("Administrator")

    result = roles.sort_records("role_name", ascending=True)
    assert result[0]["role_name"] == "Administrator", "Sortowanie nie działa poprawnie."
    assert result[1]["role_name"] == "Manager", "Sortowanie nie działa poprawnie."

def test_get_nonexistent_record(setup_database):
    """
    Test pobierania nieistniejącego rekordu.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    result = roles.get_records_by_column("role_id", 999)
    assert len(result) == 0, "Pobieranie nieistniejącego rekordu powinno zwrócić pustą listę."

def test_get_records_empty_database(setup_database):
    """
    Test pobierania rekordów z pustej bazy.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    result = roles.get_all_records()
    assert len(result) == 0, "Baza powinna być pusta."

def test_filter_records_in_operator(setup_database):
    """
    Test filtrowania rekordów z operatorem IN.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Administrator")
    roles.create_new_record("Manager")

    result = roles.filter_records("role_name", "IN", ["Administrator", "Manager"])
    assert len(result) == 2, "Filtrowanie z operatorem IN nie zwróciło wszystkich oczekiwanych rekordów."

def test_sort_records_ascending(setup_database):
    """
    Test sortowania rekordów rosnąco.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Manager")
    roles.create_new_record("Administrator")

    result = roles.sort_records("role_name", ascending=True)
    assert result[0]["role_name"] == "Administrator", "Sortowanie rosnąco nie działa poprawnie."
    assert result[1]["role_name"] == "Manager", "Sortowanie rosnąco nie działa poprawnie."


def test_sort_records_descending(setup_database):
    """
    Test sortowania rekordów malejąco.
    """
    db_controller = setup_database
    roles = Roles(db_controller)

    roles.create_new_record("Manager")
    roles.create_new_record("Administrator")

    result = roles.sort_records("role_name", ascending=False)
    assert result[0]["role_name"] == "Manager", "Sortowanie malejąco nie działa poprawnie."
    assert result[1]["role_name"] == "Administrator", "Sortowanie malejąco nie działa poprawnie."
