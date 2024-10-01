import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, QRect

from map import create_map

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FDMS")
        self.setGeometry(20, 30, 1200, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tab_widget = QTabWidget(parent=self.central_widget)
        self.tab_widget.setGeometry(QRect(8, 3, 1190, 740))

        self.main_tab()
        self.setting_tab()
        
        # Initialize the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_map)
        self.timer.start(120000)  # 120000 milliseconds = 2 minutes

        # Initial map update
        self.update_map()
    
    def main_tab(self):
        self.tab_main = QWidget()
        
        self.web_view = QWebEngineView(self.tab_main)
        self.web_view.setGeometry(QRect(0, 0, 800, 710))
        
        self.data_widget = QWidget(self.tab_main)
        self.data_widget.setGeometry(QRect(950, 20, 350, 710))
        
        
        self.tab_widget.addTab(self.tab_main, "Main")
    
    def setting_tab(self):
        self.tab_setting = QWidget()
        self.tab_widget.addTab(self.tab_setting, "Setting")

    def update_map(self):
        # In a real application, you would fetch new coordinates here
        # For this example, we'll use static coordinates
        latitude, longitude = 35.591556, 53.399074
        map_html = create_map(latitude, longitude)
        self.web_view.setHtml(map_html)
        print("Map updated")  # Optional: for debugging

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec())