import cv2 
import mediapipe as mp
import math
import numpy as np 
import torch
import config

class FacialDrowsiness:
    def __init__(self):
        self.model = torch.jit.load(config.LSTM_MODEL_PATH)
        self.model.eval()
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.3, min_tracking_confidence=0.8)
        self.mp_drawing = mp.solutions.drawing_utils 
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.right_eye = [[33, 133], [160, 144], [159, 145], [158, 153]]
        self.left_eye = [[263, 362], [387, 373], [386, 374], [385, 380]]
        self.mouth = [[61, 291], [39, 181], [0, 17], [269, 405]]
        self.states = ['alert', 'drowsy']

    def distance(self, p1, p2):
        return (((p1[:2] - p2[:2])**2).sum())**0.5

    def eye_aspect_ratio(self, landmarks, eye):
        N1 = self.distance(landmarks[eye[1][0]], landmarks[eye[1][1]])
        N2 = self.distance(landmarks[eye[2][0]], landmarks[eye[2][1]])
        N3 = self.distance(landmarks[eye[3][0]], landmarks[eye[3][1]])
        D = self.distance(landmarks[eye[0][0]], landmarks[eye[0][1]])
        return (N1 + N2 + N3) / (3 * D)

    def eye_feature(self, landmarks):
        return (self.eye_aspect_ratio(landmarks, self.left_eye) + \
            self.eye_aspect_ratio(landmarks, self.right_eye))/2

    def mouth_feature(self, landmarks):
        N1 = self.distance(landmarks[self.mouth[1][0]], landmarks[self.mouth[1][1]])
        N2 = self.distance(landmarks[self.mouth[2][0]], landmarks[self.mouth[2][1]])
        N3 = self.distance(landmarks[self.mouth[3][0]], landmarks[self.mouth[3][1]])
        D = self.distance(landmarks[self.mouth[0][0]], landmarks[self.mouth[0][1]])
        return (N1 + N2 + N3)/(3*D)
    
    def pupil_circularity(self, landmarks, eye):
        perimeter = self.distance(landmarks[eye[0][0]], landmarks[eye[1][0]]) + \
                self.distance(landmarks[eye[1][0]], landmarks[eye[2][0]]) + \
                self.distance(landmarks[eye[2][0]], landmarks[eye[3][0]]) + \
                self.distance(landmarks[eye[3][0]], landmarks[eye[0][1]]) + \
                self.distance(landmarks[eye[0][1]], landmarks[eye[3][1]]) + \
                self.distance(landmarks[eye[3][1]], landmarks[eye[2][1]]) + \
                self.distance(landmarks[eye[2][1]], landmarks[eye[1][1]]) + \
                self.distance(landmarks[eye[1][1]], landmarks[eye[0][0]])
        area = math.pi * ((self.distance(landmarks[eye[1][0]], landmarks[eye[3][1]]) * 0.5) ** 2)
        return (4*math.pi*area)/(perimeter**2)

    def pupil_feature(self, landmarks):
        return (self.pupil_circularity(landmarks, self.left_eye) + \
            self.pupil_circularity(landmarks, self.right_eye))/2

    def run_face_mp(self, image):
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.face_mesh.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            landmarks_positions = []
            # assume that only face is present in the image
            for _, data_point in enumerate(results.multi_face_landmarks[0].landmark):
                landmarks_positions.append([data_point.x, data_point.y, data_point.z]) # saving normalized landmark positions
            landmarks_positions = np.array(landmarks_positions)
            landmarks_positions[:, 0] *= image.shape[1]
            landmarks_positions[:, 1] *= image.shape[0]
            
            ear = self.eye_feature(landmarks_positions)
            mar = self.mouth_feature(landmarks_positions)
            puc = self.pupil_feature(landmarks_positions)
            moe = mar/ear
        else:
            ear = -1000
            mar = -1000
            puc = -1000
            moe = -1000
            
        return ear, mar, puc, moe, image
    
    def calibrate(self, images):
        ears = []
        mars = []
        pucs = []
        moes = []

        for img in images:
            ear, mar,puc, moe, _ = self.run_face_mp(img)
            if ear != -1000:
                ears.append(ear)
                mars.append(mar)
                pucs.append(puc)
                moes.append(moe)

        ears = np.array(ears)
        mars = np.array(mars)
        pucs = np.array(pucs)
        moes = np.array(moes)
        return [ears.mean(), ears.std()], [mars.mean(), mars.std()], \
            [pucs.mean(), pucs.std()], [moes.mean(), moes.std()]
    
    def get_classification(self, input_data):
        model_input = []
        model_input.append(input_data[:5])
        model_input.append(input_data[3:8])
        model_input.append(input_data[6:11])
        model_input.append(input_data[9:14])
        model_input.append(input_data[12:17])
        model_input.append(input_data[15:])
        model_input = torch.FloatTensor(np.array(model_input))
        preds = torch.sigmoid(self.model(model_input))
        return np.mean(preds.float().data.numpy())
    
    def infer(self, images, ears_norm, mars_norm, pucs_norm, moes_norm):
        ear_main = 0
        mar_main = 0
        puc_main = 0
        moe_main = 0
        decay = 0.9
        input_data = []
        for image in images:
            ear, mar, puc, moe, image = self.run_face_mp(image)
            if ear != -1000:
                ear = (ear - ears_norm[0])/ears_norm[1]
                mar = (mar - mars_norm[0])/mars_norm[1]
                puc = (puc - pucs_norm[0])/pucs_norm[1]
                moe = (moe - moes_norm[0])/moes_norm[1]
                if ear_main == -1000:
                    ear_main = ear
                    mar_main = mar
                    puc_main = puc
                    moe_main = moe
                else:
                    ear_main = ear_main*decay + (1-decay)*ear
                    mar_main = mar_main*decay + (1-decay)*mar
                    puc_main = puc_main*decay + (1-decay)*puc
                    moe_main = moe_main*decay + (1-decay)*moe
            else:
                ear_main = -1000
                mar_main = -1000
                puc_main = -1000
                moe_main = -1000
            input_data.append([ear_main, mar_main, puc_main, moe_main])
        pred = self.get_classification(input_data)
        return pred
    
    def close(self):
        self.face_mesh.close()