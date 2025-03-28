
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import QTimer


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.btn = QPushButton('Refresh', self)
        self.btn.clicked.connect(self.refresh)
        self.btnTimer = QTimer(self)
        self.btnTimer.setInterval(2000)
        self.btnTimer.setSingleShot(True)
        self.btnTimer.timeout.connect(self.timerTimeout)
        self.btn.setEnabled(False)

    def refresh(self):
        self.btn.setEnabled(False)
        self.btnTimer.start()
        print('Button was pressed, starting timer')

    def timerTimeout(self):
        self.btn.setEnabled(True)
        print('In Timer TimeOut')


if __name__ == "__main__":
    app = QApplication([])
    window = Widget()
    window.show()
    sys.exit(app.exec())
