
import sqlite3

class RoomService():
    """
    Klasa obsługująca logikę wyświetlania pacjentów w zależności od roli użytkownika.
    """

    def __init__(self, room_service_controller):
        self.room_service_controller = room_service_controller




    def get_room_types_table(self):
        """
        Pobiera dane z tabeli room_types.

        Returns:
            list: Lista słowników zawierających dane z tabeli room_types.
        """
        try:
            # Pobranie wszystkich danych z tabeli room_types
            query = "SELECT * FROM room_types"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            room_types_data = [dict(row) for row in cursor.fetchall()]
            # print(f"[### ROOM_SERVICE] Pobranie danych z tabeli room_types: {room_types_data}")

            return room_types_data

        except AttributeError as attr_error:
            print(f"[### ROOM_SERVICE] Błąd atrybutu: {str(attr_error)}")
            return []
        except TypeError as type_error:
            print(f"[### ROOM_SERVICE] Błąd typu danych: {str(type_error)}")
            return []



    def get_rooms_with_types(self):
        """
        Pobiera wszystkie pokoje i ich typy z tabeli `rooms`.
        """
        try:
            query = """
                SELECT r.room_id, r.room_number, r.floor, 
                    COALESCE(rt.room_type_id, 0) AS fk_room_type_id, 
                    COALESCE(rt.room_type, 'Nieznany typ') AS room_type
                FROM rooms r
                LEFT JOIN room_types rt ON r.fk_room_type_id = rt.room_type_id
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            rooms = []
            for row in cursor.fetchall():
                room_data = dict(row)
                room_data["fk_room_type_id"] = int(room_data["fk_room_type_id"])  # Konwersja na liczbę
                rooms.append(room_data)

            return rooms
        except sqlite3.OperationalError as op_err:
            print(f"[ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_room_reservations_with_detailed_rooms(self):
        """
        Pobiera wszystkie rezerwacje pokoi z tabeli `room_reservations`,
        zamieniając `fk_room_id` na pełne dane z tabeli `rooms`,
        oraz `fk_room_type_id` na pełne dane z tabeli `room_types`.
        Dane są sortowane od najpóźniejszej do najwcześniejszej rezerwacji.

        :return: Lista słowników z kompletnymi danymi rezerwacji.
        """
        try:
            # Pobranie listy typów pokoi
            room_types_list = self.get_room_types_table()
            room_types_dict = {int(rt["room_type_id"]): rt["room_type"] for rt in room_types_list}

            # Pobranie wszystkich pokoi z tabeli `rooms`
            query_rooms = """
                SELECT room_id, room_number, floor, 
                    COALESCE(fk_room_type_id, 0) AS fk_room_type_id
                FROM rooms
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query_rooms)
            rooms_data = {
                int(room["room_id"]): {
                    "room_id": int(room["room_id"]),
                    "room_number": room["room_number"],
                    "floor": room["floor"],
                    "fk_room_type_id": int(room["fk_room_type_id"]),
                    "room_type": room_types_dict.get(int(room["fk_room_type_id"]), "Nieznany typ"),
                }
                for room in cursor.fetchall()
            }

            # Pobranie wszystkich rezerwacji pokoi z tabeli `room_reservations`
            query_reservations = "SELECT reservation_id, fk_room_id, reservation_date, reservation_time FROM room_reservations ORDER BY reservation_id DESC"
            cursor = self.room_service_controller.db_controller.connection.execute(query_reservations)
            reservations_data = []

            for row in cursor.fetchall():
                reservation = dict(row)
                room_id = reservation.get("fk_room_id")

                # Upewnienie się, że room_id jest liczbą
                if room_id is not None:
                    room_id = int(room_id)

                room_info = rooms_data.get(room_id, {
                    "room_id": None,
                    "room_number": "Nieznany",
                    "floor": "Nieznane",
                    "room_type": "Nieznany typ"
                })

                # Sprawdzenie, czy `reservation_time` istnieje
                reservation_time = reservation.get("reservation_time", "Brak godziny")

                # Aktualizacja danych rezerwacji
                reservation.update(room_info)
                reservation["reservation_time"] = reservation_time  # Dodajemy godzinę rezerwacji
                reservation.pop("fk_room_id", None)  # Usunięcie klucza obcego

                reservations_data.append(reservation)

            return reservations_data

        except sqlite3.OperationalError as op_err:
            print(f"[ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []



    def get_all_room_numbers(self):
        """
        Pobiera wszystkie wartości `room_number` z tabeli `rooms`.

        :return: Lista numerów pokoi.
        """
        try:
            # Pobranie wszystkich `room_number` z tabeli `rooms`
            query = "SELECT room_number FROM rooms"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            room_numbers = [row["room_number"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych numerów pokoi
            print(f"[### ROOM_SERVICE] Pobranie numerów pokoi: {room_numbers}")

            return room_numbers

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_room_type_ids(self):
        """
        Pobiera wszystkie wartości `room_type_id` z tabeli `room_types`.

        :return: Lista identyfikatorów typów pokoi.
        """
        try:
            # Pobranie wszystkich `room_type_id` z tabeli `room_types`
            query = "SELECT room_type_id FROM room_types"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            room_type_ids = [row["room_type_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych identyfikatorów typów pokoi
            print(f"[### ROOM_SERVICE] Pobranie identyfikatorów typów pokoi: {room_type_ids}")

            return room_type_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_room_ids(self):
        """
        Pobiera wszystkie `room_id` z tabeli `rooms`.

        :return: Lista wszystkich `room_id` jako lista liczb całkowitych.
        """
        try:
            query = "SELECT room_id FROM rooms"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            room_ids = [row["room_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych room_id
            print(f"[### ROOM_SERVICE] Pobranie room_id: {room_ids}")

            return room_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []




    def get_all_room_reservations(self):
        """
        Pobiera wszystkie rekordy z tabeli `room_reservations`.

        :return: Lista słowników zawierających wszystkie dane rezerwacji.
        """
        try:
            query = "SELECT * FROM room_reservations"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            reservations = [dict(row) for row in cursor.fetchall()]  # Konwersja na listę słowników

            # Debug: Wyświetlenie pobranych rezerwacji
            print(f"[### ROOM_SERVICE] Pobranie rezerwacji pokoi: {reservations}")

            return reservations

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_all_room_types(self):
        """
        Pobiera wszystkie wartości z kolumny room_type z tabeli room_types.

        :return: Lista wszystkich room_type jako lista stringów.
        """
        try:
            query = "SELECT room_type FROM room_types"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            room_types = [row["room_type"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych typów pokoi
            print(f"[### ROOM_SERVICE] Pobranie room_type: {room_types}")

            return room_types

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []
        

    def get_all_reservation_ids(self):
        """
        Pobiera wszystkie `reservation_id` z tabeli `room_reservations`.

        :return: Lista wszystkich `reservation_id` jako lista liczb całkowitych.
        """
        try:
            query = "SELECT reservation_id FROM room_reservations"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            reservation_ids = [row["reservation_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych reservation_id
            print(f"[### ROOM_SERVICE] Pobranie reservation_id: {reservation_ids}")

            return reservation_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []
        
    def get_reservation_by_id(self, insert_reservation_id: int):
        """
        Pobiera rekord z tabeli `room_reservations` na podstawie `reservation_id`.

        :param insert_reservation_id: ID rezerwacji do pobrania.
        :return: Słownik zawierający dane rezerwacji lub None, jeśli nie znaleziono rekordu.
        """
        try:
            query = "SELECT * FROM room_reservations WHERE reservation_id = ?"
            cursor = self.room_service_controller.db_controller.connection.execute(query, (insert_reservation_id,))
            row = cursor.fetchone()

            if row is None:
                print(f"[### ROOM_SERVICE] Rezerwacja o ID {insert_reservation_id} nie istnieje.")
                return None

            reservation_data = dict(row)  # Konwersja obiektu `sqlite3.Row` na słownik

            # Debug: Wyświetlenie pobranej rezerwacji
            print(f"[### ROOM_SERVICE] Pobranie rezerwacji: {reservation_data}")

            return reservation_data

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return None

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return None
        
    def get_all_appointment_id_reservation_id(self):
        """
        Pobiera wszystkie `fk_reservation_id` i `appointment_id` z tabeli `appointments`.

        :return: Lista słowników, gdzie każdy słownik zawiera `fk_reservation_id` i `appointment_id`.
        """
        try:
            query = "SELECT fk_reservation_id, appointment_id FROM appointments"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            appointment_reservations = [dict(row) for row in cursor.fetchall()]  # Konwersja do listy słowników

            # Debug: Wyświetlenie pobranych rekordów
            print(f"[### ROOM_SERVICE] Pobranie wszystkich fk_reservation_id i appointment_id z appointments: {appointment_reservations}")

            return appointment_reservations

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_meeting_id_reservation_id(self):
        """
        Pobiera wszystkie `fk_reservation_id` i `meeting_id` z tabeli `internal_meetings`.

        :return: Lista słowników, gdzie każdy słownik zawiera `fk_reservation_id` i `meeting_id`.
        """
        try:
            query = "SELECT fk_reservation_id, meeting_id FROM internal_meetings"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            meeting_reservations = [dict(row) for row in cursor.fetchall()]  # Konwersja do listy słowników

            # Debug: Wyświetlenie pobranych rekordów
            print(f"[### ROOM_SERVICE] Pobranie wszystkich fk_reservation_id i meeting_id z internal_meetings: {meeting_reservations}")

            return meeting_reservations

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def table_get_all_appointments(self):
        """
        Pobiera i formatuje wszystkie rekordy z tabeli `appointments`.

        Returns:
            list: Lista sformatowanych słowników zawierających dane wizyt (`appointments`).
        """
        try:
            # Pobranie wszystkich wizyt
            query_appointments = "SELECT * FROM appointments"
            cursor = self.room_service_controller.db_controller.connection.execute(query_appointments)
            appointments_data = [dict(row) for row in cursor.fetchall()]

            if not appointments_data:
                print("[### ROOM_SERVICE] Brak wizyt w bazie danych.")
                return []

            # Pobranie dodatkowych danych do sformatowania wyników

            # Pobranie `assignment_id`, `fk_patient_id`, `fk_employee_id` z `assigned_patients`
            query_assigned_patients = "SELECT assignment_id, fk_patient_id, fk_employee_id FROM assigned_patients"
            cursor = self.room_service_controller.db_controller.connection.execute(query_assigned_patients)
            assigned_patients_data = {row["assignment_id"]: dict(row) for row in cursor.fetchall()}  # KONWERSJA NA SŁOWNIK

            # Pobranie imion i nazwisk pracowników
            query_employees = "SELECT employee_id, first_name, last_name FROM employees"
            cursor = self.room_service_controller.db_controller.connection.execute(query_employees)
            employees_data = {row["employee_id"]: f"{row['first_name']} {row['last_name']}" for row in cursor.fetchall()}

            # Pobranie imion i nazwisk pacjentów
            query_patients = "SELECT patient_id, first_name, last_name FROM patients"
            cursor = self.room_service_controller.db_controller.connection.execute(query_patients)
            patients_data = {row["patient_id"]: f"{row['first_name']} {row['last_name']}" for row in cursor.fetchall()}

            # Pobranie typów usług na podstawie `fk_service_id`
            query_services = "SELECT service_id, service_type FROM services"
            cursor = self.room_service_controller.db_controller.connection.execute(query_services)
            services_data = {row["service_id"]: row["service_type"] for row in cursor.fetchall()}

            # Pobranie `fk_room_id` na podstawie `fk_reservation_id` z `room_reservations`
            query_room_reservations = "SELECT reservation_id, fk_room_id FROM room_reservations"
            cursor = self.room_service_controller.db_controller.connection.execute(query_room_reservations)
            room_reservations_data = {row["reservation_id"]: row["fk_room_id"] for row in cursor.fetchall()}

            # Pobranie numerów pokojów na podstawie `room_id`
            query_rooms = "SELECT room_id, room_number FROM rooms"
            cursor = self.room_service_controller.db_controller.connection.execute(query_rooms)
            rooms_data = {row["room_id"]: row["room_number"] for row in cursor.fetchall()}

            # Formatowanie wyników
            formatted_appointments = []
            for appointment in appointments_data:
                assignment_id = appointment["fk_assignment_id"]
                patient_id = assigned_patients_data.get(assignment_id, {}).get("fk_patient_id", None)
                employee_id = assigned_patients_data.get(assignment_id, {}).get("fk_employee_id", None)
                service_id = appointment["fk_service_id"]
                reservation_id = appointment["fk_reservation_id"]

                formatted_appointments.append({
                    "appointment_id": appointment["appointment_id"],
                    "fk_assignment_id": assignment_id,
                    "patient_name": patients_data.get(patient_id, "Nieznany pacjent"),
                    "employee_name": employees_data.get(employee_id, "Nieznany pracownik"),
                    "fk_service_id": service_id,
                    "service_type": services_data.get(service_id, "Nieznana usługa"),
                    "fk_reservation_id": reservation_id,
                    "room_number": rooms_data.get(room_reservations_data.get(reservation_id), "Nieznany pokój"),
                    "appointment_date": appointment["appointment_date"],
                    "appointment_status": appointment["appointment_status"],
                    "notes": appointment["notes"],
                })

            # Debug: Wyświetlenie pobranych i sformatowanych danych
            # print(f"[### ROOM_SERVICE] Sformatowane dane wizyt: {formatted_appointments}")

            return formatted_appointments

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except KeyError as ke:
            print(f"[### ROOM_SERVICE] Błąd klucza w danych: {ke}")
            return []
        except TypeError as te:
            print(f"[### ROOM_SERVICE] Błąd przetwarzania danych: {te}")
            return []




    def table_get_formatted_appointments_for_employee(self, employee_id):
        """
        Pobiera i formatuje dane wizyt (`appointments`) dla podanego pracownika (`employee_id`).
        """
        try:
            if employee_id is None:
                print("[### ROOM_SERVICE] Brak przypisanego pracownika dla zalogowanego użytkownika.")
                return []

            # Pobranie wszystkich `assignment_id` przypisanych do `employee_id` z `assigned_patients`
            query_assignments = """
                SELECT assignment_id FROM assigned_patients WHERE fk_employee_id = ?
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query_assignments, (employee_id,))
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            if not assignment_ids:
                print(f"[### ROOM_SERVICE] Brak przypisanych pacjentów dla employee_id: {employee_id}")
                return []

            # Pobranie wszystkich rekordów z `appointments` na podstawie `fk_assignment_id`
            placeholders = ', '.join(['?'] * len(assignment_ids))
            query_appointments = f"""
                SELECT * FROM appointments WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
            appointments_data = [dict(row) for row in cursor.fetchall()]

            if not appointments_data:
                print(f"[### ROOM_SERVICE] Brak wizyt przypisanych do pracownika o ID {employee_id}")
                return []

            # Pobranie dodatkowych danych do sformatowania wyników

            # Pobranie `assignment_id`, `fk_patient_id`, `fk_employee_id` dla aktualnego `employee_id`
            query_assigned_patients = """
                SELECT assignment_id, fk_patient_id FROM assigned_patients WHERE fk_employee_id = ?
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query_assigned_patients, (employee_id,))
            assigned_patients_data = {row["assignment_id"]: row["fk_patient_id"] for row in cursor.fetchall()}

            # Pobranie imienia i nazwiska pracownika
            query_employee_name = """
                SELECT first_name, last_name FROM employees WHERE employee_id = ?
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query_employee_name, (employee_id,))
            employee_name = cursor.fetchone()
            employee_full_name = f"{employee_name['first_name']} {employee_name['last_name']}" if employee_name else "Nieznany"

            # Pobranie imienia i nazwiska pacjentów na podstawie `fk_patient_id`
            patient_ids = list(assigned_patients_data.values())
            if patient_ids:
                placeholders = ', '.join(['?'] * len(patient_ids))
                query_patients = f"""
                    SELECT patient_id, first_name, last_name FROM patients WHERE patient_id IN ({placeholders})
                """
                cursor = self.room_service_controller.db_controller.connection.execute(query_patients, patient_ids)
                patients_data = {row["patient_id"]: f"{row['first_name']} {row['last_name']}" for row in cursor.fetchall()}
            else:
                patients_data = {}

            # Pobranie typu usługi `service_type` na podstawie `fk_service_id`
            service_ids = [appointment["fk_service_id"] for appointment in appointments_data if appointment["fk_service_id"]]
            if service_ids:
                placeholders = ', '.join(['?'] * len(service_ids))
                query_services = f"""
                    SELECT service_id, service_type FROM services WHERE service_id IN ({placeholders})
                """
                cursor = self.room_service_controller.db_controller.connection.execute(query_services, service_ids)
                services_data = {row["service_id"]: row["service_type"] for row in cursor.fetchall()}
            else:
                services_data = {}

            # Pobranie `fk_room_id` na podstawie `fk_reservation_id` z `room_reservations`
            reservation_ids = [appointment["fk_reservation_id"] for appointment in appointments_data if appointment["fk_reservation_id"]]
            if reservation_ids:
                placeholders = ', '.join(['?'] * len(reservation_ids))
                query_room_reservations = f"""
                    SELECT reservation_id, fk_room_id FROM room_reservations WHERE reservation_id IN ({placeholders})
                """
                cursor = self.room_service_controller.db_controller.connection.execute(query_room_reservations, reservation_ids)
                room_reservations_data = {row["reservation_id"]: row["fk_room_id"] for row in cursor.fetchall()}
            else:
                room_reservations_data = {}

            # Pobranie numerów pokojów na podstawie `room_id`
            room_ids = list(room_reservations_data.values())
            if room_ids:
                placeholders = ', '.join(['?'] * len(room_ids))
                query_rooms = f"""
                    SELECT room_id, room_number FROM rooms WHERE room_id IN ({placeholders})
                """
                cursor = self.room_service_controller.db_controller.connection.execute(query_rooms, room_ids)
                rooms_data = {row["room_id"]: row["room_number"] for row in cursor.fetchall()}
            else:
                rooms_data = {}

            # Formatowanie wyników
            formatted_appointments = []
            for appointment in appointments_data:
                assignment_id = appointment["fk_assignment_id"]
                patient_id = assigned_patients_data.get(assignment_id, None)
                service_id = appointment["fk_service_id"]
                reservation_id = appointment["fk_reservation_id"]

                formatted_appointments.append({
                    "appointment_id": appointment["appointment_id"],
                    "fk_assignment_id": assignment_id,
                    "patient_name": patients_data.get(patient_id, "Nieznany pacjent"),
                    "employee_name": employee_full_name,
                    "fk_service_id": service_id,
                    "service_type": services_data.get(service_id, "Nieznana usługa"),
                    "fk_reservation_id": reservation_id,
                    "room_number": rooms_data.get(room_reservations_data.get(reservation_id), "Nieznany pokój"),
                    "appointment_date": appointment["appointment_date"],
                    "appointment_status": appointment["appointment_status"],
                    "notes": appointment["notes"],
                })

            # print(f"[############################### ROOM_SERVICE] Sformatowane dane: {formatted_appointments}")

            return formatted_appointments

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except KeyError as ke:
            print(f"[### ROOM_SERVICE] Błąd klucza w danych: {ke}")
            return []
        except TypeError as te:
            print(f"[### ROOM_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def table_get_all_meeting_types(self):
        """
        Pobiera wszystkie wartości z tabeli `meeting_types` i formatuje dane.

        :return: Lista słowników zawierających dane w formacie: `meeting_type_id`, `meeting_type`.
        """
        try:
            query = "SELECT meeting_type_id, meeting_type FROM meeting_types"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            meeting_types = [
                {"meeting_type_id": row["meeting_type_id"], "meeting_type": row["meeting_type"]}
                for row in cursor.fetchall()
            ]

            # Debug: Wyświetlenie pobranych i sformatowanych typów spotkań
            # print(f"[### ROOM_SERVICE] Pobranie meeting_types: {meeting_types}")

            return meeting_types

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def table_get_all_internal_meetings(self):
        """
        Pobiera i formatuje dane ze spotkań wewnętrznych (`internal_meetings`).

        :return: Lista słowników zawierających dane ze spotkań wewnętrznych.
        """
        try:
            # Pobranie wszystkich rekordów z `internal_meetings`
            query_meetings = "SELECT * FROM internal_meetings"
            cursor = self.room_service_controller.db_controller.connection.execute(query_meetings)
            meetings_data = [dict(row) for row in cursor.fetchall()]

            if not meetings_data:
                print("[### ROOM_SERVICE] Brak spotkań wewnętrznych w bazie.")
                return []

            # Pobranie wszystkich `fk_reservation_id`
            reservation_ids = [meeting["fk_reservation_id"] for meeting in meetings_data if meeting["fk_reservation_id"]]
            if reservation_ids:
                placeholders = ', '.join(['?'] * len(reservation_ids))
                query_room_reservations = f"""
                    SELECT reservation_id, fk_room_id FROM room_reservations WHERE reservation_id IN ({placeholders})
                """
                cursor = self.room_service_controller.db_controller.connection.execute(query_room_reservations, reservation_ids)
                room_reservations_data = {row["reservation_id"]: row["fk_room_id"] for row in cursor.fetchall()}
            else:
                room_reservations_data = {}

            # Pobranie numerów pokojów na podstawie `room_id`
            room_ids = list(room_reservations_data.values())
            if room_ids:
                placeholders = ', '.join(['?'] * len(room_ids))
                query_rooms = f"""
                    SELECT room_id, room_number FROM rooms WHERE room_id IN ({placeholders})
                """
                cursor = self.room_service_controller.db_controller.connection.execute(query_rooms, room_ids)
                rooms_data = {row["room_id"]: row["room_number"] for row in cursor.fetchall()}
            else:
                rooms_data = {}

            # Formatowanie wyników
            formatted_meetings = []
            for meeting in meetings_data:
                reservation_id = meeting["fk_reservation_id"]
                room_id = room_reservations_data.get(reservation_id, None)
                room_number = rooms_data.get(room_id, "Nieznany pokój")

                formatted_meetings.append({
                    "meeting_id": meeting["meeting_id"],
                    "fk_meeting_type_id": meeting["fk_meeting_type_id"],
                    "fk_reservation_id": reservation_id,
                    "room_number": room_number,
                    "meeting_date": meeting["meeting_date"],
                    "notes": meeting["notes"],
                    "internal_meeting_status": meeting["internal_meeting_status"],
                })

            # print(f"[############################### ROOM_SERVICE] Sformatowane dane: {formatted_meetings}")

            return formatted_meetings

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except KeyError as ke:
            print(f"[### ROOM_SERVICE] Błąd klucza w danych: {ke}")
            return []
        except TypeError as te:
            print(f"[### ROOM_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def get_all_assignment_ids_for_employee(self, employee_id):
        """
        Pobiera wszystkie `assignment_id` z tabeli `assigned_patients`, które są przypisane do podanego `employee_id`.

        :param employee_id: ID pracownika, dla którego mają zostać pobrane `assignment_id`.
        :return: Lista wartości `assignment_id` jako liczby całkowite.
        """
        try:
            if employee_id is None:
                print("[### BRIDGE_ROOM] Brak podanego employee_id.")
                return []

            query = "SELECT assignment_id FROM assigned_patients WHERE fk_employee_id = ?"
            cursor = self.room_service_controller.db_controller.connection.execute(query, (employee_id,))
            
            # Zmiana: Pobieramy bezpośrednio wartość z pierwszego elementu krotki
            assignment_ids = [row[0] for row in cursor.fetchall()]

            print(f"[### BRIDGE_ROOM] Pobranie assignment_id dla employee_id {employee_id}: {assignment_ids}")
            return assignment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### BRIDGE_ROOM] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### BRIDGE_ROOM] Błąd bazy danych: {db_err}")
            return []


    def get_all_service_ids_for_employee(self, employee_id):
        """
        Pobiera wszystkie `service_id` z tabeli `employee_services`, które są przypisane do podanego `employee_id`.

        :param employee_id: ID pracownika, dla którego mają zostać pobrane `service_id`.
        :return: Lista wartości `service_id` jako liczby całkowite.
        """
        try:
            if employee_id is None:
                print("[### BRIDGE_ROOM] Brak podanego employee_id.")
                return []

            query = "SELECT service_id FROM employee_services WHERE employee_id = ?"
            cursor = self.room_service_controller.db_controller.connection.execute(query, (employee_id,))
            
            # Zmiana: Pobieramy bezpośrednio wartość z pierwszego elementu krotki
            service_ids = [row[0] for row in cursor.fetchall()]

            print(f"[### BRIDGE_ROOM] Pobranie service_id dla employee_id {employee_id}: {service_ids}")
            return service_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### BRIDGE_ROOM] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### BRIDGE_ROOM] Błąd bazy danych: {db_err}")
            return []


    def get_reservation_datetime(self, insert_reservation_id):
        """
        Pobiera `reservation_date` i `reservation_time` z tabeli `room_reservations`
        na podstawie `insert_reservation_id`, a następnie łączy je w jeden string.

        :param insert_reservation_id: ID rezerwacji, dla której mają zostać pobrane dane.
        :return: String w formacie "YYYY-MM-DD HH:MM" lub pusty string w przypadku błędu.
        """
        try:
            # Sprawdzenie, czy insert_reservation_id jest podane
            if insert_reservation_id is None:
                print("[### BRIDGE_ROOM] Brak podanego insert_reservation_id.")
                return ""

            # Zapytanie SQL pobierające reservation_date i reservation_time
            query = """
                SELECT reservation_date, reservation_time 
                FROM room_reservations 
                WHERE reservation_id = ?
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query, (insert_reservation_id,))
            reservation_data = cursor.fetchone()

            # Sprawdzenie, czy znaleziono dane
            if not reservation_data:
                print(f"[### BRIDGE_ROOM] Brak danych dla insert_reservation_id {insert_reservation_id}.")
                return ""

            # Połączenie `reservation_date` i `reservation_time` w jeden string
            reservation_datetime = f"{reservation_data['reservation_date']} {reservation_data['reservation_time']}"

            # Debug: Wyświetlenie pobranych i sformatowanych danych
            print(f"[### BRIDGE_ROOM] Pobranie reservation_datetime dla insert_reservation_id {insert_reservation_id}: {reservation_datetime}")

            return reservation_datetime

        except sqlite3.OperationalError as op_err:
            print(f"[### BRIDGE_ROOM] Błąd operacyjny bazy danych: {op_err}")
            return ""

        except sqlite3.DatabaseError as db_err:
            print(f"[### BRIDGE_ROOM] Błąd bazy danych: {db_err}")
            return ""


    def get_all_assignment_ids(self):
        """
        Pobiera wszystkie assignment_id z tabeli assigned_patients.

        :return: Lista assignment_id jako lista liczb całkowitych.
        """
        try:
            query = "SELECT assignment_id FROM assigned_patients"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych assignment_id
            print(f"[### ROOM_SERVICE] Pobranie wszystkich assignment_id z assigned_patients: {assignment_ids}")

            return assignment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_service_ids(self):
        """
        Pobiera wszystkie service_id z tabeli services.

        :return: Lista service_id jako lista liczb całkowitych.
        """
        try:
            query = "SELECT service_id FROM services"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            service_ids = [row["service_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych service_id
            print(f"[### ROOM_SERVICE] Pobranie wszystkich service_id z services: {service_ids}")

            return service_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_all_appointment_ids(self):
        """
        Pobiera wszystkie `appointment_id` z tabeli `appointments`.

        :return: Lista `appointment_id` jako lista liczb całkowitych.
        """
        try:
            query = "SELECT appointment_id FROM appointments"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            appointment_ids = [row["appointment_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych appointment_id
            print(f"[### ROOM_SERVICE] Pobranie wszystkich appointment_id z appointments: {appointment_ids}")

            return appointment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_reservation_ids_from_appointments(self):
        """
        Pobiera wszystkie fk_reservation_id z tabeli appointments.

        :return: Lista fk_reservation_id jako lista liczb całkowitych.
        """
        try:
            query = "SELECT DISTINCT fk_reservation_id FROM appointments"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            reservation_ids = [row["fk_reservation_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych fk_reservation_id
            print(f"[### ROOM_SERVICE] Pobranie wszystkich fk_reservation_id z appointments: {reservation_ids}")

            return reservation_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_all_reservation_ids_from_internal_meetings(self):
        """
        Pobiera wszystkie wartości fk_reservation_id z tabeli internal_meetings.
        
        :return: Lista wartości fk_reservation_id jako liczby całkowite.
        :rtype: list[int]
        """
        try:
            query = "SELECT fk_reservation_id FROM internal_meetings"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            reservation_ids = [row[0] for row in cursor.fetchall()]  # Bezpośredni dostęp do wartości

            # Debug: wyświetlenie pobranych ID rezerwacji
            print(f"[### ROOM_SERVICE] Pobrano fk_reservation_id z internal_meetings: {reservation_ids}")
            
            return reservation_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny przy pobieraniu rezerwacji: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych przy pobieraniu rezerwacji: {db_err}")
            return []
        

    def get_appointment_ids_by_assignment(self, assignment_ids: list) -> list:
        """
        Pobiera wszystkie `appointment_id` na podstawie listy `assignment_ids` z tabeli `appointments`.

        :param assignment_ids: Lista ID przypisań pacjenta do pracownika
        :return: Lista ID wizyt lub pusta lista w przypadku błędu
        """
        try:
            # Walidacja danych wejściowych
            if not assignment_ids or not isinstance(assignment_ids, list):
                print("[### BRIDGE_ROOM] Nieprawidłowa lista assignment_ids")
                return []

            # Tworzenie placeholders dla zapytania SQL
            placeholders = ",".join("?" * len(assignment_ids))
            
            query = f"""
                SELECT appointment_id 
                FROM appointments 
                WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query, tuple(assignment_ids))
            
            appointments = [row["appointment_id"] for row in cursor.fetchall()]
            print(f"[### BRIDGE_ROOM] Pobrano appointment_ids dla assignment_ids {assignment_ids}: {appointments}")
            
            return appointments

        except sqlite3.OperationalError as op_err:
            print(f"[### BRIDGE_ROOM] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### BRIDGE_ROOM] Błąd bazy danych: {db_err}")
            return []


    def get_all_appointment_ids_diagnoses_ids_from_diagnoses(self):
        """
        Pobiera wszystkie dane z kolumn fk_appointment_id i diagnosis_id z tabeli diagnoses.

        :return: Lista słowników zawierających 'fk_appointment_id' i 'diagnosis_id'.
        """
        try:
            query = "SELECT fk_appointment_id, diagnosis_id FROM diagnoses"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            diagnoses = [{"fk_appointment_id": row["fk_appointment_id"], "diagnosis_id": row["diagnosis_id"]} 
                         for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych diagnoz
            print(f"[### ROOM_SERVICE] Pobranie wszystkich diagnosis_id z diagnoses: {diagnoses}")

            return diagnoses

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych podczas pobierania diagnoz: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych podczas pobierania diagnoz: {db_err}")
            return []


    def get_all_appointment_ids_prescriptions_ids_from_prescriptions(self):
        """
        Pobiera wszystkie dane z kolumn fk_appointment_id i prescription_id z tabeli prescriptions.

        :return: Lista słowników zawierających 'fk_appointment_id' i 'prescription_id'.
        """
        try:
            query = "SELECT fk_appointment_id, prescription_id FROM prescriptions"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            prescriptions = [{"fk_appointment_id": row["fk_appointment_id"], "prescription_id": row["prescription_id"]} 
                             for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych recept
            print(f"[### ROOM_SERVICE] Pobranie wszystkich prescription_id z prescriptions: {prescriptions}")

            return prescriptions

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych podczas pobierania recept: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych podczas pobierania recept: {db_err}")
            return []
        

    def get_all_meeting_ids(self):
        """
        Pobiera wszystkie meeting_id z tabeli internal_meetings.

        :return: Lista meeting_id jako lista liczb całkowitych.
        """
        try:
            query = "SELECT meeting_id FROM internal_meetings"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            meeting_ids = [row["meeting_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych meeting_id
            print(f"[### ROOM_SERVICE] Pobranie wszystkich meeting_id z internal_meetings: {meeting_ids}")

            return meeting_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []

        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_participant_ids(self):
        """
        Pobiera wszystkie `participant_id` z tabeli `meeting_participants`.

        :return: Lista participant_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `participant_id` z tabeli `meeting_participants`
            query = "SELECT participant_id FROM meeting_participants"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            participant_ids = [row["participant_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych participant_id
            print(f"[### ROOM_SERVICE] Pobranie participant_id z meeting_participants: {participant_ids}")

            return participant_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_meeting_participants_table(self):
        """
        Pobiera dane z tabeli meeting_participants oraz dołącza imiona i nazwiska z tabeli employees.

        Returns:
            list: Lista słowników zawierających dane z tabeli meeting_participants oraz kolumnę employee_name.
        """
        try:
            # Zapytanie SQL pobierające dane uczestników oraz imię i nazwisko pracownika
            query = """
                SELECT 
                    mp.participant_id, 
                    mp.fk_meeting_id, 
                    mp.fk_employee_id, 
                    e.first_name || ' ' || e.last_name AS employee_name,
                    mp.participant_role, 
                    mp.attendance
                FROM meeting_participants mp
                LEFT JOIN employees e ON mp.fk_employee_id = e.employee_id
            """
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            
            # Konwersja wyników do listy słowników
            meeting_participants_data = [dict(row) for row in cursor.fetchall()]

            # Debugowanie danych
            # print(f"[### ROOM_SERVICE] Pobranie danych z tabeli meeting_participants: {meeting_participants_data}")

            return meeting_participants_data

        except AttributeError as attr_error:
            print(f"[### ROOM_SERVICE] Błąd atrybutu: {str(attr_error)}")
            return []
        except TypeError as type_error:
            print(f"[### ROOM_SERVICE] Błąd typu danych: {str(type_error)}")
            return []
        except sqlite3.DatabaseError as db_error:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {str(db_error)}")
            return []



    def get_all_employee_id_for_assignment(self, assignment_id):
        """
        Pobiera wszystkie `fk_employee_id` z tabeli `assigned_patients` na podstawie `assignment_id`.

        :return: Lista `fk_employee_id` jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `fk_employee_id` z tabeli `assigned_patients`
            query = "SELECT fk_employee_id FROM assigned_patients WHERE assignment_id = ?"
            cursor = self.room_service_controller.db_controller.connection.execute(query, (assignment_id,))
            employee_ids = [row["fk_employee_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych fk_employee_id
            print(f"[### ROOM_SERVICE get_all_employee_id_for_assignment] Pobranie fk_employee_id z assigned_patients: {employee_ids}")

            return employee_ids if employee_ids else []

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE get_all_employee_id_for_assignment] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE get_all_employee_id_for_assignment] Błąd bazy danych: {db_err}")
            return []

    def get_all_service_ids_by_employee(self, employee_ids):
        """
        Pobiera wszystkie service_id z tabeli employee_services na podstawie employee_id.

        :param employee_ids: Lista ID pracowników, dla których pobierane są usługi.
        :return: Lista service_id jako lista liczb całkowitych.
        """
        try:
            # Jeśli employee_ids to lista, należy ją przekonwertować na poprawny format do SQL (wielokrotne bindery)
            if not isinstance(employee_ids, list):
                employee_ids = [employee_ids]  # Zamiana pojedynczej wartości na listę

            if not employee_ids:  # Jeśli lista jest pusta, zwracamy pustą listę
                return []

            placeholders = ", ".join("?" * len(employee_ids))  # Tworzenie dynamicznych placeholderów (?,?,?)
            query = f"SELECT service_id FROM employee_services WHERE employee_id IN ({placeholders})"

            cursor = self.room_service_controller.db_controller.connection.execute(query, employee_ids)
            service_ids = [row["service_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych service_id
            print(f"[### ROOM_SERVICE get_all_service_ids_by_employee] Pobranie service_id dla employee_id {employee_ids}: {service_ids}")

            return service_ids if service_ids else []

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE get_all_service_ids_by_employee] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE get_all_service_ids_by_employee] Błąd bazy danych: {db_err}")
            return []


    def get_all_meeting_type_ids(self):
        """
        Pobiera wszystkie meeting_type_id z tabeli meeting_types.

        :return: Lista meeting_type_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich meeting_type_id z tabeli meeting_types
            query = "SELECT meeting_type_id FROM meeting_types"
            cursor = self.room_service_controller.db_controller.connection.execute(query)
            meeting_type_ids = [row["meeting_type_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych meeting_type_id
            print(f"[### ROOM_SERVICE] Pobranie meeting_type_id z meeting_types: {meeting_type_ids}")

            return meeting_type_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ROOM_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ROOM_SERVICE] Błąd bazy danych: {db_err}")
            return []
