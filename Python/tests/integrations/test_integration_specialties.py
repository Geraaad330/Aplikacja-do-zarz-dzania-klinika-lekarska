# test_integration_specialties.py


"""
Użycie kontrolera SpecialtiesController
Na prawym ekranie kontroler (SpecialtiesController) jest tworzony raz w konfiguracji testowej:

    specialties_controller = SpecialtiesController(db_controller)

Testy odwołują się do kontrolera, a nie bezpośrednio do modelu:

    controller.add_specialty("Psychiatra dorosłych")

Kontroler zarządza modelem w tle, co eliminuje potrzebę bezpośredniego odwoływania się do modelu w testach.
Dlaczego nie musisz wywoływać kontrolera w każdym teście?

Kontroler został stworzony raz w setupie testowym i jest używany w testach jako centralny punkt dostępu.
Kontroler przejmuje odpowiedzialność za logikę biznesową i deleguje zadania do modelu.

"""




import os
import pytest
from controllers.database_controller import DatabaseController
from controllers.specialties_controller import SpecialtiesController
from models.employees import Employees
from models.specialties import Specialties

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_specialties_controller")
def setup_specialties_controller_fixture():
    """
    Fixture konfiguruje bazę danych oraz instancję kontrolera `SpecialtiesController`.
    Czyszczenie danych odbywa się przed każdym testem.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    specialties_controller = SpecialtiesController(db_controller)
    specialties_controller.create_table()

    # Tworzenie tabeli `specialties`
    specialties_model = Specialties(db_controller)
    specialties_model.create_table()

        # Tworzenie tabeli `employees`
    employees_model = Employees(db_controller)
    employees_model.create_table()

    # Tworzenie tabeli `employee_specialties`
    db_controller.connection.execute("""
    CREATE TABLE IF NOT EXISTS employee_specialties (
        employee_id INTEGER,
        specialty_id INTEGER,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(specialty_id) REFERENCES specialties(specialty_id)
    )
    """)
    db_controller.connection.commit()

    # Czyszczenie danych przed każdym testem
    db_controller.connection.execute("DELETE FROM employee_specialties")
    db_controller.connection.execute("DELETE FROM specialties")
    db_controller.connection.execute("DELETE FROM employees")
    db_controller.connection.commit()

    yield specialties_controller

    # Czyszczenie tabel po wszystkich testach
    if db_controller.connection is None:
        db_controller.connect_to_database()  # Otwieramy połączenie, jeśli zostało zamknięte
    # Czyszczenie tabel po wszystkich testach
    db_controller.connection.execute("DROP TABLE IF EXISTS employee_specialties")
    db_controller.connection.execute("DROP TABLE IF EXISTS specialties")
    db_controller.connection.execute("DROP TABLE IF EXISTS employees")
    db_controller.close_connection()

def test_add_specialty_with_valid_data(setup_specialties_controller):
    """
    Testuje dodawanie nowej specjalności z poprawnymi danymi.

    jeśli chcesz korzystać z metod kontrolera w swojej metodzie testowej, musisz odwoływać się do instancji kontrolera, która jest przypisana 
    do zmiennej, np. controller. W tym przypadku controller reprezentuje instancję klasy kontrolera (np. SpecialtiesController), która 
    udostępnia metody kontrolera.
    """
    # setup_specialties_controller jest kontrolerem przygotowanym przez fiksturę
    # controller = setup_specialties_controller -->> specialties_controller = SpecialtiesController(db_controller)
    controller = setup_specialties_controller

    # Dodanie nowej specjalności
    controller.add_specialty("Psychiatra dorosłych")

    specialties = controller.get_all_specialties()
    assert len(specialties) == 1
    assert specialties[0]["specialty_name"] == "Psychiatra dorosłych"

def test_add_specialty_with_invalid_data(setup_specialties_controller):
    """
    Testuje dodawanie nowej specjalności z niepoprawnymi danymi.
    """
    controller = setup_specialties_controller

    with pytest.raises(ValueError, match="Nazwa specjalności nie może być pusta."):
        controller.add_specialty("")

    with pytest.raises(ValueError, match="Nazwa specjalności musi mieć od 3 do 100 znaków."):
        controller.add_specialty("AB")



def test_update_specialty_with_valid_data(setup_specialties_controller):
    """
    Testuje aktualizację specjalności z poprawnymi danymi.
    """
    controller = setup_specialties_controller

    # Dodaje nową specjalność do tabeli specialties.
    controller.add_specialty("Psychiatra dorosłych")

    # controller.get_all_specialties() -->> Wywołuje metodę kontrolera, która zwraca wszystkie rekordy z tabeli specialties.
    # [0]: Pobiera pierwszy rekord (pierwszy element listy) i zapisuje go do zmiennej specialty -> przechowuje {"specialty_id": 1, "specialty_name": "Psychiatra dorosłych"}
    specialty = controller.get_all_specialties()[0]

    # Aktualizacja
    updates = {"specialty_name": "Psycholog kliniczny"}
    
    #specialty["specialty_id"]: Pobiera wartość klucza "specialty_id" z rekordu specialty. W powyższym przykładzie wartość to 1. 
    # updates: Zawiera dane, które mają zostać zaktualizowane w tabeli specialties.
    # Aktualizuje rekord o specialty_id = 1, zmieniając wartość "specialty_name" na "Psycholog kliniczny".
    controller.update_specialty(specialty["specialty_id"], updates)

    updated_specialty = controller.get_all_specialties()[0]
    assert updated_specialty["specialty_name"] == "Psycholog kliniczny"

def test_update_specialty_with_invalid_data(setup_specialties_controller):
    """
    Testuje aktualizację specjalności z niepoprawnymi danymi.
    """
    controller = setup_specialties_controller

    # Dodanie specjalności
    controller.add_specialty("Psychiatra dorosłych")
    specialty = controller.get_all_specialties()[0]

    with pytest.raises(ValueError, match="Nazwa specjalności nie może być pusta."):
        controller.update_specialty(specialty["specialty_id"], {"specialty_name": ""})


def test_update_nonexistent_specialty(setup_specialties_controller):
    """
    Testuje aktualizację rekordu, który nie istnieje.
    """
    controller = setup_specialties_controller

    updates = {"specialty_name": "Psycholog kliniczny kliniczny"}
    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.update_specialty(999, updates)






def test_delete_nonexistent_specialty(setup_specialties_controller):
    """
    Testuje usuwanie rekordu, który nie istnieje.
    """
    controller = setup_specialties_controller

    with pytest.raises(RuntimeError, match="Rekord o ID 999 nie istnieje."):
        controller.delete_specialty(999)


def test_delete_specialty(setup_specialties_controller):
    """
    Testuje usuwanie specjalności.
    """
    controller = setup_specialties_controller

    # Dodanie specjalności
    controller.add_specialty("Psychiatra dorosłych")
    specialty = controller.get_all_specialties()[0]

    # Usuwanie
    controller.delete_specialty(specialty["specialty_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM specialties").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_delete_specialty."



def test_full_crud_flow(setup_specialties_controller):
    """
    Testuje pełny przepływ CRUD: Dodanie, Pobranie, Aktualizacja, Usunięcie.
    """
    controller = setup_specialties_controller

    # Dodanie specjalności
    controller.add_specialty("Psychiatra dorosłych")
    specialty = controller.get_all_specialties()[0]
    assert specialty["specialty_name"] == "Psychiatra dorosłych"

    # Aktualizacja specjalności
    updates = {"specialty_name": "Psycholog kliniczny kliniczny"}
    controller.update_specialty(specialty["specialty_id"], updates)
    updated_specialty = controller.get_all_specialties()[0]
    assert updated_specialty["specialty_name"] == "Psycholog kliniczny kliniczny"

    # Usuwanie specjalności
    controller.delete_specialty(updated_specialty["specialty_id"])
    remaining = controller.db_controller.connection.execute("SELECT COUNT(*) FROM specialties").fetchone()[0]
    assert remaining == 0, "Dane nie zostały usunięte z metody test_full_crud_flow."


def test_get_specialties_with_filters(setup_specialties_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości filtracji.
    """
    controller = setup_specialties_controller

    # Dodanie danych
    controller.add_specialty("Psychiatra dzieci i młodzieży")
    controller.add_specialty("Psycholog kliniczny kliniczny")

    filters = [{"column": "specialty_name", "operator": "LIKE", "value": "Psychiatra%"}]
    results = controller.get_specialties_with_filters(filters=filters)

    assert len(results) == 1
    assert results[0]["specialty_name"] == "Psychiatra dzieci i młodzieży"


def test_get_specialties_with_sorting(setup_specialties_controller):
    """
    Testuje pobieranie danych z wykorzystaniem wszystkich możliwości sortowania.
    """
    controller = setup_specialties_controller

    # Dodanie danych
    controller.add_specialty("Psychiatra dzieci i młodzieży")
    controller.add_specialty("Psycholog kliniczny kliniczny")

    # Sortowanie alfabetyczne rosnąco
    results = controller.get_specialties_with_filters(sort_by=[("specialty_name", "ASC")])
    assert results[0]["specialty_name"] == "Psychiatra dzieci i młodzieży"

    # Sortowanie alfabetyczne malejąco
    results = controller.get_specialties_with_filters(sort_by=[("specialty_name", "DESC")])
    assert results[0]["specialty_name"] == "Psycholog kliniczny kliniczny"




def test_database_disconnection_handling_specialties(setup_specialties_controller):
    """
    Testuje obsługę błędów bazy danych przy rozłączeniu połączenia w tabeli `specialties`.
    """
    controller = setup_specialties_controller

    # Rozłączenie bazy danych
    controller.db_controller.close_connection()

    # Próba dodania specjalności po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.add_specialty("Psychiatra dorosłych")

    # Próba pobrania specjalności po rozłączeniu
    with pytest.raises(RuntimeError, match="Brak połączenia z bazą danych."):
        controller.get_all_specialties()




def test_count_specialties_for_profession(setup_specialties_controller):
    """
    Testuje metodę `count_specialties_for_profession`, zliczając specjalności dla danego zawodu.
    """
    controller = setup_specialties_controller

    # Dodawanie danych testowych
    controller.db_controller.connection.execute("""
        INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
        VALUES (1, 'Jan', 'Kowalski', 'admin.jan@klinika.com', '555909909', 'Psychiatra', 1)
    """)
    controller.add_specialty("Psychiatra dzieci")
    controller.add_specialty("Psychiatra dorosłych")

    controller.db_controller.connection.execute("INSERT INTO employee_specialties (employee_id, specialty_id) VALUES (1, 1)")
    controller.db_controller.connection.execute("INSERT INTO employee_specialties (employee_id, specialty_id) VALUES (1, 2)")
    controller.db_controller.connection.commit()

    # Testowanie
    results = controller.count_specialties_for_profession("Psychiatra")
    assert len(results) == 2
    assert results[0]["specialty_name"] == "Psychiatra dorosłych"
    assert results[1]["specialty_name"] == "Psychiatra dzieci"




def test_get_available_professions(setup_specialties_controller):
    """
    Testuje metodę `get_available_professions`, sprawdzając zwracane zawody.
    """
    controller = setup_specialties_controller

    # Dodawanie danych testowych
    controller.db_controller.connection.execute("""
        INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
        VALUES 
        (1, 'Jan', 'Kowalski', 'admin.jan@klinika.com', '555909909', 'Psychiatra', 1),
        (2, 'Anna', 'Nowak', 'anna.nowak@klinika.com', '555707707', 'Psycholog kliniczny', 1)
    """)
    controller.db_controller.connection.commit()

    # Testowanie
    professions = controller.get_available_professions()
    assert len(professions) == 2
    assert "Psychiatra" in professions
    assert "Psycholog kliniczny" in professions




def test_count_specialties_for_all_professions(setup_specialties_controller):
    """
    Testuje metodę `count_specialties_for_all_professions`, zliczając specjalności dla wszystkich zawodów.
    """
    controller = setup_specialties_controller

    # Dodawanie danych testowych
    controller.db_controller.connection.execute("""
        INSERT INTO employees (employee_id, first_name, last_name, email, phone, profession, is_medical_staff)
        VALUES 
        (1, 'Jan', 'Kowalski', 'admin.jan@klinika.com', '555909909', 'Psychiatra', 1),
        (2, 'Anna', 'Nowak', 'anna.nowak@klinika.com', '555707707', 'Psycholog kliniczny', 1)
    """)
    controller.add_specialty("Psychiatra dzieci")
    controller.add_specialty("Psychiatra dorosłych")
    controller.add_specialty("Psycholog kliniczny")

    controller.db_controller.connection.execute("INSERT INTO employee_specialties (employee_id, specialty_id) VALUES (1, 1)")
    controller.db_controller.connection.execute("INSERT INTO employee_specialties (employee_id, specialty_id) VALUES (1, 2)")
    controller.db_controller.connection.execute("INSERT INTO employee_specialties (employee_id, specialty_id) VALUES (2, 3)")
    controller.db_controller.connection.commit()

    # Testowanie
    results = controller.count_specialties_for_all_professions()
    assert len(results) == 2
    assert results[0]["profession"] == "Psychiatra"
    assert results[0]["number_of_specialties"] == 2
    assert results[1]["profession"] == "Psycholog kliniczny"
    assert results[1]["number_of_specialties"] == 1


