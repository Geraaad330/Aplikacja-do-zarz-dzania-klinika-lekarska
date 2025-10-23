# permissions.py
# Moduł odpowiedzialny za zarządzanie tabelą `system_permissions` w bazie danych.

import sqlite3
from controllers.database_controller import DatabaseController
from validators.permissions_model_validation import SystemPermissionsValidation

#      WYMAGANIA MODELU: 

# -- model nie posiada operacji CRUD (dodawanie, usuwanie, aktualizacja). Model posiada funkcję tylko do odczytu jako tabela w interfejsie
# -- zarządzanie uprawnieniami nie odbywa się na poziomie modelu czy aplikacji tylko na poziomie kodu SQL. Uprawnienia są zawsze statyczne
# -- stworzenie tabeli w modelu na podstawie kodu sql dla bazy testowej 

#      WYMAGANE FUNKCJE:

# -- odczyt rekordów -->> pobieranie listy wszystkich rekordów
# -- zaawansowana filtracja danych z użyciem operatorów LIKE, IN 
# -- sortowanie danych ->> sortowanie kolumny permission_name od a do z i od z do a oraz sortowanie kolumny permission_id od najmniejszej do największej i od największej do najmniejdzej
# -- metody zliczające rekordy --> Zliczanie wszystkich rekordów, Zliczanie rekordów spełniających określone kryteria i z z operatorami LIKE, IN
# -- dodać obsługę try-except jeśli metody bezpośrednio komunikują się z bazą danych


class Permissions:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `system_permissions`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Permissions z kontrolerem bazy danych.
        """
        SystemPermissionsValidation.validate_database_connection(db_controller)
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `system_permissions` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            query = """
            CREATE TABLE IF NOT EXISTS system_permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                permission_name TEXT NOT NULL UNIQUE CHECK (
                    permission_name IN (
                        'zarzadzaj_wszystkimi_pacjentami',
                        'przegladaj_przypisanych_pacjentow',
                        'edytuj_przypisanych_pacjentow',
                        'zarzadzaj_wizytami',
                        'zarzadzaj_swoimi_wizytami',
                        'zarzadzaj_pracownikami',
                        'zarzadzaj_rolami_i_uprawnieniami',
                        'zarzadzaj_pomieszczeniami',
                        'zarzadzaj_platnosciami',
                        'przegladaj_swoj_kalendarz',
                        'zarzadzaj_swoim_kalendarzem',
                        'przegladaj_kalendarz_placowki',
                        'zarzadzaj_spotkaniami_wewnetrznymi',
                        'zarzadzaj_typami_spotkan_wewnetrznych',
                        'zarzadzaj_uslugami',
                        'zarzadzaj_specjalnosciami',
                        'przegladaj_diagnozy',
                        'zarzadzaj_diagnozami',
                        'przegladaj_recepty',
                        'zarzadzaj_receptami',
                        'zarzadzaj_typami_formularzy',
                        'zarzadzaj_formularzami_pacjentow'
                    )
                )
            )
            """
            self.db_controller.connection.execute(query)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e




    def add_permission(self, permission_name: str):
        """
        Dodaje nowy rekord do tabeli `system_permissions`.

        :param permission_name: Nazwa uprawnienia.
        :raises ValueError: Jeśli nazwa jest nieprawidłowa.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """

        try:
            query = "INSERT INTO system_permissions (permission_name) VALUES (?)"
            self.db_controller.connection.execute(query, (permission_name,))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Uprawnienie o nazwie '{permission_name}' już istnieje.") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania rekordu: {e}") from e


    def get_all_permissions(self):
        """
        Pobiera wszystkie uprawnienia z tabeli `system_permissions`.

        permissions.get_all_permissions()

         {'permission_id': 1, 'permission_name': 'Dodawanie pacjentów'},
         {'permission_id': 2, 'permission_name': 'Edycja pacjentów'},
         {'permission_id': 3, 'permission_name': 'Przeglądanie pacjentów'},
         {'permission_id': 4, 'permission_name': 'Dodawanie wizyt'},
         {'permission_id': 5, 'permission_name': 'Edycja wizyt'},
        """
        SystemPermissionsValidation.validate_database_connection(self.db_controller)
        query = "SELECT * FROM system_permissions"
        cursor = self.db_controller.connection.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    


    def filter_permissions(self, permission_names=None, name_pattern=None):
        """
        Filtruje uprawnienia na podstawie listy nazw (IN) lub wzorca (LIKE).

        Filtrowanie po nazwach (IN)
        permissions.filter_permissions(permission_names=['Edycja pacjentów', 'Przeglądanie wizyt'])
        {'permission_id': 2, 'permission_name': 'Edycja pacjentów'},
        {'permission_id': 6, 'permission_name': 'Przeglądanie wizyt'}

        Filtrowanie po wzorcu (LIKE) -> permissions.filter_permissions(name_pattern='%wizyt%')
        {'permission_id': 4, 'permission_name': 'Dodawanie wizyt'},
        {'permission_id': 5, 'permission_name': 'Edycja wizyt'},
        {'permission_id': 6, 'permission_name': 'Przeglądanie wizyt'}

        """
        SystemPermissionsValidation.validate_database_connection(self.db_controller)
        query = "SELECT * FROM system_permissions WHERE 1=1"
        params = []

        if permission_names is not None:
            if not isinstance(permission_names, list):
                raise ValueError("Lista nazw uprawnień musi być listą ciągów znaków.")
            if not permission_names:
                raise ValueError("Lista nazw uprawnień nie może być pusta.")
            SystemPermissionsValidation.validate_operator_and_value("IN", permission_names)
            placeholders = ", ".join(["?"] * len(permission_names))
            query += f" AND permission_name IN ({placeholders})"
            params.extend(permission_names)

        if name_pattern:
            SystemPermissionsValidation.validate_operator_and_value("LIKE", name_pattern)
            query += " AND permission_name LIKE ?"
            params.append(name_pattern)

        # Dodaj sortowanie wyników
        query += " ORDER BY permission_name ASC"

        cursor = self.db_controller.connection.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        SystemPermissionsValidation.validate_query_results(results, allow_empty=True)
        return results

    def get_sorted_permissions(self, order_by="permission_name", ascending=True):
        """
        Pobiera posortowane uprawnienia według wskazanej kolumny i kierunku.

        Sortowanie po permission_name rosnąco
        
        permissions.get_sorted_permissions(order_by="permission_name", ascending=True)

        {'permission_id': 4, 'permission_name': 'Dodawanie wizyt'},
        {'permission_id': 7, 'permission_name': 'Dodawanie diagnoz'},
        {'permission_id': 1, 'permission_name': 'Dodawanie pacjentów'},

        Sortowanie po permission_id malejąco

        {'permission_id': 10, 'permission_name': 'Zarządzanie rolami'},
        {'permission_id': 9, 'permission_name': 'Wystawianie recept'},
        {'permission_id': 8, 'permission_name': 'Edycja diagnoz'},    
        """
        valid_columns = ["permission_id", "permission_name"]
        SystemPermissionsValidation.validate_column_name(order_by, valid_columns)

        direction = "ASC" if ascending else "DESC"
        query = f"SELECT * FROM system_permissions ORDER BY {order_by} {direction}"

        cursor = self.db_controller.connection.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        SystemPermissionsValidation.validate_query_results(results, allow_empty=True)
        return results
    
    def count_permissions(self, name_pattern=None):
        """
        Zlicza uprawnienia, opcjonalnie z filtrem LIKE.

        Zliczanie wszystkich rekordów -> permissions.count_permissions() -> wynik: 10

        Zliczanie rekordów z wzorcem (LIKE) -> permissions.count_permissions(name_pattern='%wizyt%')
        wynik: 3 -> Wyjaśnienie: W tabeli znajdują się trzy uprawnienia z frazą "wizyt".
        """
        SystemPermissionsValidation.validate_database_connection(self.db_controller)
        query = "SELECT COUNT(*) as count FROM system_permissions WHERE 1=1"
        params = []

        if name_pattern:
            SystemPermissionsValidation.validate_operator_and_value("LIKE", name_pattern)
            query += " AND permission_name LIKE ?"
            params.append(name_pattern)

        cursor = self.db_controller.connection.execute(query, params)
        return cursor.fetchone()["count"]

    def count_permissions_by_name(self, names):
        """
        Zlicza uprawnienia na podstawie listy nazw.

        permissions.count_permissions_by_name(['Dodawanie pacjentów', 'Edycja wizyt', 'Zarządzanie rolami'])
        wynik: 3 -> Wyjaśnienie: Tabela zawiera uprawnienia:

        Dodawanie pacjentów → istnieje.
        Edycja wizyt → istnieje.
        Zarządzanie rolami → istnieje.
        """
        SystemPermissionsValidation.validate_database_connection(self.db_controller)
        SystemPermissionsValidation.validate_operator_and_value("IN", names)
        placeholders = ", ".join(["?"] * len(names))
        query = f"SELECT COUNT(*) as count FROM system_permissions WHERE permission_name IN ({placeholders})"

        cursor = self.db_controller.connection.execute(query, names)
        return cursor.fetchone()["count"]
