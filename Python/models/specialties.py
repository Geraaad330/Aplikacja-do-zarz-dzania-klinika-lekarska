# specialties.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.specialties_model_validation import (
    validate_specialty_name,
    validate_unique_specialty_name,
    validate_filters_and_sorting,
    validate_update_fields,
    validate_profession,
)


def get_valid_columns(db_controller, table_name: str) -> list:
    """
    Pobiera listę kolumn dla podanej tabeli z bazy danych.
    :param db_controller: Obiekt kontrolera bazy danych.
    :param table_name: Nazwa tabeli.
    :return: Lista nazw kolumn.
    """
    db_controller.ensure_connection()
    query = f"PRAGMA table_info({table_name})"
    cursor = db_controller.connection.execute(query)
    return [row["name"] for row in cursor.fetchall()]

class Specialties:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `specialties` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Specialties z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `specialties` w bazie danych, jeśli jeszcze nie istnieje.
        
        Przykład:
        specialties.create_table()
        
        Wynik:
        Utworzona tabela `specialties` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("specialties"):
                query = """
                CREATE TABLE IF NOT EXISTS specialties (
                    specialty_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    specialty_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (specialty_name GLOB '*[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def create_new_record(self, specialty_name: str, is_active=True):
        """
        Tworzy nowy rekord w tabeli `specialties`.

        Przykład:
        specialties.create_new_record("Psychiatra dorosłych")

        Wynik:
        Nowy rekord w tabeli `specialties`.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("specialties"):
                raise RuntimeError("Tabela 'specialties' nie istnieje w bazie danych.")
            validate_specialty_name(specialty_name)
            validate_unique_specialty_name(self.db_controller, specialty_name)
            query = "INSERT INTO specialties (specialty_name, is_active) VALUES (?, ?)"
            self.db_controller.connection.execute(query, (specialty_name, is_active))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            raise ValueError(f"Błąd podczas dodawania rekordu: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas dodawania rekordu: {e}") from e


    def get_specialty_name_by_id(self, specialty_id):
        """
        Pobiera nazwę specjalizacji na podstawie specialty_id.

        Args:
            specialty_id (int): ID specjalizacji.

        Returns:
            str: Nazwa specjalizacji, jeśli istnieje, w przeciwnym razie None.
        """
        try:
            # Upewnij się, że połączenie z bazą danych jest aktywne
            self.db_controller.ensure_connection()

            # Zapytanie SQL
            query = """
            SELECT specialty_name
            FROM specialties
            WHERE specialty_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (specialty_id,))
            result = cursor.fetchone()

            if result:
                specialty_name = result[0]  # Pobiera nazwę specjalizacji
                # print(f"model Specialties: Pobrano nazwę specjalizacji dla specialty_id {specialty_id}: {specialty_name}")  # Debug
                return specialty_name
            else:
                print(f"Nie znaleziono specjalizacji dla specialty_id {specialty_id}")  # Debug
                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania nazwy specjalizacji dla specialty_id {specialty_id}: {e}") from e



    def get_records(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `specialties`.

        Przykład:
        specialties.get_records(filters=[{"column": "specialty_name", "operator": "LIKE", "value": "Psych%"}])

        Wynik:
        Lista rekordów zgodnych z zapytaniem.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("specialties"):
                raise RuntimeError("Tabela 'specialties' nie istnieje w bazie danych.")
            valid_columns = get_valid_columns(self.db_controller, "specialties")  # Pobierz kolumny dynamicznie
            validate_filters_and_sorting(filters, sort_by, valid_columns)
            query, values = self.db_controller.build_filters(filters, sort_by)
            cursor = self.db_controller.connection.execute(f"SELECT * FROM specialties WHERE {query}", values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e




    def update_record(self, specialty_id: int, updates: dict):
        """
        Aktualizuje rekord w tabeli `specialties` na podstawie ID.
        """
        try:
            if not updates:
                raise ValueError("Nie podano danych do aktualizacji.")

            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM specialties WHERE specialty_id = ?"
            cursor = self.db_controller.connection.execute(query, (specialty_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {specialty_id} nie istnieje.")

            # Walidacja danych aktualizacji za pomocą validate_update_fields
            valid_columns = get_valid_columns(self.db_controller, "specialties")
            validate_update_fields(updates, valid_columns)


            # Walidacja danych aktualizacji
            valid_columns = get_valid_columns(self.db_controller, "specialties")
            for column, value in updates.items():
                if column not in valid_columns:
                    raise ValueError(f"Nieprawidłowa kolumna: {column}")
                if column == "specialty_name":
                    validate_specialty_name(value)

            # Aktualizacja rekordu
            set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
            query = f"UPDATE specialties SET {set_clause} WHERE specialty_id = ?"
            params = list(updates.values()) + [specialty_id]
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizowania rekordu: {e}") from e




    def delete_record(self, specialty_id: int):
        """
        Usuwa rekord z tabeli `specialties` na podstawie ID.

        :param specialty_id: ID specjalności do usunięcia.
        :raises RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM specialties WHERE specialty_id = ?"
            cursor = self.db_controller.connection.execute(query, (specialty_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {specialty_id} nie istnieje.")

            # Usunięcie rekordu
            query = "DELETE FROM specialties WHERE specialty_id = ?"
            
            self.db_controller.connection.execute(query, (specialty_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e



    def count_specialties_for_all_professions(self):
        """
        Zlicza unikalne specjalności dla każdego dostępnego zawodu.

        :return: Lista słowników zawierających zawód i liczbę unikalnych specjalności.

        Przykład:
        specialties.count_specialties_for_all_professions()

        Wynik:
        [
            {"profession": "Psychiatra", "number_of_specialties": 2},
            {"profession": "Psycholog kliniczny", "number_of_specialties": 2},
            {"profession": "Psychoterapeuta", "number_of_specialties": 3},
        ]

            Gdybyśmy użyli prostego COUNT(es.specialty_id) (bez DISTINCT), specjalność zostałaby zliczona dwa razy. Aby tego uniknąć:
            Rozwiązanie: Użycie COUNT(DISTINCT es.specialty_id) w SQL, co sprawi, że każda specjalność będzie liczona tylko raz, niezależnie od 
            liczby pracowników, którzy ją mają.

        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("specialties"):
                raise RuntimeError("Tabela 'specialties' nie istnieje w bazie danych.")
            query = """
            SELECT e.profession, COUNT(DISTINCT es.specialty_id) AS number_of_specialties
            FROM employees e
            JOIN employee_specialties es ON e.employee_id = es.employee_id
            JOIN specialties s ON es.specialty_id = s.specialty_id
            GROUP BY e.profession
            """
            cursor = self.db_controller.connection.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas zliczania specjalności: {e}") from e


    def get_available_professions(self):
        """
        Pobiera dynamiczną listę wszystkich dostępnych zawodów z tabeli `employees`.

        :return: Lista dostępnych zawodów.

        Przykład:
        specialties.get_available_professions()

        Wynik:
        ["Psychiatra", "Psycholog kliniczny", "Psychoterapeuta"]
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("specialties"):
                raise RuntimeError("Tabela 'specialties' nie istnieje w bazie danych.")
            query = "SELECT DISTINCT profession FROM employees"
            cursor = self.db_controller.connection.execute(query)
            return [row["profession"] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania listy zawodów: {e}") from e

    def count_specialties_for_profession(self, profession: str):
        """
        Zlicza specjalności na podstawie podanego zawodu, weryfikując jego istnienie w bazie.

        :param profession: Nazwa zawodu, np. "Psychiatra".
        :return: Lista słowników zawierających nazwę specjalności i liczbę wystąpień.

        Przykład:
        specialties.count_specialties_for_profession("Psychiatra")

        Wynik:
        [
            {"specialty_name": "Psychiatra dorosłych", "number_of_occurrences": 3},
            {"specialty_name": "Psychiatra dzieci i młodzieży", "number_of_occurrences": 2},
        ]
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("specialties"):
                raise RuntimeError("Tabela 'specialties' nie istnieje w bazie danych.")
            available_professions = self.get_available_professions()
            validate_profession(profession, available_professions)
            # Sprawdź, czy zawód istnieje w bazie
            available_professions = self.get_available_professions()
            if profession not in available_professions:
                raise ValueError(f"Zawód '{profession}' nie istnieje w bazie danych.")

            # Zlicz specjalności dla podanego zawodu
            query = """
            SELECT s.specialty_name, COUNT(es.specialty_id) AS number_of_occurrences
            FROM employees e
            JOIN employee_specialties es ON e.employee_id = es.employee_id
            JOIN specialties s ON es.specialty_id = s.specialty_id
            WHERE e.profession = ?
            GROUP BY s.specialty_name
            """
            cursor = self.db_controller.connection.execute(query, (profession,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas zliczania specjalności dla zawodu '{profession}': {e}") from e


    def get_all_specialty_names(self):
        """
        Pobiera wszystkie unikalne `specialty_name` z tabeli `specialties`.

        :return: Lista specjalności.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        query = "SELECT DISTINCT specialty_name FROM specialties ORDER BY specialty_name ASC"
        try:
            cursor = self.db_controller.connection.execute(query)
            specialty_names = [row[0] for row in cursor.fetchall()]
            return specialty_names
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania specjalności: {db_error}") from db_error

    def get_all_specialty_ids(self):
        """
        Pobiera wszystkie `specialty_id` z tabeli `specialties`.
        Zwraca listę ID specjalności.

        :return: Lista specialty_id.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        query = "SELECT specialty_id FROM specialties ORDER BY specialty_id ASC"

        try:
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query)
            specialty_ids = [row[0] for row in cursor.fetchall()]
            return specialty_ids

        except sqlite3.OperationalError as oe:
            raise RuntimeError(f"Błąd operacyjny podczas pobierania specialty_id: {oe}") from oe
        except sqlite3.DatabaseError as de:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania specialty_id: {de}") from de
        
    def get_specialty_by_id(self, specialty_id: int):
        """
        Pobiera wszystkie kolumny rekordu w tabeli `specialties` dla podanego specialty_id.

        :param specialty_id: ID specjalności do pobrania.
        :return: Słownik z danymi specjalności lub None, jeśli nie znaleziono.
        :raises ValueError: Jeśli specialty_id jest niepoprawne.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        if not isinstance(specialty_id, int) or specialty_id <= 0:
            raise ValueError("Niepoprawne specialty_id. ID musi być liczbą całkowitą większą od 0.")

        query = "SELECT * FROM specialties WHERE specialty_id = ?"

        try:
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query, (specialty_id,))
            specialty = cursor.fetchone()

            if specialty:
                return dict(specialty)  # Konwersja rekordu na słownik
            return None

        except sqlite3.OperationalError as oe:
            raise RuntimeError(f"Błąd operacyjny podczas pobierania danych specjalności: {oe}") from oe
        except sqlite3.DatabaseError as de:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania danych specjalności: {de}") from de