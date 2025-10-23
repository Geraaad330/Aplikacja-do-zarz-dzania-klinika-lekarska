# test_integration_role_permissions.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.role_permissions_controller import RolePermissionsController
from controllers.roles_controller import RolesController
from controllers.permissions_controller import PermissionsController

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"


@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Konfiguracja testowej bazy danych dla testów RolePermissions.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "roles": RolesController(db_controller),
        "permissions": PermissionsController(db_controller),
        "role_permissions": RolePermissionsController(db_controller)
    }

    # Tworzenie tabel
    for controller in controllers.values():
        controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM role_permissions")
                db_controller.connection.execute("DELETE FROM roles")
                db_controller.connection.execute("DELETE FROM system_permissions")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()


# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_role_permissions.py

def test_add_role_permission_valid_data_by_id(setup_controllers):
    """
    Testuje poprawne dodanie rekordu korzystając z `role_id` i `permission_id`.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Admin")
    permissions_controller.add_permission("zarzadzaj_wizytami")

    role_id = roles_controller.get_role_by_column("role_name", "Admin")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Weryfikacja
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 1
    assert records[0]["role_id"] == role_id
    assert records[0]["permission_id"] == permission_id


def test_add_role_permission_valid_data_by_names(setup_controllers):
    """
    Testuje poprawne dodanie rekordu korzystając z nazw roli i uprawnienia.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Manager")
    permissions_controller.add_permission("zarzadzaj_wszystkimi_pacjentami")

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_names("Manager", "zarzadzaj_wszystkimi_pacjentami")

    # Weryfikacja
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 1
    assert records[0]["role_id"] == roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"]
    assert records[0]["permission_id"] == permissions_controller.filter_permissions(["zarzadzaj_wszystkimi_pacjentami"])[0]["permission_id"]


def test_add_role_permission_missing_data_by_id(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi korzystając z `role_id` i `permission_id`.
    """

    role_permissions_controller = setup_controllers["role_permissions"]


    with pytest.raises(ValueError, match="Błąd walidacji: Brakujące dane."):
        role_permissions_controller.add_role_permission_by_ids(1, None)


def test_add_role_permission_missing_data_by_names(setup_controllers):
    """
    Testuje próbę dodania rekordu z brakującymi danymi korzystając z nazw roli i uprawnienia.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba dodania rekordu bez nazwy uprawnienia
    with pytest.raises(ValueError, match="Błąd walidacji: Nazwa uprawnienia musi być ciągiem znaków."):
        role_permissions_controller.add_role_permission_by_names("Admin", None)


def test_add_role_permission_invalid_data_by_id(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi korzystając z `role_id` i `permission_id`.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba dodania rekordu z nieprawidłowym `permission_id`
    with pytest.raises(ValueError, match=r"Uprawnienie o ID 99 nie istnieje\."):
        role_permissions_controller.add_role_permission_by_ids(1, 99)


def test_add_role_permission_invalid_data_by_names(setup_controllers):
    """
    Testuje próbę dodania rekordu z nieprawidłowymi danymi korzystając z nazw roli i uprawnienia.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba dodania rekordu z nieprawidłową nazwą uprawnienia
    with pytest.raises(ValueError, match="Błąd walidacji: Rola 'Admin' nie istnieje."):
        role_permissions_controller.add_role_permission_by_names("Admin", "NieprawidlowaNazwa")


def test_add_role_permission_duplicate_data_by_id(setup_controllers):
    """
    Testuje próbę dodania rekordu z duplikatem korzystając z `role_id` i `permission_id`.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Editor")
    permissions_controller.add_permission("zarzadzaj_diagnozami")

    role_id = roles_controller.get_role_by_column("role_name", "Editor")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_diagnozami"])[0]["permission_id"]

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Próba dodania tego samego rekordu
    with pytest.raises(ValueError, match=r"Kombinacja rola=\d+ i uprawnienie=\d+ już istnieje\."):
        role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)


def test_add_role_permission_to_empty_database(setup_controllers):
    """
    Testuje próbę dodania rekordu do pustej bazy.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba dodania rekordu bez dodania ról i uprawnień
    with pytest.raises(ValueError, match=r"Błąd walidacji: Błąd walidacji: Uprawnienie o ID 1 nie istnieje."):
        role_permissions_controller.add_role_permission_by_ids(1, 1)


# +-+-+-+- Testy metod pobierania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_role_permissions.py

def test_get_role_permission_by_id(setup_controllers):
    """
    Testuje poprawne pobranie istniejącego rekordu korzystając z `role_permission_id`.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Admin")
    permissions_controller.add_permission("zarzadzaj_wizytami")

    role_id = roles_controller.get_role_by_column("role_name", "Admin")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Pobranie rekordu
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 1
    assert records[0]["role_id"] == role_id
    assert records[0]["permission_id"] == permission_id


def test_get_nonexistent_role_permission(setup_controllers):
    """
    Testuje próbę pobrania nieistniejącego rekordu.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba pobrania nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanych wartościach."):
        role_permissions_controller.get_role_permission_by_ids(9999, 9999)



def test_get_all_role_permissions(setup_controllers):
    """
    Testuje pobranie wszystkich rekordów z bazy.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Admin")
    permissions_controller.add_permission("zarzadzaj_wizytami")

    role_id = roles_controller.get_role_by_column("role_name", "Admin")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Pobranie wszystkich rekordów
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) > 0, "Nie pobrano rekordów, mimo że istnieją."


def test_get_all_role_permissions_empty_database(setup_controllers):
    """
    Testuje pobranie rekordów z pustej bazy.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Pobranie wszystkich rekordów
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 0, "Baza danych powinna być pusta."


def test_get_role_permissions_with_filters(setup_controllers):
    """
    Testuje pobranie rekordów z użyciem filtrów korzystając z `role_id` i `permission_id`.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Manager")
    permissions_controller.add_permission("zarzadzaj_wszystkimi_pacjentami")

    role_id = roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wszystkimi_pacjentami"])[0]["permission_id"]

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Pobranie rekordów z filtrem
    filters = [{"column": "role_id", "operator": "=", "value": role_id}]
    records = role_permissions_controller.get_all_role_permissions(filters=filters)
    assert len(records) == 1
    assert records[0]["role_id"] == role_id


def test_get_role_permissions_with_sorting(setup_controllers):
    """
    Testuje pobranie rekordów z sortowaniem.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("RoleA")
    roles_controller.add_role("RoleB")
    permissions_controller.add_permission("zarzadzaj_platnosciami")
    permissions_controller.add_permission("zarzadzaj_pomieszczeniami")

    role_id_a = roles_controller.get_role_by_column("role_name", "RoleA")[0]["role_id"]
    role_id_b = roles_controller.get_role_by_column("role_name", "RoleB")[0]["role_id"]
    permission_id_a = permissions_controller.filter_permissions(["zarzadzaj_platnosciami"])[0]["permission_id"]
    permission_id_b = permissions_controller.filter_permissions(["zarzadzaj_pomieszczeniami"])[0]["permission_id"]

    role_permissions_controller.add_role_permission_by_ids(role_id_a, permission_id_a)
    role_permissions_controller.add_role_permission_by_ids(role_id_b, permission_id_b)

    # Test sortowania
    sort_by = [{"column": "role_id", "direction": "DESC"}]
    records = role_permissions_controller.get_all_role_permissions(sort_by=sort_by)
    assert len(records) == 2
    assert records[0]["role_id"] == role_id_b  # Najpierw RoleB
    assert records[1]["role_id"] == role_id_a  # Potem RoleA


def test_get_role_and_permission_by_names(setup_controllers):
    """
    Testuje próbę pobrania ID i nazwy uprawnienia poprzez nazwy.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("User")
    permissions_controller.add_permission("zarzadzaj_uslugami")

    role = roles_controller.get_role_by_column("role_name", "User")[0]
    permission = permissions_controller.filter_permissions(["zarzadzaj_uslugami"])[0]

    # Weryfikacja
    assert role["role_name"] == "User"
    assert permission["permission_name"] == "zarzadzaj_uslugami"


def test_missing_dependency_between_tables(setup_controllers):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba dodania rekordu bez istniejącej roli lub uprawnienia
    with pytest.raises(ValueError, match="Błąd walidacji: Uprawnienie o ID 9999 nie istnieje."):
        role_permissions_controller.add_role_permission_by_ids(9999, 9999)


# +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_role_permissions.py

def test_update_role_permission_valid_data_by_names(setup_controllers):
    """
    Testuje poprawną aktualizację rekordu korzystając z nazw roli i uprawnienia.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("RoleOld")
    roles_controller.add_role("RoleNew")
    permissions_controller.add_permission("zarzadzaj_wizytami")
    permissions_controller.add_permission("zarzadzaj_wszystkimi_pacjentami")

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_names("RoleOld", "zarzadzaj_wizytami")

    # Aktualizacja danych
    role_permissions_controller.update_role_permission_by_names(
        role_permissions_controller.get_all_role_permissions()[0]["role_permission_id"],
        "RoleNew",
        "zarzadzaj_wszystkimi_pacjentami"
    )

    # Weryfikacja
    updated_record = role_permissions_controller.get_all_role_permissions()[0]
    assert updated_record["role_id"] == roles_controller.get_role_by_column("role_name", "RoleNew")[0]["role_id"]
    assert updated_record["permission_id"] == permissions_controller.filter_permissions(["zarzadzaj_wszystkimi_pacjentami"])[0]["permission_id"]


def test_update_role_permission_invalid_data_by_names(setup_controllers):
    """
    Testuje aktualizację rekordu z niepoprawnymi danymi korzystając z nazw roli i uprawnienia.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("RoleForInvalidUpdate")
    permissions_controller.add_permission("zarzadzaj_diagnozami")

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_names("RoleForInvalidUpdate", "zarzadzaj_diagnozami")

    # Próba aktualizacji z niepoprawnymi danymi
    with pytest.raises(ValueError, match="Błąd walidacji: Rola 'InvalidRoleName' nie istnieje."):
        role_permissions_controller.update_role_permission_by_names(
            role_permissions_controller.get_all_role_permissions()[0]["role_permission_id"],
            "InvalidRoleName",
            None
        )


def test_update_nonexistent_role_permission_by_names(setup_controllers):
    """
    Testuje próbę aktualizacji nieistniejącego rekordu korzystając z nazw.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba aktualizacji nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanym ID."):
        role_permissions_controller.update_role_permission_by_names(9999, "NonExistentRole", "NonExistentPermission")


def test_update_role_permission_with_no_data_by_names(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu bez podania danych korzystając z nazw.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("EmptyUpdateRole")
    permissions_controller.add_permission("przegladaj_recepty")

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_names("EmptyUpdateRole", "przegladaj_recepty")

    # Próba aktualizacji bez podania danych
    with pytest.raises(ValueError, match="Błąd walidacji: Nie podano żadnych wartości do aktualizacji."):
        role_permissions_controller.update_role_permission_by_names(
            role_permissions_controller.get_all_role_permissions()[0]["role_permission_id"],
            None,
            None
        )


def test_update_role_permission_unique_constraint_violation_by_names(setup_controllers):
    """
    Testuje próbę aktualizacji rekordu naruszającą ograniczenia unikalności korzystając z nazw.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Rola A")
    roles_controller.add_role("Rola B")
    permissions_controller.add_permission("zarzadzaj_diagnozami")
    permissions_controller.add_permission("zarzadzaj_uslugami")

    role_permissions_controller.add_role_permission_by_names("Rola A", "zarzadzaj_diagnozami")
    role_permissions_controller.add_role_permission_by_names("Rola B", "zarzadzaj_uslugami")

    role_permission_id = role_permissions_controller.get_all_role_permissions()[0]["role_permission_id"]

    # Próba aktualizacji naruszająca unikalność
    with pytest.raises(ValueError, match="Kombinacja rola='Rola B' i uprawnienie='zarzadzaj_uslugami' już istnieje."):
        role_permissions_controller.update_role_permission_by_names(
            role_permission_id,
            "Rola B",
            "zarzadzaj_uslugami"
        )




# +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# test_integration_role_permissions.py

def test_delete_role_permission_by_id(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z `role_permission_id`.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Admin")
    permissions_controller.add_permission("zarzadzaj_wizytami")

    role_id = roles_controller.get_role_by_column("role_name", "Admin")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Pobranie ID rekordu
    role_permission_id = role_permissions_controller.get_all_role_permissions()[0]["role_permission_id"]

    # Usunięcie rekordu
    role_permissions_controller.delete_role_permission_by_id(role_permission_id)

    # Weryfikacja
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_role_permission_by_names(setup_controllers):
    """
    Testuje poprawne usunięcie rekordu korzystając z nazw roli i uprawnienia.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # Dodanie danych testowych
    roles_controller.add_role("Manager")
    permissions_controller.add_permission("zarzadzaj_wszystkimi_pacjentami")

    # Dodanie rekordu
    role_permissions_controller.add_role_permission_by_names("Manager", "zarzadzaj_wszystkimi_pacjentami")

    # Usunięcie rekordu
    role_permissions_controller.delete_record_by_role_and_permission(
        roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"],
        permissions_controller.filter_permissions(["zarzadzaj_wszystkimi_pacjentami"])[0]["permission_id"]
    )

    # Weryfikacja
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 0, "Rekord nie został poprawnie usunięty."


def test_delete_nonexistent_role_permission_by_id(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z `role_permission_id`.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanym ID."):
        role_permissions_controller.delete_role_permission_by_id(9999)


def test_delete_nonexistent_role_permission_by_names(setup_controllers):
    """
    Testuje próbę usunięcia nieistniejącego rekordu korzystając z nazw roli i uprawnienia.
    """
    role_permissions_controller = setup_controllers["role_permissions"]

    # Ustawienie nieistniejących wartości
    role_id = -1
    permission_id = -1

    # Próba usunięcia nieistniejącego rekordu
    with pytest.raises(KeyError, match="Nie znaleziono rekordu o podanych wartościach."):
        role_permissions_controller.delete_record_by_role_and_permission(role_id, permission_id)




# +-+-+-+- Testy metod inne -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_database_connection_error_handling(setup_controllers):
    """
    Testuje obsługę błędów połączenia z bazą danych.
    """
    db_controller = setup_controllers["role_permissions"].db_controller
    role_permissions_controller = setup_controllers["role_permissions"]

    # Rozłączenie bazy danych
    db_controller.close_connection()

    # Próba wykonania operacji po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        role_permissions_controller.get_all_role_permissions()



def test_full_crud_flow(setup_controllers):
    """
    Testuje pełne przepływy danych CRUD między kontrolerem, walidacją, modelem i bazą danych.
    """
    roles_controller = setup_controllers["roles"]
    permissions_controller = setup_controllers["permissions"]
    role_permissions_controller = setup_controllers["role_permissions"]

    # 1. CREATE: Dodanie roli, uprawnienia i rekordu `role_permission`
    roles_controller.add_role("Developer")
    permissions_controller.add_permission("zarzadzaj_uslugami")

    role_id = roles_controller.get_role_by_column("role_name", "Developer")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_uslugami"])[0]["permission_id"]

    role_permissions_controller.add_role_permission_by_ids(role_id, permission_id)

    # Weryfikacja dodania
    records = role_permissions_controller.get_all_role_permissions()
    assert len(records) == 1
    assert records[0]["role_id"] == role_id
    assert records[0]["permission_id"] == permission_id

    # 2. READ: Pobranie danych za pomocą ID i nazw
    record_by_ids = role_permissions_controller.get_role_permission_by_ids(role_id, permission_id)
    assert record_by_ids is not None
    assert record_by_ids["role_id"] == role_id
    assert record_by_ids["permission_id"] == permission_id

    # Pobranie za pomocą nazw
    role_permission_by_names = role_permissions_controller.get_all_role_permissions(
        filters=[{"column": "role_id", "operator": "=", "value": role_id}]
    )
    assert len(role_permission_by_names) == 1
    assert role_permission_by_names[0]["role_id"] == role_id

    # 3. UPDATE: Aktualizacja roli i uprawnienia w `role_permission`
    roles_controller.add_role("Senior Developer")
    permissions_controller.add_permission("zarzadzaj_wizytami")

    new_role_id = roles_controller.get_role_by_column("role_name", "Senior Developer")[0]["role_id"]
    new_permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    role_permission_id = role_permissions_controller.get_all_role_permissions()[0]["role_permission_id"]
    role_permissions_controller.update_role_permission_by_ids(role_permission_id, new_role_id, new_permission_id)

    # Weryfikacja aktualizacji
    updated_record = role_permissions_controller.get_all_role_permissions()[0]
    assert updated_record["role_id"] == new_role_id
    assert updated_record["permission_id"] == new_permission_id

    # 4. DELETE: Usunięcie rekordu
    role_permissions_controller.delete_role_permission_by_id(role_permission_id)

    # Weryfikacja usunięcia
    records_after_delete = role_permissions_controller.get_all_role_permissions()
    assert len(records_after_delete) == 0, "Rekord nie został poprawnie usunięty."
