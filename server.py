from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
import mysql.connector
import cv2
import face_recognition
import numpy as np
import os
from io import BytesIO
from fastapi.responses import FileResponse
import csv
from fastapi import Query
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  # tu contraseña si aplica
    database="asistencias"
)
cursor = conexion.cursor()

# Cargar rostros conocidos
known_face_encodings = []
known_face_names = []

for filename in os.listdir("known_faces"):
    if filename.endswith((".jpg", ".png")):
        image_path = os.path.join("known_faces", filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)

# Registrar asistencia en la base
def registrar_asistencia(nombre):
    hoy = date.today()
    cursor.execute("SELECT * FROM asistencias WHERE nombre = %s AND DATE(fecha) = %s", (nombre, hoy))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO asistencias (nombre, fecha) VALUES (%s, NOW())", (nombre,))
        conexion.commit()
        print(f"Asistencia registrada para {nombre}")

# Generar frames de video con reconocimiento
def generar_frames():
    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Desconocido"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                registrar_asistencia(name)

            top, right, bottom, left = [v * 4 for v in face_location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    video.release()

# Ruta raíz
@app.get("/", response_class=HTMLResponse)
async def root():
    return {"message": "Servidor de reconocimiento facial activo"}

# Ruta de video
@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generar_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# Ruta para consultar asistencias
@app.get("/asistencias")
def obtener_asistencias():
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, fecha FROM asistencias ORDER BY fecha DESC")
    registros = cursor.fetchall()
    return {
        "asistencia": [
            {"nombre": nombre, "fecha_hora": fecha.strftime("%Y-%m-%d %H:%M:%S")}
            for nombre, fecha in registros
        ]
    }


@app.get("/exportar_csv")
def exportar_asistencia():
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, fecha FROM asistencias ORDER BY fecha DESC")
    registros = cursor.fetchall()

    archivo_csv = "asistencia.csv"
    with open(archivo_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nombre", "Fecha"])
        writer.writerows(registros)

    return FileResponse(archivo_csv, filename="asistencia.csv", media_type="text/csv")

#show in page
@app.get("/historial_asistencias")
def historial_asistencias():
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, fecha FROM asistencias ORDER BY fecha DESC")
    registros = cursor.fetchall()
    datos = [{"nombre": nombre, "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S")} for nombre, fecha in registros]
    return JSONResponse(content=datos)


