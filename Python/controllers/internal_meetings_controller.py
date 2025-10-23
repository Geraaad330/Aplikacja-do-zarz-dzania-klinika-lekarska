# internal_meetings_controller.py

import sqlite3
from models.internal_meetings import InternalMeetings
from controllers.database_controller import DatabaseController


class InternalMeetingsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `internal_meetings`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `internal_meetings` oraz model zarządzający danymi `internal_meetings`.

        Args:
            db_controller (DatabaseController): Instancja kontrolera bazy danych.
        """
        self.db_controller = db_controller
        self.internal_meetings_model = InternalMeetings(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `internal_meetings` w bazie danych.
        """
        try:
            self.internal_meetings_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `internal_meetings`.") from db_error

    def add_meeting(self, fk_meeting_type_id: int, fk_reservation_id: int, meeting_date: str, notes: str, internal_meeting_status: str) -> int:
        """
        Wywołuje metodę modelu do dodania nowego spotkania.

        :param fk_meeting_type_id: ID typu spotkania.
        :param fk_reservation_id: ID rezerwacji.
        :param meeting_date: Data spotkania (format: YYYY-MM-DD HH:MM).
        :param notes: Notatki dotyczące spotkania.
        :param internal_meeting_status: Status spotkania.
        :return: ID nowo dodanego spotkania.
        :raises ValueError: Jeśli dane wejściowe są niepoprawne.
        :raises RuntimeError: Jeśli wystąpił błąd bazy danych.
        """
        try:
            # Sprawdzenie poprawności danych wejściowych
            if not isinstance(fk_meeting_type_id, int) or fk_meeting_type_id <= 0:
                raise ValueError("Nieprawidłowy format ID typu spotkania.")

            if not isinstance(fk_reservation_id, int) or fk_reservation_id <= 0:
                raise ValueError("Nieprawidłowy format ID rezerwacji.")

            if not isinstance(meeting_date, str) or not meeting_date.strip():
                raise ValueError("Nieprawidłowy format daty spotkania.")

            if not isinstance(notes, str):
                raise ValueError("Nieprawidłowy format notatek.")

            if not isinstance(internal_meeting_status, str) or not internal_meeting_status.strip():
                raise ValueError("Nieprawidłowy format statusu spotkania.")

            # Wywołanie metody modelu do dodania spotkania
            meeting_id = self.internal_meetings_model.add_meeting(
                fk_meeting_type_id, fk_reservation_id, meeting_date, notes, internal_meeting_status
            )

            return meeting_id

        except ValueError as ve:
            print(f"[InternalMeetingsController_add_meeting] Błąd danych wejściowych: {ve}")
            raise

        except RuntimeError as re:
            print(f"[InternalMeetingsController_add_meeting] Błąd bazy danych: {re}")
            raise


    def get_meetings(self, filters=None, sort_by=None):
        """
        Pobiera spotkania z tabeli `internal_meetings` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów.
            sort_by (list): Lista parametrów sortowania.

        Returns:
            list[dict]: Lista spotkań jako słowniki.
        """
        try:
            return self.internal_meetings_model.get_meetings(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania spotkań.") from db_error

    def update_meeting(self, meeting_id: int, fk_meeting_type_id: int = None, fk_reservation_id: int = None, 
                    meeting_date: str = None, notes: str = None, internal_meeting_status: str = None) -> bool:
        """
        Wywołuje metodę modelu do aktualizacji spotkania.

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
            # Walidacja `meeting_id`
            if not isinstance(meeting_id, int):
                raise ValueError(f"Nieprawidłowy format `meeting_id`: {meeting_id}. Oczekiwano liczby całkowitej.")

            # Wywołanie metody modelu do aktualizacji
            success = self.internal_meetings_model.update_meeting(
                meeting_id, fk_meeting_type_id, fk_reservation_id, meeting_date, notes, internal_meeting_status
            )

            if not success:
                print(f"[### INTERNAL_MEETINGS_CONTROLLER] Nie dokonano żadnych zmian dla spotkania {meeting_id}.")
                return False  # Brak zmian w bazie danych

            return True  # Aktualizacja zakończona sukcesem

        except ValueError as ve:
            print(f"[### INTERNAL_MEETINGS_CONTROLLER] Błąd wartości: {ve}")
            return False

        except RuntimeError as re:
            print(f"[### INTERNAL_MEETINGS_CONTROLLER] Błąd bazy danych: {re}")
            return False


    def delete_meeting(self, meeting_id: int) -> bool:
        """
        Usuwa spotkanie na podstawie `meeting_id`.

        Args:
            meeting_id (int): ID spotkania do usunięcia.

        Returns:
            bool: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.internal_meetings_model.delete_meeting(meeting_id)
            return True  # Usunięcie zakończone sukcesem
        except sqlite3.Error as db_error:
            print(f"[InternalMeetingsController_delete_meeting] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd




    def get_meeting_by_id(self, meeting_id):
        """
        Pobiera dane spotkania z modelu na podstawie `meeting_id`.

        :param meeting_id: ID spotkania do pobrania.
        :return: Słownik z danymi spotkania lub komunikat błędu.
        """
        try:
            # Sprawdzenie, czy podane `meeting_id` jest liczbą całkowitą
            if not isinstance(meeting_id, int):
                raise ValueError(f"Nieprawidłowy format `meeting_id`: {meeting_id}. Oczekiwano liczby całkowitej.")

            # Pobranie spotkania z modelu
            meeting_data = self.internal_meetings_model.get_meeting_by_id(meeting_id)

            if meeting_data is None:
                return f"Spotkanie o ID {meeting_id} nie zostało znalezione."

            return meeting_data

        except ValueError as ve:
            print(f"[### INTERNAL_MEETINGS_CONTROLLER] Błąd wartości: {ve}")
            return f"Błąd wartości: {ve}"

        except TypeError as te:
            print(f"[### INTERNAL_MEETINGS_CONTROLLER] Błąd typu danych: {te}")
            return f"Błąd typu danych: {te}"
