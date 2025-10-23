# test_patient_forms_model_validation.py

import os
import pytest
import sqlite3
from controllers.database_controller import DatabaseController
from controllers.patients_controller import PatientController
from controllers.form_types_controller import FormTypesController
from validators.patient_forms_model_validation import (
    validate_submission_date,
    validate_fk_patient_id_exists,
    validate_fk_form_type_id_exists,
    validate_non_nullable_fields,
    validate_update_fields,
    validate_operator_and_value,
    validate_filters_and_sorting
)

# Ustawienie środowiska testowego
os.environ["APP_ENV"] = "test"

@pytest.fixture(name="setup_controllers")
def setup_controllers_fixture():
    """
    Fixture konfigurujący testową bazę danych SQLite3.
    Tworzy wymagane tabele i zapewnia czyste środowisko testowe.
    """
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    controllers = {
        "db_controller": db_controller,
        "patients": PatientController(db_controller),
        "form_types": FormTypesController(db_controller),
    }

    # Tworzenie tabel
    for controller in controllers.values():
        if hasattr(controller, "create_table"):
            controller.create_table()

    yield controllers

    # Czyszczenie danych po każdym teście
    if db_controller.connection is not None:
        try:
            with db_controller.connection:
                db_controller.connection.execute("DELETE FROM patients")
                db_controller.connection.execute("DELETE FROM form_types")
        except sqlite3.Error as e:
            print(f"Błąd podczas czyszczenia danych: {e}")
    db_controller.close_connection()

def test_validate_submission_date():
    """
    Testuje walidację daty zgłoszenia.
    """
    # Poprawne dane
    validate_submission_date("2025-01-13")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nieprawidłowy format daty zgłoszenia: .*"):
        validate_submission_date("13-01-2025")
    with pytest.raises(ValueError, match="Nieprawidłowy format daty zgłoszenia: .*"):
        validate_submission_date("2025/01/13")
    with pytest.raises(ValueError, match="Nieprawidłowy format daty zgłoszenia: .*"):
        validate_submission_date("")

def test_validate_fk_patient_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_patient_id` w tabeli `patients`.
    """
    db_controller = setup_controllers["db_controller"]
    patients_controller = setup_controllers["patients"]

    # Dodanie pacjenta
    patient = patients_controller.add_patient("Jan", "Kowalski", "12345678901", "555123456", "jan@example.com", "Adres", "1980-01-01")
    patient_id = patient["patient_id"]

    # Poprawne dane
    validate_fk_patient_id_exists(db_controller, patient_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Pacjent o ID .* nie istnieje."):
        validate_fk_patient_id_exists(db_controller, 999)

def test_validate_fk_form_type_id_exists(setup_controllers):
    """
    Testuje walidację istnienia `fk_form_type_id` w tabeli `form_types`.
    """
    db_controller = setup_controllers["db_controller"]
    form_types_controller = setup_controllers["form_types"]

    # Dodanie typu formularza
    form_type_id = form_types_controller.add_form_types("Zgoda na leczenie")

    # Poprawne dane
    validate_fk_form_type_id_exists(db_controller, form_type_id)

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Typ formularza o ID .* nie istnieje."):
        validate_fk_form_type_id_exists(db_controller, 999)


def test_validate_non_nullable_fields():
    """
    Testuje walidację pól wymaganych.
    """
    # Poprawne dane
    validate_non_nullable_fields(1, 2, "2025-01-13")

    # Niepoprawne dane
    with pytest.raises(ValueError, match="Pole `fk_patient_id` nie może być null."):
        validate_non_nullable_fields(None, 2, "2025-01-13")
    with pytest.raises(ValueError, match="Pole `fk_form_type_id` nie może być null."):
        validate_non_nullable_fields(1, None, "2025-01-13")
    with pytest.raises(ValueError, match="Pole `submission_date` nie może być null."):
        validate_non_nullable_fields(1, 2, None)


# +-+-+-+- metody stałe -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def test_validate_update_fields():
    """
    Testuje walidację pól aktualizacji.
    """
    valid_columns = ["patient_form_id", "fk_patient_id", "fk_form_type_id", "submission_date", "content"]
    # Poprawne dane
    validate_update_fields({"patient_form_id": "Nowy opis"}, valid_columns)
    validate_update_fields({"fk_patient_id": "A01.0"}, valid_columns)
    validate_update_fields({"fk_form_type_id": 123}, valid_columns)
    validate_update_fields({"submission_date": "Nowy opis"}, valid_columns)
    validate_update_fields({"content": "A01.0"}, valid_columns)


    # Niepoprawne dane
    with pytest.raises(ValueError, match="Nie podano danych do aktualizacji."):
        validate_update_fields({}, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna do aktualizacji: invalid_column."):
        validate_update_fields({"invalid_column": "wartość"}, valid_columns)


def test_validate_operator_and_value():
    """
    Testuje walidację operatorów i wartości w zapytaniach SQL.
    """
    # Poprawne przypadki
    validate_operator_and_value("=", "Opis diagnozy")
    validate_operator_and_value("LIKE", "Opis%")
    validate_operator_and_value("BETWEEN", (1, 10))
    validate_operator_and_value("IN", [1, 2, 3])
    validate_operator_and_value("IS NULL", None)
    validate_operator_and_value("IS NOT NULL", None)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Nieobsługiwany operator: <>."):
        validate_operator_and_value("<>", "Niepoprawny operator")

    with pytest.raises(ValueError, match="Wartość dla operatora LIKE musi być niepustym ciągiem znaków."):
        validate_operator_and_value("LIKE", "")

    with pytest.raises(ValueError, match="Operator BETWEEN wymaga krotki zawierającej dwie wartości."):
        validate_operator_and_value("BETWEEN", (1,))

    with pytest.raises(ValueError, match="Wartość dla operatora IN musi być niepustą listą lub krotką."):
        validate_operator_and_value("IN", [])


def test_validate_filters_and_sorting():
    """
    Testuje walidację filtrów i sortowania w zapytaniach SQL.
    """
    valid_columns = ["patient_form_id", "fk_patient_id", "fk_form_type_id", "submission_date", "content"]

    # Poprawne dane
    filters = [
        {"column": "patient_form_id", "operator": "LIKE", "value": "Opis%"},
        {"column": "fk_patient_id", "operator": ">", "value": 1},
        {"column": "fk_form_type_id", "operator": "=", "value": "A01.0"},
        {"column": "submission_date", "operator": "!=", "value": "Błąd opisu"},
        {"column": "content", "operator": "=", "value": "A01.0"},
    ]
    sort_by = [
        {"column": "fk_patient_id", "direction": "ASC"},
        {"column": "submission_date", "direction": "DESC"},
    ]

    # Powinno przejść bez błędów
    validate_filters_and_sorting(filters, sort_by, valid_columns)

    # Niepoprawne przypadki
    with pytest.raises(ValueError, match="Każdy filtr musi zawierać klucze: 'column', 'operator', 'value'."):
        validate_filters_and_sorting([{"column": "description", "operator": "LIKE"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: invalid_column."):
        validate_filters_and_sorting([{"column": "invalid_column", "operator": "LIKE", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w filtrze: description. Dozwolone kolumny: patient_form_id, fk_patient_id, fk_form_type_id, submission_date, content"):
        validate_filters_and_sorting([{"column": "description", "operator": "INVALID", "value": "Opis%"}], None, valid_columns)

    with pytest.raises(ValueError, match="Każde sortowanie musi zawierać klucze: 'column' i 'direction'."):
        validate_filters_and_sorting(None, [{"column": "description"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: invalid_column."):
        validate_filters_and_sorting(None, [{"column": "invalid_column", "direction": "ASC"}], valid_columns)

    with pytest.raises(ValueError, match="Nieprawidłowa kolumna w sortowaniu: description. Dozwolone kolumny: patient_form_id, fk_patient_id, fk_form_type_id, submission_date, content"):
        validate_filters_and_sorting(None, [{"column": "description", "direction": "INVALID"}], valid_columns)