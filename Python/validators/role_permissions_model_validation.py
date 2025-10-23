# role_permissions_model_validation.py

import re
from controllers.roles_controller import RolesController
from controllers.permissions_controller import PermissionsController
from controllers.database_controller import DatabaseController


# +-+-+-+- Walidacja nazwy roli i uprawnienia -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_role_name(role_name: str) -> None:
    """
    Waliduje nazwę roli.

    :param role_name: Nazwa roli.
    :raises ValueError: Jeśli nazwa jest nieprawidłowa.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s():.,/_-]+$"
    if not isinstance(role_name, str):
        raise ValueError("Nazwa roli musi być ciągiem znaków.")
    if not role_name.strip():
        raise ValueError("Nazwa roli nie może być pusta.")
    if len(role_name) < 3 or len(role_name) > 100:
        raise ValueError("Nazwa roli musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, role_name):
        raise ValueError("Nazwa roli zawiera niedozwolone znaki.")


def validate_permission_name(permission_name: str) -> None:
    """
    Waliduje nazwę uprawnienia.

    :param permission_name: Nazwa uprawnienia.
    :raises ValueError: Jeśli nazwa jest nieprawidłowa.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s():.,/_-]+$"
    if not isinstance(permission_name, str):
        raise ValueError("Nazwa uprawnienia musi być ciągiem znaków.")
    if not permission_name.strip():
        raise ValueError("Nazwa uprawnienia nie może być pusta.")
    if len(permission_name) < 3 or len(permission_name) > 100:
        raise ValueError("Nazwa uprawnienia musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, permission_name):
        raise ValueError("Nazwa uprawnienia zawiera niedozwolone znaki.")


# +-+-+-+- Walidacja istnienia rekordów w tabelach -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_role_exists(roles_controller: RolesController, role_name: str) -> None:
    """
    Sprawdza, czy rola istnieje w tabeli `roles`.

    :param roles_controller: Kontroler ról.
    :param role_name: Nazwa roli.
    :raises ValueError: Jeśli rola nie istnieje.
    """
    results = roles_controller.get_role_by_column("role_name", role_name)
    if not results:
        raise ValueError(f"Rola '{role_name}' nie istnieje.")


def validate_permission_exists(permissions_controller: PermissionsController, permission_name: str) -> None:
    """
    Sprawdza, czy uprawnienie istnieje w tabeli `system_permissions`.

    :param permissions_controller: Kontroler uprawnień.
    :param permission_name: Nazwa uprawnienia.
    :raises ValueError: Jeśli uprawnienie nie istnieje.
    """
    results = permissions_controller.filter_permissions(permission_names=[permission_name])
    if not results:
        raise ValueError(f"Uprawnienie '{permission_name}' nie istnieje.")


def validate_role_id_exists(roles_controller: RolesController, role_id: int) -> None:
    """
    Sprawdza, czy `role_id` istnieje w tabeli `roles`.

    :param roles_controller: Kontroler ról.
    :param role_id: ID roli.
    :raises ValueError: Jeśli rola nie istnieje.
    """
    if not role_id:
        raise ValueError("Brakujące dane: role_id jest wymagane.")
    results = roles_controller.get_role_by_column("role_id", role_id)
    if not results:
        raise ValueError(f"Rola o ID {role_id} nie istnieje.")


def validate_permission_id_exists(permissions_controller: PermissionsController, permission_id: int) -> None:
    """
    Sprawdza, czy `permission_id` istnieje w tabeli `system_permissions`.

    :param permissions_controller: Kontroler uprawnień.
    :param permission_id: ID uprawnienia.
    :raises ValueError: Jeśli uprawnienie nie istnieje.
    """
    # Pobierz wszystkie uprawnienia
    all_permissions = permissions_controller.permissions_model.get_all_permissions()

    # Sprawdź, czy ID znajduje się w wynikach
    if not any(permission["permission_id"] == permission_id for permission in all_permissions):
        raise ValueError(f"Uprawnienie o ID {permission_id} nie istnieje.")



# +-+-+-+- Walidacja unikalności kombinacji -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_unique_role_permission(db_controller: DatabaseController, role_id: int, permission_id: int) -> None:
    """
    Waliduje unikalność kombinacji `role_id` i `permission_id`.

    :param db_controller: Kontroler bazy danych.
    :param role_id: ID roli.
    :param permission_id: ID uprawnienia.
    :raises ValueError: Jeśli kombinacja jest już w tabeli.
    """
    query = """
    SELECT COUNT(*) FROM role_permissions
    WHERE role_id = ? AND permission_id = ?
    """
    cursor = db_controller.connection.execute(query, (role_id, permission_id))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Kombinacja rola={role_id} i uprawnienie={permission_id} już istnieje.")


def validate_unique_role_permission_by_names(
    db_controller: DatabaseController,
    roles_controller: RolesController,
    permissions_controller: PermissionsController,
    role_name: str,
    permission_name: str,
) -> None:
    """
    Sprawdza unikalność rekordu na podstawie nazwy roli i uprawnienia.

    :param db_controller: Kontroler bazy danych.
    :param roles_controller: Kontroler ról.
    :param permissions_controller: Kontroler uprawnień.
    :param role_name: Nazwa roli.
    :param permission_name: Nazwa uprawnienia.
    :raises ValueError: Jeśli kombinacja już istnieje.
    """
    validate_role_name(role_name)
    validate_permission_name(permission_name)

    role_id = roles_controller.get_role_by_column("role_name", role_name)[0]["role_id"]
    permission_id = permissions_controller.filter_permissions(permission_names=[permission_name])[0]["permission_id"]

    validate_unique_role_permission(db_controller, role_id, permission_id)

# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def validate_operator_and_value(operator: str, value=None):
    """
    Waliduje operator i wartość w zapytaniach SQL.

    :param operator: Operator SQL (np. "=", "LIKE").
    :param value: Wartość przypisana operatorowi.
    :raises ValueError: Jeśli operator lub wartość są nieprawidłowe.
    """
    valid_operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN", "IS NULL", "IS NOT NULL"]

    if operator not in valid_operators:
        raise ValueError(f"Nieobsługiwany operator: {operator}.")

    if operator == "LIKE" and (not isinstance(value, str) or not value.strip()):
        raise ValueError("Wartość dla operatora LIKE musi być niepustym ciągiem znaków.")

    if operator == "BETWEEN" and not (isinstance(value, tuple) and len(value) == 2):
        raise ValueError("Operator BETWEEN wymaga krotki zawierającej dwie wartości.")

    if operator == "IN" and not (isinstance(value, (list, tuple)) and len(value) > 0):
        raise ValueError("Wartość dla operatora IN musi być niepustą listą lub krotką.")

    if operator in ["IS NULL", "IS NOT NULL"] and value is not None:
        raise ValueError(f"Operator {operator} nie wymaga przypisanej wartości.")


def validate_filters_and_sorting(filters, sort_by, valid_columns):
    """
    Waliduje filtry i sortowanie używane w zapytaniach SQL.

    :param filters: Lista słowników reprezentujących filtry, gdzie każdy słownik powinien zawierać klucze:
        - "column" (str): Nazwa kolumny, na której zastosowany jest filtr.
        - "operator" (str): Operator SQL (np. '=', 'LIKE', 'IN', 'BETWEEN', 'IS NULL').
        - "value" (opcjonalny): Wartość przypisana do operatora, wymagana dla większości operatorów.
    :param sort_by: Lista krotek reprezentujących sortowanie, gdzie każda krotka zawiera:
        - Nazwa kolumny do sortowania.
        - Kierunek sortowania ('ASC' lub 'DESC').
    :param valid_columns: Lista dozwolonych kolumn (str) w zapytaniach SQL.
    :raises ValueError: Jeśli:
        - Filtr zawiera nieprawidłową kolumnę.
        - Filtr używa nieprawidłowego operatora lub niewłaściwej wartości dla operatora.
        - Sortowanie używa nieprawidłowej kolumny lub kierunku.

    :return: None
    """
    if filters:
        for filter_item in filters:
            if not all(key in filter_item for key in ["column", "operator", "value"]):
                raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")
            if filter_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if filter_item["operator"] not in ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN", "IS NULL", "IS NOT NULL"]:
                raise ValueError(f"Nieprawidłowy operator w filtrze: {filter_item['operator']}.")

    if sort_by:
        for sort_item in sort_by:
            if "column" not in sort_item or "direction" not in sort_item:
                raise ValueError("Każde sortowanie musi zawierać klucze: 'column' i 'direction'.")
            if sort_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w sortowaniu: {sort_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if sort_item["direction"].upper() not in ["ASC", "DESC"]:
                raise ValueError(f"Nieprawidłowy kierunek sortowania: {sort_item['direction']}. Dozwolone wartości: 'ASC', 'DESC'.")


def handle_database_error(db_controller, query: str, params: tuple):
    """
    Obsługuje błędy bazy danych i zgłasza bardziej czytelne komunikaty.

    :param db_controller: Kontroler bazy danych.
    :param query: Zapytanie SQL.
    :param params: Parametry zapytania SQL.
    :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
    """
    try:
        return db_controller.connection.execute(query, params)
    except Exception as e:
        raise RuntimeError(f"Błąd podczas wykonywania zapytania: {query}. Szczegóły: {str(e)}") from e