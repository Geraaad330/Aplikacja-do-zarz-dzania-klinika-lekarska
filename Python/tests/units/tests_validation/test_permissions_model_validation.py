# test_permissions_model_validation.py
# Testy dla permissions_model_validation.py

import pytest
from validators.permissions_model_validation import SystemPermissionsValidation


def test_validate_database_connection():
    """Testuje walidację połączenia z bazą danych."""
    class MockDBController:
        """Atrapa kontrolera bazy danych dla testów."""
        def __init__(self, connection):
            self.connection = connection

    # Poprawny przypadek
    db_controller = MockDBController(connection="connected")
    SystemPermissionsValidation.validate_database_connection(db_controller)

    # Brak połączenia
    db_controller = MockDBController(connection=None)
    with pytest.raises(RuntimeError, match="Brak aktywnego połączenia z bazą danych."):
        SystemPermissionsValidation.validate_database_connection(db_controller)


def test_validate_column_name():
    """Testuje walidację nazw kolumn."""
    valid_columns = ["permission_id", "permission_name"]

    # Poprawne kolumny
    SystemPermissionsValidation.validate_column_name("permission_id", valid_columns)
    SystemPermissionsValidation.validate_column_name("permission_name", valid_columns)

    # Niepoprawne kolumny
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna: invalid_column. Dozwolone kolumny: .*"):
        SystemPermissionsValidation.validate_column_name("invalid_column", valid_columns)


def test_validate_operator_and_value():
    """Testuje walidację operatora i wartości dla filtracji."""
    # Poprawne operatory i wartości
    SystemPermissionsValidation.validate_operator_and_value("LIKE", "%pacjent%")
    SystemPermissionsValidation.validate_operator_and_value("IN", ["Dodawanie pacjentów", "Edycja wizyt"])
    SystemPermissionsValidation.validate_operator_and_value("=", "Dodawanie pacjentów")

    # Nieobsługiwany operator
    with pytest.raises(ValueError, match="Nieobsługiwany operator: INVALID. Obsługiwane operatory: .*"):
        SystemPermissionsValidation.validate_operator_and_value("INVALID", "value")

    # Operator IN wymaga listy wartości
    with pytest.raises(ValueError, match="Operator 'IN' wymaga listy wartości."):
        SystemPermissionsValidation.validate_operator_and_value("IN", "Dodawanie pacjentów")


def test_validate_order_by():
    """Testuje walidację kolumny do sortowania."""
    valid_columns = ["permission_id", "permission_name"]

    # Poprawne kolumny
    SystemPermissionsValidation.validate_column_name("permission_id", valid_columns)
    SystemPermissionsValidation.validate_column_name("permission_name", valid_columns)

    # Niepoprawna kolumna
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna: invalid_column. Dozwolone kolumny: .*"):
        SystemPermissionsValidation.validate_column_name("invalid_column", valid_columns)


def test_validate_query_results():
    """Testuje walidację wyników zapytania."""
    # Poprawne wyniki
    results = [{"permission_id": 1, "permission_name": "Dodawanie pacjentów"}]
    SystemPermissionsValidation.validate_query_results(results)

    # Brak wyników
    with pytest.raises(ValueError, match="Zapytanie nie zwróciło żadnych wyników."):
        SystemPermissionsValidation.validate_query_results([])
