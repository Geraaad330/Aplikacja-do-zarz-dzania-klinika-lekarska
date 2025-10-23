import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false

    Image {
        id: background
        // source: "images/background22_1920x1080.png"
        // source: "images/background_dark_4.png"
        source: (backendBridge && backendBridge.isDarkMode) ? "images/background_dark_4.png" : "images/background22_1920x1080.png"

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
        text: qsTr("Menu główne")
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.03 // Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true
        elide: Text.ElideRight
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
    }

    Rectangle {
        id: idRamka
        width: background.width * 0.13 // 13% szerokości tła
        height: background.height * 0.95 // 95% wysokości tła

        color: "transparent"
        border.color: "white"
        border.width: 5
        radius: 20

        anchors.left: id_quit.left
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
        width: Math.min(parent.width * 0.05, parent.height * 0.035)
        height: width
        radius: width * 0.1
        color: (backendBridge && backendBridge.isDarkMode)
               ? (checked ? "#118f39" : "#961c3d")
               : (checked ? "#ffde59" : "#D3D3D3")
        border.color: (backendBridge && backendBridge.isDarkMode)
                ? (checked ? "#22ff00" : "#ff0000")
                : (checked ? "#ffde59" : "#D3D3D3")
        border.width: width * 0.05
        anchors.left: idRamka.right
        anchors.leftMargin: idRamka.width * 0.4
        anchors.bottom: idRamka.bottom
        anchors.bottomMargin: idRamka.height * 0.03

        property bool checked: false
        signal toggled(bool checked)

        MouseArea {
            anchors.fill: parent
            onClicked: {
                customCheckBox.checked = !customCheckBox.checked
                customCheckBox.toggled(customCheckBox.checked)
                canvas.requestPaint()
            }
        }

        onCheckedChanged: {
            console.log("Checkbox state changed to: " + checked);
            geometryManager.fullscreen = checked;
        }

        Canvas {
            id: canvas
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height);
                if (customCheckBox.checked) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.2, height * 0.5);
                    ctx.lineTo(width * 0.4, height * 0.7);
                    ctx.lineTo(width * 0.8, height * 0.3);
                    ctx.strokeStyle = "#000000";
                    ctx.lineWidth = width * 0.1;
                    ctx.stroke();
                }
            }
        }

        Text {
            id: textFullSceen
            text: qsTr("Tryb pełnoekranowy")
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            anchors.leftMargin: width * 0.1
            font.pixelSize: parent.height * 0.8
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        Component.onCompleted: {
            customCheckBox.checked = geometryManager.fullscreen;
        }
    }

    Rectangle {
        id: checkBoxDarkMode
        width: Math.min(parent.width * 0.05, parent.height * 0.035)
        height: width
        radius: width * 0.1
        color: (backendBridge && backendBridge.isDarkMode)
               ? (checked ? "#118f39" : "#961c3d")
               : (checked ? "#ffde59" : "#D3D3D3")
        border.color: (backendBridge && backendBridge.isDarkMode)
                ? (checked ? "#22ff00" : "#ff0000")
                : (checked ? "#ffde59" : "#D3D3D3")
        border.width: width * 0.05
        anchors.left: customCheckBox.right
        anchors.leftMargin: customCheckBox.height * 10
        anchors.bottom: customCheckBox.bottom
        anchors.bottomMargin: customCheckBox.height * 0

        property bool checked: false

        MouseArea {
            anchors.fill: parent
            onClicked: {
                console.log("Kliknięto checkbox trybu ciemnego");
                checkBoxDarkMode.checked = !checkBoxDarkMode.checked;
                backendBridge.isDarkMode = checkBoxDarkMode.checked;
                canvasDark.requestPaint();
            }
        }

        Canvas {
            id: canvasDark
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height);
                if (checkBoxDarkMode.checked) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.2, height * 0.5);
                    ctx.lineTo(width * 0.4, height * 0.7);
                    ctx.lineTo(width * 0.8, height * 0.3);
                    ctx.strokeStyle = "#000000";
                    ctx.lineWidth = width * 0.1;
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
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        Component.onCompleted: {
            checkBoxDarkMode.checked = backendBridge.isDarkMode;
        }
    }

    Text {
        id: textMain
        text: qsTr("Witaj w aplikacji! - ekran główny")
        width: parent.width * 0.55
        height: parent.height * 0.11
        font.pixelSize: Math.min(parent.width * 0.025, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.07
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.15
        anchors.right: background.right
        anchors.rightMargin: background.width * 0.15
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Text {
        id: textUser1
        textFormat: Text.RichText
        text: "Zalogowany użytkownik: <i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.formattedUsername ? backendBridge.formattedUsername : "Nieznany") +
              "</span></b></i>"
        width: parent.width * 0.3
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textRole1
        textFormat: Text.RichText
        text: "Twoja rola w klinice: <i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.userRole ? backendBridge.userRole : "Nieznany") +
              "</span></b></i>"
        width: parent.width * 0.3
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.5
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textRoleNumber
        textFormat: Text.RichText
        text: "Indentyfikator roli: <i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.userRoleId ? backendBridge.userRoleId : "Nieznany") +
              "</span></b></i>"
        width: parent.width * 0.3
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.55
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textEmployeeNumber
        textFormat: Text.RichText
        text: "Indentyfikator pracownika: <i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.employeeId ? backendBridge.employeeId : "Nieznany") +
              "</span></b></i>"
        width: parent.width * 0.3
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.6
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textSpecialtyMain
        textFormat: Text.RichText
        text: "Twoje specjalności:"
        width: parent.width * 0.15
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.7
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textSpecialty
        textFormat: Text.RichText
        text: "<i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.specialties ? backendBridge.specialties : "Brak specjalizacji") +
              "</span></b></i>"
        wrapMode: Text.WordWrap
        width: parent.width * 0.3
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.75
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textTodayDate
        textFormat: Text.RichText
        text: "Data: <i><b><span style='color:" +
            ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
            (backendBridge.currentDate && backendBridge.currentDayName
                ? backendBridge.currentDate + " (" + backendBridge.currentDayName + ")"
                : "Brak daty i dnia tygodnia") +
            "</span></b></i>"
        width: parent.width * 0.2
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.25
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textTodayNumberAppointments
        textFormat: Text.RichText
        text: "Liczba dzisiejszych wizyt: <i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.todaysAppointments ? backendBridge.todaysAppointments : "Nieznana liczba wizyt") +
              "</span></b></i>"
        width: parent.width * 0.2
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.3
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textNumberAppointmentsForUser
        textFormat: Text.RichText
        text: "Liczba umówionych wizyt: <i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.appointmentsCountForUser ? backendBridge.appointmentsCountForUser : "0") +
              "</span></b></i>"
        width: parent.width * 0.2
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.35
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
    }

    Text {
        id: textAppointments
        textFormat: Text.RichText
        text: "Twoje najbliższe wizyty:"
        width: parent.width * 0.2
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.25
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38
    }

    Text {
        id: textAppointmentsList
        textFormat: Text.RichText
        text: "<i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.upcomingAppointments ? backendBridge.upcomingAppointments : "Brak specjalizacji") +
              "</span></b></i>"
        width: parent.width * 0.2
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.3
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38
    }

    Text {
        id: textMeetings
        textFormat: Text.RichText
        text: "Nadchodzące spotkania wewnętrzne:"
        width: parent.width * 0.25
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.52
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38
    }

    Text {
        id: textMeetingsList
        textFormat: Text.RichText
        text: "<i><b><span style='color:" +
              ((backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF") + ";'>" +
              (backendBridge.meetings ? backendBridge.meetings : "Brak specjalizacji") +
              "</span></b></i>"
        wrapMode: Text.WordWrap
        width: parent.width * 0.47
        height: parent.height * 0.05
        font.pixelSize: Math.min(parent.width * 0.015, parent.height * 0.1)
        color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.57
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38
    }

    Button {
        id: id_logout
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.12

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Wyloguj"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "Login.qml";
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }

    Button {
        id: id_quit
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.05

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Wyjdź z aplikacji"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            Qt.quit();
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }

    Button {
        id: idSchedule
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.4

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Harmonogram"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "ScheduleMainListAppointment.qml";
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }

    Button {
        id: idPatients
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.7

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Pacjenci"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "PatientsMainList.qml";
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }

    Button {
        id: idEmployees
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.6

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Pracownicy"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "EmployeeMainList.qml";
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }

    Button {
        id: idRoomsReservations
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.5

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Pokoje i rezerwacje"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.4)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "RoomsMainList.qml";
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }

    Button {
        id: idAdministrativeSettings
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: parent.width * 0.018
        anchors.bottomMargin: parent.height * 0.3

        contentItem: Text {
            color: (backendBridge && backendBridge.isDarkMode) ? "#FFFFFF" : "#000000"
            text: "Ustawienia administracyjne"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.3)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "AdminSettingsMainUsersList.qml";
        }

        background: Rectangle {
            color: (backendBridge && backendBridge.isDarkMode) ? "#961c3d" : "#ffe599"
            radius: 15
        }
    }


}
