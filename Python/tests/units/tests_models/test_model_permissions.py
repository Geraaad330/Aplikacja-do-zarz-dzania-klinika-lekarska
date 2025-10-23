# test_model_permissions.py
# Testy dla modelu Permissions

import os
import pytest
from controllers.database_controller import DatabaseController
from models.permissions import Permissions

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"


@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    Konfiguracja testowej bazy danych dla testów modelu Permissions.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `employees`
    permissions_model = Permissions(db_controller)
    permissions_model.create_table()

    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        db_controller.connection.execute("DELETE FROM system_permissions")
    db_controller.close_connection()


def test_get_all_permissions_empty_database(setup_database):
    """
    Test pobierania wszystkich rekordów z pustej bazy danych.
    """
    permissions = Permissions(setup_database)
    results = permissions.get_all_permissions()
    assert len(results) == 0, "Baza powinna być pusta."


def test_get_all_permissions(setup_database):
    """
    Test pobierania wszystkich rekordów z bazy danych.
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (1, 'zarzadzaj_wszystkimi_pacjentami'), (2, 'przegladaj_przypisanych_pacjentow')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    results = permissions.get_all_permissions()
    assert len(results) == 2, "Niepoprawna liczba rekordów."
    assert results[0]["permission_name"] == "zarzadzaj_wszystkimi_pacjentami"


def test_filter_permissions_by_names(setup_database):
    """
    Test filtrowania rekordów po nazwach (IN).
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (1, 'zarzadzaj_wszystkimi_pacjentami'),
           (2, 'przegladaj_przypisanych_pacjentow'),
           (3, 'edytuj_przypisanych_pacjentow')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    results = permissions.filter_permissions(permission_names=[
        "zarzadzaj_wszystkimi_pacjentami",
        "przegladaj_przypisanych_pacjentow"
    ])
    assert len(results) == 2, "Niepoprawna liczba wyników filtrowania."
    assert results[0]["permission_name"] == "przegladaj_przypisanych_pacjentow"
    assert results[1]["permission_name"] == "zarzadzaj_wszystkimi_pacjentami"



def test_filter_permissions_by_pattern(setup_database):
    """
    Test filtrowania rekordów po wzorcu (LIKE).
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (1, 'zarzadzaj_wszystkimi_pacjentami'), (2, 'przegladaj_przypisanych_pacjentow'), (3, 'edytuj_przypisanych_pacjentow')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    results = permissions.filter_permissions(name_pattern="%aj%")
    assert len(results) == 2, "Niepoprawna liczba wyników filtrowania po wzorcu."


def test_get_sorted_permissions(setup_database):
    """
    Test sortowania rekordów według kolumny.
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (2, 'przegladaj_przypisanych_pacjentow'), (1, 'zarzadzaj_wszystkimi_pacjentami')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    results = permissions.get_sorted_permissions(order_by="permission_name", ascending=True)
    assert results[0]["permission_name"] == "przegladaj_przypisanych_pacjentow", "Sortowanie nie działa poprawnie."
    assert results[1]["permission_name"] == "zarzadzaj_wszystkimi_pacjentami", "Sortowanie nie działa poprawnie."


def test_count_permissions(setup_database):
    """
    Test zliczania rekordów.
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (1, 'zarzadzaj_wszystkimi_pacjentami'), (2, 'przegladaj_przypisanych_pacjentow')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    count = permissions.count_permissions()
    assert count == 2, "Niepoprawna liczba rekordów."


def test_count_permissions_with_pattern(setup_database):
    """
    Test zliczania rekordów z wzorcem (LIKE).
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (1, 'zarzadzaj_wszystkimi_pacjentami'), (2, 'przegladaj_przypisanych_pacjentow'), (3, 'edytuj_przypisanych_pacjentow')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    count = permissions.count_permissions(name_pattern="%aj%")
    assert count == 2, "Niepoprawna liczba rekordów z wzorcem."


def test_count_permissions_by_name(setup_database):
    """
    Test zliczania rekordów na podstawie listy nazw (IN).
    """
    db_controller = setup_database
    db_controller.connection.execute("""
    INSERT INTO system_permissions (permission_id, permission_name)
    VALUES (1, 'zarzadzaj_wszystkimi_pacjentami'), (2, 'przegladaj_przypisanych_pacjentow'), (3, 'edytuj_przypisanych_pacjentow')
    """)
    db_controller.connection.commit()

    permissions = Permissions(db_controller)
    count = permissions.count_permissions_by_name(["zarzadzaj_wszystkimi_pacjentami", "przegladaj_przypisanych_pacjentow"])
    assert count == 2, "Niepoprawna liczba rekordów na podstawie listy nazw."



def test_get_all_permissions_no_connection(setup_database):
    """
    Test sprawdzający działanie metody get_all_permissions
    w przypadku braku połączenia z bazą danych.
    """
    setup_database.close_connection()
    with pytest.raises(RuntimeError, match="Brak aktywnego połączenia z bazą danych."):
        permissions = Permissions(setup_database)
        permissions.get_all_permissions()



def test_filter_permissions_empty_names(setup_database):
    """
    Test sprawdzający działanie metody filter_permissions
    w przypadku pustej listy w parametrze permission_names.
    """
    permissions = Permissions(setup_database)
    with pytest.raises(ValueError, match="Lista nazw uprawnień nie może być pusta."):
        permissions.filter_permissions(permission_names=[])


def test_filter_permissions_invalid_like_pattern(setup_database):
    """
    Test sprawdzający działanie metody filter_permissions
    w przypadku nieprawidłowego wzorca LIKE (np. zawierającego niedozwolone znaki SQL).
    """
    permissions = Permissions(setup_database)
    with pytest.raises(ValueError, match="Wzorzec LIKE zawiera niedozwolone znaki."):
        permissions.filter_permissions(name_pattern="DROP TABLE;")


def test_filter_permissions_nonexistent_values(setup_database):
    """
    Test sprawdzający działanie metody filter_permissions
    w przypadku wartości, które nie istnieją w bazie danych.
    """
    permissions = Permissions(setup_database)
    results = permissions.filter_permissions(permission_names=["Nieistniejący rekord"])
    assert len(results) == 0, "Wynik powinien być pusty dla wartości, które nie istnieją w bazie."



def test_get_sorted_permissions_empty_database(setup_database):
    """
    Test sprawdzający działanie metody get_sorted_permissions
    w przypadku pustej tabeli.
    """
    permissions = Permissions(setup_database)
    results = permissions.get_sorted_permissions(order_by="permission_name")
    assert len(results) == 0, "Baza powinna być pusta."


def test_get_sorted_permissions_invalid_column(setup_database):
    """
    Test sprawdzający działanie metody get_sorted_permissions
    w przypadku podania niepoprawnej nazwy kolumny.
    """
    permissions = Permissions(setup_database)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna: invalid_column. Dozwolone kolumny: .*"):
        permissions.get_sorted_permissions(order_by="invalid_column")


def test_count_permissions_no_results(setup_database):
    """
    Test sprawdzający działanie metody count_permissions
    w przypadku wzorca LIKE, który nie pasuje do żadnego rekordu.
    """
    permissions = Permissions(setup_database)
    count = permissions.count_permissions(name_pattern="%Nieistniejący%")
    assert count == 0, "Liczba wyników powinna wynosić 0."


def test_count_permissions_invalid_pattern(setup_database):
    """
    Test sprawdzający działanie metody count_permissions
    w przypadku niepoprawnego wzorca LIKE.
    """
    permissions = Permissions(setup_database)
    with pytest.raises(ValueError, match="Wzorzec LIKE zawiera niedozwolone znaki."):
        permissions.count_permissions(name_pattern="DROP TABLE;")


def test_count_permissions_by_name_empty_list(setup_database):
    """
    Test sprawdzający działanie metody count_permissions_by_name
    w przypadku pustej listy nazw.
    """
    permissions = Permissions(setup_database)
    with pytest.raises(ValueError, match="Lista nazw uprawnień nie może być pusta."):
        permissions.count_permissions_by_name([])


def test_count_permissions_by_name_invalid_values(setup_database):
    """
    Test sprawdzający działanie metody count_permissions_by_name
    w przypadku listy zawierającej niepoprawne wartości.
    """
    permissions = Permissions(setup_database)
    with pytest.raises(ValueError, match="Wszystkie elementy w permission_names muszą być ciągami znaków."):
        permissions.count_permissions_by_name([None, "zarzadzaj_wszystkimi_pacjentami"])
