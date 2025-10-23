# rooms_model_validation.py

import re
from controllers.database_controller import DatabaseController
from controllers.room_types_controller import RoomTypesController

def validate_room_type(room_type: str) -> None:
    """
    Waliduje pole `room_type` zgodnie z ograniczeniami SQL.

    :param room_type: Nazwa typu pokoju do walidacji.
    :raises ValueError: Jeśli nazwa zawiera niedozwolone znaki, jest pusta, zbyt krótka lub zbyt długa.
    :example:
    validate_room_type("Psychiatra dorosłych")  # Brak błędu
    validate_room_type("")  # ValueError: Nazwa typu pokoju nie może być sta.
    """
    # Definiuje dokładnie, jakie znaki są dozwolone
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*$"

    # 1. Sprawdzenie, czy room_type jest ciągiem znaków
    if not isinstance(room_type, str):
        raise ValueError("Nazwa typu pokoju musi być ciągiem znaków.")

    # 2. Sprawdzenie, czy room_type nie jest pusty
    if not room_type.strip():
        raise ValueError("Nazwa typu pokoju nie może być pusta.")

    # 3. Sprawdzenie długości nazwy
    if len(room_type) < 3 or len(room_type) > 100:
        raise ValueError("Nazwa typu pokoju musi mieć od 3 do 100 znaków.")

    # 4. Sprawdzenie, czy nazwa zawiera tylko dozwolone znaki. Jeśli pojawi się niedozwolony znak, ciąg zostanie odrzucony.
    if not re.fullmatch(pattern, room_type):
        raise ValueError("Nazwa typu pokoju zawiera niedozwolone znaki.")

    # 5. re.search(r"[0-9]", room_type) sprawdza, czy w nazwie występują cyfry (0-9). Jeśli znajdzie cyfrę, zgłosi błąd.
    if re.search(r"[0-9]", room_type):
        raise ValueError("Nazwa typu pokoju nie może zawierać cyfr.")



def validate_room_number(room_number: int) -> None:
    """
    Waliduje numer pokoju (room_number). 
    Może przyjmować tylko liczby od 0 do 100.

    Args:
        room_number (int): Numer pokoju.

    Raises:
        ValueError: Jeśli room_number jest poza zakresem lub zawiera niedozwolone znaki.
    """
    if not isinstance(room_number, int):
        raise ValueError("Numer pokoju musi być liczbą całkowitą.")
    if not (0 <= room_number <= 1000):
        raise ValueError("Numer pokoju musi być liczbą w zakresie od 0 do 100.")

def validate_floor(floor: int) -> None:
    """
    Waliduje piętro (floor). 
    Może przyjmować tylko liczby od 0 do 2.

    Args:
        floor (int): Piętro pokoju.

    Raises:
        ValueError: Jeśli floor jest poza zakresem lub zawiera niedozwolone znaki.
    """
    if not isinstance(floor, int):
        raise ValueError("Piętro musi być liczbą całkowitą.")
    if not (0 <= floor <= 5):
        raise ValueError("Piętro musi być liczbą w zakresie od 0 do 2.")

def validate_fk_room_type_id(fk_room_type_id: int) -> None:
    """
    Waliduje klucz obcy `fk_room_type_id`. 
    Może przyjmować tylko liczby całkowite.

    Args:
        fk_room_type_id (int): ID typu pokoju.

    Raises:
        ValueError: Jeśli fk_room_type_id nie jest liczbą.
    """
    if not isinstance(fk_room_type_id, int):
        raise ValueError("ID typu pokoju (fk_room_type_id) musi być liczbą całkowitą.")

def validate_room_type_exists(room_types_controller: RoomTypesController, fk_room_type_id: int) -> None:
    """
    Sprawdza, czy `fk_room_type_id` istnieje w tabeli `room_types`.

    Args:
        room_types_controller (RoomTypesController): Kontroler typu pokoi.
        fk_room_type_id (int): ID typu pokoju.

    Raises:
        ValueError: Jeśli ID typu pokoju nie istnieje.
    """
    room_types = room_types_controller.get_all_room_types()
    if not any(rt["room_type_id"] == fk_room_type_id for rt in room_types):
        raise ValueError(f"ID typu pokoju '{fk_room_type_id}' nie istnieje w tabeli room_types.")

def validate_unique_room_number(db_controller: DatabaseController, room_number: int) -> None:
    """
    Sprawdza unikalność numeru pokoju (room_number).

    Args:
        db_controller (DatabaseController): Kontroler bazy danych.
        room_number (int): Numer pokoju.

    Raises:
        ValueError: Jeśli room_number nie jest unikalny.
    """
    query = "SELECT COUNT(*) FROM rooms WHERE room_number = ?"
    cursor = db_controller.connection.execute(query, (room_number,))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Numer pokoju '{room_number}' już istnieje w tabeli rooms.")

def validate_update_fields(updates: dict, valid_columns: list) -> None:
    """
    Waliduje pola aktualizacji w zapytaniach SQL.

    :param updates: Słownik pól do aktualizacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli pole do aktualizacji jest nieprawidłowe lub słownik jest pusty.
    :example:
    validate_update_fields({"room_type": "Nowa nazwa"}, ["room_type_id", "room_type"])  # Brak błędu
    validate_update_fields({"invalid_column": "value"}, ["room_type_id", "room_type"])  # ValueError
    """
    if not updates:
        raise ValueError("Nie podano danych do aktualizacji.")
    for column in updates.keys():
        if column not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna do aktualizacji: {column}.")

# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def validate_operator_and_value(operator: str, value=None):
    """
    Waliduje operator i wartość w zapytaniach SQL.

    :param operator: Operator SQL (np. "=", "LIKE").
    :param value: Wartość przypisana operatorowi.
    :raises ValueError: Jeśli operator lub wartość są nieprawidłowe.
    """
    valid_operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN", "IS NULL", "IS NOT NULL"]

    if operator not in valid_operators:
        raise ValueError(f"Nieobsługiwany operator: {operator}.")

    if operator == "LIKE" and (not isinstance(value, str) or not value.strip()):
        raise ValueError("Wartość dla operatora LIKE musi być niepustym ciągiem znaków.")

    if operator == "BETWEEN" and not (isinstance(value, tuple) and len(value) == 2):
        raise ValueError("Operator BETWEEN wymaga krotki zawierającej dwie wartości.")

    if operator == "IN" and not (isinstance(value, (list, tuple)) and len(value) > 0):
        raise ValueError("Wartość dla operatora IN musi być niepustą listą lub krotką.")

    if operator in ["IS NULL", "IS NOT NULL"] and value is not None:
        raise ValueError(f"Operator {operator} nie wymaga przypisanej wartości.")


def validate_filters_and_sorting(filters, sort_by, valid_columns):
    """
    Waliduje filtry i sortowanie używane w zapytaniach SQL.

    :param filters: Lista słowników reprezentujących filtry, gdzie każdy słownik powinien zawierać klucze:
        - "column" (str): Nazwa kolumny, na której zastosowany jest filtr.
        - "operator" (str): Operator SQL (np. '=', 'LIKE', 'IN', 'BETWEEN', 'IS NULL').
        - "value" (opcjonalny): Wartość przypisana do operatora, wymagana dla większości operatorów.
    :param sort_by: Lista krotek reprezentujących sortowanie, gdzie każda krotka zawiera:
        - Nazwa kolumny do sortowania.
        - Kierunek sortowania ('ASC' lub 'DESC').
    :param valid_columns: Lista dozwolonych kolumn (str) w zapytaniach SQL.
    :raises ValueError: Jeśli:
        - Filtr zawiera nieprawidłową kolumnę.
        - Filtr używa nieprawidłowego operatora lub niewłaściwej wartości dla operatora.
        - Sortowanie używa nieprawidłowej kolumny lub kierunku.

    :return: None
    """
    if filters:
        for filter_item in filters:
            if not all(key in filter_item for key in ["column", "operator", "value"]):
                raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")
            if filter_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if filter_item["operator"] not in ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN", "IS NULL", "IS NOT NULL"]:
                raise ValueError(f"Nieprawidłowy operator w filtrze: {filter_item['operator']}.")

    if sort_by:
        for sort_item in sort_by:
            if "column" not in sort_item or "direction" not in sort_item:
                raise ValueError("Każde sortowanie musi zawierać klucze: 'column' i 'direction'.")
            if sort_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w sortowaniu: {sort_item['column']}. Dozwolone kolumny: {', '.join(valid_columns)}")
            if sort_item["direction"].upper() not in ["ASC", "DESC"]:
                raise ValueError(f"Nieprawidłowy kierunek sortowania: {sort_item['direction']}. Dozwolone wartości: 'ASC', 'DESC'.")


def handle_database_error(db_controller, query: str, params: tuple):
    """
    Obsługuje błędy bazy danych i zgłasza bardziej czytelne komunikaty.

    :param db_controller: Kontroler bazy danych.
    :param query: Zapytanie SQL.
    :param params: Parametry zapytania SQL.
    :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
    """
    try:
        return db_controller.connection.execute(query, params)
    except Exception as e:
        raise RuntimeError(f"Błąd podczas wykonywania zapytania: {query}. Szczegóły: {str(e)}") from e