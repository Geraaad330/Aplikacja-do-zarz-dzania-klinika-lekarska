# test_role_permissions_model_validation.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.roles_controller import RolesController
from controllers.permissions_controller import PermissionsController
from models.role_permissions import RolePermissions
from validators.role_permissions_model_validation import (
    validate_role_name,
    validate_permission_name,
    validate_role_exists,
    validate_permission_exists,
    validate_role_id_exists,
    validate_permission_id_exists,
    validate_unique_role_permission,
    validate_unique_role_permission_by_names,
)

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Fixture do konfiguracji bazy danych testowej.
    Tworzy tabele i zapewnia środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabel
    roles_controller = RolesController(db_controller)
    permissions_controller = PermissionsController(db_controller)
    roles_controller.create_table()
    permissions_controller.create_table()

    roles_permissions = RolePermissions(db_controller)
    roles_permissions.create_table()

    yield db_controller, roles_controller, permissions_controller

    # Czyszczenie bazy danych
    with db_controller.connection:
        db_controller.connection.execute("DELETE FROM roles")
        db_controller.connection.execute("DELETE FROM system_permissions")
        db_controller.connection.execute("DELETE FROM role_permissions")
    db_controller.close_connection()


def test_validate_role_name():
    """
    Testuje walidację poprawności nazw ról.
    """
    # Poprawna nazwa
    validate_role_name("Admin")
    validate_role_name("Admin_żółty")
    validate_role_name("Admin:dupa.")
    validate_role_name("Admin/ noob(-)")

    # Złe dane
    with pytest.raises(ValueError, match="Nazwa roli musi być ciągiem znaków."):
        validate_role_name(123)
    with pytest.raises(ValueError, match="Nazwa roli nie może być pusta."):
        validate_role_name("")
    with pytest.raises(ValueError, match="Nazwa roli musi mieć od 3 do 100 znaków."):
        validate_role_name("A")
    with pytest.raises(ValueError, match="Nazwa roli zawiera niedozwolone znaki."):
        validate_role_name("Role123!")


def test_validate_permission_name():
    """
    Testuje walidację poprawności nazw uprawnień.
    """
    # Poprawna nazwa
    validate_permission_name("zarzadzaj_wszystkimi_pacjentami")
    validate_permission_name("Przegladaj_przypisanych_pacjentow")
    validate_permission_name("Zarzadzaj-wszystkimi:pacjentam,i.")
    validate_permission_name("Przegladaj_przypisanych_pacjentow()")

    # Złe dane
    with pytest.raises(ValueError, match="Nazwa uprawnienia musi być ciągiem znaków."):
        validate_permission_name(123)
    with pytest.raises(ValueError, match="Nazwa uprawnienia nie może być pusta."):
        validate_permission_name("")
    with pytest.raises(ValueError, match="Nazwa uprawnienia musi mieć od 3 do 100 znaków."):
        validate_permission_name("R")
    with pytest.raises(ValueError, match="Nazwa uprawnienia zawiera niedozwolone znaki."):
        validate_permission_name("zarzadzaj_wszystkimi_pacjentami123!")


def test_validate_role_exists(setup_controllers):
    """
    Testuje, czy walidacja poprawnie wykrywa istniejącą rolę.
    """
    _, roles_controller, _ = setup_controllers
    roles_controller.add_role("Admin")

    # Poprawna walidacja
    validate_role_exists(roles_controller, "Admin")

    # Złe dane
    with pytest.raises(ValueError, match="Rola 'User' nie istnieje."):
        validate_role_exists(roles_controller, "User")


def test_validate_permission_exists(setup_controllers):
    """
    Testuje, czy walidacja poprawnie wykrywa istniejące uprawnienie.
    """
    _, _, permissions_controller = setup_controllers
    permissions_controller.permissions_model.add_permission("zarzadzaj_wszystkimi_pacjentami")

    # Poprawna walidacja
    validate_permission_exists(permissions_controller, "zarzadzaj_wszystkimi_pacjentami")

    # Złe dane
    with pytest.raises(ValueError, match="Uprawnienie 'zarzadzaj_wizytami' nie istnieje."):
        validate_permission_exists(permissions_controller, "zarzadzaj_wizytami")


def test_validate_role_id_exists(setup_controllers):
    """
    Testuje, czy walidacja poprawnie wykrywa istniejące ID roli.
    """
    _, roles_controller, _ = setup_controllers
    roles_controller.add_role("Manager")
    role_id = roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"]

    # Poprawna walidacja
    validate_role_id_exists(roles_controller, role_id)

    # Złe dane
    with pytest.raises(ValueError, match="Rola o ID 999 nie istnieje."):
        validate_role_id_exists(roles_controller, 999)


def test_validate_permission_id_exists(setup_controllers):
    """
    Testuje, czy walidacja poprawnie wykrywa istniejące ID uprawnienia.
    """
    _, _, permissions_controller = setup_controllers
    permissions_controller.permissions_model.add_permission("zarzadzaj_wizytami")
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    # Poprawna walidacja
    validate_permission_id_exists(permissions_controller, permission_id)

    # Złe dane
    with pytest.raises(ValueError, match="Uprawnienie o ID 999 nie istnieje."):
        validate_permission_id_exists(permissions_controller, 999)


def test_validate_unique_role_permission(setup_controllers):
    """
    Testuje unikalność kombinacji role_id i permission_id.
    """
    db_controller, roles_controller, permissions_controller = setup_controllers
    roles_controller.add_role("Editor")
    permissions_controller.permissions_model.add_permission("zarzadzaj_wizytami")

    role_id = roles_controller.get_role_by_column("role_name", "Editor")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(["zarzadzaj_wizytami"])[0]["permission_id"]

    db_controller.connection.execute(
        "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, permission_id)
    )

    # Duplikat
    with pytest.raises(ValueError, match="Kombinacja rola=.+ i uprawnienie=.+ już istnieje."):
        validate_unique_role_permission(db_controller, role_id, permission_id)


def test_validate_unique_role_permission_by_names(setup_controllers):
    """
    Testuje unikalność kombinacji na podstawie nazw ról i uprawnień.
    """
    db_controller, roles_controller, permissions_controller = setup_controllers
    roles_controller.add_role("Viewer")
    permissions_controller.permissions_model.add_permission("przegladaj_diagnozy")

    validate_unique_role_permission_by_names(
        db_controller, roles_controller, permissions_controller, "Viewer", "przegladaj_diagnozy"
    )

    db_controller.connection.execute(
        "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
        (
            roles_controller.get_role_by_column("role_name", "Viewer")[0]["role_id"],
            permissions_controller.filter_permissions(["przegladaj_diagnozy"])[0]["permission_id"],
        ),
    )

    with pytest.raises(ValueError, match="Kombinacja rola=.+ i uprawnienie=.+ już istnieje."):
        validate_unique_role_permission_by_names(
            db_controller, roles_controller, permissions_controller, "Viewer", "przegladaj_diagnozy"
        )
