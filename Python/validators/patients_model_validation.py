# patients_model_validation.py
# Ten plik zawiera funkcje walidujące dane pacjentów przed ich zapisaniem w bazie danych.

import re  # Moduł regex do pracy z wyrażeniami regularnymi
from datetime import datetime  # Moduł datetime do walidacji dat

def validate_first_name(first_name):
    """
    Waliduje imię.
    """
    if not first_name or not re.match(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+$", first_name):
        raise ValueError("Imię jest nieprawidłowe. Powinno zawierać tylko litery.")

def validate_last_name(last_name):
    """
    Waliduje nazwisko.
    """
    if not last_name or not re.match(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+$", last_name):
        raise ValueError("Nazwisko jest nieprawidłowe. Powinno zawierać tylko litery.")

def validate_pesel(pesel, existing_pesels, required=True):
    """
    Waliduje numer PESEL:
    - Jeśli required=True (np. dodawanie nowego pacjenta), PESEL nie może być pusty.
    - Jeśli required=False (np. aktualizacja), PESEL może być pusty (czyli zostanie pominięty w walidacji).
    - PESEL (o ile nie jest pusty) może zawierać tylko cyfry (dokładnie 11 cyfr).
    - PESEL musi być unikalny.
    - PESEL nie może zawierać liter ani znaków specjalnych.
    """
    # 1. Sprawdzenie, czy PESEL jest pusty
    if not pesel:
        if required:
            raise ValueError("Numer PESEL nie może być pusty.")
        else:
            # W trybie aktualizacji pozwalamy pominąć PESEL
            return

    # 2. Sprawdzenie formatu (dokładnie 11 cyfr)
    if not re.match(r"^\d{11}$", pesel):
        raise ValueError("Numer PESEL powinien zawierać dokładnie 11 cyfr.")

    # 3. Unikalność PESEL
    if pesel in existing_pesels:
        raise ValueError("Numer PESEL musi być unikalny.")


def validate_phone(phone):
    """
    Waliduje numer telefonu.
    """
    if not phone:
        return  # Telefon jest opcjonalny
    phone = phone.replace(" ", "").replace("-", "")  # Usunięcie spacji i myślników
    if not re.match(r"^\d{9}$", phone):
        raise ValueError("Numer telefonu powinien składać się z 9 cyfr, bez znaków specjalnych.")

def validate_email(email):
    """
    Waliduje adres email.
    """
    if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        raise ValueError("Adres email jest nieprawidłowy.")

def validate_date_of_birth(date_of_birth):
    """
    Waliduje datę urodzenia.
    """
    if not date_of_birth:
        raise ValueError("Data urodzenia nie może być pusta.")
    try:
        datetime.strptime(date_of_birth, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Data urodzenia jest nieprawidłowa. Powinna mieć format YYYY-MM-DD.") from exc

def validate_address(address):
    """
    Waliduje adres po usunięciu niedozwolonych znaków specjalnych.
    """
    if not address:
        raise ValueError("Adres nie może być pusty.")
    if re.search(r"[^A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,\.\- ]", address):
        raise ValueError("Adres zawiera niedozwolone znaki specjalne.")  # Komunikat dostosowany do testu
    return address


    

def validate_patient_update(update_data, existing_pesels):
    """
    Waliduje dane aktualizowane w tabeli pacjentów.
    :param update_data: Słownik zawierający dane do aktualizacji (kwargs).
    :param existing_pesels: Lista istniejących PESEL do walidacji unikalności.
    """
    if "first_name" in update_data:
        validate_first_name(update_data["first_name"])
    if "last_name" in update_data:
        validate_last_name(update_data["last_name"])
    if "pesel" in update_data:
        validate_pesel(update_data["pesel"], existing_pesels)
    if "phone" in update_data:
        validate_phone(update_data["phone"])
    if "email" in update_data:
        validate_email(update_data["email"])
    if "date_of_birth" in update_data:
        validate_date_of_birth(update_data["date_of_birth"])
    if "address" in update_data:
        validate_address(update_data["address"])

def validate_filter_criteria(criteria):
    """
    Waliduje kryteria filtrowania pacjentów. Kryteria mogą być opcjonalne,
    ale jeśli są podane, muszą być poprawne.
    """
    allowed_keys = {"first_name", "last_name", "pesel", "phone", "email", "address", "date_of_birth"}
    for key in criteria.keys():
        if key not in allowed_keys:
            raise ValueError(f"Nieobsługiwane kryterium filtrowania: {key}")

    # Walidacja poszczególnych kryteriów, jeśli są podane
    if "first_name" in criteria:
        validate_first_name(criteria["first_name"])
    if "last_name" in criteria:
        validate_last_name(criteria["last_name"])
    if "pesel" in criteria:
        validate_pesel(criteria["pesel"], [])  # PESEL w filtrach nie wymaga sprawdzenia unikalności
    if "phone" in criteria:
        validate_phone(criteria["phone"])
    if "email" in criteria:
        validate_email(criteria["email"])
    if "date_of_birth" in criteria:
        validate_date_of_birth(criteria["date_of_birth"])
    if "address" in criteria:
        validate_address(criteria["address"])


def validate_future_date_of_birth(date_of_birth):
    """
    Waliduje datę urodzenia w formacie YYYY-MM-DD.
    """
    if not date_of_birth:
        raise ValueError("Data urodzenia nie może być pusta.")
    try:
        date = datetime.strptime(date_of_birth, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError("Data urodzenia jest nieprawidłowa. Powinna mieć format YYYY-MM-DD.") from e
    
    if date > datetime.now():
        raise ValueError("Data urodzenia nie może być w przyszłości.")


def clean_address(address):
    """
    Usuwa znaki specjalne z adresu, pozostawiając tylko litery, cyfry i podstawowe znaki interpunkcyjne.
    """
    return re.sub(r"[^A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,\.\- ]", "", address)