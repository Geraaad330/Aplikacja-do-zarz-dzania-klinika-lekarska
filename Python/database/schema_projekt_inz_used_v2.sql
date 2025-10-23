-- tabele usuwa się w odwrotnej kolejności niż są tworzone
DROP TABLE IF EXISTS patient_forms;
DROP TABLE IF EXISTS meeting_participants;
DROP TABLE IF EXISTS internal_meetings;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS diagnoses;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS room_reservations;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS assigned_patients;
DROP TABLE IF EXISTS users_accounts;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS employee_services;
DROP TABLE IF EXISTS employee_specialties;
DROP TABLE IF EXISTS form_types;
DROP TABLE IF EXISTS room_types;
DROP TABLE IF EXISTS meeting_types;
DROP TABLE IF EXISTS specialties;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS system_permissions;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS patients;



-- 1. 
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Klucz główny z AUTOINCREMENT
    first_name TEXT NOT NULL CHECK (
        first_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*' -- może zawierać tylko małe i duże litery z polskimi znakami. Nie może zawirać innych znaków ANI SPACJI
    ),
    last_name TEXT NOT NULL CHECK (
        last_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*' -- może zawierać tylko małe i duże litery z polskimi znakami. Nie może zawirać innych znaków ANI SPACJI
    ),
    pesel TEXT NOT NULL UNIQUE CHECK (
        LENGTH(pesel) = 11 AND pesel GLOB '[0-9]*' -- może zawierać tylko dokładnie 11 cyfr. Nie może zawirać innych znaków
    ),
    phone TEXT NOT NULL UNIQUE CHECK (
        LENGTH(phone) = 9 AND phone GLOB '[0-9]*' -- może zawierać tylko dokładnie 9 cyfr. Nie może zawirać innych znaków
    ),
    email TEXT NOT NULL UNIQUE CHECK (
        email LIKE '%@%' AND email LIKE '%.%' -- Musi zawierać znak '@' i '.', może zawierać cyfry, małe i duże litery
    ),
    address TEXT, -- Dowolny tekst, brak dodatkowych ograniczeń
    date_of_birth TEXT NOT NULL CHECK (
        date_of_birth GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]' -- Format daty YYYY-MM-DD
    ),
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. 
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    -- Główne pole identyfikatora pracownika, automatycznie zwiększane (autoincrement).

    first_name TEXT NOT NULL CHECK (first_name GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]*'), 
    -- Imię pracownika, wymagane, musi zawierać tylko litery (w tym polskie znaki).

    last_name TEXT NOT NULL CHECK (last_name GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]*'), 
    -- Nazwisko pracownika, wymagane, musi zawierać tylko litery (w tym polskie znaki).

    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@__%.__%'), 
    -- Adres e-mail pracownika, wymagany, musi być unikalny i pasować do formatu zawierającego "@" i ".".

    phone TEXT NOT NULL UNIQUE CHECK (LENGTH(phone) = 9 AND phone GLOB '[0-9]*'),
    -- Numer telefonu pracownika, wymagany, musi być unikalny i zawierać dokładnie 9 cyfr.

    profession TEXT NOT NULL CHECK ( -- MODYFIKOWANE TYLKO NA POZIOMIE KODU SQL PRZEZ KLAUZksULĘ CHECK IN () 
        profession IN (
            'Informatyk', 
            'Psychiatra', 
            'Psycholog kliniczny', 
            'Psychoterapeuta', 
            'Psychopedagog', 
            'Terapeuta uzależnień', 
            'Dietetyk kliniczny', 
            'Recepcjonista', 
            'Księgowy', 
            'Pracownik obsługi technicznej', 
            'Pracownik obsługi porządkowej',
            'Administrator',
            'Kierownik'
        )
    ), 
    -- Zawód pracownika, wymagany, musi być jednym z określonych predefiniowanych zawodów.

    is_medical_staff INTEGER NOT NULL CHECK (is_medical_staff IN (0, 1)),
    -- Określenie, czy pracownik należy do personelu medycznego (0 - nie, 1 - tak), wymagane

    is_active BOOLEAN DEFAULT TRUE
);

-- 3.
CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Główne pole identyfikatora roli, automatycznie zwiększane.

    role_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (role_name GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]*')
);



-- 4.
CREATE TABLE services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(service_type) > 0),
    duration_minutes INTEGER NOT NULL CHECK (
        duration_minutes BETWEEN 1 AND 300
    ),
    service_price REAL NOT NULL CHECK (
        service_price BETWEEN 1 AND 500
    ),
    is_active BOOLEAN DEFAULT TRUE
);


-- 5.
CREATE TABLE specialties (
    specialty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (specialty_name GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*'),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE meeting_types (
    meeting_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (meeting_type GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\]*')
);

--7. 
CREATE TABLE room_types (
    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (room_type GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
);

-- 8.
CREATE TABLE form_types (
    form_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (form_name GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*'),
    is_active BOOLEAN DEFAULT TRUE
);

-- 9. TABELA PODRZĘDNA
CREATE TABLE employee_specialties (
    employee_specialty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    specialty_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT,
    FOREIGN KEY (specialty_id) REFERENCES specialties(specialty_id) ON DELETE RESTRICT,
    UNIQUE (employee_id, specialty_id)
);

-- ON DELETE CASCADE Jeśli usuniesz rekord pracownika z tabeli employees, to automatycznie zostaną usunięte 
-- wszystkie rekordy w tabeli PODRZĘDNEJ employee_specialties powiązane z tym employee_id.


-- 10. 
CREATE TABLE employee_services (
    employee_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE RESTRICT,
    UNIQUE (employee_id, service_id)
);


-- 11. 
CREATE TABLE users_accounts  (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator użytkownika
    employee_id INTEGER NOT NULL UNIQUE, -- Klucz obcy odwołujący się do pracownika
    role_id INTEGER NOT NULL,
    username TEXT NOT NULL UNIQUE CHECK (
        username GLOB '[a-z0-9._]*'
    ), -- Unikalna nazwa użytkownika, tylko małe litery, cyfry, kropka i podkreślenie
    password_hash TEXT NOT NULL, -- Hash hasła, brak dodatkowej walidacji
    is_active INTEGER NOT NULL CHECK (
        is_active IN (0, 1)
    ), -- Aktywność konta, 0 = nieaktywne, 1 = aktywne
    created_at TEXT NOT NULL CHECK (
        created_at GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]'
    ), -- Data utworzenia w formacie YYYY-MM-DD HH:MM
    last_login TEXT CHECK (
        last_login GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]' OR last_login IS NULL
    ), -- Ostatnie logowanie, opcjonalne, format YYYY-MM-DD HH:MM
    expired TEXT CHECK (
        expired GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]'
    ), -- Ostatnie logowanie, opcjonalne, format YYYY-MM-DD HH:MM
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT ON UPDATE CASCADE
     -- Automatyczne zarządzanie kluczem obcym
);

-- 12.
CREATE TABLE assigned_patients (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_patient_id INTEGER NOT NULL,
    fk_employee_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (fk_patient_id) REFERENCES patients(patient_id) ON DELETE RESTRICT,
    FOREIGN KEY (fk_employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT,
    UNIQUE (fk_patient_id, fk_employee_id)
);

-- 13.
CREATE TABLE rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number INTEGER NOT NULL UNIQUE CHECK (room_number BETWEEN 0 AND 100),
    floor INTEGER NOT NULL CHECK (floor BETWEEN 0 AND 5),
    fk_room_type_id INTEGER,
    FOREIGN KEY (fk_room_type_id) REFERENCES room_types(room_type_id) 
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 14. 
CREATE TABLE room_reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator rezerwacji
    fk_room_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do pokoju
    reservation_date TEXT NOT NULL CHECK (
        reservation_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
    ), -- Format daty YYYY-MM-DD
    reservation_time TEXT NOT NULL CHECK (
       reservation_time GLOB '[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]'
    ), -- Format daty YYYY-MM-DD
    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE -- Automatyczne zarządzanie relacją pokoju
);

-- 15. 
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_assignment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do tabeli assigned_patients
    fk_service_id INTEGER,
    fk_reservation_id INTEGER,
    appointment_date TEXT NOT NULL CHECK (
        appointment_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]'
    ), -- Format daty YYYY-MM-DD
    appointment_status TEXT NOT NULL CHECK (
        appointment_status GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.\\/]*'
    ),
    notes TEXT, -- Notatki bez walidacji
    FOREIGN KEY (fk_assignment_id) REFERENCES assigned_patients(assignment_id)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    FOREIGN KEY (fk_service_id) REFERENCES services(service_id)
    -- jeśli usunie się services_id w services to 
    -- powiązane rekordy fk_service_id z services w zostaną ustawione na NULL
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    FOREIGN KEY (fk_reservation_id) REFERENCES room_reservations(reservation_id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);


-- 16. 
CREATE TABLE diagnoses (
    diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator diagnozy
    fk_appointment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do wizyt
    description TEXT NOT NULL CHECK (
        description GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.\\/]*'
    ), -- Walidacja na małe i duże litery z polskimi znakami
    icd11_code TEXT NOT NULL, -- Walidacja kodu ICD-11 (np. F32.2)
    FOREIGN KEY (fk_appointment_id) REFERENCES appointments(appointment_id)
    -- Operacja zostanie zablokowana, jeśli istnieją powiązane diagnozy.
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

-- 17. 
CREATE TABLE prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator recepty
    fk_appointment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do wizyt
    medicine_name TEXT NOT NULL CHECK (
        medicine_name GLOB '[A-Za-z ]*'
    ), -- Walidacja: tylko duże i małe litery oraz spacje
    dosage REAL NOT NULL CHECK (
        dosage > 0 AND dosage <= 10000
    ), -- Walidacja: liczba zmiennoprzecinkowa > 0 i <= 10000
    medicine_price REAL NOT NULL CHECK (
        medicine_price >= 0
    ), -- Walidacja: liczba zmiennoprzecinkowa >= 0
    prescription_code TEXT NOT NULL CHECK (
        prescription_code GLOB '[0-9][0-9][0-9][0-9]'
    ), -- Walidacja: dokładnie 4 cyfry
    FOREIGN KEY (fk_appointment_id) REFERENCES appointments(appointment_id)
    -- nie pozwoli na usunięcie appointmetn_id w appointments, 
    -- jeśli istnieją powiązane fk_appointment_id w perscriptions.
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);


-- 18. 
CREATE TABLE internal_meetings (
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator spotkania
    fk_meeting_type_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do typu spotkania
    fk_reservation_id INTEGER, -- Klucz obcy odwołujący się do pokoju
    meeting_date TEXT NOT NULL CHECK (
        meeting_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]'
    ), -- Format daty YYYY-MM-DD
    notes TEXT, -- Notatki bez walidacji
    internal_meeting_status TEXT NOT NULL CHECK ( 
        internal_meeting_status GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ]*'
    ), -- Status tylko Zaplanowana, Zrealizowana, Odwołana
    FOREIGN KEY (fk_meeting_type_id) REFERENCES meeting_types(meeting_type_id)
        ON DELETE SET NULL -- jeśli typ pokoju zostanie usunięty to fk_meeting_ty_id będzie NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (fk_reservation_id) REFERENCES room_reservations(reservation_id)
    -- nie pozwoli na usunięcie reservation_id w room_reservations
    -- jeśli istnieją fk_reservation_id w internal_meetings
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

-- 19. 
CREATE TABLE meeting_participants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator uczestnika spotkania
    fk_meeting_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do spotkania
    fk_employee_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do pracownika
    participant_role TEXT NOT NULL CHECK (
        participant_role GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\]*'
    ), -- Tylko dozwolone role: Organizator, Uczestnik
    attendance TEXT NOT NULL CHECK (
        attendance GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\]*'
    ), -- Tylko dozwolone statusy obecności: Obecny, Nieobecny
    FOREIGN KEY (fk_meeting_id) REFERENCES internal_meetings(meeting_id)
    -- jeżeli usunę meeting_id z internal_meetings to zostaną usunięte wszystkie 
    -- rekordy z tabeli meeting_participants zawierające fk_meeting_id
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (fk_employee_id) REFERENCES employees(employee_id)
    -- jeżeli usunę employee_id z tabeli employees to zostaną usunięte wszystkie 
    -- rekordy z tabeli meeting_participants zawierające fk_employee_id
        ON DELETE CASCADE 
        ON UPDATE CASCADE 
);

-- ASSIGN_PATIENTES
-- Dezaktywacja przypisań pacjentów, jeśli pacjent zostanie dezaktywowany
CREATE TRIGGER deactivate_assigned_patients_on_patient
AFTER UPDATE OF is_active ON patients
WHEN NEW.is_active = FALSE
BEGIN
    UPDATE assigned_patients
    SET is_active = FALSE
    WHERE fk_patient_id = OLD.patient_id;
END;

-- Reaktywacja przypisań pacjentów, jeśli pacjent zostanie ponownie aktywowany
CREATE TRIGGER reactivate_assigned_patients_on_patient
AFTER UPDATE OF is_active ON patients
WHEN NEW.is_active = TRUE
BEGIN
    UPDATE assigned_patients
    SET is_active = TRUE
    WHERE fk_patient_id = NEW.patient_id;
END;

-- Dezaktywacja przypisań pacjentów, jeśli pracownik zostanie dezaktywowany
CREATE TRIGGER deactivate_assigned_patients_on_employee
AFTER UPDATE OF is_active ON employees
WHEN NEW.is_active = FALSE
BEGIN
    UPDATE assigned_patients
    SET is_active = FALSE
    WHERE fk_employee_id = OLD.employee_id;
END;

-- Reaktywacja przypisań pacjentów, jeśli pracownik zostanie ponownie aktywowany
CREATE TRIGGER reactivate_assigned_patients_on_employee
AFTER UPDATE OF is_active ON employees
WHEN NEW.is_active = TRUE
BEGIN
    UPDATE assigned_patients
    SET is_active = TRUE
    WHERE fk_employee_id = NEW.employee_id;
END;



-- Trigger dla EMPLOYEE_SEPECIALTIES
-- Gdy employees.is_active = FALSE
-- Dezaktywacja przypisań specjalności, jeśli pracownik zostanie dezaktywowany
CREATE TRIGGER deactivate_employee_specialties_on_employee
AFTER UPDATE OF is_active ON employees
WHEN NEW.is_active = FALSE
BEGIN
    UPDATE employee_specialties
    SET is_active = FALSE
    WHERE employee_id = OLD.employee_id;
END;

-- Reaktywacja przypisań specjalności, jeśli pracownik zostanie ponownie aktywowany
CREATE TRIGGER reactivate_employee_specialties_on_employee
AFTER UPDATE OF is_active ON employees
WHEN NEW.is_active = TRUE
BEGIN
    UPDATE employee_specialties
    SET is_active = TRUE
    WHERE employee_id = NEW.employee_id;
END;

-- Dezaktywacja przypisań specjalności, jeśli specjalność zostanie dezaktywowana
CREATE TRIGGER deactivate_employee_specialties_on_specialty
AFTER UPDATE OF is_active ON specialties
WHEN NEW.is_active = FALSE
BEGIN
    UPDATE employee_specialties
    SET is_active = FALSE
    WHERE specialty_id = OLD.specialty_id;
END;

-- Reaktywacja przypisań specjalności, jeśli specjalność zostanie ponownie aktywowana
CREATE TRIGGER reactivate_employee_specialties_on_specialty
AFTER UPDATE OF is_active ON specialties
WHEN NEW.is_active = TRUE
BEGIN
    UPDATE employee_specialties
    SET is_active = TRUE
    WHERE specialty_id = NEW.specialty_id;
END;



-- Trigger dla EMPLOYEE_SERVICES
-- Gdy employees.is_active = FALSE:
-- Dezaktywacja przypisań usług, jeśli pracownik zostanie dezaktywowany
CREATE TRIGGER deactivate_employee_services_on_employee
AFTER UPDATE OF is_active ON employees
WHEN NEW.is_active = FALSE
BEGIN
    UPDATE employee_services
    SET is_active = FALSE
    WHERE employee_id = OLD.employee_id;
END;

-- Reaktywacja przypisań usług, jeśli pracownik zostanie ponownie aktywowany
CREATE TRIGGER reactivate_employee_services_on_employee
AFTER UPDATE OF is_active ON employees
WHEN NEW.is_active = TRUE
BEGIN
    UPDATE employee_services
    SET is_active = TRUE
    WHERE employee_id = NEW.employee_id;
END;

-- Dezaktywacja przypisań usług, jeśli usługa zostanie dezaktywowana
CREATE TRIGGER deactivate_employee_services_on_service
AFTER UPDATE OF is_active ON services
WHEN NEW.is_active = FALSE
BEGIN
    UPDATE employee_services
    SET is_active = FALSE
    WHERE service_id = OLD.service_id;
END;

-- Reaktywacja przypisań usług, jeśli usługa zostanie ponownie aktywowana
CREATE TRIGGER reactivate_employee_services_on_service
AFTER UPDATE OF is_active ON services
WHEN NEW.is_active = TRUE
BEGIN
    UPDATE employee_services
    SET is_active = TRUE
    WHERE service_id = NEW.service_id;
END;





