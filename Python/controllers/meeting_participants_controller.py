# meeting_participants_controller.py

import sqlite3
from models.meeting_participants import MeetingParticipants
from controllers.database_controller import DatabaseController


class MeetingParticipantsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `meeting_participants`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `meeting_participants` oraz model zarządzający danymi `meeting_participants`.

        Args:
            db_controller (DatabaseController): Instancja kontrolera bazy danych.
        """
        self.db_controller = db_controller
        self.meeting_participants_model = MeetingParticipants(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `meeting_participants` w bazie danych.
        """
        try:
            self.meeting_participants_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `meeting_participants`.") from db_error

    def get_meetings_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie fk_meeting_id, do których przypisany jest podany pracownik (employee_id).

        Args:
            employee_id (int): ID pracownika.

        Returns:
            list: Lista fk_meeting_id przypisanych do pracownika.
        """
        try:
            # Wywołanie metody z modelu
            return self.meeting_participants_model.get_meetings_by_employee_id(employee_id)
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania spotkań dla employee_id={employee_id}: {db_error}") from db_error
        except ValueError as ve:
            raise RuntimeError(f"Błąd wartości wejściowych: {ve}") from ve



    def add_participant(self, fk_meeting_id, fk_employee_id, participant_role, attendance):
        """
        Dodaje nowego uczestnika do tabeli `meeting_participants`.

        Args:
            fk_meeting_id (int): ID spotkania.
            fk_employee_id (int): ID pracownika.
            participant_role (str): Rola uczestnika.
            attendance (str): Status obecności.

        Returns:
            dict: Dane nowo dodanego uczestnika.
        """
        try:
            participant_id = self.meeting_participants_model.add_participant(
                fk_meeting_id, fk_employee_id, participant_role, attendance
            )
            return {
                "participant_id": participant_id,
                "fk_meeting_id": fk_meeting_id,
                "fk_employee_id": fk_employee_id,
                "participant_role": participant_role,
                "attendance": attendance,
            }
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania uczestnika.") from db_error

    def get_participants(self, filters=None, sort_by=None):
        """
        Pobiera uczestników z tabeli `meeting_participants` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów w formacie [{"column": ..., "operator": ..., "value": ...}].
            sort_by (list): Lista sortowania w formacie [{"column": ..., "direction": ...}].

        Returns:
            list[dict]: Lista uczestników jako słowniki.
        """
        try:
            return self.meeting_participants_model.get_participants(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania uczestników.") from db_error

    def update_participant(self, participant_id: int, fk_meeting_id: int = None, fk_employee_id: int = None, 
                            participant_role: str = None, attendance: str = None) -> bool:
        """
        Aktualizuje uczestnika na podstawie `participant_id`.

        Args:
            participant_id (int): ID uczestnika do aktualizacji.
            fk_meeting_id (int, opcjonalnie): Nowe ID spotkania.
            fk_employee_id (int, opcjonalnie): Nowe ID pracownika.
            participant_role (str, opcjonalnie): Nowa rola uczestnika.
            attendance (str, opcjonalnie): Nowy status obecności.

        Returns:
            bool: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.meeting_participants_model.update_participant(
                participant_id, fk_meeting_id, fk_employee_id, participant_role, attendance
            )
            return True  # Aktualizacja zakończona sukcesem
        except sqlite3.Error as db_error:
            print(f"[MeetingParticipantsController_update_participant] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd


    def delete_participant(self, participant_id: int) -> bool:
        """
        Usuwa uczestnika na podstawie `participant_id`.

        Args:
            participant_id (int): ID uczestnika do usunięcia.

        Returns:
            bool: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.meeting_participants_model.delete_participant(participant_id)
            return True  # Usunięcie zakończone sukcesem
        except sqlite3.Error as db_error:
            print(f"[MeetingParticipantsController_delete_participant] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd



    def get_participant_by_id(self, participant_id: int) -> dict:
        """
        Pobiera szczegóły uczestnika spotkania na podstawie `participant_id` z modelu.

        :param participant_id: ID uczestnika spotkania do pobrania.
        :return: Słownik z danymi uczestnika lub pusty słownik, jeśli uczestnik nie istnieje.
        :raises ValueError: Jeśli `participant_id` nie jest liczbą całkowitą.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            # Walidacja danych wejściowych
            if not isinstance(participant_id, int):
                raise ValueError(f"Nieprawidłowy format `participant_id`: {participant_id}. Oczekiwano liczby całkowitej.")

            participant_data = self.meeting_participants_model.get_participant_by_id(participant_id)

            if not participant_data:
                return f"Uczestnik o ID {participant_id} nie został znaleziony."

            return participant_data

        except ValueError as ve:
            print(f"[### MEETING_PARTICIPANTS_CONTROLLER] Błąd wartości: {ve}")
            return f"Błąd wartości: {ve}"

        except RuntimeError as re:
            print(f"[### MEETING_PARTICIPANTS_CONTROLLER] Błąd bazy danych: {re}")
            return f"Błąd bazy danych: {re}"
