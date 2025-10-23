# rooms.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.room_types_controller import RoomTypesController
from validators.rooms_model_validation import (
    validate_room_number,
    validate_floor,
    validate_fk_room_type_id,
    validate_unique_room_number,
    validate_room_type_exists,
    validate_room_type,
    validate_filters_and_sorting
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


class Rooms:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `rooms` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Rooms z kontrolerem bazy danych.
        """
        self.db_controller = db_controller
        self.room_types_controller = RoomTypesController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `rooms` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("rooms"):
                query = """
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_number INTEGER NOT NULL UNIQUE CHECK (room_number BETWEEN 0 AND 100),
                    floor INTEGER NOT NULL CHECK (floor BETWEEN 0 AND 2),
                    fk_room_type_id INTEGER,
                    FOREIGN KEY (fk_room_type_id) REFERENCES room_types(room_type_id) ON UPDATE CASCADE ON DELETE SET NULL
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e



    def add_room_by_ids(self, room_number: int, floor: int, fk_room_type_id: int):
        """
        Dodaje nowy rekord do tabeli `rooms` z podaniem ID typu pokoju.
        """
        try:
            # Walidacje
            validate_room_number(room_number)
            validate_floor(floor)
            validate_fk_room_type_id(fk_room_type_id)
            validate_unique_room_number(self.db_controller, room_number)
            validate_room_type_exists(self.room_types_controller, fk_room_type_id)

            # Dodanie pokoju
            query = """
            INSERT INTO rooms (room_number, floor, fk_room_type_id)
            VALUES (?, ?, ?)
            """
            self.db_controller.connection.execute(query, (room_number, floor, fk_room_type_id))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania pokoju: {e}") from e





    def add_room_by_name(self, room_number: int, floor: int, room_type_name: str):
        """
        Dodaje nowy rekord do tabeli `rooms` z podaniem nazwy typu pokoju.

        Args:
            room_number (int): Numer pokoju.
            floor (int): Piętro, na którym znajduje się pokój.
            room_type_name (str): Nazwa typu pokoju.

        Raises:
            ValueError: Jeśli walidacja któregokolwiek pola się nie powiedzie.
            RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            # Walidacje
            validate_room_number(room_number)  # Walidacja numeru pokoju
            validate_floor(floor)  # Walidacja piętra
            validate_room_type(room_type_name)  # Walidacja nazwy typu pokoju

            # Pobranie ID typu pokoju za pomocą kontrolera
            room_types = self.room_types_controller.get_all_room_types()
            room_type = next((rt for rt in room_types if rt["room_type"] == room_type_name), None)

            if not room_type:
                raise ValueError(f"Typ pokoju '{room_type_name}' nie istnieje.")

            fk_room_type_id = room_type["room_type_id"]

            # Dodanie pokoju za pomocą ID
            self.add_room_by_ids(room_number, floor, fk_room_type_id)
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas dodawania pokoju: {e}") from e







    

    def get_rooms_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera dowolne rekordy z tabeli `rooms` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            # Pobranie dozwolonych kolumn
            valid_columns = get_valid_columns(self.db_controller, "rooms")

            # Walidacje
            validate_filters_and_sorting(filters, sort_by, valid_columns)

            # Pobieranie danych
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM rooms WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e


    def get_rooms_with_room_type_names(self, filters=None, sort_by=None):
        """
        Pobiera pokoje z tabeli `rooms`, zastępując ID typu pokoju nazwą.
        """
        try:
            self.db_controller.ensure_connection()

            # Budowanie warunku zapytania na podstawie filtrów
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)

            query = f"""
            SELECT
                r.room_id,
                r.room_number,
                r.floor,
                rt.room_type AS room_type_name
            FROM rooms r
            LEFT JOIN room_types rt ON r.fk_room_type_id = rt.room_type_id
            WHERE {query_conditions}
            """
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z nazwami: {e}") from e


    def get_room_type_id(self, room_type_name: str) -> int:
        """
        Pobiera ID typu pokoju na podstawie jego nazwy za pomocą kontrolera `room_types_controller`.

        Args:
            room_type_name (str): Nazwa typu pokoju.

        Returns:
            int: ID typu pokoju.

        Przykład:
            get_room_type_id("Konferencyjny") -> 1
        """
        try:
            room_types = self.room_types_controller.get_all_room_types()
            room_type = next((rt for rt in room_types if rt["room_type_name"] == room_type_name), None)

            if not room_type:
                raise ValueError(f"Typ pokoju '{room_type_name}' nie istnieje.")

            return room_type["room_type_id"]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania ID typu pokoju: {e}") from e

    def update_room_by_ids(self, room_id: int, data_to_update: dict):
        """
        Aktualizuje pokój w bazie na podstawie ID i przekazanych pól do aktualizacji.
        :param room_id: ID pokoju do aktualizacji.
        :param data_to_update: Słownik zawierający pola do aktualizacji.
        """
        try:
            # Budowanie dynamicznego zapytania SQL
            set_clause = ", ".join([f"{key} = ?" for key in data_to_update.keys()])
            values = list(data_to_update.values()) + [room_id]

            query = f"UPDATE rooms SET {set_clause} WHERE room_id = ?"
            self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()

        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji pokoju.") from db_error






    def delete_room(self, room_id: int):
        """
        Usuwa rekord z tabeli `rooms` na podstawie room_id.

        Args:
            room_id (int): ID pokoju, który ma zostać usunięty.

        Przykład:
            delete_room(1)
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy rekord istnieje
            query_check = "SELECT COUNT(*) FROM rooms WHERE room_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (room_id,))
            if cursor.fetchone()[0] == 0:
                raise KeyError("Pokój o podanym ID nie istnieje.")

            # Usunięcie rekordu
            query_delete = "DELETE FROM rooms WHERE room_id = ?"
            self.db_controller.connection.execute(query_delete, (room_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania pokoju: {e}") from e

    def get_room_by_id(self, room_id):
        """
        Pobiera rekord pokoju na podstawie podanego `room_id`.

        :param room_id: ID pokoju do wyszukania.
        :return: Słownik zawierający dane pokoju lub None, jeśli nie znaleziono.
        """
        try:
            query = "SELECT * FROM rooms WHERE room_id = ?"
            cursor = self.db_controller.connection.execute(query, (room_id,))
            room = cursor.fetchone()

            if room is None:
                print(f"[### ROOMS_MODEL] Pokój o ID {room_id} nie istnieje w bazie.")
                return None

            room_data = dict(room)  # Konwersja `sqlite3.Row` na `dict`
            print(f"[### ROOMS_MODEL] Pobranie pokoju: {room_data}")
            return room_data

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOMS_MODEL] Błąd operacyjny bazy danych: {op_err}")
            return None

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOMS_MODEL] Błąd bazy danych: {db_err}")
            return None
