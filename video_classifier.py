import numpy as np
import onnxruntime as ort
import cv2
import config

class VideoClassifier:
    def __init__(self) -> None:
        self.feature_extractor = ort.InferenceSession(config.FEATURE_EXTRACTOR_MODEL_PATH)
        self.lstm_classifier = ort.InferenceSession(config.LSTM_MODEL_PATH)
        
        self.input_name_feature = self.feature_extractor.get_inputs()[0].name
        self.output_name_feature = self.feature_extractor.get_outputs()[0].name
        
        self.input_name_lstm = self.lstm_classifier.get_inputs()[0].name
        self.output_name_lstm = self.lstm_classifier.get_outputs()[0].name

    def preprocess_image(self, image) -> np.ndarray:
        # Resize the image to 224x224
        image = cv2.resize(image, (224, 224))
        
        # Convert to float32 and normalize
        image = image.astype(np.float32)
        
        # DenseNet preprocessing
        image /= 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = (image - mean) / std
        
        # Transpose to (C, H, W) format
        image = np.transpose(image, (2, 0, 1))
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image

    def extract_features(self, frames) -> np.ndarray:
        features = []
        for frame in frames:
            preprocessed_frame = self.preprocess_image(frame)
            feature = self.feature_extractor.run([self.output_name_feature], {self.input_name_feature: preprocessed_frame})[0]
            features.append(feature.squeeze())
        return np.array(features)

    def classify(self, features) -> np.ndarray:
        # Ensure we have 70 frames, pad if necessary
        if features.shape[0] < 70:
            pad_length = 70 - features.shape[0]
            features = np.pad(features, ((0, pad_length), (0, 0)), mode='constant')
        elif features.shape[0] > 70:
            features = features[:70]
        
        # Add batch dimension
        features = np.expand_dims(features, axis=0)
        
        # Run LSTM classifier
        output = self.lstm_classifier.run([self.output_name_lstm], {self.input_name_lstm: features})[0]
        return output.squeeze()

    def process_video(self) -> np.ndarray:
        cap = cv2.VideoCapture(0)
        frames = []
        
        i = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        
        features = self.extract_features(frames)
        classification = self.classify(features)
        
        return classification

# Usage example
if __name__ == "__main__":
    classifier = VideoClassifier()
    
    result = classifier.process_video()
    print("Classification result:", result)