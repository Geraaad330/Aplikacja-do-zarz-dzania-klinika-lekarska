# test_model_specialties.py

import os
import pytest
from controllers.database_controller import DatabaseController
from models.specialties import Specialties
from models.employees import Employees

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu Specialties.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `specialties`
    specialties_model = Specialties(db_controller)
    specialties_model.create_table()

        # Tworzenie tabeli `employees`
    employees_model = Employees(db_controller)
    employees_model.create_table()

    db_controller.connection.execute("""
    CREATE TABLE employee_specialties (
        employee_id INTEGER,
        specialty_id INTEGER,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(specialty_id) REFERENCES specialties(specialty_id)
    )
    """)

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM specialties")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+

def test_create_new_record_success(setup_database):
    """
    Test poprawnego dodania rekordu.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    # Test dodawania poprawnych rekordów
    specialties.create_new_record("Psychiatra dorosłych")
    result = specialties.get_records()
    assert len(result) == 1
    assert result[0]["specialty_name"] == "Psychiatra dorosłych"

    specialties.create_new_record("Specjalność - Test (Zaawansowany)")
    result = specialties.get_records()
    assert len(result) == 2
    assert result[1]["specialty_name"] == "Specjalność - Test (Zaawansowany)"

    specialties.create_new_record("Specjalność: Dietetyk")
    result = specialties.get_records()
    assert len(result) == 3
    assert result[2]["specialty_name"] == "Specjalność: Dietetyk"

    specialties.create_new_record("Terapia poznawczo behawioralna /CBT)")
    result = specialties.get_records()
    assert len(result) == 4
    assert result[3]["specialty_name"] == "Terapia poznawczo behawioralna /CBT)"


def test_create_new_record_invalid_data(setup_database):
    """
    Test próby dodania rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    # Każdy przypadek niepoprawnych danych testowany osobno
    with pytest.raises(ValueError, match="Nazwa specjalności musi być ciągiem znaków."):
        specialties.create_new_record(123)

    with pytest.raises(ValueError, match="Nazwa specjalności nie może być pusta."):
        specialties.create_new_record("")

    with pytest.raises(ValueError, match="Nazwa specjalności musi mieć od 3 do 100 znaków."):
        specialties.create_new_record("AB")

    with pytest.raises(ValueError, match="Nazwa specjalności musi mieć od 3 do 100 znaków."):
        specialties.create_new_record("A" * 101)

    with pytest.raises(ValueError, match="Nazwa specjalności zawiera niedozwolone znaki."):
        specialties.create_new_record("!@#%&*")

    with pytest.raises(ValueError, match="Nazwa specjalności zawiera niedozwolone znaki."):
        specialties.create_new_record("Dietetyk 50%")


def test_create_new_record_duplicate(setup_database):
    """
    Test próby dodania rekordu z duplikatem.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    specialties.create_new_record("Psychiatra dorosłych")

    with pytest.raises(ValueError, match="Specjalność o nazwie 'Psychiatra dorosłych' już istnieje."):
        specialties.create_new_record("Psychiatra dorosłych")


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+

def test_update_record_success(setup_database):
    """
    Test poprawnej aktualizacji rekordu.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    specialties.create_new_record("Psychiatra dorosłych")
    specialties.update_record(1, {"specialty_name": "Psycholog dziecięcy"})

    result = specialties.get_records()
    assert result[0]["specialty_name"] == "Psycholog dziecięcy", "Aktualizacja rekordu nie powiodła się."


def test_update_record_invalid_data(setup_database):
    """
    Test próby aktualizacji rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    specialties.create_new_record("Psychiatra dorosłych")

    with pytest.raises(ValueError, match="Nazwa specjalności zawiera niedozwolone znaki."):
        specialties.update_record(1, {"specialty_name": "Psychiatra@"})


def test_update_record_nonexistent_id(setup_database):
    """
    Test próby aktualizacji nieistniejącego rekordu.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        specialties.update_record(999, {"specialty_name": "Psycholog dziecięcy"})


# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+

def test_delete_record_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    specialties.create_new_record("Psychiatra dorosłych")
    specialties.delete_record(1)

    result = specialties.get_records()
    assert len(result) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_record_nonexistent_id(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        specialties.delete_record(999)


# +-+-+-+- Testy metod pobierania i filtrowania -+-+-+-+-+

def test_get_records_empty_database(setup_database):
    """
    Test pobierania rekordów z pustej bazy.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    result = specialties.get_records()
    assert len(result) == 0, "Baza powinna być pusta."


def test_get_records_with_all_filters(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności filtrowania.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    # Dodanie danych testowych
    specialties.create_new_record("Psychiatra dorosłych")
    specialties.create_new_record("Psycholog dziecięcy")
    specialties.create_new_record("Psychiatra dzieci i młodzieży")
    specialties.create_new_record("Psychoterapeuta")
    
    # Test: LIKE
    filters = [{"column": "specialty_name", "operator": "LIKE", "value": "%Psychiatra%"}]
    result = specialties.get_records(filters=filters)
    assert len(result) == 2, "Filtracja LIKE nie zwróciła poprawnych wyników."

    # Test: =
    filters = [{"column": "specialty_name", "operator": "=", "value": "Psychiatra dorosłych"}]
    result = specialties.get_records(filters=filters)
    assert len(result) == 1, "Filtracja = nie zwróciła poprawnych wyników."
    assert result[0]["specialty_name"] == "Psychiatra dorosłych"

    # Test: IN
    filters = [{"column": "specialty_name", "operator": "IN", "value": ["Psychiatra dorosłych", "Psychoterapeuta"]}]
    result = specialties.get_records(filters=filters)
    assert len(result) == 2, "Filtracja IN nie zwróciła poprawnych wyników."

    # Test: IS NULL (brak danych null w tabeli, baza powinna zwrócić 0 wyników)
    filters = [{"column": "specialty_name", "operator": "IS NULL"}]
    result = specialties.get_records(filters=filters)
    assert len(result) == 0, "Filtracja IS NULL nie powinna zwrócić wyników."

    # Test: IS NOT NULL
    filters = [{"column": "specialty_name", "operator": "IS NOT NULL"}]
    result = specialties.get_records(filters=filters)
    assert len(result) == 4, "Filtracja IS NOT NULL nie zwróciła poprawnych wyników."


def test_get_records_with_all_sorting(setup_database):
    """
    Test pobierania rekordów z wykorzystaniem wszystkich funkcjonalności sortowania.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    # Dodanie danych testowych
    specialties.create_new_record("Psychoterapeuta")
    specialties.create_new_record("Psychiatra dzieci i młodzieży")
    specialties.create_new_record("Psycholog dziecięcy")
    specialties.create_new_record("Psychiatra dorosłych")
    
    # Test: Sortowanie rosnące
    sort_by = [("specialty_name", "ASC")]
    result = specialties.get_records(sort_by=sort_by)
    assert result[0]["specialty_name"] == "Psychiatra dorosłych", "Sortowanie ASC nie działa poprawnie."
    assert result[-1]["specialty_name"] == "Psychoterapeuta"

    # Test: Sortowanie malejące
    sort_by = [("specialty_name", "DESC")]
    result = specialties.get_records(sort_by=sort_by)
    assert result[0]["specialty_name"] == "Psychoterapeuta", "Sortowanie DESC nie działa poprawnie."
    assert result[-1]["specialty_name"] == "Psychiatra dorosłych"

    # Test: Wielokrotne sortowanie (przykład z jedną kolumną i dwoma różnymi kierunkami)
    sort_by = [("specialty_name", "ASC")]
    result = specialties.get_records(sort_by=sort_by)
    assert result[0]["specialty_name"] == "Psychiatra dorosłych", "Wielokrotne sortowanie nie działa poprawnie."

    # Dodanie kolejnego rekordu dla testowania stabilności sortowania
    specialties.create_new_record("Psychiatra terapeutyczny")
    sort_by = [("specialty_name", "ASC")]
    result = specialties.get_records(sort_by=sort_by)
    assert result[1]["specialty_name"] == "Psychiatra dzieci i młodzieży", "Sortowanie z dużą ilością rekordów nie działa poprawnie."



# +-+-+-+- Testy metod specjalnych -+-+-+-+-+

def test_count_specialties_for_all_professions(setup_database):
    """
    Test metody zliczania specjalności dla wszystkich zawodów.
    """
    db_controller = setup_database
    specialties = Specialties(db_controller)

    # Dodaj dane i przetestuj logikę
    specialties.create_new_record("Psychiatra dorosłych")
    result = specialties.count_specialties_for_all_professions()
    assert len(result) == 0, "Niepoprawne wyniki zliczania specjalności."


# +-+-+-+- Testy metod specjalnych -+-+-+-+-+

# def test_count_specialties_for_all_professions(setup_database):
#     """
#     Test metody zliczania specjalności dla wszystkich zawodów.
#     """
#      # Przygotowanie bazy danych
#     db_controller = setup_database
#     specialties = Specialties(db_controller)

#     # Dodaj specjalności
#     specialties.create_new_record("Psychiatria dzieci i młodzieży")
#     specialties.create_new_record("Psychiatria dorosłych")
#     specialties.create_new_record("Terapia poznawczo-behawioralna")

#     # Dodaj pracowników i przypisania
#     employees = Employees(db_controller)
#     employees.add_employee("Jan", "Kowalski", "Psychiatra")
#     employees.add_employee("Anna", "Nowak", "Psychiatra")
#     employees.add_employee("Wojciech", "Szymański", "Psycholog")

#     employee_specialties = EmployeeSpecialties(db_controller)
#     employee_specialties.add_record(1, 1)  # Jan - Psychiatria dzieci
#     employee_specialties.add_record(1, 2)  # Jan - Psychiatria dorosłych
#     employee_specialties.add_record(2, 2)  # Anna - Psychiatria dorosłych
#     employee_specialties.add_record(3, 3)  # Wojciech - Terapia CBT

#     # Test właściwej metody
#     result = specialties.count_specialties_for_all_professions()

#     # Oczekiwany wynik
#     expected_result = [
#         {"specialty_name": "Psychiatria dzieci i młodzieży", "number_of_occurrences": 1},
#         {"specialty_name": "Psychiatria dorosłych", "number_of_occurrences": 2},
#         {"specialty_name": "Terapia poznawczo-behawioralna", "number_of_occurrences": 1},
#     ]

#     assert result == expected_result, "Niepoprawne wyniki zliczania specjalności."