# test_integration_roles.py
import pytest
import os
from controllers.database_controller import DatabaseController
from controllers.roles_controller import RolesController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

# Fixture do konfiguracji bazy danych
@pytest.fixture(name="test_db_connection")
def test_db_connection_fixture():
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli roles
    roles_controller = RolesController(db_controller)
    roles_controller.create_table()

    yield roles_controller

    # Czyszczenie po testach
    if db_controller.connection is None:
        db_controller.connect_to_database()
    if db_controller.table_exists("roles"):
        db_controller.connection.execute("DROP TABLE roles")
    db_controller.close_connection()


# +-+-+-+-+- Testy dla operacji CRUD +-+-+-+-+-+

def test_add_role(test_db_connection):
    """
    Testuje dodanie nowej roli.
    """
    controller = test_db_connection

    # Dodanie roli
    controller.add_role("Administrator")

    # Weryfikacja dodania
    roles = controller.get_all_roles()
    assert len(roles) == 1
    assert roles[0]["role_name"] == "Administrator"

    # Czyszczenie danych
    controller.delete_role_by_id(roles[0]["role_id"])
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_add_role."


def test_add_role_validation_error(test_db_connection):
    """
    Testuje dodanie roli z błędnymi danymi - walidacja powinna zablokować operację.
    """
    controller = test_db_connection

    # Próba dodania roli z niepoprawną nazwą
    with pytest.raises(ValueError, match="role_name musi mieć długość od 3 do 50 znaków."):
        controller.add_role("Ad")

    # Weryfikacja, że tabela jest pusta
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_add_role_validation_error."


def test_update_role(test_db_connection):
    """
    Testuje aktualizację istniejącej roli.
    """
    controller = test_db_connection

    # Dodanie roli
    controller.add_role("Administrator")

    # Aktualizacja roli
    roles = controller.get_all_roles()
    controller.update_role(roles[0]["role_id"], {"role_name": "Manager"})

    # Weryfikacja aktualizacji
    updated_roles = controller.get_all_roles()
    assert updated_roles[0]["role_name"] == "Manager"

    # Czyszczenie danych
    controller.delete_role_by_id(updated_roles[0]["role_id"])
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_update_role."


def test_delete_nonexistent_role(test_db_connection):
    """
    Testuje próbę usunięcia nieistniejącej roli.
    """
    controller = test_db_connection

    with pytest.raises(ValueError, match="Rekord z role_id = 999 nie istnieje w tabeli roles."):
        controller.delete_role_by_id(999)


# +-+-+-+-+- Testy filtrowania i sortowania +-+-+-+-+-+

def test_filter_roles(test_db_connection):
    """
    Testuje filtrowanie ról na podstawie operatora LIKE.
    """
    controller = test_db_connection

    # Dodanie ról
    controller.add_role("Administrator")
    controller.add_role("Manager")

    # Filtrowanie
    filtered_roles = controller.filter_roles("role_name", "LIKE", "%Admin%")
    assert len(filtered_roles) == 1
    assert filtered_roles[0]["role_name"] == "Administrator"

    # Czyszczenie danych
    roles = controller.get_all_roles()
    for role in roles:
        controller.delete_role_by_id(role["role_id"])

    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_filter_roles."



def test_sort_roles(test_db_connection):
    controller = test_db_connection
    controller.create_table()
    controller.add_role("Admin")
    controller.add_role("User")

    # Test sortowania bez filtrowania
    sorted_roles = controller.sort_roles("role_name", ascending=True)
    assert sorted_roles[0]["role_name"] == "Admin"
    assert sorted_roles[1]["role_name"] == "User"

    # Test sortowania z filtrowaniem
    filtered_sorted_roles = controller.sort_roles("role_name", ascending=True, filter_column="role_name", filter_value="Admin")
    assert len(filtered_sorted_roles) == 1
    assert filtered_sorted_roles[0]["role_name"] == "Admin"



# +-+-+-+-+- Testy liczenia ról +-+-+-+-+-+

def test_count_roles(test_db_connection):
    """
    Testuje liczenie ról w tabeli.
    """
    controller = test_db_connection

    # Dodanie ról
    controller.add_role("Administrator")
    controller.add_role("Manager")

    # Liczenie ról
    count = controller.count_roles()
    assert count == 2

    # Czyszczenie danych
    roles = controller.get_all_roles()
    for role in roles:
        controller.delete_role_by_id(role["role_id"])

    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_count_roles."


def test_operations_on_empty_table(test_db_connection):
    """
    Testuje operacje pobierania, filtrowania i sortowania na pustej tabeli.
    """
    controller = test_db_connection

    # Pobieranie wszystkich rekordów
    all_roles = controller.get_all_roles()
    assert len(all_roles) == 0, "Tabela powinna być pusta."

    # Filtrowanie na pustej tabeli
    filtered_roles = controller.filter_roles("role_name", "LIKE", "%Admin%")
    assert len(filtered_roles) == 0, "Filtrowanie na pustej tabeli powinno zwrócić pustą listę."

    # Sortowanie na pustej tabeli
    sorted_roles = controller.sort_roles("role_name", ascending=True)
    assert len(sorted_roles) == 0, "Sortowanie na pustej tabeli powinno zwrócić pustą listę."


def test_add_duplicate_role(test_db_connection):
    """
    Testuje dodanie duplikatów do tabeli `roles`.
    """
    controller = test_db_connection

    # Dodanie pierwszego rekordu
    controller.add_role("Administrator")

    # Próba dodania duplikatu
    with pytest.raises(ValueError, match="Nazwa roli 'Administrator' już istnieje w bazie danych."):
        controller.add_role("Administrator")

    # Czyszczenie danych
    roles = controller.get_all_roles()
    controller.delete_role_by_id(roles[0]["role_id"])
    result = controller.db_controller.connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    assert result == 0, "Dane nie zostały usunięte z metody test_add_duplicate_role."


def test_filter_roles_with_in_operator(test_db_connection):
    """
    Testuje filtrowanie z operatorem IN.
    """
    controller = test_db_connection

    # Dodanie rekordów
    controller.add_role("Administrator")
    controller.add_role("Manager")

    # Filtrowanie za pomocą operatora IN
    filtered_roles = controller.filter_roles("role_name", "IN", ["Administrator", "Manager"])
    assert len(filtered_roles) == 2, "Filtrowanie za pomocą operatora IN nie zwróciło wszystkich oczekiwanych rekordów."

    # Filtrowanie z pustą listą
    empty_filter = controller.filter_roles("role_name", "IN", [])
    assert empty_filter == [], "Filtrowanie z pustą listą nie zwróciło pustego wyniku."





def test_database_disconnection_handling(test_db_connection):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia.
    """
    controller = test_db_connection

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba dodania roli po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.add_role("Administrator")

    # Próba pobrania ról po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.get_all_roles()  # Poprawiona nazwa metody

    # Ponowne połączenie i weryfikacja
    controller.db_controller.connect_to_database()
    controller.ensure_table_exists()
    controller.add_role("Administrator")
    roles = controller.get_all_roles()
    assert len(roles) == 1
    assert roles[0]["role_name"] == "Administrator"

    # Czyszczenie danych
    controller.delete_role_by_id(roles[0]["role_id"])



def test_reconnect_to_database(test_db_connection):
    controller = test_db_connection

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba ponownego połączenia
    controller.db_controller.connect_to_database()
    controller.ensure_table_exists()

    # Dodanie nowego rekordu po ponownym połączeniu
    controller.add_role("Administrator")
    roles = controller.get_all_roles()
    assert len(roles) == 1
    assert roles[0]["role_name"] == "Administrator"

    # Czyszczenie danych
    controller.delete_role_by_id(roles[0]["role_id"])

