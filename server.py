from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
import mysql.connector
import cv2
import face_recognition
import numpy as np
import os
import csv
import time

app = FastAPI()
ultimos_registros = {}
COOLDOWN_SEGUNDOS = 10

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="asistencias"
)

# Cargar rostros conocidos
known_face_encodings = []
known_face_names = []

for filename in os.listdir("known_faces"):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image = face_recognition.load_image_file(f"known_faces/{filename}")
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(os.path.splitext(filename)[0])

# Variable para almacenar último nombre detectado
ultimo_nombre_detectado = {"nombre": ""}

# Video global (se mantiene abierta la cámara)
video_capture = cv2.VideoCapture(0)

# Registrar asistencia
@app.post("/registrar_asistencia")
def registrar_asistencia(nombre: str):
    cursor = conexion.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM asistencias WHERE nombre = %s AND DATE(fecha) = %s", (nombre, hoy))
    ya_registrado = cursor.fetchone()

    if not ya_registrado:
        cursor.execute("INSERT INTO asistencias (nombre, fecha) VALUES (%s, %s)", (nombre, datetime.now()))
        conexion.commit()
        ultimo_nombre_detectado["nombre"] = nombre
        return {"message": f"Asistencia registrada para {nombre}"}
    else:
        return {"message": f"{nombre} ya registró su asistencia hoy"}

@app.get("/nombre_detectado")
def nombre_detectado():
    nombre = ultimo_nombre_detectado.get("nombre", "")
    ultimo_nombre_detectado["nombre"] = ""  # Limpiar
    return {"nombre": nombre}

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

@app.get("/asistencias")
def obtener_asistencias():
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, fecha FROM asistencias ORDER BY fecha DESC")
    datos = cursor.fetchall()
    lista = [{"nombre": nombre, "fecha_hora": fecha.strftime("%Y-%m-%d %H:%M:%S")} for nombre, fecha in datos]
    return {"asistencia": lista}

@app.get("/asistencia")
def obtener_asistencia_hoy():
    cursor = conexion.cursor()
    hoy = date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT nombre, fecha FROM asistencias WHERE DATE(fecha) = %s", (hoy,))
    datos = cursor.fetchall()
    lista = [{"nombre": nombre, "fecha_hora": fecha.strftime("%Y-%m-%d %H:%M:%S")} for nombre, fecha in datos]
    return {"asistencia": lista}

def generar_frames():
    while True:
        # Verifica que la cámara esté abierta, si no, intenta reabrir
        if not video_capture.isOpened():
            print("[❌] Cámara no disponible. Reintentando...")
            time.sleep(1)
            continue

        try:
            ret, frame = video_capture.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Desconocido"
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                if matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                if name != "Desconocido":
                    ahora = time.time()
                    if name not in ultimos_registros or ahora - ultimos_registros[name] > COOLDOWN_SEGUNDOS:
                        try:
                            registrar_asistencia(name)
                            ultimos_registros[name] = ahora
                        except Exception as e:
                            print(f"[❌ ERROR registrando asistencia]: {e}")

                # Mostrar el nombre y recuadro en la imagen
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

            # Mostrar frame en la interfaz web
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except Exception as e:
            print(f"[❌ ERROR en captura de video]: {e}")
            time.sleep(1)
            continue

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generar_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
