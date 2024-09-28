import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

# PyQt6 Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FDMs")
        self.setGeometry(100, 100, 800, 600)

# Main function to run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())