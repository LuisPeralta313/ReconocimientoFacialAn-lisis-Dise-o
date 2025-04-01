import os
import webbrowser
import cv2
import mediapipe as mp
import mysql.connector
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, date
import time
import io
import csv

app = FastAPI()

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    raise RuntimeError(f"La carpeta 'static' no existe en {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Inicializar MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Iniciar cámara
cap = cv2.VideoCapture(0)

# Conexión a MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",           # <- Reemplaza esto
    password="root",   # <- Reemplaza esto
    database="asistencia_db"
)
cursor = conexion.cursor()

# Streaming de cámara
def generar_frames():
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = detector.process(rgb)

            if resultado.detections:
                for d in resultado.detections:
                    mp_drawing.draw_detection(frame, d)

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)

@app.get("/")
def home():
    return {"message": "Servidor activo"}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generar_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/registrar_asistencia")
def registrar(nombre: str = Query(...)):
    hoy = date.today()
    cursor.execute("""
        SELECT COUNT(*) FROM asistencia
        WHERE nombre = %s AND DATE(fecha_hora) = %s
    """, (nombre, hoy))
    resultado = cursor.fetchone()

    if resultado[0] > 0:
        return JSONResponse(
            content={"message": f"❌ Ya registraste tu asistencia hoy, {nombre}"},
            status_code=400
        )

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO asistencia (nombre, fecha_hora) VALUES (%s, %s)", (nombre, ahora))
    conexion.commit()
    return JSONResponse(content={"message": f"✅ Asistencia registrada para {nombre} a las {ahora}"})

@app.get("/asistencia")
def ver_asistencia():
    cursor.execute("SELECT nombre, fecha_hora FROM asistencia ORDER BY fecha_hora DESC")
    datos = cursor.fetchall()
    return {"asistencia": [{"nombre": n, "fecha_hora": f.strftime("%Y-%m-%d %H:%M:%S")} for n, f in datos]}

@app.get("/exportar_csv")
def exportar_csv():
    cursor.execute("SELECT nombre, fecha_hora FROM asistencia ORDER BY fecha_hora DESC")
    filas = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nombre", "Fecha y Hora"])
    for fila in filas:
        writer.writerow([fila[0], fila[1].strftime("%Y-%m-%d %H:%M:%S")])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=asistencias.csv"}
    )

if __name__ == "__main__":
    print("\nServidor iniciado en:")
    print("http://127.0.0.1:8000/static/index.html")
    webbrowser.open("http://127.0.0.1:8000/static/index.html")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
