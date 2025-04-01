# ReconocimientoFacialAn-lisis-Dise-o
Proyecto Sistema de Reconocimiento Facial para toma de asistencias. 

# 🎯 Reconocimiento Facial para Control de Asistencia

Este proyecto es una aplicación web que utiliza **MediaPipe**, **OpenCV** y **FastAPI** para detectar rostros en tiempo real desde la cámara y registrar asistencia manualmente desde la interfaz web.

---

## ✅ Requisitos

- Python **3.10.x** (probado con 3.10.9)
- pip (gestor de paquetes de Python)
- Cámara web
- Navegador moderno

---

## ⚙️ Instalación

### 1. Instalar Python 3.10
Descárgalo desde:  
🔗 https://www.python.org/downloads/release/python-3109/

Durante la instalación:
- ✅ Marca "Add Python to PATH"
- 📂 Recomendada: instalar en `C:\\Python310`

---

### 2. Instalar las librerías necesarias

Abre la terminal y ejecuta:

```bash
py -3.10 -m pip install --upgrade pip
py -3.10 -m pip install mediapipe opencv-python fastapi uvicorn numpy
