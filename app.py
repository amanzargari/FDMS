import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, QRect

from gps_sim import GPSSimulator
from map import OSMHandler, RequestInterceptor, load_map, start_http_server
from camera import Camera, CameraWidget


class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FDMS")
        self.setGeometry(20, 30, 1200, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tab_widget = QTabWidget(parent=self.central_widget)
        self.tab_widget.setGeometry(QRect(8, 3, 1190, 740))
        
        self.tab_main = QWidget()
        self.tab_setting = QWidget()
        
        self.web_view = QWebEngineView(self.tab_main)
        self.web_view.setGeometry(QRect(0, 0, 800, 710))

        # GPS
        self.gps_sim = GPSSimulator()
        
        # Map
        handler = OSMHandler()
        start_http_server()
        interceptor = RequestInterceptor(handler.ways)
        self.web_view.page().profile().setUrlRequestInterceptor(interceptor)
        html = load_map(self.gps_sim.latitude, self.gps_sim.longitude)
        self.web_view.setHtml(html)
        # Initial map update
        self.update_map()
        # Initialize the timer
        self.map_timer = QTimer(self)
        self.map_timer.timeout.connect(self.update_map)
        self.map_timer.start(1000)
        
        # Camera
        self.camera = Camera(camera_id=0, resize=(400, 400))
        
        # Create Tabs
        self.main_tab()
        self.setting_tab()
    
    def main_tab(self):
        self.data_widget = QWidget(self.tab_main)
        self.data_widget.setGeometry(QRect(950, 20, 350, 710))
        
        self.camera_widget = CameraWidget(self.camera, self.tab_main)
        self.camera_widget.setGeometry(QRect(820, 0, 400, 400))
        
        self.tab_widget.addTab(self.tab_main, "Main")
    
    def setting_tab(self):
        self.tab_widget.addTab(self.tab_setting, "Setting")

    def update_map(self):
        lat, lon, speed, heading = self.gps_sim.get_next_reading()
        self.web_view.page().runJavaScript(f"updateMarker({lat}, {lon}, {speed}, {heading});")
    
    def closeEvent(self, event):
        # Release the camera when closing the application
        self.camera.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec())