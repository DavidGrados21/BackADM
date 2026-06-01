import sqlite3

DB_PATH = "hospital_dbSCD.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # ⚠️ Activar claves foráneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # =========================
    # PACIENTES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paciente (
        dni_paciente TEXT PRIMARY KEY,
        nombre_paciente TEXT NOT NULL,
        fecha_nacimiento_paciente DATE,
        sexo_paciente TEXT CHECK(sexo_paciente IN ('M','F')),
        telefono_paciente TEXT,
        direccion_paciente TEXT,
        tipo_sangre_paciente TEXT,
        tiene_tatuajes_paciente BOOLEAN DEFAULT 0,
        religion_paciente TEXT,
        contacto_emergencia_paciente TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # =========================
    # HISTORIAL CLÍNICO
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_clinico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni_paciente TEXT NOT NULL,
        diagnostico TEXT,
        id_receta INTEGER,
        observaciones TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(dni_paciente) REFERENCES paciente(dni_paciente) ON DELETE CASCADE,
        FOREIGN KEY(id_receta) REFERENCES receta(id_receta) ON DELETE SET NULL
    )
    """)

    # =========================
    # MEDICAMENTOS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicamento (
        id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_medicamento TEXT NOT NULL
    )
    """)
    
    # =========================
    # RECETA
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receta (
        id_receta INTEGER PRIMARY KEY AUTOINCREMENT
    )
    """)
    
    # =========================
    # DETALLE RECETA
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receta_detalle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_receta INTEGER,
        id_medicamento INTEGER,
        cantidad INTEGER NOT NULL CHECK(cantidad > 0),
        FOREIGN KEY(id_receta) REFERENCES receta(id_receta) ON DELETE CASCADE,
        FOREIGN KEY(id_medicamento) REFERENCES medicamento(id_medicamento)
)
    """)
    
    

    # =========================
    # ESPECIALIDADES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS especialidad (
        id_especialidad INTEGER PRIMARY KEY,
        nombre_especialidad TEXT UNIQUE NOT NULL
    )
    """)

    # =========================
    # DOCTORES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctor (
        id_doctor INTEGER PRIMARY KEY,
        nombre_doctor TEXT NOT NULL,
        especialidad_id INTEGER NOT NULL ,
        disponibilidad INTEGER CHECK(disponibilidad IN (0,1)),
        email_doctor TEXT UNIQUE NOT NULL,
        password_doctor TEXT NOT NULL,
        FOREIGN KEY(especialidad_id) REFERENCES especialidad(id_especialidad) ON DELETE RESTRICT
    )
    """)


    # =========================
    # CAMILLAS (EMERGENCIA)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS camilla (
        id_camilla INTEGER PRIMARY KEY,
        estado_camilla BOOLEAN DEFAULT 0
    )
    """)


    # =========================
    # ESTADOS CASO
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estados_caso (
        id_estado INTEGER PRIMARY KEY,
        nombre_estado TEXT UNIQUE NOT NULL
    )
    """)
    
    # =========================
    # CASOS EMERGENCIA
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS casos_emergencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni_paciente TEXT,
        id_doctor INTEGER,
        id_estado INTEGER,
        prioridad INTEGER CHECK(prioridad BETWEEN 1 AND 5),
        id_especialidad INTEGER NOT NULL,
        origen TEXT,
        fecha_llegada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(dni_paciente) REFERENCES paciente(dni_paciente) ON DELETE CASCADE,
        FOREIGN KEY(id_doctor) REFERENCES doctor(id_doctor) ON DELETE SET NULL,
        FOREIGN KEY(id_estado) REFERENCES estados_caso(id_estado),
        FOREIGN KEY(id_especialidad) REFERENCES especialidad(id_especialidad)
    )
    """)

    # =========================
    # TRIAJE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS triaje (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caso_id INTEGER UNIQUE NOT NULL,
        sintomas TEXT,
        altura REAL CHECK(altura > 0),
        peso REAL CHECK(peso > 0),
        prioridad_ia INTEGER CHECK(prioridad_ia BETWEEN 1 AND 5),
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(caso_id)
            REFERENCES casos_emergencia(id)
            ON DELETE CASCADE
    )
    """)
    
    # =========================
    # MONITOREO
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoreo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        caso_id INTEGER NOT NULL,

        presion_arterial TEXT,

        frecuencia_cardiaca INTEGER CHECK(frecuencia_cardiaca > 0),

        saturacion_oxigeno INTEGER CHECK(saturacion_oxigeno BETWEEN 0 AND 100),

        temperatura REAL CHECK(temperatura BETWEEN 30 AND 45),

        observaciones TEXT,

        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(caso_id)
            REFERENCES casos_emergencia(id)
            ON DELETE CASCADE
    )
    """)

    # =========================
    # HOSPITALIZACIÓN
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitalizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caso_id INTEGER UNIQUE NOT NULL,
        fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_salida TIMESTAMP,
        estado TEXT DEFAULT 'internado' CHECK(estado IN ('internado', 'alta')),
        observaciones TEXT,
        FOREIGN KEY(caso_id) REFERENCES casos_emergencia(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()