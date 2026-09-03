
import random
import string
import uuid

import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT = "serviceAccountKey.json"
MAX_JUGADORES = 30


def inicializar_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
    return firestore.client()


db = inicializar_firebase()


def generar_codigo_sala():
    caracteres = string.ascii_uppercase + string.digits
    while True:
        codigo = "".join(random.choices(caracteres, k=6))
        if not db.collection("salas").document(codigo).get().exists:
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
        "resultados_jornadas": {},
    }

    db.collection("salas").document(codigo).set(sala)
    return codigo, admin_id


def obtener_sala(codigo):
    if not codigo:
        return None

    codigo = codigo.upper().strip()
    doc = db.collection("salas").document(codigo).get()

    if not doc.exists:
        return None

    return doc.to_dict()


def unirse_sala(codigo, nombre_jugador):
    codigo = codigo.upper().strip()
    ref = db.collection("salas").document(codigo)
    doc = ref.get()

    if not doc.exists:
        return False, "La sala no existe.", None

    sala = doc.to_dict()
    estado = sala.get("estado", "esperando")

    if estado != "esperando":
        return False, "El administrador todavía no permite nuevas entradas.", None

    jugadores = sala.get("jugadores") or {}

    if len(jugadores) >= MAX_JUGADORES:
        return False, f"La sala está llena. Máximo {MAX_JUGADORES} jugadores.", None

    player_id = str(uuid.uuid4())

    jugadores[player_id] = {
        "id": player_id,
        "nombre": nombre_jugador,
        "equipo": [],
        "presupuesto_restante": 0,
        "listo": False,
        "puntos_jornada": 0,
        "puntos_totales": 0,
    }

    ref.update({"jugadores": jugadores})
    return True, "Te has unido correctamente.", player_id


def abrir_seleccion(codigo):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    ref.update({
        "estado": "seleccion",
        "seleccion_abierta": True,
    })
    return True, "Selección abierta."


def cerrar_seleccion(codigo):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    ref.update({
        "estado": "esperando",
        "seleccion_abierta": False,
    })
    return True, "Selección cerrada."


def guardar_equipo(codigo, player_id, equipo, presupuesto_restante):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    if sala.get("estado") != "seleccion" or not sala.get("seleccion_abierta"):
        return False, "La selección está cerrada."

    jugadores = sala.get("jugadores") or {}

    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    jugadores[player_id]["equipo"] = list(equipo)
    jugadores[player_id]["presupuesto_restante"] = presupuesto_restante
    jugadores[player_id]["listo"] = False

    ref.update({"jugadores": jugadores})
    return True, "Equipo guardado."


def marcar_listo(codigo, player_id, listo=True):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    jugadores = sala.get("jugadores") or {}

    if player_id not in jugadores:
        return False, "Jugador no encontrado."

    jugadores[player_id]["listo"] = bool(listo)
    ref.update({"jugadores": jugadores})
    return True, "Estado actualizado."


def todos_jugadores_listos(sala):
    jugadores = sala.get("jugadores") or {}
    return bool(jugadores) and all(
        jugador.get("listo", False)
        for jugador in jugadores.values()
    )


def iniciar_partida(codigo):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    jugadores = sala.get("jugadores") or {}

    if not jugadores:
        return False, "Se necesita al menos un jugador."

    if not todos_jugadores_listos(sala):
        return False, "No todos los jugadores están listos."

    torneo = obtener_torneo(sala)

    if torneo is None:
        return False, "El torneo todavía no ha sido generado."

    ref.update({
        "estado": "jugando",
        "seleccion_abierta": False,
        "jornada_actual": 1,
    })
    return True, "Partida iniciada."


def guardar_torneo(codigo, torneo):
    torneo_json = json.dumps(torneo, ensure_ascii=False)

    db.collection("salas").document(codigo.upper().strip()).update({
        "torneo": torneo_json,
        "jornada_actual": 0,
    })
    return True


def obtener_torneo(sala):
    torneo = sala.get("torneo")

    if isinstance(torneo, str):
        try:
            return json.loads(torneo)
        except json.JSONDecodeError:
            return None

    return torneo


def guardar_resultado_jornada(codigo, jornada, resultados, puntos_jugadores):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    jugadores = sala.get("jugadores") or {}
    resultados_jornadas = sala.get("resultados_jornadas") or {}

    resultados_jornadas[str(jornada)] = resultados

    for player_id, puntos in puntos_jugadores.items():
        if player_id not in jugadores:
            continue

        jugadores[player_id]["puntos_jornada"] = round(float(puntos), 2)
        jugadores[player_id]["puntos_totales"] = round(
            float(jugadores[player_id].get("puntos_totales", 0))
            + float(puntos),
            2,
        )

    estado = "final" if int(jornada) >= 7 else "resultado"

    ref.update({
        "jugadores": jugadores,
        "resultados_jornadas": resultados_jornadas,
        "jornada_actual": int(jornada),
        "estado": estado,
        "seleccion_abierta": False,
    })
    return True, "Jornada guardada."


def avanzar_jornada(codigo):
    ref = db.collection("salas").document(codigo.upper().strip())
    sala = ref.get().to_dict()

    if not sala:
        return False, "La sala no existe."

    jornada = int(sala.get("jornada_actual", 1))

    if jornada >= 7:
        ref.update({"estado": "final"})
        return True, "Torneo terminado."

    jugadores = sala.get("jugadores") or {}

    for jugador in jugadores.values():
        jugador["listo"] = False
        jugador["puntos_jornada"] = 0

    ref.update({
        "jugadores": jugadores,
        "jornada_actual": jornada + 1,
        "estado": "seleccion",
        "seleccion_abierta": True,
    })
    return True, "Siguiente jornada preparada."


def eliminar_sala(codigo):
    db.collection("salas").document(codigo.upper().strip()).delete()
