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
        return False, "La sala no existe.", None

    sala = doc.to_dict()

    # Permitimos entrar mientras la partida todavía no ha comenzado.
    if sala.get("estado") in ("jugando", "resultado", "final"):
        return False, "La partida ya comenzó y no se permiten nuevos jugadores.", None

    jugadores = sala.get("jugadores", {})

    if len(jugadores) >= MAX_JUGADORES:
        return False, "La sala ya alcanzó los 30 jugadores.", None

    player_id = str(uuid.uuid4())

    jugadores[player_id] = {
        "nombre": nombre_jugador,
        "equipo": [],
        "presupuesto": 0,
        "listo": False,
        "puntos_jornada": 0,
        "puntos_totales": 0,
        "cambios_jornada": 0,
    }

    ref.update({"jugadores": jugadores})
    return True, None, player_id


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


def marcar_listo(codigo, player_id, listo=True):
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

    jugadores[player_id]["listo"] = bool(listo)
    ref.update({"jugadores": jugadores})
    return True, None


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


def todos_jugadores_listos(codigo_o_sala):
    """Comprueba si todos los jugadores de una sala están listos.
    Acepta tanto el código de sala como el diccionario de la sala.
    """
    if isinstance(codigo_o_sala, dict):
        sala = codigo_o_sala
    else:
        sala = obtener_sala(codigo_o_sala)

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


def guardar_resultado_jornada(codigo, jornada, puntos_por_jugador, puntos_jugadores=None, detalles_jugadores=None):
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
            jugadores[player_id]["cambios_jornada"] = 0

    estado = "final" if jornada >= 7 else "resultado"

    actualizacion = {
        "jugadores": jugadores,
        "jornada_actual": jornada,
        "estado": estado,
        "seleccion_abierta": False,
        f"resultados_jornadas.jornada_{jornada}": puntos_por_jugador,
    }

    if puntos_jugadores is not None:
        actualizacion[f"puntos_jugadores_jornadas.jornada_{jornada}"] = puntos_jugadores

    if detalles_jugadores is not None:
        actualizacion[f"detalles_jornadas.jornada_{jornada}"] = detalles_jugadores

    ref.update(actualizacion)

    return True



def guardar_cambio_equipo(codigo, player_id, equipo_nuevo, presupuesto_nuevo):
    """Guarda un cambio de 1 jugador por otro, máximo 3 entre jornadas."""
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False, "La sala no existe."

    sala = doc.to_dict()
    if sala.get("estado") != "resultado":
        return False, "Los cambios solo están disponibles después de una jornada."

    jugadores = sala.get("jugadores", {})
    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    jugador = jugadores[player_id]
    equipo_anterior = list(jugador.get("equipo") or [])
    equipo_nuevo = list(equipo_nuevo or [])

    if len(equipo_nuevo) != 11 or len(set(equipo_nuevo)) != 11:
        return False, "La plantilla debe tener 11 jugadores distintos."

    vendidos = set(equipo_anterior) - set(equipo_nuevo)
    comprados = set(equipo_nuevo) - set(equipo_anterior)

    if len(vendidos) != 1 or len(comprados) != 1:
        return False, "Cada operación debe cambiar exactamente 1 jugador."

    cambios = int(jugador.get("cambios_jornada", 0))
    if cambios >= 3:
        return False, "Ya has utilizado tus 3 cambios."

    try:
        presupuesto_nuevo = float(presupuesto_nuevo)
    except (TypeError, ValueError):
        return False, "Presupuesto no válido."

    if presupuesto_nuevo < 0:
        return False, "No puedes superar el presupuesto."

    jugador["equipo"] = equipo_nuevo
    jugador["presupuesto"] = presupuesto_nuevo
    jugador["cambios_jornada"] = cambios + 1
    jugador["listo"] = False

    ref.update({"jugadores": jugadores})
    return True, None


def eliminar_jugador(codigo, player_id):
    """Elimina un jugador de la sala desde el panel del administrador."""
    db = inicializar_firebase()
    codigo = codigo.upper()
    ref = db.collection(NOMBRE_COLECCION).document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False, "La sala no existe."

    sala = doc.to_dict()
    jugadores = sala.get("jugadores", {})

    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    del jugadores[player_id]
    ref.update({"jugadores": jugadores})
    return True, None

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

