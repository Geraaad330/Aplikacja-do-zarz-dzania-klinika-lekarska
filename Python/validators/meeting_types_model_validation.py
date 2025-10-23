# meeting_types_model_validation.py 

import re


def validate_meeting_type(meeting_type: str) -> None:
    """
    Waliduje pole `meeting_type` zgodnie z ograniczeniami SQL.

    :param meeting_type: Nazwa typu spotkania do walidacji.
    :raises ValueError: Jeśli nazwa zawiera niedozwolone znaki, jest pusta, zbyt krótka lub zbyt długa.
    :example:
    validate_meeting_type("Psychiatra dorosłych")  # Brak błędu
    validate_meeting_type("")  # ValueError: Nazwa typu spotkania nie może być pusta.
    """
    # Definiuje dokładnie, jakie znaki są dozwolone
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*$"

    # 1. Sprawdzenie, czy meeting_type jest ciągiem znaków
    if not isinstance(meeting_type, str):
        raise ValueError("Nazwa typu spotkania musi być ciągiem znaków.")

    # 2. Sprawdzenie, czy meeting_type nie jest pusty
    if not meeting_type.strip():
        raise ValueError("Nazwa typu spotkania nie może być pusta.")

    # 3. Sprawdzenie długości nazwy
    if len(meeting_type) < 3 or len(meeting_type) > 100:
        raise ValueError("Nazwa typu spotkania musi mieć od 3 do 100 znaków.")

    # 4. Sprawdzenie, czy nazwa zawiera tylko dozwolone znaki. Jeśli pojawi się niedozwolony znak, ciąg zostanie odrzucony.
    if not re.fullmatch(pattern, meeting_type):
        raise ValueError("Nazwa typu spotkania zawiera niedozwolone znaki.")

    # 5. re.search(r"[0-9]", meeting_type) sprawdza, czy w nazwie występują cyfry (0-9). Jeśli znajdzie cyfrę, zgłosi błąd.
    if re.search(r"[0-9]", meeting_type):
        raise ValueError("Nazwa typu spotkania nie może zawierać cyfr.")

def validate_operator_and_value(operator: str, value=None):
    # validate_operator_and_value jest wywoływana w  validate_filters_and_sorting!!!!!!!!!!
    """
    Waliduje operator i wartość w zapytaniach SQL.

    :param operator: Operator SQL (np. "=", "LIKE").
    :param value: Wartość przypisana operatorowi.
    :raises ValueError: Jeśli operator lub wartość są nieprawidłowe.
    """
    valid_operators = ["=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN"]
    if operator not in valid_operators:
        raise ValueError(f"Nieobsługiwany operator: {operator}.")

    if operator == "LIKE" and (not isinstance(value, str) or not value.strip()):
        raise ValueError("Wartość dla operatora LIKE musi być niepustym ciągiem znaków.")

    if operator == "BETWEEN" and not (isinstance(value, tuple) and len(value) == 2):
        raise ValueError("Operator 'BETWEEN' wymaga krotki zawierającej dwie wartości.")

    if operator == "IN" and not (isinstance(value, (list, tuple)) and len(value) > 0):
        raise ValueError("Wartość dla operatora IN musi być niepustą listą lub krotką.")


def validate_filters_and_sorting(filters, sort_by, valid_columns):
    """
    Waliduje filtry i sortowanie używane w zapytaniach SQL.

    :param filters: Lista słowników reprezentujących filtry, gdzie każdy słownik powinien zawierać klucze:
                    - "column" (str): Nazwa kolumny, na której zastosowany jest filtr.
                    - "operator" (str): Operator SQL (np. '=', 'LIKE', 'IN', 'BETWEEN', 'IS NULL').
                    - "value" (opcjonalny): Wartość przypisana do operatora, wymagana dla większości operatorów.
    :param sort_by: Lista krotek reprezentujących sortowanie, gdzie każda krotka zawiera:
                    - "column" (str): Nazwa kolumny do sortowania.
                    - "direction" (str): Kierunek sortowania ('ASC' lub 'DESC').
    :param valid_columns: Lista dozwolonych kolumn (str) w zapytaniu SQL.
    :raises ValueError: W przypadku gdy:
                        - Filtr zawiera nieprawidłową kolumnę.
                        - Filtr używa nieprawidłowego operatora lub niewłaściwej wartości dla operatora.
                        - Sortowanie używa nieprawidłowej kolumny lub kierunku.
    :return: None
    :example:
        validate_filters_and_sorting(
            filters=[
                {"column": "meeting_type", "operator": "LIKE", "value": "Psych%"},
                {"column": "meeting_type_id", "operator": "IN", "value": [1, 2, 3]},
            ],
            sort_by=[("meeting_type", "ASC")],
            valid_columns=["meeting_type", "meeting_type_id"]
        )  # Brak błędów
    """
    if not filters and not sort_by:
        return  # Brak filtrów i sortowania - zwracamy wszystkie dane.

    if filters:
        for filter_item in filters:
            column = filter_item.get("column")
            operator = filter_item.get("operator")
            value = filter_item.get("value")

            if column not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {column}. Dozwolone kolumny: {', '.join(valid_columns)}")

            if operator in ["IS NULL", "IS NOT NULL"]:
                if "value" in filter_item:
                    raise ValueError(f"Filtr '{operator}' nie wymaga wartości 'value'.")
            else:
                if "value" not in filter_item:
                    raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")
                validate_operator_and_value(operator, value)

    if sort_by:
        for column, direction in sort_by:
            if column not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna sortowania: {column}.")
            if direction.upper() not in ["ASC", "DESC"]:
                raise ValueError(f"Nieprawidłowy kierunek sortowania: {direction}. Dozwolone: 'ASC', 'DESC'.")



def validate_update_fields(updates: dict, valid_columns: list) -> None:
    """
    Waliduje pola aktualizacji w zapytaniach SQL.

    :param updates: Słownik pól do aktualizacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli pole do aktualizacji jest nieprawidłowe lub słownik jest pusty.
    :example:
    validate_update_fields({"meeting_type": "Nowa nazwa"}, ["meeting_type_id", "meeting_type"])  # Brak błędu
    validate_update_fields({"invalid_column": "value"}, ["meeting_type_id", "meeting_type"])  # ValueError
    """
    if not updates:
        raise ValueError("Nie podano danych do aktualizacji.")
    for column in updates.keys():
        if column not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna do aktualizacji: {column}.")


def validate_unique_meeting_type(db_controller, meeting_type: str):
    """
    Sprawdza, czy nazwa typu spotkania jest unikalna w bazie danych.

    :param db_controller: Obiekt kontrolera bazy danych.
    :param meeting_type: Nazwa typu spotkania do sprawdzenia.
    :raises ValueError: Jeśli nazwa typu spotkania już istnieje w bazie danych.
    :example:
    validate_unique_meeting_type(db_controller, "Konsylium terapeutyczne")  # Brak błędu
    """
    query = "SELECT COUNT(*) FROM meeting_types WHERE meeting_type = ?"
    cursor = db_controller.connection.execute(query, (meeting_type,))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Typ spotkania o nazwie '{meeting_type}' już istnieje.")
    


# Dlaczego metoda validate_column_name nie jest potrzebna w modelu?
# Widać, że funkcja build_filters działa w sposób samowystarczalny, ponieważ:

# Obsługuje dynamiczne budowanie zapytań SQL.
# Waliduje użycie operatorów oraz sprawdza wartość odpowiednio do operatora.
# Wymaga dostarczenia kolumn (column), które najprawdopodobniej są wcześniej zweryfikowane w get_valid_columns.
# Metoda get_valid_columns w pliku meeting_types.py:

# Wywołuje ona zapytanie SQL (PRAGMA table_info) w celu dynamicznego pobrania nazw kolumn tabeli z bazy danych.
# Jest to używane jako podstawa do weryfikacji, czy kolumna przekazana w zapytaniach SQL istnieje.
# Ta metoda dynamicznie sprawdza poprawność kolumn, co oznacza, że każdy fragment kodu korzystający z niej (np. validate_filters_and_sorting) 
# już korzysta z tej walidacji.