import cv2
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
        return self.frame_rate