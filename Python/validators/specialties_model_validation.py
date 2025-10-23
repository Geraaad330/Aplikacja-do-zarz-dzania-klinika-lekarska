# specialties_model_validation.py

import re


def validate_specialty_name(specialty_name: str) -> None:
    """
    Waliduje pole `specialty_name` zgodnie z ograniczeniami SQL.

    :param specialty_name: Nazwa specjalności do walidacji.
    :raises ValueError: Jeśli nazwa zawiera niedozwolone znaki, jest pusta, zbyt krótka lub zbyt długa.
    :example:
    validate_specialty_name("Psychiatra dorosłych")  # Brak błędu
    validate_specialty_name("")  # ValueError: Nazwa specjalności nie może być pusta.
    """
    # Definiuje dokładnie, jakie znaki są dozwolone
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*$"

    # 1. Sprawdzenie, czy specialty_name jest ciągiem znaków
    if not isinstance(specialty_name, str):
        raise ValueError("Nazwa specjalności musi być ciągiem znaków.")

    # 2. Sprawdzenie, czy specialty_name nie jest pusty
    if not specialty_name.strip():
        raise ValueError("Nazwa specjalności nie może być pusta.")

    # 3. Sprawdzenie długości nazwy
    if len(specialty_name) < 3 or len(specialty_name) > 100:
        raise ValueError("Nazwa specjalności musi mieć od 3 do 100 znaków.")

    # 4. Sprawdzenie, czy nazwa zawiera tylko dozwolone znaki. Jeśli pojawi się niedozwolony znak, ciąg zostanie odrzucony.
    if not re.fullmatch(pattern, specialty_name):
        raise ValueError("Nazwa specjalności zawiera niedozwolone znaki.")

    # 5. re.search(r"[0-9]", specialty_name) sprawdza, czy w nazwie występują cyfry (0-9). Jeśli znajdzie cyfrę, zgłosi błąd.
    if re.search(r"[0-9]", specialty_name):
        raise ValueError("Nazwa specjalności nie może zawierać cyfr.")


def validate_operator_and_value(operator: str, value=None):
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



def validate_profession(profession: str, available_professions: list) -> None:
    """
    Waliduje, czy podany zawód istnieje na liście dostępnych zawodów.

    :param profession: Nazwa zawodu do walidacji.
    :param available_professions: Lista dostępnych zawodów.
    :raises ValueError: Jeśli zawód nie znajduje się na liście dostępnych zawodów.
    :example:
    validate_profession("Psychiatra", ["Psychiatra", "Psycholog kliniczny"])  # Brak błędu
    validate_profession("Nieistniejący zawód", ["Psychiatra", "Psycholog kliniczny"])  # ValueError
    """
    if profession not in available_professions:
        raise ValueError(f"Zawód '{profession}' nie znajduje się na liście dostępnych zawodów: {', '.join(available_professions)}.")


def validate_update_fields(updates: dict, valid_columns: list) -> None:
    """
    Waliduje pola aktualizacji w zapytaniach SQL.

    :param updates: Słownik pól do aktualizacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli pole do aktualizacji jest nieprawidłowe lub słownik jest pusty.
    :example:
    validate_update_fields({"specialty_name": "Nowa nazwa"}, ["specialty_id", "specialty_name"])  # Brak błędu
    validate_update_fields({"invalid_column": "value"}, ["specialty_id", "specialty_name"])  # ValueError
    """
    if not updates:
        raise ValueError("Nie podano danych do aktualizacji.")
    for column in updates.keys():
        if column not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna do aktualizacji: {column}.")

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
def validate_column_name(column_name: str, valid_columns: list) -> None:
    """
    Sprawdza, czy podana kolumna znajduje się w liście dozwolonych kolumn.

    :param column_name: Nazwa kolumny do walidacji.
    :param valid_columns: Lista dozwolonych kolumn.
    :raises ValueError: Jeśli nazwa kolumny jest nieprawidłowa.
    :example:
    validate_column_name("specialty_name", ["specialty_id", "specialty_name"])  # Brak błędu
    validate_column_name("invalid_column", ["specialty_id", "specialty_name"])  # ValueError
    """
    if column_name not in valid_columns:
        raise ValueError(f"Kolumna '{column_name}' nie jest prawidłowa. Dozwolone kolumny: {', '.join(valid_columns)}.")


def validate_unique_specialty_name(db_controller, specialty_name: str):
    """
    Sprawdza, czy nazwa specjalności jest unikalna w bazie danych.

    :param db_controller: Obiekt kontrolera bazy danych.
    :param specialty_name: Nazwa specjalności do sprawdzenia.
    :raises ValueError: Jeśli nazwa specjalności już istnieje w bazie danych.
    :example:
    validate_unique_specialty_name(db_controller, "Psychiatra dorosłych")  # Brak błędu
    """
    query = "SELECT COUNT(*) FROM specialties WHERE specialty_name = ?"
    cursor = db_controller.connection.execute(query, (specialty_name,))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Specjalność o nazwie '{specialty_name}' już istnieje.")