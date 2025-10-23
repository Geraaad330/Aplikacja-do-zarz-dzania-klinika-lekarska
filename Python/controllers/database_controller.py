# database_controller.py

import sqlite3
from config import Config

class DatabaseController:
    def __init__(self):
        self.database_path = Config.get_database_path()
        self.connection = None

    def connect_to_database(self):
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.database_path)
                self.connection.row_factory = sqlite3.Row

                # Włączenie obsługi kluczy obcych
                self.connection.execute("PRAGMA foreign_keys = ON;")

            print(f"Połączono z bazą danych: {self.database_path}")
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas łączenia z bazą danych: {e}") from e


    def table_exists(self, table_name: str) -> bool:
        """
        Sprawdza, czy tabela istnieje w bazie danych.
        """
        if self.connection is None:
            raise RuntimeError("Brak połączenia z bazą danych.")
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor = self.connection.execute(query, (table_name,))
        return cursor.fetchone() is not None

    def ensure_connection(self):
        """
        Sprawdza, czy połączenie z bazą danych istnieje. Jeśli nie, zgłasza błąd.
        """
        if self.connection is None:
            raise RuntimeError("Brak połączenia z bazą danych.")

    def build_filters(self, filters=None, sort_by=None):
        """
        Tworzy zapytanie SQL na podstawie filtrów i sortowania.

        metoda może pobierać wszystkie rekordy, jeśli nie przekażesz żadnych filtrów (filters=None) i zostawisz sortowanie 
        również jako None (sort_by=None). Wynika to z tego, że w implementacji funkcji build_filters

        :param filters: Lista filtrów, np. [{"column": "service_price", "operator": ">", "value": 100}]
        :param sort_by: Lista sortowania, np. [("service_price", "ASC"), ("service_type", "DESC")]
        :return: Krotka (query_string, values), gdzie query_string to zapytanie SQL, a values to lista parametrów.
        """
        query_string = "1=1"  # Domyślne zapytanie
        values = []

        # Obsługa filtrów
        if filters:
            conditions = []
            for filter_item in filters:
                column = filter_item["column"]
                operator = filter_item["operator"]
                value = filter_item.get("value")

                # Obsługa różnych operatorów
                if operator.upper() == "BETWEEN" and isinstance(value, tuple) and len(value) == 2:
                    conditions.append(f"{column} BETWEEN ? AND ?")
                    values.extend(value)
                elif operator.upper() in ["=", ">", "<", ">=", "<="]:
                    conditions.append(f"{column} {operator} ?")
                    values.append(value)
                elif operator.upper() == "LIKE":
                    # Dodajemy dokładniejsze dopasowanie wzorca
                    if not value.startswith("%") and not value.endswith("%"):
                        value = f"%{value}%"
                    conditions.append(f"{column} LIKE ?")
                    values.append(value)
                elif operator.upper() == "IN" and isinstance(value, (list, tuple)):
                    placeholders = ", ".join("?" for _ in value)
                    conditions.append(f"{column} IN ({placeholders})")
                    values.extend(value)
                elif operator.upper() == "IS NULL":
                    conditions.append(f"{column} IS NULL")
                elif operator.upper() == "IS NOT NULL":
                    conditions.append(f"{column} IS NOT NULL")
                else:
                    raise ValueError(f"Nieobsługiwany operator: {operator}")

            query_string += " AND " + " AND ".join(conditions)

        # Obsługa sortowania
        if sort_by:
            sort_clauses = []
            for column, direction in sort_by:
                if direction.upper() not in ["ASC", "DESC"]:
                    raise ValueError(f"Nieobsługiwany kierunek sortowania: {direction}")
                sort_clauses.append(f"{column} {direction.upper()}")
            query_string += " ORDER BY " + ", ".join(sort_clauses)

        return query_string, values

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None







    #test połączenia z bazą danych poprzez dodanie rekordu do bazy danych

    # def add_patient(self, first_name, last_name, pesel, phone, email, address, date_of_birth):
    #     try:
    #         if not self.connection:
    #             self.connect_to_database()
    #         query = """
    #         INSERT INTO patients (first_name, last_name, pesel, phone, email, address, date_of_birth)
    #         VALUES (?, ?, ?, ?, ?, ?, ?)
    #         """
    #         self.connection.execute(query, (first_name, last_name, pesel, phone, email, address, date_of_birth))
    #         self.connection.commit()
    #         print("Pacjent został dodany pomyślnie.")
    #     except sqlite3.Error as e:
    #         print(f"Błąd podczas dodawania pacjenta: {e}")