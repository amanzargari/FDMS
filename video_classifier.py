import numpy as np
import onnxruntime as ort
import cv2
import config
from PyQt6.QtCore import QThread, pyqtSignal

class VideoClassifier:
    """
    A class used to classify videos using a feature extractor and an LSTM classifier.
    Attributes
    ----------
    feature_extractor : ort.InferenceSession
        ONNX Runtime session for the feature extractor model.
    lstm_classifier : ort.InferenceSession
        ONNX Runtime session for the LSTM classifier model.
    input_name_feature : str
        Name of the input node for the feature extractor model.
    output_name_feature : str
        Name of the output node for the feature extractor model.
    input_name_lstm : str
        Name of the input node for the LSTM classifier model.
    output_name_lstm : str
        Name of the output node for the LSTM classifier model.
    Methods
    -------
    preprocess_image(image) -> np.ndarray
        Preprocesses an image by resizing, normalizing, and adding a batch dimension.
    extract_features(frames) -> np.ndarray
        Extracts features from a list of frames using the feature extractor model.
    classify(features) -> np.ndarray
        Classifies the extracted features using the LSTM classifier model.
    """
    def __init__(self) -> None:
        """
        Initializes the VideoClassifier object.
        This constructor sets up the feature extractor and LSTM classifier using 
        the specified model paths from the configuration. It also retrieves and 
        stores the input and output names for both the feature extractor and the 
        LSTM classifier.
        Attributes:
            feature_extractor (ort.InferenceSession): The ONNX runtime session for the feature extractor model.
            lstm_classifier (ort.InferenceSession): The ONNX runtime session for the LSTM classifier model.
            input_name_feature (str): The input name for the feature extractor model.
            output_name_feature (str): The output name for the feature extractor model.
            input_name_lstm (str): The input name for the LSTM classifier model.
            output_name_lstm (str): The output name for the LSTM classifier model.
        """
        self.feature_extractor = ort.InferenceSession(config.FEATURE_EXTRACTOR_MODEL_PATH)
        self.lstm_classifier = ort.InferenceSession(config.LSTM_MODEL_PATH)
        
        self.input_name_feature = self.feature_extractor.get_inputs()[0].name
        self.output_name_feature = self.feature_extractor.get_outputs()[0].name
        
        self.input_name_lstm = self.lstm_classifier.get_inputs()[0].name
        self.output_name_lstm = self.lstm_classifier.get_outputs()[0].name

    def preprocess_image(self, image) -> np.ndarray:
        """
        Preprocesses an input image for DenseNet model.
        Args:
            image (np.ndarray): Input image to preprocess.
        Returns:
            np.ndarray: Preprocessed image ready for model input.
        Steps:
            1. Resizes the image to 224x224 pixels.
            2. Converts the image to float32 and normalizes pixel values to [0, 1].
            3. Applies DenseNet-specific preprocessing by normalizing with mean and standard deviation.
            4. Adds a batch dimension to the image.
        """
        # Resize the image to 224x224
        image = cv2.resize(image, (224, 224))
        
        # Convert to float32 and normalize
        image = image.astype(np.float32)
        
        # DenseNet preprocessing
        image /= 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image = (image - mean) / std
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image

    def extract_features(self, frames) -> np.ndarray:
        """
        Extracts features from a list of frames using a pre-trained feature extractor.

        Args:
            frames (list): A list of image frames to extract features from.

        Returns:
            np.ndarray: A numpy array containing the extracted features for each frame.
        """
        features = []
        for frame in frames:
            preprocessed_frame = self.preprocess_image(frame)
            feature = self.feature_extractor.run([self.output_name_feature], {self.input_name_feature: preprocessed_frame})[0]
            features.append(feature.squeeze())
        return np.array(features, dtype=np.float32)

    def classify(self, features) -> np.ndarray:
        """
        Classifies the given features using an LSTM classifier.
        This method ensures that the input features have exactly 200 frames.
        If the number of frames is less than 200, it pads the features with zeros.
        If the number of frames is more than 200, it truncates the features to 200 frames.
        It then adds a batch dimension to the features and runs the LSTM classifier.
        Args:
            features (np.ndarray): A 2D array of shape (num_frames, num_features) representing the input features.
        Returns:
            np.ndarray: The classification output from the LSTM classifier.
        """
        # Ensure we have 200 frames, pad if necessary
        if features.shape[0] < 200:
            pad_length = 200 - features.shape[0]
            features = np.pad(features, ((0, pad_length), (0, 0)), mode='constant')
        elif features.shape[0] > 200:
            features = features[:200]
        
        # Add batch dimension
        features = np.expand_dims(features, axis=0)
        
        # Run LSTM classifier
        output = self.lstm_classifier.run([self.output_name_lstm], {self.input_name_lstm: features})[0]
        return output.squeeze()


class VideoClassificationThread(QThread):
    """
    A QThread subclass for performing video classification in a separate thread.
    Signals:
        classification_done (np.ndarray): Emitted when the classification is done, with the classification result.
    Attributes:
        video_classifier (VideoClassifier): An instance of the VideoClassifier used for extracting features and classifying frames.
        frames (list): A list of frames to be classified.
    Methods:
        __init__(video_classifier: VideoClassifier) -> None:
            Initializes the thread with a video classifier instance.
        set_frames(frames: list) -> None:
            Sets the frames to be classified.
        run() -> None:
            Executes the video classification process in a separate thread.
    """
    classification_done = pyqtSignal(np.ndarray)

    def __init__(self, video_classifier: VideoClassifier) -> None:
        """
        Initializes the VideoClassifier instance.

        Args:
            video_classifier (VideoClassifier): An instance of the VideoClassifier class.
        """
        super().__init__()
        self.video_classifier = video_classifier
        self.frames = []

    def set_frames(self, frames):
        """
        Sets the frames for the video classifier.

        Parameters:
        frames (list): A list of frames to be set.
        """
        self.frames = frames

    def run(self):
        """
        Executes the video classification process.
        This method checks if there are any frames available. If frames are present,
        it extracts features from the frames using the video classifier, classifies
        the features to determine a label, and emits a signal with the classification result.
        Returns:
            None
        """
        if len(self.frames) == 0:
            return

        features = self.video_classifier.extract_features(self.frames)
        label = self.video_classifier.classify(features)
        self.classification_done.emit(label)