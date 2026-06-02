from db.db import get_db

def seed_data():
    db = get_db()
    cursor = db.cursor()

    # Activar claves foráneas
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 🏥 Estados de casos de emergencia
    cursor.executemany("""
        INSERT OR IGNORE INTO estados_caso 
        (id_estado, nombre_estado) 
        VALUES (?, ?)
    """, [
        (1, 'entrante'),
        (2, 'pendiente'),
        (3, 'en_atencion'),
        (4, 'finalizado')
    ])

    # 🏥 Especialidades
    cursor.executemany("""
    INSERT OR IGNORE INTO especialidad
    (id_especialidad, nombre_especialidad) 
    VALUES (?, ?)
    """, [
        (1, 'CARDIOLOGIA'),
        (2, 'NEUROLOGIA'),
        (3, 'TRAUMATOLOGIA PEDIATRICA'),
        (4, 'GASTROENTEROLOGIA'),
        (5, 'OFTALMOLOGIA')
    ])

    # 🧑‍⚕️ Doctores
    cursor.executemany("""
    INSERT OR IGNORE INTO doctor
    (id_doctor, nombre_doctor, especialidad_id, email_doctor, password_doctor)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'Dr. MIGUEL ALBERTO RIVERA', 1, 'miguel.rivera@clinica.com', 'Miguel123'),
        (2, 'Dr. ROGER MARTIN SARMIENTO', 1, 'roger.sarmiento@clinica.com', 'Roger123'),
        (3, 'Dr. CARLOS ALBERTO ROCHA', 2, 'carlos.rocha@clinica.com', 'Carlos123'),
        (4, 'Dr. TATIANA MARISELA VALERA', 3, 'tatiana.valera@clinica.com', 'Tatiana123'),
        (5, 'Dr. PETER WILLIAM ROJAS', 4, 'peter.rojas@clinica.com', 'Peter123'),
        (6, 'Dr. MIGUEL DE LOS SANTOS VERONA', 4, 'miguel.verona@clinica.com', 'Verona123'),
        (7, 'Dr. ROBERTH ISAAC ACOSTA', 5, 'roberth.acosta@clinica.com', 'Acosta123'),
        (8, 'Dr. SUSSAN TATIANA CASTRO', 5, 'sussan.castro@clinica.com', 'Castro123'),
    ])

    # 🛏️ Camillas
    cursor.executemany("""
        INSERT OR IGNORE INTO camilla
        (id_camilla, estado_camilla)
        VALUES (?, ?)
    """, [
        (1, 0),
        (2, 0),
        (3, 0),
        (4, 0),
        (5, 0)
    ])

    db.commit()
    print("✅ Datos iniciales cargados correctamente")


if __name__ == "__main__":
    seed_data()