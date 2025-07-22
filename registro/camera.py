import cv2
import os

class VideoCamera(object):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.video = cv2.VideoCapture(0)

        if not self.video.isOpened():
            print("Erro ao acessar a câmera.")

    def __del__(self):
        self.video.release()

    def restart(self):
        self.video.release()
        self.video = cv2.VideoCapture(0)

    def get_camera(self):
        ret, frame = self.video.read()
        if not ret:
            print('Falha ao capturar frame.')
            return None
        
        return ret, frame

    def detect_face(self):
        ret, frame = self.get_camera()
        if not ret:
            print("Falha ao capturar o frame.")
            return None
        

        altura, largura, _ = frame.shape
        centro_x, centro_y = int(largura/2), int(altura/2)
        a, b = 140, 180
        x1, y1 = centro_x - a, centro_y - b
        x2, y2 = centro_x + a, centro_y + b
        roi = frame[y1:y2, x1:x2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (0, 0, 255), 10)

        for(x, y, w, h) in faces:
            cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (0, 255, 0), 10)

        ret, jpeg = cv2.imencode('.jpeg', frame)
        return jpeg.tobytes()
