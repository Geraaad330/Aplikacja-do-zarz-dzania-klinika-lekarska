# permissions_model_validation.py
"""
Moduł odpowiedzialny za walidację metod z system_permissions.py.
"""

# Metody statyczne to takie, które są definiowane wewnątrz klasy, ale nie wymagają dostępu do instancji klasy (self) ani do jej atrybutów.
# W Pythonie oznaczamy je dekoratorem @staticmethod. Wtedy w modelu bedzie można umieścić import całej klasy zamiast importowac 
# każdą metodę osobno jak w roles.py

class SystemPermissionsValidation:
    """
    Klasa zawierająca metody walidacji parametrów i połączeń bazy danych dla modelu system_permissions.
    """

    @staticmethod
    def validate_database_connection(db_controller):
        """
        Sprawdza, czy istnieje aktywne połączenie z bazą danych.

        Argumenty:
        - db_controller: Obiekt kontrolera bazy danych.

        Wyjątki:
        - RuntimeError: Jeśli brak aktywnego połączenia z bazą danych.

        Przykładowy wynik zapytania:
        (brak, metoda sprawdza samą dostępność połączenia)
        """
        if db_controller.connection is None:
            raise RuntimeError("Brak aktywnego połączenia z bazą danych.")
        

    @staticmethod
    def validate_column_name(column_name, valid_columns):
        """
        Sprawdza, czy podana kolumna należy do listy dozwolonych kolumn.

        Argumenty:
        - column_name (str): Nazwa kolumny do sprawdzenia.
        - valid_columns (list): Lista dozwolonych kolumn.

        Wyjątki:
        - ValueError: Jeśli kolumna nie znajduje się na liście dozwolonych.

        Przykład:
        valid_columns = ["permission_id", "permission_name"]
        validate_column_name("permission_name", valid_columns) -> OK
        validate_column_name("invalid_column", valid_columns) -> ValueError
        """
        if column_name not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna: {column_name}. Dozwolone kolumny: {valid_columns}")

    @staticmethod
    def validate_operator_and_value(operator, value):
        valid_operators = ["LIKE", "IN", "="]
        if operator.upper() not in valid_operators:
            raise ValueError(f"Nieobsługiwany operator: {operator}. Obsługiwane operatory: {valid_operators}")

        if operator.upper() == "IN":
            if not isinstance(value, list):
                raise ValueError("Operator 'IN' wymaga listy wartości.")
            if not value:
                raise ValueError("Lista nazw uprawnień nie może być pusta.")
            if not all(isinstance(item, str) for item in value):
                raise ValueError("Wszystkie elementy w permission_names muszą być ciągami znaków.")

        if operator.upper() == "LIKE":
            if not isinstance(value, str):
                raise ValueError("Wzorzec LIKE musi być ciągiem znaków.")
            if ";" in value or "--" in value:
                raise ValueError("Wzorzec LIKE zawiera niedozwolone znaki.")


    def validate_order_by(self, order_by):
        """
        Waliduje kolumnę używaną do sortowania.

        :param order_by: Nazwa kolumny (str).
        :raises ValueError: Jeśli kolumna nie jest dozwolona.

        Przykład:
            validate_order_by('permission_name')
            -> Brak błędów

            validate_order_by('invalid_column')
            -> ValueError: Nieprawidłowa kolumna: invalid_column.
        """
        valid_columns = ["permission_id", "permission_name"]
        if order_by not in valid_columns:
            raise ValueError(f"Nieprawidłowa kolumna: {order_by}. Dozwolone kolumny: {valid_columns}")

    @staticmethod
    def validate_query_results(results, allow_empty=False):
        """
        Sprawdza, czy zapytanie zwróciło wyniki.

        Argumenty:
        - results (list): Wyniki zapytania (lista słowników).
        - allow_empty (bool): Czy dopuszczalne są puste wyniki.

        Wyjątki:
        - ValueError: Jeśli wyniki są puste, a allow_empty=False.
        """
        if not results and not allow_empty:
            raise ValueError("Zapytanie nie zwróciło żadnych wyników.")


