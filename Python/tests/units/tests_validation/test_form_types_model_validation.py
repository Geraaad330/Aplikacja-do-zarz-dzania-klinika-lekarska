# test_form_types_model_validation.py

import pytest
from validators.form_types_model_validation import (
    validate_form_name,
    validate_operator_and_value,
    validate_filters_and_sorting,
    validate_update_fields,
)


def test_validate_form_name():
    """Testuje walidację nazwy formularza."""
    # Poprawne dane
    validate_form_name("Zgoda, na leczenie.")
    validate_form_name("Zgoda na: przetwarzanie danych osobowych (RODO)")
    validate_form_name("Zgoda - na udostępnienie / danych medycznych")
    validate_form_name("ĄąĆćĘęŁłŃńÓóŚśŹźŻż")
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nazwa formularza musi być ciągiem znaków."):
        validate_form_name(123)
    with pytest.raises(ValueError, match="Nazwa formularza nie może być pusta."):
        validate_form_name("")
    with pytest.raises(ValueError, match="Nazwa formularza musi mieć od 3 do 100 znaków."):
        validate_form_name("AB")
    with pytest.raises(ValueError, match="Nazwa formularza musi mieć od 3 do 100 znaków."):
        validate_form_name("A" * 101)
    with pytest.raises(ValueError, match="Nazwa formularza zawiera niedozwolone znaki."):
        validate_form_name("!@#$%^%&*")
    with pytest.raises(ValueError, match="Nazwa formularza nie może zawierać cyfr."):
        validate_form_name("Szkolenie, wewnętrzne. 50")


def test_validate_operator_and_value():
    """Testuje walidację operatorów i wartości."""
    # Poprawne dane
    validate_operator_and_value("LIKE", "Zgoda%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", ["Zgoda na leczenie", "Zgoda na przetwarzanie danych osobowych (RODO)"])
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
    valid_columns = ["form_type_id", "form_name"]
    
    # Poprawne dane
    validate_filters_and_sorting(
        filters=[{"column": "form_name", "operator": "LIKE", "value": "Zgoda%"}],
        sort_by=[("form_name", "ASC")],
        valid_columns=valid_columns,
    )
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting(filters=[{"column": "form_name"}], sort_by=None, valid_columns=valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting(
            filters=[{"column": "invalid_column", "operator": "=", "value": "Zgoda na leczenie"}],
            sort_by=None,
            valid_columns=valid_columns,
        )
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna sortowania: invalid_column."):
        validate_filters_and_sorting(
            filters=None,
            sort_by=[("invalid_column", "ASC")],
            valid_columns=valid_columns,
        )

# -->> ta metoda walidacji nie wymaga testów walidacji wartości kolumny z test_validate_form_name() - od tego jest test modelu
# by przy aktualizacji jednocześnie sprawdzał wartość pola kolumny
def test_validate_update_fields(): 
    """Testuje walidację pól aktualizacji."""
    valid_columns = ["form_type_id", "form_name"]
    
    # Poprawne dane
    validate_update_fields({"form_name": "Zgoda na leczenie dziecka przez opiekuna prawnego"}, valid_columns)
    
    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "Wartość"}, valid_columns)

