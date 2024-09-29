import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

# PyQt6 Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FDMS")
        self.setGeometry(50, 50, 1200, 700)

# Main function to run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())