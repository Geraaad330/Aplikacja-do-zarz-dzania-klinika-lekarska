# roles.py
# Moduł odpowiedzialny za zarządzanie tabelą `roles` w bazie danych.

import sqlite3
from controllers.database_controller import DatabaseController
from validators.roles_model_validation import (
    validate_role_name,
    validate_unique_role_name,
    validate_column_name,
    validate_operator_and_value,
    validate_sorting,
    validate_record_existence,
    validate_count_like_pattern,
)

class Roles:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `roles` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Roles z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `roles` w bazie danych, jeśli jeszcze nie istnieje.
        Tabela zgodna z dostarczonym kodem SQL.

        Przykład:
        roles.create_table()

        Wynik:
        Utworzona tabela `roles` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                query = """
                CREATE TABLE IF NOT EXISTS roles (
                    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (role_name GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]*')
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def create_new_record(self, role_name: str) -> bool:
        """
        Tworzy nowy rekord w tabeli `roles`.

        :param role_name: Nazwa roli do dodania.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia

            if not self.db_controller.table_exists("roles"):
                print("[RolesModel_create_new_record] Błąd: Tabela 'roles' nie istnieje w bazie danych.")
                return False

            # Walidacja nazwy roli
            validate_role_name(role_name)
            validate_unique_role_name(self.db_controller, role_name)

            # Wstawienie nowego rekordu
            query = "INSERT INTO roles (role_name) VALUES (?)"
            self.db_controller.connection.execute(query, (role_name,))
            self.db_controller.connection.commit()

            print(f"[RolesModel_create_new_record] Rola '{role_name}' została dodana pomyślnie.")
            return True  # Operacja zakończona sukcesem

        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            print(f"[RolesModel_create_new_record] Błąd integralności podczas dodawania roli: {e}")
            return False

        except sqlite3.Error as e:
            print(f"[RolesModel_create_new_record] Błąd bazy danych podczas dodawania roli: {e}")
            return False

        except ValueError as ve:
            print(f"[RolesModel_create_new_record] Błąd walidacji: {ve}")
            return False







    def get_all_records(self):
        """
        Pobiera wszystkie rekordy z tabeli `roles`.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                raise RuntimeError("Tabela 'roles' nie istnieje w bazie danych.")
            query = "SELECT * FROM roles"
            cursor = self.db_controller.connection.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania wszystkich rekordów: {e}") from e



    def get_records_by_column(self, column_name, value):
        """
        Pobiera rekordy na podstawie wartości w danej kolumnie.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                raise RuntimeError("Tabela 'roles' nie istnieje w bazie danych.")
            validate_column_name(column_name, ["role_id", "role_name"])
            query = f"SELECT * FROM roles WHERE {column_name} = ?"
            cursor = self.db_controller.connection.execute(query, (value,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e




    def filter_records(self, column_name, operator, values):
        """
        Filtruje rekordy na podstawie operatorów (LIKE, IN).
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                raise RuntimeError("Tabela 'roles' nie istnieje w bazie danych.")

            # Obsługa pustej listy dla operatora IN
            if operator == "IN" and not values:
                return []

            validate_operator_and_value(operator, values)

            query = ""
            if operator.upper() == "IN":
                placeholders = ", ".join(["?"] * len(values))
                query = f"SELECT * FROM roles WHERE {column_name} IN ({placeholders})"
            elif operator.upper() == "LIKE":
                query = f"SELECT * FROM roles WHERE {column_name} LIKE ?"
                values = [values]

            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas filtrowania rekordów: {e}") from e





    def update_record(self, role_id: int, role_name: str) -> bool:
        """
        Aktualizuje nazwę roli w tabeli 'roles' na podstawie ID.

        :param role_id: ID roli do aktualizacji.
        :param role_name: Nowa nazwa roli.
        :return: True, jeśli aktualizacja się powiodła, False w przypadku błędu.
        """
        if not role_name:
            print("[RolesModel_update_record] Brak nowej nazwy roli do aktualizacji.")
            return False  # Brak zmian do aktualizacji

        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia

            if not self.db_controller.table_exists("roles"):
                print("[RolesModel_update_record] Tabela 'roles' nie istnieje w bazie danych.")
                return False  # Brak tabeli w bazie

            validate_record_existence(self.db_controller, "roles", "role_id", role_id)

            # Walidacja nazwy roli
            validate_role_name(role_name)

            query = "UPDATE roles SET role_name = ? WHERE role_id = ?"
            params = (role_name, role_id)

            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

            return cursor.rowcount > 0  # Zwróci True, jeśli co najmniej 1 wiersz został zaktualizowany

        except sqlite3.IntegrityError:
            print("[RolesModel_update_record] Nazwa roli już istnieje w bazie danych.")
            return False  # Duplikacja nazwy roli

        except sqlite3.Error as e:
            print(f"[RolesModel_update_record] Błąd podczas aktualizowania rekordu: {e}")
            return False  # Błąd bazy danych





    def delete_record_by_id(self, record_id) -> bool:
        """
        Usuwa rekord na podstawie ID.

        :param record_id: ID rekordu do usunięcia.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia

            # Sprawdzenie, czy tabela istnieje
            if not self.db_controller.table_exists("roles"):
                print("[RolesModel_delete_record_by_id] Błąd: Tabela 'roles' nie istnieje w bazie danych.")
                return False

            # Usunięcie rekordu
            query = "DELETE FROM roles WHERE role_id = ?"
            cursor = self.db_controller.connection.execute(query, (record_id,))
            self.db_controller.connection.commit()

            return cursor.rowcount > 0  # Zwraca True, jeśli usunięto przynajmniej jeden rekord

        except sqlite3.Error as e:
            print(f"[RolesModel_delete_record_by_id] Błąd bazy danych: {e}")
            return False  # Wystąpił błąd



    def delete_records_by_criteria(self, column_name, value):
        """
        Usuwa rekordy na podstawie określonego kryterium.
        :param column_name: Nazwa kolumny, w której szukamy wartości.
        :param value: Wartość, na podstawie której usuwamy rekordy.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                raise RuntimeError("Tabela 'roles' nie istnieje w bazie danych.")
            validate_column_name(column_name, ["role_id", "role_name"])
            query = f"DELETE FROM roles WHERE {column_name} = ?"
            self.db_controller.connection.execute(query, (value,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordów na podstawie kryterium: {e}") from e


    def sort_records(self, column_name, ascending=True, filter_column=None, filter_value=None):
        """
        Sortuje rekordy według wybranej kolumny i kierunku z opcjonalnym filtrowaniem.
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                raise RuntimeError("Tabela 'roles' nie istnieje w bazie danych.")
            
            # Walidacja kolumny sortowania
            validate_sorting(column_name, ["role_id", "role_name"])

            # Budowanie zapytania SQL
            query = "SELECT * FROM roles"
            if filter_column and filter_value:
                query += f" WHERE {filter_column} = ?"
            query += f" ORDER BY {column_name} {'ASC' if ascending else 'DESC'}"
            
            params = (filter_value,) if filter_column and filter_value else ()
            cursor = self.db_controller.connection.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas sortowania rekordów: {e}") from e

    def count_records(self, column_name=None, like_pattern=None, value=None):
        """
        Liczy rekordy w tabeli `roles` na podstawie opcjonalnych kryteriów.
        :param column_name: Kolumna, według której liczymy rekordy (opcjonalnie).
        :param like_pattern: Wzorzec LIKE do filtrowania rekordów (opcjonalnie).
        :param value: Konkretna wartość do porównania w kolumnie (opcjonalnie).
        """
        try:
            self.db_controller.ensure_connection()  # Sprawdzenie połączenia
            if not self.db_controller.table_exists("roles"):
                raise RuntimeError("Tabela 'roles' nie istnieje w bazie danych.")

            if column_name and like_pattern:
                validate_column_name(column_name, ["role_id", "role_name"])
                validate_count_like_pattern(like_pattern)  # Walidacja wzorca LIKE
                query = f"SELECT COUNT(*) FROM roles WHERE {column_name} LIKE ?"
                params = (like_pattern,)
            elif column_name and value:
                validate_column_name(column_name, ["role_id", "role_name"])
                query = f"SELECT COUNT(*) FROM roles WHERE {column_name} = ?"
                params = (value,)
            else:
                query = "SELECT COUNT(*) FROM roles"
                params = ()

            cursor = self.db_controller.connection.execute(query, params)
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas liczenia rekordów: {e}") from e




    def get_role_by_user_id(self, user_id):
        """
        Pobiera nazwę roli użytkownika z bazy danych na podstawie jego ID.
        """
        try:
            query = """
            SELECT r.role_name
            FROM roles r
            JOIN users u ON r.role_id = u.role_id
            WHERE u.user_id = ?
            """
            self.db_controller.ensure_connection()
            result = self.db_controller.connection.execute(query, (user_id,)).fetchone()
            if result:
                role_name = result["role_name"]
                print(f"Pobrano rolę: {role_name} dla user_id: {user_id}")  # Debug
                return role_name
            else:
                print(f"Nie znaleziono roli w bazie danych dla user_id: {user_id}")  # Debug
                return None
        except AttributeError as ae:
            print(f"Błąd atrybutu: {ae}")
        except TypeError as te:
            print(f"Błąd typu danych: {te}")
        except ValueError as ve:
            print(f"Błąd wartości: {ve}")
        except IndexError as ie:
            print(f"Błąd indeksu w wyniku zapytania: {ie}")

        # Domyślna wartość w przypadku błędu
        print("Błąd podczas zapytania o rolę użytkownika.")
        return None
    
    def get_role_by_id(self, role_id: int) -> dict:
        """
        Pobiera wszystkie dane roli z tabeli `roles` na podstawie `role_id`.

        :param role_id: ID roli do pobrania.
        :return: Słownik z danymi roli lub pusty słownik jeśli nie znaleziono.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie czy rola istnieje
            query = "SELECT * FROM roles WHERE role_id = ?"
            cursor = self.db_controller.connection.execute(query, (role_id,))
            role_data = cursor.fetchone()

            if role_data is None:
                print(f"[RolesModel_get_role_by_id] Rola o ID {role_id} nie została znaleziona.")
                return {}

            # Konwersja wyniku do słownika
            column_names = [desc[0] for desc in cursor.description]
            role_dict = dict(zip(column_names, role_data))

            print(f"[RolesModel_get_role_by_id] Pobranie roli: {role_dict}")
            return role_dict

        except sqlite3.OperationalError as op_err:
            print(f"[RolesModel_get_role_by_id] Błąd operacyjny bazy danych: {op_err}")
            return {}

        except sqlite3.DatabaseError as db_err:
            print(f"[RolesModel_get_role_by_id] Błąd bazy danych: {db_err}")
            return {}
