from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()


# =========================
# DASHBOARD - RESUMEN GLOBAL
# =========================

@router.get("/dashboard/resumen")
def resumen_global():
    db = get_db()
    cursor = db.cursor()

    try:
        # Total pacientes
        cursor.execute("SELECT COUNT(*) AS total FROM pacientes")
        total_pacientes = cursor.fetchone()["total"]

        # Casos críticos en espera
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM casos_emergencia
            WHERE estado_id IN (1,2)
              AND prioridad IN (1,2)
        """)
        en_espera_criticos = cursor.fetchone()["total"]

        # Camillas disponibles
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM camillas
            WHERE ocupada = 0
        """)
        camillas_disponibles = cursor.fetchone()["total"]

        # Tiempo promedio de espera
        cursor.execute("""
            SELECT AVG(
                (JULIANDAY('now') - JULIANDAY(fecha_llegada))
                * 24 * 60
            ) AS promedio_minutos
            FROM casos_emergencia
            WHERE estado_id = 2
        """)

        row = cursor.fetchone()

        tiempo_promedio = (
            round(row["promedio_minutos"], 1)
            if row["promedio_minutos"]
            else 0
        )

        return {
            "total_pacientes": total_pacientes,
            "en_espera_criticos": en_espera_criticos,
            "camillas_disponibles": camillas_disponibles,
            "tiempo_promedio_espera_min": tiempo_promedio
        }

    finally:
        db.close()


# =========================
# DASHBOARD - FLUJO DE PACIENTES POR ESTADO
# =========================

@router.get("/dashboard/flujo")
def flujo_pacientes():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT
                ec.nombre AS estado,
                COUNT(*) AS total
            FROM casos_emergencia ce
            JOIN estados_caso ec
                ON ce.estado_id = ec.id
            GROUP BY ce.estado_id
        """)

        rows = cursor.fetchall()

        return {
            "flujo": [
                {
                    "estado": r["estado"],
                    "total": r["total"]
                }
                for r in rows
            ]
        }

    finally:
        db.close()

# =========================
# DASHBOARD - PACIENTES POR NIVEL DE TRIAJE
# =========================

@router.get("/dashboard/triaje")
def pacientes_por_triaje():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT
                prioridad,
                COUNT(*) AS total
            FROM casos_emergencia
            WHERE estado_id IN (1,2,3)
            GROUP BY prioridad
            ORDER BY prioridad
        """)

        rows = cursor.fetchall()

        niveles = {i: 0 for i in range(1, 6)}

        for r in rows:
            niveles[r["prioridad"]] = r["total"]

        return {
            "total_activos": sum(niveles.values()),
            "por_nivel": [
                {
                    "nivel": f"Triage {n}",
                    "total": t
                }
                for n, t in niveles.items()
            ]
        }

    finally:
        db.close()


# =========================
# DASHBOARD - GESTIÓN DE CAMILLAS
# =========================

@router.get("/dashboard/camillas")
def estado_camillas():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT id, ocupada
            FROM camillas
            ORDER BY id
        """)

        rows = cursor.fetchall()

        camillas = [
            {
                "id": r["id"],
                "ocupada": bool(r["ocupada"])
            }
            for r in rows
        ]

        total = len(camillas)
        ocupadas = sum(c["ocupada"] for c in camillas)

        return {
            "total": total,
            "ocupadas": ocupadas,
            "libres": total - ocupadas,
            "camillas": camillas
        }

    finally:
        db.close()


# =========================
# DASHBOARD - RECURSOS Y PERSONAL
# =========================

@router.get("/dashboard/personal")
def resumen_personal():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT
                e.nombre AS especialidad,
                COUNT(d.id) AS total
            FROM especialidades e
            LEFT JOIN doctores d
                ON d.especialidad_id = e.id
            GROUP BY e.id
            ORDER BY total DESC
        """)

        rows = cursor.fetchall()

        especialidades = [
            {
                "especialidad": r["especialidad"],
                "total": r["total"]
            }
            for r in rows
        ]

        cursor.execute("""
            SELECT COUNT(DISTINCT doctor_id) AS activos
            FROM casos_emergencia
            WHERE estado_id = 3
              AND doctor_id IS NOT NULL
        """)

        doctores_activos = cursor.fetchone()["activos"]

        return {
            "doctores_activos": doctores_activos,
            "por_especialidad": especialidades
        }

    finally:
        db.close()


# =========================
# DASHBOARD - MÉTRICAS DE TIEMPO (últimas 24h)
# =========================

@router.get("/dashboard/metricas-tiempo")
def metricas_tiempo():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT
                strftime('%H:00', fecha_llegada) AS hora,
                AVG(
                    (JULIANDAY('now') - JULIANDAY(fecha_llegada))
                    * 24 * 60
                ) AS promedio_min
            FROM casos_emergencia
            WHERE fecha_llegada >= datetime('now','-24 hours')
            GROUP BY strftime('%H', fecha_llegada)
            ORDER BY hora
        """)

        evolucion = [
            {
                "hora": r["hora"],
                "minutos": round(r["promedio_min"],1)
            }
            for r in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT AVG(
                (
                    JULIANDAY(h.fecha_salida)
                    - JULIANDAY(ce.fecha_llegada)
                ) * 24 * 60
            ) AS promedio_estancia
            FROM hospitalizaciones h
            JOIN casos_emergencia ce
                ON ce.id = h.caso_id
            WHERE h.estado = 'alta'
              AND h.fecha_salida IS NOT NULL
        """)

        row = cursor.fetchone()

        promedio_estancia = (
            round(row["promedio_estancia"],1)
            if row["promedio_estancia"]
            else 0
        )

        return {
            "evolucion_espera": evolucion,
            "promedio_estancia_min": promedio_estancia
        }

    finally:
        db.close()

# =========================
# DASHBOARD - ALERTAS Y EVENTOS RECIENTES
# =========================

@router.get("/dashboard/alertas")
def alertas_recientes():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT
                ce.id AS caso_id,
                p.nombre,
                ce.fecha_llegada,
                ce.prioridad,
                ec.nombre AS estado
            FROM casos_emergencia ce
            JOIN pacientes p
                ON p.id = ce.paciente_id
            JOIN estados_caso ec
                ON ec.id = ce.estado_id
            WHERE ce.prioridad = 1
              AND ce.fecha_llegada >= datetime('now','-1 hour')
            ORDER BY ce.fecha_llegada DESC
            LIMIT 5
        """)

        criticos = cursor.fetchall()

        cursor.execute("""
            SELECT
                ce.id AS caso_id,
                p.nombre,
                ce.fecha_llegada,
                ce.prioridad,
                ec.nombre AS estado
            FROM casos_emergencia ce
            JOIN pacientes p
                ON p.id = ce.paciente_id
            JOIN estados_caso ec
                ON ec.id = ce.estado_id
            WHERE ce.fecha_llegada >= datetime('now','-1 hour')
            ORDER BY ce.fecha_llegada DESC
            LIMIT 10
        """)

        recientes = cursor.fetchall()

        def formato(rows):
            return [
                {
                    "caso_id": r["caso_id"],
                    "nombre": r["nombre"],
                    "fecha": r["fecha_llegada"],
                    "prioridad": r["prioridad"],
                    "estado": r["estado"]
                }
                for r in rows
            ]

        return {
            "criticos": formato(criticos),
            "recientes": formato(recientes)
        }

    finally:
        db.close()
