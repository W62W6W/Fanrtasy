import os
import json
import uuid
import random
import string

import firebase_admin
from firebase_admin import credentials, firestore

MAX_JUGADORES = 30
COLECCION = "salas"


def inicializar_firebase():
    if firebase_admin._apps:
        return firestore.client()

    # Streamlit Cloud: credenciales guardadas en Advanced settings > Secrets.
    try:
        import streamlit as st
        if "firebase" in st.secrets:
            datos = dict(st.secrets["firebase"])
            firebase_admin.initialize_app(credentials.Certificate(datos))
            return firestore.client()
    except Exception:
        pass

    # PC local: archivo privado. Nunca subirlo a GitHub.
    ruta = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            "No se encontró serviceAccountKey.json ni los Secrets de Firebase."
        )
    firebase_admin.initialize_app(credentials.Certificate(ruta))
    return firestore.client()


def _ref(codigo):
    db = inicializar_firebase()
    return db.collection(COLECCION).document(str(codigo).upper())


def generar_codigo_sala():
    db = inicializar_firebase()
    while True:
        codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.collection(COLECCION).document(codigo).get().exists:
            return codigo


def crear_sala(nombre_admin):
    codigo = generar_codigo_sala()
    admin_id = str(uuid.uuid4())
    sala = {
        "codigo": codigo,
        "admin_id": admin_id,
        "admin_nombre": nombre_admin,
        "estado": "esperando",
        "seleccion_abierta": False,
        "jornada_actual": 0,
        "max_jugadores": MAX_JUGADORES,
        "jugadores": {},
        "torneo": None,
    }
    _ref(codigo).set(sala)
    return codigo, admin_id


def obtener_sala(codigo):
    if isinstance(codigo, dict):
        codigo = codigo.get("codigo")
    if not codigo:
        return None
    doc = _ref(codigo).get()
    return doc.to_dict() if doc.exists else None


def unirse_sala(codigo, nombre_jugador):
    codigo = str(codigo).strip().upper()
    ref = _ref(codigo)
    doc = ref.get()
    if not doc.exists:
        return False, "La sala no existe.", None

    sala = doc.to_dict()
    if sala.get("estado") in ("jugando", "resultado", "final"):
        return False, "La partida ya comenzó.", None

    jugadores = sala.get("jugadores") or {}
    if len(jugadores) >= MAX_JUGADORES:
        return False, "La sala ya tiene 30 jugadores.", None

    player_id = str(uuid.uuid4())
    jugadores[player_id] = {
        "nombre": nombre_jugador,
        "equipo": [],
        "presupuesto": 0,
        "listo": False,
        "puntos_jornada": 0.0,
        "puntos_totales": 0.0,
    }
    ref.update({"jugadores": jugadores})
    return True, None, player_id


def guardar_equipo(codigo, player_id, equipo, presupuesto):
    ref = _ref(codigo)
    doc = ref.get()
    if not doc.exists:
        return False, "La sala no existe."

    sala = doc.to_dict()
    if not sala.get("seleccion_abierta", False):
        return False, "La selección está cerrada."

    jugadores = sala.get("jugadores") or {}
    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    jugadores[player_id]["equipo"] = list(equipo)
    jugadores[player_id]["presupuesto"] = float(presupuesto)
    jugadores[player_id]["listo"] = False
    ref.update({"jugadores": jugadores})
    return True, None


def marcar_listo(codigo, player_id, listo=True):
    ref = _ref(codigo)
    doc = ref.get()
    if not doc.exists:
        return False, "La sala no existe."

    jugadores = doc.to_dict().get("jugadores") or {}
    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    jugadores[player_id]["listo"] = bool(listo)
    ref.update({"jugadores": jugadores})
    return True, None


def abrir_seleccion(codigo):
    _ref(codigo).update({"estado": "seleccion", "seleccion_abierta": True})
    return True, None


def cerrar_seleccion(codigo):
    _ref(codigo).update({"estado": "esperando", "seleccion_abierta": False})
    return True, None


def todos_jugadores_listos(sala_o_codigo):
    sala = obtener_sala(sala_o_codigo)
    jugadores = (sala or {}).get("jugadores") or {}
    return bool(jugadores) and all(j.get("listo", False) for j in jugadores.values())


def iniciar_partida(codigo):
    sala = obtener_sala(codigo)
    if not sala:
        return False, "La sala no existe."
    if not sala.get("torneo"):
        return False, "Primero genera el torneo."
    if not sala.get("jugadores"):
        return False, "Debe haber al menos un jugador."
    if not todos_jugadores_listos(codigo):
        return False, "Todavía faltan jugadores por marcar LISTO."

    _ref(codigo).update({
        "estado": "jugando",
        "jornada_actual": 1,
        "seleccion_abierta": False,
    })
    return True, None


def guardar_torneo(codigo, torneo, jornada_actual=0):
    _ref(codigo).update({
        "torneo": json.dumps(torneo, ensure_ascii=False, default=str),
        "jornada_actual": jornada_actual,
    })


def obtener_torneo(codigo_o_sala):
    sala = obtener_sala(codigo_o_sala)
    if not sala:
        return None
    torneo = sala.get("torneo")
    if not torneo:
        return None
    return json.loads(torneo) if isinstance(torneo, str) else torneo


def guardar_resultado_jornada(codigo, jornada, puntos_por_jugador, detalles=None):
    ref = _ref(codigo)
    doc = ref.get()
    if not doc.exists:
        return False

    sala = doc.to_dict()
    jugadores = sala.get("jugadores") or {}
    for player_id, puntos in puntos_por_jugador.items():
        if player_id in jugadores:
            jugadores[player_id]["puntos_jornada"] = float(puntos)
            jugadores[player_id]["puntos_totales"] = (
                float(jugadores[player_id].get("puntos_totales", 0))
                + float(puntos)
            )

    updates = {
        "jugadores": jugadores,
        "jornada_actual": int(jornada),
        "estado": "final" if int(jornada) >= 7 else "resultado",
        "seleccion_abierta": False,
    }
    if detalles is not None:
        updates["ultimo_detalle"] = json.dumps(
            detalles, ensure_ascii=False, default=str
        )
    ref.update(updates)
    return True


def avanzar_jornada(codigo):
    sala = obtener_sala(codigo)
    if not sala:
        return False, "La sala no existe."

    jornada = int(sala.get("jornada_actual", 0))
    if jornada >= 7:
        return False, "El torneo ya terminó."

    jugadores = sala.get("jugadores") or {}
    for jugador in jugadores.values():
        jugador["listo"] = False
        jugador["puntos_jornada"] = 0.0

    _ref(codigo).update({
        "jugadores": jugadores,
        "jornada_actual": jornada + 1,
        "estado": "seleccion",
        "seleccion_abierta": True,
    })
    return True, None


def eliminar_sala(codigo):
    _ref(codigo).delete()
