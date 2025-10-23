# pylint: disable=all

# test_model_role_permissions.py

import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.roles_controller import RolesController
from controllers.permissions_controller import PermissionsController
from models.role_permissions import RolePermissions


os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database():
    """
    Konfiguracja testowej bazy danych SQLite.
    """

    db_controller = DatabaseController()
    db_controller.connect_to_database()

    roles_controller = RolesController(db_controller)
    roles_controller.create_table()

    permissions_controller = PermissionsController(db_controller)
    permissions_controller.create_table()

    role_permissions = RolePermissions(db_controller)
    role_permissions.create_table()


    
    yield db_controller, roles_controller, permissions_controller, role_permissions

    # Czyszczenie danych po testach
    db_controller.connection.execute("DELETE FROM role_permissions")
    db_controller.connection.execute("DELETE FROM roles")
    db_controller.connection.execute("DELETE FROM system_permissions")
    db_controller.connection.commit()
    db_controller.close_connection()


def test_add_role_permission_by_ids(setup_database):
    """
    Testuje dodawanie uprawnienia na podstawie ID roli i ID uprawnienia.
    """
    db_controller, roles_controller, permissions_controller, role_permissions = setup_database

    # Dodaj role i uprawnienia
    roles_controller.add_role("Admin")
    permissions_controller.add_permission("ManageUsers")

    role_id = roles_controller.get_role_by_column("role_name", "Admin")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(permission_names=["ManageUsers"])[0]["permission_id"]

    # Dodaj uprawnienie
    role_permissions.add_role_permission_by_ids(role_id, permission_id)

    # Sprawdź poprawność dodania
    records = role_permissions.get_all_role_permissions()
    assert len(records) == 1
    assert records[0]["role_id"] == role_id
    assert records[0]["permission_id"] == permission_id


def test_add_role_permission_duplicate(setup_database):
    """
    Testuje, czy nie można dodać duplikatów dla tej samej roli i uprawnienia.
    """
    db_controller, roles_controller, permissions_controller, role_permissions = setup_database

    role_id = roles_controller.get_role_by_column("role_name", "Admin")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(permission_names=["ManageUsers"])[0]["permission_id"]

    with pytest.raises(ValueError, match="Kombinacja rola=.* i uprawnienie=.* już istnieje."):
        role_permissions.add_role_permission_by_ids(role_id, permission_id)


def test_delete_role_permission_by_id(setup_database):
    """
    Testuje usuwanie rekordu na podstawie `role_permission_id`.
    """
    db_controller, roles_controller, permissions_controller, role_permissions = setup_database

    # Dodaj dane
    roles_controller.add_role("User")
    permissions_controller.add_permission("ViewReports")

    role_id = roles_controller.get_role_by_column("role_name", "User")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(permission_names=["ViewReports"])[0]["permission_id"]

    role_permissions.add_role_permission_by_ids(role_id, permission_id)
    role_permission_id = role_permissions.get_all_role_permissions()[0]["role_permission_id"]

    # Usuń rekord
    role_permissions.delete_role_permission_by_id(role_permission_id)

    # Sprawdź, czy rekord został usunięty
    records = role_permissions.get_all_role_permissions()
    assert len(records) == 0


def test_get_records_with_filters(setup_database):
    """
    Testuje pobieranie rekordów z filtrami.
    """
    db_controller, roles_controller, permissions_controller, role_permissions = setup_database

    # Dodaj dane
    roles_controller.add_role("Manager")
    permissions_controller.add_permission("EditData")

    role_id = roles_controller.get_role_by_column("role_name", "Manager")[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(permission_names=["EditData"])[0]["permission_id"]

    role_permissions.add_role_permission_by_ids(role_id, permission_id)

    # Pobierz z filtrami
    filters = [{"column": "role_id", "operator": "=", "value": role_id}]
    records = role_permissions.get_records_with_filters(filters=filters)

    assert len(records) == 1
    assert records[0]["role_id"] == role_id
    assert records[0]["permission_id"] == permission_id


@pytest.mark.parametrize("invalid_role_name", ["", "x", "a" * 101, "Role123!"])
def test_invalid_role_name(setup_database, invalid_role_name):
    """
    Testuje walidację nazw ról.
    """
    db_controller, roles_controller, permissions_controller, role_permissions = setup_database

    with pytest.raises(ValueError, match="Nazwa roli .* nie jest poprawna."):
        roles_controller.add_role(invalid_role_name)


def test_cleanup(setup_database):
    """
    Testuje czyszczenie danych po testach.
    """
    db_controller, roles_controller, permissions_controller, role_permissions = setup_database

    role_permissions.get_all_role_permissions()
    roles_controller.get_all_roles()
    permissions_controller.get_all_permissions()

    db_controller.connection.execute("DELETE FROM role_permissions")
    db_controller.connection.execute("DELETE FROM roles")
    db_controller.connection.execute("DELETE FROM system_permissions")
    db_controller.connection.commit()

    assert role_permissions.get_all_role_permissions() == []
    assert roles_controller.get_all_roles() == []
    assert permissions_controller.get_all_permissions() == []
