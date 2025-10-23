# roles_model_validation.py
# Walidacje dla modelu `roles`.

# Czy funkcje w roles_model_validation są metodami statycznymi?
# Obecnie w roles_model_validation.py funkcje są zdefiniowane jako niezależne funkcje na poziomie modułu. Oznacza to, że nie są ani 
# metodami klasy, ani instancji. W takim przypadku należy importować każdą metodę osobno w modelu roles.py 
# Aby przekształcić je w metody statyczne, należy je umieścić w klasie i oznaczyć dekoratorem 
# @staticmethod. Wtedy w modelu bedzie można umieścić import całej klasy zamiast importowac każdą metodę osobno jak w roles.py

import re
from typing import Any

def validate_role_name(role_name: str) -> None:
    """
    Waliduje pole `role_name`.
    - NOT NULL.
    - Musi być ciągiem znaków.
    - Nie może być pusty.
    - Musi pasować do wzorca: tylko litery (w tym polskie znaki).
    - Długość: minimum 3 znaki, maksimum 50 znaków.
    """
    # Sprawdzenie, czy role_name jest ciągiem znaków
    if not isinstance(role_name, str):
        raise ValueError("role_name musi być ciągiem znaków.")
    if not role_name.strip():
        raise ValueError("role_name nie może być pusty.")
    if not (3 <= len(role_name) <= 50):
        raise ValueError("role_name musi mieć długość od 3 do 50 znaków.")
    if not re.fullmatch(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\s]+", role_name):
        raise ValueError("role_name może zawierać tylko litery (w tym polskie znaki).")




def validate_column_name(column_name, valid_columns):
    """
    Sprawdza, czy podana kolumna znajduje się w liście dozwolonych kolumn.
    """
    if column_name not in valid_columns:
        raise ValueError(f"Kolumna '{column_name}' nie jest prawidłowa. Dostępne kolumny: {', '.join(valid_columns)}")


def validate_operator_and_value(operator: str, values: Any) -> None:
    """
    Sprawdza poprawność operatora ('LIKE', 'IN') oraz wartości.
    - Operator 'LIKE': wartość musi być niepustym ciągiem znaków.
    - Operator 'IN': wartość musi być listą ciągów znaków.
    """
    if operator not in ["LIKE", "IN"]:
        raise ValueError("Obsługiwane operatory to 'LIKE' oraz 'IN'.")
    if operator == "IN" and (not isinstance(values, list) or not values):
        raise ValueError("Lista wartości dla operatora IN nie może być pusta.")
    if operator == "LIKE" and (not isinstance(values, str) or not values.strip()):
        raise ValueError("Wartość dla operatora LIKE musi być niepustym ciągiem znaków.")



def validate_sorting(column_name, valid_columns) -> None:
    """
    Waliduje kolumnę sortowania.
    """
    if column_name not in valid_columns:
        raise ValueError(f"Kolumna '{column_name}' nie jest prawidłowa. Dostępne kolumny: {', '.join(valid_columns)}")


def validate_record_existence(db_controller, table_name, column_name, value) -> None:
    """
    Sprawdza, czy rekord istnieje w tabeli na podstawie podanej kolumny i wartości.
    """
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} = ?"
    cursor = db_controller.connection.execute(query, (value,))
    if cursor.fetchone()[0] == 0:
        raise ValueError(f"Rekord z {column_name} = {value} nie istnieje w tabeli {table_name}.")


def validate_update_fields(updates: dict, valid_columns: list) -> None:
    """
    Waliduje pola, które mają być zaktualizowane.
    """
    if not updates:
        raise ValueError("Nie podano danych do aktualizacji.")

    for column, _value in updates.items():
        if column not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna: {column}.")





def validate_count_like_pattern(pattern):
    """
    Waliduje wzorzec LIKE dla funkcji zliczającej rekordy.
    """
    if not isinstance(pattern, str):
        raise ValueError("Wzorzec LIKE musi być ciągiem znaków.")
    if ";" in pattern or "--" in pattern:
        raise ValueError("Wzorzec LIKE zawiera niedozwolone znaki.")
    
def validate_unique_role_name(db_controller, role_name: str) -> None:
    """
    Sprawdza, czy nazwa roli jest unikalna w tabeli `roles`.
    """
    if db_controller.connection is None:
        raise RuntimeError("Brak połączenia z bazą danych.")
    
    query = "SELECT COUNT(*) FROM roles WHERE role_name = ?"
    cursor = db_controller.connection.execute(query, (role_name,))
    count = cursor.fetchone()[0]
    if count > 0:
        raise ValueError(f"Nazwa roli '{role_name}' już istnieje w bazie danych.")


