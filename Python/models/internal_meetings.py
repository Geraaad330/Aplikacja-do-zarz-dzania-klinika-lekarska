# internal_meetings.py

import sqlite3
from validators.internal_meetings_model_validation import (
    validate_filters_and_sorting,
    validate_operator_and_value
)
from controllers.database_controller import DatabaseController


class InternalMeetings:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `internal_meetings` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy InternalMeetings z kontrolerem bazy danych.
        """
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `internal_meetings` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("internal_meetings"):
                query = """
                CREATE TABLE IF NOT EXISTS internal_meetings (
                    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_meeting_type_id INTEGER NOT NULL,
                    fk_room_id INTEGER NOT NULL,
                    start_meeting_date TEXT NOT NULL,
                    end_meeting_date TEXT NOT NULL,
                    notes TEXT,
                    internal_meeting_status TEXT NOT NULL,
                    FOREIGN KEY (fk_meeting_type_id) REFERENCES meeting_types(meeting_type_id)
                        ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e




    def add_meeting(self, fk_meeting_type_id, fk_reservation_id, meeting_date, notes, internal_meeting_status):
        """
        Dodaje nowy rekord do tabeli `internal_meetings`.

        Args:
            fk_meeting_type_id (int): ID typu spotkania.
            fk_room_id (int): ID pokoju.
            start_meeting_date (str): Data rozpoczęcia spotkania (format: YYYY-MM-DD HH:MM).
            end_meeting_date (str): Data zakończenia spotkania (format: YYYY-MM-DD HH:MM).
            notes (str): Notatki dotyczące spotkania.
            internal_meeting_status (str): Status spotkania.

        Returns:
            int: ID nowo dodanego spotkania.
        """
        try:
            # Walidacje

            self.db_controller.ensure_connection()
            query = """
            INSERT INTO internal_meetings (fk_meeting_type_id, fk_reservation_id, meeting_date, notes, internal_meeting_status)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(query, (fk_meeting_type_id, fk_reservation_id, meeting_date, notes, internal_meeting_status))
            self.db_controller.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania spotkania: {e}") from e

    def get_meetings(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `internal_meetings` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów.
            sort_by (list): Lista sortowania.

        Returns:
            list: Lista rekordów w formie słowników.
        """
        try:
            # Walidacja filtrów i sortowania
            valid_columns = ["meeting_id", "fk_meeting_type_id", "fk_room_id", "start_meeting_date", "end_meeting_date", "notes", "internal_meeting_status"]
            validate_filters_and_sorting(filters, sort_by, valid_columns)

            if filters:
                for filter_item in filters:
                    validate_operator_and_value(filter_item["operator"], filter_item.get("value"))

            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM internal_meetings WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania spotkań: {e}") from e

    def update_meeting(self, meeting_id: int, fk_meeting_type_id: int = None, fk_reservation_id: int = None, 
                    meeting_date: str = None, notes: str = None, internal_meeting_status: str = None):
        """
        Aktualizuje rekord w tabeli `internal_meetings` na podstawie `meeting_id`.

        Args:
            meeting_id (int): ID spotkania do aktualizacji.
            fk_meeting_type_id (int, opcjonalnie): Nowe ID typu spotkania.
            fk_reservation_id (int, opcjonalnie): Nowe ID rezerwacji.
            meeting_date (str, opcjonalnie): Nowa data spotkania (format: YYYY-MM-DD HH:MM).
            notes (str, opcjonalnie): Nowe notatki dotyczące spotkania.
            internal_meeting_status (str, opcjonalnie): Nowy status spotkania.

        Returns:
            bool: True jeśli aktualizacja zakończyła się sukcesem, False jeśli nie dokonano zmian.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy rekord z `meeting_id` istnieje
            query_check = "SELECT 1 FROM internal_meetings WHERE meeting_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (meeting_id,))
            if cursor.fetchone() is None:
                raise RuntimeError(f"Rekord z podanym ID {meeting_id} nie istnieje.")

            # Tworzenie słownika z danymi do aktualizacji
            fields = {}
            if fk_meeting_type_id is not None:
                fields["fk_meeting_type_id"] = fk_meeting_type_id
            if fk_reservation_id is not None:
                fields["fk_reservation_id"] = fk_reservation_id
            if meeting_date is not None:
                fields["meeting_date"] = meeting_date
            if notes is not None:
                fields["notes"] = notes
            if internal_meeting_status is not None:
                fields["internal_meeting_status"] = internal_meeting_status

            if not fields:
                raise ValueError("Brak danych do aktualizacji.")

            set_clause = ", ".join([f"{column} = ?" for column in fields.keys()])
            values = list(fields.values()) + [meeting_id]

            query = f"UPDATE internal_meetings SET {set_clause} WHERE meeting_id = ?"
            self.db_controller.connection.execute(query, values)
            self.db_controller.connection.commit()

            return True  # Aktualizacja zakończona sukcesem

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji spotkania: {e}") from e




    def delete_meeting(self, meeting_id):
        """
        Usuwa rekord z tabeli `internal_meetings` na podstawie meeting_id.

        Args:
            meeting_id (int): ID spotkania do usunięcia.
        """
        try:
            self.db_controller.ensure_connection()
            query_check = "SELECT 1 FROM internal_meetings WHERE meeting_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (meeting_id,))
            if cursor.fetchone() is None:
                raise RuntimeError(f"Rekord z podanym ID {meeting_id} nie istnieje.")

            query_delete = "DELETE FROM internal_meetings WHERE meeting_id = ?"
            self.db_controller.connection.execute(query_delete, (meeting_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania spotkania: {e}") from e


    def get_meeting_by_id(self, meeting_id):
        """
        Pobiera wszystkie kolumny rekordu z tabeli `internal_meetings` na podstawie `meeting_id`.

        :param meeting_id: ID spotkania do pobrania.
        :return: Słownik zawierający dane spotkania lub None, jeśli nie znaleziono.
        """
        try:
            query = "SELECT * FROM internal_meetings WHERE meeting_id = ?"
            cursor = self.db_controller.connection.execute(query, (meeting_id,))
            meeting = cursor.fetchone()

            if meeting is None:
                print(f"[### INTERNAL_MEETINGS_MODEL] Spotkanie o ID {meeting_id} nie istnieje w bazie.")
                return None

            meeting_data = dict(meeting)  # Konwersja `sqlite3.Row` na `dict`
            print(f"[### INTERNAL_MEETINGS_MODEL] Pobranie spotkania: {meeting_data}")
            return meeting_data

        except sqlite3.OperationalError as op_err:
            print(f"[### INTERNAL_MEETINGS_MODEL] Błąd operacyjny bazy danych: {op_err}")
            return None

        except sqlite3.DatabaseError as db_err:
            print(f"[### INTERNAL_MEETINGS_MODEL] Błąd bazy danych: {db_err}")
            return None
