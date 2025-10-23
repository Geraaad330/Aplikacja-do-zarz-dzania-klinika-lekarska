# test_employees_model_validation.py
# Testy dla walidacji z employees_model_validation.py

import re
import pytest
from validators.employees_model_validation import (
    validate_first_name,
    validate_last_name,
    validate_email,
    validate_phone,
    validate_profession,
    validate_is_medical_staff,
    validate_employee_entry,
    validate_update_fields,
    validate_search_criteria
)


def test_validate_first_name():
    """Testuje poprawność walidacji first_name."""
    validate_first_name("Jan")
    validate_first_name("Marek")
    with pytest.raises(ValueError, match="first_name może zawierać tylko litery"):
        validate_first_name("Jan123")
    with pytest.raises(ValueError, match="first_name musi być ciągiem znaków."):
        validate_first_name(None)


def test_validate_last_name():
    """Testuje poprawność walidacji last_name."""
    validate_last_name("Kowalski")
    validate_last_name("Nowak")
    with pytest.raises(ValueError, match="last_name może zawierać tylko litery"):
        validate_last_name("Nowak123")
    with pytest.raises(ValueError, match="last_name musi być ciągiem znaków."):
        validate_last_name(123)


def test_validate_email():
    """Testuje poprawność walidacji email."""
    validate_email("test@example.com")
    validate_email("jan.kowalski@klinika.com")
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        validate_email("invalid_email")
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        validate_email(123)


def test_validate_phone():
    """Testuje poprawność walidacji phone."""
    validate_phone("123456789")
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        validate_phone("12345")
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        validate_phone("1234abcd")
    with pytest.raises(ValueError, match="phone musi być ciągiem znaków."):
        validate_phone(123456789)


def test_validate_profession():
    """Testuje poprawność walidacji profession."""
    validate_profession("Informatyk")
    validate_profession("Psycholog kliniczny")
    with pytest.raises(ValueError, match="profession musi należeć do listy dopuszczalnych wartości."):
        validate_profession("Nieznany zawód")
    with pytest.raises(ValueError, match="profession musi być ciągiem znaków."):
        validate_profession(123)

def test_validate_is_medical_staff():
    """Testuje poprawność walidacji is_medical_staff."""
    validate_is_medical_staff(0)
    validate_is_medical_staff(1)
    with pytest.raises(ValueError, match=re.escape("is_medical_staff musi przyjmować wartość 0 (nie-medyk) lub 1 (medyk).")):
        validate_is_medical_staff(2)
    with pytest.raises(ValueError, match=re.escape("is_medical_staff musi przyjmować wartość 0 (nie-medyk) lub 1 (medyk).")):
        validate_is_medical_staff("1")

def test_validate_employee_entry():
    """Testuje walidację kompletnego wpisu pracownika."""
    validate_employee_entry("Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Informatyk", 1)
    with pytest.raises(ValueError, match="first_name może zawierać tylko litery"):
        validate_employee_entry("Jan123", "Kowalski", "jan@example.com", "123456789", "Informatyk", 1)
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        validate_employee_entry("Jan", "Kowalski", "jan@com", "123456789", "Informatyk", 1)
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        validate_employee_entry("Jan", "Kowalski", "jan@example.com", "1234", "Informatyk", 1)
    with pytest.raises(ValueError, match=re.escape("is_medical_staff musi przyjmować wartość 0 (nie-medyk) lub 1 (medyk).")):
        validate_employee_entry("Jan", "Kowalski", "jan@example.com", "123456789", "Informatyk", 2)

    with pytest.raises(ValueError, match="last_name może zawierać tylko litery"):
        validate_employee_entry("Jan", "Kowalski123", "jan@example.com", "123456789", "Informatyk", 1)
    with pytest.raises(ValueError, match="profession musi należeć do listy dopuszczalnych wartości."):
        validate_employee_entry("Jan", "Kowalski", "jan@example.com", "123456789", "Nieznany zawód", 1)
    with pytest.raises(ValueError, match="first_name musi być ciągiem znaków"):
        validate_employee_entry(None, "Kowalski", "jan@example.com", "123456789", "Informatyk", 1)


def test_validate_update_fields():
    """Testuje walidację pól aktualizacji."""
    validate_update_fields(first_name="Jan", phone="123456789")
    validate_update_fields(last_name="Kowalski", is_medical_staff=0)
    with pytest.raises(ValueError, match="phone musi zawierać dokładnie 9 cyfr."):
        validate_update_fields(phone="12345")
    with pytest.raises(ValueError, match="Nieznane pole do aktualizacji: .*"):
        validate_update_fields(nieznane_pole="Wartość")

    with pytest.raises(ValueError, match="first_name musi być ciągiem znaków"):
        validate_update_fields(first_name=123)
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        validate_update_fields(email=None)


def test_validate_search_criteria():
    """Testuje walidację kryteriów wyszukiwania."""
    validate_search_criteria(first_name="Jan")
    validate_search_criteria(profession="Informatyk", is_medical_staff=1)
    with pytest.raises(ValueError, match="Przynajmniej jedno kryterium wyszukiwania musi być podane"):
        validate_search_criteria()
    with pytest.raises(ValueError, match="first_name musi być ciągiem znaków."):
        validate_search_criteria(first_name=123)
    with pytest.raises(ValueError, match="email musi być poprawnym adresem e-mail."):
        validate_search_criteria(email=123)
    with pytest.raises(ValueError, match="Przynajmniej jedno kryterium wyszukiwania musi być podane"):
        validate_search_criteria(first_name=None, last_name=None)

