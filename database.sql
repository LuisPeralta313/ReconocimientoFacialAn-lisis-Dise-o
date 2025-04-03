CREATE DATABASE IF NOT EXISTS asistencias;
USE asistencias;
CREATE TABLE IF NOT EXISTS asistencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha DATETIME NOT NULL
);

select * from asistencias

TRUNCATE TABLE asistencias;