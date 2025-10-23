# employees_model_validation.py
# Walidacje dla modelu `employees`.

import re


def validate_first_name(first_name: str) -> None:
    """allowed_fields 
    Waliduje pole `first_name`.
    - NOT NULL.
    - Może zawierać tylko litery (w tym polskie znaki).
    """
    if not isinstance(first_name, str):
        raise ValueError("first_name musi być ciągiem znaków.")
    if not re.fullmatch(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+", first_name):
        raise ValueError("first_name może zawierać tylko litery (w tym polskie znaki).")


def validate_last_name(last_name: str) -> None:
    """
    Waliduje pole `last_name`.
    - NOT NULL.
    - Może zawierać tylko litery (w tym polskie znaki).
    """
    if not isinstance(last_name, str):
        raise ValueError("last_name musi być ciągiem znaków.")
    if not re.fullmatch(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+", last_name):
        raise ValueError("last_name może zawierać tylko litery (w tym polskie znaki).")


def validate_email(email: str) -> None:
    """
    Waliduje pole `email`.
    - NOT NULL.
    - Musi być ciągiem znaków.
    - Musi pasować do formatu adresu e-mail (zawiera @ i .).
    """
    if email is None:
        raise ValueError("email musi być poprawnym adresem e-mail.")
    if email == "":
        raise ValueError("email musi być poprawnym adresem e-mail.")
    if not isinstance(email, str):
        raise ValueError("email musi być poprawnym adresem e-mail.")
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("email musi być poprawnym adresem e-mail.")


def validate_phone(phone: str) -> None:
    """
    Waliduje pole `phone`.
    - NOT NULL.
    - Musi zawierać dokładnie 9 cyfr.
    """
    if not isinstance(phone, str):
        raise ValueError("phone musi być ciągiem znaków.")
    if not re.fullmatch(r"[0-9]{9}", phone):
        raise ValueError("phone musi zawierać dokładnie 9 cyfr.")


def validate_profession(profession: str) -> None:
    """
    Waliduje pole `profession`.
    - NOT NULL.
    - Musi być jedną z predefiniowanych wartości.
    """
    allowed_professions = [
        "Informatyk", "Psychiatra", "Psycholog kliniczny", "Psychoterapeuta",
        "Psychopedagog", "Terapeuta uzależnień", "Dietetyk kliniczny",
        "Recepcjonista", "Księgowy", "Pracownik obsługi technicznej",
        "Pracownik obsługi porządkowej", "Administrator", "Kierownik"
    ]
    if not isinstance(profession, str):
        raise ValueError("profession musi być ciągiem znaków.")
    if profession not in allowed_professions:
        raise ValueError("profession musi należeć do listy dopuszczalnych wartości.")


def validate_is_medical_staff(is_medical_staff: int) -> None:
    """
    Waliduje pole `is_medical_staff`.
    - NOT NULL.
    - Musi przyjmować wartość 0 lub 1.
    """
    if not isinstance(is_medical_staff, int) or is_medical_staff not in (0, 1):
        raise ValueError("is_medical_staff musi przyjmować wartość 0 (nie-medyk) lub 1 (medyk).")


def validate_employee_entry(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    profession: str,
    is_medical_staff: int
) -> None:
    """
    Waliduje wszystkie pola pracownika.
    """
    validate_first_name(first_name)
    validate_last_name(last_name)
    validate_email(email)
    validate_phone(phone)
    validate_profession(profession)
    validate_is_medical_staff(is_medical_staff)


def validate_update_fields(**kwargs) -> None:
    """
    Waliduje pola podane do aktualizacji w metodzie update_employee.
    """
    allowed_fields = {"first_name", "last_name", "email", "phone", "profession", "is_medical_staff"}
    for field, value in kwargs.items():
        if field not in allowed_fields:
            raise ValueError(f"Nieznane pole do aktualizacji: {field}.")
        if field == "first_name":
            validate_first_name(value)
        elif field == "last_name":
            validate_last_name(value)
        elif field == "email":
            validate_email(value)
        elif field == "phone":
            validate_phone(value)
        elif field == "profession":
            validate_profession(value)
        elif field == "is_medical_staff":
            validate_is_medical_staff(value)




def validate_search_criteria(**criteria) -> None:
    """
    Sprawdza, czy podano przynajmniej jedno kryterium wyszukiwania.
    """
    if all(value is None or value == "" for value in criteria.values()):
        raise ValueError("Przynajmniej jedno kryterium wyszukiwania musi być podane.")

    for key, value in criteria.items():
        if key == "first_name" and not isinstance(value, str):
            raise ValueError("first_name musi być ciągiem znaków.")
        if key == "email":
            try:
                validate_email(value)
            except ValueError as e:
                raise ValueError(f"Błąd w polu email: {str(e)}") from e 



def validate_unique_email(db_connection, email: str) -> None:
    """
    Sprawdza, czy email jest unikalny w bazie danych.
    """
    cursor = db_connection.connection.cursor()  # Poprawione
    cursor.execute("SELECT COUNT(*) FROM employees WHERE email = ?", (email,))
    if cursor.fetchone()[0] > 0:
        raise ValueError("email musi być unikalny")


def validate_unique_phone(db_connection, phone: str) -> None:
    """
    Sprawdza, czy numer telefonu jest unikalny w bazie danych.
    """
    cursor = db_connection.connection.cursor()  # Poprawione
    cursor.execute("SELECT COUNT(*) FROM employees WHERE phone = ?", (phone,))
    if cursor.fetchone()[0] > 0:
        raise ValueError("phone musi być unikalny")


def validate_employee_exists(db_connection, employee_id: int) -> None:
    """
    Sprawdza, czy pracownik o podanym ID istnieje w bazie danych.
    """
    cursor = db_connection.connection.cursor()  # Poprawione
    cursor.execute("SELECT COUNT(*) FROM employees WHERE employee_id = ?", (employee_id,))
    if cursor.fetchone()[0] == 0:
        raise KeyError(f"Pracownik o ID {employee_id} nie istnieje.")
