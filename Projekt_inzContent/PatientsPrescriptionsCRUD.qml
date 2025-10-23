import QtQuick
import QtQuick.Controls
import QtQuick.Controls.FluentWinUI3

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false

    Component.onCompleted: {
        console.log("Setting current screen to PatientsMainList");
        backendBridge.currentScreen = "PatientsMainList";
        backendBridge.checkPrescriptionsCRUDAccess();
    }

    // Timer do automatycznego ukrywania komunikatu po 5 sekundach
    Timer {
        id: messageTimer
        interval: 10000
        running: false
        repeat: false
        onTriggered: {
            idMessages.text = ""  // Gdy Timer się skończy, czyścimy tekst
        }
    }

    Popup {
        id: prescriptionErrorPopup
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        // Wyśrodkowanie Popup na ekranie
        anchors.centerIn: Overlay.overlay

        // Tło Popup z półprzezroczystością
        background: Rectangle {
            color: "black" // Półprzezroczyste szare tło (RGBA: 50% przezroczystości)
            radius: 10         // Zaokrąglone rogi
        }


        // Obsługa zamknięcia Popup
        onClosed: {
            console.log("[QML] Zamknięto komunikat błędu. Przełączanie widoku...");
            mainViewLoader.source = "PatientsMainList.qml"; // Zmiana widoku na główny
        }

        // Kolumna do wyświetlania treści
        Column {
            anchors.centerIn: parent
            spacing: 20

            // Tekst błędu
            Text {
                id: prescriptionErrorText
                text: "Brak uprawnień do przeglądania recept."
                font.pixelSize: 18
                color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                horizontalAlignment: Text.AlignHCenter
            }

            // Przycisk "OK"
            Button {
                width: parent.width * 0.25
                height: parent.height * 0.4
                text: "OK"

                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    prescriptionErrorPopup.close()
                    mainViewLoader.source = "PatientsMainList.qml";
                }

                background: Rectangle {
                    color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
                    radius: 5 // Zaokrąglenie rogów o 15 pikseli
                }
            }

        }
    }


    Connections {
        target: backendBridge

        function onPrescriptionsErrorOccurred(errorMessage) {
            console.log("[QML] Błąd: " + errorMessage);

            // Ustawienie komunikatu w tekście wewnątrz Popup
            prescriptionErrorText.text = errorMessage;
            prescriptionErrorPopup.open();
        }

        // Obsługa błędu podczas dodawania recepty
        function onPrescriptionAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania recepty: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }

        // Obsługa pomyślnego dodania recepty
        function onPrescriptionAddedSuccessfully() {
            console.log("[QML] Recepta została dodana pomyślnie!");
            idMessages.text = qsTr("Recepta została dodana do bazy danych!");
            idMessages.visible = true;
            messageTimer.start();
        }

        // Obsługa błędu podczas aktualizacji recepty
        function onPrescriptionUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji recepty: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnej aktualizacji recepty
        function onPrescriptionUpdatedSuccessfully() {
            console.log("[QML] Recepta została zaktualizowana pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Recepta została zaktualizowana w bazie danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // **Obsługa błędu podczas usuwania recepty**
        function onPrescriptionDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania recepty: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // **Obsługa pomyślnego usunięcia recepty**
        function onPrescriptionDeletedSuccessfully() {
            console.log("[QML] Recepta została usunięta!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Recepta została pomyślnie usunięta.");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

    }


    function validateEmptyField(value, fieldName) {
        if (!value || value.trim() === "") {
            showValidationMessage(`${fieldName} nie może być puste.`);
            return false;
        }
        return true; // Gdy wartość nie jest pusta
    }


    // Funkcja walidująca Code: przyjmuje tylko i wyłącznie 4 cyfry
    function validateCode(code) {
        let regex = /^\d{4}$/;
        return regex.test(code);
    }

    // Funkcja walidująca Price: przyjmuje tylko i wyłącznie cyfry zmiennoprzecinkowe (format np. 123 lub 123.45)
    function validatePrice(price) {
        // Dopasowuje liczbę całkowitą lub zmiennoprzecinkową z kropką jako separatorem
        let regex = /^\d+(\.\d+)?$/;
        return regex.test(price);
    }

    // Funkcja walidująca Dose: przyjmuje tylko i wyłącznie cyfry całkowite o długości od 1 do 5 cyfr
    function validateDose(dose) {
        let regex = /^\d{1,5}$/;
        return regex.test(dose);
    }

    function validatePositiveInteger(value) {
        return validateEmptyField(value) && /^\d+$/.test(value) && parseInt(value) > 0;
    }

    // Funkcja walidująca nazwę roli (duże i małe litery + polskie znaki + spacja)
    function validateMedicine(medicine) {
        let regex = /^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]+$/;
        return regex.test(medicine);
    }


    function showValidationMessage(message) {
        console.log("Komunikat walidacji:", message);
        idMessages.text = message;
        idMessages.visible = true;

        // Uruchamiamy timer, aby ukryć komunikat po 5 sekundach
        messageTimer.restart();
    }

    Image {
        id: background
        //source: "images/background22_1920x1080.png"
        // source: "images/background_dark_4.png"
        source: backendBridge.isDarkMode ? "images/background_dark_4.png" : "images/background22_1920x1080.png"

        //fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: 0  // Wypełnia cały widok
        fillMode: Image.PreserveAspectCrop
    }

    Text {
        id: idBarMenu
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("Menu")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.03 // Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Text {
        id: idBarHarmonogram
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("panel pacjenci")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.065// Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idRamka
        // Rozmiar ramki proporcjonalny do tła
        width: background.width * 0.13 // 13% szerokości tła
        height: background.height * 0.95 // 95% wysokości tła

        color: "transparent"
        border.color: "white"
        border.width: 5
        radius: 20

        // Wyśrodkowanie ramki względem przycisków i marginesy
        anchors.left: idBackToDashboard.left
        anchors.right: id_quit.right
        anchors.leftMargin: -20
        anchors.rightMargin: -20
        anchors.top: background.top
        anchors.bottom: background.bottom
        anchors.topMargin: background.height * 0.02 // Proporcjonalny margines od góry
        anchors.bottomMargin: background.height * 0.02 // Proporcjonalny margines od dołu
    }


    Text {
        id: idTextAdd
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj receptę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.15
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }




    Rectangle {
        id: idInputTextContainerAppointmentIdAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsAppointmentIdAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID wizyty")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID wizyty")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: inputContainerDoseAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsDoseAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Dawka")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Dawka")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerPriceAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27


        TextInput {
            id: fieldsPriceAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Cena")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Cena")) {
                    text = ""
                }
            }
        }
    }





    Rectangle {
        id: inputContainerMedicineAdd
        width: parent.width * 0.21
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true   // włączenie przycinania w kontenerze


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.26
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsMedicineAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa leku")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true   // włączenie przycinania w kontenerze

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa leku")) {
                    text = ""
                }
            }
        }


    }



    Rectangle {
        id: inputContainerCodeAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.26
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: fieldsCodeAdd
            anchors.fill: parent
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0
            anchors.bottomMargin: 0
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Kod recepty")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Kod recepty")) {
                    text = ""
                }
            }
        }
    }



    Button {
        id: idButtonPatientsAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: inputContainerPriceAdd.top
        anchors.topMargin: inputContainerPriceAdd.height * 0.08
        anchors.left: inputContainerPriceAdd.right
        anchors.leftMargin: parent.width * 0.025

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj receptę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];


            if (!validateEmptyField(fieldsAppointmentIdAdd.text)) {
                errors.push("ID wizyty może być puste.");
            } else if (!validatePositiveInteger(fieldsAppointmentIdAdd.text)) {
                errors.push("ID wizyty musi być liczbą całkowitą większą od 0.");
            }

            if (!validateEmptyField(fieldsCodeAdd.text)) {
                errors.push("Kod recepty nie może być puste.");
            } else if (!validateCode(fieldsCodeAdd.text)) {
                errors.push("Niepoprawny kod recepty: może zawierać tylko 4 cyfry.");
            }

            if (!validateEmptyField(fieldsPriceAdd.text)) {
                errors.push("Cena nie może być pusta.");
            } else if (!validatePrice(fieldsPriceAdd.text)) {
                errors.push("Niepoprawna Cena: tylko cyfry zmiennoprzecinkowe.");
            }

            if (!validateEmptyField(fieldsDoseAdd.text)) {
                errors.push("Dawka nie może być pusty.");
            } else if (!validateDose(fieldsDoseAdd.text)) {
                errors.push("Niepoprawna dawka: tylko cyfry.");
            }

            if (!validateEmptyField(fieldsMedicineAdd.text)) {
                errors.push("Nazwa leku nie może być puste.");
            } else if (!validateMedicine(fieldsMedicineAdd.text)) {
                errors.push("Niepoprawna nazwa leku.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                backendBridge.addPrescription(
                    fieldsAppointmentIdAdd.text,
                    fieldsMedicineAdd.text,
                    fieldsDoseAdd.text,
                    fieldsPriceAdd.text,
                    fieldsCodeAdd.text
                );
            }
        }
    }






    Button {
            id: idButtonPatientsUpdate
            width: parent.width * 0.1
            height: parent.height * 0.042

            anchors.top: inputContainerPriceUpdate.top
            anchors.topMargin: inputContainerPriceUpdate.height * 0.08
            anchors.leftMargin: parent.width * 0.025
            anchors.left: inputContainerPriceUpdate.right

            background: Rectangle {
                color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
                radius: 15
            }

            contentItem: Text {
                color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
                text: "Aktualizuj receptę"
                font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                console.log("Przycisk 'Aktualizuj dane' został kliknięty.");

                let errors = [];

                if (!validateEmptyField(fieldsPerscriptionIdUpdate.text)) {
                    errors.push("ID recepty może być puste.");
                } else if (!validatePositiveInteger(fieldsPerscriptionIdUpdate.text)) {
                    errors.push("ID recepty musi być liczbą całkowitą większą od 0.");
                }

                if (fieldsCodeUpdate.text.length > 0 && !validateCode(fieldsCodeUpdate.text)) {
                    errors.push("Niepoprawny kod recepty: może zawierać tylko 4 cyfry.");
                }
                if (fieldsAppointmentIdUpdate.text.length > 0 && !validatePositiveInteger(fieldsAppointmentIdUpdate.text)) {
                    errors.push("ID wizyty musi być liczbą całkowitą większą od 0.");
                }
                if (fieldsMedicineUpdate.text.length > 0 && !validateMedicine(fieldsMedicineUpdate.text)) {
                    errors.push("Niepoprawna nazwa leku.");
                }
                if (fieldsDoseUpdate.text.length > 0 && !validateDose(fieldsDoseUpdate.text)) {
                    errors.push("Niepoprawna dawka: tylko cyfry.");
                }
                if (fieldsPriceUpdate.text.length > 0 && !validatePrice(fieldsPriceUpdate.text)) {
                    errors.push("Niepoprawna Cena: tylko cyfry zmiennoprzecinkowe.");
                }

                if (errors.length > 0) {
                    console.log("Błędy walidacji:", errors);
                    showValidationMessage(errors.join("\n"));
                } else {
                    console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                    try {
                        backendBridge.updatePrescription(
                            fieldsPerscriptionIdUpdate.text,
                            fieldsAppointmentIdUpdate.text,
                            fieldsMedicineUpdate.text,
                            fieldsDoseUpdate.text,
                            fieldsPriceUpdate.text,
                            fieldsCodeUpdate.text,
                        );
                        // showValidationMessage("Dane pacjenta zostały zaktualizowane!");
                    } catch (e) {
                        console.log("Błąd podczas wysyłania do backendu:", e);
                        showValidationMessage("Błąd podczas aktualizacji pacjenta.");
                    }
                }
            }
        }


    Text {
        id: idTextDelete
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń receptę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.61
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextPerscriptionIdDel
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.66
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsPerscriptionIdDel
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID recepty")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID recepty")) {
                    text = ""
                }
            }
        }
    }






    Button {
        id: idButtonPatientsDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextPerscriptionIdDel.top
        anchors.topMargin: idInputTextPerscriptionIdDel.height * 0.08
        anchors.leftMargin: parent.width * 0.025 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextPerscriptionIdDel.right


        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Usuń receptę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }



        onClicked: {
            console.log("Przycisk 'Usuń dane' został kliknięty.");

            let errors = [];

            // Walidacja pola ID pacjenta
            if (!validateEmptyField(fieldsPerscriptionIdDel.text, "ID pacjenta")) {
                errors.push("ID recepty nie może być puste.");
            } else if (!validatePositiveInteger(fieldsPerscriptionIdDel.text)) {
                errors.push("ID recepty musi być liczbą.");
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                try {
                    backendBridge.deletePrescription(
                        parseInt(fieldsPerscriptionIdDel.text),
                    );
                    // showValidationMessage("Dane pacjenta zostały usunięte!");
                } catch (e) {
                    console.log("Błąd podczas wysyłania do backendu:", e);
                    showValidationMessage("Błąd podczas usuwania pacjenta.");
                }
            }
        }
    }



    Text {
        id: idTextUpdate
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj receptę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.35
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextContainerAppointmentIdUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.46
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsAppointmentIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID wizyty")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID wizyty")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerPerscriptionIdUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.4
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsPerscriptionIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID recepty")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID recepty")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerDoseUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.46
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsDoseUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Dawka")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Dawka")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerPriceUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.46
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27


        TextInput {
            id: fieldsPriceUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Cena")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Cena")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerCodeUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.52
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: fieldsCodeUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Kod recepty")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Kod recepty")) {
                    text = ""
                }
            }
        }
    }




    Rectangle {
        id: inputContainerMedicineUpdate
        width: parent.width * 0.21
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true   // włączenie przycinania w kontenerze


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.52
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsMedicineUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa leku")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true   // włączenie przycinania w kontenerze

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa leku")) {
                    text = ""
                }
            }
        }
    }





    Text {
        id: idMessages
        width: parent.width * 0.65 // 90% szerokości ramki
        height: parent.height * 0.15 // 10% wysokości ramki
        text: qsTr("")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.75
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        // verticalAlignment: Text.AlignVCenter
        verticalAlignment: TextEdit.AlignBottom   // kluczowa linia
        wrapMode: Text.WordWrap //
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.01, parent.height * 0.1)
    }








    Rectangle {
        id: customCheckBox
        // width: parent.height * 0.03// Dynamiczny rozmiar checkboxa
        width: Math.min(parent.width * 0.05, parent.height * 0.035) // Skalowanie w poziomie i pionie
        height: width // Zachowanie kwadratowego kształtu
        radius: width * 0.1 // Zaokrąglenia rogów
        // color: checked ? "#22ff00" : "#cccccc" // Kolor w zależności od stanu zaznaczenia
        color: backendBridge.isDarkMode
               ? (checked ? "#118f39" : "#961c3d") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
               : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.color: backendBridge.isDarkMode
                ? (checked ? "#22ff00" : "#ff0000") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
                : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.width: width * 0.05 // Grubość ramki
        anchors.left: idRamka.right
        anchors.leftMargin: idRamka.width * 0.4 // Dynamiczny odstęp od ramki
        anchors.bottom: idRamka.bottom
        anchors.bottomMargin: idRamka.height * 0.03 // Dynamiczny odstęp od dołu (5% wysokości rodzica)


        property bool checked: false // Własna właściwość przechowująca stan
        signal toggled(bool checked) // Sygnał emitowany po zmianie stanu

        MouseArea {
            anchors.fill: parent
            onClicked: {
                customCheckBox.checked = !customCheckBox.checked // Przełącz stan
                customCheckBox.toggled(customCheckBox.checked) // Emituj sygnał
                canvas.requestPaint() // Wymuś odświeżenie płótna
            }
        }

        onCheckedChanged: {
            console.log("Checkbox state changed to: " + checked);
            geometryManager.fullscreen = checked;
        }

        // Symbol "ptaszek" w środku, wyświetlany tylko po zaznaczeniu
        Canvas {
            id: canvas
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height); // Wyczyść obszar rysowania
                if (customCheckBox.checked) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.2, height * 0.5);
                    ctx.lineTo(width * 0.4, height * 0.7);
                    ctx.lineTo(width * 0.8, height * 0.3);
                    ctx.strokeStyle = "#000000"; // Kolor "ptaszka" na czarny
                    ctx.lineWidth = width * 0.1;
                    ctx.stroke();
                }
            }
        }

        // Tekst obok checkboxa
        Text {
            id: textFullSceen
            text: qsTr("Tryb pełnoekranowy")
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            anchors.leftMargin: width * 0.1
            font.pixelSize: parent.height * 0.8 // Dynamiczny rozmiar tekstu (proporcja wysokości rodzica)
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            // clip: true
            // elide: Text.ElideRight
        }

        Component.onCompleted: {
            // Synchronizuj stan checkboxa z aktualnym stanem trybu pełnoekranowego
            customCheckBox.checked = geometryManager.fullscreen;
        }
    }


    Rectangle {
        id: checkBoxDarkMode
        width: Math.min(parent.width * 0.05, parent.height * 0.035) // Skalowanie w poziomie i pionie
        height: width // Zachowanie kwadratowego kształtu
        radius: width * 0.1 // Zaokrąglenia rogów
        color: backendBridge.isDarkMode
               ? (checked ? "#118f39" : "#961c3d") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
               : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.color: backendBridge.isDarkMode
                ? (checked ? "#22ff00" : "#ff0000") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
                : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.width: width * 0.05
        anchors.left: customCheckBox.right
        anchors.leftMargin: customCheckBox.height * 10
        anchors.bottom: customCheckBox.bottom
        anchors.bottomMargin: customCheckBox.height * 0// Dynamiczny odstęp od dołu (5% wysokości rodzica)

        property bool checked: false

        MouseArea {
            anchors.fill: parent
            onClicked: {
                console.log("Kliknięto checkbox trybu ciemnego");
                checkBoxDarkMode.checked = !checkBoxDarkMode.checked;
                backendBridge.isDarkMode = checkBoxDarkMode.checked; // Synchronizacja z backendem
                canvasDark.requestPaint(); // Wymuszenie odświeżenia płótna
            }
        }

        Canvas {
            id: canvasDark
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height); // Czyszczenie płótna

                if (checkBoxDarkMode.checked) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.2, height * 0.5); // Start ptaszka
                    ctx.lineTo(width * 0.4, height * 0.7); // Środek ptaszka
                    ctx.lineTo(width * 0.8, height * 0.3); // Koniec ptaszka
                    ctx.strokeStyle = "#000000"; // Czarny kolor
                    ctx.lineWidth = width * 0.1; // Grubość linii
                    ctx.stroke();
                }
            }
        }

        Text {
            text: qsTr("Tryb ciemny")
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            anchors.leftMargin: width * 0.19
            font.pixelSize: parent.height * 0.8
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            // clip: true
            // elide: Text.ElideRight
        }

        Component.onCompleted: {
            checkBoxDarkMode.checked = backendBridge.isDarkMode;
        }

    }



    // Text {
    //     text: "Fullscreen: " + geometryManager.fullscreen
    //     color: "red"
    //     anchors.bottom: parent.bottom
    //     anchors.bottomMargin: 20
    // }



    Text {
        text: qsTr("Panel pacjenci - zarządzanie receptami")
        width: parent.width * 0.55
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.025, parent.height * 0.1)
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.04// Proporcjonalne pozycjonowanie
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.15
        anchors.right: background.right
        anchors.rightMargin: background.width * 0.15
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true
        elide: Text.ElideRight
    }

    Button {
        id: idBackToDashboard
        width: parent.width * 0.1
        height: parent.height * 0.042
        font.pixelSize: height * 0.42
        text: "Powrót"
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.12 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Powrót"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Dashboard.qml
            mainViewLoader.source = "Dashboard.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"
            radius: 15 // Zaokrąglenie rogów o 5 pikseli
        }
    }

    Button {
        id: id_quit
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.05

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Wyjdź z aplikacji"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        // Obsługa kliknięcia
        onClicked: {
            Qt.quit(); // Wyłączenie aplikacji
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }


    Button {
        id: idPatientsDiagnoses
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.45 // Margines od dolnej krawędzi (2% wy

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie diagnozami"
            font.pixelSize: Math.min(parent.width * 0.075, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "PatientsDiagnosesCRUD.qml";
            // Zmieniamy stan isClicked na true

        }

    }


    Button {
        id: idPatientsMedicalData
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.55 // Margines od dolnej krawędzi (2% wy

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista diagnóz"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "PatientsDiagnoses.qml";
            // Zmieniamy stan isClicked na true

        }

    }


    Button {
        id: idPatientsMainList
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.75// Margines od dolnej krawędzi (2% wy

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów


        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista pacjentów"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // backendBridge.currentScreen = "PatientsMainList"; // Zmiana aktywnej zakładki
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsMainList.qml";

        }
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }

    Button {
        id: idPatientsCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.65 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie pacjentami"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.32)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }


        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsCRUD.qml";


        }


        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }



    Button {
        id: idPatientsPerscriptionsCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.25 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie receptami"
            font.pixelSize: Math.min(parent.width * 0.08, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsPrescriptionsCRUD.qml";
            idPatientsMainList.isClicked = true;
        }

        background: Rectangle {
            color: backendBridge.currentScreen === "PatientsMainList"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
        }

    }

    Button {
        id: idPatientsPerscriptions
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.35 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista Recept"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsPrescriptions.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }
}

