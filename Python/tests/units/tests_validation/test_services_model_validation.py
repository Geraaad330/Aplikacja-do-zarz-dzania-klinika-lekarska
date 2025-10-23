# test_services_model_validation.py

import pytest
from validators.services_model_validation import (
    validate_service_type,
    validate_duration_minutes,
    validate_service_price,
    validate_column_name,
    validate_operator_and_value,
    validate_update_fields,
)


def test_validate_service_type():
    """Testuje walidację pola `service_type`."""
    # Poprawne dane
    validate_service_type("Usługa A")
    validate_service_type("Opcja - (Specjalna) + Test")
    validate_service_type(r"Usługa \ Specjalna")  # Raw string dla \
    validate_service_type("Usługa: Test / 50%")  # Test dla /

    # Niepoprawne dane
    with pytest.raises(ValueError, match="service_type musi być ciągiem znaków."):
        validate_service_type(123)
    with pytest.raises(ValueError, match="service_type zawiera niedozwolone znaki."):
        validate_service_type("Usługa@#")


def test_validate_duration_minutes():
    """Testuje walidację pola `duration_minutes`."""
    # Poprawne dane
    validate_duration_minutes(1)
    validate_duration_minutes(120)
    validate_duration_minutes(300)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Czas trwania musi być liczbą całkowitą."):
        validate_duration_minutes("120")
    with pytest.raises(ValueError, match="Czas trwania musi być pomiędzy 1 a 300 minut."):
        validate_duration_minutes(0)
    with pytest.raises(ValueError, match="Czas trwania musi być pomiędzy 1 a 300 minut."):
        validate_duration_minutes(301)


def test_validate_service_price():
    """Testuje walidację pola `service_price`."""
    # Poprawne dane
    validate_service_price(1)
    validate_service_price(250)
    validate_service_price(500)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Cena usługi musi być liczbą całkowitą."):
        validate_service_price("500")
    with pytest.raises(ValueError, match="Cena usługi musi być pomiędzy 1 a 500."):
        validate_service_price(0)
    with pytest.raises(ValueError, match="Cena usługi musi być pomiędzy 1 a 500."):
        validate_service_price(501)


def test_validate_column_name():
    """Testuje walidację kolumny."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Poprawne dane
    validate_column_name("service_type", valid_columns)
    validate_column_name("service_price", valid_columns)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Kolumna 'invalid_column' nie jest prawidłowa."):
        validate_column_name("invalid_column", valid_columns)


def test_validate_operator_and_value():
    """Testuje walidację operatora i wartości."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Poprawne przypadki
    validate_operator_and_value("LIKE", "Usługa%")
    validate_operator_and_value("IN", ["Usługa A", "Usługa B"])
    validate_operator_and_value(">", 50)
    validate_operator_and_value("BETWEEN", (1, 300))

    # Niepoprawne operatory
    with pytest.raises(ValueError, match="Nieobsługiwany operator: INVALID_OPERATOR"):
        validate_operator_and_value("INVALID_OPERATOR", "%Usługa%")

    # Niepoprawne wartości
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")
    with pytest.raises(ValueError, match="Wartość dla operatora IN musi być niepustą listą lub krotką."):
        validate_operator_and_value("IN", [])
    with pytest.raises(ValueError, match="Wartość dla operatora BETWEEN musi być krotką z dwoma liczbami całkowitymi."):
        validate_operator_and_value("BETWEEN", (1, "300"))

    # Niepoprawne sortowanie
    with pytest.raises(ValueError, match="Kolumna 'invalid_column' jest nieprawidłowa."):
        validate_operator_and_value("=", 100, sort_by=[("invalid_column", "ASC")], valid_columns=valid_columns)
    with pytest.raises(ValueError, match="Kierunek sortowania 'UP' jest nieprawidłowy. Dozwolone: 'ASC', 'DESC'."):
        validate_operator_and_value("=", 100, sort_by=[("service_price", "UP")], valid_columns=valid_columns)




def test_validate_update_fields():
    """Testuje walidację pól do aktualizacji."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Poprawne dane
    validate_update_fields({"service_type": "Usługa A"}, valid_columns)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_field."):
        validate_update_fields({"invalid_field": "value"}, valid_columns)

def test_service_type_none_and_empty():
    """Testuje zachowanie dla pustych i None wartości w service_type."""
    with pytest.raises(ValueError, match="service_type musi być ciągiem znaków."):
        validate_service_type(None)
    with pytest.raises(ValueError, match="service_type nie może być pusty."):
        validate_service_type("")

def test_operator_and_value_complex():
    """Testuje złożone warunki dla validate_operator_and_value."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Poprawne przypadki
    validate_operator_and_value("BETWEEN", (1, 300))
    validate_operator_and_value("=", "Wartość", sort_by=[("service_price", "ASC")], valid_columns=valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nieobsługiwany operator: INVALID_OPERATOR"):
        validate_operator_and_value("INVALID_OPERATOR", "Wartość")
    with pytest.raises(ValueError, match="Kierunek sortowania 'UP' jest nieprawidłowy. Dozwolone: 'ASC', 'DESC'."):
        validate_operator_and_value("=", 50, sort_by=[("duration_minutes", "UP")], valid_columns=valid_columns)

def test_update_fields_edge_cases():
    """Testuje nietypowe przypadki dla validate_update_fields."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Pusty słownik aktualizacji
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)

    # Aktualizacja z nieistniejącymi kolumnami
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_field."):
        validate_update_fields({"invalid_field": "value"}, valid_columns)

def test_integration_validate_all():
    """Testuje integrację walidacji różnych funkcji."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Poprawne dane
    validate_service_type("Standardowa Usługa")
    validate_duration_minutes(150)
    validate_service_price(350)
    validate_column_name("service_price", valid_columns)
    validate_operator_and_value("LIKE", "%Usługa%", sort_by=[("service_price", "ASC")], valid_columns=valid_columns)
    validate_update_fields({"service_price": 300}, valid_columns)

    # Niepoprawne dane w kombinacji
    with pytest.raises(ValueError, match="service_type musi być ciągiem znaków."):
        validate_service_type(None)
    with pytest.raises(ValueError, match="Czas trwania musi być pomiędzy 1 a 300 minut."):
        validate_duration_minutes(0)
    with pytest.raises(ValueError, match="Cena usługi musi być pomiędzy 1 a 500."):
        validate_service_price(600)
    with pytest.raises(ValueError, match="Kolumna 'invalid_column' nie jest prawidłowa."):
        validate_column_name("invalid_column", valid_columns)
    with pytest.raises(ValueError, match="Nieobsługiwany operator: INVALID_OPERATOR"):
        validate_operator_and_value("INVALID_OPERATOR", "Wartość", valid_columns=valid_columns)

def test_specific_combinations():
    """Testuje specyficzne kombinacje danych dla walidacji."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Operator BETWEEN na granicach
    validate_operator_and_value("BETWEEN", (1, 300))
    with pytest.raises(ValueError, match="Wartość dla operatora BETWEEN musi być krotką z dwoma liczbami całkowitymi."):
        validate_operator_and_value("BETWEEN", (1, "300"))

    # Sortowanie po liczbach i daty
    validate_operator_and_value("=", 100, sort_by=[("duration_minutes", "DESC")], valid_columns=valid_columns)
    with pytest.raises(ValueError, match="Kierunek sortowania 'INVALID' jest nieprawidłowy. Dozwolone: 'ASC', 'DESC'."):
        validate_operator_and_value("=", 100, sort_by=[("duration_minutes", "INVALID")], valid_columns=valid_columns)

    # Kombinacja LIKE z pustą wartością
    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")

def test_unexpected_types():
    """Testuje nieoczekiwane typy danych w walidacji."""
    valid_columns = ["service_type", "duration_minutes", "service_price"]

    # Nieoczekiwane typy dla service_type
    with pytest.raises(ValueError, match="service_type musi być ciągiem znaków."):
        validate_service_type(12345)
    with pytest.raises(ValueError, match="service_type musi być ciągiem znaków."):
        validate_service_type({"type": "Usługa"})

    # Nieoczekiwane typy dla duration_minutes
    with pytest.raises(ValueError, match="Czas trwania musi być liczbą całkowitą."):
        validate_duration_minutes("60")
    with pytest.raises(ValueError, match="Czas trwania musi być liczbą całkowitą."):
        validate_duration_minutes([30])

    # Nieoczekiwane typy dla service_price
    with pytest.raises(ValueError, match="Cena usługi musi być liczbą całkowitą."):
        validate_service_price("100")
    with pytest.raises(ValueError, match="Cena usługi musi być liczbą całkowitą."):
        validate_service_price({"price": 300})

    # Nieoczekiwane typy dla sortowania
    with pytest.raises(ValueError, match="Kierunek sortowania '123' jest nieprawidłowy. Dozwolone: 'ASC', 'DESC'."):
        validate_operator_and_value("=", 100, sort_by=[("duration_minutes", 123)], valid_columns=valid_columns)


