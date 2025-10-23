-- tabele usuwa się w odwrotnej kolejności niż są tworzone
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS patient_forms;
DROP TABLE IF EXISTS employee_schedule;
DROP TABLE IF EXISTS room_reservations;
DROP TABLE IF EXISTS meeting_participants;
DROP TABLE IF EXISTS internal_meetings;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS diagnoses;
DROP TABLE IF EXISTS appointments;
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


-- Jeśli dana kolumna ma ustawione ograniczenie UNIQUE, oznacza to, że wartości w tej kolumnie muszą być unikalne w całej tabeli. 
-- Pozostałe kolumny w tabeli mogą mieć identyczne wartości.
-- order_id	customer_name	order_date	unique_code
-- 1	    John Doe	2024-12-20	ABC123
-- 2	    John Doe	2024-12-20	DEF456
-- 3	    John Doe	2024-12-20	GHI789
-- 4	    Jane Smith	2024-12-21	JKL101
-- 5	    Jane Smith	2024-12-21	MNO112

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
    )
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
            'Administrator'
        )
    ), 
    -- Zawód pracownika, wymagany, musi być jednym z określonych predefiniowanych zawodów.

    is_medical_staff INTEGER NOT NULL CHECK (is_medical_staff IN (0, 1)) 
    -- Określenie, czy pracownik należy do personelu medycznego (0 - nie, 1 - tak), wymagane.
);

-- 3. 
-- IN jest częścią klauzuli CHECK używanej do walidacji wartości w kolumnie. W tym przypadku permission_name (baza danych) 
-- może przyjmować tylko te wartości, które są wymienione w nawiasach.

-- Nie, jeśli pozostawisz kod SQL w obecnej formie (permission_name IN (wartość1 ,wartość2) ), nie będziesz mógł 
-- dynamicznie dodać nowych wartości do listy permission_name za pomocą aplikacji.

-- jeżeli permission_name jest unique w tabeli system_permissions to czy permission_id musi też być unique w tabeli role_permissions?
-- Nie, kolumna permission_id w tabeli role_permissions nie musi być unikalna, nawet jeśli permission_name jest unikalna w tabeli system_permissions.

CREATE TABLE system_permissions (
    permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    permission_name TEXT NOT NULL UNIQUE CHECK (
        permission_name IN ( -- MODYFIKOWANE TYLKO NA POZIOMIE KODU SQL PRZEZ KLAUZULĘ CHECK IN () 
            'zarzadzaj_wszystkimi_pacjentami',
            'przegladaj_przypisanych_pacjentow',
            'edytuj_przypisanych_pacjentow',
            'zarzadzaj_wizytami',
            'zarzadzaj_swoimi_wizytami',
            'zarzadzaj_pracownikami',
            'zarzadzaj_rolami_i_uprawnieniami',
            'zarzadzaj_pomieszczeniami',
            'zarzadzaj_platnosciami',
            'przegladaj_swoj_kalendarz',
            'zarzadzaj_swoim_kalendarzem',
            'przegladaj_kalendarz_placowki',
            'zarzadzaj_spotkaniami_wewnetrznymi',
            'zarzadzaj_typami_spotkan_wewnetrznych',
            'zarzadzaj_uslugami',
            'zarzadzaj_specjalnosciami',
            'przegladaj_diagnozy',
            'zarzadzaj_diagnozami',
            'przegladaj_recepty',
            'zarzadzaj_receptami',
            'zarzadzaj_typami_formularzy',
            'zarzadzaj_formularzami_pacjentow'
        )
    )
);



-- 4.
CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Główne pole identyfikatora roli, automatycznie zwiększane.

    role_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (role_name GLOB '[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]*')
    -- Nazwa roli musi być unikalna i nie może być pusta, musi zawierać tylko duże i małe litery (w tym polskie znaki) z spacją
    -- przewidziane nazwy roli: Administrator, Recepcjonista, Psychiatra, Psycholog kliniczny, Psychoterapeuta, PsychopedagogTerapeuta uzależnień, 
    -- Dietetyk kliniczny, Informatyk, Księgowy, Kierownik
);

    -- W SQLite GLOB w definicji tabeli (w ramach CHECK) jest nieprawidłowym podejściem. W SQLite, CHECK może obsługiwać tylko proste warunki logiczne 
    -- (np. >, <, =, IS NULL) i nie obsługuje zaawansowanych wyrażeń takich jak GLOB w kontekście sprawdzania wartości w definicji tabeli.  
    -- Rozwiązanie w SQL dla SQLite.Możesz skorzystać z CHECK z ograniczeniami, które są obsługiwane przez SQLite, a następnie przenieść bardziej 
    -- zaawansowaną walidację na poziom aplikacji.

    -- first_name TEXT NOT NULL CHECK (
    --     first_name GLOB '[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]*' 

    -- service_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(service_type) > 0)
    -- SQLite nie pozwala na jednoczesne użycie klauzul UNIQUE i CHECK dla jednej kolumny w takiej kombinacji. Dzieje się tak, ponieważ UNIQUE i CHECK to
    -- różne ograniczenia i SQLite oczekuje, że będą zapisane oddzielnie.

    -- Możesz jawnie ustawić kolację NOCASE dla konkretnej kolumny w momencie tworzenia tabeli:
    -- CREATE TABLE przyklad ( tekst TEXT COLLATE NOCASE UNIQUE); W tym przypadku kolumna tekst będzie ignorować wielkość liter zarówno dla porównań, 
    -- jak i ograniczenia UNIQUE. Wartości takie jak Przykład i PRZYKŁAD będą traktowane jako identyczne.


-- 5.
CREATE TABLE services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(service_type) > 0),
    duration_minutes INTEGER NOT NULL CHECK (
        duration_minutes BETWEEN 1 AND 300
    ),
    service_price INTEGER NOT NULL CHECK (
        service_price BETWEEN 1 AND 500
    )
);


-- 6.
CREATE TABLE specialties (
    specialty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (specialty_name GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
);

-- 7. 
CREATE TABLE meeting_types (
    meeting_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (meeting_type GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\]*')
);

--8. 
CREATE TABLE room_types (
    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (room_type GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
);

-- 9.
CREATE TABLE form_types (
    form_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (form_name GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.,/\\]*')
);

-- 10. TABELA PODRZĘDNA
CREATE TABLE employee_specialties (
    employee_specialty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    specialty_id INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (specialty_id) REFERENCES specialties(specialty_id) ON DELETE CASCADE,
    UNIQUE (employee_id, specialty_id)
);

-- ON DELETE CASCADE Jeśli usuniesz rekord pracownika z tabeli employees, to automatycznie zostaną usunięte 
-- wszystkie rekordy w tabeli PODRZĘDNEJ employee_specialties powiązane z tym employee_id.

-- NIE TRZEBA DODAWAĆ WALIDACJI W TABELACH NADRZĘDNYCH employees i specialties ponieważ

-- 11. 
CREATE TABLE employee_services (
    employee_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE,
    UNIQUE (employee_id, service_id)
);


-- 12. 
CREATE TABLE role_permissions (
    role_permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES system_permissions(permission_id) ON DELETE CASCADE,
    UNIQUE (role_id, permission_id)
);


-- 13. 
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
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT ON UPDATE CASCADE
     -- Automatyczne zarządzanie kluczem obcym
);

-- 14.
CREATE TABLE assigned_patients (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_patient_id INTEGER NOT NULL,
    fk_user_id INTEGER NOT NULL,
    FOREIGN KEY (fk_patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_user_id) REFERENCES users_accounts(user_id) ON DELETE CASCADE,
    UNIQUE (fk_patient_id, fk_user_id)
);

-- 15.
CREATE TABLE rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number INTEGER NOT NULL UNIQUE CHECK (room_number BETWEEN 0 AND 100),
    floor INTEGER NOT NULL CHECK (floor BETWEEN 0 AND 2),
    fk_room_type_id INTEGER,
    FOREIGN KEY (fk_room_type_id) REFERENCES room_types(room_type_id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- 16. 
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_patient_id INTEGER NOT NULL,
    fk_employee_id INTEGER NOT NULL,
    fk_service_id INTEGER NOT NULL,
    fk_room_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL CHECK (
        appointment_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]'
    ), -- Format daty YYYY-MM-DD HH:MM
    appointment_status TEXT NOT NULL CHECK (
        appointment_status GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.\\/]*'
    ),
    notes TEXT, -- Notatki bez walidacji
    FOREIGN KEY (fk_patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (fk_employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (fk_service_id) REFERENCES services(service_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE (fk_patient_id, appointment_date), -- Zapobiega powtórzeniom pacjenta i daty wizyty
    UNIQUE (fk_room_id, appointment_date) -- Zapobiega powtórzeniom pokoju i daty wizyty
);

-- 17. 
CREATE TABLE diagnoses (
    diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator diagnozy
    appointment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do wizyt
    description TEXT NOT NULL CHECK (
        description GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ()-:.\\/]*'
    ), -- Walidacja na małe i duże litery z polskimi znakami
    icd11_code TEXT NOT NULL CHECK (
        icd11_code GLOB '[A-Z][0-9][0-9](\\.[0-9])?'
    ), -- Walidacja kodu ICD-11 (np. F32.2)
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    ON DELETE SET NULL ON UPDATE CASCADE -- Optymalna obsługa klucza obcego
);

-- 18. 
CREATE TABLE prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator recepty
    appointment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do wizyt
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
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    ON DELETE SET NULL ON UPDATE CASCADE -- Optymalna obsługa klucza obcego
);

-- 19. NIE STWORZONO MODELU CRUD
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator płatności
    appointment_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do wizyt
    payment_date TEXT NOT NULL CHECK (
        payment_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
    ), -- Walidacja formatu daty YYYY-MM-DD
    service_price REAL NOT NULL CHECK (
        service_price IN (150, 170, 180, 200, 250, 300)
    ), -- Tylko określone wartości ceny
    payment_method TEXT NOT NULL CHECK (
        payment_method IN ('Gotówka', 'Karta', 'Przelew', 'Blik')
    ), -- Tylko najważniejsze metody płatności
    payment_status TEXT NOT NULL CHECK (
        payment_status IN ('Opłacona', 'Oczekująca', 'Anulowana', 'Odrzucona')
    ), -- Tylko najważniejsze statusy płatności
    transaction_id TEXT, -- Może być NULL
    notes TEXT, -- Brak walidacji, pole opcjonalne
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    ON DELETE SET NULL ON UPDATE CASCADE -- Optymalna obsługa klucza obcego
);

-- 20. 
CREATE TABLE internal_meetings (
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator spotkania
    fk_meeting_type_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do typu spotkania
    fk_room_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do pokoju
    start_meeting_date TEXT NOT NULL CHECK (
        start_meeting_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]'
    ), -- Format daty YYYY-MM-DD
    end_meeting_date TEXT NOT NULL CHECK (
       end_meeting_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]'
    ), -- Format daty YYYY-MM-DD
    notes TEXT, -- Notatki bez walidacji
    internal_meeting_status TEXT NOT NULL CHECK ( 
        internal_meeting_status GLOB '[a-zA-ZĄąĆćĘęŁłŃńÓóŚśŹźŻż ]*'
    ), -- Status tylko Zaplanowana, Zrealizowana, Odwołana
    FOREIGN KEY (fk_meeting_type_id) REFERENCES meeting_types(meeting_type_id)
    ON DELETE RESTRICT ON UPDATE CASCADE, -- Ograniczenie usuwania typu spotkania
    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id)
    ON DELETE SET NULL ON UPDATE CASCADE -- Pokój może zostać ustawiony jako NULL
);

-- 21. 
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
    ON DELETE CASCADE ON UPDATE CASCADE, -- Automatyczne zarządzanie usuwaniem/aktualizacją spotkań
    FOREIGN KEY (fk_employee_id) REFERENCES employees(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE -- Automatyczne zarządzanie usuwaniem/aktualizacją pracowników
);

-- 22. 
CREATE TABLE room_reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator rezerwacji
    fk_room_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do pokoju
    reservation_date TEXT NOT NULL CHECK (
        reservation_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
    ), -- Format daty YYYY-MM-DD
    reservation_time TEXT NOT NULL CHECK (
        reservation_time GLOB '[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]'
    ),
    fk_appointment_id INTEGER, -- Może być NULL (opcjonalne pole)
    fk_meeting_id INTEGER, -- Może być NULL (opcjonalne pole)
    FOREIGN KEY (fk_room_id) REFERENCES rooms(room_id)
    ON DELETE CASCADE ON UPDATE CASCADE, -- Automatyczne zarządzanie relacją pokoju
    FOREIGN KEY (fk_appointment_id) REFERENCES appointments(appointment_id)
    ON DELETE SET NULL ON UPDATE CASCADE, -- Opcjonalność: NULL, jeśli wizyta zostanie usunięta
    FOREIGN KEY (fk_meeting_id) REFERENCES internal_meetings(meeting_id)
    ON DELETE SET NULL ON UPDATE CASCADE -- Opcjonalność: NULL, jeśli spotkanie zostanie usunięte
);



-- 23. NIE STWORZONO MODELU CRUD
CREATE TABLE employee_schedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator harmonogramu
    employee_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do tabeli pracowników
    work_date TEXT NOT NULL CHECK (
        work_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
    ), -- Format daty YYYY-MM-DD
    reservation_time TEXT NOT NULL CHECK (
        reservation_time GLOB '[0-2][0-9]:[0-5][0-9]'
    ), -- Format czasu HH:MM
    end_time TEXT NOT NULL CHECK (
        end_time GLOB '[0-2][0-9]:[0-5][0-9]'
    ), -- Format czasu HH:MM
    notes TEXT, -- Pole opcjonalne, brak dodatkowej walidacji
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE -- Automatyczne zarządzanie relacją z tabelą employees
);

--24. 
CREATE TABLE patient_forms (
    patient_form_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator formularza
    fk_patient_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do pacjenta
    fk_form_type_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do typu formularza
    submission_date TEXT NOT NULL CHECK (
        submission_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
    ), -- Format daty YYYY-MM-DD
    content TEXT, -- Pole opcjonalne, brak dodatkowej walidacji
    FOREIGN KEY (fk_patient_id) REFERENCES patients(patient_id)
    ON DELETE CASCADE ON UPDATE CASCADE, -- Automatyczne zarządzanie relacją z tabelą patients
    FOREIGN KEY (fk_form_type_id) REFERENCES form_types(form_type_id)
    ON DELETE RESTRICT ON UPDATE CASCADE -- Usunięcie typu formularza nie powinno być możliwe, jeśli istnieją powiązane formularze
);

--25. NIE STWORZONO MODELU CRUD
CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikalny identyfikator wiadomości
    sender_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do wysyłającego (pracownika)
    recipient_id INTEGER NOT NULL, -- Klucz obcy odwołujący się do odbiorcy (pracownika)
    message_content TEXT NOT NULL, -- Treść wiadomości, brak dodatkowej walidacji
    send_date TEXT NOT NULL CHECK (
        send_date GLOB '[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'
    ), -- Format daty i czasu YYYY-MM-DD HH:MM:SS
    read_status INTEGER NOT NULL CHECK (
        read_status IN (0, 1)
    ), -- Status odczytania: 0 = Nieodczytane, 1 = Odczytane
    FOREIGN KEY (sender_id) REFERENCES employees(employee_id)
    ON DELETE SET NULL ON UPDATE CASCADE, -- Automatyczne zarządzanie relacją z wysyłającym
    FOREIGN KEY (recipient_id) REFERENCES employees(employee_id)
    ON DELETE SET NULL ON UPDATE CASCADE -- Automatyczne zarządzanie relacją z odbiorcą
);



-- FOREIGN KEY (occupied_by) REFERENCES staff(staff_id)
-- KLUCZ OBCY (kolumna tabeli 1) ODNOSI SIĘ DO tabela 2(kolumna tabeli 2)

-- occupied_by: Jest kolumną w tabeli (np. rooms), w której przechowywany jest identyfikator pracownika (staff_id).
-- REFERENCES staff(staff_id): Relacja wskazuje, że wartości w kolumnie occupied_by muszą istnieć w kolumnie staff_id tabeli staff.