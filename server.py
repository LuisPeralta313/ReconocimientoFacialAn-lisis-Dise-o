import os
import cv2
import mediapipe as mp
from fastapi import FastAPI, Response, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime
import time

app = FastAPI()

# Obtener la ruta absoluta del directorio donde está el script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Verificar si la carpeta static existe
if not os.path.exists(STATIC_DIR):
    raise RuntimeError(f"⚠️ ERROR: La carpeta 'static' no existe en {STATIC_DIR}")

# Montar la carpeta estática para servir la página web
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Inicializar MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Iniciar la cámara
cap = cv2.VideoCapture(0)

# Lista de asistencia
asistencia = {}

def generar_frames():
    """Función generadora para transmitir el video en vivo."""
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convertir la imagen a RGB para MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)

            # Dibujar las detecciones en la imagen
            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)

            # Codificar la imagen como JPEG y enviarla en un flujo continuo
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.03)  # Pequeña pausa para optimizar el rendimiento

@app.get("/")
def home():
    return {"message": "Servidor de reconocimiento facial activo"}

@app.get("/video_feed")
def video_feed():
    """Envía el video en streaming continuo."""
    return StreamingResponse(generar_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/registrar_asistencia")
def registrar_asistencia(nombre: str = Query(...)):
    """Registra la asistencia con un nombre proporcionado desde la interfaz web."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    asistencia[nombre] = timestamp
    return JSONResponse(content={"message": f"Asistencia registrada para {nombre} a las {timestamp}"})

@app.get("/asistencia")
def get_asistencia():
    """Devuelve la lista de personas detectadas y la hora de detección."""
    return {"asistencia": asistencia}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
