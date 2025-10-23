# test_model_employee_specialties.py

"""
Testuje model EmployeeSpecialties, weryfikując wszystkie operacje CRUD
oraz walidacje przy użyciu testowej bazy SQLite w pamięci.
"""

import os
import pytest
from controllers.database_controller import DatabaseController
from models.employee_specialties import EmployeeSpecialties
from models.specialties import Specialties
from models.employees import Employees

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_database")
def setup_database_fixture():
    """
    2. Wykonanie fixture: Pytest wywołuje funkcję setup_database_fixture przed rozpoczęciem kodu testu:

    Kod fixture:
        Tworzy db_controller i nawiązuje połączenie z bazą.
        Tworzy tabelę form_types.
        Zwraca db_controller (za pomocą yield), co pozwala testowi korzystać z tego obiektu.

    3. Wykonanie testu: Dopiero po zakończeniu kodu przed yield, pytest przekazuje wynik fixture (db_controller) do testu:
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Tworzenie tabeli `employees`
    employees_model = Employees(db_controller)
    employees_model.create_table()

    # Tworzenie tabeli `specialties`
    specialties_model = Specialties(db_controller)
    specialties_model.create_table()

    # Tworzenie tabeli `form_types`
    employee_specialties_model = EmployeeSpecialties(db_controller)
    employee_specialties_model.create_table()


    yield db_controller

    # Czyszczenie danych po każdym teście
    if db_controller.connection:
        if db_controller.table_exists("employee_specialties"):
            db_controller.connection.execute("DELETE FROM employee_specialties")
        if db_controller.table_exists("employees"):
            db_controller.connection.execute("DELETE FROM employees")
        if db_controller.table_exists("specialties"):
            db_controller.connection.execute("DELETE FROM specialties")
    db_controller.close_connection()



# +-+-+-+- Testy metod dodawania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Testy metod dodawania rekordów
def test_add_employee_specialty_valid_data(setup_database):
    """
    Testuje dodanie poprawnego rekordu do tabeli `employee_specialties`.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO specialties (specialty_id, specialty_name)
    VALUES (1, 'Kardiologia')
    """)

    # Wykonanie testu
    employee_specialties_model.add_employee_specialty(1, 1)

    # Walidacja wyniku
    records = employee_specialties_model.get_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1

    # Czyszczenie danych testowych
    db_controller.connection.execute("DELETE FROM employee_specialties WHERE employee_specialty_id = 1")
    db_controller.connection.execute("DELETE FROM employees WHERE employee_id = 1")
    db_controller.connection.execute("DELETE FROM specialties WHERE specialty_id = 1")




def test_add_employee_specialty_invalid_data(setup_database):
    """
    Testuje dodanie niepoprawnego rekordu do tabeli `employee_specialties`.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO specialties (specialty_id, specialty_name)
    VALUES (1, 'Kardiologia')
    """)
    

    # Próba dodania rekordu z nieistniejącym employee_id
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        employee_specialties_model.add_employee_specialty(99, 1)

    # Czyszczenie danych testowych
    db_controller.connection.execute("DELETE FROM specialties WHERE specialty_id = 1")





def test_add_employee_specialty_duplicate(setup_database):
    """
    Testuje dodanie zduplikowanego rekordu specjalizacji pracownika.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Kardiologia"))

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie specjalizacji pracownika
    employee_specialties_model.add_employee_specialty(1, 1)

    # Próba dodania zduplikowanego rekordu
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i specialty_id=1 już istnieje."):
        employee_specialties_model.add_employee_specialty(1, 1)



def test_add_employee_specialty_by_names_valid_data(setup_database):
    """
    Testuje dodanie rekordu na podstawie imienia, nazwiska i nazwy specjalizacji.
    """

    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Kardiologia"))

    # Dodanie specjalizacji
    employee_specialties_model.add_employee_specialty_by_names("Maria", "Nowak", "Kardiologia")

    # Walidacja rekordu
    records = employee_specialties_model.get_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1



def test_add_employee_specialty_by_names_invalid_data(setup_database):
    """
    Testuje przypadki niepoprawnych danych przy dodawaniu rekordu
    na podstawie imienia, nazwiska i nazwy specjalizacji.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Niepoprawne imię
    with pytest.raises(ValueError, match="Imię nie może być puste."):
        employee_specialties_model.add_employee_specialty_by_names("", "Kowalski", "Kardiologia")

    # Niepoprawne nazwisko
    with pytest.raises(ValueError, match="Nazwisko nie może być puste."):
        employee_specialties_model.add_employee_specialty_by_names("Jan", "", "Kardiologia")

    # Niepoprawna specjalizacja
    with pytest.raises(ValueError, match="Nazwa specjalizacji nie może być pusta."):
        employee_specialties_model.add_employee_specialty_by_names("Jan", "Kowalski", "")


def test_add_employee_specialty_by_names_duplicate(setup_database):
    """
    Testuje dodanie zduplikowanego rekordu na podstawie imienia, nazwiska i nazwy specjalizacji.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Kardiologia"))

    # Dodanie rekordu za pomocą nazw
    employee_specialties_model.add_employee_specialty_by_names("Jan", "Kowalski", "Kardiologia")

    # Próba dodania zduplikowanego rekordu
    with pytest.raises(ValueError, match="Kombinacja employee_id=1 i specialty_id=1 już istnieje."):
        employee_specialties_model.add_employee_specialty_by_names("Jan", "Kowalski", "Kardiologia")



 # +-+-+-+- Testy metod aktualizacji rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



def test_update_record_by_id_valid_data(setup_database):
    """
    Testuje poprawną aktualizację rekordu w tabeli `employee_specialties`.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO specialties (specialty_id, specialty_name)
    VALUES (1, 'Kardiologia')
    """)
    employee_specialties_model.add_employee_specialty(1, 1)

    # Aktualizacja rekordu
    employee_specialties_model.update_record_by_id(1, new_employee_id=1, new_specialty_id=1)

    # Walidacja wyniku
    records = employee_specialties_model.get_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1

    # Czyszczenie danych testowych
    db_controller.connection.execute("DELETE FROM employee_specialties WHERE employee_specialty_id = 1")
    db_controller.connection.execute("DELETE FROM employees WHERE employee_id = 1")
    db_controller.connection.execute("DELETE FROM specialties WHERE specialty_id = 1")




def test_update_record_by_id_invalid_data(setup_database):
    """
    Testuje poprawną aktualizację rekordu na podstawie employee_specialty_id.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, "Maria", "Nowak", "maria.nosak@example.com", "111222333", "Psycholog kliniczny", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Psychiatra dorosłych"))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (2, "Psychiatra dzieci i młodzieży"))

    # Dodanie specjalizacji pracownika
    employee_specialties_model.add_employee_specialty(1, 1)

    # Przypadek 1: Aktualizacja z nieistniejącym `new_employee_id`
    with pytest.raises(ValueError, match="Pracownik o ID 99 nie istnieje."):
        employee_specialties_model.update_record_by_id(
            employee_specialty_id=1,
            new_employee_id=99,  # Nieprawidłowy `employee_id`
            new_specialty_id=1
        )

    # Przypadek 2: Aktualizacja z nieistniejącym `new_specialty_id`
    with pytest.raises(ValueError, match="Specjalizacja o ID 99 nie istnieje."):
        employee_specialties_model.update_record_by_id(
            employee_specialty_id=1,
            new_employee_id=1,
            new_specialty_id=99  # Nieprawidłowy `specialty_id`
        )

    # Przypadek 3: Aktualizacja z nieistniejącym `employee_specialty_id`
    with pytest.raises(KeyError, match="Rekord o ID 99 nie istnieje."):
        employee_specialties_model.update_record_by_id(
            employee_specialty_id=99,  # Nieprawidłowy `employee_specialty_id`
            new_employee_id=1,
            new_specialty_id=1
        )

    # Przypadek 4: Brak nowych wartości do aktualizacji
    with pytest.raises(ValueError, match="Nie podano nowych wartości do aktualizacji."):
        employee_specialties_model.update_record_by_id(
            employee_specialty_id=1
            # Brak `new_employee_id` i `new_specialty_id`
        )




def test_update_record_by_id_no_changes(setup_database):
    """
    Testuje przypadek, gdy nie podano nowych wartości do aktualizacji w update_record_by_id.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    with pytest.raises(ValueError, match="Nie podano nowych wartości do aktualizacji."):
        employee_specialties_model.update_record_by_id(employee_specialty_id=1)




def test_update_record_by_name_using_names_success(setup_database):
    """
    Testuje poprawną aktualizację rekordu na podstawie nazw (imienia, nazwiska i specjalizacji).
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Psychiatra dorosłych"))

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, "Adam", "Kowalski", "maria.notak@example.com", "187654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (2, "Psychiatra dzieci i młodzieży"))

    # Dodanie specjalizacji pracownika
    employee_specialties_model.add_employee_specialty(1, 1)

    # Aktualizacja rekordu
    employee_specialties_model.update_record_by_name_using_names(
        first_name="Maria",
        last_name="Nowak",
        specialty_name="Psychiatra dorosłych",
        new_first_name="Adam",
        new_last_name="Kowalski",
        new_specialty_name="Psychiatra dzieci i młodzieży"
    )

    # Pobranie zaktualizowanego rekordu
    cursor = db_controller.connection.execute(
        """
        SELECT es.employee_specialty_id, e.first_name, e.last_name, s.specialty_name AS specialty_name
        FROM employee_specialties es
        JOIN employees e ON es.employee_id = e.employee_id
        JOIN specialties s ON es.specialty_id = s.specialty_id
        WHERE es.employee_specialty_id = 1
        """
    )
    record = cursor.fetchone()

    # Sprawdzenie, czy rekord został zaktualizowany poprawnie
    assert record is not None
    assert record["employee_specialty_id"] == 1
    assert record["first_name"] == "Adam"  # Nowe imię
    assert record["last_name"] == "Kowalski"  # Nowe nazwisko
    assert record["specialty_name"] == "Psychiatra dzieci i młodzieży"  # Nowa specjalizacja


def test_update_record_by_name_using_id_valid_data(setup_database):
    """
    Testuje poprawną aktualizację rekordu na podstawie nazw i ID.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (2, "Psychiatra dzieci i młodzieży"))

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Jan", "Kowalski", "maria.nowak@exqmple.com", "987654391", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Kardiologia"))

    # Dodanie specjalizacji pracownika
    employee_specialties_model.add_employee_specialty(1, 1)

    # Aktualizacja rekordu
    employee_specialties_model.update_record_by_name_using_id(
        first_name="Jan",
        last_name="Kowalski",
        specialty_name="Kardiologia",
        employee_id=2,
        specialty_id=2
    )

    # Pobranie zaktualizowanego rekordu
    cursor = db_controller.connection.execute("SELECT * FROM employee_specialties WHERE employee_specialty_id = 1")
    record = cursor.fetchone()

    # Sprawdzenie, czy rekord został zaktualizowany
    assert record is not None
    assert record["employee_id"] == 2
    assert record["specialty_id"] == 2


 # +-+-+-+- Testy metod usuwania rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



# Testy metod usuwania rekordów
def test_delete_employee_specialty(setup_database):
    """
    Testuje usuwanie rekordu specjalizacji pracownika.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Psychiatra dorosłych"))

    # Dodanie specjalizacji pracownika
    employee_specialties_model.add_employee_specialty(1, 1)

    # Usunięcie rekordu
    employee_specialties_model.delete_employee_specialty(1)

    # Walidacja usunięcia
    records = employee_specialties_model.get_records()
    assert len(records) == 0



# Testy metod usuwania rekordów na podstawie imienia, nazwiska i nazwy specjalizacji
def test_delete_record_by_name(setup_database):
    """
    Testuje usuwanie rekordu na podstawie imienia, nazwiska i nazwy specjalizacji.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Psychiatra dzieci i młodzieży"))

    # Dodanie specjalizacji pracownika
    employee_specialties_model.add_employee_specialty(1, 1)

    # Usunięcie rekordu na podstawie nazw
    employee_specialties_model.delete_record_by_name("Maria", "Nowak", "Psychiatra dzieci i młodzieży")

    # Walidacja usunięcia
    records =  employee_specialties_model.get_records()
    assert len(records) == 0



def test_delete_record_by_name_nonexistent(setup_database):
    """
    Testuje przypadek usuwania rekordu dla nieistniejących nazw.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute("""
    INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (1, 'Jan', 'Kowalski', 'jan.kowalski@example.com', '123456789', 'Psychiatra', 1)
    """)
    db_controller.connection.execute("""
    INSERT INTO specialties (specialty_id, specialty_name)
    VALUES (1, 'Kardiologia')
    """)

    # Próba usunięcia rekordu, który nie istnieje
    with pytest.raises(KeyError, match="Rekord dla Jan Kowalski z \'Kardiologia\' nie istnieje."):
        employee_specialties_model.delete_record_by_name("Jan", "Kowalski", "Kardiologia")



# +-+-+-+- Testy metod pobierania i rekordu -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def test_get_records_with_various_filters_and_names(setup_database):
    """
    Testuje pobieranie rekordów z tabeli `employee_specialties` z różnymi typami filtrów.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychoterapeuta", 1))

    db_controller.connection.execute("""
    INSERT INTO employees
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties
    (specialty_id, specialty_name)
    VALUES (?, ?)
    """, (1, "Psychiatra dorosłych"))

    db_controller.connection.execute("""
    INSERT INTO specialties
    (specialty_id, specialty_name)
    VALUES (?, ?)
    """, (2, "Psychologia kliniczna dorosłych"))

    # Dodanie danych testowych do tabeli employee_specialties
    db_controller.connection.execute("""
    INSERT INTO employee_specialties
    (employee_specialty_id, employee_id, specialty_id)
    VALUES (?, ?, ?)
    """, (1, 1, 1))
    db_controller.connection.execute("""
    INSERT INTO employee_specialties
    (employee_specialty_id, employee_id, specialty_id)
    VALUES (?, ?, ?)
    """, (2, 2, 2))

    # Testowanie pobierania rekordów
    records = employee_specialties_model.get_records()
    assert len(records) == 2
    assert records[0]["employee_id"] == 1
    assert records[1]["employee_id"] == 2

    # Test filtrowania po `employee_id`
    records_filtered = employee_specialties_model.get_records(
        filters=[{"column": "employee_id", "operator": "=", "value": 1}]
    )
    assert len(records_filtered) == 1
    assert records_filtered[0]["employee_id"] == 1

    # Test filtrowania po `specialty_id`
    records_specialty_filtered = employee_specialties_model.get_records(
        filters=[{"column": "specialty_id", "operator": "=", "value": 2}]
    )
    assert len(records_specialty_filtered) == 1
    assert records_specialty_filtered[0]["specialty_id"] == 2


def test_get_records_with_invalid_filters(setup_database):
    """
    Testuje reakcję metody na niepoprawne filtry.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Psychiatra dzieci i młodzieży"))
    employee_specialties_model.add_employee_specialty(1, 1)

    # Test 1: Nieistniejąca kolumna
    filters_invalid_column = [{"column": "non_existing_column", "operator": "=", "value": 1}]
    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: non_existing_column. Dozwolone kolumny: employee_specialty_id, employee_id, specialty_id"):
        employee_specialties_model.get_records(filters=filters_invalid_column)

    # Test 2: Nieobsługiwany operator
    filters_invalid_operator = [{"column": "employee_id", "operator": "NON_EXISTING_OPERATOR", "value": 1}]
    with pytest.raises(ValueError, match="Nieobsługiwany operator: NON_EXISTING_OPERATOR"):
        employee_specialties_model.get_records(filters=filters_invalid_operator)

    # Test 3: Brak wartości w filtrze
    filters_missing_value = [{"column": "employee_id", "operator": "=", "value": None}]
    with pytest.raises(ValueError, match="Filtr zawiera brakującą wartość dla kolumny: employee_id"):
        employee_specialties_model.get_records(filters=filters_missing_value)

    # Test 4: Nieistniejące wartości w bazie danych
    filters_non_existing_value = [{"column": "employee_id", "operator": "=", "value": 999}]
    records = employee_specialties_model.get_records(filters=filters_non_existing_value)
    assert len(records) == 0  # Spodziewamy się pustego wyniku



def test_get_records_table_not_exist(setup_database):
    """
    Testuje próbę pobrania rekordów z nieistniejącej tabeli.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Usuń tabelę, aby sprawdzić obsługę błędu
    db_controller.connection.execute("DROP TABLE employee_specialties")

    with pytest.raises(RuntimeError, match="Tabela 'employee_specialties' nie istnieje w bazie danych."):
        employee_specialties_model.get_records()




def test_get_records_with_names_invalid_table(setup_database):
    """
    Testuje próbę pobrania rekordów z tabeli `employee_specialties` z nazwami, gdy tabela nie istnieje.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Usuń tabelę
    db_controller.connection.execute("DROP TABLE employee_specialties")

    with pytest.raises(RuntimeError, match="Tabela 'employee_specialties' nie istnieje w bazie danych."):
        employee_specialties_model.get_records_with_names()




def test_get_employee_id_valid_data(setup_database):
    """
    Testuje poprawne pobranie ID pracownika na podstawie imienia i nazwiska.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Pobranie ID
    employee_id = employee_specialties_model.get_employee_id("Maria", "Nowak")

    # Walidacja
    assert employee_id == 1


def test_get_employee_id_not_found(setup_database):
    """
    Testuje próbę pobrania ID pracownika, który nie istnieje.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    with pytest.raises(ValueError, match="Pracownik Jan Kowalski nie istnieje."):
        employee_specialties_model.get_employee_id("Jan", "Kowalski")



def test_get_specialty_id_valid_data(setup_database):
    """
    Testuje poprawne pobranie ID specjalizacji na podstawie nazwy.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie danych testowych
    db_controller.connection.execute(
        "INSERT INTO specialties (specialty_id, specialty_name) VALUES (?, ?)", (1, "Kardiologia")
    )

    # Pobranie ID
    specialty_id = employee_specialties_model.get_specialty_id("Kardiologia")

    # Walidacja
    assert specialty_id == 1


def test_get_specialty_id_not_found(setup_database):
    """
    Testuje próbę pobrania ID specjalizacji, która nie istnieje.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    with pytest.raises(ValueError, match="Specjalizacja 'Kardiologia' nie istnieje."):
        employee_specialties_model.get_specialty_id("Kardiologia")



def test_missing_dependencies(setup_database):
    """
    Testuje brakujące zależności między tabelami w modelu.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Próba dodania rekordu bez istniejącej specjalizacji
    with pytest.raises(ValueError, match="Specjalizacja o ID 1 nie istnieje."):
        employee_specialties_model.add_employee_specialty(employee_id=1, specialty_id=1)

    # Próba aktualizacji na brakującą zależność
    db_controller.connection.execute(
        "INSERT INTO specialties (specialty_id, specialty_name) VALUES (?, ?)", (2, "Neurologia")
    )
    employee_specialties_model.add_employee_specialty(employee_id=1, specialty_id=2)

    with pytest.raises(ValueError, match="Specjalizacja o ID 1 nie istnieje."):
        employee_specialties_model.update_record_by_id(
            employee_specialty_id=1, new_employee_id=1, new_specialty_id=1
        )


def test_sorting_records(setup_database):
    """
    Testuje sortowanie rekordów w tabeli `employee_specialties`.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)


# Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Jan", "Kowalski", "jan.kowalski@example.com", "123456789", "Psychoterapeuta", 1))

    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    # Dodanie przykładowych danych do tabeli specialties
    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (1, "Psychiatra dorosłych"))

    db_controller.connection.execute("""
    INSERT INTO specialties 
    (specialty_id, specialty_name) 
    VALUES (?, ?)
    """, (2, "Psychologia kliniczna dorosłych"))


    # Dodanie danych testowych
    db_controller.connection.execute(
        "INSERT INTO employee_specialties (employee_specialty_id, employee_id, specialty_id) VALUES (?, ?, ?)",
        (1, 1, 2)
    )
    db_controller.connection.execute(
        "INSERT INTO employee_specialties (employee_specialty_id, employee_id, specialty_id) VALUES (?, ?, ?)",
        (2, 2, 1)
    )

    # Sortowanie rosnące po `employee_id`
    records_asc = employee_specialties_model.get_records(sort_by=[("employee_id", "ASC")])
    assert len(records_asc) == 2
    assert records_asc[0]["employee_id"] == 1
    assert records_asc[1]["employee_id"] == 2

    # Sortowanie malejące po `specialty_id`
    records_desc = employee_specialties_model.get_records(sort_by=[("specialty_id", "DESC")])
    assert len(records_desc) == 2
    assert records_desc[0]["specialty_id"] == 2
    assert records_desc[1]["specialty_id"] == 1


def test_add_delete_add_same_record(setup_database):
    """
    Testuje dodanie, usunięcie i ponowne dodanie tego samego rekordu.
    """
    db_controller = setup_database
    employee_specialties_model = EmployeeSpecialties(db_controller)

    # Dodanie wstępnych danych
    # Dodanie przykładowych danych do tabeli employees
    db_controller.connection.execute("""
    INSERT INTO employees 
    (employee_id, first_name, last_name, email, phone, profession, is_medical_staff) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Maria", "Nowak", "maria.nowak@example.com", "987654321", "Psychiatra", 1))

    db_controller.connection.execute(
        "INSERT INTO specialties (specialty_id, specialty_name) VALUES (?, ?)", (1, "Kardiologia")
    )

    # Dodanie rekordu po raz pierwszy
    employee_specialties_model.add_employee_specialty(employee_id=1, specialty_id=1)
    records = employee_specialties_model.get_records()
    assert len(records) == 1
    assert records[0]["employee_id"] == 1
    assert records[0]["specialty_id"] == 1

    # Usunięcie rekordu
    employee_specialties_model.delete_employee_specialty(employee_specialty_id=records[0]["employee_specialty_id"])
    records_after_delete = employee_specialties_model.get_records()
    assert len(records_after_delete) == 0

    # Ponowne dodanie tego samego rekordu
    employee_specialties_model.add_employee_specialty(employee_id=1, specialty_id=1)
    records_after_readd = employee_specialties_model.get_records()
    assert len(records_after_readd) == 1
    assert records_after_readd[0]["employee_id"] == 1
    assert records_after_readd[0]["specialty_id"] == 1
