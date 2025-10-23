# assigned_patients_model_validation.py

import re
# from controllers.database_controller import DatabaseController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.patients_controller import PatientController

# +-+-+-+- Walidacja nazw -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_name(name: str) -> None:
    """
    Waliduje imię lub nazwisko pacjenta.

    :param name: Imię lub nazwisko.
    :raises ValueError: Jeśli nazwa jest nieprawidłowa.
    """
    pattern = r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż\s]+$"
    if not isinstance(name, str):
        raise ValueError("Nazwa musi być ciągiem znaków.")
    if not name.strip():
        raise ValueError("Nazwa nie może być pusta.")
    if len(name) < 3 or len(name) > 100:
        raise ValueError("Nazwa musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, name):
        raise ValueError("Nazwa zawiera niedozwolone znaki.")

def validate_user_name(username: str) -> None:
    """
    Waliduje nazwę użytkownika.

    :param username: Nazwa użytkownika.
    :raises ValueError: Jeśli nazwa jest nieprawidłowa.
    """
    pattern = r"^[a-z0-9\.\-_]+$"
    if not isinstance(username, str):
        raise ValueError("Nazwa użytkownika musi być ciągiem znaków.")
    if not username.strip():
        raise ValueError("Nazwa użytkownika nie może być pusta.")
    if len(username) < 3 or len(username) > 100:
        raise ValueError("Nazwa użytkownika musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, username):
        raise ValueError("Nazwa użytkownika zawiera niedozwolone znaki.")

# +-+-+-+- Walidacja istnienia rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_patient_exists(patient_controller: PatientController, first_name: str, last_name: str) -> None:
    """
    Sprawdza, czy pacjent istnieje w tabeli `patients`.

    :param patient_controller: Kontroler pacjentów.
    :param first_name: Imię pacjenta.
    :param last_name: Nazwisko pacjenta.
    :raises ValueError: Jeśli pacjent nie istnieje.
    """
    results = patient_controller.advanced_filter_patients(first_name=first_name, last_name=last_name)
    if not results:
        raise ValueError(f"Pacjent '{first_name} {last_name}' nie istnieje.")

def validate_user_exists(users_accounts_controller: UsersAccountsController, username: str) -> None:
    """
    Sprawdza, czy użytkownik istnieje w tabeli `users_accounts`.

    :param users_accounts_controller: Kontroler użytkowników.
    :param username: Nazwa użytkownika.
    :raises ValueError: Jeśli użytkownik nie istnieje.
    """
    results = users_accounts_controller.get_users_with_filters(filters=[{"column": "username", "operator": "=", "value": username}])
    if not results:
        raise ValueError(f"Użytkownik '{username}' nie istnieje.")

# +-+-+-+- Walidacja unikalności kombinacji -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# def validate_unique_assignment(db_controller: DatabaseController, fk_patient_id: int, fk_user_id: int) -> None:
#     """
#     Waliduje unikalność kombinacji `fk_patient_id` i `fk_user_id`.

#     :param db_controller: Kontroler bazy danych.
#     :param fk_patient_id: ID pacjenta.
#     :param fk_user_id: ID użytkownika.
#     :raises ValueError: Jeśli kombinacja jest już w tabeli.
#     """
#     query = """
#     SELECT COUNT(*) FROM assigned_patients
#     WHERE fk_patient_id = ? AND fk_user_id = ?
#     """
#     cursor = db_controller.connection.execute(query, (fk_patient_id, fk_user_id))
#     if cursor.fetchone()[0] > 0:
#         raise ValueError(f"Kombinacja pacjent_id={fk_patient_id} i user_id={fk_user_id} już istnieje.")

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

def validate_filters_and_sorting(filters, sort_by, valid_columns, alias_map=None):
    """
    Waliduje filtry i sortowanie używane w zapytaniach SQL.
    """
    if alias_map is None:
        alias_map = {}

    if filters:
        for filter_item in filters:
            if not all(key in filter_item for key in ["column", "operator", "value"]):
                raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")

            column = filter_item["column"]
            # Zastosowanie alias_map do zamiany aliasów na rzeczywiste kolumny
            column = alias_map.get(column, column)

            if column not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna: {filter_item['column']}")

            # Walidacja operatora i wartości
            validate_operator_and_value(filter_item["operator"], filter_item["value"])

    if sort_by:
        for sort_item in sort_by:
            column = sort_item["column"]
            # Zastosowanie alias_map do zamiany aliasów na rzeczywiste kolumny
            column = alias_map.get(column, column)

            if column not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna do sortowania: {sort_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if sort_item["direction"].upper() not in ["ASC", "DESC"]:
                raise ValueError("Sortowanie musi używać 'ASC' lub 'DESC'.")




