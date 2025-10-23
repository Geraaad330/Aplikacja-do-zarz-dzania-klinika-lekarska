# test_meeting_types_model_validation.py

import pytest
from validators.meeting_types_model_validation import (
    validate_meeting_type,
    validate_operator_and_value,
    validate_filters_and_sorting,
    validate_update_fields,
)


def test_validate_meeting_type():
    """Testuje walidację nazwy typu spotkania."""
    # Poprawne dane
    validate_meeting_type("Konsylium terapeutyczne")
    validate_meeting_type("Superwizja - Test (Zaawansowany)")
    validate_meeting_type("Szkolenie, wewnętrzne.")
    validate_meeting_type("Szkolenie: wewnętrzne")
    validate_meeting_type("Spotkanie zespołu interdyscyplinarnego")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa typu spotkania musi być ciągiem znaków."):
        validate_meeting_type(123)
    with pytest.raises(ValueError, match="Nazwa typu spotkania nie może być pusta."):
        validate_meeting_type("")
    with pytest.raises(ValueError, match="Nazwa typu spotkania musi mieć od 3 do 100 znaków."):
        validate_meeting_type("AB")
    with pytest.raises(ValueError, match="Nazwa typu spotkania musi mieć od 3 do 100 znaków."):
        validate_meeting_type("A" * 101)
    with pytest.raises(ValueError, match="Nazwa typu spotkania zawiera niedozwolone znaki."):
        validate_meeting_type("!@#$%^%&*")
    with pytest.raises(ValueError, match="Nazwa typu spotkania nie może zawierać cyfr."):
        validate_meeting_type("Szkolenie, wewnętrzne. 50")


def test_validate_operator_and_value():
    """Testuje walidację operatorów i wartości."""
    # Poprawne dane
    validate_operator_and_value("LIKE", "Specjalność%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", ["Konsylium terapeutyczne", "Superwizja"])
    validate_operator_and_value("=", "Szkolenie wewnętrzne")

    # Niepoprawne operatory
    with pytest.raises(ValueError, match="Nieobsługiwany operator: INVALID"):
        validate_operator_and_value("INVALID", "Wartość")
    
    # Niepoprawne wartości
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")
    with pytest.raises(ValueError, match="Operator 'BETWEEN' wymaga krotki zawierającej dwie wartości."):
        validate_operator_and_value("BETWEEN", (1,))
    with pytest.raises(ValueError, match="Wartość dla operatora IN musi być niepustą listą lub krotką."):
        validate_operator_and_value("IN", [])


def test_validate_filters_and_sorting():
    """Testuje walidację filtrów i sortowania."""
    valid_columns = ["meeting_type_id", "meeting_type"]
    
    # Poprawne dane
    validate_filters_and_sorting(
        filters=[{"column": "meeting_type", "operator": "LIKE", "value": "Supe%"}],
        sort_by=[("meeting_type", "ASC")],
        valid_columns=valid_columns,
    )
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters=[{"column": "meeting_type"}], sort_by=None, valid_columns=valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(
            filters=[{"column": "invalid_column", "operator": "=", "value": "Szkolenie wewnętrzne"}],
            sort_by=None,
            valid_columns=valid_columns,
        )
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna sortowania: invalid_column."):
        validate_filters_and_sorting(
            filters=None,
            sort_by=[("invalid_column", "ASC")],
            valid_columns=valid_columns,
        )


def test_validate_update_fields():
    """Testuje walidację pól aktualizacji."""
    valid_columns = ["meeting_type_id", "meeting_type"]
    
    # Poprawne dane
    validate_update_fields({"meeting_type": "Nowa specjalność"}, valid_columns)
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "Wartość"}, valid_columns)

