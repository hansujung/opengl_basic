import sys, datetime
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView

import outdoorView as outdoor
import indoorView as indoor
import dustView as dust


class Window(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        self.outWidget = outdoor.GLWidget()
        self.inWidget = indoor.GLWidget()

        self.dustWidget = dust.dustWidget()

        self.weatherWidget = QWebEngineView()
        self.weatherWidget.setUrl(QUrl("http://localhost/openapi_w.html"))

        self.trafficWidget = QWebEngineView()
        self.trafficWidget.setUrl(QUrl("http://localhost/openapi_c.html"))

        self.floorWidget = QLabel()
        self.floorWidget.setText('15F')
        self.floorWidget.setStyleSheet("font-family: Arial; padding: 6px; "
                                      "font-style:normal; font-size: 20pt; font-weight: bold; color: #EEEEEE;")

        self.areaWidget = QLabel()
        self.areaWidget.setText('Gyeonggi-do Yeongtong-gu, Suwon-si Gwanggyo')
        self.areaWidget.setStyleSheet("font-family: Arial; padding: 6px; "
                                       "font-style:normal; font-size: 20pt; font-weight: bold; color: #EEEEEE;")

        mainLayout = QHBoxLayout()

        ipsLayout = QHBoxLayout()

        ips1Layout = QVBoxLayout()
        ips1Layout.addWidget(self.weatherWidget)

        ips2Layout = QVBoxLayout()
        ips2Layout.addWidget(self.floorWidget, 0.5)
        ips2Layout.addWidget(self.inWidget, 4)
        ips2Layout.addWidget(self.dustWidget, 1)

        ipsLayout.addLayout(ips1Layout, 0.7)
        ipsLayout.addLayout(ips2Layout, 1)

        opsLayout = QHBoxLayout()

        ops1Layout = QVBoxLayout()
        ops1Layout.addWidget(self.areaWidget, 0.5)
        ops1Layout.addWidget(self.outWidget, 5)

        ops2Layout = QVBoxLayout()
        ops2Layout.addWidget(self.trafficWidget)

        opsLayout.addLayout(ops1Layout, 2)
        opsLayout.addLayout(ops2Layout, 1)

        mainLayout.addLayout(ipsLayout, 1)
        mainLayout.addLayout(opsLayout, 1)

        self.setLayout(mainLayout)

        self.setWindowTitle("opengl")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    # window.setAutoFillBackground(True)
    window.setStyleSheet("background-color:#0C0D0E;")
    window.setGeometry(0.1, 0.1, 3840, 1070)
    window.show()
    sys.exit(app.exec_())
