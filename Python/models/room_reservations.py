# room_reservations.py

import sqlite3
from controllers.database_controller import DatabaseController
#pylint: disable=E0401
#pylint: disable=E0611
from validators.room_reservations_model_validation import (
    validate_reservation_date,
    validate_reservation_time,
    validate_fk_room_id_exists,
)


class RoomReservations:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `room_reservations` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `room_reservations` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("room_reservations"):
                query = """
                CREATE TABLE IF NOT EXISTS room_reservations (
                    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_room_id INTEGER NOT NULL,
                    fk_appointment_id INTEGER,
                    fk_meeting_id INTEGER,
                    reservation_date TEXT NOT NULL,
                    reservation_time TEXT NOT NULL,
                    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (fk_appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (fk_meeting_id) REFERENCES internal_meetings(meeting_id) ON DELETE CASCADE ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def add_reservation(self, fk_room_id, reservation_date, reservation_time):
        """
        Dodaje nową rezerwację do tabeli `room_reservations`.

        Args:
            fk_room_id (int): ID pokoju.
            fk_appointment_id (int | None): ID wizyty.
            fk_meeting_id (int | None): ID spotkania.
            reservation_date (str): Data rezerwacji.
            reservation_time (str): Czas rezerwacji.

        Returns:
            int: ID nowo dodanej rezerwacji.
        """
        try:
            # Walidacje
            # Dodanie rezerwacji
            self.db_controller.ensure_connection()
            query = """
            INSERT INTO room_reservations (fk_room_id, reservation_date, reservation_time)
            VALUES (?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(
                query, (fk_room_id, reservation_date, reservation_time)
            )
            self.db_controller.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania rezerwacji: {e}") from e

    def get_reservations(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `room_reservations` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów w formacie [{"column": ..., "operator": ..., "value": ...}].
            sort_by (list): Lista sortowania w formacie [{"column": ..., "direction": ...}].

        Returns:
            list: Lista rekordów w formie słowników.
        """
        try:
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM room_reservations WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rezerwacji: {e}") from e

    def update_reservation(self, reservation_id, fk_room_id=None, reservation_date=None, reservation_time=None):
        """
        Aktualizuje rekord w tabeli `room_reservations`.

        Args:
            reservation_id (int): ID rezerwacji do aktualizacji.
            fk_room_id (int, opcjonalnie): Nowe ID pokoju.
            fk_appointment_id (int, opcjonalnie): Nowe ID wizyty.
            fk_meeting_id (int, opcjonalnie): Nowe ID spotkania.
            reservation_date (str, opcjonalnie): Nowa data rezerwacji.
            reservation_time (str, opcjonalnie): Nowy czas rezerwacji.

        Raises:
            RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy rekord istnieje
            query_check = "SELECT COUNT(*) FROM room_reservations WHERE reservation_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (reservation_id,))
            record_exists = cursor.fetchone()[0] > 0

            if not record_exists:
                raise RuntimeError(f"Nie znaleziono rekordu o podanym ID {reservation_id}.")

            updates = {}
            if fk_room_id is not None:
                validate_fk_room_id_exists(self.db_controller, fk_room_id)
                updates["fk_room_id"] = fk_room_id
            if reservation_date is not None:
                validate_reservation_date(reservation_date)
                updates["reservation_date"] = reservation_date
            if reservation_time is not None:
                validate_reservation_time(reservation_time)
                updates["reservation_time"] = reservation_time

            if not updates:
                raise ValueError("Brak danych do aktualizacji.")

            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [reservation_id]
            query = f"UPDATE room_reservations SET {set_clause} WHERE reservation_id = ?"
            self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rezerwacji: {e}") from e



    def delete_reservation(self, reservation_id):
        """
        Usuwa rekord z tabeli `room_reservations`.

        Args:
            reservation_id (int): ID rezerwacji do usunięcia.

        Raises:
            RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            # Sprawdzenie, czy rekord istnieje
            query_check = "SELECT COUNT(*) FROM room_reservations WHERE reservation_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (reservation_id,))
            record_exists = cursor.fetchone()[0] > 0

            if not record_exists:
                raise RuntimeError(f"Nie znaleziono rekordu o podanym ID {reservation_id}.")

            # Usunięcie rekordu
            query_delete = "DELETE FROM room_reservations WHERE reservation_id = ?"
            self.db_controller.connection.execute(query_delete, (reservation_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rezerwacji: {e}") from e

