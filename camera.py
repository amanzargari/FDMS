import config
import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPainter
import numpy as np

class Camera:
    """
    A class to represent a camera and handle its operations.
    Attributes
    ----------
    camera : cv2.VideoCapture
        The video capture object for the camera.
    frame_rate : float
        The frame rate of the camera.
    size : tuple[int, int]
        The size (width, height) of the camera frames.
    black_image : np.ndarray
        A black image of the same size as the camera frames.
    is_rgb : bool
        Flag to determine if the frames should be converted to RGB.
    resize : tuple[int, int] or None
        The size to which frames should be resized, if any.
    Methods
    -------
    __init__(camera_id, rgb=True, resize=None)
        Initializes the Camera object with the given camera ID, RGB flag, and resize dimensions.
    get_frame() -> np.ndarray
        Captures a frame from the camera, resizes it if needed, and converts it to RGB if specified.
    release() -> None
        Releases the camera resource.
    get_size() -> tuple[int, int]
        Returns the size of the camera frames.
    get_framerate() -> int
        Returns the frame rate of the camera.
    """
    def __init__(self, camera_id, rgb=True, resize=None, fake=True) -> None:
        """
        Initializes the Camera object.
        Args:
            camera_id (int): The ID of the camera to be used.
            rgb (bool, optional): Flag to indicate if the camera captures RGB images. Defaults to True.
            resize (tuple, optional): Tuple containing the new width and height to resize the frames. Defaults to None.
        Attributes:
            camera (cv2.VideoCapture): The VideoCapture object for the camera.
            frame_rate (float): The frame rate of the camera.
            size (tuple): The width and height of the camera frames.
            black_image (np.ndarray): A black image with the same size as the camera frames.
            is_rgb (bool): Indicates if the camera captures RGB images.
            resize (tuple): The new width and height to resize the frames.
        """
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
        
        self.fake_frame = cv2.imread(config.DRIVER_SAMPLE_IMAGE)
        self.fake_frame = cv2.resize(self.fake_frame, self.size)
        self.fake_frame = cv2.cvtColor(self.fake_frame, cv2.COLOR_BGR2RGB)
        
        self.fake = fake
        

    def get_frame(self) -> np.ndarray:
        """
        Captures a frame from the camera, processes it, and returns the resulting image.
        Returns:
            np.ndarray: The processed image frame. If the capture is unsuccessful, 
                returns a black image. If the `is_rgb` attribute is True, 
                the image is converted to RGB format; otherwise, it is returned 
                in its original format.
        """
        if self.fake:
            return self.fake_frame
        
        success, image = self.camera.read()
        
        if self.resize : image = cv2.resize(image, self.size)
        
        if not success:
            return self.black_image        
        
        if self.is_rgb:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            return image

    def release(self) -> None:
        """
        Releases the camera resource.

        This method calls the release method on the camera object to free up the 
        camera resource. It should be called when the camera is no longer needed 
        to ensure that the resource is properly released.
        """
        self.camera.release()
    
    def get_size(self) -> tuple[int, int]:
        """
        Retrieve the size of the camera.

        Returns:
            tuple[int, int]: A tuple containing the width and height of the camera.
        """
        return self.size
    
    def get_framerate(self) -> int:
        """
        Retrieve the current frame rate of the camera.

        Returns:
            int: The frame rate of the camera as an integer.
        """
        return int(self.frame_rate)

class CameraWidget(QWidget):
    """
    CameraWidget is a custom QWidget that interfaces with a Camera object to display and process frames.
    Attributes:
        frames_collected (pyqtSignal): Signal emitted when a specified number of frames are collected.
        camera (Camera): The camera object providing frames.
        timer (QTimer): Timer to trigger frame updates at the camera's framerate.
        current_frame (numpy.ndarray): The current frame being displayed.
        frame_buffer (list): Buffer to store collected frames.
        frames_to_collect (int): Number of frames to collect before emitting the frames_collected signal.
    Methods:
        __init__(camera: Camera, parent=None):
            Initializes the CameraWidget with the given camera and optional parent widget.
        update_frame():
            Updates the current frame from the camera and manages the frame buffer.
        emit_frames():
            Emits the frames_collected signal with the collected frames and clears the buffer.
        paintEvent(event):
            Handles the paint event to draw the current frame on the widget.
    """
    frames_collected = pyqtSignal(list)  # Signal to emit when 200 frames are collected

    def __init__(self, camera: Camera, parent=None):
        """
        Initializes the camera object and sets up the timer for frame updates.

        Args:
            camera (Camera): The camera object to interface with.
            parent (optional): The parent widget, if any. Defaults to None.

        Attributes:
            camera (Camera): The camera object to interface with.
            timer (QTimer): Timer to trigger frame updates.
            current_frame: The current frame from the camera.
            frame_buffer (list): Buffer to store frames.
            frames_to_collect (int): Number of frames to collect before emitting.
        """
        super().__init__(parent)
        self.camera = camera
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // self.camera.get_framerate())  # Set timer to match camera FPS
        self.current_frame = self.camera.black_image
        self.frame_buffer = []  # Buffer to store frames
        self.frames_to_collect = 200  # Number of frames to collect before emitting

    def update_frame(self):
        """
        Updates the current frame from the camera and manages the frame buffer.
        This method retrieves a new frame from the camera. If a frame is successfully
        retrieved, it updates the current frame and appends the frame to the frame buffer.
        Once the buffer reaches the specified number of frames to collect, it emits the
        frames and clears the buffer. Finally, it triggers a repaint of the display.
        Returns:
            None
        """
        frame = self.camera.get_frame()
        if frame is not None:
            self.current_frame = frame
            self.frame_buffer.append(frame)  # Add the frame to the buffer
            
            if len(self.frame_buffer) >= self.frames_to_collect:
                self.emit_frames()
                self.frame_buffer.clear()  # Clear the buffer after emitting

            self.update()  # Trigger a repaint

    def emit_frames(self):
        """
        Emit the collected frames.

        This method emits the list of collected frames stored in the frame buffer
        using the `frames_collected` signal.
        """
        self.frames_collected.emit(self.frame_buffer)  # Emit the list of collected frames

    def paintEvent(self, event):
        """
        Handles the paint event for the widget.

        This method is called whenever the widget needs to be repainted. It uses a QPainter
        to draw the current frame (stored in `self.current_frame`) onto the widget.

        Args:
            event (QPaintEvent): The paint event that triggered this method.
        """
        painter = QPainter(self)
        height, width, channel = self.current_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.current_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        painter.drawImage(0, 0, q_image)