# employee_specialties_model_validation.py

import re
from controllers.database_controller import DatabaseController
from controllers.employees_controller import EmployeesController
from controllers.specialties_controller import SpecialtiesController

# +-+-+-+- metody walidacji nazw rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_employee_name(first_name: str, last_name: str) -> None:
    """
    Waliduje imię i nazwisko pracownika.
    
    :param first_name: Imię pracownika.
    :param last_name: Nazwisko pracownika.
    :raises ValueError: Jeśli imię lub nazwisko są nieprawidłowe.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s]+$"

    for name, label in [(first_name, "Imię"), (last_name, "Nazwisko")]:
        if not isinstance(name, str):
            raise ValueError(f"{label} musi być ciągiem znaków.")
        if not name.strip():
            raise ValueError(f"{label} nie może być puste.")
        if len(name) < 3 or len(name) > 100:
            raise ValueError(f"{label} musi mieć od 3 do 100 znaków.")
        if not re.fullmatch(pattern, name):
            raise ValueError(f"{label} zawiera niedozwolone znaki.")

def validate_specialty_name(specialty_name: str) -> None:
    """
    Waliduje nazwę specjalizacji.
    
    :param specialty_name: Nazwa specjalizacji.
    :raises ValueError: Jeśli nazwa jest nieprawidłowa.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s()\-:.,/\\]+$"

    if not isinstance(specialty_name, str):
        raise ValueError("Nazwa specjalizacji musi być ciągiem znaków.")
    if not specialty_name.strip():
        raise ValueError("Nazwa specjalizacji nie może być pusta.")
    if len(specialty_name) < 3 or len(specialty_name) > 100:
        raise ValueError("Nazwa specjalizacji musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, specialty_name):
        raise ValueError("Nazwa specjalizacji zawiera niedozwolone znaki.")

# +-+-+-+- metody walidacji dodawania rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_add_employee_specialty(db_controller: DatabaseController, employee_id: int, specialty_id: int) -> None:
    """
    Waliduje dane wejściowe dla metody `add_employee_specialty`.

    :param db_controller: Kontroler bazy danych.
    :param employee_id: ID pracownika.
    :param specialty_id: ID specjalizacji.
    :raises ValueError: Jeśli dane są nieprawidłowe.
    """
    validate_employee_id(db_controller, employee_id)
    validate_specialty_id(db_controller, specialty_id)

# jeśli chcemy dodać specialty_id do tabeli employee_specialties to specialty_id musi istnieć w tabeli specialties
# jeśli chcemy dodać employee_id do tabeli employee_specialties to employee_id musi istnieć w tabeli employees
def validate_add_employee_specialty_by_names(first_name: str, last_name: str, specialty_name: str) -> None:
    """
    Waliduje dane wejściowe dla metody `add_employee_specialty_by_names`.

    :param first_name: Imię pracownika.
    :param last_name: Nazwisko pracownika.
    :param specialty_name: Nazwa specjalizacji.
    :raises ValueError: Jeśli dane są nieprawidłowe.
    """
    validate_employee_name(first_name, last_name)
    validate_specialty_name(specialty_name)

    # Metoda nic nie zwraca ponieważ wyjątki pojawiają się w metodch validate_specialty_name validate_employee_name

# +-+-+-+- metody sprawdzania id -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_employee_id(employees_controller: EmployeesController, employee_id: int) -> None:
    """
    Sprawdza, czy `employee_id` istnieje w tabeli `employees`.

    :param employees_controller: Kontroler pracowników.
    :param employee_id: ID pracownika.
    :raises ValueError: Jeśli `employee_id` nie istnieje.
    """
    # jeśli chcemy dodać employee_id do tabeli employee_specialties to employee_id musi istnieć w tabeli employees
    # jeśli rekord nie istnieje nie będzie w stanie pobrać wskazanego przez użytkownika employee_id metoda podniesie błąd
    try:
        if not employees_controller.get_employee(employee_id):
            raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.")
    except KeyError as exc:
        raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.") from exc

def validate_specialty_id(specialties_controller: SpecialtiesController, specialty_id: int) -> None:
    """
    Sprawdza, czy `specialty_id` istnieje w tabeli `specialties`.

    :param specialties_controller: Kontroler specjalizacji.
    :param specialty_id: ID specjalizacji.
    :raises ValueError: Jeśli `specialty_id` nie istnieje.
    """
    # jeśli chcemy dodać specialty_id do tabeli employee_specialties to specialty_id musi istnieć w tabeli specialties
    # jeśli rekord nie istnieje nie będzie w stanie pobrać wskazanego przez użytkownika employee_id metoda podniesie błąd
    filters = {"specialty_id": specialty_id}
    if not specialties_controller.get_specialties_with_filters(filters=filters):
        raise ValueError(f"Specjalizacja o ID {specialty_id} nie istnieje.")

# +-+-+-+- metody sprawdzania unikalności -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_unique_employee_specialty(db_controller, employee_id: int, specialty_id: int) -> None:
    """
    Sprawdza, czy kombinacja employee_id i specialty_id jest unikalna.

    :param db_controller: Kontroler bazy danych.
    :param employee_id: ID pracownika.
    :param specialty_id: ID specjalności.
    :raises ValueError: Jeśli kombinacja istnieje w tabeli employee_specialties.
    """

    #Zapytanie SQL zlicza rekordy w tabeli employee_specialties, które spełniają dwa warunki:
    # employee_id musi być równe podanej wartości employee_id.
    # specialty_id musi być równe podanej wartości specialty_id.
    # nie jest wykonywane dopóki nie wykona się cursor = db_controller.connection.execute(query, (employee_id, specialty_id))?
    query = """
    SELECT COUNT(*) FROM employee_specialties
    WHERE employee_id = ? AND specialty_id = ?
    """
    # query -> wykonanie powyższego query, (employee_id, specialty_id))
    # db_controller.connection.execute() wykonuje zapytanie SQL, podstawiając wartości employee_id i specialty_id w miejsce parametrów ?.
    cursor = db_controller.connection.execute(query, (employee_id, specialty_id))

    # jeśli komibinacja employee_id, specialty_id już istnieje cursor.fetchone()[0] zwróci [1] -> warunek zostaje spełniony więc podniesie się błąd
    # jeśli komibinacja employee_id, specialty_id nie istnieje cursor.fetchone()[0] zwróci [0] -> warunek nie zostaje spełniony więc nie podniesie się błąd
    # w tableli sql jest unique więc nie może znaleźć się więcej takich samych wyników niż 1
    if cursor.fetchone()[0] > 0: # cursor.fetchone -> wynik zapytania sql
        raise ValueError(f"Kombinacja employee_id={employee_id} i specialty_id={specialty_id} już istnieje.")

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
            if filter_item["column"] not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}. "
                                 f"Dozwolone kolumny: {', '.join(valid_columns)}")
            if filter_item["operator"] not in ["=", "<", ">", "<=", ">=", "!=", "LIKE", "IN", "IS NULL", "IS NOT NULL"]:
                raise ValueError(f"Nieobsługiwany operator: {filter_item['operator']}")
            if "value" not in filter_item or filter_item["value"] is None:
                raise ValueError(f"Filtr zawiera brakującą wartość dla kolumny: {filter_item['column']}")

    if sort_by:
        for sort_item in sort_by:
            column, direction = sort_item
            if column not in valid_columns:
                raise ValueError(f"Nieprawidłowa kolumna w sortowaniu: {column}. "
                                 f"Dozwolone kolumny: {', '.join(valid_columns)}")
            if direction not in ["ASC", "DESC"]:
                raise ValueError(f"Nieprawidłowy kierunek sortowania: {direction}")



    
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
