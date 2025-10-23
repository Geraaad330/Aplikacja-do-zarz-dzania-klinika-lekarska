# test_specialties_model_validation.py

import pytest
from validators.specialties_model_validation import (
    validate_specialty_name,
    validate_operator_and_value,
    validate_filters_and_sorting,
    validate_profession,
    validate_update_fields,
    validate_column_name,
)


def test_validate_specialty_name():
    """Testuje walidację nazwy specjalności."""
    # Poprawne dane
    validate_specialty_name("Psychiatra dorosłych")
    validate_specialty_name("Specjalność - Test (Zaawansowany)")
    validate_specialty_name("Specjalność: Dietetyk")
    validate_specialty_name("Psychiatra dzieci, młodzieży.")
    validate_specialty_name("Terapia poznawczo behawioralna /CBT)")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa specjalności musi być ciągiem znaków."):
        validate_specialty_name(123)
    with pytest.raises(ValueError, match="Nazwa specjalności nie może być pusta."):
        validate_specialty_name("")
    with pytest.raises(ValueError, match="Nazwa specjalności musi mieć od 3 do 100 znaków."):
        validate_specialty_name("AB")
    with pytest.raises(ValueError, match="Nazwa specjalności musi mieć od 3 do 100 znaków."):
        validate_specialty_name("A" * 101)
    with pytest.raises(ValueError, match="Nazwa specjalności zawiera niedozwolone znaki."):
        validate_specialty_name("!@#$%^&*")
    with pytest.raises(ValueError, match="Nazwa specjalności zawiera niedozwolone znaki."):
        validate_specialty_name("Dietetyk 50%")  # Zawiera cyfry


def test_validate_operator_and_value():
    """Testuje walidację operatorów i wartości."""
    # Poprawne dane
    validate_operator_and_value("LIKE", "Specjalność%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", ["Specjalność A", "Specjalność B"])
    validate_operator_and_value("=", "Psychiatra")

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
    valid_columns = ["specialty_id", "specialty_name"]
    
    # Poprawne dane
    validate_filters_and_sorting(
        filters=[{"column": "specialty_name", "operator": "LIKE", "value": "Psych%"}],
        sort_by=[("specialty_name", "ASC")],
        valid_columns=valid_columns,
    )
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters=[{"column": "specialty_name"}], sort_by=None, valid_columns=valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(
            filters=[{"column": "invalid_column", "operator": "=", "value": "Psychiatra"}],
            sort_by=None,
            valid_columns=valid_columns,
        )
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna sortowania: invalid_column."):
        validate_filters_and_sorting(
            filters=None,
            sort_by=[("invalid_column", "ASC")],
            valid_columns=valid_columns,
        )


def test_validate_profession():
    """Testuje walidację zawodu."""
    available_professions = ["Psychiatra", "Psycholog kliniczny"]
    
    # Poprawne dane
    validate_profession("Psychiatra", available_professions)
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Zawód 'Nieznany zawód' nie znajduje się na liście dostępnych zawodów: Psychiatra, Psycholog kliniczny."):
        validate_profession("Nieznany zawód", available_professions)


def test_validate_update_fields():
    """Testuje walidację pól aktualizacji."""
    valid_columns = ["specialty_id", "specialty_name"]
    
    # Poprawne dane
    validate_update_fields({"specialty_name": "Nowa specjalność"}, valid_columns)
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "Wartość"}, valid_columns)


def test_validate_column_name():
    """Testuje walidację nazw kolumn."""
    valid_columns = ["specialty_id", "specialty_name"]
    
    # Poprawne dane
    validate_column_name("specialty_name", valid_columns)
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Kolumna 'invalid_column' nie jest prawidłowa. Dozwolone kolumny: specialty_id, specialty_name."):
        validate_column_name("invalid_column", valid_columns)
