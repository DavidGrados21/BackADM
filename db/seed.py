from db.db import get_db

def seed_data():
    db = get_db()
    cursor = db.cursor()

    # Activar claves foráneas
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 🏥 Estados de casos de emergencia
    cursor.executemany("""
    INSERT OR IGNORE INTO estados_caso (id, nombre) VALUES (?, ?)
    """, [
        (1, 'entrante'),
        (2, 'pendiente'),
        (3, 'en_atencion'),
        (4, 'finalizado')
    ])

    # 🏥 Especialidades
    cursor.executemany("""
    INSERT OR IGNORE INTO especialidades (id, nombre) VALUES (?, ?)
    """, [
        (1, 'CARDIOLOGIA'),
        (2, 'NEUROLOGIA'),
        (3, 'TRAUMATOLOGIA PEDIATRICA'),
        (4, 'GASTROENTEROLOGIA'),
        (5, 'OFTALMOLOGIA')
    ])

    # 🧑‍⚕️ Doctores
    cursor.executemany("""
    INSERT OR IGNORE INTO doctores 
    (id, nombre, especialidad_id, disponibilidad, puntuacion)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'Dr. MIGUEL ALBERTO RIVERA', 1, 1, 5),
        (2, 'Dr. ROGER MARTIN SARMIENTO', 1, 1, 5),
        (3, 'Dr. CARLOS ALBERTO ROCHA', 2, 1, 5),
        (4, 'Dr. TATIANA MARISELA VALERA', 3, 1, 5),
        (5, 'Dr. PETER WILLIAM ROJAS', 4, 1, 5),
        (6, 'Dr. MIGUEL DE LOS SANTOS VERONA', 4, 1, 5),
        (7, 'Dr. ROBERTH ISAAC ACOSTA', 5, 1, 5),
        (8, 'Dr. SUSSAN TATIANA CASTRO', 5, 1, 5),

    ])

    # 🔐 Usuarios (asociados a doctores)
    cursor.executemany("""
    INSERT OR IGNORE INTO usuarios
    (doctor_id, email, password)
    VALUES (?, ?, ?)
    """, [
        (1, 'juan@hospital.com', '1234'),
        (2, 'ana@hospital.com', '1234'),
        (3, 'luis@hospital.com', '1234')
    ])

    # 🛏️ Camillas
    cursor.executemany("""
    INSERT OR IGNORE INTO camillas (id, ocupada)
    VALUES (?, ?)
    """, [
        (1, 0),
        (2, 0),
        (3, 0),
        (4, 0),
        (5, 0)
    ])
    
    # 🏨 Habitaciones
    cursor.executemany("""
    INSERT OR IGNORE INTO habitaciones
    (id, numero, piso, ocupada)
    VALUES (?, ?, ?, ?)
    """, [
    (1, '101', 1, 0),
    (2, '102', 1, 0),
    (3, '201', 2, 0),
    (4, '202', 2, 0),
    (5, '301', 3, 0)
])

    db.commit()
    print("✅ Datos iniciales cargados correctamente")


if __name__ == "__main__":
    seed_data()