import sqlite3
from datetime import date, timedelta
from controllers.roles_controller import RolesController
from controllers.employee_specialties_controller import EmployeeSpecialtiesController
from controllers.specialties_controller import SpecialtiesController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.employees_controller import EmployeesController
from controllers.database_controller import DatabaseController

class DashboardService:
    def __init__(self, dashboard_controller, db_controller: DatabaseController):
        """
        Inicjalizuje DashboardService z kontrolerem dashboardu.
        """
        self.dashboard_controller = dashboard_controller
        self.db_controller = db_controller  # Przypisanie kontrolera bazy danych do atrybutu klasy

    def fetch_and_format_username(self, user_id):
        """
        Pobiera employee_id na podstawie user_id, następnie pobiera dane pracownika za pomocą metody get_employee
        z employees_controller oraz zwraca sformatowaną nazwę w postaci "First_name Last_name".

        Args:
            user_id (int): ID użytkownika.

        Returns:
            str or None: Sformatowana nazwa pracownika lub None, jeśli nie uda się pobrać danych.
        """
        # Pobranie employee_id na podstawie user_id
        users_accounts_controller = UsersAccountsController(self.dashboard_controller.db_controller)
        employee_id = users_accounts_controller.get_employee_id_by_user_id(user_id)
        if not employee_id:
            print(f"Nie znaleziono employee_id dla user_id: {user_id}")
            return None

        # Pobranie danych pracownika
        employees_controller = EmployeesController(self.dashboard_controller.db_controller)
        employee = employees_controller.get_employee(employee_id)
        if not employee:
            print(f"Nie znaleziono danych pracownika dla employee_id: {employee_id}")
            return None

        # Sformatowanie imienia i nazwiska (zakładamy, że employee to słownik zawierający klucze 'first_name' oraz 'last_name')
        formatted_name = f"{employee.get('first_name', '').capitalize()} {employee.get('last_name', '').capitalize()}".strip()
        return formatted_name


 # -------------------------------------------------------------------------


    def fetch_user_role_name(self, user_id):
        """
        Pobiera nazwę roli użytkownika na podstawie jego ID.
        """
        try:
            roles_controller = RolesController(self.dashboard_controller.db_controller)
            role_name = roles_controller.get_role_name_by_user_id(user_id)
            # print(f"service role_name: Nazwa roli użytkownika {user_id}: {role_name}")
            return role_name
        except ValueError as ve:
            print(f"Błąd danych użytkownika (user_id): {ve}")
            return "Nieznana rola"
        except KeyError as ke:
            print(f"Błąd klucza podczas pobierania roli użytkownika: {ke}")
            return "Nieznana rola"
        except AttributeError as ae:
            print(f"Błąd atrybutów (np. roles_controller): {ae}")
            return "Nieznana rola"
        

 # -------------------------------------------------------------------------


    def get_specialties_for_logged_in_user(self, user_id):

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.dashboard_controller.db_controller)

            # Pobranie employee_id
            employee_id = users_accounts_controller.get_employee_id_by_user_id(user_id)
            # print(f"service specialties: Pobrano employee_id: {employee_id}")  # Debug
            if not employee_id:
                print(f"Brak employee_id dla user_id: {user_id}")  # Debug
                return []

            # Pobranie specialty_id
            employee_specialties_controller = EmployeeSpecialtiesController(self.dashboard_controller.db_controller)
            specialties_ids = employee_specialties_controller.get_specialties_by_employee_id(employee_id)
            # print(f"service specialties: Pobrano specialties_ids: {specialties_ids}")  # Debug
            if not specialties_ids:
                print(f"Brak specialties dla employee_id: {employee_id}")  # Debug
                return []

            # Pobranie nazw specjalizacji
            specialties_controller = SpecialtiesController(self.dashboard_controller.db_controller)
            specialties_names = []
            for specialty_id in specialties_ids:
                specialty_name = specialties_controller.get_specialty_name_by_id(specialty_id)
                # print(f"service specialties: Pobrano specialty_name: {specialty_name} dla specialty_id: {specialty_id}")  # Debug
                if specialty_name:
                    specialties_names.append(specialty_name)

            # print(f"service specialties: Zwracam specialties_names: {specialties_names}")  # Debug
            return specialties_names

        except ValueError as ve:
            print(f"Błąd danych wejściowych podczas pobierania specjalności użytkownika: {ve}")
            return []

        except KeyError as ke:
            print(f"Błąd klucza podczas pobierania specjalności użytkownika: {ke}")
            return []

        except AttributeError as ae:
            print(f"Błąd atrybutów (np. kontrolery): {ae}")
            return []


 # -------------------------------------------------------------------------





    def get_date_with_offset(self, days_offset=0):
        """
        Zwraca datę przesuniętą o określoną liczbę dni od bieżącej daty.

        Args:
            days_offset (int): Liczba dni do przesunięcia. Wartość domyślna to 0 (dzisiaj).

        Returns:
            str: Data w formacie 'YYYY-MM-DD'.
        """
        try:
            # Pobranie bieżącej daty
            current_date = date.today()
            # Obliczenie przesuniętej daty
            shifted_date = current_date + timedelta(days=days_offset)
            # Zwracanie daty w formacie 'YYYY-MM-DD'
            return shifted_date.strftime('%Y-%m-%d')

        except TypeError as te:
            print(f"Błąd typu danych (days_offset powinno być liczbą całkowitą): {te}")
        except AttributeError as ae:
            print(f"Błąd atrybutu (problem z obiektem date lub timedelta): {ae}")
        except ValueError as ve:
            print(f"Błąd wartości: {ve}")

        # Jeśli wystąpi wyjątek, zwróć None
        return None


    def get_current_day_name(self, days_offset=0):
        """
        Zwraca nazwę aktualnego dnia tygodnia w języku polskim, z możliwością przesunięcia daty.

        Args:
            days_offset (int): Liczba dni do przesunięcia. Domyślnie 0 (dzisiaj).

        Returns:
            str: Nazwa dnia tygodnia (np. 'Poniedziałek', 'Wtorek').
        """
        # Mapowanie dni tygodnia na język polski
        days_in_polish = {
            0: "Poniedziałek",
            1: "Wtorek",
            2: "Środa",
            3: "Czwartek",
            4: "Piątek",
            5: "Sobota",
            6: "Niedziela",
        }

        try:
            # Pobranie przesuniętej daty
            shifted_date = date.today() + timedelta(days=days_offset)

            # Pobranie dnia tygodnia (0 = Poniedziałek, 6 = Niedziela)
            current_day = shifted_date.weekday()

            # Debugowanie: Sprawdzenie przesuniętej daty i dnia tygodnia
            # print(f"get_current_day_name: Przesunięta data: {shifted_date}, Dzień tygodnia: {current_day}")

            # Zwrócenie nazwy dnia tygodnia w języku polskim
            return days_in_polish.get(current_day, "Nieznany dzień")

        except KeyError as ke:
            print(f"Błąd klucza: dzień tygodnia nie został znaleziony w słowniku: {ke}")
        except TypeError as te:
            print(f"Błąd typu danych (days_offset powinno być liczbą całkowitą): {te}")
        except AttributeError as ae:
            print(f"Błąd atrybutu: {ae}")
        except ValueError as ve:
            print(f"Błąd wartości: {ve}")

        # W przypadku błędu zwróć domyślną wartość
        return "Nieznany dzień"

 # -------------------------------------------------------------------------


    def get_meeting_details_by_employee_id(self, employee_id, date_offset=0):
        """
        Pobiera szczegóły spotkań dla danego `employee_id`:
        - Data spotkania (`meeting_date`)
        - Nazwa spotkania (`meeting_type`)
        - Numer pokoju (`room_number`)

        Args:
            employee_id (int): ID pracownika.
            date_offset (int): Przesunięcie daty (domyślnie 0 = dzisiejsza data).

        Returns:
            list: Lista słowników z `meeting_date`, `meeting_type`, `room_number`.
        """
        try:
            self.db_controller.ensure_connection()

            # Oblicz przesuniętą datę
            target_date = (date.today() + timedelta(days=date_offset)).strftime("%Y-%m-%d")

            ### Pobranie `meeting_id` dla `employee_id` ###
            query_meeting_ids = """
            SELECT fk_meeting_id 
            FROM meeting_participants 
            WHERE fk_employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query_meeting_ids, (employee_id,))
            meeting_ids = [row[0] for row in cursor.fetchall()]

            # Debugowanie
            # print(f"[DEBUG] Pobranie meeting_id dla employee_id {employee_id}: {meeting_ids}")

            if not meeting_ids:
                return []  # Brak spotkań dla pracownika

            ### Pobranie szczegółów spotkań ###
            placeholders = ", ".join(["?"] * len(meeting_ids))
            query_meeting_details = f"""
            SELECT meeting_id, meeting_date, fk_meeting_type_id, fk_reservation_id
            FROM internal_meetings
            WHERE meeting_id IN ({placeholders}) AND meeting_date >= ?
            """
            cursor = self.db_controller.connection.execute(query_meeting_details, meeting_ids + [target_date])
            meeting_details = {
                row[0]: {
                    "meeting_date": row[1],
                    "fk_meeting_type_id": row[2],
                    "fk_reservation_id": row[3]
                }
                for row in cursor.fetchall()
            }

            # Debugowanie
            # print(f"[DEBUG] Szczegóły spotkań: {meeting_details}")

            ### Pobranie nazw `meeting_type` ###
            meeting_type_ids = list(set([details["fk_meeting_type_id"] for details in meeting_details.values()]))

            query_meeting_types = f"""
            SELECT meeting_type_id, meeting_type 
            FROM meeting_types 
            WHERE meeting_type_id IN ({", ".join(["?"] * len(meeting_type_ids))})
            """
            cursor = self.db_controller.connection.execute(query_meeting_types, meeting_type_ids)
            meeting_types = {row[0]: row[1] for row in cursor.fetchall()}

            # Debugowanie
            # print(f"[DEBUG] Pobranie meeting_types: {meeting_types}")

            ### Pobranie numerów pokoi ###
            reservation_ids = list(set([details["fk_reservation_id"] for details in meeting_details.values()]))

            # Pobierz powiązania między reservation_id a room_id z tabeli room_reservations
            query_reservations = f"""
            SELECT reservation_id, fk_room_id 
            FROM room_reservations 
            WHERE reservation_id IN ({", ".join(["?"] * len(reservation_ids))})
            """
            cursor = self.db_controller.connection.execute(query_reservations, reservation_ids)
            reservation_to_room = {row[0]: row[1] for row in cursor.fetchall()}

            # Debugowanie
            # print(f"[DEBUG] Powiązanie reservation_id -> room_id: {reservation_to_room}")

            # Pobierz room_number na podstawie room_id
            room_ids = list(set(reservation_to_room.values()))
            query_room_numbers = f"""
            SELECT room_id, room_number 
            FROM rooms 
            WHERE room_id IN ({", ".join(["?"] * len(room_ids))})
            """
            cursor = self.db_controller.connection.execute(query_room_numbers, room_ids)
            room_numbers = {row[0]: row[1] for row in cursor.fetchall()}

            # Debugowanie
            # print(f"[DEBUG] Pobranie room_numbers: {room_numbers}")

            ### Formatowanie wyników ###
            final_results = []
            #pylint: disable=W0612
            for meeting_id, details in meeting_details.items():
                meeting_type = meeting_types.get(details["fk_meeting_type_id"], "Nieznane")
                room_id = reservation_to_room.get(details["fk_reservation_id"], None)
                room_number = room_numbers.get(room_id, "Brak pokoju")
                final_results.append({
                    "meeting_date": details["meeting_date"],
                    "meeting_type": meeting_type,
                    "room_number": room_number
                })

            # Debugowanie
            # print(f"[DEBUG] Końcowe wyniki spotkań: {final_results}")

            return final_results

        except sqlite3.Error as e:
            print(f"[ERROR] Błąd podczas pobierania szczegółów spotkań: {e}")
            raise RuntimeError(f"Błąd podczas pobierania szczegółów spotkań: {e}") from e

 # -------------------------------------------------------------------------

    def get_patient_appointments_with_rooms(self, fk_employee_id, date_offset=0):
        """
        Pobiera szczegółowe informacje o wizytach przypisanych do pracownika (`fk_employee_id`),
        zaczynając od dzisiejszej daty lub przesuniętej (date_offset):
        - Data wizyty (`appointment_date`)
        - Imię i nazwisko pacjenta (`first_name last_name`)
        - Numer pokoju (`room_number`)

        Args:
            fk_employee_id (int): ID pracownika.
            date_offset (int): Przesunięcie daty (np. -1 dla wczoraj, 1 dla jutra).

        Returns:
            list: Lista słowników z informacjami o wizytach (maksymalnie 5 wizyt).
        """
        try:
            self.db_controller.ensure_connection()

            # Obliczenie daty początkowej
            target_date = (date.today() + timedelta(days=date_offset)).strftime("%Y-%m-%d")
            # print(f"[dashboard_service][DEBUG] Używana data: {target_date}")

            # Pobranie assignment_id przypisanych do fk_employee_id
            query_assignments = """
            SELECT assignment_id
            FROM assigned_patients
            WHERE fk_employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query_assignments, (fk_employee_id,))
            assignment_ids = [row[0] for row in cursor.fetchall()]

            # print(f"[dashboard_service][DEBUG] Pobranie assignment_id dla fk_employee_id {fk_employee_id}: {assignment_ids}")

            if not assignment_ids:
                return []  # Brak przypisań dla pracownika

            # Pobranie appointment_date oraz fk_reservation_id z tabeli appointments
            placeholders = ", ".join(["?"] * len(assignment_ids))
            query_appointments = f"""
            SELECT fk_assignment_id, appointment_date, fk_reservation_id
            FROM appointments
            WHERE fk_assignment_id IN ({placeholders}) AND appointment_date >= ?
            ORDER BY appointment_date ASC
            LIMIT 5
            """
            cursor = self.db_controller.connection.execute(query_appointments, assignment_ids + [target_date])
            appointments = {
                row[0]: {
                    "appointment_date": row[1],
                    "fk_reservation_id": row[2]
                }
                for row in cursor.fetchall()
            }

            # print(f"[dashboard_service][DEBUG] Szczegóły wizyt z tabeli appointments: {appointments}")

            if not appointments:
                return []  # Brak wizyt

            # Pobranie fk_patient_id przypisanych do assignment_id
            query_patients = f"""
            SELECT assignment_id, fk_patient_id
            FROM assigned_patients
            WHERE assignment_id IN ({placeholders})
            """
            cursor = self.db_controller.connection.execute(query_patients, assignment_ids)
            assignment_to_patient = {row[0]: row[1] for row in cursor.fetchall()}

            # print(f"[dashboard_service][DEBUG] Powiązania assignment_id -> fk_patient_id: {assignment_to_patient}")

            # Pobranie first_name i last_name z tabeli patients
            patient_ids = list(set(assignment_to_patient.values()))
            query_patient_names = f"""
            SELECT patient_id, first_name || ' ' || last_name AS full_name
            FROM patients
            WHERE patient_id IN ({", ".join(["?"] * len(patient_ids))})
            """
            cursor = self.db_controller.connection.execute(query_patient_names, patient_ids)
            patient_names = {row[0]: row[1] for row in cursor.fetchall()}

            # print(f"[dashboard_service][DEBUG] Pobranie imion i nazwisk pacjentów: {patient_names}")

            # Pobranie numerów pokoi na podstawie fk_reservation_id
            reservation_ids = list(set([details["fk_reservation_id"] for details in appointments.values()]))
            query_room_numbers = f"""
            SELECT reservation_id, room_number
            FROM room_reservations
            JOIN rooms ON room_reservations.fk_room_id = rooms.room_id
            WHERE reservation_id IN ({", ".join(["?"] * len(reservation_ids))})
            """
            cursor = self.db_controller.connection.execute(query_room_numbers, reservation_ids)
            room_numbers = {row[0]: row[1] for row in cursor.fetchall()}

            # print(f"[dashboard_service][DEBUG] Pobranie numerów pokoi: {room_numbers}")

            # Formatowanie wyników
            final_results = []
            for assignment_id, appointment in appointments.items():
                patient_id = assignment_to_patient.get(assignment_id)
                patient_name = patient_names.get(patient_id, "Nieznany pacjent")
                room_number = room_numbers.get(appointment["fk_reservation_id"], "Brak pokoju")
                final_results.append({
                    "appointment_date": appointment["appointment_date"],
                    "patient_name": patient_name,
                    "room_number": room_number
                })

            # print(f"[dashboard_service][DEBUG] Końcowe wyniki wizyt: {final_results}")

            return final_results

        except sqlite3.Error as e:
            print(f"[dashboard_service][ERROR] Błąd podczas pobierania szczegółów wizyt: {e}")
            raise RuntimeError(f"Błąd podczas pobierania szczegółów wizyt: {e}") from e


    def get_appointment_count_by_employee_id(self, employee_id):
        """
        Pobiera liczbę wizyt przypisanych do danego pracownika (`employee_id`).

        Args:
            employee_id (int): ID pracownika.

        Returns:
            str: Liczba przypisanych wizyt jako tekst do wyświetlenia.
        """
        try:
            self.db_controller.ensure_connection()

            # Pobranie assignment_id przypisanych do employee_id
            query_assignments = """
            SELECT assignment_id
            FROM assigned_patients
            WHERE fk_employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query_assignments, (employee_id,))
            assignment_ids = [row[0] for row in cursor.fetchall()]

            # print(f"[dashboard_services][DEBUG] Pobranie assignment_id dla employee_id {employee_id}: {assignment_ids}")

            if not assignment_ids:
                return "Brak przypisanych wizyt."

            # Pobranie appointment_id przypisanych do assignment_id
            placeholders = ", ".join(["?"] * len(assignment_ids))
            query_appointments = f"""
            SELECT COUNT(*)
            FROM appointments
            WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.db_controller.connection.execute(query_appointments, assignment_ids)
            appointment_count = cursor.fetchone()[0]

            # print(f"[dashboard_services][DEBUG] Liczba pobranych wizyt dla employee_id {employee_id}: {appointment_count}")

            return f"Liczba przypisanych wizyt: {appointment_count}"

        except sqlite3.Error as e:
            print(f"[dashboard_services][ERROR] Błąd podczas pobierania liczby wizyt: {e}")
            raise RuntimeError(f"Błąd podczas pobierania liczby wizyt: {e}") from e


    def get_todays_appointments_by_employee_id(self, employee_id, date_offset=0):
        """
        Pobiera wizyty przypisane do danego `employee_id` z tabeli `appointments`,
        tylko dla wizyt na określoną datę (dzisiejszą z możliwością przesunięcia).

        Args:
            employee_id (int): ID pracownika.
            date_offset (int, opcjonalne): Przesunięcie daty w dniach (np. -1 dla wczoraj, 1 dla jutra).

        Returns:
            list: Lista słowników z `appointment_id`, `appointment_date`, `fk_patient_id`, `fk_reservation_id`.
        """
        try:
            self.db_controller.ensure_connection()

            # Obliczenie daty z przesunięciem 
            target_date = (date.today() + timedelta(days=date_offset)).strftime("%Y-%m-%d")
            # print(f"[dashboard_service][DEBUG] Pobieranie wizyt dla employee_id {employee_id} na dzień: {target_date}")

            # Pobranie assignment_id przypisanych do employee_id
            query_assignments = """
            SELECT assignment_id FROM assigned_patients WHERE fk_employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query_assignments, (employee_id,))
            assignment_ids = [row[0] for row in cursor.fetchall()]

            # print(f"[dashboard_service][DEBUG] Pobranie assignment_id: {assignment_ids}")

            if not assignment_ids:
                return []  # Brak przypisań do pracownika

            # Pobranie wizyt przypisanych do assignment_id 
            placeholders = ", ".join(["?"] * len(assignment_ids))
            query_appointments = f"""
            SELECT appointment_id, appointment_date, fk_assignment_id, fk_reservation_id
            FROM appointments
            WHERE fk_assignment_id IN ({placeholders}) AND appointment_date LIKE ?
            ORDER BY appointment_date ASC
            """
            cursor = self.db_controller.connection.execute(query_appointments, assignment_ids + [f"{target_date}%"])
            appointments = [
                {
                    "appointment_id": row[0],
                    "appointment_date": row[1],
                    "fk_assignment_id": row[2],
                    "fk_reservation_id": row[3],
                }
                for row in cursor.fetchall()
            ]

            # print(f"[dashboard_service][DEBUG] Pobranie wizyt: {appointments}")

            return appointments

        except sqlite3.Error as e:
            print(f"[dashboard_service][ERROR] Błąd podczas pobierania wizyt: {e}")
            raise RuntimeError(f"Błąd podczas pobierania wizyt: {e}") from e
