# test_integration_permissions.py
import pytest
import os
from controllers.database_controller import DatabaseController
from controllers.permissions_controller import PermissionsController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

# Fixture do konfiguracji bazy danych
@pytest.fixture(name="test_db_connection")
def test_db_connection_fixture():
    """
    Konfiguracja połączenia z testową bazą danych SQLite oraz inicjalizacja tabeli `system_permissions`.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli permissions
    permissions_controller = PermissionsController(db_controller)
    permissions_controller.create_table()

    yield permissions_controller

    # Czyszczenie tabeli po testach
    if db_controller.connection is not None:
        db_controller.connection.execute("DROP TABLE system_permissions")
    db_controller.close_connection()


def test_create_table(test_db_connection):
    """
    Testuje utworzenie tabeli `system_permissions`.

    Spodziewany rezultat:
    Tabela `system_permissions` zostaje pomyślnie utworzona.
    """
    permissions_controller = test_db_connection
    assert permissions_controller.db_controller.connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='system_permissions';"
    ).fetchone(), "Tabela `system_permissions` nie została utworzona."


def test_get_all_permissions_empty(test_db_connection):
    """
    Testuje pobieranie wszystkich uprawnień w pustej tabeli.

    Spodziewany rezultat:
    Metoda zwraca pustą listę, ponieważ tabela nie zawiera rekordów.
    """
    permissions_controller = test_db_connection
    permissions = permissions_controller.get_all_permissions()
    assert len(permissions) == 0, "Tabela powinna być pusta."


def test_add_and_get_all_permissions(test_db_connection):
    """
    Testuje dodanie uprawnień do tabeli i ich pobranie.

    Spodziewany rezultat:
    Rekordy są dodawane do tabeli i poprawnie zwracane przez metodę `get_all_permissions`.
    """
    permissions_controller = test_db_connection

    # Dodanie rekordów do tabeli
    permissions_controller.db_controller.connection.execute(
        """
        INSERT INTO system_permissions (permission_name) VALUES 
        ('zarzadzaj_pracownikami'), ('przegladaj_diagnozy');
        """
    )
    permissions_controller.db_controller.connection.commit()

    # Pobranie wszystkich rekordów
    permissions = permissions_controller.get_all_permissions()
    assert len(permissions) == 2, "Tabela powinna zawierać dwa rekordy."
    assert permissions[0]["permission_name"] == "zarzadzaj_pracownikami"


def test_filter_permissions_by_name(test_db_connection):
    """
    Testuje filtrowanie uprawnień na podstawie nazw (IN).

    Spodziewany rezultat:
    Metoda zwraca tylko rekordy odpowiadające podanym nazwom.
    """
    permissions_controller = test_db_connection

    # Dodanie rekordów do tabeli
    permissions_controller.db_controller.connection.execute(
        """
        INSERT INTO system_permissions (permission_name) VALUES 
        ('zarzadzaj_pracownikami'), ('przegladaj_diagnozy'), ('zarzadzaj_wszystkimi_pacjentami');
        """
    )
    permissions_controller.db_controller.connection.commit()

    # Filtrowanie po nazwach
    filtered_permissions = permissions_controller.filter_permissions(
        permission_names=["zarzadzaj_pracownikami", "zarzadzaj_wszystkimi_pacjentami"]
    )
    assert len(filtered_permissions) == 2, "Powinny zostać zwrócone dwa rekordy."
    assert filtered_permissions[0]["permission_name"] == "zarzadzaj_pracownikami"


def test_sort_permissions(test_db_connection):
    """
    Testuje sortowanie uprawnień według kolumny `permission_name`.

    Spodziewany rezultat:
    Rekordy są zwracane w rosnącej kolejności według nazw uprawnień.
    """
    permissions_controller = test_db_connection

    # Dodanie rekordów do tabeli
    permissions_controller.db_controller.connection.execute(
        """
        INSERT INTO system_permissions (permission_name) VALUES 
        ('zarzadzaj_pracownikami'), ('przegladaj_diagnozy'), ('zarzadzaj_wszystkimi_pacjentami');
        """
    )
    permissions_controller.db_controller.connection.commit()

    # Sortowanie
    sorted_permissions = permissions_controller.get_sorted_permissions(
        order_by="permission_name", ascending=True
    )
    assert sorted_permissions[0]["permission_name"] == "przegladaj_diagnozy"
    assert sorted_permissions[1]["permission_name"] == "zarzadzaj_pracownikami"
    assert sorted_permissions[2]["permission_name"] == "zarzadzaj_wszystkimi_pacjentami"


def test_count_permissions(test_db_connection):
    """
    Testuje zliczanie wszystkich uprawnień w tabeli.

    Spodziewany rezultat:
    Metoda zwraca poprawną liczbę rekordów w tabeli.
    """
    permissions_controller = test_db_connection

    # Dodanie rekordów do tabeli
    permissions_controller.db_controller.connection.execute(
        """
        INSERT INTO system_permissions (permission_name) VALUES 
        ('zarzadzaj_wszystkimi_pacjentami'), ('przegladaj_przypisanych_pacjentow');
        """
    )
    permissions_controller.db_controller.connection.commit()

    # Zliczanie rekordów
    count = permissions_controller.count_permissions()
    assert count == 2, "Tabela powinna zawierać dwa rekordy."


def test_validation_error_on_invalid_like_pattern(test_db_connection):
    """
    Testuje działanie walidacji w przypadku niepoprawnego wzorca LIKE.

    Spodziewany rezultat:
    Walidacja zgłasza wyjątek ValueError z odpowiednim komunikatem.
    """
    permissions_controller = test_db_connection
    with pytest.raises(ValueError, match="Wzorzec LIKE zawiera niedozwolone znaki."):
        permissions_controller.filter_permissions(name_pattern="DROP TABLE;")

def test_filter_permissions_empty_list(test_db_connection):
    """
    Testuje walidację pustej listy w metodzie filter_permissions.

    Spodziewany rezultat:
    Walidacja zgłasza wyjątek ValueError z odpowiednim komunikatem.
    """
    permissions_controller = test_db_connection
    with pytest.raises(ValueError, match="Lista nazw uprawnień nie może być pusta."):
        permissions_controller.filter_permissions(permission_names=[])

def test_get_all_permissions_no_connection(test_db_connection):
    """
    Testuje reakcję systemu na brak połączenia z bazą danych podczas pobierania uprawnień.

    Spodziewany rezultat:
    System zgłasza wyjątek RuntimeError z odpowiednim komunikatem.
    """
    permissions_controller = test_db_connection
    permissions_controller.db_controller.close_connection()  # Zamknięcie połączenia
    with pytest.raises(RuntimeError, match="Brak aktywnego połączenia z bazą danych."):
        permissions_controller.get_all_permissions()

def test_filter_permissions_nonexistent_values(test_db_connection):
    """
    Testuje filtrowanie wartości, które nie istnieją w bazie danych.

    Spodziewany rezultat:
    System zwraca pustą listę wyników.
    """
    permissions_controller = test_db_connection
    filtered_permissions = permissions_controller.filter_permissions(
        permission_names=["Nieistniejący rekord"]
    )
    assert len(filtered_permissions) == 0, "Powinien zostać zwrócony pusty wynik."
