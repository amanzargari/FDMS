import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QTextEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, QRect

from gps_sim import GPSSimulator
from map import OSMHandler, RequestInterceptor, load_map, start_http_server
from camera import Camera, CameraWidget
from timedate import TimeDate

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
        
        # Camera
        self.camera = Camera(camera_id=0, resize=(400, 400))
        
        # Create Tabs
        self.main_tab()
        self.setting_tab()
        
        # Create TimeDate instance
        self.time_date = TimeDate()

        # Create a text box for displaying information
        self.info_text_box = QTextEdit(self.tab_main)
        self.info_text_box.setGeometry(QRect(820, 410, 350, 300))
        self.info_text_box.setReadOnly(True)  # Make it read-only
        
        # Initialize the timer
        self.map_timer = QTimer(self)
        self.map_timer.timeout.connect(self.update_map)
        self.map_timer.start(1000)
        
        self.collected_frames = []
    
    def main_tab(self):
        self.data_widget = QWidget(self.tab_main)
        self.data_widget.setGeometry(QRect(950, 20, 350, 710))
        
        self.camera_widget = CameraWidget(self.camera, self.tab_main)
        self.camera_widget.setGeometry(QRect(820, 0, 400, 400))
        self.camera_widget.frames_collected.connect(self._store_frames)
        
        self.tab_widget.addTab(self.tab_main, "Main")
    
    def setting_tab(self):
        self.tab_widget.addTab(self.tab_setting, "Setting")

    def update_map(self):
        lat, lon, speed, heading = self.gps_sim.get_next_reading()
        self.web_view.page().runJavaScript(f"updateMarker({lat}, {lon}, {speed}, {heading});")
        
        # Update the text box with the latest GPS data and time/date
        current_time_str = self.time_date.get_datetime_str()
        persian_date = self.time_date.persina_date()
        persian_date_str = f"{persian_date[0]}/{persian_date[1]}/{persian_date[2]} - {self.time_date.persian_week_day()}"  # Format: YYYY/MM/DD
        info_text = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
        <h2 style="color: #4CAF50;">GPS Information</h2>
        <p><b>Latitude:</b> <span style="color: #2196F3;">{lat:.6f}</span></p>
        <p><b>Longitude:</b> <span style="color: #2196F3;">{lon:.6f}</span></p>
        <p><b>Speed:</b> <span style="color: #2196F3;">{speed:.1f} km/h</span></p>
        <hr style="border: 1px solid #4CAF50;">
        <h3 style="color: #4CAF50;">Date and Time</h3>
        <p><b>Gregorian:</b> <span style="color: #FF9800;">{current_time_str}</span></p>
        <p><b>Persian Date:</b> <span style="color: #FF9800;">{persian_date_str}</span></p>
    </div>
    """
        self.info_text_box.setHtml(info_text)
    
    def closeEvent(self, event):
        # Release the camera when closing the application
        self.map_timer.stop()
        self.camera_widget.timer.stop()
        self.camera.release()
        event.accept()
        
    def _store_frames(self, frames):
        self.collected_frames = frames

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec())