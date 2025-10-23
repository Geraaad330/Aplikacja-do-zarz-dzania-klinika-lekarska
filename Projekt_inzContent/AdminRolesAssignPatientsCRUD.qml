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
        backendBridge.currentScreen = "AdminSettingsMainUsers";
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


    Connections {
        target: bridgeAdmin

        // Obsługa błędu podczas przypisywania pacjenta do pracownika
        function onPatientAssignmentFailed(errorMessage) {
            console.log("[QML] Błąd przypisania pacjenta do pracownika: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego przypisania pacjenta do pracownika
        function onPatientAssignedSuccessfully() {
            console.log("[QML] Pacjent został przypisany do pracownika!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Pacjent został przypisany do pracownika!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas aktualizacji przypisania pacjenta do pracownika
        function onPatientAssignmentUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji przypisania pacjenta: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnej aktualizacji przypisania pacjenta do pracownika
        function onPatientAssignmentUpdatedSuccessfully() {
            console.log("[QML] Przypisanie pacjenta do pracownika zostało zaktualizowane pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Przypisanie pacjenta do pracownika zostało pomyślnie zaktualizowane!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas usuwania przypisania pacjenta
        function onPatientAssignmentDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania przypisania pacjenta: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego usunięcia przypisania pacjenta
        function onPatientAssignmentDeletedSuccessfully() {
            console.log("[QML] Przypisanie pacjenta zostało usunięte!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Przypisanie pacjenta zostało usunięte!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas dodawania roli
        function onRoleAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania roli: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego dodania roli
        function onRoleAddedSuccessfully() {
            console.log("[QML] Rola została dodana pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Rola została dodana do bazy danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas aktualizacji roli
        function onRoleUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji roli: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }

        // Obsługa pomyślnej aktualizacji roli
        function onRoleUpdatedSuccessfully() {
            console.log("[QML] Rola została zaktualizowana pomyślnie!");
            idMessages.text = qsTr("Rola została zaktualizowana pomyślnie!");
            idMessages.visible = true;
            messageTimer.start();
        }

        // Obsługa błędu podczas usuwania roli
        function onRoleDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania roli: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego usunięcia roli
        function onRoleDeletedSuccessfully() {
            console.log("[QML] Rola została usunięta pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Rola została usunięta pomyślnie!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

    }


    function validateIsActive(isActive) {
        let formattedValue = isActive.trim().toLowerCase();
        return formattedValue === "tak" || formattedValue === "nie";
    }

    function formatIsActive(value) {
        // Usuwa zbędne spacje, konwertuje na małe litery
        return value.trim().toLowerCase();
    }

    function showValidationMessage(message) {
        console.log("Komunikat walidacji:", message);
        idMessages.text = message;
        idMessages.visible = true;

        // Uruchamiamy timer, aby ukryć komunikat po 5 sekundach
        messageTimer.restart();
    }

    function validateEmptyField(value, fieldName) {
        if (!value || value.trim() === "") {
            showValidationMessage(`${fieldName} nie może być puste.`);
            return false;
        }
        return true; // Gdy wartość nie jest pusta
    }
    // Funkcja sprawdzająca, czy wartość jest liczbą całkowitą, nieujemną i niepustą


    function validatePositiveInteger(value) {
        return validateEmptyField(value) && /^\d+$/.test(value) && parseInt(value) > 0;
    }

    // Funkcja walidująca nazwę roli (duże i małe litery + polskie znaki + spacja)
    function validateRoleName(roleName) {
        let regex = /^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]+$/;
        return regex.test(roleName);
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
        font.pixelSize: Math.min(parent.width * 0.009, parent.height * 0.1)
    }

    Text {
        id: idBarHarmonogram
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("ustawienia administracyjne")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.065// Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.009, parent.height * 0.1)
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
        id: idTextDeleteRole
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń rolę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.51
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Button {
        id: idButtonRoleDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerRoleIdDelete.top
        anchors.topMargin: idInputTextContainerRoleIdDelete.height * 0.08
        anchors.leftMargin: parent.width * 0.02 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerRoleIdDelete.right


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
            text: "Usuń rolę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsRoleIdDelete.text)) {
                errors.push("ID roli nie może być puste.");
            } else if (!validatePositiveInteger(fieldsRoleIdDelete.text)) {
                errors.push("ID roli musi być liczbą.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeAdmin.deleteRole(
                    fieldsRoleIdDelete.text,
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoleIdDelete
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.56
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47

        TextInput {
            id: fieldsRoleIdDelete
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID roli")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID roli")) {
                    text = ""
                }
            }
        }
    }


    Text {
        id: idTextRoleUpdate
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj rolę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.3
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Button {
        id: idButtonRoleUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerRoleNameUpdate.top
        anchors.topMargin: idInputTextContainerRoleNameUpdate.height * 0.08
        anchors.leftMargin: parent.width * 0.02 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerRoleNameUpdate.right


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
            text: "Aktualizuj rolę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];


            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsRoleIdUpdate.text)) {
                errors.push("ID roli nie może być puste.");
            } else if (!validatePositiveInteger(fieldsRoleIdUpdate.text)) {
                errors.push("ID roli musi być liczbą.");
            }

            if (fieldsRoleNameUpdate.text.length > 0 && !validateRoleName(fieldsRoleNameUpdate.text)) {
                errors.push("Pole nazwa roli zawiera niepoprawne znaki.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeAdmin.updateRole(
                    fieldsRoleIdUpdate.text,
                    fieldsRoleNameUpdate.text,
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoleNameUpdate
        width: parent.width * 0.225
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.41
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47

        TextInput {
            id: fieldsRoleNameUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa roli")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa roli")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoleIdUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.35
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47

        TextInput {
            id: fieldsRoleIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID roli")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID roli")) {
                    text = ""
                }
            }
        }
    }


    Text {
        id: idTextRoleAdd
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj rolę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.15
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Button {
        id: idButtonRoleAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerRoleNameAdd.top
        anchors.topMargin: idInputTextContainerRoleNameAdd.height * 0.08
        anchors.leftMargin: parent.width * 0.02 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerRoleNameAdd.right


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
            text: "Dodaj rolę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsRoleNameAdd.text)) {
                errors.push("Pole nazwa roli nie może być puste.");
            } else if (!validateRoleName(fieldsRoleNameAdd.text)) {
                errors.push("Pole nazwa roli zawiera niepoprawne znaki.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeAdmin.addRole(
                    fieldsRoleNameAdd.text
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoleNameAdd
        width: parent.width * 0.225
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.47

        TextInput {
            id: fieldsRoleNameAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa roli")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa roli")) {
                    text = ""
                }
            }
        }
    }


    Text {
        id: idTextAdd
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj przypisanie pacjenta do pracownika")
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
        id: idInputTextContainerEmployeeIdAssignAdd
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
            id: fieldsEmployeeIdAssignAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pracownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pracownika")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerPatientIdAssignAdd
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
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsPatientIdAssignAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pacjenta")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pacjenta")) {
                    text = ""
                }
            }
        }
    }


    Button {
        id: idButtonPatientsAssignUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerEmployeeIdAssignUpdate.top
        anchors.topMargin: idInputTextContainerEmployeeIdAssignUpdate.height * 0.08
        anchors.leftMargin: parent.width * 0.02 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerEmployeeIdAssignUpdate.right


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
            text: "Aktualizuj przypisanie"
            font.pixelSize: Math.min(parent.width * 0.08, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsAssignmentIdUpdate.text)) {
                errors.push("ID przypisania nie może być puste.");
            } else if (!validatePositiveInteger(fieldsAssignmentIdUpdate.text)) {
                errors.push("ID przypisania musi być liczbą.");
            }

            if (fieldsPatientIdAssignUpdate.text.length > 0 && !validatePositiveInteger(fieldsPatientIdAssignUpdate.text)) {
                errors.push("ID pacjenta musi być liczbą.");
            }

            if (fieldsEmployeeIdAssignUpdate.text.length > 0 && !validatePositiveInteger(fieldsEmployeeIdAssignUpdate.text)) {
                errors.push("ID pracownika musi być liczbą.");
            }

            let isActiveValue = fieldsAssignmentIsActiveUpdate.text.trim();
            if (isActiveValue.length > 0 && !validateIsActive(isActiveValue)) {
                errors.push("Podaj wartość 'Tak' lub 'Nie' dla pola 'Aktywność'.");
            } else if (isActiveValue.length > 0) {
                isActiveValue = formatIsActive(isActiveValue);  // Konwersja na "tak" lub "nie"
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeAdmin.updateAssignedPatient(
                    fieldsAssignmentIdUpdate.text,
                    fieldsPatientIdAssignUpdate.text,
                    fieldsEmployeeIdAssignUpdate.text,
                    isActiveValue
                );
            }
        }
    }













    Text {
        id: idTextDeleteAssign
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń przypisanie pacjenta do pracownika")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.51
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }




    Rectangle {
        id: idInputTextContainerEmployeeIdDeleteAssign
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.56
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsEmployeeIdDelAssign
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID przypisania")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID przypisania")) {
                    text = ""
                }
            }
        }
    }

    Button {
        id: idButtonPatientsAssignDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerEmployeeIdDeleteAssign.top
        anchors.topMargin: idInputTextContainerEmployeeIdDeleteAssign.height * 0.08
        anchors.leftMargin: parent.width * 0.02 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerEmployeeIdDeleteAssign.right


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
            text: "Usuń przypisania"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsEmployeeIdDelAssign.text)) {
                errors.push("ID przypisania nie może być puste.");
            } else if (!validatePositiveInteger(fieldsEmployeeIdDelAssign.text)) {
                errors.push("ID przypisania musi być liczbą.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeAdmin.deleteAssignedPatient(
                   fieldsEmployeeIdDelAssign.text,
                );
            }
        }
    }

    Button {
        id: idButtonPatientsAssignAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerPatientIdAssignAdd.top
        anchors.topMargin: idInputTextContainerPatientIdAssignAdd.height * 0.08
        anchors.leftMargin: parent.width * 0.02 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerPatientIdAssignAdd.right


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
            text: "Dodaj przypisanie"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsEmployeeIdAssignAdd.text)) {
                errors.push("ID pracownika nie może być puste.");
            } else if (!validatePositiveInteger(fieldsEmployeeIdAssignAdd.text)) {
                errors.push("ID pracownika musi być liczbą.");
            }

            if (!validateEmptyField(fieldsPatientIdAssignAdd.text)) {
                errors.push("ID pacjenta nie może być puste.");
            } else if (!validatePositiveInteger(fieldsPatientIdAssignAdd.text)) {
                errors.push("ID pacjenta musi być liczbą.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeAdmin.addAssignedPatient(
                    fieldsPatientIdAssignAdd.text,
                    fieldsEmployeeIdAssignAdd.text
                );
            }
        }
    }

    Text {
        id: idTextUpdate
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj przypisanie pacjenta do pracownika")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.3
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextContainerAssignmentIsActiveUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.35
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsAssignmentIsActiveUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Aktywny Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.012, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Aktywny Tak/Nie")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerAssignmentIdUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.35
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsAssignmentIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID przypisania")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID przypisania")) {
                    text = ""
                }
            }
        }
    }


    Text {
        id: idMessages
        width: parent.width * 0.65 // 90% szerokości ramki
        height: parent.height * 0.18 // 10% wysokości ramki
        text: qsTr("")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.7
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        // verticalAlignment: Text.AlignVCenter
        verticalAlignment: TextEdit.AlignBottom   // kluczowa linia
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.01, parent.height * 0.1)
    }


    Rectangle {
        id: idInputTextContainerEmployeeIdAssignUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.41
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsEmployeeIdAssignUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pracownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pracownika")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerPatientIdAssignUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.41
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsPatientIdAssignUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pacjenta")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pacjenta")) {
                    text = ""
                }
            }
        }
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
        text: qsTr("Panel ustawienia administracyjne - zarządzanie rolami oraz przydzielaniem pacjentów")
        width: parent.width * 0.6
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.017, parent.height * 0.1)
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.04// Proporcjonalne pozycjonowanie
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.1
        anchors.right: background.right
        anchors.rightMargin: background.width * 0.1
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
        id: idButtonRolesPermissions
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.5 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Role i przypisani pacjenci"
            font.pixelSize: Math.min(parent.width * 0.075, parent.height * 0.4)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "AdminRolesAssignPatientsList.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }


    Button {
        id: idButtonMainUsers
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.7// Margines od dolnej krawędzi (2% wy

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Użytkownicy"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // backendBridge.currentScreen = "PatientsMainList"; // Zmiana aktywnej zakładki
            // Przełącz widok na Login.qml
            mainViewLoader.source = "AdminSettingsMainUsersList.qml";
            // Zmieniamy stan isClicked na true

        }


    }

    Button {
        id: idButtonUsersCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.6 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie użytkownikami"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.3)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }


        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "AdminSettingsUsersCRUD.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }

    Button {
        id: idButtonRolesCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.4 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządz. rolami i przypisaniami"
            font.pixelSize: Math.min(parent.width * 0.06, parent.height * 0.4)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "AdminRolesAssignPatientsCRUD.qml";
            idButtonMainUsers.isClicked = true;
        }


        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.currentScreen === "AdminSettingsMainUsers"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
        }


    }

}

