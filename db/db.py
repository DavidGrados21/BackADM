import sqlite3

DB_PATH = "hospital_db.db"

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
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        fecha_nacimiento DATE,
        sexo TEXT CHECK(sexo IN ('M','F')),
        telefono TEXT,
        direccion TEXT,
        tipo_sangre TEXT,
        tiene_tatuajes BOOLEAN DEFAULT 0,
        religion TEXT,
        contacto_emergencia TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # =========================
    # HISTORIAL CLÍNICO
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_clinico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        diagnostico TEXT,
        tratamiento TEXT,
        observaciones TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(paciente_id)
            REFERENCES pacientes(id)
            ON DELETE CASCADE
    )
    """)
    

    # =========================
    # ENFERMEDADES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paciente_enfermedades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        enfermedad TEXT NOT NULL,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
    )
    """)

    # =========================
    # MEDICAMENTOS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paciente_medicamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        medicamento TEXT NOT NULL,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
    )
    """)

    # =========================
    # ESPECIALIDADES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS especialidades (
        id INTEGER PRIMARY KEY,
        nombre TEXT UNIQUE NOT NULL
    )
    """)

    # =========================
    # DOCTORES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctores (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        especialidad_id INTEGER,
        disponibilidad INTEGER CHECK(disponibilidad IN (0,1)),
        puntuacion INTEGER CHECK(puntuacion BETWEEN 1 AND 5),
        FOREIGN KEY(especialidad_id) REFERENCES especialidades(id) ON DELETE SET NULL
    )
    """)

    # =========================
    # USUARIOS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        doctor_id INTEGER UNIQUE,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        FOREIGN KEY(doctor_id) REFERENCES doctores(id) ON DELETE CASCADE
    )
    """)

    # =========================
    # CAMILLAS (EMERGENCIA)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS camillas (
        id INTEGER PRIMARY KEY,
        ocupada INTEGER CHECK(ocupada IN (0,1))
    )
    """)
    
    # =========================
    # HABITACIONES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habitaciones (
        id INTEGER PRIMARY KEY,

        numero TEXT UNIQUE NOT NULL,

        piso INTEGER,

        ocupada BOOLEAN DEFAULT 0
    )
    """)

    # =========================
    # ESTADOS CASO
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estados_caso (
        id INTEGER PRIMARY KEY,
        nombre TEXT UNIQUE NOT NULL
    )
    """)
    
    # =========================
    # CASOS EMERGENCIA
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS casos_emergencia (
        id INTEGER PRIMARY KEY,
        paciente_id INTEGER,
        doctor_id INTEGER,
        camilla_id INTEGER,
        estado_id INTEGER,
        prioridad INTEGER CHECK(prioridad BETWEEN 1 AND 5),
        origen TEXT,
        fecha_llegada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctores(id) ON DELETE SET NULL,
        FOREIGN KEY(camilla_id) REFERENCES camillas(id) ON DELETE SET NULL,
        FOREIGN KEY(estado_id) REFERENCES estados_caso(id)
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

        frecuencia_cardiaca INTEGER,

        saturacion_oxigeno INTEGER,

        temperatura REAL,

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

        habitacion_id INTEGER,

        fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        fecha_salida TIMESTAMP,

        estado TEXT DEFAULT 'internado'
            CHECK(estado IN ('internado', 'alta')),

        observaciones TEXT,

        FOREIGN KEY(caso_id)
            REFERENCES casos_emergencia(id)
            ON DELETE CASCADE,

        FOREIGN KEY(habitacion_id)
            REFERENCES habitaciones(id)
            ON DELETE SET NULL
    )
    """)

    conn.commit()
    conn.close()