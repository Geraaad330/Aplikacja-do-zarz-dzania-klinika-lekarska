import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false

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

        // Obsługa błędu dodawania użytkownika
        function onUserAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania użytkownika: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }

        // Obsługa pomyślnego dodania użytkownika
        function onUserAddedSuccessfully() {
            console.log("[QML] Użytkownik został dodany pomyślnie!");
            idMessages.text = qsTr("Użytkownik został dodany do bazy danych!");
            idMessages.visible = true;
            messageTimer.start();
        }

        // Obsługa błędów dla aktualizacji użytkownika
        function onUserUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji użytkownika: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }

        // Obsługa sukcesu dla aktualizacji użytkownika
        function onUserUpdatedSuccessfully() {
            console.log("[QML] Użytkownik został zaktualizowany pomyślnie!");
            idMessages.text = qsTr("Użytkownik został zaktualizowany pomyślnie!");
            idMessages.visible = true;
            messageTimer.start();
        }

        function onUserDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania użytkownika: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        function onUserDeletedSuccessfully() {
            console.log("[QML] Użytkownik został usunięty pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Użytkownik został usunięty z bazy danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }
    }

    Component.onCompleted: {
        console.log("Setting current screen to AdminSettingsMainUsers");
        backendBridge.currentScreen = "AdminSettingsMainUsers";
    }


    // Funkcja walidująca format daty YYYY-MM-DD HH:MM
    function validateExpirationDate(date) {
        let regex = /^[1-2]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):([0-5]\d)$/;
        return regex.test(date);
    }

    // Funkcja walidująca nazwę użytkownika (małe litery + kropka, bez polskich znaków i spacji)
    function validateUsername(username) {
        let regex = /^[a-z.]+$/;
        return regex.test(username);
    }

    function validateIsActive(isActive) {
        let formattedValue = isActive.trim().toLowerCase();
        return formattedValue === "tak" || formattedValue === "nie";
    }

    function formatIsActive(value) {
        return value.trim().toLowerCase();
    }

    function showValidationMessage(message) {
        console.log("Komunikat walidacji:", message);
        idMessages.text = message;
        idMessages.visible = true;
        messageTimer.restart();
    }

    function validateEmptyField(value, fieldName = "Pole") {
        if (!value || value.trim() === "") {
            showValidationMessage(`${fieldName} nie może być puste.`);
            return false;
        }
        return true;
    }

    // Funkcja sprawdzająca, czy wartość jest liczbą całkowitą, nieujemną i niepustą
    function validatePositiveInteger(value) {
        return validateEmptyField(value) && /^\d+$/.test(value) && parseInt(value) > 0;
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
        text: qsTr("Panel ustawienia administracyjne - zarządzanie użytkownikami")
        width: parent.width * 0.6
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.023, parent.height * 0.1)
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

        // Tło przycisku z dynamiczną zmianą kolorów
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
            idButtonMainUsers.isClicked = true;
        }


        background: Rectangle {
            color: backendBridge.currentScreen === "AdminSettingsMainUsers"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
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
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }


    Text {
        id: idTextDel
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń użytkownika")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.55
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Button {
        id: idButtonUserDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerUserIdDel.top
        anchors.topMargin: idInputTextContainerUserIdDel.height * 0.08
        anchors.left: idInputTextContainerUserIdDel.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Usuń użytkownika"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");
            let errors = [];

            if (!validateEmptyField(fieldsUserIdDel.text)) {
                errors.push("ID pracownika nie może być puste.");
            } else if (!validatePositiveInteger(fieldsUserIdDel.text)) {
                errors.push("ID pracownika musi być liczbą.");
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeAdmin.deleteUser(
                    fieldsUserIdDel.text,
                );
            }
        }

    }


    Rectangle {
        id: idInputTextContainerUserIdDel
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.6
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsUserIdDel
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID użytkownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID użytkownika")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idTextUpdate
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj użytkownika")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.32
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Button {
        id: idButtonUserUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerPasswordUpdate.top
        anchors.topMargin: idInputTextContainerPasswordUpdate.height * 0.08
        anchors.left: idInputTextContainerPasswordUpdate.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Aktualizuj użytkownika"
            font.pixelSize: Math.min(parent.width * 0.08, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");
            let errors = [];

            if (!validateEmptyField(fieldsUserIdUpdate.text, "ID użytkownika")) {
                errors.push("ID użytkownika nie może być puste.");
            } else if (!validatePositiveInteger(fieldsUserIdUpdate.text)) {
                errors.push("ID użytkownika musi być liczbą.");
            }

            if (fieldsEmpIdUpdate.text.length > 0 && !validatePositiveInteger(fieldsEmpIdUpdate.text)) {
                errors.push("ID pracownika musi być liczbą.");
            }

            if (fieldsRoleIdUpdate.text.length > 0 && !validatePositiveInteger(fieldsRoleIdUpdate.text)) {
                errors.push("ID przypisania musi być liczbą.");
            }

            if (fieldsUserNameUpdate.text.length > 0 && !validateUsername(fieldsUserNameUpdate.text)) {
                errors.push("Pole nazwa użytkownika zawiera niepoprawne znaki. Dozwolone znaki: a-z oraz '.'.");
            }

            if (fieldsExpiredUpdate.text.length > 0 && !validateExpirationDate(fieldsExpiredUpdate.text)) {
                errors.push("Pole data wygaśnięcia zawiera niepoprawne znaki. Dozwolony format daty: YYYY-MM-DD HH:MM.");
            }

            let isActiveValue = fieldsIsActiveUpdate.text.trim();
            if (isActiveValue.length > 0 && !validateIsActive(isActiveValue)) {
                errors.push("Podaj wartość 'Tak' lub 'Nie' dla pola 'Aktywność'.");
            } else if (isActiveValue.length > 0) {
                isActiveValue = formatIsActive(isActiveValue);  // Konwersja na "tak" lub "nie"
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeAdmin.updateUser(
                    parseInt(fieldsUserIdUpdate.text),
                    fieldsEmpIdUpdate.text,
                    fieldsRoleIdUpdate.text,
                    fieldsUserNameUpdate.text,
                    fieldsPasswordUpdate.text,
                    fieldsExpiredUpdate.text,
                    isActiveValue
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerIsActiveUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.37
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsIsActiveUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Aktywny Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.011, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Aktywny Tak/Nie")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerPasswordUpdate
        width: parent.width * 0.155
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.43
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.545

        TextInput {
            id: fieldsPasswordUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Hasło")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Hasło")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerUserNameUpdate
        width: parent.width * 0.155
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.43
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38

        TextInput {
            id: fieldsUserNameUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa użytkownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa użytkownika")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerUserIdUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.37
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsUserIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID użytkownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID użytkownika")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerExpiredUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.43
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: fieldsExpiredUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Wygasa")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.012, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Wygasa")) {
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
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.43
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsRoleIdUpdate
            anchors.fill: parent
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0
            anchors.bottomMargin: 0
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID roli")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID roli")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerIdEmpUpdate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.43
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsEmpIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pracownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pracownika")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idTextAdd
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj użytkownika")
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

    Button {
        id: idButtonUserAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerPasswordAdd.top
        anchors.topMargin: idInputTextContainerPasswordAdd.height * 0.08
        anchors.left: idInputTextContainerPasswordAdd.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj użytkownika"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");
            let errors = [];


            if (!validateEmptyField(fieldsIdEmpAdd.text)) {
                errors.push("ID pracownika nie może być puste.");
            } else if (!validatePositiveInteger(fieldsIdEmpAdd.text)) {
                errors.push("ID pracownika musi być liczbą.");
            }

            if (!validateEmptyField(fieldsIdRoleIdAdd.text)) {
                errors.push("ID roli nie może być puste.");
            } else if (!validatePositiveInteger(fieldsIdRoleIdAdd.text)) {
                errors.push("ID roli musi być liczbą.");
            }

            if (!validateEmptyField(fieldsUserNameAdd.text)) {
                errors.push("Pole nazwa użytkownika nie może być puste.");
            } else if (!validateUsername(fieldsUserNameAdd.text)) {
                errors.push("Pole nazwa użytkownika zawiera niepoprawne znaki. Dozwolone znaki: tylko małe litery oraz kropka '.'");
            }

            if (!validateEmptyField(fieldsPasswordAdd.text)) {
                errors.push("Hasło nie może być puste");
            } else if (!validateUsername(fieldsUserNameAdd.text)) {
                errors.push("Pole nazwa użytkownika zawiera niepoprawne znaki. Dozwolone znaki: tylko małe litery oraz kropka '.'");
            }

            if (!validateEmptyField(fieldsExpiredAdd.text)) {
                errors.push("Pole data wygaśnięcia nie może być pusta.");
            } else if (!validateExpirationDate(fieldsExpiredAdd.text)) {
                errors.push("Pole data wygaśnięcia zawiera niepoprawne znaki. Dozwolony format daty YYYY-MM-DD HH:MM");
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeAdmin.addInternalUser(
                    fieldsIdEmpAdd.text,
                    fieldsIdRoleIdAdd.text,
                    fieldsUserNameAdd.text,
                    fieldsPasswordAdd.text,
                    fieldsExpiredAdd.text,
                );
            }
        }

    }

    Rectangle {
        id: idInputTextContainerPasswordAdd
        width: parent.width * 0.155
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.545

        TextInput {
            id: fieldsPasswordAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Hasło")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Hasło")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerUserNameAdd
        width: parent.width * 0.155
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38

        TextInput {
            id: fieldsUserNameAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa użytkownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa użytkownika")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerExpiredAdd
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
            id: fieldsExpiredAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Wygasa")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.012, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Wygasa")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoleIdAdd
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
            id: fieldsIdRoleIdAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID roli")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID roli")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerIdEmpAdd
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
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsIdEmpAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pracownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pracownika")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idMessages
        width: parent.width * 0.65 // 90% szerokości ramki
        height: parent.height * 0.17 // 10% wysokości ramki
        text: qsTr("")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.72
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        // verticalAlignment: Text.AlignVCenter
        verticalAlignment: TextEdit.AlignBottom   // kluczowa linia
        wrapMode: Text.WordWrap //
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.01, parent.height * 0.1)
    }

}

