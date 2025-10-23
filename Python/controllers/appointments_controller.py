# appointments_controller.py

import sqlite3
from models.appointments import Appointments
from controllers.database_controller import DatabaseController


class AppointmentsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `appointments`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `appointments` oraz model zarządzający danymi `appointments`.
        """
        self.db_controller = db_controller
        self.appointments_model = Appointments(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `appointments` w bazie danych.
        """
        try:
            self.appointments_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `appointments`.") from db_error


    

    


    def add_appointment(self, fk_assignment_id, fk_service_id, fk_reservation_id, appointment_date, appointment_status, notes=None):
        """
        Dodaje nową wizytę.
        """
        try:
            return self.appointments_model.add_appointment(
                fk_assignment_id, fk_service_id, fk_reservation_id, appointment_date, appointment_status, notes
            )
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania wizyty.") from db_error

    def get_appointments(self, filters=None, sort_by=None):
        """
        Pobiera wizyty z tabeli `appointments` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            return self.appointments_model.get_appointments(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania wizyt.") from db_error


    def get_patient_id(self, first_name, last_name):
        """
        Pobiera ID pacjenta na podstawie imienia i nazwiska.
        """
        try:
            return self.appointments_model.get_patient_id(first_name, last_name)
        except RuntimeError as e:
            raise ValueError(f"Błąd podczas pobierania ID pacjenta: {e}") from e

    def get_employee_id(self, first_name, last_name):
        """
        Pobiera ID pracownika na podstawie imienia i nazwiska.
        """
        try:
            return self.appointments_model.get_employee_id(first_name, last_name)
        except RuntimeError as e:
            raise ValueError(f"Błąd podczas pobierania ID pracownika: {e}") from e

    def get_service_id(self, service_type):
        """
        Pobiera ID usługi na podstawie typu usługi.
        """
        try:
            return self.appointments_model.get_service_id(service_type)
        except RuntimeError as e:
            raise ValueError(f"Błąd podczas pobierania ID usługi: {e}") from e

    def get_room_id(self, room_number):
        """
        Pobiera ID pokoju na podstawie numeru pokoju.
        """
        try:
            return self.appointments_model.get_room_id(room_number)
        except RuntimeError as e:
            raise ValueError(f"Błąd podczas pobierania ID pokoju: {e}") from e


    def delete_appointment(self, appointment_id):
        """
        Usuwa wizytę z tabeli `appointments` na podstawie `appointment_id`.
        """
        try:
            self.appointments_model.delete_appointment(appointment_id)
            return True  # Aktualizacja zakończona sukcesem
        
        except KeyError as e:
            raise ValueError(f"Wizyta o podanym ID {appointment_id} nie istnieje.") from e
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania wizyty.") from db_error





    def get_all_appointments_by_patient(self):
        """
        Pobiera wszystkie wizyty przypisane do pacjentów (fk_patient_id).

        Returns:
            dict: Słownik w formacie {fk_patient_id: [lista appointment_id]}.
        
        Raises:
            RuntimeError: W przypadku błędu bazy danych podczas pobierania wizyt.
        """
        try:
            # Wywołanie metody modelu
            return self.appointments_model.get_all_appointments_by_patient()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania wizyt przypisanych do pacjentów.") from db_error
        


    def get_appointment_by_id(self, appointment_id: int) -> dict:
        """
        Pobiera szczegóły wizyty na podstawie `appointment_id`.

        :param appointment_id: ID wizyty do pobrania.
        :return: Słownik z danymi wizyty lub pusty słownik, jeśli wizyta nie istnieje.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            return self.appointments_model.get_appointment_by_id(appointment_id)
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania wizyty {appointment_id}.") from db_error
        except ValueError as ve:
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve


    def update_appointment(self, appointment_id: int, assignment_id: int = None, service_id: int = None, 
                        reservation_id: int = None, appointment_date: str = None,
                        appointment_status: str = None, notes: str = None) -> bool:
        """
        Aktualizuje rekord wizyty na podstawie `appointment_id`.

        :param appointment_id: ID wizyty do aktualizacji.
        :param assignment_id: (Opcjonalne) Nowe ID przypisania pacjenta.
        :param service_id: (Opcjonalne) Nowe ID usługi.
        :param reservation_id: (Opcjonalne) Nowe ID rezerwacji.
        :param appointment_date: (Opcjonalne) Nowa data wizyty.
        :param appointment_status: (Opcjonalne) Nowy status wizyty.
        :param notes: (Opcjonalne) Nowe notatki do wizyty.
        :return: True jeśli aktualizacja się powiodła, False jeśli nie dokonano zmian.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            return self.appointments_model.update_appointment(
                appointment_id, assignment_id, service_id, reservation_id, 
                appointment_date, appointment_status, notes
            )
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas aktualizacji wizyty {appointment_id}.") from db_error
        except ValueError as ve:
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve

    def get_assignment_id_by_appointment_id(self, appointment_id: int) -> int:
        """
        Pobiera `fk_assignment_id` na podstawie `appointment_id` za pomocą modelu `appointments`.

        :param appointment_id: ID wizyty.
        :return: ID przypisania pacjenta (`fk_assignment_id`) lub `None`, jeśli nie znaleziono.
        :raises RuntimeError: W przypadku błędu bazy danych.
        :raises ValueError: Jeśli `appointment_id` ma nieprawidłowy format.
        """
        try:
            return self.appointments_model.get_assignment_id_by_appointment_id(appointment_id)
        
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania `fk_assignment_id` dla `appointment_id` {appointment_id}.") from db_error

        except ValueError as ve:
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve
