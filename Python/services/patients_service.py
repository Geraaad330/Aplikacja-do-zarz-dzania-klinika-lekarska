import sqlite3
from controllers.users_accounts_controller import UsersAccountsController
from controllers.patients_controller import PatientController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.diagnoses_controller import DiagnosesController
from controllers.prescriptions_controller import PrescriptionsController

class PatientsService():
    """
    Klasa obsługująca logikę wyświetlania pacjentów w zależności od roli użytkownika.
    """

    def __init__(self, patients_service_controller):
        self.patients_service_controller = patients_service_controller

    def table_get_patients_for_user(self, insert_employee_id: int) -> list:
        """
        Pobiera listę pacjentów do wyświetlenia w zależności od roli użytkownika.
        """
        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.patients_service_controller.db_controller)
            patients_controller = PatientController(self.patients_service_controller.db_controller)
            assigned_patients_controller = AssignedPatientsController(self.patients_service_controller.db_controller)

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(insert_employee_id)
            # print(f"[patients_service] Pobrano role_id {role_id} dla user_id {user_id}")  # Debug

            # USER_ID POBIERANY Z dashboard_service.py

            # Logika oparta na roli
            if role_id in [1, 2, 9, 10]:
                # Role z pełnym dostępem do wszystkich pacjentów
                patients = patients_controller.get_all_patients_details()
                # print(f"[patients_service] Pobranie wszystkich pacjentów dla role_id {role_id}: {len(patients)} rekordów")  # Debug
            elif role_id in [3, 4, 5, 6, 7, 8]:
                # Role z ograniczonym dostępem do przypisanych pacjentów
                assigned_patients = assigned_patients_controller.get_assigned_patients_by_employee_id(insert_employee_id)
                # print(f"[patients_service] Pobranie przypisanych pacjentów dla role_id {role_id}: {len(assigned_patients)} rekordów")  # Debug
                patients = []
                for assigned_patient in assigned_patients:
                    patient_id = assigned_patient['fk_patient_id']
                    patient_details = patients_controller.get_patient_by_id(patient_id)  # Pobieranie danych jednego pacjenta
                    if patient_details:
                        patients.append(patient_details)
                # print(f"[patients_service] Łącznie pobrano {len(patients)} pacjentów przypisanych użytkownikowi {insert_employee_id}")  # Debug
            else:
                print(f"[patients_service] Nieznana rola: {role_id}")  # Debug
                raise ValueError(f"Nieznana rola: {role_id}")

            return patients

        except ValueError as ve:
            print(f"[patients_service] Błąd danych wejściowych: {ve}")  # Debug
            raise ValueError(f"Błąd danych wejściowych: {ve}") from ve
        except KeyError as ke:
            print(f"[patients_service] Błąd klucza: {ke}")  # Debug
            raise KeyError(f"Błąd klucza: {ke}") from ke
        except AttributeError as ae:
            print(f"[patients_service] Błąd atrybutu: {ae}")  # Debug
            raise AttributeError(f"Błąd atrybutu: {ae}") from ae

    def table_get_diagnoses_data(self, logged_in_user_id):
        """
        Pobiera listę diagnoz dla użytkownika z określoną rolą.

        - Jeśli użytkownik ma `role_id in [1, 2, 9, 10]`, pobiera wszystkie diagnozy.
        - Jeśli `role_id in [3, 4, 5, 6, 7, 8]`, pobiera diagnozy związane z pacjentami przypisanymi do pracownika.
        
        Args:
            logged_in_user_id (int): ID zalogowanego użytkownika.

        Returns:
            list: Lista słowników zawierających szczegóły diagnoz.
        """
        try:
            # Pobranie roli użytkownika
            users_accounts_controller = UsersAccountsController(self.patients_service_controller.db_controller)
            role_id = users_accounts_controller.get_role_id_by_user_id(logged_in_user_id)

            formatted_diagnoses_data = []

            # ----------------------- ROLA: ADMIN / SPECJALISTA -----------------------
            if role_id in [1, 2, 9, 10]:  
                # print(f"[### PATIENTS_SERVICE] Pobieranie wszystkich diagnoz dla użytkownika {logged_in_user_id}")

                diagnoses_controller = DiagnosesController(self.patients_service_controller.db_controller)
                diagnoses_data = diagnoses_controller.get_all_diagnoses()

                if not diagnoses_data:
                    return []

                # Pobranie appointment_id z diagnoz
                appointment_ids = list(set(diagnosis["fk_appointment_id"] for diagnosis in diagnoses_data))

                # Pobranie fk_assignment_id dla appointment_id
                placeholders = ", ".join(["?"] * len(appointment_ids))
                query_assignments = f"""
                SELECT appointment_id, fk_assignment_id
                FROM appointments
                WHERE appointment_id IN ({placeholders})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, appointment_ids)
                appointment_to_assignment = {row[0]: row[1] for row in cursor.fetchall()}

                # Pobranie fk_patient_id dla assignment_id
                assignment_ids = list(set(appointment_to_assignment.values()))
                query_patients = f"""
                SELECT assignment_id, fk_patient_id
                FROM assigned_patients
                WHERE assignment_id IN ({", ".join(["?"] * len(assignment_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_patients, assignment_ids)
                assignment_to_patient = {row[0]: row[1] for row in cursor.fetchall()}

                # Pobranie first_name, last_name, is_active dla pacjentów
                patient_ids = list(set(assignment_to_patient.values()))
                query_patient_details = f"""
                SELECT patient_id, first_name, last_name, is_active
                FROM patients
                WHERE patient_id IN ({", ".join(["?"] * len(patient_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_patient_details, patient_ids)
                patient_details = {row[0]: {"first_name": row[1], "last_name": row[2], "is_active": row[3]} for row in cursor.fetchall()}

                # Formatowanie danych
                for diagnosis in diagnoses_data:
                    appointment_id = diagnosis["fk_appointment_id"]
                    assignment_id = appointment_to_assignment.get(appointment_id)
                    patient_id = assignment_to_patient.get(assignment_id)

                    patient_name = f"{patient_details[patient_id]['first_name']} {patient_details[patient_id]['last_name']}" if patient_id in patient_details else "Nieznany Pacjent"
                    is_active = patient_details[patient_id]["is_active"] if patient_id in patient_details else "Brak danych"

                    formatted_diagnoses_data.append({
                        "diagnosis_id": diagnosis["diagnosis_id"],
                        "fk_appointment_id": diagnosis["fk_appointment_id"],
                        "patient_name": patient_name,
                        "is_active": is_active,
                        "description": diagnosis["description"],
                        "icd11_code": diagnosis["icd11_code"]
                    })

            # -------------------- ROLA: LEKARZ / TERAPEUTA / PSYCHOLOG --------------------
            elif role_id in [3, 4, 5, 6, 7, 8]:
                # print(f"[### PATIENTS_SERVICE] Pobieranie diagnoz przypisanych do pracownika {logged_in_user_id}")

                employee_id = users_accounts_controller.get_employee_id_by_user_id(logged_in_user_id)
                if not employee_id:
                    print(f"[### PATIENTS_SERVICE] Brak przypisanego employee_id dla użytkownika: {logged_in_user_id}")
                    return []

                # Pobranie assignment_id i fk_patient_id dla pracownika
                query_assignments = """
                SELECT assignment_id, fk_patient_id
                FROM assigned_patients
                WHERE fk_employee_id = ?
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, (employee_id,))
                assignments = cursor.fetchall()
                assignment_map = {row[0]: row[1] for row in assignments}

                if not assignment_map:
                    return []

                # Pobranie danych pacjentów
                patient_ids = list(set(assignment_map.values()))
                query_patients = f"""
                SELECT patient_id, first_name || ' ' || last_name AS full_name, is_active
                FROM patients
                WHERE patient_id IN ({", ".join(["?"] * len(patient_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_patients, patient_ids)
                patients_map = {row[0]: {"full_name": row[1], "is_active": row[2]} for row in cursor.fetchall()}

                # Pobranie appointment_id dla assignment_id
                assignment_ids = list(assignment_map.keys())
                query_appointments = f"""
                SELECT appointment_id, fk_assignment_id
                FROM appointments
                WHERE fk_assignment_id IN ({", ".join(["?"] * len(assignment_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
                appointment_map = {row[0]: row[1] for row in cursor.fetchall()}

                if not appointment_map:
                    return []

                # Pobranie diagnosis_id dla appointment_id
                appointment_ids = list(appointment_map.keys())
                query_diagnoses = f"""
                SELECT diagnosis_id, fk_appointment_id, description, icd11_code
                FROM diagnoses
                WHERE fk_appointment_id IN ({", ".join(["?"] * len(appointment_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_diagnoses, appointment_ids)
                diagnoses_data = cursor.fetchall()

                if not diagnoses_data:
                    return []

                # Formatowanie wyników
                for diagnosis in diagnoses_data:
                    diagnosis_id, fk_appointment_id, description, icd11_code = diagnosis
                    fk_assignment_id = appointment_map.get(fk_appointment_id)
                    fk_patient_id = assignment_map.get(fk_assignment_id, None)

                    patient_name = patients_map[fk_patient_id]["full_name"] if fk_patient_id in patients_map else "Nieznany pacjent"
                    is_active = patients_map[fk_patient_id]["is_active"] if fk_patient_id in patients_map else "Brak danych"

                    formatted_diagnoses_data.append({
                        "diagnosis_id": diagnosis_id,
                        "fk_appointment_id": fk_appointment_id,
                        "patient_name": patient_name,
                        "is_active": is_active,
                        "description": description,
                        "icd11_code": icd11_code
                    })

            return formatted_diagnoses_data

        except ValueError as ve:
            print(f"[### PATIENTS_SERVICE] Błąd danych wejściowych: {ve}")
        except KeyError as ke:
            print(f"[### PATIENTS_SERVICE] Błąd klucza: {ke}")
        except AttributeError as ae:
            print(f"[### PATIENTS_SERVICE] Błąd atrybutów: {ae}")



    def table_get_prescriptions_data(self, logged_in_user_id):
        """
        Pobiera listę recept dla użytkownika z określoną rolą.

        - Jeśli użytkownik ma `role_id in [1, 2, 9, 10]`, pobiera wszystkie recepty.
        
        Args:
            logged_in_user_id (int): ID zalogowanego użytkownika.

        Returns:
            list: Lista słowników zawierających szczegóły recept.
        """
        try:
            # Pobranie roli użytkownika
            users_accounts_controller = UsersAccountsController(self.patients_service_controller.db_controller)
            role_id = users_accounts_controller.get_role_id_by_user_id(logged_in_user_id)

            formatted_prescriptions_data = []

            # ----------------------- ROLA: ADMIN / SPECJALISTA -----------------------
            if role_id in [1, 2, 9, 10]:  
                # print(f"[### PATIENTS_SERVICE] Pobieranie wszystkich recept dla użytkownika {logged_in_user_id}")

                prescriptions_controller = PrescriptionsController(self.patients_service_controller.db_controller)
                prescriptions_data = prescriptions_controller.get_all_prescriptions()

                # print(f"[### PATIENTS_SERVICE] Pobranie wszystkich recept: {prescriptions_data}")

                if not prescriptions_data:
                    return []

                # Pobranie appointment_id z recept
                appointment_ids = list(set(prescription["fk_appointment_id"] for prescription in prescriptions_data))

                # Pobranie fk_assignment_id dla appointment_id
                placeholders = ", ".join(["?"] * len(appointment_ids))
                query_assignments = f"""
                SELECT appointment_id, fk_assignment_id
                FROM appointments
                WHERE appointment_id IN ({placeholders})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, appointment_ids)
                appointment_to_assignment = {row[0]: row[1] for row in cursor.fetchall()}

                # print(f"[### PATIENTS_SERVICE] Pobranie powiązań appointment_id -> fk_assignment_id: {appointment_to_assignment}")

                # Pobranie fk_patient_id dla assignment_id
                assignment_ids = list(set(appointment_to_assignment.values()))
                query_patients = f"""
                SELECT assignment_id, fk_patient_id
                FROM assigned_patients
                WHERE assignment_id IN ({", ".join(["?"] * len(assignment_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_patients, assignment_ids)
                assignment_to_patient = {row[0]: row[1] for row in cursor.fetchall()}

                # print(f"[### PATIENTS_SERVICE] Pobranie powiązań assignment_id -> fk_patient_id: {assignment_to_patient}")

                # Pobranie first_name, last_name, is_active dla pacjentów
                patient_ids = list(set(assignment_to_patient.values()))
                query_patient_details = f"""
                SELECT patient_id, first_name, last_name, is_active
                FROM patients
                WHERE patient_id IN ({", ".join(["?"] * len(patient_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_patient_details, patient_ids)
                patient_details = {row[0]: {"first_name": row[1], "last_name": row[2], "is_active": row[3]} for row in cursor.fetchall()}

                # print(f"[### PATIENTS_SERVICE] Pobranie danych pacjentów: {patient_details}")

                # Formatowanie danych
                for prescription in prescriptions_data:
                    appointment_id = prescription["fk_appointment_id"]
                    assignment_id = appointment_to_assignment.get(appointment_id)
                    patient_id = assignment_to_patient.get(assignment_id)

                    patient_name = f"{patient_details[patient_id]['first_name']} {patient_details[patient_id]['last_name']}" if patient_id in patient_details else "Nieznany Pacjent"
                    is_active = patient_details[patient_id]["is_active"] if patient_id in patient_details else "Brak danych"

                    formatted_prescriptions_data.append({
                        "prescription_id": prescription["prescription_id"],
                        "appointment_id": prescription["fk_appointment_id"],
                        "patient_name": patient_name,
                        "is_active": is_active,
                        "medicine_name": prescription["medicine_name"],
                        "dosage": prescription["dosage"],
                        "medicine_price": prescription["medicine_price"],
                        "prescription_code": prescription["prescription_code"]
                    })


            elif role_id in [3]:
                print(f"[### PATIENTS_SERVICE] Pobieranie recept dla użytkownika: {logged_in_user_id}")

                # Pobranie employee_id
                employee_id = users_accounts_controller.get_employee_id_by_user_id(logged_in_user_id)
                if not employee_id:
                    print(f"[### PATIENTS_SERVICE] Brak przypisanego employee_id dla użytkownika: {logged_in_user_id}")
                    return []

                # Pobranie assignment_id i fk_patient_id dla employee_id
                query_assignments = """
                SELECT assignment_id, fk_patient_id
                FROM assigned_patients
                WHERE fk_employee_id = ?
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, (employee_id,))
                assignments = cursor.fetchall()
                assignment_map = {row[0]: row[1] for row in assignments}

                # print(f"[### PATIENTS_SERVICE] Pobranie assignment_id i fk_patient_id: {assignment_map}")

                if not assignment_map:
                    print("[### PATIENTS_SERVICE] Brak przypisanych pacjentów dla pracownika.")
                    return []

                # Pobranie danych pacjentów (imienia, nazwiska i statusu)
                patient_ids = list(set(assignment_map.values()))
                query_patients = f"""
                SELECT patient_id, first_name || ' ' || last_name AS full_name, is_active
                FROM patients
                WHERE patient_id IN ({", ".join(["?"] * len(patient_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_patients, patient_ids)
                patients_map = {row[0]: {"full_name": row[1], "is_active": row[2]} for row in cursor.fetchall()}

                # print(f"[### PATIENTS_SERVICE] Pobranie danych pacjentów: {patients_map}")

                # Pobranie appointment_id dla assignment_id
                assignment_ids = list(assignment_map.keys())
                query_appointments = f"""
                SELECT appointment_id, fk_assignment_id
                FROM appointments
                WHERE fk_assignment_id IN ({", ".join(["?"] * len(assignment_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
                appointment_map = {row[0]: row[1] for row in cursor.fetchall()}

                # print(f"[### PATIENTS_SERVICE] Pobranie appointment_id na podstawie assignment_id: {appointment_map}")

                if not appointment_map:
                    print("[### PATIENTS_SERVICE] Brak przypisanych wizyt do pacjentów.")
                    return []

                # Pobranie wszystkich recept dla pobranych appointment_id
                appointment_ids = list(appointment_map.keys())
                query_prescriptions = f"""
                SELECT prescription_id, fk_appointment_id, medicine_name, dosage, medicine_price, prescription_code
                FROM prescriptions
                WHERE fk_appointment_id IN ({", ".join(["?"] * len(appointment_ids))})
                """
                cursor = self.patients_service_controller.db_controller.connection.execute(query_prescriptions, appointment_ids)
                prescriptions_data = cursor.fetchall()

                # print(f"[### PATIENTS_SERVICE] Pobranie recept: {prescriptions_data}")

                if not prescriptions_data:
                    print("[### PATIENTS_SERVICE] Brak przypisanych recept do wizyt.")
                    return []

                # **Formatowanie danych do wyświetlenia**
                for prescription in prescriptions_data:
                    prescription_id, fk_appointment_id, medicine_name, dosage, medicine_price, prescription_code = prescription
                    fk_assignment_id = appointment_map.get(fk_appointment_id)
                    fk_patient_id = assignment_map.get(fk_assignment_id, None)

                    patient_name = patients_map[fk_patient_id]["full_name"] if fk_patient_id in patients_map else "Nieznany pacjent"
                    is_active = patients_map[fk_patient_id]["is_active"] if fk_patient_id in patients_map else "Brak danych"

                    formatted_prescriptions_data.append({
                        "prescription_id": prescription_id,
                        "appointment_id": fk_appointment_id,
                        "patient_name": patient_name,
                        "is_active": is_active,
                        "medicine_name": medicine_name,
                        "dosage": dosage,
                        "medicine_price": medicine_price,
                        "prescription_code": prescription_code
                    })

                # print(f"[### PATIENTS_SERVICE] Końcowe wyniki recept: {formatted_prescriptions_data}")

            return formatted_prescriptions_data

        except ValueError as ve:
            print(f"[### PATIENTS_SERVICE] Błąd danych wejściowych: {ve}")
        except KeyError as ke:
            print(f"[### PATIENTS_SERVICE] Błąd klucza: {ke}")
        except AttributeError as ae:
            print(f"[### PATIENTS_SERVICE] Błąd atrybutów: {ae}")


    def get_all_patient_id_assigned(self):
        """
        Pobiera wszystkie `fk_patient_id` z tabeli `assigned_patients`.

        :return: Lista `fk_patient_id` jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `fk_patient_id` z tabeli `assigned_patients`
            query = "SELECT fk_patient_id FROM assigned_patients"
            cursor = self.patients_service_controller.db_controller.connection.execute(query)
            patient_ids = [row["fk_patient_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych wartości
            print(f"[### ADMIN_SERVICE] Pobranie fk_patient_id z assigned_patients: {patient_ids}")

            return patient_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []




    def get_appointments_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie appointment_id przypisane do podanego employee_id
        poprzez assignment_id.

        :param employee_id: ID pracownika, dla którego pobierane są wizyty.
        :return: Lista appointment_id.
        """
        try:
            # Pobranie wszystkich assignment_id przypisanych do employee_id
            query_assignments = """
                SELECT assignment_id FROM assigned_patients WHERE fk_employee_id = ?
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, (employee_id,))
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            if not assignment_ids:
                print(f"[### PATIENTS_SERVICE] Brak przypisanych assignment_id dla employee_id: {employee_id}.")
                return []

            # Pobranie wszystkich appointment_id na podstawie assignment_id
            placeholders = ', '.join(['?'] * len(assignment_ids))
            query_appointments = f"""
                SELECT appointment_id FROM appointments WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
            appointment_ids = [row["appointment_id"] for row in cursor.fetchall()]

            if not appointment_ids:
                print(f"[### PATIENTS_SERVICE] Brak przypisanych appointment_id dla employee_id: {employee_id}.")
                return []

            return appointment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except TypeError as te:
            print(f"[### PATIENTS_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def get_all_appointment_ids_diagnoses(self):
        """
        Pobiera wszystkie fk_appointment_id z tabeli diagnoses.

        :return: Lista fk_appointment_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich fk_appointment_id z tabeli diagnoses
            query = "SELECT fk_appointment_id FROM diagnoses"
            cursor =  self.patients_service_controller.db_controller.connection.execute(query)
            appointment_ids = [row["fk_appointment_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych fk_appointment_id
            print(f"[### PATIENTS_SERVICE] Pobranie fk_appointment_id z diagnoses: {appointment_ids}")

            return appointment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_appointment_ids_appointments_table(self):
        """
        Pobiera wszystkie appointment_id z tabeli appointments.

        :return: Lista appointment_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich appointment_id z tabeli appointments
            query = "SELECT appointment_id FROM appointments"
            cursor = self.patients_service_controller.db_controller.connection.execute(query)
            appointment_ids = [row["appointment_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych appointment_id
            print(f"[### PATIENTS_SERVICE] Pobranie appointment_id z appointments: {appointment_ids}")

            return appointment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_diagnosis_ids(self):
        """
        Pobiera wszystkie diagnosis_id z tabeli diagnoses.

        :return: Lista diagnosis_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich diagnosis_id z tabeli diagnoses
            query = "SELECT diagnosis_id FROM diagnoses"
            cursor = self.patients_service_controller.db_controller.connection.execute(query)
            diagnosis_ids = [row["diagnosis_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych diagnosis_id
            print(f"[### PATIENTS_SERVICE] Pobranie diagnosis_id z diagnoses: {diagnosis_ids}")

            return diagnosis_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_diagnosis_by_id_diagnoses_table(self, diagnosis_id):
        """
        Pobiera wszystkie kolumny rekordu z tabeli diagnoses na podstawie diagnosis_id.

        :param diagnosis_id: ID diagnozy do pobrania.
        :return: Słownik zawierający dane diagnozy lub None, jeśli nie znaleziono.
        """
        try:
            # Pobranie wszystkich kolumn dla podanego diagnosis_id
            query = "SELECT * FROM diagnoses WHERE diagnosis_id = ?"
            cursor = self.patients_service_controller.db_controller.connection.execute(query, (diagnosis_id,))
            diagnosis_record = cursor.fetchone()

            if diagnosis_record is None:
                print(f"[### PATIENTS_SERVICE] Diagnoza o ID {diagnosis_id} nie istnieje w bazie.")
                return None

            # Konwersja na słownik
            diagnosis_dict = dict(diagnosis_record)

            # Debug: Wyświetlenie pobranego rekordu
            print(f"[### PATIENTS_SERVICE] Pobranie danych diagnozy: {diagnosis_dict}")

            return diagnosis_dict

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return None
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return None


    def get_diagnosis_id_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie diagnosis_id przypisane do podanego employee_id
        poprzez powiązane appointment_id.

        :param employee_id: ID pracownika, dla którego pobierane są diagnozy.
        :return: Lista diagnosis_id przypisanych do danego pracownika.
        """
        try:
            # Pobranie wszystkich assignment_id przypisanych do employee_id
            query_assignments = """
                SELECT assignment_id FROM assigned_patients WHERE fk_employee_id = ?
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, (employee_id,))
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            if not assignment_ids:
                print(f"[### PATIENTS_SERVICE] Brak przypisanych assignment_id dla employee_id: {employee_id}.")
                return []

            # Pobranie wszystkich appointment_id na podstawie assignment_id
            placeholders = ', '.join(['?'] * len(assignment_ids))
            query_appointments = f"""
                SELECT appointment_id FROM appointments WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
            appointment_ids = [row["appointment_id"] for row in cursor.fetchall()]

            if not appointment_ids:
                print(f"[### PATIENTS_SERVICE] Brak przypisanych appointment_id dla employee_id: {employee_id}.")
                return []

            # Pobranie wszystkich diagnosis_id na podstawie fk_appointment_id
            placeholders = ', '.join(['?'] * len(appointment_ids))
            query_diagnoses = f"""
                SELECT diagnosis_id FROM diagnoses WHERE fk_appointment_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_diagnoses, appointment_ids)
            diagnosis_ids = [row["diagnosis_id"] for row in cursor.fetchall()]

            print(f"################# Przypisane diagnozy: {diagnosis_ids}")

            return diagnosis_ids  # Teraz zwraca tylko listę diagnosis_id

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except TypeError as te:
            print(f"[### PATIENTS_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def get_all_prescription_codes(self):
        """
        Pobiera wszystkie prescription_code z tabeli prescriptions.

        :return: Lista prescription_code jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich prescription_code z tabeli prescriptions
            query = "SELECT prescription_code FROM prescriptions"
            cursor = self.patients_service_controller.db_controller.connection.execute(query)
            prescription_codes = [row["prescription_code"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych prescription_code
            print(f"[### PATIENTS_SERVICE] Pobranie prescription_code z prescriptions: {prescription_codes}")

            return prescription_codes

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []



    def get_prescriptions_id_by_employee_id(self, employee_id):
        """
        Pobiera wszystkie diagnosis_id przypisane do podanego employee_id
        poprzez powiązane appointment_id.

        :param employee_id: ID pracownika, dla którego pobierane są diagnozy.
        :return: Lista diagnosis_id przypisanych do danego pracownika.
        """
        try:
            # Pobranie wszystkich assignment_id przypisanych do employee_id
            query_assignments = """
                SELECT assignment_id FROM assigned_patients WHERE fk_employee_id = ?
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, (employee_id,))
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            if not assignment_ids:
                print(f"[### PATIENTS_SERVICE] Brak przypisanych assignment_id dla employee_id: {employee_id}.")
                return []

            # Pobranie wszystkich appointment_id na podstawie assignment_id
            placeholders = ', '.join(['?'] * len(assignment_ids))
            query_appointments = f"""
                SELECT appointment_id FROM appointments WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
            appointment_ids = [row["appointment_id"] for row in cursor.fetchall()]

            if not appointment_ids:
                print(f"[### PATIENTS_SERVICE] Brak przypisanych appointment_id dla employee_id: {employee_id}.")
                return []

            # Pobranie wszystkich diagnosis_id na podstawie fk_appointment_id
            placeholders = ', '.join(['?'] * len(appointment_ids))
            query_diagnoses = f"""
                SELECT prescription_id FROM prescriptions WHERE fk_appointment_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_diagnoses, appointment_ids)
            diagnosis_ids = [row["prescription_id"] for row in cursor.fetchall()]

            print(f"################# Przypisane recepty: {diagnosis_ids}")

            return diagnosis_ids  # Teraz zwraca tylko listę diagnosis_id

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except TypeError as te:
            print(f"[### PATIENTS_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def get_all_prescription_ids(self):
        """
        Pobiera wszystkie prescription_id z tabeli prescriptions.

        :return: Lista prescription_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich prescription_id z tabeli prescriptions
            query = "SELECT prescription_id FROM prescriptions"
            cursor = self.patients_service_controller.db_controller.connection.execute(query)
            prescription_ids = [row["prescription_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych prescription_id
            print(f"[### PATIENTS_SERVICE] Pobranie prescription_id z prescriptions: {prescription_ids}")

            return prescription_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []



    def get_appointment_id_by_user_id(self):
        """
        Pobiera wszystkie prescription_id przypisane do employee_id,
        dla pracowników posiadających role_id = 3.

        :return: Lista prescription_id przypisanych do pracowników z role_id = 3.
        """
        try:
            # **1. Pobranie wszystkich employee_id dla użytkowników z role_id = 3**
            query_employees = """
                SELECT employee_id FROM users_accounts WHERE role_id = 3
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_employees)
            employee_ids = [row["employee_id"] for row in cursor.fetchall()]

            if not employee_ids:
                print("[### PATIENTS_SERVICE] Brak pracowników z role_id = 3.")
                return []

            # **2. Pobranie wszystkich assignment_id dla tych employee_id**
            placeholders = ', '.join(['?'] * len(employee_ids))
            query_assignments = f"""
                SELECT assignment_id FROM assigned_patients WHERE fk_employee_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_assignments, employee_ids)
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            if not assignment_ids:
                print("[### PATIENTS_SERVICE] Brak przypisanych assignment_id dla pracowników z role_id = 3.")
                return []

            # **3. Pobranie wszystkich appointment_id na podstawie assignment_id**
            placeholders = ', '.join(['?'] * len(assignment_ids))
            query_appointments = f"""
                SELECT appointment_id FROM appointments WHERE fk_assignment_id IN ({placeholders})
            """
            cursor = self.patients_service_controller.db_controller.connection.execute(query_appointments, assignment_ids)
            appointment_ids = [row["appointment_id"] for row in cursor.fetchall()]

            if not appointment_ids:
                print("[### PATIENTS_SERVICE] Brak przypisanych appointment_id dla pracowników z role_id = 3.")
                return []

            print(f"################# Przypisane wizyty dla pracowników z role_id = 3: {appointment_ids}")

            return appointment_ids  # Zwraca tylko listę prescription_id

        except sqlite3.OperationalError as op_err:
            print(f"[### PATIENTS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### PATIENTS_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except TypeError as te:
            print(f"[### PATIENTS_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def get_prescription_by_id(self, prescription_id):
        """
        Pobiera wszystkie kolumny rekordu z tabeli prescriptions na podstawie prescription_id.

        :param prescription_id: ID recepty do pobrania.
        :return: Słownik zawierający dane recepty lub None, jeśli nie znaleziono.
        """
        try:
            # Pobranie wszystkich danych recepty na podstawie prescription_id
            query = """
                SELECT * FROM prescriptions WHERE prescription_id = ?
            """
            cursor =  self.patients_service_controller.db_controller.connection.execute(query, (prescription_id,))
            prescription = cursor.fetchone()

            if prescription is None:
                print(f"[### PRESCRIPTIONS_SERVICE] Recepta o ID {prescription_id} nie istnieje.")
                return None

            # Konwersja wyniku na słownik
            column_names = [description[0] for description in cursor.description]
            prescription_data = dict(zip(column_names, prescription))

            print(f"[### PRESCRIPTIONS_SERVICE] Pobranie danych recepty: {prescription_data}")
            return prescription_data

        except sqlite3.OperationalError as op_err:
            print(f"[### PRESCRIPTIONS_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return None
        except sqlite3.DatabaseError as db_err:
            print(f"[### PRESCRIPTIONS_SERVICE] Błąd bazy danych: {db_err}")
            return None
