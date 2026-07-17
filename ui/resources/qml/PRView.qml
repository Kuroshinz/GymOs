import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#0B0F19"
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 16

        // Header Section
        ColumnLayout {
            spacing: 4
            Layout.fillWidth: true

            Label {
                text: "Personal Records"
                color: "#F1F5F9"
                font.pixelSize: 28
                font.bold: true
                font.family: "Segoe UI"
            }

            Label {
                text: "Your best performances across all exercises"
                color: "#94A3B8"
                font.pixelSize: 14
                font.family: "Segoe UI"
            }
        }

        // Scrollable Grid of cards
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Flow {
                width: parent.width
                spacing: 16
                padding: 4

                Repeater {
                    model: prModel

                    Rectangle {
                        width: (parent.width - 16) / 2 - 4
                        height: 110
                        radius: 12
                        color: hoverHandler.hovered ? "#1E293B" : "#131C2E"
                        border.color: hoverHandler.hovered ? typeColor(modelData.pr_type) : "#1E293B"
                        border.width: 1

                        HoverHandler {
                            id: hoverHandler
                        }

                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 4

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Label {
                                    text: modelData.exercise_name
                                    color: "#F1F5F9"
                                    font.pixelSize: 15
                                    font.bold: true
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                    font.family: "Segoe UI"
                                }

                                Rectangle {
                                    radius: 6
                                    color: "#0F172A"
                                    implicitWidth: typeLabel.implicitWidth + 16
                                    implicitHeight: typeLabel.implicitHeight + 4

                                    Label {
                                        id: typeLabel
                                        anchors.centerIn: parent
                                        text: typeText(modelData.pr_type)
                                        color: typeColor(modelData.pr_type)
                                        font.pixelSize: 10
                                        font.bold: true
                                        font.family: "Segoe UI"
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Label {
                                    text: modelData.display_value
                                    color: typeColor(modelData.pr_type)
                                    font.pixelSize: 22
                                    font.bold: true
                                    font.family: "Segoe UI"
                                }

                                Label {
                                    text: modelData.improvement_text
                                    color: "#10B981"
                                    font.pixelSize: 12
                                    font.bold: true
                                    visible: modelData.improvement_text !== ""
                                    font.family: "Segoe UI"
                                }
                            }

                            Label {
                                text: modelData.date_text
                                color: "#64748B"
                                font.pixelSize: 11
                                font.family: "Segoe UI"
                            }
                        }
                    }
                }
            }
        }
    }

    function typeColor(type) {
        switch (type) {
            case "weight": return "#10B981";
            case "reps": return "#3B82F6";
            case "volume": return "#F59E0B";
            case "e1rm": return "#8B5CF6";
            default: return "#94A3B8";
        }
    }

    function typeText(type) {
        switch (type) {
            case "weight": return "Weight PR";
            case "reps": return "Rep PR";
            case "volume": return "Volume PR";
            case "e1rm": return "Est. 1RM";
            default: return type.toUpperCase();
        }
    }
}
