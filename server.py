from fastapi import FastAPI, Response
import cv2
import mediapipe as mp

app = FastAPI()

# Inicializar la detección facial
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Capturar video desde la cámara
cap = cv2.VideoCapture(0)

@app.get("/")
def home():
    return {"message": "Servidor de reconocimiento facial activo"}

@app.get("/video_feed")
def video_feed():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir la imagen a RGB y procesarla con MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            results = face_detection.process(rgb_frame)

        # Dibujar las detecciones en la imagen
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        # Codificar la imagen como JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return Response(content=buffer.tobytes(), media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
