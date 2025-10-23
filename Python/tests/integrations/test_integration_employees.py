# test_integration_employees.py
import pytest
import os
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

# Fixture do konfiguracji bazy danych
@pytest.fixture(name="test_db_connection")
def test_db_connection_fixture():
    """
    Konfiguracja połączenia z testową bazą danych SQLite.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli employees
    employees_controller = EmployeesController(db_controller)
    employees_controller.create_table()

    yield employees_controller

    # Czyszczenie po testach
    db_controller.connection.execute("DROP TABLE employees")
    db_controller.close_connection()


def test_add_employee(test_db_connection):
    """
    Testuje dodanie nowego pracownika.
    """
    controller = test_db_connection

    # Dodanie pracownika
    controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)

    # Sprawdzenie, czy pracownik istnieje
    employee = controller.get_employee(1)
    assert employee["first_name"] == "Jan"
    assert employee["email"] == "jan.kowalski@example.com"

    # Czyszczenie danych
    controller.delete_employee(1)

    # Weryfikacja usunięcia
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_add_employee."


def test_add_employee_validation_error(test_db_connection):
    """
    Testuje dodanie pracownika z błędnymi danymi - walidacja powinna zablokować operację.
    """
    controller = test_db_connection

    # Próba dodania z niepoprawnym email
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        controller.add_employee("Anna", "Nowak", "niepoprawny_email", "123456789", "Psycholog kliniczny", 1)

    # Weryfikacja, że tabela jest pusta
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_add_employee_validation_error."


def test_update_employee(test_db_connection):
    """
    Testuje aktualizację danych istniejącego pracownika.
    """
    controller = test_db_connection

    # Dodanie pracownika
    controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)

    # Aktualizacja pracownika
    controller.update_employee(1, email="nowy.email@example.com", phone="987654321")
    updated_employee = controller.get_employee(1)

    # Sprawdzenie poprawności aktualizacji
    assert updated_employee["email"] == "nowy.email@example.com"
    assert updated_employee["phone"] == "987654321"

    # Czyszczenie danych
    controller.delete_employee(1)

    # Weryfikacja usunięcia
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_update_employee."


def test_delete_nonexistent_employee(test_db_connection):
    """
    Testuje próbę usunięcia nieistniejącego pracownika.
    """
    controller = test_db_connection

    # Próba usunięcia nieistniejącego pracownika
    with pytest.raises(KeyError, match="Pracownik o ID 999 nie istnieje."):
        controller.delete_employee(999)

    # Weryfikacja, że tabela jest pusta
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_delete_nonexistent_employee."


def test_get_all_employees(test_db_connection):
    """
    Testuje pobieranie wszystkich pracowników.
    """
    controller = test_db_connection

    # Dodanie pracowników
    controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)
    controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Recepcjonista", 0)

    # Pobranie wszystkich pracowników
    employees = controller.get_all_employees()
    assert len(employees) == 2

    # Czyszczenie danych
    controller.delete_employee(1)
    controller.delete_employee(2)

    # Weryfikacja usunięcia
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_get_all_employees."


def test_filter_and_sort_employees(test_db_connection):
    """
    Testuje filtrowanie i sortowanie pracowników na podstawie wielu kryteriów.
    """
    controller = test_db_connection

    # Dodanie pracowników
    controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)
    controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "987654321", "Recepcjonista", 0)
    controller.add_employee("Piotr", "Zieliński", "piotr.zielinski@example.com", "555555555", "Psycholog kliniczny", 1)

    # Filtrowanie po zawodzie i sortowanie po imieniu
    filtered_sorted = controller.filter_employees(profession="Informatyk")
    sorted_list = controller.get_sorted_employees(order_by="first_name", ascending=False)

    # Weryfikacja wyników filtrowania
    assert len(filtered_sorted) == 1
    assert filtered_sorted[0]["first_name"] == "Jan"

    # Weryfikacja wyników sortowania
    assert sorted_list[0]["first_name"] == "Piotr", "Błąd sortowania malejącego."
    assert sorted_list[2]["first_name"] == "Anna", "Błąd sortowania malejącego."

    # Czyszczenie danych
    controller.db_controller.connection.execute("DELETE FROM employees")
    controller.db_controller.connection.commit()
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_filter_and_sort_employees."


def test_add_employee_duplicate_email(test_db_connection):
    """
    Testuje próbę dodania pracownika z istniejącym e-mailem lub numerem telefonu.
    """
    controller = test_db_connection

    # Dodanie pierwszego pracownika
    controller.add_employee("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)

    # Próba dodania drugiego pracownika z tym samym e-mailem
    with pytest.raises(ValueError, match="email musi być unikalny"):
        controller.add_employee("Anna", "Nowak", "jan.kowalski@example.com", "987654321", "Psycholog kliniczny", 1)

    # Próba dodania drugiego pracownika z tym samym numerem telefonu
    with pytest.raises(ValueError, match="phone musi być unikalny"):
        controller.add_employee("Anna", "Nowak", "anna.nowak@example.com", "123456789", "Recepcjonista", 0)

    # Weryfikacja liczby rekordów w bazie (powinien być tylko jeden)
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 1, "W bazie danych powinien znajdować się tylko jeden unikalny pracownik."

    # Czyszczenie danych
    controller.delete_employee(1)
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_add_employee_duplicate_email."

