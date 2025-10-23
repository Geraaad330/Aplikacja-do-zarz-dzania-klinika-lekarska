# test_patients_model_validation.py
# Ten plik zawiera testy jednostkowe dla funkcji walidacyjnych z pliku patients_model_validation.py

import pytest
from validators.patients_model_validation import (
    validate_first_name,
    validate_last_name,
    validate_pesel,
    validate_phone,
    validate_email,
    validate_date_of_birth,
    validate_address,
    validate_patient_update, # Dodano testowaną funkcję
    clean_address,
    validate_future_date_of_birth,
    validate_filter_criteria
)


def test_validate_patient_update():
    """
    Test funkcji validate_patient_update z poprawnym formatem daty.
    """
    existing_pesels = ["12345678901", "11111111111", "22222222222"]

    # Poprawne dane aktualizowane
    update_data_valid = {
        "first_name": "Anna",
        "last_name": "Nowak",
        "pesel": "33333333333",
        "phone": "123456789",
        "email": "anna.nowak@example.com",
        "date_of_birth": "1990-01-01",  # Poprawny format daty
        "address": "Warszawa, ul. Przykładowa 5"
    }
    validate_patient_update(update_data_valid, existing_pesels)  # Nie powinno rzucić wyjątku

    # Niepoprawne dane - imię zawierające cyfry
    update_data_invalid_first_name = {"first_name": "Anna123"}
    with pytest.raises(ValueError, match="Imię jest nieprawidłowe. Powinno zawierać tylko litery."):
        validate_patient_update(update_data_invalid_first_name, existing_pesels)

    # Niepoprawne dane - powtórzony PESEL
    update_data_invalid_pesel = {"pesel": "12345678901"}  # PESEL już istnieje
    with pytest.raises(ValueError, match="Numer PESEL musi być unikalny."):
        validate_patient_update(update_data_invalid_pesel, existing_pesels)

    # Niepoprawne dane - za krótki numer telefonu
    update_data_invalid_phone = {"phone": "12345"}
    with pytest.raises(ValueError, match="Numer telefonu powinien składać się z 9 cyfr, bez znaków specjalnych."):
        validate_patient_update(update_data_invalid_phone, existing_pesels)

    # Niepoprawne dane - błędny email
    update_data_invalid_email = {"email": "niepoprawny.email"}
    with pytest.raises(ValueError, match="Adres email jest nieprawidłowy."):
        validate_patient_update(update_data_invalid_email, existing_pesels)

    # Niepoprawne dane - zły format daty
    update_data_invalid_date_of_birth = {"date_of_birth": "01.01.1990"}  # Nieprawidłowy format
    with pytest.raises(ValueError, match="Data urodzenia jest nieprawidłowa. Powinna mieć format YYYY-MM-DD."):
        validate_patient_update(update_data_invalid_date_of_birth, existing_pesels)

    # Niepoprawne dane - adres zawierający znaki specjalne
    update_data_invalid_address = {"address": "Niepoprawny@Adres"}
    with pytest.raises(ValueError, match="Adres zawiera niedozwolone znaki specjalne."):  # Poprawiony komunikat
        validate_patient_update(update_data_invalid_address, existing_pesels)

    # Częściowe dane poprawne
    update_data_partial = {
        "first_name": "Ewa",
        "phone": "987654321",
    }
    validate_patient_update(update_data_partial, existing_pesels)  # Nie powinno rzucić wyjątku

def test_validate_first_name():
    validate_first_name("Jan")
    validate_first_name("Łukasz")
    with pytest.raises(ValueError, match="Imię jest nieprawidłowe. Powinno zawierać tylko litery."):
        validate_first_name("")
    with pytest.raises(ValueError, match="Imię jest nieprawidłowe. Powinno zawierać tylko litery."):
        validate_first_name("Jan123")

def test_validate_last_name():
    validate_last_name("Kowalski")
    validate_last_name("Żółkiewski")
    with pytest.raises(ValueError, match="Nazwisko jest nieprawidłowe. Powinno zawierać tylko litery."):
        validate_last_name("")
    with pytest.raises(ValueError, match="Nazwisko jest nieprawidłowe. Powinno zawierać tylko litery."):
        validate_last_name("Kowalski123")

def test_validate_pesel():
    """
    Testuje walidację numeru PESEL zgodnie z wymaganiami:
    - PESEL nie może być pusty.
    - PESEL może zawierać tylko cyfry (dokładnie 11 cyfr).
    - PESEL musi być unikalny.
    - PESEL nie może zawierać liter ani znaków specjalnych.
    """

    # Lista istniejących PESEL
    existing_pesels = ["99010112345", "00112233444"]

    # Test poprawnego PESEL
    validate_pesel("12345678901", existing_pesels)  # Nowy, unikalny PESEL (przechodzi bez błędów)

    # Test pustego PESEL
    with pytest.raises(ValueError, match="Numer PESEL nie może być pusty."):
        validate_pesel("", existing_pesels)  # Pusty PESEL

    # Test PESEL zawierającego nie tylko cyfry
    with pytest.raises(ValueError, match="Numer PESEL powinien zawierać dokładnie 11 cyfr."):
        validate_pesel("1234abcd567", existing_pesels)  # PESEL zawiera litery

    # Test PESEL o niewłaściwej długości
    with pytest.raises(ValueError, match="Numer PESEL powinien zawierać dokładnie 11 cyfr."):
        validate_pesel("12345", existing_pesels)  # Za krótki PESEL

    # Test PESEL zawierającego znaki specjalne
    with pytest.raises(ValueError, match="Numer PESEL powinien zawierać dokładnie 11 cyfr."):
        validate_pesel("123-456-789", existing_pesels)  # PESEL zawiera myślniki

    # Test nieunikalnego PESEL
    with pytest.raises(ValueError, match="Numer PESEL musi być unikalny."):
        validate_pesel("99010112345", existing_pesels)  # Powtarzający się PESEL

def test_validate_phone():
    validate_phone("123456789")  # Poprawny telefon
    validate_phone("")  # Pusty numer (opcjonalny)
    validate_phone("123 456 789")  # Zawiera spacje
    validate_phone("123-456-789")  # Zawiera myślniki
    with pytest.raises(ValueError, match="Numer telefonu powinien składać się z 9 cyfr, bez znaków specjalnych."):
        validate_phone("12345")
    with pytest.raises(ValueError, match="Numer telefonu powinien składać się z 9 cyfr, bez znaków specjalnych."):
        validate_phone("12345abcd")

def test_validate_email():
    validate_email("jan.kowalski@example.com")
    validate_email("")  # Opcjonalny email
    with pytest.raises(ValueError, match="Adres email jest nieprawidłowy."):
        validate_email("jan.kowalski.com")
    with pytest.raises(ValueError, match="Adres email jest nieprawidłowy."):
        validate_email("jan.kowalski@com")

def test_validate_date_of_birth():
    """
    Test walidacji daty urodzenia w formacie YYYY-MM-DD.
    """
    validate_date_of_birth("1985-01-01")  # Poprawny format
    with pytest.raises(ValueError, match="Data urodzenia nie może być pusta."):
        validate_date_of_birth("")
    with pytest.raises(ValueError, match="Data urodzenia jest nieprawidłowa. Powinna mieć format YYYY-MM-DD."):
        validate_date_of_birth("01.01.1985")  # Niepoprawny format


def test_validate_address():
    """
    Test walidacji adresu, sprawdzający poprawność i niedozwolone znaki.
    """
    validate_address("Warszawa, ul. Przykładowa 10")
    with pytest.raises(ValueError, match="Adres zawiera niedozwolone znaki specjalne."):
        validate_address("Warszawa@ulica")  # Niedozwolony znak '@'



def test_validate_filter_criteria():
    """
    Testuje walidację kryteriów filtrowania:
    - Każde pole musi być poprawnie walidowane.
    - Niedozwolone kryteria powinny zgłaszać wyjątek.
    """
    criteria_valid = {
        "first_name": "Jan",
        "pesel": "12345678901",
        "address": "Warszawa, ul. Przykładowa 5"
    }
    validate_filter_criteria(criteria_valid)  # Poprawne kryteria

    criteria_invalid_key = {"unknown_field": "value"}
    with pytest.raises(ValueError, match="Nieobsługiwane kryterium filtrowania: unknown_field"):
        validate_filter_criteria(criteria_invalid_key)

def test_validate_future_date_of_birth():
    """
    Test walidacji daty przyszłej.
    """
    validate_future_date_of_birth("1985-01-01")  # Data z przeszłości

    # Sprawdzenie daty z przyszłości
    with pytest.raises(ValueError, match="Data urodzenia nie może być w przyszłości."):
        validate_future_date_of_birth("2099-01-01")  # Data z przyszłości

    # Sprawdzenie błędnego formatu daty
    with pytest.raises(ValueError, match="Data urodzenia jest nieprawidłowa. Powinna mieć format YYYY-MM-DD."):
        validate_future_date_of_birth("01.01.2099")  # Nieprawidłowy format



# nowa funkcja
def test_clean_address():
    """
    Testuje funkcję czyszczącą adres z niedozwolonych znaków.
    """
    assert clean_address("Warszawa@ulica") == "Warszawaulica"  # Usunięcie znaku '@'
    assert clean_address("ul. Przykładowa 10!") == "ul. Przykładowa 10"  # Usunięcie '!'
    assert clean_address("Kraków, ul. Żółkiewskiego 5") == "Kraków, ul. Żółkiewskiego 5"  # Brak zmian
