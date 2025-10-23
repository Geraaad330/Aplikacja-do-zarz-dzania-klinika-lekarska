# room_types.py# room_types.py

import sqlite3
from controllers.database_controller import DatabaseController
from validators.room_types_model_validation import (
    validate_room_type,
    validate_unique_room_type,
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


class RoomTypes:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `room_types` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy room_types z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `room_types` w bazie danych, jeśli jeszcze nie istnieje.
        
        Przykład:
        room_types.create_table()
        
        Wynik:
        Utworzona tabela `room_types` w bazie danych, jeśli nie istniała.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("room_types"):
                query = """
                CREATE TABLE IF NOT EXISTS room_types (
                    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (room_type GLOB '*[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def create_new_record(self, room_type: str):
        """
        Tworzy nowy rekord w tabeli `room_types`.

        Przykład:
        room_types.create_new_record("Gabinet diagnostyczny")

        Wynik:
        Nowy rekord w tabeli `room_types`.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("room_types"):
                raise RuntimeError("Tabela 'room_types' nie istnieje w bazie danych.")
            validate_room_type(room_type)
            validate_unique_room_type(self.db_controller, room_type)
            query = "INSERT INTO room_types (room_type) VALUES (?)"
            self.db_controller.connection.execute(query, (room_type,))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            self.db_controller.connection.rollback()
            raise ValueError(f"Błąd podczas dodawania rekordu: {e}") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd bazy danych podczas dodawania rekordu: {e}") from e

    def get_records(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `room_types`.

        Przykład:
        room_types.get_records(filters=[{"column": "room_type", "operator": "LIKE", "value": "Psych%"}])

        Wynik:
        Lista rekordów zgodnych z zapytaniem.
        """
        try:

            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("room_types"):
                raise RuntimeError("Tabela 'room_types' nie istnieje w bazie danych.")
            valid_columns = get_valid_columns(self.db_controller, "room_types")  # Pobierz kolumny dynamicznie
            validate_filters_and_sorting(filters, sort_by, valid_columns)
            query, values = self.db_controller.build_filters(filters, sort_by)
            cursor = self.db_controller.connection.execute(f"SELECT * FROM room_types WHERE {query}", values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e



    def update_room_type(self, room_type_id: int, new_room_type: str):
        """
        Aktualizuje nazwę typu pokoju w tabeli `room_types`.

        :param room_type_id: ID typu pokoju do aktualizacji.
        :param new_room_type: Nowa nazwa typu pokoju.
        :raises RuntimeError: Jeśli rekord o podanym ID nie istnieje lub wystąpił błąd bazy danych.
        """
        try:
            # Aktualizacja typu pokoju
            query_update = "UPDATE room_types SET room_type = ? WHERE room_type_id = ?"
            self.db_controller.connection.execute(query_update, (new_room_type, room_type_id))
            self.db_controller.connection.commit()

        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {op_err}") from op_err

        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych: {db_err}") from db_err




    def delete_record(self, room_type_id: int):
        """
        Usuwa rekord z tabeli `room_types` na podstawie ID.

        :param room_type_id: ID specjalności do usunięcia.
        :raises RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            # Sprawdzenie istnienia rekordu
            query = "SELECT COUNT(*) FROM room_types WHERE room_type_id = ?"
            cursor = self.db_controller.connection.execute(query, (room_type_id,))
            if cursor.fetchone()[0] == 0:
                raise RuntimeError(f"Rekord o ID {room_type_id} nie istnieje.")

            # Usunięcie rekordu
            query = "DELETE FROM room_types WHERE room_type_id = ?"
            
            self.db_controller.connection.execute(query, (room_type_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e