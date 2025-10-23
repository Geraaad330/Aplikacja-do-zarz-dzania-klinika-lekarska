# employee_services_model_validation.py

import re
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.database_controller import DatabaseController

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


def validate_service_name(service_name: str) -> None:
    """
    Waliduje nazwę usługi.

    :param service_name: Nazwa usługi.
    :raises ValueError: Jeśli nazwa jest nieprawidłowa.
    """
    pattern = r"^[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż\s()-:.,/\\]+$"
    if not isinstance(service_name, str):
        raise ValueError("Nazwa usługi musi być ciągiem znaków.")
    if not service_name.strip():
        raise ValueError("Nazwa usługi nie może być pusta.")
    if len(service_name) < 3 or len(service_name) > 100:
        raise ValueError("Nazwa usługi musi mieć od 3 do 100 znaków.")
    if not re.fullmatch(pattern, service_name):
        raise ValueError("Nazwa usługi zawiera niedozwolone znaki.")

# +-+-+-+- metody walidacji aktualizacji rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_update_record_by_names(first_name, last_name, service_name):
    """
    Sprawdza, czy dane wejściowe do aktualizacji rekordu są poprawne.
    """
    validate_employee_name(first_name, last_name)
    validate_service_name(service_name)

    # Sprawdzenie długości i znaków w nazwie usługi
    if not (3 <= len(service_name) <= 100):
        raise ValueError("Nazwa usługi musi mieć od 3 do 100 znaków.")
    if not all(c.isalnum() or c in " ()-:.,/\\" for c in service_name):
        raise ValueError("Nazwa usługi zawiera niedozwolone znaki.")



def validate_update_record_by_ids(
    employees_controller: EmployeesController, 
    services_controller: ServicesController, 
    db_controller: DatabaseController, 
    current_employee_id: int, 
    current_service_id: int, 
    new_employee_id: int, 
    new_service_id: int
) -> None:
    """
    Waliduje dane wejściowe dla aktualizacji rekordu na podstawie `employee_id` i `service_id` oraz sprawdza unikalność nowej kombinacji.
    """
    validate_employee_id(employees_controller, new_employee_id)
    validate_service_id(services_controller, new_service_id)
    
    # Jeśli nowa kombinacja różni się od bieżącej, sprawdź unikalność
    if (current_employee_id != new_employee_id or current_service_id != new_service_id):
        validate_unique_employee_service(db_controller, new_employee_id, new_service_id)



# +-+-+-+- metody walidacji dodawania rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

# pylint: disable=W0613
def validate_add_employee_service_by_ids(db_controller, employees_controller, services_controller, employee_id, service_id):

    """
    Waliduje dodanie rekordu na podstawie ID pracownika i usługi.
    """
    employee_exists = employees_controller.get_employee(employee_id)
    if not employee_exists:
        raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.")

    service_exists = services_controller.get_service(service_id)
    if not service_exists:
        raise ValueError(f"Usługa o ID {service_id} nie istnieje.")






# jeśli chcemy dodać service_id do tabeli employee_services to service_id musi istnieć w tabeli services
# jeśli chcemy dodać employee_id do tabeli employee_services to employee_id musi istnieć w tabeli employees
def validate_add_employee_specialty_by_names(employees_controller, services_controller, first_name, last_name, service_name):
    """
    Sprawdza, czy można dodać specjalizację pracownika na podstawie imienia, nazwiska i nazwy usługi.
    """
    validate_employee_name(first_name, last_name)
    validate_service_name(service_name)

    employees = employees_controller.filter_employees(first_name=first_name, last_name=last_name)
    if not employees:
        raise ValueError(f"Pracownik {first_name} {last_name} nie istnieje.")

    services = services_controller.get_services_with_filters(filters=[{"column": "service_type" , "operator": "=", "value": service_name}])
    if not services:
        raise ValueError(f"Usługa '{service_name}' nie istnieje.")


    # Metoda nic nie zwraca ponieważ wyjątki pojawiają się w metodch validate_specialty_name validate_employee_name

# +-+-+-+- metody walidacji usuwania rekordów -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_delete_record_by_id(db_controller: DatabaseController, employee_service_id: int) -> None:
    """
    Waliduje usuwanie rekordu na podstawie `employee_service_id`.
    """
    query = "SELECT COUNT(*) FROM employee_services WHERE employee_service_id = ?"
    cursor = db_controller.connection.execute(query, (employee_service_id,))
    if cursor.fetchone()[0] == 0:
        raise ValueError("Nie znaleziono rekordu o podanym ID.")


def validate_delete_records_by_names(employees_controller, services_controller, first_name, last_name, service_name):
    employees = employees_controller.filter_employees(first_name=first_name, last_name=last_name)
    if not employees:
        raise KeyError(f"Pracownik {first_name} {last_name} nie istnieje.")  # Spójne z innymi miejscami.
    services = services_controller.get_services_with_filters(
        filters=[{"column": "service_type", "operator": "=", "value": service_name}]
    )
    if not services:
        raise KeyError(f"Usługa '{service_name}' nie istnieje.")



    # Walidacja zakończona poprawnie - usunięcie może być kontynuowane.



# +-+-+-+- metody sprawdzania id -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 

def validate_employee_id(employees_controller: EmployeesController, employee_id: int) -> None:
    try:
        if not employees_controller.get_employee(employee_id):
            raise ValueError(f"Pracownik o ID {employee_id} nie istnieje.")
    except KeyError as exc:
        raise ValueError("Pracownik o ID {employee_id} nie istnieje.") from exc



def validate_service_id(services_controller, service_id: int) -> None:
    """
    Sprawdza, czy `service_id` istnieje w tabeli `services`.

    :param services_controller: Kontroler usług.
    :param service_id: ID usługi.
    :raises ValueError: Jeśli `service_id` nie istnieje.
    """
    filters = [{"column": "service_id", "operator": "=", "value": service_id}]
    if not services_controller.get_services_with_filters(filters=filters):
        raise ValueError(f"Usługa o ID {service_id} nie istnieje.")





# +-+-+-+- metody sprawdzania unikalności -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def validate_unique_employee_service(db_controller, employee_id, service_id, exclude_id=None):
    """
    Waliduje unikalność kombinacji employee_id i service_id.
    Ignoruje rekord o podanym exclude_id.
    """
    query = """
    SELECT COUNT(*)
    FROM employee_services
    WHERE employee_id = ? AND service_id = ?
    """
    params = [employee_id, service_id]

    if exclude_id:
        query += " AND employee_service_id != ?"
        params.append(exclude_id)

    cursor = db_controller.connection.execute(query, params)
    if cursor.fetchone()[0] > 0:
        raise ValueError(
            f"Kombinacja employee_id={employee_id} i service_id={service_id} już istnieje."
        )


def validate_unique_employee_service_by_names(db_controller: DatabaseController, employees_controller: EmployeesController,
                                              services_controller: ServicesController, first_name: str, last_name: str, service_name: str) -> None:
    """
    Sprawdza unikalność rekordu na podstawie imienia, nazwiska i nazwy usługi.

    :param db_controller: Kontroler bazy danych.
    :param employees_controller: Kontroler pracowników.
    :param services_controller: Kontroler usług.
    :param first_name: Imię pracownika.
    :param last_name: Nazwisko pracownika.
    :param service_name: Nazwa usługi.
    :raises ValueError: Jeśli rekord już istnieje.
    """
    # Pobranie pracownika na podstawie imienia i nazwiska
    employees = employees_controller.filter_employees(first_name=first_name, last_name=last_name)
    if not employees:
        raise ValueError(f"Pracownik {first_name} {last_name} nie istnieje.")
    employee_id = employees[0]["employee_id"]

    # Pobranie usługi na podstawie nazwy
    services = services_controller.get_services_with_filters(filters=[{"column": "service_type", "operator": "=", "value": service_name}])
    if not services:
        raise ValueError(f"Usługa '{service_name}' nie istnieje.")
    service_id = services[0]["service_id"]

    # Sprawdzenie unikalności w tabeli employee_services
    query = """
    SELECT COUNT(*) FROM employee_services
    WHERE employee_id = ? AND service_id = ?
    """
    cursor = db_controller.connection.execute(query, (employee_id, service_id))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Rekord dla {first_name} {last_name} i usługi '{service_name}' już istnieje.")



def validate_unique_update_by_names(db_controller, employees_controller, services_controller,
                                    current_employee_id, current_service_id,
                                    new_first_name, new_last_name, new_service_name):
    # Pobierz ID nowego pracownika i usługi
    employees = employees_controller.filter_employees(first_name=new_first_name, last_name=new_last_name)
    if not employees:
        raise ValueError(f"Pracownik {new_first_name} {new_last_name} nie istnieje.")
    new_employee_id = employees[0]["employee_id"]

    services = services_controller.get_services_with_filters(
        filters=[{"column": "service_type", "operator": "=", "value": new_service_name}]
    )
    if not services:
        raise ValueError(f"Usługa '{new_service_name}' nie istnieje.")
    new_service_id = services[0]["service_id"]

    # Jeśli dane się nie zmieniają, zakończ walidację
    if new_employee_id == current_employee_id and new_service_id == current_service_id:
        return

    # Sprawdzenie konfliktu unikalności
    query = """
    SELECT COUNT(*)
    FROM employee_services
    WHERE employee_id = ? AND service_id = ?
    """
    cursor = db_controller.connection.execute(query, (new_employee_id, new_service_id))
    if cursor.fetchone()[0] > 0:
        raise ValueError(
            f"Rekord z {new_first_name} {new_last_name} i usługą '{new_service_name}' już istnieje."
        )



    query = """
    SELECT COUNT(*)
    FROM employee_services
    WHERE employee_id = ? AND service_id = ?
    """
    cursor = db_controller.connection.execute(query, (new_employee_id, new_service_id))
    if cursor.fetchone()[0] > 0:
        raise ValueError(
            f"Rekord z {new_first_name} {new_last_name} i usługą '{new_service_name}' już istnieje."
        )




def validate_unique_update_record_by_ids(db_controller: DatabaseController, employee_service_id: int,
                                         employee_id: int, service_id: int) -> None:
    """
    Sprawdza unikalność kombinacji `employee_id` i `service_id` przy aktualizacji rekordu.

    :param db_controller: Kontroler bazy danych.
    :param employee_service_id: ID aktualizowanego rekordu.
    :param employee_id: ID pracownika.
    :param service_id: ID usługi.
    :raises ValueError: Jeśli kombinacja `employee_id` i `service_id` już istnieje dla innego rekordu.
    """
    query = """
    SELECT COUNT(*) FROM employee_services
    WHERE employee_id = ? AND service_id = ? AND employee_service_id != ?
    """
    cursor = db_controller.connection.execute(query, (employee_id, service_id, employee_service_id))
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Kombinacja employee_id={employee_id} i service_id={service_id} już istnieje.")



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
                raise ValueError(f"Nieprawidłowa kolumna w filtrze: {filter_item['column']}. "
                                 f"Dozwolone kolumny: {', '.join(valid_columns)}")
            if filter_item["operator"] not in ["=", "<", ">", "<=", ">=", "!=", "LIKE", "IN", "IS NULL", "IS NOT NULL"]:
                raise ValueError(f"Nieprawidłowy operator w filtrze: {filter_item['operator']}.")

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