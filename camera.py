import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPainter
import numpy as np

class Camera:
    def __init__(self, camera_id, rgb=True, resize=None) -> None:
        self.camera = cv2.VideoCapture(camera_id)
        # find frame rate from camera
        self.frame_rate = self.camera.get(cv2.CAP_PROP_FPS)
        
        self.size = (int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                     int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        
        self.black_image = np.zeros((self.size[1], self.size[0], 3), np.uint8)
        
        self.is_rgb = rgb
        self.resize = resize
        
        if self.resize:
            self.size = self.resize
            self.black_image = np.zeros((self.size[1], self.size[0], 3), np.uint8)

    def get_frame(self) -> np.ndarray:
        success, image = self.camera.read()
        
        if self.resize : image = cv2.resize(image, self.size)
        
        if not success:
            return self.black_image        
        
        if self.is_rgb:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            return image

    def release(self) -> None:
        self.camera.release()
    
    def get_size(self) -> tuple[int, int]:
        return self.size
    
    def get_framerate(self) -> int:
        return int(self.frame_rate)

class CameraWidget(QWidget):
    frames_collected = pyqtSignal(list)  # Signal to emit when 200 frames are collected

    def __init__(self, camera: Camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // self.camera.get_framerate())  # Set timer to match camera FPS
        self.current_frame = self.camera.black_image
        self.frame_buffer = []  # Buffer to store frames
        self.frames_to_collect = 200  # Number of frames to collect before emitting

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is not None:
            self.current_frame = frame
            self.frame_buffer.append(frame)  # Add the frame to the buffer
            
            if len(self.frame_buffer) >= self.frames_to_collect:
                self.emit_frames()
                self.frame_buffer.clear()  # Clear the buffer after emitting

            self.update()  # Trigger a repaint

    def emit_frames(self):
        self.frames_collected.emit(self.frame_buffer)  # Emit the list of collected frames

    def paintEvent(self, event):
        painter = QPainter(self)
        height, width, channel = self.current_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.current_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        painter.drawImage(0, 0, q_image)