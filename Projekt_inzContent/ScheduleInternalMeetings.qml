import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false

    Component.onCompleted: {
        console.log("Setting current screen to Schedule");
        backendBridge.currentScreen = "Schedule";
        bridgeRoom.updateMeetingTypesList();
        bridgeRoom.updateInternalMeetingsList();
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
        text: qsTr("harmonogram")
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
        text: qsTr("Zarządzanie harmonogramem - lista spotkań wewnętrzynych")
        width: parent.width * 0.55
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.02, parent.height * 0.1)
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
        id: idSpotkaniaWew
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.5 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Spotkania wewnętrzne"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.34)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "ScheduleInternalMeetings.qml";
            idKalendarz.isClicked = true;
        }

        background: Rectangle {
            color: backendBridge.currentScreen === "Schedule"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
        }

    }

    Button {
        id: idSpotkaniaParticipantsList
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.3 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista uczestników"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.4)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "ScheduleParticipantsList.qml";
        }


        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }

    Button {
        id: idSpotkaniaWewCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.4 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie spotkaniami wew."
            font.pixelSize: Math.min(parent.width * 0.065, parent.height * 0.34)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "ScheduleInternalParticipantsCRUD.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }


    Button {
        id: idKalendarz
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.6// Margines od dolnej krawędzi (2% wy

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
            text: "Zarządzanie wizytami"
            font.pixelSize: Math.min(parent.width * 0.085, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na
            mainViewLoader.source = "ScheduleAppointmentCRUD.qml";
            // Zmieniamy stan isClicked na true

        }


    }

    Button {
        id: idWizyty
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.7 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Wizyty"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }


        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "ScheduleMainListAppointment.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }


    Item {
        id: mainContainerMeetingTypes
        anchors.fill: parent

        // Definiujemy szerokości kolumn
        property real colWidthMeetingTypeId: 0.15
        property real colWidthMeetingType: 1

        Column {
            id: listContainerMeetingTypes
            anchors {
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            width: parent.width * 0.23
            height: parent.height * 0.8
            anchors.topMargin: parent.height * 0.14
            anchors.leftMargin: parent.width * 0.04
            anchors.rightMargin: parent.width * 0.61
            anchors.bottomMargin: parent.height * 0.13
            spacing: 15

            // Nagłówki tabeli typów spotkań
            Row {
                id: headerRowMeetingTypes
                width: listContainerMeetingTypes.width
                height: listContainerMeetingTypes.height * 0.08  // 8% wysokości kontenera
                spacing: 20

                Text {
                    text: "Id typu spotkania"
                    width: headerRowMeetingTypes.width * mainContainerMeetingTypes.colWidthMeetingTypeId
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Nazwa Typu Spotkania"
                    width: headerRowMeetingTypes.width * mainContainerMeetingTypes.colWidthMeetingType
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
            }

            // ScrollView z listą typów spotkań
            ScrollView {
                id: idScrollViewMeetingTypes
                width: listContainerMeetingTypes.width
                height: listContainerMeetingTypes.height * 0.92
                clip: true

                ListView {
                    id: meetingTypesListView
                    anchors.fill: parent
                    model: meetingTypesModel

                    delegate: Item {
                        width: meetingTypesListView.width
                        height: 60
                        Row {
                            spacing: 20
                            anchors.fill: parent

                            Text {
                                text: model.meeting_type_id
                                width: meetingTypesListView.width * mainContainerMeetingTypes.colWidthMeetingTypeId
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.meeting_type
                                width: meetingTypesListView.width * mainContainerMeetingTypes.colWidthMeetingType
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                        }
                    }
                }
            }

            ListModel {
                id: meetingTypesModel
            }

            // Obsługa sygnału zmiany listy typów spotkań
            Connections {
                target: bridgeRoom
                function onMeetingTypesListChanged(meetingTypes) {
                    meetingTypesModel.clear();
                    for (let i = 0; i < meetingTypes.length; i++) {
                        let meetingType = meetingTypes[i];

                        // Obsługa brakujących danych
                        if (!meetingType.meeting_type_id) {
                            meetingType.meeting_type_id = "Brak danych";
                        }
                        if (!meetingType.meeting_type) {
                            meetingType.meeting_type = "Brak danych";
                        }

                        meetingTypesModel.append(meetingType);
                    }
                }
            }
        }
    }


    Item {
        id: mainContainerInternalMeetings
        anchors.fill: parent

        // Definiujemy szerokości kolumn
        property real colWidthMeetingId: 0.08
        property real colWidthMeetingTypeId: 0.08
        property real colWidthReservationId: 0.07
        property real colWidthRoomNumber: 0.05
        property real colWidthMeetingDate: 0.17
        property real colWidthNotes: 0.25
        property real colWidthMeetingStatus: 0.15

        Column {
            id: listContainerInternalMeetings
            anchors {
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            width: parent.width * 0.55
            height: parent.height * 0.8
            anchors.topMargin: parent.height * 0.14
            anchors.leftMargin: parent.width * 0.15
            anchors.rightMargin: parent.width * 0.035
            anchors.bottomMargin: parent.height * 0.13
            spacing: 15

            // Nagłówki tabeli spotkań wewnętrznych
            Row {
                id: headerRowInternalMeetings
                width: listContainerInternalMeetings.width
                height: listContainerInternalMeetings.height * 0.08  // 8% wysokości kontenera
                spacing: 20

                Text {
                    text: "Id Spotkania"
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthMeetingId
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Id Typu Spotkania"
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthMeetingTypeId
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Id Rezerw."
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthReservationId
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Numer Pokoju"
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthRoomNumber
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Data Spotkania"
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthMeetingDate
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 2
                }
                Text {
                    text: "Notatki"
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthNotes
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 10
                }
                Text {
                    text: "Status Spotkania"
                    width: headerRowInternalMeetings.width * mainContainerInternalMeetings.colWidthMeetingStatus
                    font.pixelSize: 15
                    verticalAlignment: Text.AlignVCenter
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    wrapMode: Text.WordWrap
                    clip: true
                    maximumLineCount: 5
                }
            }

            // ScrollView z listą spotkań wewnętrznych
            ScrollView {
                id: idScrollViewInternalMeetings
                width: listContainerInternalMeetings.width
                height: listContainerInternalMeetings.height * 0.92
                clip: true

                ListView {
                    id: internalMeetingsListView
                    anchors.fill: parent
                    model: internalMeetingsModel

                    delegate: Item {
                        width: internalMeetingsListView.width
                        height: 60
                        Row {
                            spacing: 20
                            anchors.fill: parent

                            Text {
                                text: model.meeting_id
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthMeetingId
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.fk_meeting_type_id
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthMeetingTypeId
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.fk_reservation_id
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthReservationId
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.room_number
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthRoomNumber
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.meeting_date
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthMeetingDate
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.notes
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthNotes
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 10
                            }
                            Text {
                                text: model.internal_meeting_status
                                width: internalMeetingsListView.width * mainContainerInternalMeetings.colWidthMeetingStatus
                                font.pixelSize: 15
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 10
                            }
                        }
                    }
                }
            }

            ListModel {
                id: internalMeetingsModel
            }

            Connections {
                target: bridgeRoom
                function onInternalMeetingsListChanged(meetings) {
                    internalMeetingsModel.clear();
                    for (let i = 0; i < meetings.length; i++) {
                        internalMeetingsModel.append(meetings[i]);
                    }
                }
            }
        }
    }



}

