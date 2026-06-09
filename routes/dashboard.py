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
        # Total pacientes registrados
        cursor.execute("SELECT COUNT(*) AS total FROM paciente")
        total_pacientes = cursor.fetchone()["total"]

        # Pacientes en espera (triaje I y II = prioridad 1 y 2)
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM casos_emergencia
            WHERE id_estado IN (1, 2)
              AND prioridad IN (1, 2)
        """)
        en_espera_criticos = cursor.fetchone()["total"]

        # Camillas disponibles
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM camilla
            WHERE estado_camilla = 0
        """)
        camillas_disponibles = cursor.fetchone()["total"]

        # Tiempo promedio de espera (minutos) - diferencia entre fecha_llegada y ahora
        # para casos pendientes (estado 2)
        cursor.execute("""
            SELECT AVG(
                (JULIANDAY('now') - JULIANDAY(fecha_llegada)) * 24 * 60
            ) AS promedio_minutos
            FROM casos_emergencia
            WHERE id_estado = 2
        """)
        row = cursor.fetchone()
        tiempo_promedio = round(row["promedio_minutos"], 1) if row["promedio_minutos"] else 0

        return {
            "total_pacientes": total_pacientes,
            "en_espera_criticos": en_espera_criticos,
            "camillas_disponibles": camillas_disponibles,
            "tiempo_promedio_espera_min": tiempo_promedio
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
                ec.nombre_estado AS estado,
                COUNT(*) AS total
            FROM casos_emergencia ce
            JOIN estados_caso ec ON ce.id_estado = ec.id_estado
            GROUP BY ce.id_estado
        """)
        rows = cursor.fetchall()

        return {
            "flujo": [{"estado": r["estado"], "total": r["total"]} for r in rows]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
            WHERE id_estado IN (1, 2, 3)
            GROUP BY prioridad
            ORDER BY prioridad ASC
        """)
        rows = cursor.fetchall()

        niveles = {i: 0 for i in range(1, 6)}
        for r in rows:
            if r["prioridad"]:
                niveles[r["prioridad"]] = r["total"]

        return {
            "total_activos": sum(niveles.values()),
            "por_nivel": [
                {"nivel": f"Triage {n}", "total": t}
                for n, t in niveles.items()
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
            SELECT id_camilla, estado_camilla
            FROM camilla
            ORDER BY id_camilla ASC
        """)
        rows = cursor.fetchall()

        camillas = [
            {
                "id": r["id_camilla"],
                "ocupada": bool(r["estado_camilla"])
            }
            for r in rows
        ]

        total = len(camillas)
        ocupadas = sum(1 for c in camillas if c["ocupada"])

        return {
            "total": total,
            "ocupadas": ocupadas,
            "libres": total - ocupadas,
            "camillas": camillas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
        # Total doctores por especialidad
        cursor.execute("""
            SELECT
                e.nombre_especialidad AS especialidad,
                COUNT(d.id_doctor) AS total
            FROM especialidad e
            LEFT JOIN doctor d ON d.especialidad_id = e.id_especialidad
            GROUP BY e.id_especialidad
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()

        especialidades = [
            {"especialidad": r["especialidad"], "total": r["total"]}
            for r in rows
        ]

        # Doctores con casos activos (en atención)
        cursor.execute("""
            SELECT COUNT(DISTINCT id_doctor) AS activos
            FROM casos_emergencia
            WHERE id_estado = 3 AND id_doctor IS NOT NULL
        """)
        doctores_activos = cursor.fetchone()["activos"]

        return {
            "doctores_activos": doctores_activos,
            "por_especialidad": especialidades
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
        # Evolución del tiempo de espera por hora (últimas 24h)
        cursor.execute("""
            SELECT
                strftime('%H:00', fecha_llegada) AS hora,
                AVG(
                    (JULIANDAY('now') - JULIANDAY(fecha_llegada)) * 24 * 60
                ) AS promedio_min
            FROM casos_emergencia
            WHERE fecha_llegada >= datetime('now', '-24 hours')
            GROUP BY strftime('%H', fecha_llegada)
            ORDER BY hora ASC
        """)
        rows = cursor.fetchall()

        evolucion = [
            {"hora": r["hora"], "minutos": round(r["promedio_min"], 1) if r["promedio_min"] else 0}
            for r in rows
        ]

        # Tiempo total de estancia promedio (casos finalizados)
        cursor.execute("""
            SELECT AVG(
                (JULIANDAY(h.fecha_salida) - JULIANDAY(ce.fecha_llegada)) * 24 * 60
            ) AS promedio_estancia
            FROM hospitalizaciones h
            JOIN casos_emergencia ce ON h.caso_id = ce.id
            WHERE h.estado = 'alta'
              AND h.fecha_salida IS NOT NULL
        """)
        row = cursor.fetchone()
        promedio_estancia = round(row["promedio_estancia"], 1) if row["promedio_estancia"] else 0

        return {
            "evolucion_espera": evolucion,
            "promedio_estancia_min": promedio_estancia
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
        # Casos críticos (prioridad 1) entrantes en la última hora
        cursor.execute("""
            SELECT
                ce.id AS caso_id,
                p.nombre_paciente AS nombre,
                ce.fecha_llegada,
                ce.prioridad,
                ec.nombre_estado AS estado
            FROM casos_emergencia ce
            JOIN paciente p ON p.dni_paciente = ce.dni_paciente
            JOIN estados_caso ec ON ce.id_estado = ec.id_estado
            WHERE ce.prioridad = 1
              AND ce.fecha_llegada >= datetime('now', '-1 hour')
            ORDER BY ce.fecha_llegada DESC
            LIMIT 5
        """)
        criticos = cursor.fetchall()

        # Casos recientes (última hora)
        cursor.execute("""
            SELECT
                ce.id AS caso_id,
                p.nombre_paciente AS nombre,
                ce.fecha_llegada,
                ce.prioridad,
                ec.nombre_estado AS estado
            FROM casos_emergencia ce
            JOIN paciente p ON p.dni_paciente = ce.dni_paciente
            JOIN estados_caso ec ON ce.id_estado = ec.id_estado
            WHERE ce.fecha_llegada >= datetime('now', '-1 hour')
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
