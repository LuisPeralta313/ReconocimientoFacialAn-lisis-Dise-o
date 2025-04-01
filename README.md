# 📸 Sistema de Control de Asistencia Facial

Este proyecto permite registrar la asistencia de personas utilizando reconocimiento facial en tiempo real, una interfaz web moderna y conexión a base de datos MySQL.

---

## ✅ Versión Estable - 31 de marzo de 2025

### 🎯 Funciones implementadas

- 📸 Detección facial en tiempo real con MediaPipe
- 🖥 Interfaz web con Bootstrap y tema oscuro
- 🧍 Registro de asistencia con modal personalizado
- ✅ Validación para evitar múltiples registros por día
- 📋 Tabla de asistencias actualizada en tiempo real
- 🕒 Fecha y hora actual en vivo en la barra superior
- 👥 Contador automático de asistencias del día
- 📥 Exportación de registros a CSV (descarga directa)
- 🔁 Actualización automática cada 5 segundos

---

## 🧰 Estructura del proyecto

```
ReconocimientoFacial/
│── server.py
└── static/
    ├── index.html
    └── style.css
```

---

## ⚙️ Requisitos

- Python 3.10
- MySQL Server
- Navegador moderno
- Git (opcional)

---

## 📦 Instalación de dependencias

Ejecutar en consola:

```bash
py -3.10 -m pip install mediapipe opencv-python fastapi uvicorn mysql-connector-python
```

---

## 🛢 Configuración de base de datos

Con MySQL Workbench o consola, ejecutá:

```sql
CREATE DATABASE IF NOT EXISTS asistencia_db;
USE asistencia_db;

CREATE TABLE IF NOT EXISTS asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha_hora DATETIME NOT NULL
);
```

---

## 🚀 Ejecución del sistema

Desde la carpeta del proyecto, ejecutá:

```bash
py -3.10 server.py
```

Esto:
- Inicia el servidor FastAPI
- Abre automáticamente el navegador en:

```
http://127.0.0.1:8000/static/index.html
```

---

## 📤 Exportar asistencia

- Hacé clic en el botón verde de descarga con ícono `⬇️`
- También podés acceder directamente a:

```
http://127.0.0.1:8000/exportar_csv
```

---

## 🛑 Cómo detener el sistema

Presioná `Ctrl + C` en la terminal para cerrar el servidor.


---
