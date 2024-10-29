import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QTextEdit, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, QRect, Qt
from PyQt6.QtGui import QPixmap
import numpy as np

from gps_sim import GPSSimulator
from map import OSMHandler, RequestInterceptor, load_map, start_http_server
from camera import Camera, CameraWidget
from timedate import TimeDate
from weather import Weather
from fuzzy import FuzzyInference
from video_classifier import VideoClassifier, VideoClassificationThread
from config import DRIVING_ICONS

class MainWindows(QMainWindow):
    """
    Main application window for the FDMS (Fleet Driver Monitoring System).
    Attributes:
        central_widget (QWidget): The central widget of the main window.
        tab_widget (QTabWidget): The tab widget containing different tabs.
        tab_main (QWidget): The main tab widget.
        tab_setting (QWidget): The settings tab widget.
        web_view (QWebEngineView): The web view for displaying the map.
        gps_sim (GPSSimulator): The GPS simulator instance.
        camera (Camera): The camera instance for capturing video.
        time_date (TimeDate): The time and date instance.
        info_text_box (QTextEdit): The text box for displaying information.
        map_timer (QTimer): The timer for updating the map.
        collected_frames (list): The list of collected frames from the camera.
        weather (Weather): The weather instance for fetching weather data.
        weather_timer (QTimer): The timer for updating weather information.
        weather_info_text_box (QTextEdit): The text box for displaying weather information.
        fuzzy_inference (FuzzyInference): The fuzzy inference system instance.
        fuzzy_timer (QTimer): The timer for running fuzzy inference.
        video_classifier (VideoClassifier): The video classifier instance.
        video_classification_thread (VideoClassificationThread): The thread for video classification.
        drowsy_value (float): The drowsiness value from video classification.
        video_classifier_timer (QTimer): The timer for running video classification.
        risk_icon_label (QLabel): The label for displaying the driving risk icon.
    Methods:
        __init__(): Initializes the main window and its components.
        main_tab(): Creates and sets up the main tab.
        setting_tab(): Creates and sets up the settings tab.
        update_weather(): Updates the weather information.
        update_map(): Updates the map with the latest GPS data.
        _video_classification(): Runs the video classification process.
        update_classification_result(label: np.ndarray): Updates the classification result.
        _fuzzy_inference(): Runs the fuzzy inference process.
        closeEvent(event): Handles the close event of the main window.
        _store_frames(frames): Stores the collected frames from the camera.
        update_driving_risk_icon(state: str): Updates the driving risk icon based on the given state.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fuzzy-based Driver Monitoring System")
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
        self.camera = Camera(camera_id=0, resize=(400, 350), fake=True)
        
        # Create Tabs
        self.main_tab()
        self.setting_tab()
        
        # Create TimeDate instance
        self.time_date = TimeDate(solar_hijri=False)

        # Create a text box for displaying information
        self.info_text_box = QTextEdit(self.tab_main)
        self.info_text_box.setGeometry(QRect(820, 355, 350, 150))
        self.info_text_box.setReadOnly(True)  # Make it read-only
        
        # Initialize the map timer
        self.map_timer = QTimer(self)
        self.map_timer.timeout.connect(self.update_map)
        self.map_timer.start(1000)
        
        self.collected_frames = []
        
        # Wehather
        self.weather = Weather()
        
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(1000 * 60 * 10)  # Update weather every 10 minutes
        
        self.weather_info_text_box = QTextEdit(self.tab_main)
        self.weather_info_text_box.setGeometry(QRect(820, 505, 350, 150))
        self.weather_info_text_box.setReadOnly(True)
        
        self.update_weather()
        
        # Fuzzy System
        self.fuzzy_inference = FuzzyInference()
        
        self.fuzzy_timer = QTimer(self)
        self.fuzzy_timer.timeout.connect(self._fuzzy_inference)
        self.fuzzy_timer.start(1000 * 30) # Run the fuzzy inference every half minute
        
        
        # Video Classifier
        self.video_classifier = VideoClassifier()
        
        self.video_classification_thread = VideoClassificationThread(self.video_classifier)
        self.video_classification_thread.classification_done.connect(self.update_classification_result)
        
        self.drowsy_value = 0.0
        self.video_classifier_timer = QTimer(self)
        self.video_classifier_timer.timeout.connect(self._video_classification)
        self.video_classifier_timer.start(1000 * 60 * 1)  # Run the video classification every 5 minutes
        
        # Driving risk icon
        self.risk_icon_label = QLabel(self.tab_main)
        self.risk_icon_label.setGeometry(QRect(650, 10, 150, 150))
        self.update_driving_risk_icon('very_low')
    
    def main_tab(self) -> None:
        """
        Initializes the main tab of the application.
        This method sets up the main tab by creating and configuring the data widget 
        and the camera widget. It also connects the camera widget's frames_collected 
        signal to the _store_frames method and adds the main tab to the tab widget.
        Attributes:
            data_widget (QWidget): A widget to display data on the main tab.
            camera_widget (CameraWidget): A widget to display camera feed on the main tab.
        """
        self.data_widget = QWidget(self.tab_main)
        self.data_widget.setGeometry(QRect(950, 20, 350, 710))
        
        self.camera_widget = CameraWidget(self.camera, self.tab_main)
        self.camera_widget.setGeometry(QRect(820, 0, 400, 350))
        self.camera_widget.frames_collected.connect(self._store_frames)
        
        self.tab_widget.addTab(self.tab_main, "Main")
    
    def setting_tab(self) -> None:
        """
        Adds the 'Setting' tab to the tab widget.

        This method creates a new tab labeled 'Setting' and adds it to the 
        tab widget of the application.
        """
        self.tab_widget.addTab(self.tab_setting, "Setting")
    
    def update_weather(self) -> None:
        """
        Updates the weather information by fetching the latest GPS coordinates and 
        retrieving the corresponding weather data. The weather information is then 
        formatted into an HTML string and displayed in the weather information text box.
        The method performs the following steps:
        1. Retrieves the next GPS reading (latitude and longitude).
        2. Updates the weather data using the retrieved coordinates.
        3. Fetches the main weather description, temperature, humidity, city, and country.
        4. Formats the weather information into an HTML string.
        5. Sets the formatted HTML string to the weather information text box.
        Returns:
            None
        """
        lat, lon = self.gps_sim.get_next_reading()[:2]
        self.weather.update(lat, lon)
        
        weather_main = self.weather.get_weather_main()
        temp = self.weather.get_temp()
        humidity = self.weather.get_humidity()
        city, country = self.weather.get_city_country()
        
        weather_text = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
            <h3 style="color: #4CAF50;">Weather Information</h3>
            <p><b>City:</b> <span style="color: #2196F3;">{city}, {country}</span></p>
            <p><b>Weather:</b> <span style="color: #2196F3;">{weather_main}</span></p>
            <p><b>Temperature:</b> <span style="color: #2196F3;">{temp:.1f}°C</span></p>
            <p><b>Humidity:</b> <span style="color: #2196F3;">{humidity}%</span></p>
        </div>
        """
        self.weather_info_text_box.setHtml(weather_text)

    def update_map(self) -> None:
        """
        Updates the map with the latest GPS data and updates the text box with the latest GPS data and time/date.
        This method retrieves the next GPS reading (latitude, longitude, speed, and heading) from the GPS simulator,
        updates the map marker using JavaScript, and updates the text box with the latest GPS data, current date and time,
        and driver drowsiness information.
        Returns:
            None
        """
        lat, lon, speed, heading = self.gps_sim.get_next_reading()
        self.web_view.page().runJavaScript(f"updateMarker({lat}, {lon}, {speed}, {heading});")
        
        # Update the text box with the latest GPS data and time/date
        current_time_str = self.time_date.get_datetime_str()
        weekday = self.time_date.gregorian_week_day()
        info_text = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
            <p><b>Speed:</b> <span style="color: #2196F3;">{speed:.1f} km/h</span></p>
            <p><b>Date and Time:</b> <span style="color: #FF9800;">{current_time_str} - {weekday}</span></p>
            <p><b>Driver Drowsiness: </b> <span style="color: #FF9800;">{self.drowsy_value*100:.2f}%</span></p>
        </div>
        """
        self.info_text_box.setHtml(info_text)
        
    def _video_classification(self) -> None:
        """
        Perform video classification on collected frames.
        This method checks if there are any collected frames. If there are no frames,
        it returns immediately. Otherwise, it sets the collected frames to the 
        video classification thread and starts the thread.
        Returns:
            None
        """
        if len(self.collected_frames) == 0:
            return
        
        self.video_classification_thread.set_frames(self.collected_frames)
        self.video_classification_thread.start()
    
    def update_classification_result(self, label:np.ndarray) -> None:
        """
        Updates the classification result by setting the drowsy_value attribute.

        Args:
            label (np.ndarray): A numpy array where the second element represents the drowsy value.
        """
        self.drowsy_value = float(label[1])
    
    def _fuzzy_inference(self):
        """
        Perform fuzzy inference to determine driving risk based on various factors.

        This method retrieves the current speed, drowsiness level, weather condition,
        day of the week, and hour of the day, and then performs a fuzzy inference
        to calculate the driving risk. The result is printed and used to update the
        driving risk icon.

        Returns:
            None
        """
        speed = self.gps_sim.get_next_reading()[2]
        drowsiness = self.drowsy_value
        weather = self.weather.weather_id_to_condition_number(self.weather.get_weather_id())
        week_day = self.time_date.get_week_day()
        hour = self.time_date.get_hour()
        print(f"Speed: {speed}, Drowsiness: {drowsiness}, Weather: {weather}, Week Day: {week_day}, Hour: {hour}")
        result = self.fuzzy_inference(hour=hour, day=week_day, weather=weather, speed=speed, sleep=drowsiness)
        print(result)
        self.update_driving_risk_icon(result)
    
    def closeEvent(self, event):
        """
        Handles the close event for the application.

        This method is called when the application window is about to close.
        It stops various timers and threads to ensure a clean shutdown.

        Args:
            event (QCloseEvent): The close event that triggered this method.
        """
        self.map_timer.stop()
        self.camera_widget.timer.stop()
        self.camera.release()
        self.weather_timer.stop()
        self.fuzzy_timer.stop()
        self.video_classification_thread.quit()
        self.video_classification_thread.wait()
        event.accept()
        
    def _store_frames(self, frames):
        """
        Stores the given frames in the collected_frames attribute.

        Args:
            frames (list): A list of frames to be stored.
        """
        self.collected_frames = frames
    
    def update_driving_risk_icon(self, state:str) -> None:
        """
        Updates the driving risk icon based on the provided state.
        Args:
            state (str): The driving risk state. Expected values are 'very_low', 'low', 
                         'medium', 'high', or 'very_high'.
        Returns:
            None
        """
        if state == 'very_low':
            pixmap = QPixmap(DRIVING_ICONS.very_low)
        elif state == 'low':
            pixmap = QPixmap(DRIVING_ICONS.low)
        elif state == 'medium':
            pixmap = QPixmap(DRIVING_ICONS.medium)
        elif state == 'high':
            pixmap = QPixmap(DRIVING_ICONS.high)
        elif state == 'very_high':
            pixmap = QPixmap(DRIVING_ICONS.very_high)
        else:
            return
        
        self.risk_icon_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindows()
    window.show()
    sys.exit(app.exec())