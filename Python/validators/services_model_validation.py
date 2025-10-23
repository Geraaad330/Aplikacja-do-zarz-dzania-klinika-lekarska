# services_model_validation.py

import re


def validate_service_type(service_type: str) -> None:
    """
    Waliduje pole `service_type`.
    """

    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:+.,/%\\]*$"
    if not isinstance(service_type, str):
        raise ValueError("service_type musi być ciągiem znaków.")
    if not service_type.strip():
        raise ValueError("service_type nie może być pusty.")
    if not re.fullmatch(pattern, service_type):
        raise ValueError("service_type zawiera niedozwolone znaki.")




def validate_duration_minutes(duration_minutes: int) -> None:
    """
    Waliduje pole `duration_minutes` zgodnie z ograniczeniami SQL.
    
    :param duration_minutes: Liczba minut do walidacji.
    :raises ValueError: Jeśli wartość nie mieści się w przedziale 1–300.
    :example:
    validate_duration_minutes(120)  # Brak błędu
    validate_duration_minutes(0)  # ValueError: Czas trwania musi być pomiędzy 1 a 300 minut.
    """
    if not isinstance(duration_minutes, int):
        raise ValueError("Czas trwania musi być liczbą całkowitą.")
    if not (1 <= duration_minutes <= 300):
        raise ValueError("Czas trwania musi być pomiędzy 1 a 300 minut.")


def validate_service_price(service_price: float) -> None:
    """
    Waliduje pole `service_price` zgodnie z ograniczeniami SQL.
    
    :param service_price: Cena usługi do walidacji (może być `float` lub `int`).
    :raises ValueError: Jeśli wartość nie mieści się w przedziale 1–500.
    
    :example:
    validate_service_price(100.50)  # Brak błędu
    validate_service_price(0)  # ValueError: Cena usługi musi być pomiędzy 1 a 500.
    validate_service_price(500.99)  # Brak błędu
    validate_service_price(501)  # ValueError: Cena usługi musi być pomiędzy 1 a 500.
    """
    if not isinstance(service_price, (int, float)):
        raise ValueError("Cena usługi musi być liczbą zmiennoprzecinkową.")

    if not (1 <= service_price <= 500):
        raise ValueError("Cena usługi musi być pomiędzy 1 a 500.")

    # Opcjonalnie: Zaokrąglenie do dwóch miejsc po przecinku
    service_price = round(service_price, 2)



def validate_column_name(column_name: str, valid_columns: list) -> None:
    """
    Sprawdza, czy podana kolumna znajduje się w liście dozwolonych kolumn.

    :param column_name: Nazwa kolumny do walidacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli nazwa kolumny jest nieprawidłowa.
    :example:
    validate_column_name("service_type", ["service_type", "duration_minutes", "service_price"])  # Brak błędu
    validate_column_name("invalid_column", ["service_type", "duration_minutes", "service_price"])  # ValueError
    """
    if column_name not in valid_columns:
        raise ValueError(f"Kolumna '{column_name}' nie jest prawidłowa. Dozwolone kolumny: {', '.join(valid_columns)}")


def validate_operator_and_value(operator: str, value=None, sort_by: list = None, valid_columns: list = None) -> None:
    """
    Waliduje operator, wartość w zapytaniach SQL oraz opcjonalnie sortowanie.

    :param operator: Operator SQL (np. "=", ">", "LIKE").
    :param value: Wartość przypisana operatorowi.
    :param sort_by: Lista krotek określających kolumny i kierunki sortowania.
    :param valid_columns: Lista dozwolonych kolumn w tabeli.
    :raises ValueError: Jeśli operator, wartość lub sortowanie są nieprawidłowe.
    """
    valid_operators = ["=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN"]
    if operator not in valid_operators:
        raise ValueError(f"Nieobsługiwany operator: {operator}")

    # Walidacja wartości
    if operator == "LIKE":
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Wartość dla operatora LIKE musi być niepustym ciągiem znaków.")
    if operator == "BETWEEN":
        if not (isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value)):
            raise ValueError("Wartość dla operatora BETWEEN musi być krotką z dwoma liczbami całkowitymi.")
    if operator == "IN":
        if not isinstance(value, (list, tuple)) or len(value) == 0:
            raise ValueError("Wartość dla operatora IN musi być niepustą listą lub krotką.")

    # Walidacja sortowania (jeśli sort_by zostało przekazane)
    if sort_by:
        for column, direction in sort_by:
            if valid_columns and column not in valid_columns:
                raise ValueError(f"Kolumna '{column}' jest nieprawidłowa. Dozwolone kolumny: {', '.join(valid_columns)}")
            if not isinstance(direction, str) or direction.upper() not in ["ASC", "DESC"]:
                raise ValueError(f"Kierunek sortowania '{direction}' jest nieprawidłowy. Dozwolone: 'ASC', 'DESC'.")


def validate_update_fields(updates: dict, valid_columns: list) -> None:
    """
    Waliduje pola aktualizacji w zapytaniach SQL.

    :param updates: Słownik pól do aktualizacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli pole do aktualizacji jest nieprawidłowe lub słownik jest pusty.
    """
    if not updates:
        raise ValueError("Nie podano danych do aktualizacji.")
    for column in updates.keys():
        if column not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna do aktualizacji: {column}.")

    


def validate_record_existence(db_controller, table_name: str, column_name: str, value) -> None:
    """
    Sprawdza, czy rekord istnieje w tabeli na podstawie wartości w kolumnie.

    :param db_controller: Kontroler bazy danych.
    :param table_name: Nazwa tabeli.
    :param column_name: Nazwa kolumny do sprawdzenia.
    :param value: Wartość, która ma być sprawdzona.
    :raises ValueError: Jeśli rekord nie istnieje.
    """
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} = ?"
    cursor = db_controller.connection.execute(query, (value,))
    if cursor.fetchone()[0] == 0:
        raise ValueError(f"Rekord z {column_name} = {value} nie istnieje w tabeli {table_name}.")


