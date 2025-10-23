# test_roles_model_validation.py
# Testy dla roles_model_validation.py

import pytest
from validators.roles_model_validation import (
    validate_role_name,
    validate_column_name,
    validate_operator_and_value,
    validate_sorting,
    validate_record_existence,
    validate_update_fields,
    validate_count_like_pattern,
    validate_unique_role_name
)

class MockDBController:
    """Atrapa kontrolera bazy danych dla testów."""
    def __init__(self):
        self.connection = self.MockConnection()

    class MockConnection:
        """Atrapa połączenia z bazą danych."""
        def execute(self, query, params):
            if "role_name" in query and params == ("existing_role",):
                return MockDBController.MockCursor(1)  # Symulacja istnienia rekordu
            if "role_name" in query and params == ("Admin",):
                return MockDBController.MockCursor(1)  # Symulacja istniejącej roli
            return MockDBController.MockCursor(0)  # Symulacja braku rekordu

    class MockCursor:
        """Atrapa kursora dla testów."""
        def __init__(self, count):
            self.count = count

        def fetchone(self):
            return [self.count]


def test_validate_role_name():
    """Testuje walidację pola `role_name`."""
    # Poprawne dane
    validate_role_name("Administrator")
    validate_role_name("Psychiatra")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="role_name musi być ciągiem znaków."):
        validate_role_name(123)
    with pytest.raises(ValueError, match="role_name nie może być pusty."):
        validate_role_name("   ")
    with pytest.raises(ValueError, match="role_name musi mieć długość od 3 do 50 znaków."):
        validate_role_name("Ad")
    with pytest.raises(ValueError, match="role_name może zawierać tylko litery \\(w tym polskie znaki\\)."):
        validate_role_name("Admin!@#")

def test_validate_column_name():
    """Testuje walidację kolumny."""
    valid_columns = ["role_id", "role_name", "created_at"]

    # Poprawne kolumny
    validate_column_name("role_id", valid_columns)
    validate_column_name("role_name", valid_columns)

    # Niepoprawna kolumna
    with pytest.raises(ValueError, match="Kolumna 'invalid_column' nie jest prawidłowa."):
        validate_column_name("invalid_column", valid_columns)

def test_validate_operator_and_value():
    """Testuje walidację operatora i wartości."""
    # Poprawne przypadki
    validate_operator_and_value("LIKE", "%Admin%")
    validate_operator_and_value("IN", ["Admin", "User"])

    # Niepoprawne operatory i wartości
    with pytest.raises(ValueError, match="Obsługiwane operatory to 'LIKE' oraz 'IN'."):
        validate_operator_and_value("INVALID_OPERATOR", "%Admin%")

def test_validate_sorting():
    """Testuje walidację sortowania kolumny."""
    valid_columns = ["role_id", "role_name", "created_at"]

    # Poprawna kolumna
    validate_sorting("role_id", valid_columns)

    # Niepoprawna kolumna
    with pytest.raises(ValueError, match="Kolumna 'invalid_column' nie jest prawidłowa."):
        validate_sorting("invalid_column", valid_columns)

def test_validate_record_existence():
    """Testuje walidację istnienia rekordu w bazie danych."""
    db_controller = MockDBController()

    # Rekord istnieje
    validate_record_existence(db_controller, "roles", "role_name", "existing_role")

    # Rekord nie istnieje
    with pytest.raises(ValueError, match="Rekord z role_name = non_existing_role nie istnieje w tabeli roles."):
        validate_record_existence(db_controller, "roles", "role_name", "non_existing_role")


    # Rekord istnieje
    validate_record_existence(db_controller, "roles", "role_name", "existing_role")

    # Rekord nie istnieje
    with pytest.raises(ValueError, match="Rekord z role_name = non_existing_role nie istnieje w tabeli roles."):
        validate_record_existence(db_controller, "roles", "role_name", "non_existing_role")


    # Rekord istnieje
    validate_record_existence(db_controller, "roles", "role_name", "existing_role")

    # Rekord nie istnieje
    with pytest.raises(ValueError, match="Rekord z role_name = non_existing_role nie istnieje w tabeli roles."):
        validate_record_existence(db_controller, "roles", "role_name", "non_existing_role")

def test_validate_update_fields():
    """Testuje walidację pól do aktualizacji."""
    valid_columns = ["role_id", "role_name"]

    # Poprawne dane
    validate_update_fields({"role_name": "Admin"}, valid_columns)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna: invalid_field."):
        validate_update_fields({"invalid_field": "value"}, valid_columns)



def test_validate_count_like_pattern():
    """Testuje walidację wzorca LIKE."""
    # Poprawny wzorzec
    validate_count_like_pattern("%Admin%")

    # Niepoprawny wzorzec
    with pytest.raises(ValueError, match="Wzorzec LIKE zawiera niedozwolone znaki."):
        validate_count_like_pattern("Admin;")

def test_validate_unique_role_name():
    """Testuje walidację unikalności nazwy roli."""
    db_controller = MockDBController()

    # Unikalna nazwa roli
    validate_unique_role_name(db_controller, "UniqueRole")

    # Nieunikalna nazwa roli
    with pytest.raises(ValueError, match="Nazwa roli 'Admin' już istnieje w bazie danych."):
        validate_unique_role_name(db_controller, "Admin")


    # Unikalna nazwa roli
    validate_unique_role_name(db_controller, "UniqueRole")

    # Nieunikalna nazwa roli
    with pytest.raises(ValueError, match="Nazwa roli 'Admin' już istnieje w bazie danych."):
        validate_unique_role_name(db_controller, "Admin")



def test_validate_operator_and_value_empty_like_pattern():
    """Testuje walidację operatora LIKE z pustym wzorcem."""
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")



def test_validate_operator_and_value_unexpected_types():
    """Testuje walidację operatorów z nieoczekiwanymi typami danych."""
    # Operator LIKE z nieciągiem znaków
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", 12345)

    # Operator IN z niewłaściwym typem danych
    with pytest.raises(ValueError, match="Lista wartości dla operatora IN nie może być pusta."):
        validate_operator_and_value("IN", "Dodawanie pacjentów")



def test_validate_operator_and_value_empty_list():
    """Testuje walidację operatora IN z pustą listą."""
    with pytest.raises(ValueError, match="Lista wartości dla operatora IN nie może być pusta."):
        validate_operator_and_value("IN", [])




def test_validate_operator_and_value_none_values():
    """Testuje walidację operatorów z wartością None."""
    # Operator LIKE z None
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", None)

    # Operator IN z None jako wartość
    with pytest.raises(ValueError, match="Lista wartości dla operatora IN nie może być pusta."):
        validate_operator_and_value("IN", None)
