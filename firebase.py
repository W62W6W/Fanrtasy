import os
import json
import uuid
import random
import string

import firebase_admin
from firebase_admin import credentials, firestore

MAX_JUGADORES = 30
NOMBRE_COLECCION = "salas"


def inicializar_firebase():
    """Inicializa Firebase usando Streamlit Secrets en la nube
    o serviceAccountKey.json cuando se ejecuta localmente.
    """
    if firebase_admin._apps:
        return firestore.client()

    # Streamlit Cloud: usa st.secrets["firebase"]
    try:
        import streamlit as st

        if "firebase" in st.secrets:
            datos_credenciales = dict(st.secrets["firebase"])
            cred = credentials.Certificate(datos_credenciales)
            firebase_admin.initialize_app(cred)
            return firestore.client()
    except Exception:
        pass

    # Local: usa el archivo privado que NO debe subirse a GitHub.
    ruta = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

    if not os.path.exists(ruta):
        raise FileNotFoundError(
            "No se encontró serviceAccountKey.json y tampoco están configurados "
            "los Secrets de Firebase en Streamlit."
        )

    cred = credentials.Certificate(ruta)
    firebase_admin.initialize_app(cred)
    return firestore.client()


def generar_codigo_sala():
    db = inicializar_firebase()

    while True:
        codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.collection(NOMBRE_COLECCION).document(codigo).get().exists:
            return codigo


def crear_sala(nombre_admin):
    db = inicializar_firebase()
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
        "resultados_jornadas": {},
    }

    db.collection(NOMBRE_COLECCION).document(codigo).set(sala)
    return codigo, admin_id


def obtener_sala(codigo):
    db = inicializar_firebase()
    ref = db.collection(NOMBRE_COLECCION).document(codigo.upper())
    doc = ref.get()

    if not doc.exists:
        return None

    return doc.to_dict()


def unirse_sala(codigo, nombre_jugador):
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return None, "La sala no existe."

    sala = doc.to_dict()

    # Permitimos entrar mientras la partida todavía no ha comenzado.
    if sala.get("estado") in ("jugando", "resultado", "final"):
        return None, "La partida ya comenzó y no se permiten nuevos jugadores."

    jugadores = sala.get("jugadores", {})

    if len(jugadores) >= MAX_JUGADORES:
        return None, "La sala ya alcanzó los 30 jugadores."

    player_id = str(uuid.uuid4())

    jugadores[player_id] = {
        "nombre": nombre_jugador,
        "equipo": [],
        "presupuesto": 0,
        "listo": False,
        "puntos_jornada": 0,
        "puntos_totales": 0,
    }

    ref.update({"jugadores": jugadores})
    return player_id, None


def guardar_equipo(codigo, player_id, equipo, presupuesto):
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False, "La sala no existe."

    sala = doc.to_dict()

    if not sala.get("seleccion_abierta", False):
        return False, "El administrador todavía no ha abierto la selección."

    jugadores = sala.get("jugadores", {})

    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    jugadores[player_id]["equipo"] = equipo
    jugadores[player_id]["presupuesto"] = presupuesto
    jugadores[player_id]["listo"] = False

    ref.update({"jugadores": jugadores})
    return True, None


def marcar_listo(codigo, player_id):
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False

    sala = doc.to_dict()
    jugadores = sala.get("jugadores", {})

    if player_id not in jugadores:
        return False

    jugadores[player_id]["listo"] = True
    ref.update({"jugadores": jugadores})
    return True


def abrir_seleccion(codigo):
    db = inicializar_firebase()
    ref = db.collection(NOMBRE_COLECCION).document(codigo.upper())
    ref.update({
        "estado": "seleccion",
        "seleccion_abierta": True,
    })


def cerrar_seleccion(codigo):
    db = inicializar_firebase()
    ref = db.collection(NOMBRE_COLECCION).document(codigo.upper())
    ref.update({
        "estado": "esperando",
        "seleccion_abierta": False,
    })


def todos_jugadores_listos(codigo):
    sala = obtener_sala(codigo)

    if not sala:
        return False

    jugadores = sala.get("jugadores", {})

    if not jugadores:
        return False

    return all(j.get("listo", False) for j in jugadores.values())


def iniciar_partida(codigo):
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False, "La sala no existe."

    sala = doc.to_dict()

    if not sala.get("torneo"):
        return False, "Primero hay que generar el torneo."

    if not sala.get("jugadores"):
        return False, "Debe haber al menos un jugador."

    if not todos_jugadores_listos(codigo):
        return False, "No todos los jugadores están listos."

    ref.update({
        "estado": "jugando",
        "jornada_actual": 1,
        "seleccion_abierta": False,
    })

    return True, None


def guardar_torneo(codigo, torneo, jornada_actual=0):
    db = inicializar_firebase()
    ref = db.collection(NOMBRE_COLECCION).document(codigo.upper())

    # Firestore no acepta directamente algunas estructuras complejas
    # generadas por el simulador, por eso guardamos el torneo como JSON.
    torneo_json = json.dumps(torneo, ensure_ascii=False, default=str)

    ref.update({
        "torneo": torneo_json,
        "jornada_actual": jornada_actual,
    })


def obtener_torneo(codigo):
    sala = obtener_sala(codigo)

    if not sala:
        return None

    torneo = sala.get("torneo")

    if not torneo:
        return None

    if isinstance(torneo, str):
        return json.loads(torneo)

    return torneo


def guardar_resultado_jornada(codigo, jornada, puntos_por_jugador):
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False

    sala = doc.to_dict()
    jugadores = sala.get("jugadores", {})

    for player_id, puntos in puntos_por_jugador.items():
        if player_id in jugadores:
            jugadores[player_id]["puntos_jornada"] = puntos
            jugadores[player_id]["puntos_totales"] = (
                jugadores[player_id].get("puntos_totales", 0) + puntos
            )

    estado = "final" if jornada >= 7 else "resultado"

    ref.update({
        "jugadores": jugadores,
        "jornada_actual": jornada,
        "estado": estado,
        "seleccion_abierta": False,
        f"resultados_jornadas.jornada_{jornada}": puntos_por_jugador,
    })

    return True


def avanzar_jornada(codigo):
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False, "La sala no existe."

    sala = doc.to_dict()
    jornada_actual = int(sala.get("jornada_actual", 0))

    if jornada_actual >= 7:
        return False, "El torneo ya terminó."

    jugadores = sala.get("jugadores", {})

    for jugador in jugadores.values():
        jugador["listo"] = False
        jugador["puntos_jornada"] = 0

    nueva_jornada = jornada_actual + 1

    ref.update({
        "jugadores": jugadores,
        "jornada_actual": nueva_jornada,
        "estado": "seleccion",
        "seleccion_abierta": True,
    })

    return True, None


def eliminar_sala(codigo):
    db = inicializar_firebase()
    db.collection(NOMBRE_COLECCION).document(codigo.upper()).delete()
