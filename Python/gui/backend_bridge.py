
import sqlite3
import re
from PySide6.QtCore import QObject, Signal, Slot, Property # pylint: disable=E0611
from services.dashboard_service import DashboardService
from services.patients_service import PatientsService
from controllers.users_accounts_controller import UsersAccountsController
from controllers.patients_controller import PatientController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.diagnoses_controller import DiagnosesController
from controllers.prescriptions_controller import PrescriptionsController

class BackendBridge(QObject):
    loginSuccess = Signal(str, str) 
    loginFailure = Signal(str)    
    modeChanged = Signal(bool)    
    formattedUsernameChanged = Signal() 
    userRoleChanged = Signal(str)
    specialtiesChanged = Signal(str)
    dateChanged = Signal(str) 
    dayNameChanged = Signal(str)  
    todaysAppointmentsChanged = Signal(str)
    upcomingAppointmentsChanged = Signal(str)
    meetingsChanged = Signal(str)
    patientsListChanged = Signal(list)
    medicalDataFetched = Signal(dict)  
    prescriptionsDataFetched = Signal(dict)
    appointmentsCountForUserChanged = Signal(int)
    userIdAsIntChanged = Signal(str)
    patientUpdatedSuccessfully = Signal()
    patientDeletedSuccessfully = Signal()
    employeeIdFetched = Signal(str)
    userRoleIdChanged = Signal(str)
    patientAddedSuccessfully = Signal()
    patientAdditionFailed = Signal(str)  
    prescriptionsErrorOccurred = Signal(str)  
    accessGranted = Signal()
    accessDenied = Signal(str)
    diagnosisAdditionFailed = Signal(str)
    diagnosisAddedSuccessfully = Signal()
    diagnosisUpdatedSuccessfully = Signal()
    diagnosisUpdateFailed = Signal(str)
    diagnosisDeletedSuccessfully = Signal()
    diagnosisDeletionFailed = Signal(str)
    prescriptionAddedSuccessfully = Signal()
    prescriptionAdditionFailed = Signal(str)
    prescriptionUpdatedSuccessfully = Signal()
    prescriptionUpdateFailed = Signal(str)
    prescriptionsAccessGranted = Signal()
    prescriptionDeletionFailed = Signal(str)
    prescriptionDeletedSuccessfully = Signal()



    def __init__(self, main_controller):
        try:
            super().__init__()
            print("BackendBridge initialized")  # Debugging
            self.main_controller = main_controller
            self.bridge_employee = None  # Atrybut dla bridge_employee
            self.bridge_room = None
            self.bridge_admin = None
            self._is_dark_mode = False
            self._current_screen = ""
            self._formatted_username = ""
            self._logged_in_user_id = None  
            self._user_role = "Nieznana rola"
            self._specialties = "Brak specjalizacji"
            self._current_date = ""
            self._current_day_name = "Nieznany dzień"  
            self._todays_appointments = "Nieznana liczba dni"
            self._upcoming_appointments = "Brak danych"
            self._meetings = "Brak danych"
            self._patients_list = [] 
            self._medical_data = {}  
            self._prescriptions_data = {} 
            self._appointmentsCountForUser = 0
            self._user_role_as_int = 0
            self._employee_id = None  # Przechowuje ID pracownika
        except AttributeError as e:
            print(f"Błąd w __init__: {str(e)} - problem z atrybutami")
        except TypeError as e:
            print(f"Błąd w __init__: {str(e)} - problem z typami danych")


 # -------------------------------------------------------------------------

    # Getter
    def get_current_screen(self):
        return self._current_screen

    # Setter
    def set_current_screen(self, value):
        if self._current_screen != value:
            self._current_screen = value
            self.currentScreenChanged.emit(value)

    currentScreenChanged = Signal(str)
    currentScreen = Property(str, get_current_screen, set_current_screen, notify=currentScreenChanged)

 # -------------------------------------------------------------------------

    def get_is_dark_mode(self):
        """
        Getter dla właściwości `isDarkMode`.
        """
        return self._is_dark_mode
    
    def set_is_dark_mode(self, value):
        """
        Setter dla właściwości `isDarkMode`.
        """
        if self._is_dark_mode != value:
            self._is_dark_mode = value
            print(f"Dark mode changed: {self._is_dark_mode}")
            print(f"Sygnał modeChanged emitowany: {self._is_dark_mode}")  # Debug
            self.modeChanged.emit(self._is_dark_mode)  # Emitowanie sygnału zmiany trybu

    isDarkMode = Property(bool, get_is_dark_mode, set_is_dark_mode, notify=modeChanged)

 # -------------------------------------------------------------------------

    @Slot(result=str)
    def get_formatted_username(self):
        """
        Pobiera sformatowaną nazwę aktualnie zalogowanego użytkownika.
        """
        try:
            # Sprawdzamy, czy użytkownik jest zalogowany
            if self._logged_in_user_id is None:
                return "Brak zalogowanego użytkownika"

            # Inicjalizacja DashboardService
            dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)




            # Pobieranie i formatowanie nazwy użytkownika
            formatted_username = dashboard_service.fetch_and_format_username(self._logged_in_user_id)
            return formatted_username if formatted_username else "Nieznany użytkownik"

        except ValueError as ve:
            print(f"Błąd danych wejściowych: {ve}")
            return "Błąd danych wejściowych"
        except KeyError as ke:
            print(f"Błąd podczas dostępu do danych: {ke}")
            return "Błąd danych"
        except AttributeError as ae:
            print(f"Błąd atrybutów: {ae}")
            return "Błąd w aplikacji"
        except RuntimeError as rue:
            print(f"Ogólny błąd systemowy: {rue}")
            return "Błąd systemowy"
        
    @Property(str, notify=formattedUsernameChanged)
    def formattedUsername(self):
        """
        Zwraca sformatowaną nazwę użytkownika.
        """
        return self._formatted_username

    @Slot()
    def updateFormattedUsername(self):
        """
        Aktualizuje wartość sformatowanej nazwy użytkownika.
        """
        try:
            if self._logged_in_user_id is not None:
                # Inicjalizacja DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)



                
                # Pobranie i formatowanie nazwy użytkownika
                formatted_username = dashboard_service.fetch_and_format_username(self._logged_in_user_id)
                self._formatted_username = formatted_username or "Nieznany użytkownik"
                
                # Emitowanie sygnału
                self.formattedUsernameChanged.emit()
            else:
                print("Brak zalogowanego użytkownika.")
        except ValueError as ve:
            print(f"Błąd danych użytkownika: {ve}")
        except AttributeError as ae:
            print(f"Błąd atrybutów: {ae}")
        except RuntimeError as rue:
            print(f"Błąd w logice aplikacji: {rue}")


 # -------------------------------------------------------------------------

    @Slot()
    def updateUserRole(self):
        """
        Aktualizuje rolę użytkownika i emituje sygnał zmiany do frontendu.
        """
        try:
            if self._logged_in_user_id is not None:
                # Inicjalizacja DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)


                
                # Pobranie nazwy roli użytkownika
                user_role = dashboard_service.fetch_user_role_name(self._logged_in_user_id)
                
                # Aktualizacja roli i emitowanie sygnału
                self._user_role = user_role or "Nieznana rola"
                self.userRoleChanged.emit(self._user_role)
            else:
                print("Brak zalogowanego użytkownika.")
        except ValueError as ve:
            print(f"Błąd danych wejściowych podczas aktualizacji roli użytkownika: {ve}")
        except KeyError as ke:
            print(f"Błąd klucza podczas aktualizacji roli użytkownika: {ke}")


    @Property(str, notify=userRoleChanged)
    def userRole(self):
        """
        Zwraca aktualną rolę użytkownika.
        """
        return self._user_role

 # -------------------------------------------------------------------------

    @Slot()
    def updateSpecialties(self):
        """
        Aktualizuje listę specjalizacji przypisanych do zalogowanego użytkownika
        i emituje sygnał jako pojedynczy tekst do frontendu.
        """
        try:
            if self._logged_in_user_id is not None:
                # print(f"bridge updateSpecialties: Zalogowany użytkownik o ID {self._logged_in_user_id}")
                # Inicjalizacja DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)

                
                # Pobranie listy specjalizacji użytkownika
                specialties = dashboard_service.get_specialties_for_logged_in_user(self._logged_in_user_id)
                # print(f"bridge updateSpecialties: Pobrane specjalizacje: {specialties}")

                if specialties:
                    
                    specialties_text = "<br>".join(specialties)  # Zmieniamy \n na <br>
                    # print(f"bridge updateSpecialties: Tekst specjalizacji: {specialties_text}")
                    self._specialties = specialties_text  # Aktualizacja wewnętrznego stanu

                else:
                    # Brak specjalizacji - ustawienie wartości domyślnej
                    self._specialties = "Brak specjalizacji"
                    # print("bridge updateSpecialties: Brak przypisanych specjalizacji.")    

                    self.specialtiesChanged.emit(self._specialties)

                    # Emitowanie sygnału
                    # self.specialtiesChanged.emit(specialties_text)
                    # print("bridge updateSpecialties: Sygnał specialtiesChanged został wyemitowany.")

            else:
                print("updateSpecialties: Brak zalogowanego użytkownika.")
        except AttributeError as ae:
            print(f"updateSpecialties: Błąd atrybutów: {ae}")  # np. brak metody lub atrybutu
        except TypeError as te:
            print(f"updateSpecialties: Nieprawidłowy typ danych: {te}")  # np. dane nie są listą
        except ValueError as ve:
            print(f"updateSpecialties: Błąd wartości danych: {ve}")  # np. dane mają niewłaściwą wartość
        except KeyError as ke:
            print(f"updateSpecialties: Błąd klucza: {ke}")  # np. brak wymaganego klucza w danych

    @Property(str, notify=specialtiesChanged)
    def specialties(self):
        """
        Zwraca aktualną listę specjalizacji jako ciąg tekstowy.
        """
        return self._specialties

 # -------------------------------------------------------------------------

    @Slot()
    def updateCurrentDate(self):
        """
        Pobiera aktualną datę z dashboard_service i emituje ją do frontendu.
        """
        try:
            # print("bridge: updateCurrentDate: Rozpoczynam pobieranie daty z dashboard_service...")
            dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)

            self._current_date = dashboard_service.get_date_with_offset()  # Pobranie dzisiejszej daty

            # Debugowanie - sprawdzenie, czy data została poprawnie pobrana
            # print(f"bridge: updateCurrentDate: Pobrana data = {self._current_date}")

            # Emitowanie sygnału do frontend
            self.dateChanged.emit(self._current_date)
            # print("bridge: updateCurrentDate: Sygnał dateChanged został wyemitowany do frontendu")

        except AttributeError as ae:
            print(f"updateCurrentDate: Błąd atrybutów: {ae}")  # np. brak metody w obiekcie
        except TypeError as te:
            print(f"updateCurrentDate: Nieprawidłowy typ danych: {te}")  # np. zwrócone dane są błędnego typu
        except ValueError as ve:
            print(f"updateCurrentDate: Błąd danych wejściowych: {ve}")  # np. dane mają niewłaściwą wartość
        except KeyError as ke:
            print(f"updateCurrentDate: Błąd klucza w danych: {ke}")  # np. brak klucza w danych


    @Property(str, notify=dateChanged)
    def currentDate(self):
        """
        Udostępnia aktualną datę dla QML.
        """
        return self._current_date

 # -------------------------------------------------------------------------

    @Slot()
    def updateCurrentDayName(self):
        """
        Aktualizuje nazwę aktualnego dnia tygodnia z dashboard_service i emituje ją do frontendu.
        """
        try:
            # print("bridge: updateCurrentDayName: Rozpoczynam aktualizację dnia tygodnia...")
            dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)


            # Pobranie aktualnej nazwy dnia tygodnia
            day_name = dashboard_service.get_current_day_name()
            self._current_day_name = day_name

            # Debugowanie
            # print(f"bridge: updateCurrentDayName: Aktualna nazwa dnia tygodnia to: {day_name}")

            # Emitowanie sygnału do QML
            self.dayNameChanged.emit(self._current_day_name)
            # print("bridge: updateCurrentDayName: Sygnał dayNameChanged został wyemitowany.")

        except AttributeError as ae:
            print(f"updateCurrentDayName: Błąd atrybutu lub metody: {ae}")
            self._current_day_name = "Nieznany dzień"  # Wartość domyślna
            
        except ValueError as ve:
            print(f"updateCurrentDayName: Błąd danych: {ve}")
            self._current_day_name = "Nieznany dzień"  # Wartość domyślna

        except KeyError as ke:
            print(f"updateCurrentDayName: Błąd klucza: {ke}")
            self._current_day_name = "Nieznany dzień"  # Wartość domyślna

    @Property(str, notify=dayNameChanged)
    def currentDayName(self):
        """
        Udostępnia nazwę aktualnego dnia tygodnia do QML.
        """
        return self._current_day_name

 # -------------------------------------------------------------------------

    @Slot()
    def updateTodaysAppointments(self):
        """
        Aktualizuje liczbę dzisiejszych wizyt przypisanych do zalogowanego użytkownika
        i emituje sygnał do frontendu.
        """
        try:
            if self._logged_in_user_id is not None:
                # Inicjalizacja DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)

                # Pobranie liczby dzisiejszych wizyt dla użytkownika
                todays_appointments = dashboard_service.get_todays_appointments_by_employee_id(self._logged_in_user_id)

                # Konwersja do liczby całkowitej, jeśli zwrócone zostało więcej niż 0 wizyt
                self._todays_appointments = str(len(todays_appointments))

                # Emitowanie sygnału do frontendu
                self.todaysAppointmentsChanged.emit(self._todays_appointments)
            else:
                print("updateTodaysAppointments: Brak zalogowanego użytkownika.")
                self._todays_appointments = "0"
                self.todaysAppointmentsChanged.emit(self._todays_appointments)

        except KeyError as ke:
            print(f"updateTodaysAppointments: Błąd klucza w danych: {ke}")
            self._todays_appointments = "0"
            self.todaysAppointmentsChanged.emit(self._todays_appointments)

        except ValueError as ve:
            print(f"updateTodaysAppointments: Nieprawidłowe dane wejściowe: {ve}")
            self._todays_appointments = "0"
            self.todaysAppointmentsChanged.emit(self._todays_appointments)

    @Property(str, notify=todaysAppointmentsChanged)
    def todaysAppointments(self):
        return self._todays_appointments


 # -------------------------------------------------------------------------

    @Slot()
    def updateAppointmentsCountForUser(self):
        """
        Aktualizuje liczbę wizyt przypisanych do zalogowanego użytkownika
        (z wykorzystaniem metody get_appointment_count_by_employee_id w DashboardService)
        i emituje sygnał do frontendu.
        """
        try:
            if self._logged_in_user_id is not None:
                # Inicjalizacja DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)

                # Pobranie liczby wizyt dla użytkownika (pracownika)
                appointment_count_text = dashboard_service.get_appointment_count_by_employee_id(self._logged_in_user_id)

                # Debugowanie
                # print(f"[DEBUG] Liczba wizyt dla user_id {self._logged_in_user_id}: {appointment_count_text}")

                # Konwersja na liczbę całkowitą
                self._appointmentsCountForUser = int(appointment_count_text.split(":")[-1].strip())

                # Emitowanie sygnału do frontendu
                self.appointmentsCountForUserChanged.emit(self._appointmentsCountForUser)
            else:
                print("[DEBUG] updateAppointmentsCountForUser: Brak zalogowanego użytkownika.")
                self._appointmentsCountForUser = 0
                self.appointmentsCountForUserChanged.emit(self._appointmentsCountForUser)

        except KeyError as ke:
            print(f"[ERROR] updateAppointmentsCountForUser: Błąd - brak wymaganego klucza w danych: {ke}")
            self._appointmentsCountForUser = 0
            self.appointmentsCountForUserChanged.emit(self._appointmentsCountForUser)
        except ValueError as ve:
            print(f"[ERROR] updateAppointmentsCountForUser: Nieprawidłowe dane wejściowe: {ve}")
            self._appointmentsCountForUser = 0
            self.appointmentsCountForUserChanged.emit(self._appointmentsCountForUser)



    @Property(int, notify=appointmentsCountForUserChanged)
    def appointmentsCountForUser(self):
        """
        Zwraca liczbę wizyt (jako int) przypisanych do zalogowanego użytkownika.
        """
        return self._appointmentsCountForUser




 # -------------------------------------------------------------------------

    @Slot()
    def updateUpcomingAppointments(self):
        """
        Aktualizuje listę nadchodzących wizyt dla zalogowanego użytkownika
        i emituje sygnał jako pojedynczy tekst do frontend.
        """
        try:
            if self._logged_in_user_id is not None:
                # Utworzenie instancji DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)

                # Pobranie szczegółowych informacji o wizytach dla zalogowanego użytkownika
                upcoming_appointments = dashboard_service.get_patient_appointments_with_rooms(self._logged_in_user_id)
                if upcoming_appointments:
                    # Formatowanie danych do czytelnego ciągu tekstowego
                    formatted_appointments = []
                    for appointment in upcoming_appointments:
                        appointment_date = appointment.get("appointment_date", "Nieznana data")
                        patient_name = appointment.get("patient_name", "Nieznany pacjent")
                        room_number = appointment.get("room_number", "Brak numeru pokoju")
                        formatted_appointments.append(f"{appointment_date} - Pokój: {room_number} - {patient_name}")

                    # Połączenie wszystkich wizyt w jeden ciąg tekstowy
                    self._upcoming_appointments = "<br>".join(formatted_appointments)
                else:
                    # Gdy brak wizyt
                    self._upcoming_appointments = "Brak nadchodzących wizyt."

                # Emitowanie zmiany do frontendu
                self.upcomingAppointmentsChanged.emit(self._upcoming_appointments)
            else:
                print("updateUpcomingAppointments: Brak zalogowanego użytkownika.")  # Debug
        except ValueError as ve:
            print(f"updateUpcomingAppointments: Błąd danych wejściowych: {ve}")  # Debugowanie
        except KeyError as ke:
            print(f"updateUpcomingAppointments: Błąd klucza podczas przetwarzania wizyt: {ke}")  # Debugowanie
        except AttributeError as ae:
            print(f"updateUpcomingAppointments: Błąd atrybutów (np. kontrolery): {ae}")  # Debugowanie


    @Property(str, notify=upcomingAppointmentsChanged)
    def upcomingAppointments(self):
        """
        Udostępnia listę najbliższych wizyt w formacie string.
        """
        return self._upcoming_appointments

 # -------------------------------------------------------------------------

    @Slot()
    def updateMeetings(self):
        """
        Aktualizuje listę spotkań przypisanych do zalogowanego użytkownika
        i emituje sygnał jako pojedynczy tekst do frontend.
        """
        try:
            if self._logged_in_user_id is not None:
                # Utworzenie instancji DashboardService
                dashboard_service = DashboardService(self.main_controller, self.main_controller.db_controller)

                # Pobranie szczegółów spotkań dla zalogowanego użytkownika
                meetings = dashboard_service.get_meeting_details_by_employee_id(self._logged_in_user_id)
                if meetings:
                    # Formatowanie danych do czytelnego ciągu tekstowego
                    formatted_meetings = []
                    for meeting in meetings:
                        meeting_date = meeting.get("meeting_date", "Nieznana data")
                        meeting_type = meeting.get("meeting_type", "Nieznany typ spotkania")
                        room_number = meeting.get("room_number", "Brak numeru pokoju")
                        formatted_meetings.append(f"{meeting_date} - Pokój: {room_number} - {meeting_type}")

                    # Połączenie wszystkich spotkań w jeden ciąg tekstowy
                    self._meetings = "<br>".join(formatted_meetings)
                else:
                    # Gdy brak spotkań
                    self._meetings = "Brak spotkań."

                # Emitowanie zmiany do frontendu
                self.meetingsChanged.emit(self._meetings)
            else:
                print("updateMeetings: Brak zalogowanego użytkownika.")
        except ValueError as ve:
            print(f"updateMeetings: Błąd danych wejściowych: {ve}")
        except KeyError as ke:
            print(f"updateMeetings: Błąd klucza: {ke}")
        except AttributeError as ae:
            print(f"updateMeetings: Błąd atrybutów: {ae}")

            
    @Property(str, notify=meetingsChanged)
    def meetings(self):
        return self._meetings


 # -------------------------------------------------------------------------
 
    @Slot()
    def updateUserRoleId(self):
        """
        Aktualizuje rolę użytkownika (jako int) na podstawie self._logged_in_user_id,
        wywołując metodę get_role_id_by_user_id z UsersAccountsController.
        Emituje sygnał z tą wartością do frontend jako string.
        """
        try:
            if self._logged_in_user_id is not None:
                # Tworzymy instancję kontrolera
                users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)

                # Pobieramy role_id za pomocą kontrolera
                role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)

                if role_id is not None:
                    # Przechowujemy rolę użytkownika jako int
                    self._user_role_as_int = int(role_id)
                    # print(f"self._user_role_as_int {self._user_role_as_int}")

                    # Emitujemy sygnał z rolą jako string do frontend
                    self.userRoleIdChanged.emit(str(self._user_role_as_int))
                else:
                    print(f"updateUserRoleId: Nie znaleziono role_id dla user_id: {self._logged_in_user_id}")
            else:
                print("updateUserRoleId: Brak zalogowanego użytkownika.")
        except AttributeError as ae:
            print(f"updateUserRoleId: Błąd atrybutów: {ae}")




    @Property(str, notify=userRoleIdChanged)
    def userRoleId(self):
        """
        Zwraca rolę użytkownika jako string do QML.
        """
        return str(self._user_role_as_int) if self._user_role_as_int is not None else ""


 # -------------------------------------------------------------------------

    Slot()
    def fetchEmployeeId(self):
        """
        Pobiera ID pracownika na podstawie self._logged_in_user_id
        i emituje sygnał do frontendu jako string.
        """
        try:
            if self._logged_in_user_id is not None:
                users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                if employee_id is not None:
                    self._employee_id = employee_id
                    self.employeeIdFetched.emit(str(self._employee_id))  # Emitujemy jako string do QML
                else:
                    print("fetchEmployeeId: Brak przypisanego ID pracownika.")
            else:
                print("fetchEmployeeId: Brak zalogowanego użytkownika.")
        except ValueError as ve:
            print(f"fetchEmployeeId: Błąd danych wejściowych (ValueError): {ve}")
        except KeyError as ke:
            print(f"fetchEmployeeId: Błąd klucza: {ke}")
        except AttributeError as ae:
            print(f"fetchEmployeeId: Błąd atrybutów: {ae}")

    @Property(str, notify=employeeIdFetched)
    def employeeId(self):
        return str(self._employee_id)

 # -------------------------------------------------------------------------

    @Slot(str, str, result=str)
    def login(self, username, password):
        """
        Obsługuje logowanie użytkownika na podstawie nazwy użytkownika i hasła.
        """
        try:
            # Wywołanie logiki logowania z MainController
            user = self.main_controller.login_user(username, password)

            if user:
                # Sukces logowania
                self._logged_in_user_id = user['user_id']  # Ustawiamy ID zalogowanego użytkownika

                if self.bridge_employee is not None:
                    self.bridge_employee.setLoggedInUserId(self._logged_in_user_id)
                
                if self.bridge_room is not None:
                    self.bridge_room.setLoggedInUserId(self._logged_in_user_id)

                try:
                    # Aktualizujemy sformatowaną nazwę użytkownika
                    self.updateFormattedUsername()

                    # Aktualizujemy rolę użytkownika
                    self.updateUserRole()

                    # Aktualizujemy specjalizacje użytkownika
                    self.updateSpecialties()
                    
                    # Aktualizujemy bieżącą datę dla użytkownika
                    self.updateCurrentDate()  
                    
                    self.updateCurrentDayName()

                    self.updateTodaysAppointments()

                    self.updateUpcomingAppointments()

                    self.updateMeetings()

                    self.updateAppointmentsCountForUser()

                    self.updateUserRoleId()

                    self.fetchEmployeeId()

                except KeyError as ke:
                    print(f"Błąd: Brak wymaganego klucza w danych użytkownika: {ke}")
                    self.loginFailure.emit(f"Błąd klucza danych: {ke}")
                    return f"error:Błąd klucza danych: {ke}"

                except ValueError as ve:
                    print(f"Błąd w danych użytkownika: {ve}")
                    self.loginFailure.emit(f"Błąd danych: {ve}")
                    return f"error:Błąd danych: {ve}"

                # Emitowanie sygnału sukcesu logowania z nazwą użytkownika, rolą i specjalizacjami
                self.loginSuccess.emit(user['username'], user.get('role_name', 'Nieznana rola'))
                return f"success:{user['username']}:{user.get('role_name', 'Nieznana rola')}"

            else:
                # Nieprawidłowe dane logowania
                self.loginFailure.emit("Nieprawidłowa nazwa użytkownika lub hasło.")
                return "error:Nieprawidłowa nazwa użytkownika lub hasło."

        except KeyError as ke:
            # Obsługa brakujących kluczy w słowniku
            self.loginFailure.emit(f"Błąd klucza: {str(ke)}")
            return f"error:Błąd klucza:{ke}"

        except ValueError as ve:
            # Obsługa błędów walidacji danych
            self.loginFailure.emit(f"Błąd walidacji: {str(ve)}")
            return f"error:Błąd walidacji:{ve}"


 # -------------------------------------------------------------------------

    @Slot()
    def updatePatientsList(self):
        """
        Pobiera listę pacjentów przypisanych do aktualnego użytkownika
        i emituje sygnał do QML.
        """
        if self._logged_in_user_id is not None:
            try:
                # Pobranie danych z serwisu pacjentów
                patients_service = PatientsService(self.main_controller)
                patients_list = patients_service.table_get_patients_for_user(self._logged_in_user_id)
                # Walidacja i ustawienie wartości domyślnych
                for patient in patients_list:
                    if 'patient_id' not in patient or patient['patient_id'] is None:
                        patient['patient_id'] = "Brak danych"
                    
                # print(f"lista pacjentów: {patients_list}")
                self._patients_list = patients_list
                
                # Emitowanie sygnału z listą pacjentów
                self.patientsListChanged.emit(self._patients_list)
            
            except KeyError as ke:
                print(f"[updatePatientsList] Klucz nie znaleziony w danych pacjenta: {ke}")
            except ValueError as ve:
                print(f"[updatePatientsList] Błąd w wartościach danych pacjenta: {ve}")
        else:
            print("[updatePatientsList] Brak zalogowanego użytkownika. Nie można pobrać listy pacjentów.")



    @Slot(result=list)
    def getPatientsList(self):
        """
        Zwraca listę pacjentów.
        """
        return self._patients_list


 # -------------------------------------------------------------------------


    @Slot()
    def updateDiagnosesDataForUserList(self):
        """
        Pobiera dane medyczne dla użytkownika i emituje wynik do QML.
        """
        if self._logged_in_user_id is not None:
            try:
                # Inicjalizacja serwisu danych medycznych
                patients_service = PatientsService(self.main_controller)

                # Pobranie danych medycznych dla podanego użytkownika
                diagnoses_data = patients_service.table_get_diagnoses_data(self._logged_in_user_id)

                # Debugowanie: Logowanie pobranych danych
                # print(f"[BackendBridge] Pobranie danych medycznych dla user_id={self._logged_in_user_id}: {diagnoses_data}")

                # Emitowanie danych do QML
                self.medicalDataFetched.emit({"records": diagnoses_data})

            except Exception as e:
                print(f"[BackendBridge] Błąd podczas pobierania danych medycznych dla user_id={self._logged_in_user_id}: {e}")
                raise RuntimeError(f"Błąd podczas pobierania danych medycznych: {e}") from e
        else:
            print("[BackendBridge] Nie można pobrać danych medycznych. user_id jest None.")



    @Slot(result=dict)
    def getDiagnosesData(self):
        """
        Zwraca dane medyczne przechowywane w atrybucie instancji.
        
        Returns:
            dict: Dane medyczne.
        """
        return self._medical_data  # Spójne z innymi metodami


 # -------------------------------------------------------------------------

    @Slot()
    def updatePrescriptionsDataForUser(self):
        """
        Pobiera dane recept dla użytkownika i emituje wynik do QML.
        """
        if self._logged_in_user_id is not None:
            try:
                # Pobranie roli użytkownika
                users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
                role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)

                # Warunek: Użytkownik z rolą 4-8 nie ma dostępu**
                if role_id in [4, 5, 6, 7, 8]:
                    print(f"[BackendBridge] Użytkownik {self._logged_in_user_id} (role_id={role_id}) nie ma uprawnień do przeglądania recept.")
                    
                    # **Emitowanie komunikatu błędu nowym sygnałem**
                    self.prescriptionsErrorOccurred.emit("Brak uprawnień do przeglądania recept.")
                    return  # **Zakończ metodę bez dalszego przetwarzania**

                
                patients_service = PatientsService(self.main_controller)

                prescriptions_data = patients_service.table_get_prescriptions_data(self._logged_in_user_id)

                # Debugowanie
                # print(f"[BackendBridge] Pobranie danych recept dla user_id={self._logged_in_user_id}: {prescriptions_data}")

                # Emitowanie poprawnych danych do QML
                self.prescriptionsDataFetched.emit({"records": prescriptions_data})

            except ValueError as ve:
                print(f"[BackendBridge] Błąd danych wejściowych podczas pobierania recept: {ve}")
                self.prescriptionsErrorOccurred.emit("Błąd danych wejściowych.")

            except KeyError as ke:
                print(f"[BackendBridge] Błąd klucza podczas przetwarzania danych recept: {ke}")
                self.prescriptionsErrorOccurred.emit("Błąd przetwarzania danych.")

            except AttributeError as ae:
                print(f"[BackendBridge] Błąd atrybutu (np. brak metody lub kontrolera): {ae}")
                self.prescriptionsErrorOccurred.emit("Błąd systemowy - brak kontrolera.")

        else:
            print("[BackendBridge] Nie można pobrać danych recept. user_id jest None.")
            self.prescriptionsErrorOccurred.emit("Nie zalogowano użytkownika.")



    @Slot(result=dict)
    def getPrescriptionsData(self):
        """
        Zwraca dane recept przechowywane w atrybucie instancji.

        Returns:
            dict: Dane recept, gdzie wartość pod kluczem "records" to lista rekordów.
        """
        return self._prescriptions_data  # Spójne z innymi metodami


 # -------------------------------------------------------------------------

    @Slot(str, str, str, str, str, str, str)
    def addNewPatient(self, first_name, last_name, pesel, phone, email, address, birth):
        """
        Dodaje nowego pacjenta, przyjmując dane z QML (insert_employee_id + dane pacjenta).
        W zależności od roli zalogowanego użytkownika:
        - jeżeli role_id in [1, 2, 9, 10]:
            sprawdza, czy insert_employee_id istnieje w bazie i ma is_active=1, a potem przypisuje.
        - jeżeli role_id in [3, 4, 5, 6, 7, 8]:
            pobiera employee_id zalogowanego użytkownika i porównuje z insert_employee_id,
            jeśli się zgadza -> przypisuje, w przeciwnym razie błąd.
        """

        if self._logged_in_user_id is not None:
            try:
                users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
                role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
                print(f"[BackendBridge_addNewPatient] Rola zalogowanego usera (role_id): {role_id}")

                # Inicjalizacja do weryfikacji personelu i przypisywania pacjenta
                patients_controller = PatientController(self.main_controller.db_controller) 

                errors = []

                # 3. Pobranie istniejących wartości pesel, phone, email
                existing_data = patients_controller.get_all_pesel_phone_email()
                existing_pesels = {patient["pesel"] for patient in existing_data}
                existing_phones = {patient["phone"] for patient in existing_data}
                existing_emails = {patient["email"] for patient in existing_data}

                # 4. Sprawdzenie, czy pesel, phone lub email istnieją już w bazie
                if pesel in existing_pesels:
                    errors.append(f"Numer PESEL ({pesel}) już istnieje w bazie.")

                if phone in existing_phones:
                    errors.append(f"Numer telefonu ({phone}) już istnieje w bazie.")

                if email in existing_emails:
                    errors.append(f"Adres email ({email}) już istnieje w bazie.")

                # Jeśli są jakieś błędy, wyemituj sygnał z listą błędów
                if errors:
                    error_message = "\n".join(errors)
                    print(f"[BackendBridge_addNewPatient] Błędy walidacji: {error_message}")
                    self.patientAdditionFailed.emit(error_message)
                    return
                
                # 3. Dodanie pacjenta
                patients_controller.add_new_patient(
                    first_name,
                    last_name,
                    pesel,
                    phone,
                    email,
                    address,
                    birth,
                    is_active=1
                )
                # print("[BackendBridge_addNewPatient] Pacjent został dodany i przypisany (role_id w [1,2,9,10]).")
                self.patientAddedSuccessfully.emit()

            except ValueError as ve:
                self.patientAdditionFailed.emit(f"Błąd danych wejściowych: {ve}")
            except KeyError as ke:
                self.patientAdditionFailed.emit(f"Błąd klucza w danych: {ke}")
            except RuntimeError as rue:
                self.patientAdditionFailed.emit(f"Błąd wykonania: {rue}")
            except sqlite3.Error as db_error:
                self.patientAdditionFailed.emit(f"Błąd bazy danych: {db_error}")

        else:
            msg = "Nie można dodać pacjenta. user_id jest None."
            print("[BackendBridge_addNewPatient] " + msg)
            self.patientAdditionFailed.emit(msg)


 # -------------------------------------------------------------------------

    @Slot(int, str, str, str, str, str, str, str, str)
    def updatePatient(self,
                    patient_id: int,
                    first_name: str = "",
                    last_name: str = "",
                    pesel: str = "",
                    phone: str = "",
                    email: str = "",
                    address: str = "",
                    birth: str = "",
                    insert_is_active: str = ""):
        """
        Aktualizuje dane pacjenta, przyjmując jako argumenty dane z pól tekstowych w QML.
        Sprawdza również, czy podany patient_id istnieje w bazie oraz czy wprowadzone dane są unikalne.
        """
        print("[BackendBridge_updatePatient] Odebrano dane pacjenta:")
        print(f"  Id pacjenta: {patient_id}")
        print(f"  Imię: {first_name}")
        print(f"  Nazwisko: {last_name}")
        print(f"  PESEL: {pesel}")
        print(f"  Telefon: {phone}")
        print(f"  Email: {email}")
        print(f"  Adres: {address}")
        print(f"  Data urodzenia: {birth}")
        print(f"  Czy aktywny: {insert_is_active}")

        if self._logged_in_user_id is not None:
            try:
                # Inicjalizacja kontrolerów
                users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
                patients_controller = PatientController(self.main_controller.db_controller)
                assigned_patients_controller = AssignedPatientsController(self.main_controller.db_controller)


                # Pobranie roli użytkownika
                role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
                print(f"[BackendBridge_updatePatient] Rola zalogowanego użytkownika (role_id): {role_id}")

                if role_id in [1, 2, 9, 10]:
                    # Pobranie wszystkich patient_id z bazy danych
                    all_patient_ids = patients_controller.get_all_patient_ids()
                    
                    # Sprawdzenie, czy podany patient_id istnieje
                    if patient_id not in all_patient_ids:
                        msg = f"Pacjent o Id ({patient_id}) nie istnieje w bazie."
                        print("[BackendBridge_updatePatient] " + msg)
                        self.patientAdditionFailed.emit(msg)
                        return

                    # Pobranie szczegółowych danych pacjenta
                    patient_data = patients_controller.get_patient_by_id(patient_id)

                    if not patient_data:
                        msg = f"Błąd podczas pobierania szczegółów pacjenta o Id ({patient_id})."
                        print("[BackendBridge_updatePatient] " + msg)
                        self.patientAdditionFailed.emit(msg)
                        return

                    # Lista do przechowywania błędów
                    errors = []

                    # 3. Pobranie istniejących wartości pesel, phone, email
                    existing_data = patients_controller.get_all_pesel_phone_email()
                    existing_pesels = {patient["pesel"] for patient in existing_data}
                    existing_phones = {patient["phone"] for patient in existing_data}
                    existing_emails = {patient["email"] for patient in existing_data}

                    # 4. Sprawdzenie, czy pesel, phone lub email istnieją już w bazie
                    if pesel in existing_pesels:
                        errors.append(f"Numer PESEL ({pesel}) już istnieje w bazie.")
                    if phone in existing_phones:
                        errors.append(f"Numer telefonu ({phone}) już istnieje w bazie.")
                    if email in existing_emails:
                        errors.append(f"Adres email ({email}) już istnieje w bazie.")

                    # Jeśli są jakieś błędy, wyemituj sygnał z listą błędów
                    if errors:
                        error_message = "\n".join(errors)
                        print(f"[BackendBridge_addNewPatient] Błędy walidacji: {error_message}")
                        self.patientAdditionFailed.emit(error_message)
                        return

                                # Normalizacja wartości is_active (pole opcjonalne)
                    is_active = None
                    if insert_is_active:
                        normalized_is_active = insert_is_active.strip().lower()
                        if normalized_is_active == "tak":
                            is_active = 1
                        elif normalized_is_active == "nie":
                            is_active = 0
                        else:
                            self.patientAdditionFailed.emit("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")
                            return

                    # Budowanie słownika `data_to_update` tylko dla wartości, które są różne od tych w bazie
                    data_to_update = {}
                    if first_name and first_name != patient_data["first_name"]:
                        data_to_update["first_name"] = first_name
                    if last_name and last_name != patient_data["last_name"]:
                        data_to_update["last_name"] = last_name
                    if pesel and pesel != patient_data["pesel"]:
                        data_to_update["pesel"] = pesel
                    if phone and phone != patient_data["phone"]:
                        data_to_update["phone"] = phone
                    if email and email != patient_data["email"]:
                        data_to_update["email"] = email
                    if address and address != patient_data["address"]:
                        data_to_update["address"] = address
                    if birth and birth != patient_data["date_of_birth"]:
                        data_to_update["date_of_birth"] = birth
                    if is_active is not None and is_active != patient_data.get("is_active"):
                        data_to_update["is_active"] = is_active 

                    # Jeśli użytkownik nie podał żadnych zmian, wyemituj błąd
                    if not data_to_update:
                        print("[BackendBridge_updatePatient] Brak zmian w danych pacjenta. Aktualizacja nie została wykonana.")
                        self.patientAdditionFailed.emit("Brak zmian w danych pacjenta.")
                        return

                    # Wywołanie metody aktualizacji pacjenta w kontrolerze
                    patients_controller.update_patient(patient_id, **data_to_update)
                    print("[BackendBridge_updatePatient] Pacjent został zaktualizowany w bazie danych.")
                    self.patientUpdatedSuccessfully.emit()

                elif role_id in [3, 4, 5, 6, 7, 8]:
                    # Pobranie wszystkich patient_id z bazy danych
                    all_patient_ids = patients_controller.get_all_patient_ids()
                    
                    # Sprawdzenie, czy podany patient_id istnieje
                    if patient_id not in all_patient_ids:
                        msg = f"Pacjent o Id ({patient_id}) nie istnieje w bazie."
                        print("[BackendBridge_updatePatient] " + msg)
                        self.patientAdditionFailed.emit(msg)
                        return

                    # Pobranie employee_id zalogowanego użytkownika
                    employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                    if not employee_id:
                        msg = f"Brak pracownika przypisanego do user_id ({self._logged_in_user_id})."
                        print("[BackendBridge_updatePatient] " + msg)
                        self.patientAdditionFailed.emit(msg)
                        return

                    # Pobranie wszystkich patient_id przypisanych do tego pracownika
                    assigned_patient_ids = [
                        item["fk_patient_id"] for item in assigned_patients_controller.get_assigned_patients_by_employee_id(employee_id)
                    ]

                    # Sprawdzenie, czy podany patient_id istnieje w przypisanych pacjentach
                    if patient_id not in assigned_patient_ids:
                        msg = (
                            f"Pacjent o Id ({patient_id}) nie jest przypisany do pracownika (employee_id={employee_id}).\n"
                            f"Identyfikatory przypisanych pacjentów: {', '.join(map(str, assigned_patient_ids))}"
                        )
                        print("[BackendBridge_updatePatient] " + msg)
                        self.patientAdditionFailed.emit(msg)
                        return

                    # Pobranie szczegółowych danych pacjenta
                    patient_data = patients_controller.get_patient_by_id(patient_id)

                    if not patient_data:
                        msg = f"Błąd podczas pobierania szczegółów pacjenta o Id ({patient_id})."
                        print("[BackendBridge_updatePatient] " + msg)
                        self.patientAdditionFailed.emit(msg)
                        return

                    # Lista do przechowywania błędów
                    errors = []

                    # 3. Pobranie istniejących wartości pesel, phone, email
                    existing_data = patients_controller.get_all_pesel_phone_email()
                    existing_pesels = {patient["pesel"] for patient in existing_data}
                    existing_phones = {patient["phone"] for patient in existing_data}
                    existing_emails = {patient["email"] for patient in existing_data}

                    # 4. Sprawdzenie, czy pesel, phone lub email istnieją już w bazie
                    if pesel in existing_pesels:
                        errors.append(f"Numer PESEL ({pesel}) już istnieje w bazie.")
                    if phone in existing_phones:
                        errors.append(f"Numer telefonu ({phone}) już istnieje w bazie.")
                    if email in existing_emails:
                        errors.append(f"Adres email ({email}) już istnieje w bazie.")

                    # Jeśli są jakieś błędy, wyemituj sygnał z listą błędów
                    if errors:
                        error_message = "\n".join(errors)
                        print(f"[BackendBridge_addNewPatient] Błędy walidacji: {error_message}")
                        self.patientAdditionFailed.emit(error_message)
                        return

                    # Normalizacja wartości is_active (pole opcjonalne)
                    is_active = None
                    if insert_is_active:
                        normalized_is_active = insert_is_active.strip().lower()
                        if normalized_is_active == "tak":
                            is_active = 1
                        elif normalized_is_active == "nie":
                            is_active = 0
                        else:
                            self.patientAdditionFailed.emit("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")
                            return

                    # Budowanie słownika `data_to_update` tylko dla wartości, które są różne od tych w bazie
                    data_to_update = {}
                    if first_name and first_name != patient_data["first_name"]:
                        data_to_update["first_name"] = first_name
                    if last_name and last_name != patient_data["last_name"]:
                        data_to_update["last_name"] = last_name
                    if pesel and pesel != patient_data["pesel"]:
                        data_to_update["pesel"] = pesel
                    if phone and phone != patient_data["phone"]:
                        data_to_update["phone"] = phone
                    if email and email != patient_data["email"]:
                        data_to_update["email"] = email
                    if address and address != patient_data["address"]:
                        data_to_update["address"] = address
                    if birth and birth != patient_data["date_of_birth"]:
                        data_to_update["date_of_birth"] = birth
                    if is_active is not None and is_active != patient_data.get("is_active"):
                        data_to_update["is_active"] = is_active          

                    # Jeśli użytkownik nie podał żadnych zmian, wyemituj błąd
                    if not data_to_update:
                        print("[BackendBridge_updatePatient] Brak zmian w danych pacjenta. Aktualizacja nie została wykonana.")
                        self.patientAdditionFailed.emit("Brak zmian w danych pacjenta.")
                        return

                    # Wywołanie metody aktualizacji pacjenta w kontrolerze
                    patients_controller.update_patient(patient_id, **data_to_update)
                    print("[BackendBridge_updatePatient] Pacjent został zaktualizowany w bazie danych.")
                    self.patientUpdatedSuccessfully.emit()

                else:
                    msg = f"Brak uprawnień do aktualizacji pacjenta dla roli role_id={role_id}."
                    print("[BackendBridge_updatePatient] " + msg)
                    self.patientAdditionFailed.emit(msg)

            except KeyError as ke:
                error_msg = f"[BackendBridge_updatePatient] Błąd klucza: {ke}"
                print(error_msg)
                self.patientAdditionFailed.emit(error_msg)

            except ValueError as ve:
                error_msg = f"[BackendBridge_updatePatient] Błąd wartości: {ve}"
                print(error_msg)
                self.patientAdditionFailed.emit(error_msg)

            except RuntimeError as rue:
                error_msg = f"[BackendBridge_updatePatient] Błąd systemu: {rue}"
                print(error_msg)
                self.patientAdditionFailed.emit(error_msg)
        else:
            msg = "Nie można zaktualizować pacjenta. user_id jest None."
            print("[BackendBridge_updatePatient] " + msg)
            self.patientAdditionFailed.emit(msg)



 # -------------------------------------------------------------------------


    @Slot(int)
    def deletePatient(self, insert_patient_id):
        """
        Usuwa pacjenta z systemu po zweryfikowaniu poprawności danych.

        :param insert_patient_id: ID pacjenta do usunięcia.
        """

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deletePatient] Brak zalogowanego użytkownika.")
            self.patientAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            patients_service = PatientsService(self.main_controller)
            patients_controller = PatientController(self.main_controller.db_controller)
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_deletePatient] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")



            # **Logika dla ról [1, 2, 9, 10]**
            if role_id in [1, 2, 9, 10]:

                # **Sprawdzenie, czy pacjent istnieje**
                all_patient_ids = patients_controller.get_all_patient_ids()
                if insert_patient_id not in all_patient_ids:
                    msg = f"Pacjent o ID ({insert_patient_id}) nie istnieje w bazie."
                    print(f"[BridgeRoom_deletePatient] {msg}")
                    self.patientAdditionFailed.emit(msg)
                    return
            
                assigned_patient_ids = patients_service.get_all_patient_id_assigned()
                if insert_patient_id in assigned_patient_ids:
                    msg = f"Nie można usunąć pacjenta o ID ({insert_patient_id}), ponieważ jest przypisany w tabeli przypisania pacjentów do pracowników."
                    print(f"[BridgeRoom_deletePatient] {msg}")
                    self.patientAdditionFailed.emit(msg)
                    return

            elif role_id in [3, 4, 5, 6, 7, 8]:

                msg = f"Usuwanie pacjenta nie jest przeznaczone dla użytkonwika o ID: {self._logged_in_user_id}."
                print(f"[BridgeRoom_deletePatient] {msg}")
                self.patientAdditionFailed.emit(msg)
                return

            # **Próba usunięcia pacjenta**
            success = patients_controller.delete_patient(insert_patient_id)

            if success:
                print(f"[BridgeRoom_deletePatient] Pacjent o ID {insert_patient_id} został usunięty.")
                self.patientDeletedSuccessfully.emit()
            else:
                print("[BridgeRoom_deletePatient] Nie udało się usunąć pacjenta.")
                self.patientAdditionFailed.emit("Nie udało się usunąć pacjenta.")

        except ValueError as ve:
            print(f"[BridgeRoom_deletePatient] Błąd wartości: {str(ve)}")
            self.patientAdditionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deletePatient] Błąd bazy danych: {str(rue)}")
            self.patientAdditionFailed.emit("Błąd systemu podczas usuwania pacjenta.")

        except KeyError as ke:
            print(f"[BridgeRoom_deletePatient] Błąd klucza w danych: {str(ke)}")
            self.patientAdditionFailed.emit("Błąd w strukturze danych.")





 # -------------------------------------------------------------------------

    @Slot()
    def checkAccessToAdminUsersView(self):
        """
        Sprawdza, czy użytkownik ma dostęp do widoku AdminSettingsMainUsersList.qml.
        Dostęp mają tylko role_id 1 i 9.
        """
        if self._logged_in_user_id is not None:
            try:
                # Pobranie roli użytkownika
                users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
                role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)

                # **Sprawdzenie, czy użytkownik ma uprawnienia**
                if role_id in [1, 9]:
                    print(f"[BackendBridge] Użytkownik {self._logged_in_user_id} (role_id={role_id}) ma dostęp do widoku użytkowników.")
                    
                    # Emitowanie sygnału o dostępie
                    self.accessGranted.emit()
                else:
                    print(f"[BackendBridge] Użytkownik {self._logged_in_user_id} (role_id={role_id}) nie ma dostępu do widoku użytkowników.")
                    
                    # Emitowanie komunikatu o braku dostępu
                    self.accessDenied.emit("Brak uprawnień do ustawień administracyjnych.")

            except ValueError as ve:
                print(f"[BackendBridge] Błąd danych wejściowych podczas sprawdzania dostępu: {ve}")
                self.accessDenied.emit("Błąd danych wejściowych.")

            except KeyError as ke:
                print(f"[BackendBridge] Błąd klucza podczas przetwarzania dostępu: {ke}")
                self.accessDenied.emit("Błąd przetwarzania danych.")

            except AttributeError as ae:
                print(f"[BackendBridge] Błąd atrybutu (np. brak metody lub kontrolera): {ae}")
                self.accessDenied.emit("Błąd systemowy - brak kontrolera.")

        else:
            print("[BackendBridge] Nie można sprawdzić dostępu. user_id jest None.")
            self.accessDenied.emit("Nie zalogowano użytkownika.")

 # -------------------------------------------------------------------------

    @Slot(int, str, str)
    def addDiagnosis(self, insert_appointment_id, insert_description, insert_icd11_code):
        """
        Dodaje diagnozę do bazy danych po sprawdzeniu uprawnień użytkownika.

        :param insert_appointment_id: ID wizyty, do której przypisywana jest diagnoza.
        :param insert_description: Opis diagnozy.
        :param insert_icd11_code: Kod diagnozy ICD-11.
        """

        print(f"[DEBUG] Otrzymany kod ICD-11: {insert_icd11_code}")
        
        if self._logged_in_user_id is None:
            print("[BridgeRoom_addDiagnosis] Brak zalogowanego użytkownika.")
            self.diagnosisAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            patients_service = PatientsService(self.main_controller)
            diagnoses_controller = DiagnosesController(self.main_controller.db_controller)

            errors = []  # Lista do przechowywania błędów

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_addDiagnosis] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            if role_id in [1, 2, 9, 10]:
                # Pobranie wszystkich ID wizyt w tabeli appointments
                all_appointment_ids = patients_service.get_all_appointment_ids_appointments_table()
                if insert_appointment_id not in all_appointment_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie istnieje w bazie wizyt.")

            elif role_id in [3, 4, 5, 6, 7, 8]:
                # Pobranie employee_id użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                print(f"[BridgeRoom_addDiagnosis] Employee ID dla użytkownika {self._logged_in_user_id}: {employee_id}")

                # Pobranie ID wizyt przypisanych do pracownika
                assigned_appointment_ids = patients_service.get_appointments_by_employee_id(employee_id)
                if insert_appointment_id not in assigned_appointment_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie jest przypisana do pracownika o ID {employee_id}.")
                    errors.append(f"Dostępne ID wizyt dla pracownika {employee_id}: {assigned_appointment_ids}")

            # **Walidacja danych wejściowych**
            
            # Walidacja insert_description - nie może być puste
            if not insert_description.strip():
                errors.append("Opis diagnozy nie może być pusty.")

            # Walidacja insert_icd11_code - nie może być puste
            if not insert_icd11_code.strip():
                errors.append("Kod ICD-11 nie może być pusty.")

            # **Jeśli wystąpiły błędy, zakończ działanie i wyemituj komunikaty**
            if errors:
                error_message = " | ".join(errors)  # Łączenie błędów w jeden komunikat
                print(f"[BridgeRoom_addDiagnosis] Błędy walidacji: {error_message}")
                self.diagnosisAdditionFailed.emit(error_message)
                return

            # Próba dodania diagnozy
            success = diagnoses_controller.add_diagnosis(
                insert_appointment_id, insert_description, insert_icd11_code
            )

            if success:
                print(f"[BridgeRoom_addDiagnosis] Diagnoza dla wizyty {insert_appointment_id} została dodana.")
                self.diagnosisAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addDiagnosis] Nie udało się dodać diagnozy.")
                self.diagnosisAdditionFailed.emit("Nie udało się dodać diagnozy.")

        except ValueError as ve:
            print(f"[BridgeRoom_addDiagnosis] Błąd wartości: {str(ve)}")
            self.diagnosisAdditionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_addDiagnosis] Błąd bazy danych: {str(rue)}")
            self.diagnosisAdditionFailed.emit("Błąd systemu podczas dodawania diagnozy.")

        except KeyError as ke:
            print(f"[BridgeRoom_addDiagnosis] Błąd klucza w danych: {str(ke)}")
            self.diagnosisAdditionFailed.emit("Błąd w strukturze danych.")


 # -------------------------------------------------------------------------

    @Slot(int, int, str, str)
    def updateDiagnosis(self, insert_diagnosis_id, insert_appointment_id=None, insert_description=None, insert_icd11_code=None):
        """
        Aktualizuje diagnozę w bazie danych po sprawdzeniu uprawnień użytkownika.

        :param insert_diagnosis_id: ID diagnozy do aktualizacji.
        :param insert_appointment_id: (Opcjonalnie) ID wizyty powiązanej z diagnozą.
        :param insert_description: (Opcjonalnie) Nowy opis diagnozy.
        :param insert_icd11_code: (Opcjonalnie) Nowy kod ICD-11 diagnozy.
        """

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateDiagnosis] Brak zalogowanego użytkownika.")
            self.diagnosisUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            patients_service = PatientsService(self.main_controller)
            diagnoses_controller = DiagnosesController(self.main_controller.db_controller)

            errors = []  # Lista błędów

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_updateDiagnosis] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            # Sprawdzenie czy diagnoza istnieje w bazie
            all_diagnosis_ids = patients_service.get_all_diagnosis_ids()
            if insert_diagnosis_id not in all_diagnosis_ids:
                errors.append(f"Diagnoza o ID {insert_diagnosis_id} nie istnieje w systemie.")

            # Weryfikacja uprawnień użytkownika
            if role_id in [1, 2, 9, 10] and insert_appointment_id:
                all_appointment_ids = patients_service.get_all_appointment_ids_appointments_table()
                if insert_appointment_id not in all_appointment_ids:
                    errors.append(f"Wizyta o ID {insert_appointment_id} nie istnieje w systemie.")

            elif role_id in [3, 4, 5, 6, 7, 8]:
                # Pobranie employee_id użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                print(f"[BridgeRoom_updateDiagnosis] Employee ID dla użytkownika {self._logged_in_user_id}: {employee_id}")

                if insert_appointment_id:
                    all_appointment_ids = patients_service.get_all_appointment_ids_appointments_table()
                    if insert_appointment_id not in all_appointment_ids:
                        errors.append(f"Wizyta o ID {insert_appointment_id} nie istnieje w systemie.")

                    # Sprawdzenie, czy wizyta jest przypisana do pracownika
                    assigned_appointment_ids = patients_service.get_appointments_by_employee_id(employee_id)
                    if insert_appointment_id not in assigned_appointment_ids:
                        errors.append(f"Wizyta o ID {insert_appointment_id} nie jest przypisana do pracownika o ID {employee_id}.")
                        errors.append(f"ID wizyty pracownika o ID {employee_id} to: {assigned_appointment_ids}")

                # Sprawdzenie, czy diagnoza została wystawiona przez tego pracownika
                assigned_diagnosis_ids = patients_service.get_diagnosis_id_by_employee_id(employee_id)
                if insert_diagnosis_id not in assigned_diagnosis_ids:
                    errors.append(f"Diagnoza o ID {insert_diagnosis_id} nie jest wystawiona przez pracownika o ID {employee_id}.")
                    errors.append(f"ID diagnozy wystawione przez pracownika o ID {employee_id} to: {assigned_diagnosis_ids}")

            # Jeśli są błędy, emitujemy je wszystkie na raz
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateDiagnosis] Błędy: \n{error_message}")
                self.diagnosisUpdateFailed.emit(error_message)
                return

            # Pobranie aktualnych danych diagnozy
            current_data = patients_service.get_diagnosis_by_id_diagnoses_table(insert_diagnosis_id)
            if not current_data:
                msg = f"Nie znaleziono diagnozy o ID {insert_diagnosis_id}."
                print(f"[BridgeRoom_updateDiagnosis] {msg}")
                self.diagnosisUpdateFailed.emit(msg)
                return

            # Tworzenie słownika do aktualizacji tylko dla niepustych wartości
            update_data = {}
            if insert_appointment_id and current_data.get("fk_appointment_id") != insert_appointment_id:
                update_data["fk_appointment_id"] = insert_appointment_id
            if insert_description and current_data.get("description") != insert_description:
                update_data["description"] = insert_description
            if insert_icd11_code and current_data.get("icd11_code") != insert_icd11_code:
                update_data["icd11_code"] = insert_icd11_code

            # Sprawdzenie czy są zmiany do aktualizacji
            if not update_data:
                msg = "Brak zmian w danych do aktualizacji."
                print(f"[BridgeRoom_updateDiagnosis] {msg}")
                self.diagnosisUpdateFailed.emit(msg)
                return

            # Próba aktualizacji diagnozy
            success = diagnoses_controller.update_diagnosis(insert_diagnosis_id, **update_data)

            if success:
                print(f"[BridgeRoom_updateDiagnosis] Diagnoza o ID {insert_diagnosis_id} została zaktualizowana.")
                self.diagnosisUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateDiagnosis] Nie udało się zaktualizować diagnozy.")
                self.diagnosisUpdateFailed.emit("Nie udało się zaktualizować diagnozy.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateDiagnosis] Błąd operacyjny bazy danych: {str(op_err)}")
            self.diagnosisUpdateFailed.emit("Błąd operacyjny bazy danych.")
        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateDiagnosis] Błąd bazy danych: {str(db_err)}")
            self.diagnosisUpdateFailed.emit("Błąd bazy danych.")
        except KeyError as ke:
            print(f"[BridgeRoom_updateDiagnosis] Błąd klucza w danych: {str(ke)}")
            self.diagnosisUpdateFailed.emit("Błąd w strukturze danych.")
        except TypeError as te:
            print(f"[BridgeRoom_updateDiagnosis] Błąd przetwarzania danych: {str(te)}")
            self.diagnosisUpdateFailed.emit("Błąd przetwarzania danych.")



 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteDiagnosis(self, insert_diagnosis_id):
        """
        Usuwa diagnozę z systemu po zweryfikowaniu poprawności danych.

        :param insert_diagnosis_id: ID diagnozy do usunięcia.
        """

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteDiagnosis] Brak zalogowanego użytkownika.")
            self.diagnosisDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            patients_service = PatientsService(self.main_controller)
            diagnoses_controller = DiagnosesController(self.main_controller.db_controller)

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_deleteDiagnosis] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            # Sprawdzenie czy diagnoza istnieje w bazie
            all_diagnosis_ids = patients_service.get_all_diagnosis_ids()
            if insert_diagnosis_id not in all_diagnosis_ids:
                msg = f"Diagnoza o ID {insert_diagnosis_id} nie istnieje w systemie."
                print(f"[BridgeRoom_deleteDiagnosis] {msg}")
                self.diagnosisDeletionFailed.emit(msg)
                return

            # **Logika dla ról [3, 4, 5, 6, 7, 8]**
            if role_id in [3, 4, 5, 6, 7, 8]:
                # Pobranie employee_id użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                print(f"[BridgeRoom_deleteDiagnosis] Employee ID dla użytkownika {self._logged_in_user_id}: {employee_id}")

                # Pobranie listy przypisanych diagnosis_id dla pracownika
                assigned_diagnosis_ids = patients_service.get_diagnosis_id_by_employee_id(employee_id)

                # Debugowanie wartości
                print(f"[BridgeRoom_deleteDiagnosis] Debug - Diagnosis ID do usunięcia: {insert_diagnosis_id}")
                print(f"[BridgeRoom_deleteDiagnosis] Debug - Lista przypisanych diagnosis_id: {assigned_diagnosis_ids}")

                # Ostateczne sprawdzenie, czy diagnoza należy do pracownika
                if insert_diagnosis_id not in assigned_diagnosis_ids:
                    msg = f"Diagnoza o ID {insert_diagnosis_id} nie jest wystawiona przez pracownika o ID {employee_id}."
                    print(f"[BridgeRoom_deleteDiagnosis] {msg}")
                    self.diagnosisDeletionFailed.emit(msg)
                    msg1 = f"ID Diagnozy wystawiona przez pracownika o ID {employee_id} to: {assigned_diagnosis_ids}"
                    print(f"[BridgeRoom_deleteDiagnosis] {msg1}")
                    self.diagnosisDeletionFailed.emit(msg1)
                    return

            # **Próba usunięcia diagnozy**
            success = diagnoses_controller.delete_diagnosis(insert_diagnosis_id)

            if success:
                print(f"[BridgeRoom_deleteDiagnosis] Diagnoza o ID {insert_diagnosis_id} została usunięta.")
                self.diagnosisDeletedSuccessfully.emit()
            else:
                print("[BridgeRoom_deleteDiagnosis] Nie udało się usunąć diagnozy.")
                self.diagnosisDeletionFailed.emit("Nie udało się usunąć diagnozy.")

        except ValueError as ve:
            print(f"[BridgeRoom_deleteDiagnosis] Błąd wartości: {str(ve)}")
            self.diagnosisDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deleteDiagnosis] Błąd bazy danych: {str(rue)}")
            self.diagnosisDeletionFailed.emit("Błąd systemu podczas usuwania diagnozy.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteDiagnosis] Błąd klucza w danych: {str(ke)}")
            self.diagnosisDeletionFailed.emit("Błąd w strukturze danych.")


 # -------------------------------------------------------------------------

    @Slot(int, str, int, float, int)
    def addPrescription(self, insert_appointment_id, insert_medicine, insert_dose, insert_price, insert_code):
        """
        Dodaje receptę do bazy danych po sprawdzeniu uprawnień użytkownika.

        :param insert_appointment_id: ID wizyty, do której przypisywana jest recepta.
        :param insert_medicine: Nazwa leku.
        :param insert_dose: Dawka leku.
        :param insert_price: Cena leku.
        :param insert_code: Kod recepty.
        """

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addPrescription] Brak zalogowanego użytkownika.")
            self.prescriptionAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            patients_service = PatientsService(self.main_controller)
            prescriptions_controller = PrescriptionsController(self.main_controller.db_controller)

            errors = []  # Lista na błędy

            # **Sprawdzenie, czy kod recepty już istnieje**
            all_prescription_codes = patients_service.get_all_prescription_codes()
            if str(insert_code) in map(str, all_prescription_codes):  # Konwersja na stringi, aby uniknąć błędów porównania
                errors.append(f"Recepta o kodzie {insert_code} już istnieje w systemie.")

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_addPrescription] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            if role_id in [1, 2, 9, 10]:
                # Pobranie wszystkich ID wizyt w tabeli appointments
                all_appointment_ids = patients_service.get_all_appointment_ids_appointments_table()
                if insert_appointment_id not in all_appointment_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie istnieje w bazie wizyt.")

                # **Dodatkowe sprawdzenie - czy wizyta jest przypisana do pracownika (role_id = 3)**
                assigned_prescriptions_ids = patients_service.get_appointment_id_by_user_id()
                if insert_appointment_id not in assigned_prescriptions_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie jest przypisana do żadnego lekarza (role_id = 3).")
                    errors.append(f"Dostępne ID wizyty dla użytkownika o roli 3: {assigned_prescriptions_ids}")

            elif role_id == 3:
                # Pobranie employee_id użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                print(f"[BridgeRoom_addPrescription] Employee ID dla użytkownika {self._logged_in_user_id}: {employee_id}")

                # Pobranie ID wizyt przypisanych do pracownika
                assigned_appointment_ids = patients_service.get_appointments_by_employee_id(employee_id)
                if insert_appointment_id not in assigned_appointment_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie jest przypisana do pracownika o ID {employee_id}.")
                    errors.append(f"Dostępne ID wizyty dla pracownika o ID {employee_id}: {assigned_appointment_ids}.")

            # **Walidacje danych**
            
            # Walidacja insert_medicine - tylko litery, polskie znaki i spacja
            if not re.match(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]+$", insert_medicine):
                errors.append("Nazwa leku może zawierać tylko litery i polskie znaki.")

            # Walidacja insert_dose - tylko liczby od 1 do 99999
            if not re.match(r"^\d{1,5}$", str(insert_dose)) or not (1 <= int(insert_dose) <= 99999):
                errors.append("Dawka leku musi być liczbą od 1 do 99999.")

            # Walidacja insert_price - liczby zmiennoprzecinkowe dodatnie
            try:
                insert_price = float(insert_price)
                if insert_price <= 0:
                    raise ValueError
            except ValueError:
                errors.append("Cena musi być dodatnią liczbą zmiennoprzecinkową.")

            # Walidacja insert_code - czterocyfrowa liczba
            insert_code = str(insert_code).strip()  # Konwersja na str i usunięcie białych znaków
            if not re.fullmatch(r"\d{4}", insert_code):
                errors.append("Kod recepty musi składać się dokładnie z 4 cyfr.")

            # **Jeśli wystąpiły błędy, zakończ działanie i wyemituj komunikaty**
            if errors:
                error_message = " | ".join(errors)  # Łączenie błędów w jeden komunikat
                print(f"[BridgeRoom_addPrescription] Błędy walidacji: {error_message}")
                self.prescriptionAdditionFailed.emit(error_message)
                return

            # **Próba dodania recepty**
            success = prescriptions_controller.add_prescription(
                insert_appointment_id, insert_medicine, insert_dose, insert_price, insert_code
            )

            if success:
                print(f"[BridgeRoom_addPrescription] Recepta dla wizyty {insert_appointment_id} została dodana.")
                self.prescriptionAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addPrescription] Nie udało się dodać recepty.")
                self.prescriptionAdditionFailed.emit("Nie udało się dodać recepty.")

        except ValueError as ve:
            print(f"[BridgeRoom_addPrescription] Błąd wartości: {str(ve)}")
            self.prescriptionAdditionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_addPrescription] Błąd bazy danych: {str(rue)}")
            self.prescriptionAdditionFailed.emit("Błąd systemu podczas dodawania recepty.")

        except KeyError as ke:
            print(f"[BridgeRoom_addPrescription] Błąd klucza w danych: {str(ke)}")
            self.prescriptionAdditionFailed.emit("Błąd w strukturze danych.")

 # -------------------------------------------------------------------------

    @Slot(int, int, str, int, float, str)
    def updatePrescription(self, insert_prescription_id, insert_appointment_id, insert_medicine, insert_dose, insert_price, insert_code):
        """
        Aktualizuje receptę w bazie danych po sprawdzeniu uprawnień użytkownika.

        :param insert_prescription_id: ID recepty do aktualizacji.
        :param insert_appointment_id: ID wizyty powiązanej z receptą.
        :param insert_medicine: Nowa nazwa leku.
        :param insert_dose: Nowa dawka leku.
        :param insert_price: Nowa cena leku.
        :param insert_code: Nowy kod recepty (opcjonalnie).
        """

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updatePrescription] Brak zalogowanego użytkownika.")
            self.prescriptionUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            patients_service = PatientsService(self.main_controller)
            prescriptions_controller = PrescriptionsController(self.main_controller.db_controller)

            errors = []  # Lista na błędy

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_updatePrescription] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            # Sprawdzenie, czy recepta istnieje
            all_prescription_ids = patients_service.get_all_prescription_ids()
            if insert_prescription_id not in all_prescription_ids:
                errors.append(f"Recepta o ID {insert_prescription_id} nie istnieje w systemie.")

            if role_id in [1, 2, 9, 10]:
                # Pobranie wszystkich ID wizyt z tabeli appointments
                all_appointment_ids = patients_service.get_all_appointment_ids_appointments_table()
                if insert_appointment_id and insert_appointment_id not in all_appointment_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie istnieje w bazie wizyt.")

                # Dodatkowe sprawdzenie – czy wizyta jest przypisana do lekarza (role_id = 3)
                assigned_prescriptions_ids = patients_service.get_appointment_id_by_user_id()
                if insert_appointment_id and insert_appointment_id not in assigned_prescriptions_ids:
                    errors.append(f"Wizyta o ID ({insert_appointment_id}) nie jest przypisana do żadnego lekarza (role_id = 3).")
                    errors.append(f"Dostępne wizyty dla pracownika o roli o ID {role_id}: {assigned_prescriptions_ids}")

            elif role_id == 3:
                # Pobranie employee_id użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                print(f"[BridgeRoom_updatePrescription] Employee ID dla użytkownika {self._logged_in_user_id}: {employee_id}")

                # Sprawdzenie, czy wizyta jest przypisana do pracownika
                assigned_appointment_ids = patients_service.get_appointments_by_employee_id(employee_id)
                if insert_appointment_id and insert_appointment_id not in assigned_appointment_ids:
                    errors.append(f"Wizyta o ID {insert_appointment_id} nie jest przypisana do pracownika o ID {employee_id}.")
                    errors.append(f"Dostępne ID wizyt dla pracownika {employee_id}: {assigned_appointment_ids}")

                # Sprawdzenie, czy recepta została wystawiona przez tego pracownika
                assigned_prescription_ids = patients_service.get_prescriptions_id_by_employee_id(employee_id)
                if insert_prescription_id not in assigned_prescription_ids:
                    errors.append(f"Recepta o ID {insert_prescription_id} nie została wystawiona przez pracownika o ID {employee_id}.")
                    errors.append(f"Dostępne recepty dla pracownika {employee_id}: {assigned_prescription_ids}")

            # Sprawdzenie, czy kod recepty już istnieje – wykonujemy tylko, gdy podano wartość
            if insert_code and insert_code.strip() != "":
                all_prescription_codes = patients_service.get_all_prescription_codes()
                if str(insert_code) in map(str, all_prescription_codes):
                    errors.append(f"Recepta o kodzie {insert_code} już istnieje w systemie.")

            # Walidacje danych – wykonujemy walidację tylko dla pól, które nie są puste
            if insert_medicine:
                # Walidacja insert_medicine – tylko litery, polskie znaki i spacja
                if not re.match(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]+$", insert_medicine):
                    errors.append("Nazwa leku może zawierać tylko litery i polskie znaki.")

            if insert_dose:
                # Walidacja insert_dose – tylko liczby od 1 do 99999
                if not re.match(r"^\d{1,5}$", str(insert_dose)) or not (1 <= int(insert_dose) <= 99999):
                    errors.append("Dawka leku musi być liczbą od 1 do 99999.")

            if insert_price:
                # Walidacja insert_price – liczby zmiennoprzecinkowe dodatnie
                try:
                    insert_price = float(insert_price)
                    if insert_price <= 0:
                        raise ValueError
                except ValueError:
                    errors.append("Cena musi być dodatnią liczbą zmiennoprzecinkową.")

            # Jeśli wystąpiły błędy, zakończ działanie i wyemituj komunikaty
            if errors:
                error_message = " | ".join(errors)
                print(f"[BridgeRoom_updatePrescription] Błędy walidacji: {error_message}")
                self.prescriptionUpdateFailed.emit(error_message)
                return

            # Pobranie aktualnych danych recepty
            current_data = patients_service.get_prescription_by_id(insert_prescription_id)
            if not current_data:
                errors.append(f"Nie znaleziono recepty o ID {insert_prescription_id}.")

            # Konwersja kodu recepty – jeśli pole puste, traktujemy jako None
            if not insert_code or insert_code.strip() == "":
                insert_code = None

            # Tworzenie słownika do aktualizacji tylko dla pól, które są niepuste i uległy zmianie
            update_data = {}
            if insert_appointment_id and current_data.get("fk_appointment_id") != insert_appointment_id:
                update_data["fk_appointment_id"] = insert_appointment_id
            if insert_medicine and current_data.get("medicine_name") != insert_medicine:
                update_data["medicine_name"] = insert_medicine
            if insert_dose and current_data.get("dosage") != insert_dose:
                update_data["dosage"] = insert_dose
            if insert_price and current_data.get("medicine_price") != insert_price:
                update_data["medicine_price"] = insert_price
            if insert_code and current_data.get("prescription_code") != insert_code:
                update_data["prescription_code"] = insert_code

            if not update_data:
                errors.append("Brak zmian w danych do aktualizacji.")

            if errors:
                error_message = " | ".join(errors)
                print(f"[BridgeRoom_updatePrescription] Błędy walidacji: {error_message}")
                self.prescriptionUpdateFailed.emit(error_message)
                return

            # Próba aktualizacji recepty
            success = prescriptions_controller.update_prescription(insert_prescription_id, **update_data)

            if success:
                print(f"[BridgeRoom_updatePrescription] Recepta o ID {insert_prescription_id} została zaktualizowana.")
                self.prescriptionUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updatePrescription] Nie udało się zaktualizować recepty.")
                self.prescriptionUpdateFailed.emit("Nie udało się zaktualizować recepty.")

        except ValueError as ve:
            print(f"[BridgeRoom_updatePrescription] Błąd wartości: {str(ve)}")
            self.prescriptionUpdateFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_updatePrescription] Błąd bazy danych: {str(rue)}")
            self.prescriptionUpdateFailed.emit("Błąd systemu podczas aktualizacji recepty.")

        except KeyError as ke:
            print(f"[BridgeRoom_updatePrescription] Błąd klucza w danych: {str(ke)}")
            self.prescriptionUpdateFailed.emit("Błąd w strukturze danych.")


 # -------------------------------------------------------------------------

    @Slot(int)
    def deletePrescription(self, insert_prescription_id):
        """
        Usuwa receptę z systemu po zweryfikowaniu poprawności danych.

        :param insert_prescription_id: ID recepty do usunięcia.
        """

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deletePrescription] Brak zalogowanego użytkownika.")
            self.prescriptionDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            patients_service = PatientsService(self.main_controller)
            prescriptions_controller = PrescriptionsController(self.main_controller.db_controller)

            errors = []  # Lista na błędy

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BridgeRoom_deletePrescription] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            # Sprawdzenie czy recepta istnieje w bazie
            all_prescription_ids = patients_service.get_all_prescription_ids()
            if insert_prescription_id not in all_prescription_ids:
                errors.append(f"Recepta o ID {insert_prescription_id} nie istnieje w systemie.")

            if role_id == 3:
                # Pobranie employee_id użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                print(f"[BridgeRoom_deletePrescription] Employee ID dla użytkownika {self._logged_in_user_id}: {employee_id}")

                # Sprawdzenie, czy recepta została wystawiona przez tego pracownika
                assigned_prescription_ids = patients_service.get_prescriptions_id_by_employee_id(employee_id)
                if insert_prescription_id not in assigned_prescription_ids:
                    errors.append(
                        f"Recepta o ID {insert_prescription_id} nie została wystawiona przez pracownika o ID {employee_id}."
                    )
                    errors.append(f"Dostępne recepty dla pracownika {employee_id}: {assigned_prescription_ids}")


            # **Jeśli wystąpiły błędy, zakończ działanie i wyemituj komunikaty**
            if errors:
                error_message = " | ".join(errors)  # Łączenie błędów w jeden komunikat
                print(f"[BridgeRoom_deletePrescription] Błędy walidacji: {error_message}")
                self.prescriptionDeletionFailed.emit(error_message)
                return

            # **Próba usunięcia recepty**
            success = prescriptions_controller.delete_prescription(insert_prescription_id)

            if success:
                print(f"[BridgeRoom_deletePrescription] Recepta o ID {insert_prescription_id} została usunięta.")
                self.prescriptionDeletedSuccessfully.emit()
            else:
                print("[BridgeRoom_deletePrescription] Nie udało się usunąć recepty.")
                self.prescriptionDeletionFailed.emit("Nie udało się usunąć recepty.")

        except ValueError as ve:
            print(f"[BridgeRoom_deletePrescription] Błąd wartości: {str(ve)}")
            self.prescriptionDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deletePrescription] Błąd bazy danych: {str(rue)}")
            self.prescriptionDeletionFailed.emit("Błąd systemu podczas usuwania recepty.")

        except KeyError as ke:
            print(f"[BridgeRoom_deletePrescription] Błąd klucza w danych: {str(ke)}")
            self.prescriptionDeletionFailed.emit("Błąd w strukturze danych.")


 # -------------------------------------------------------------------------

    @Slot()
    def checkPrescriptionsCRUDAccess(self):
        """
        Sprawdza, czy użytkownik ma dostęp do widoku recept.
        Jeśli użytkownik ma rolę w zakresie [4, 5, 6, 7, 8], blokuje dostęp i emituje błąd.
        """

        if self._logged_in_user_id is None:
            print("[BackendBridge_checkPrescriptionsAccess] Brak zalogowanego użytkownika.")
            self.prescriptionsErrorOccurred.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolera użytkowników
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"[BackendBridge_checkPrescriptionsAccess] Użytkownik o ID {self._logged_in_user_id} ma rolę {role_id}.")

            # Warunek: Użytkownik z rolą 4-8 nie ma dostępu
            if role_id in [4, 5, 6, 7, 8]:
                msg = "Brak uprawnień do rzadządzania receptami."
                print(f"[BackendBridge_checkPrescriptionsAccess] {msg}")
                
                # Emitowanie komunikatu błędu
                self.prescriptionsErrorOccurred.emit(msg)
                return  # Zakończ metodę bez dalszego przetwarzania

            # Jeśli użytkownik ma dostęp, wyemituj sygnał o przyznaniu dostępu
            print(f"[BackendBridge_checkPrescriptionsAccess] Użytkownik {self._logged_in_user_id} ma dostęp do widoku recept.")
            self.prescriptionsAccessGranted.emit()

        except sqlite3.OperationalError as op_err:
            msg = f"Błąd operacyjny bazy danych: {op_err}"
            print(f"[BackendBridge_checkPrescriptionsAccess] {msg}")
            self.prescriptionsErrorOccurred.emit(msg)

        except sqlite3.DatabaseError as db_err:
            msg = f"Błąd bazy danych: {db_err}"
            print(f"[BackendBridge_checkPrescriptionsAccess] {msg}")
            self.prescriptionsErrorOccurred.emit(msg)

        except KeyError as ke:
            msg = f"Błąd struktury danych: {ke}"
            print(f"[BackendBridge_checkPrescriptionsAccess] {msg}")
            self.prescriptionsErrorOccurred.emit(msg)

        except TypeError as te:
            msg = f"Błąd przetwarzania danych: {te}"
            print(f"[BackendBridge_checkPrescriptionsAccess] {msg}")
            self.prescriptionsErrorOccurred.emit(msg)
