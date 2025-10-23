from controllers.database_controller import DatabaseController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.roles_controller import RolesController
from controllers.role_permissions_controller import RolePermissionsController
from controllers.permissions_controller import PermissionsController
from controllers.employees_controller import EmployeesController
from controllers.patients_controller import PatientController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from controllers.room_reservations_controller import RoomReservationsController
from controllers.internal_meetings_controller import InternalMeetingsController
from controllers.appointments_controller import AppointmentsController
from controllers.services_controller import ServicesController
from controllers.login_controller import LoginController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.diagnoses_controller import DiagnosesController
from controllers.employee_services_controller import EmployeeServicesController
from controllers.employee_specialties_controller import EmployeeSpecialtiesController
from controllers.form_types_controller import FormTypesController
from controllers.meeting_participants_controller import MeetingParticipantsController
from controllers.meeting_types_controller import MeetingTypesController
from controllers.patient_forms_controller import PatientFormsController
from controllers.prescriptions_controller import PrescriptionsController
from controllers.specialties_controller import SpecialtiesController


class MainController:
    """
    Główny kontroler aplikacji.
    Zarządza dynamicznym tworzeniem kontrolerów, logowaniem i inicjalizacją tabel.
    """

    def __init__(self):
        """
        Inicjalizuje kontroler bazy danych i dynamiczne zarządzanie kontrolerami.
        """
        self.db_controller = DatabaseController()
        self.controllers = {}  # Słownik do przechowywania dynamicznie tworzonych kontrolerów
        self.logged_in_user = None  # Przechowuje dane zalogowanego użytkownika

    def get_controller(self, controller_class):
        """
        Zwraca instancję kontrolera, tworząc ją tylko wtedy, gdy jest potrzebna.
        """
        if controller_class not in self.controllers:
            self.controllers[controller_class] = controller_class(self.db_controller)
            #print(f"Kontroler {controller_class.__name__} został zainicjalizowany.")
        return self.controllers[controller_class]

    def initialize_critical_tables(self):
        """
        Tworzy tabele krytyczne, które muszą być dostępne od razu po starcie aplikacji.
        """
        critical_controllers = [
            AppointmentsController,
            AssignedPatientsController,
            DiagnosesController,
            EmployeeServicesController,
            EmployeeSpecialtiesController,
            EmployeesController,
            FormTypesController,
            InternalMeetingsController,
            MeetingParticipantsController,
            MeetingTypesController,
            PatientFormsController,
            PatientController,
            PermissionsController,
            PrescriptionsController,
            RolePermissionsController,
            RolesController,
            RoomReservationsController,
            RoomTypesController,
            RoomsController,
            ServicesController,
            SpecialtiesController,
            UsersAccountsController
        ]

        for controller_class in critical_controllers:
            controller = self.get_controller(controller_class)
            controller.create_table()
            #print(f"Tabela dla kontrolera {controller_class.__name__} została utworzona.")

    def perform_table_operation(self, controller_class, operation, *args, **kwargs):
        """
        Wykonuje operację na tabeli za pomocą odpowiedniego kontrolera.
        """
        controller = self.get_controller(controller_class)

        method = getattr(controller, operation, None)
        if not method:
            raise AttributeError(f"Kontroler {controller_class.__name__} nie ma metody '{operation}'")

        return method(*args, **kwargs)

    def initialize_application(self):
        """
        Inicjalizuje aplikację, w tym bazę danych i krytyczne tabele.
        """
        print("Inicjalizacja aplikacji...")
        self.db_controller.connect_to_database()
        self.initialize_critical_tables()
        print("Aplikacja została pomyślnie zainicjalizowana.")

    def shutdown_application(self):
        """
        Zamyka połączenie z bazą danych i zwalnia zasoby.
        """
        print("Zamykanie aplikacji...")
        self.db_controller.close_connection()
        print("Aplikacja została zamknięta.")

    def login_user(self, username, password):
        """
        Loguje użytkownika na podstawie username i hasła.
        Pobiera również przypisane role i uprawnienia.

        Args:
            username (str): Nazwa użytkownika.
            password (str): Hasło użytkownika.

        Returns:
            dict: Dane zalogowanego użytkownika (ID, username, rola, uprawnienia).
        """
        login_controller = self.get_controller(LoginController)
        user = login_controller.authenticate_user(username, password)

        if user:
            self.logged_in_user = user
            print(f"Zalogowano pomyślnie: {user['username']} ({user['role_name']})")
            print(f"Zalogowany użytkownik: {user}")
            return user
        else:
            print("Nieprawidłowy username lub hasło.")
            return None