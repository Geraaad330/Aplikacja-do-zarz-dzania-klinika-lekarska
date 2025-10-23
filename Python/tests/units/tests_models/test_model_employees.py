# test_model_employees.py

import os
import re
import pytest
from controllers.database_controller import DatabaseController
from models.employees import Employees

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu Employees.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `employees`
    employees_model = Employees(db_controller)
    employees_model.create_table()

    yield db_controller
    db_controller.close_connection()

# +-+-+-+- testy metod aktualizacji rekordu: -+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+--+-+-+-+

def test_update_single_column_each_field(setup_database):
    """
    Test aktualizacji pojedynczej wartości dla każdej kolumny osobno.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", 
        "Informatyk", 1
    )

    # Aktualizacja pól i weryfikacja
    employees.update_employee(1, first_name="Janusz")
    assert employees.get_employee_by_id(1)["first_name"] == "Janusz", "Niepoprawna aktualizacja first_name."

    employees.update_employee(1, last_name="Nowak")
    assert employees.get_employee_by_id(1)["last_name"] == "Nowak", "Niepoprawna aktualizacja last_name."

    employees.update_employee(1, email="nowy.email@example.com")
    assert employees.get_employee_by_id(1)["email"] == "nowy.email@example.com", "Niepoprawna aktualizacja email."

    employees.update_employee(1, phone="987654321")
    assert employees.get_employee_by_id(1)["phone"] == "987654321", "Niepoprawna aktualizacja phone."

    employees.update_employee(1, profession="Recepcjonista")
    assert employees.get_employee_by_id(1)["profession"] == "Recepcjonista", "Niepoprawna aktualizacja profession."

    employees.update_employee(1, is_medical_staff=0)
    assert employees.get_employee_by_id(1)["is_medical_staff"] == 0, "Niepoprawna aktualizacja is_medical_staff."


def test_update_all_columns(setup_database):
    """
    Test aktualizacji wszystkich pól jednocześnie.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "123456789", 
        "Informatyk", 1
    )

    # Aktualizacja wszystkich pól
    employees.update_employee(1, 
        first_name="Katarzyna",
        last_name="Zielińska",
        email="katarzyna.zielinska@example.com",
        phone="987654321",
        profession="Recepcjonista",
        is_medical_staff=0
    )
    result = employees.get_employee_by_id(1)
    assert result["first_name"] == "Katarzyna", "Niepoprawna aktualizacja first_name."
    assert result["last_name"] == "Zielińska", "Niepoprawna aktualizacja last_name."
    assert result["email"] == "katarzyna.zielinska@example.com", "Niepoprawna aktualizacja email."
    assert result["phone"] == "987654321", "Niepoprawna aktualizacja phone."
    assert result["profession"] == "Recepcjonista", "Niepoprawna aktualizacja profession."
    assert result["is_medical_staff"] == 0, "Niepoprawna aktualizacja is_medical_staff."



def test_update_multiple_columns(setup_database):
    """
    Test aktualizacji wielu pól jednocześnie.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Marek", "Lewandowski", "marek.lewandowski@example.com", "123456789", 
        "Psycholog kliniczny", 1
    )

    # Aktualizacja dwóch pól
    employees.update_employee(1, email="nowy.email@example.com", phone="987654321")
    result = employees.get_employee_by_id(1)
    assert result["email"] == "nowy.email@example.com", "Niepoprawna aktualizacja email."
    assert result["phone"] == "987654321", "Niepoprawna aktualizacja phone."


def test_update_nonexistent_employee(setup_database):
    """
    Test aktualizacji nieistniejącego pracownika.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    with pytest.raises(KeyError, match="Pracownik o ID 1 nie istnieje."):
        employees.update_employee(1, email="test@example.com")


def test_update_without_data(setup_database):
    """
    Test aktualizacji bez danych.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", 
        "Informatyk", 1
    )

    # Próba aktualizacji bez podania danych
    with pytest.raises(ValueError, match="Brak danych do aktualizacji."):
        employees.update_employee(1)


def test_update_with_duplicate_unique_fields(setup_database):
    """
    Test aktualizacji, gdy unikalne pola powodują konflikt.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie dwóch pracowników
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", 
        "Informatyk", 1
    )
    employees.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "987654321", 
        "Recepcjonista", 0
    )

    # Próba aktualizacji z konfliktem email
    with pytest.raises(ValueError, match="email musi być unikalny"):
        employees.update_employee(2, email="jan.kowalski@example.com")

    # Próba aktualizacji z konfliktem phone
    with pytest.raises(ValueError, match="phone musi być unikalny"):
        employees.update_employee(2, phone="123456789")


def test_update_with_invalid_data(setup_database):
    """
    Test aktualizacji z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", 
        "Informatyk", 1
    )

    # Aktualizacja z nieprawidłowym emailem
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        employees.update_employee(1, email="niepoprawny_email")

    # Aktualizacja z nieprawidłowym numerem telefonu
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        employees.update_employee(1, phone="12345")

    # Aktualizacja z nieprawidłowym zawodem
    with pytest.raises(ValueError, match="profession musi należeć do listy dopuszczalnych wartości."):
        employees.update_employee(1, profession="Nieprawidłowy zawód")

    # Aktualizacja z nieprawidłową wartością is_medical_staff
    with pytest.raises(ValueError, match=re.escape("is_medical_staff musi przyjmować wartość 0 (nie-medyk) lub 1 (medyk).")):
        employees.update_employee(1, is_medical_staff=2)



# +-+-+-+- testy metod dodawania rekordu: -+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+--+-+-+-+

def test_add_employee_success(setup_database):
    """
    Test poprawnego dodania rekordu.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie poprawnego rekordu
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )

    # Pobranie dodanego rekordu
    result = employees.get_employee_by_id(1)

    # Weryfikacja danych
    assert result["first_name"] == "Jan", "Imię nie zostało poprawnie zapisane."
    assert result["last_name"] == "Kowalski", "Nazwisko nie zostało poprawnie zapisane."
    assert result["email"] == "jan.kowalski@example.com", "Email nie został poprawnie zapisany."
    assert result["phone"] == "123456789", "Numer telefonu nie został poprawnie zapisany."
    assert result["profession"] == "Informatyk", "Zawód nie został poprawnie zapisany."
    assert result["is_medical_staff"] == 1, "Flaga is_medical_staff nie została poprawnie zapisana."


def test_add_employee_missing_data(setup_database):
    """
    Test próby dodania rekordu z brakującymi danymi.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Próba dodania rekordu bez emaila
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        employees.add_employee(
            "Jan", "Kowalski", "", "123456789", "Informatyk", 1
        )

    # Próba dodania rekordu bez numeru telefonu
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        employees.add_employee(
            "Jan", "Kowalski", "jan.kowalski@example.com", "", "Informatyk", 1
        )


def test_add_employee_invalid_data(setup_database):
    """
    Test próby dodania rekordu z nieprawidłowymi danymi.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Nieprawidłowy email
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        employees.add_employee(
            "Jan", "Kowalski", "niepoprawny_email", "123456789", "Informatyk", 1
        )

    # Nieprawidłowy numer telefonu
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        employees.add_employee(
            "Jan", "Kowalski", "jan.kowalski@example.com", "12345", "Informatyk", 1
        )

    # Nieprawidłowy zawód
    with pytest.raises(ValueError, match="profession musi należeć do listy dopuszczalnych wartości."):
        employees.add_employee(
            "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Nieprawidłowy zawód", 1
        )

    # Nieprawidłowa wartość is_medical_staff
    with pytest.raises(ValueError, match=re.escape("is_medical_staff musi przyjmować wartość 0 (nie-medyk) lub 1 (medyk).")):
        employees.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 2)




def test_add_employee_duplicate_unique_fields(setup_database):
    """
    Test próby dodania rekordu z duplikatem email lub phone (UNIQUE).
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pierwszego rekordu
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )

    # Próba dodania rekordu z tym samym email
    with pytest.raises(ValueError, match="email musi być unikalny"):
        employees.add_employee(
            "Anna", "Nowak", "jan.kowalski@example.com", "987654321",
            "Recepcjonista", 0
        )

    # Próba dodania rekordu z tym samym numerem telefonu
    with pytest.raises(ValueError, match="phone musi być unikalny"):
        employees.add_employee(
            "Anna", "Nowak", "anna.nowak@example.com", "123456789",
            "Recepcjonista", 0
        )



def test_add_employee_to_empty_database(setup_database):
    """
    Test dodania rekordu do pustej bazy danych.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pierwszego rekordu
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )

    # Pobranie wszystkich rekordów
    results = employees.get_all_employees()

    # Weryfikacja, czy baza zawiera dokładnie jeden rekord
    assert len(results) == 1, "Baza danych powinna zawierać jeden rekord."
    assert results[0]["email"] == "jan.kowalski@example.com", "Email pierwszego rekordu jest niepoprawny."


# +-+-+-+- testy metod usuwania rekordu: -+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+--+-+-+-+

def test_delete_employee_success(setup_database):
    """
    Test poprawnego usunięcia rekordu.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )

    # Sprawdzenie, czy rekord istnieje przed usunięciem
    result_before_delete = employees.get_employee_by_id(1)
    assert result_before_delete is not None, "Rekord powinien istnieć przed usunięciem."

    # Usunięcie pracownika
    employees.delete_employee(1)

    # Sprawdzenie, czy rekord został usunięty
    with pytest.raises(KeyError, match="Pracownik o ID 1 nie istnieje."):
        employees.get_employee_by_id(1)


def test_delete_employee_not_found(setup_database):
    """
    Test próby usunięcia nieistniejącego rekordu.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(KeyError, match="Pracownik o ID 1 nie istnieje."):
        employees.delete_employee(1)

# +-+-+-+- testy metod pobierania, filtrowania, sortowania -+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+--+-+-+-+

def test_get_employee_by_id_success(setup_database):
    """
    Test poprawnego pobrania istniejącego rekordu.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracownika
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )

    # Pobranie pracownika
    result = employees.get_employee_by_id(1)

    # Weryfikacja danych
    assert result["first_name"] == "Jan", "Niepoprawne dane: first_name."
    assert result["last_name"] == "Kowalski", "Niepoprawne dane: last_name."
    assert result["email"] == "jan.kowalski@example.com", "Niepoprawne dane: email."
    assert result["phone"] == "123456789", "Niepoprawne dane: phone."
    assert result["profession"] == "Informatyk", "Niepoprawne dane: profession."
    assert result["is_medical_staff"] == 1, "Niepoprawne dane: is_medical_staff."


def test_get_employee_by_id_not_found(setup_database):
    """
    Test próby pobrania nieistniejącego rekordu.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Próba pobrania pracownika, który nie istnieje
    with pytest.raises(KeyError, match="Pracownik o ID 1 nie istnieje."):
        employees.get_employee_by_id(1)


def test_get_all_employees(setup_database):
    """
    Test pobrania wszystkich rekordów z bazy.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracowników
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )
    employees.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "987654321",
        "Recepcjonista", 0
    )

    # Pobranie wszystkich rekordów
    results = employees.get_all_employees()

    # Weryfikacja liczby i danych rekordów
    assert len(results) == 2, "Niepoprawna liczba rekordów."
    assert results[0]["first_name"] == "Jan", "Niepoprawne dane pierwszego rekordu."
    assert results[1]["first_name"] == "Anna", "Niepoprawne dane drugiego rekordu."


def test_get_all_employees_empty_database(setup_database):
    """
    Test pobrania rekordów z pustej bazy.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Pobranie rekordów z pustej bazy
    results = employees.get_all_employees()

    # Weryfikacja, czy baza jest pusta
    assert len(results) == 0, "Baza powinna być pusta."


def test_filter_employees_single_parameter(setup_database):
    """
    Test filtrowania rekordów za pomocą jednego parametru.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracowników
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )
    employees.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "987654321",
        "Recepcjonista", 0
    )

    # Filtrowanie po profession
    results = employees.filter_employees(profession="Informatyk")

    # Weryfikacja wyników
    assert len(results) == 1, "Niepoprawna liczba wyników filtrowania."
    assert results[0]["first_name"] == "Jan", "Niepoprawne dane wyniku filtrowania."


def test_filter_employees_multiple_parameters(setup_database):
    """
    Test filtrowania rekordów za pomocą kilku parametrów.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracowników
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )
    employees.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "987654321",
        "Recepcjonista", 0
    )

    # Filtrowanie po profession i is_medical_staff
    results = employees.filter_employees(profession="Informatyk", is_medical_staff=1)

    # Weryfikacja wyników
    assert len(results) == 1, "Niepoprawna liczba wyników filtrowania."
    assert results[0]["first_name"] == "Jan", "Niepoprawne dane wyniku filtrowania."


def test_get_sorted_employees(setup_database):
    """
    Test pobrania rekordów z sortowaniem.
    """
    db_controller = setup_database
    employees = Employees(db_controller)

    # Dodanie pracowników
    employees.add_employee(
        "Anna", "Nowak", "anna.nowak@example.com", "987654321",
        "Recepcjonista", 0
    )
    employees.add_employee(
        "Jan", "Kowalski", "jan.kowalski@example.com", "123456789",
        "Informatyk", 1
    )

    # Pobranie posortowanych pracowników
    results = employees.get_sorted_employees(order_by="first_name", ascending=True)

    # Weryfikacja wyników
    assert results[0]["first_name"] == "Anna", "Pracownicy nie są poprawnie posortowani."
    assert results[1]["first_name"] == "Jan", "Pracownicy nie są poprawnie posortowani."
