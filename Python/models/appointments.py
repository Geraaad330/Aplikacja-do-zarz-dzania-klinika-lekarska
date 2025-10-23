# appointments.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.patients_controller import PatientController
from controllers.employees_controller import EmployeesController
from controllers.services_controller import ServicesController
from controllers.rooms_controller import RoomsController

class Appointments:
    """
    Klasa odpowiedzialna za zarządzanie tabelą `appointments` w kontekście operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje instancję klasy Appointments z kontrolerem bazy danych.
        """
        self.db_controller = db_controller
        self.patients_controller = PatientController(db_controller)
        self.employees_controller = EmployeesController(db_controller)
        self.services_controller = ServicesController(db_controller)
        self.rooms_controller = RoomsController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `appointments` w bazie danych, jeśli jeszcze nie istnieje.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("appointments"):
                query = """
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_assignment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do tabeli assigned_patients
                    fk_service_id INTEGER NOT NULL,
                    fk_room_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL CHECK (
                        appointment_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
                    ), -- Format daty YYYY-MM-DD HH:MM
                    appointment_time TEXT NOT NULL CHECK (
                        appointment_time GLOB '[0-2][0-9]:[0-5][0-9]' OR
                        appointment_time GLOB '[0-9]:[0-5][0-9]'
                    ),
                    appointment_status TEXT NOT NULL CHECK (
                        appointment_status GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.\\/]*'
                    ),
                    notes TEXT, -- Notatki bez walidacji
                    FOREIGN KEY (fk_assignment_id) REFERENCES assigned_patients(assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (fk_service_id) REFERENCES services(service_id) ON DELETE SET NULL ON UPDATE CASCADE,
                    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id) ON DELETE SET NULL ON UPDATE CASCADE,
                    UNIQUE (fk_assignment_id, appointment_date), -- Zapobiega powtórzeniom przypisania i daty wizyty
                    UNIQUE (fk_room_id, appointment_date) -- Zapobiega powtórzeniom pokoju i daty wizyty
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e








    def add_appointment(self, fk_assignment_id, fk_service_id, fk_reservation_id, appointment_date, appointment_status, notes=None):
        """
        Adds a new appointment to the appointments table in the database.

        Args:
            assignment_id (int): Foreign key to the assigned_patients table.
            service_id (int): Foreign key to the services table.
            room_id (int): Foreign key to the rooms table.
            appointment_date (str): Appointment date in YYYY-MM-DD format.
            appointment_time (str): Appointment time in HH:MM format.
            appointment_status (str): Status of the appointment.
            notes (str, optional): Additional notes about the appointment.

        Returns:
            int: ID of the newly inserted appointment.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            INSERT INTO appointments (
                fk_assignment_id,
                fk_service_id,
                fk_reservation_id,
                appointment_date,
                appointment_status,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor = self.db_controller.connection.execute(
                query,
                (fk_assignment_id, fk_service_id, fk_reservation_id, appointment_date, appointment_status, notes)
            )
            self.db_controller.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas dodawania wizyty: {e}") from e





    def get_appointments(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `appointments` z opcjonalnymi filtrami i sortowaniem.
        
        :param filters: Lista filtrów, np. [{"column": "appointment_date", "operator": "=", "value": "2025-01-09"}].
        :param sort_by: Lista sortowania, np. [("appointment_date", "ASC")].
        :return: Lista rekordów jako słowniki.
        
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"SELECT * FROM appointments WHERE {query_conditions}"
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e

    def get_patient_id(self, first_name, last_name):
        """
        Pobiera ID pacjenta na podstawie imienia i nazwiska.
        
        :param first_name: Imię pacjenta.
        :param last_name: Nazwisko pacjenta.
        :return: ID pacjenta.
        
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            return self.patients_controller.advanced_filter_patients(first_name=first_name, last_name=last_name)[0]["patient_id"]
        except (IndexError, sqlite3.Error) as e:
            raise RuntimeError(f"Błąd podczas pobierania ID pacjenta: {e}") from e

    def get_employee_id(self, first_name, last_name):
        """
        Pobiera ID pracownika na podstawie imienia i nazwiska.
        
        :param first_name: Imię pracownika.
        :param last_name: Nazwisko pracownika.
        :return: ID pracownika.
        
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            return self.employees_controller.filter_employees(first_name=first_name, last_name=last_name)[0]["employee_id"]
        except (IndexError, sqlite3.Error) as e:
            raise RuntimeError(f"Błąd podczas pobierania ID pracownika: {e}") from e

    def get_service_id(self, service_type):
        """
        Pobiera ID usługi na podstawie typu usługi.
        
        :param service_type: Typ usługi.
        :return: ID usługi.
        
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            return self.services_controller.get_services_with_filters(filters=[{"column": "service_type", "operator": "=", "value": service_type}])[0]["service_id"]
        except (IndexError, sqlite3.Error) as e:
            raise RuntimeError(f"Błąd podczas pobierania ID usługi: {e}") from e

    def get_room_id(self, room_number):
        """
        Pobiera ID pokoju na podstawie numeru pokoju.
        
        :param room_number: Numer pokoju.
        :return: ID pokoju.
        
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            return self.rooms_controller.get_rooms_with_filters(filters=[{"column": "room_number", "operator": "=", "value": room_number}])[0]["room_id"]
        except (IndexError, sqlite3.Error) as e:
            raise RuntimeError(f"Błąd podczas pobierania ID pokoju: {e}") from e







    def delete_appointment(self, appointment_id):
        """
        Usuwa rekord z tabeli `appointments` na podstawie `appointment_id`.

        :param appointment_id: ID wizyty do usunięcia.
        
        :raises KeyError: Jeśli rekord o podanym `appointment_id` nie istnieje.
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            self.db_controller.ensure_connection()

            # Sprawdzenie, czy rekord istnieje
            query_check = "SELECT COUNT(*) FROM appointments WHERE appointment_id = ?"
            cursor = self.db_controller.connection.execute(query_check, (appointment_id,))
            if cursor.fetchone()[0] == 0:
                raise KeyError(f"Rekord o `appointment_id` {appointment_id} nie istnieje.")

            # Usunięcie rekordu
            query_delete = "DELETE FROM appointments WHERE appointment_id = ?"
            self.db_controller.connection.execute(query_delete, (appointment_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e



    def get_all_appointments_by_patient(self):
        """
        Pobiera wszystkie appointment_id przypisane do wszystkich fk_patient_id.

        :return: Słownik {fk_patient_id: [lista appointment_id]}
        :raises RuntimeError: W przypadku błędu w bazie danych.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            SELECT fk_patient_id, appointment_id
            FROM appointments
            """
            cursor = self.db_controller.connection.execute(query)

            # Tworzenie słownika wyników
            results = {}
            for row in cursor.fetchall():
                patient_id = row["fk_patient_id"]
                appointment_id = row["appointment_id"]
                if patient_id not in results:
                    results[patient_id] = []
                results[patient_id].append(appointment_id)
            
            # Debugowanie: Wyświetlenie pobranych wizyt
            # print(f"[###MODEL APPOINTMENTS] Pobrano listę wizyt: {results}")

            return results
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania wizyt: {e}") from e


    def get_appointment_by_id(self, appointment_id: int) -> dict:
        """
        Pobiera wszystkie kolumny z tabeli `appointments` na podstawie `appointment_id`.

        :param appointment_id: ID wizyty do pobrania.
        :return: Słownik z danymi wizyty lub pusty słownik, jeśli wizyta nie istnieje.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            # Sprawdzenie poprawności przekazanego ID
            if not isinstance(appointment_id, int) or appointment_id <= 0:
                raise ValueError("Nieprawidłowy format ID wizyty.")

            self.db_controller.ensure_connection()
            query = """
            SELECT * FROM appointments WHERE appointment_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (appointment_id,))
            appointment_data = cursor.fetchone()

            if not appointment_data:
                return {}  # Zwróć pusty słownik, jeśli nie znaleziono wizyty

            # Konwersja do słownika
            appointment_dict = dict(appointment_data)

            # Debugowanie: Wyświetlenie pobranych danych
            print(f"[###MODEL APPOINTMENTS] Pobrano wizytę {appointment_id}: {appointment_dict}")

            return appointment_dict
        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych podczas pobierania wizyty {appointment_id}.") from op_err
        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania wizyty {appointment_id}.") from db_err
        except ValueError as ve:
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve



    def update_appointment(self, appointment_id: int, assignment_id: int = None, service_id: int = None, 
                        reservation_id: int = None, appointment_date: str = None,
                        appointment_status: str = None, notes: str = None) -> bool:
        """
        Aktualizuje rekord w tabeli `appointments` na podstawie `appointment_id`.

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
            # Sprawdzenie poprawności przekazanego ID
            if not isinstance(appointment_id, int) or appointment_id <= 0:
                raise ValueError("Nieprawidłowy format ID wizyty.")

            # Tworzenie zapytania dynamicznie w zależności od podanych argumentów
            fields_to_update = []
            values = []

            if assignment_id is not None:
                fields_to_update.append("fk_assignment_id = ?")
                values.append(assignment_id)
            if service_id is not None:
                fields_to_update.append("fk_service_id = ?")
                values.append(service_id)
            if reservation_id is not None:
                fields_to_update.append("fk_reservation_id = ?")
                values.append(reservation_id)
            if appointment_date is not None:
                fields_to_update.append("appointment_date = ?")
                values.append(appointment_date)
            if appointment_status is not None:
                fields_to_update.append("appointment_status = ?")
                values.append(appointment_status)
            if notes is not None:
                fields_to_update.append("notes = ?")
                values.append(notes)

            # Jeśli nie ma pól do aktualizacji, zwracamy False
            if not fields_to_update:
                return False

            # Dodanie ID wizyty na końcu listy wartości
            values.append(appointment_id)

            query = f"UPDATE appointments SET {', '.join(fields_to_update)} WHERE appointment_id = ?"
            
            self.db_controller.connection.execute(query, tuple(values))
            self.db_controller.connection.commit()

            # Debugowanie: Wyświetlenie zaktualizowanych pól
            print(f"[###MODEL APPOINTMENTS] Zaktualizowano wizytę {appointment_id} z nowymi wartościami: {fields_to_update}")

            return True
        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych podczas aktualizacji wizyty {appointment_id}.") from op_err
        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych podczas aktualizacji wizyty {appointment_id}.") from db_err
        except ValueError as ve:
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve

    def get_assignment_id_by_appointment_id(self, appointment_id: int) -> int:
        """
        Pobiera `fk_assignment_id` na podstawie `appointment_id` z tabeli `appointments`.

        :param appointment_id: ID wizyty.
        :return: ID przypisania pacjenta (`fk_assignment_id`) lub `None`, jeśli wizyta nie istnieje.
        :raises RuntimeError: W przypadku błędu bazy danych.
        :raises ValueError: Jeśli `appointment_id` ma nieprawidłowy format.
        """
        try:
            # Sprawdzenie poprawności `appointment_id`
            if not isinstance(appointment_id, int) or appointment_id <= 0:
                raise ValueError("Nieprawidłowy format `appointment_id`.")

            query = "SELECT fk_assignment_id FROM appointments WHERE appointment_id = ?"
            cursor = self.db_controller.connection.execute(query, (appointment_id,))
            result = cursor.fetchone()

            if result:
                return result["fk_assignment_id"]
            else:
                return None  # Brak dopasowania w bazie

        except sqlite3.OperationalError as op_err:
            raise RuntimeError(f"Błąd operacyjny bazy danych podczas pobierania `fk_assignment_id` dla `appointment_id` {appointment_id}.") from op_err

        except sqlite3.DatabaseError as db_err:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania `fk_assignment_id` dla `appointment_id` {appointment_id}.") from db_err
