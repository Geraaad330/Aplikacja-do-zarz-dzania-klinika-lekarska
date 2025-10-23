import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false

    Component.onCompleted: {
        console.log("Setting current screen to AdminSettingsMainUsers");
        backendBridge.currentScreen = "AdminSettingsMainUsers";
        backendBridge.checkAccessToAdminUsersView();
        bridgeAdmin.updateUserList(); // Wywołanie funkcji
    }

    Connections {
        target: backendBridge

        function onAccessGranted() {
            console.log("[QML] Dostęp przyznany. Przechodzenie do AdminSettingsMainUsersList.");
            mainViewLoader.source = "AdminSettingsMainUsersList.qml";
        }

        function onAccessDenied(errorMessage) {
            console.log("[QML] Dostęp zabroniony: " + errorMessage);
            prescriptionErrorText.text = errorMessage;
            prescriptionErrorPopup.open();
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
            mainViewLoader.source = "Dashboard.qml"; // Zmiana widoku na główny
        }

        // Kolumna do wyświetlania treści
        Column {
            anchors.centerIn: parent
            spacing: 20

            // Tekst błędu
            Text {
                id: prescriptionErrorText
                text: "Brak uprawnień do ustawień administracyjnych."
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
                    mainViewLoader.source = "Dashboard.qml";
                }

                background: Rectangle {
                    color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
                    radius: 5 // Zaokrąglenie rogów o 15 pikseli
                }
            }

        }
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
        text: qsTr("Panel ustawienia administracyjne - użytkownicy")
        width: parent.width * 0.6
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.027, parent.height * 0.1)
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
            color: backendBridge.currentScreen === "AdminSettingsMainUsers"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
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
            idButtonMainUsers.isClicked = true;

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

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "AdminSettingsUsersCRUD.qml";

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

    Item {
        id: mainContainerUsers
        anchors.fill: parent

        // Definiujemy szerokości kolumn dla tabeli użytkowników
        property real colWidthUserId: 0.04
        property real colWidthEmployeeId: 0.045
        property real colWidthEmployeeName: 0.12
        property real colWidthRoleId: 0.05
        property real colWidthRoleName: 0.12
        property real colWidthUsername: 0.11
        property real colWidthIsActive: 0.07
        property real colWidthCreatedAt: 0.11
        property real colWidthLastLogin: 0.11
        property real colWidthExpired: 0.1

        Column {
            id: listContainerUsers
            anchors {
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            width: parent.width * 0.8
            height: parent.height * 0.8
            anchors.topMargin: parent.height * 0.14
            anchors.leftMargin: parent.width * 0.04
            anchors.rightMargin: parent.width * 0.02
            anchors.bottomMargin: parent.height * 0.13
            spacing: 5

            // Nagłówki – wiersz z etykietami kolumn
            Row {
                id: headerRowUsers
                width: listContainerUsers.width
                height: listContainerUsers.height * 0.08
                spacing: 10

                Text {
                    text: "ID użytk."
                    width: headerRowUsers.width * mainContainerUsers.colWidthUserId
                    font.pixelSize: 14
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "ID pracow."
                    width: headerRowUsers.width * mainContainerUsers.colWidthEmployeeId
                    font.pixelSize: 14
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Imię i nazwisko"
                    width: headerRowUsers.width * mainContainerUsers.colWidthEmployeeName
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "ID roli"
                    width: headerRowUsers.width * mainContainerUsers.colWidthRoleId
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Rola"
                    width: headerRowUsers.width * mainContainerUsers.colWidthRoleName
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Nazwa użytkownika"
                    width: headerRowUsers.width * mainContainerUsers.colWidthUsername
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
                Text {
                    text: "Aktywny"
                    width: headerRowUsers.width * mainContainerUsers.colWidthIsActive
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Utworzono"
                    width: headerRowUsers.width * mainContainerUsers.colWidthCreatedAt
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Ostatnie logowanie"
                    width: headerRowUsers.width * mainContainerUsers.colWidthLastLogin
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Wygasa"
                    width: headerRowUsers.width * mainContainerUsers.colWidthExpired
                    font.pixelSize: 17
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
            }

            // ScrollView z listą użytkowników
            ScrollView {
                id: idScrollViewUsers
                width: listContainerUsers.width
                height: listContainerUsers.height * 0.92
                clip: true

                ListView {
                    id: usersListView
                    anchors.fill: parent
                    model: usersModel

                    delegate: Item {
                        width: usersListView.width
                        height: 50
                        Row {
                            spacing: 10
                            anchors.fill: parent

                            Text {
                                text: model.user_id
                                width: usersListView.width * mainContainerUsers.colWidthUserId
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.employee_id
                                width: usersListView.width * mainContainerUsers.colWidthEmployeeId
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.employee_name
                                width: usersListView.width * mainContainerUsers.colWidthEmployeeName
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.role_id
                                width: usersListView.width * mainContainerUsers.colWidthRoleId
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.role_name
                                width: usersListView.width * mainContainerUsers.colWidthRoleName
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.username
                                width: usersListView.width * mainContainerUsers.colWidthUsername
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.is_active === 1 ? "Aktywny" : "Nieaktywny"
                                width: usersListView.width * mainContainerUsers.colWidthIsActive
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.created_at
                                width: usersListView.width * mainContainerUsers.colWidthCreatedAt
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.last_login !== null ? model.last_login : "Brak logowania"
                                width: usersListView.width * mainContainerUsers.colWidthLastLogin
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.expired
                                width: usersListView.width * mainContainerUsers.colWidthExpired
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                        }
                    }
                }
            }
        }

        ListModel {
            id: usersModel
        }
    }


    // Po zmianie listy użytkowników, aktualizujemy model
    Connections {
        target: bridgeAdmin
        function onUserListChanged(users) {
            usersModel.clear();
            for (let user of users) {
                for (let key in user) {
                    if (user[key] === undefined || user[key] === null) {
                        user[key] = "Brak danych";
                    }
                }
                usersModel.append(user);
            }
        }
    }

}

