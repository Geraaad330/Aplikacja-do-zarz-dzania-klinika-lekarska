# meeting_participants.py

import sqlite3
from controllers.database_controller import DatabaseController

from validators.meeting_participants_model_validation import (
    validate_attendance,
    validate_participant_role,
    validate_fk_meeting_id_exists,
    validate_fk_employee_id_exists,
    validate_update_fields,
    validate_filters_and_sorting,
    validate_operator_and_value,
)


class MeetingParticipants:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `meeting_participants` w kontekście operacji CRUD.
    """
    def __init__(self, db_controller: DatabaseController):
        self.db_controller = db_controller

    def create_table(self):
        """
        Tworzy tabelę `meeting_participants` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("meeting_participants"):
                query = """
                CREATE TABLE IF NOT EXISTS meeting_participants (
                    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_meeting_id INTEGER NOT NULL,
                    fk_employee_id INTEGER NOT NULL,
                    participant_role TEXT NOT NULL CHECK (participant_role GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]*'),
                    attendance TEXT NOT NULL CHECK (attendance GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]*'),
                    FOREIGN KEY (fk_meeting_id) REFERENCES internal_meetings(meeting_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (fk_employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def get_meetings_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie fk_meeting_id, do których przypisany jest podany employee_id.

        Args:
            employee_id (int): ID pracownika.

        Returns:
            list: Lista fk_meeting_id przypisanych do pracownika.
        """
        try:
            # Walidacja employee_id
            if not isinstance(employee_id, int) or employee_id <= 0:
                raise ValueError("Nieprawidłowy identyfikator pracownika. Musi być liczbą całkowitą większą od zera.")

            self.db_controller.ensure_connection()

            # Zapytanie do bazy danych
            query = """
            SELECT fk_meeting_id
            FROM meeting_participants
            WHERE fk_employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (employee_id,))
            results = [row["fk_meeting_id"] for row in cursor.fetchall()]  # Pobranie wszystkich meeting_id

            # Debugowanie: Wyświetl pobrane dane
            # print(f"MODEL PARTICITANST Debug: Pobrane ID spotkań: {results} dla employee_id: {employee_id}")

            return results
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania spotkań dla employee_id={employee_id}: {e}") from e
        except ValueError as ve:
            raise RuntimeError(f"Wartość nieprawidłowa: {ve}") from ve


    def add_participant(self, fk_meeting_id, fk_employee_id, participant_role, attendance):
        """
        Tworzy tabelę `meeting_participants` w bazie danych, jeśli jeszcze nie istnieje.
        """ 
        try:
            # Walidacje
            validate_fk_meeting_id_exists(self.db_controller, fk_meeting_id)
            validate_fk_employee_id_exists(self.db_controller, fk_employee_id)
            validate_participant_role(participant_role)
            validate_attendance(attendance)

            self.db_controller.ensure_connection()
            query = """
            INSERT INTO meeting_participants (fk_meeting_id, fk_employee_id, participant_role, attendance)
            VALUES (?, ?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(query, (fk_meeting_id, fk_employee_id, participant_role, attendance))
            self.db_controller.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania uczestnika: {e}") from e

    def update_participant(self, participant_id, fk_meeting_id=None, fk_employee_id=None, participant_role=None, attendance=None):
        """
        Aktualizuje rekord w tabeli `meeting_participants`.

        Args:
            participant_id (int): ID uczestnika do aktualizacji.
            fk_meeting_id (int, opcjonalnie): Nowe ID spotkania.
            fk_employee_id (int, opcjonalnie): Nowe ID pracownika.
            participant_role (str, opcjonalnie): Nowa rola uczestnika.
            attendance (str, opcjonalnie): Nowy status obecności.

        Returns:
            None
        """
        try:
            # Sprawdzenie, czy rekord istnieje
            self.db_controller.ensure_connection()
            query_check = "SELECT COUNT(1) FROM meeting_participants WHERE participant_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (participant_id,))
            record_exists = cursor.fetchone()[0]

            if not record_exists:
                raise RuntimeError(f"Rekord o participant_id={participant_id} nie istnieje w bazie danych.")

            # Tworzenie słownika danych do aktualizacji
            updates = {}
            if fk_meeting_id is not None:
                validate_fk_meeting_id_exists(self.db_controller, fk_meeting_id)
                updates["fk_meeting_id"] = fk_meeting_id
            if fk_employee_id is not None:
                validate_fk_employee_id_exists(self.db_controller, fk_employee_id)
                updates["fk_employee_id"] = fk_employee_id
            if participant_role is not None:
                validate_participant_role(participant_role)
                updates["participant_role"] = participant_role
            if attendance is not None:
                validate_attendance(attendance)
                updates["attendance"] = attendance

            validate_update_fields(updates, ["fk_meeting_id", "fk_employee_id", "participant_role", "attendance"])

            # Aktualizacja rekordu
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [participant_id]
            query_update = f"UPDATE meeting_participants SET {set_clause} WHERE participant_id = ?"
            self.db_controller.connection.execute(query_update, values)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas aktualizacji uczestnika: {e}") from e


    def get_participants(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `meeting_participants` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów w formacie [{"column": ..., "operator": ..., "value": ...}].
            sort_by (list): Lista sortowania w formacie [{"column": ..., "direction": ...}].

        Returns:
            list: Lista rekordów w formie słowników.
        """
        try:
            # Walidacja filtrów i sortowania
            valid_columns = ["participant_id", "fk_meeting_id", "fk_employee_id", "participant_role", "attendance"]
            if filters:
                for filter_item in filters:
                    if "column" in filter_item and "operator" in filter_item:
                        # Walidacja operatora i wartości
                        validate_operator_and_value(filter_item["operator"], filter_item.get("value"))
                    else:
                        raise ValueError("Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'.")

            validate_filters_and_sorting(filters, sort_by, valid_columns)

            # Przygotowanie zapytania SQL
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM meeting_participants WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania uczestników: {e}") from e


    def delete_participant(self, participant_id):
        """
        Usuwa rekord z tabeli `meeting_participants`.

        Args:
            participant_id (int): ID uczestnika do usunięcia.

        Returns:
            None

        Raises:
            ValueError: Jeśli participant_id jest nieprawidłowe.
            RuntimeError: Jeśli rekord o podanym ID nie istnieje.
        """
        try:
            # Walidacja participant_id
            if not isinstance(participant_id, int) or participant_id <= 0:
                raise ValueError("Nieprawidłowy identyfikator uczestnika. Musi być liczbą całkowitą większą od zera.")

            # Sprawdzenie, czy rekord istnieje
            self.db_controller.ensure_connection()
            query_check = "SELECT COUNT(1) FROM meeting_participants WHERE participant_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (participant_id,))
            record_exists = cursor.fetchone()[0]

            if not record_exists:
                raise RuntimeError(f"Rekord o participant_id={participant_id} nie istnieje w bazie danych.")

            # Usuwanie rekordu
            query = "DELETE FROM meeting_participants WHERE participant_id = ?"
            self.db_controller.connection.execute(query, (participant_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania uczestnika: {e}") from e

    def get_participant_by_id(self, participant_id: int) -> dict:
        """
        Pobiera szczegóły uczestnika spotkania na podstawie `participant_id`.

        :param participant_id: ID uczestnika spotkania do pobrania.
        :return: Słownik z danymi uczestnika lub pusty słownik, jeśli uczestnik nie istnieje.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            query = "SELECT * FROM meeting_participants WHERE participant_id = ?"
            cursor = self.db_controller.connection.execute(query, (participant_id,))
            participant = cursor.fetchone()

            if participant is None:
                print(f"[### MEETING_PARTICIPANTS_MODEL] Uczestnik o ID {participant_id} nie istnieje w bazie.")
                return {}

            participant_data = dict(participant)  # Konwersja `sqlite3.Row` na `dict`
            print(f"[### MEETING_PARTICIPANTS_MODEL] Pobranie uczestnika: {participant_data}")
            return participant_data

        except sqlite3.OperationalError as op_err:
            print(f"[### MEETING_PARTICIPANTS_MODEL] Błąd operacyjny bazy danych: {op_err}")
            return {}

        except sqlite3.DatabaseError as db_err:
            print(f"[### MEETING_PARTICIPANTS_MODEL] Błąd bazy danych: {db_err}")
            return {}
