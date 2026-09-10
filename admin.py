import streamlit as st
from streamlit_autorefresh import st_autorefresh

from firebase import (
    crear_sala,
    obtener_sala,
    abrir_seleccion,
    cerrar_seleccion,
    todos_jugadores_listos,
    iniciar_partida,
    guardar_torneo,
    obtener_torneo,
    guardar_resultado_jornada,
    eliminar_jugador,
)
from datos import jugadores
from simulador import generar_jornadas, simular_jornada
from fantasy import calcular_fantasy, calcular_desgloses_partido

st.set_page_config(page_title="World Cup Fantasy · Admin", page_icon="👑", layout="wide")

MAX_JUGADORES = 30

st.markdown("""
<style>
.stApp { background:#050505; color:white; }
h1,h2,h3,h4,h5,h6,p,label { color:white !important; }
.stButton > button { background:#151515 !important; color:white !important;
border:1px solid #444 !important; border-radius:10px !important;
font-weight:bold !important; min-height:44px !important; }
.box { background:linear-gradient(145deg,#171717,#090909); border:1px solid #333;
border-radius:15px; padding:18px; margin-bottom:12px; }
.big { font-size:30px; font-weight:700; }
.small { color:#999; font-size:13px; letter-spacing:1px; }
</style>
""", unsafe_allow_html=True)

if "codigo_sala" not in st.session_state:
    st.session_state.codigo_sala = None
if "admin_id" not in st.session_state:
    st.session_state.admin_id = None
if "admin_nombre" not in st.session_state:
    st.session_state.admin_nombre = None

st_autorefresh(interval=3000, limit=None, key="admin_autorefresh")

def salir():
    for k in ("codigo_sala","admin_id","admin_nombre"):
        st.session_state.pop(k, None)


def calcular_puntos_jornada(resultado_partidos, equipo_fantasy):
    ids = set(equipo_fantasy or [])
    puntos = {pid: 0.0 for pid in ids}
    for resultado in resultado_partidos:
        fantasy = calcular_fantasy(resultado)
        for pid in ids:
            puntos[pid] += float(fantasy.get(pid, 0))
    return puntos, {}

# ADMIN LOGIN / CREATE ROOM
if not st.session_state.codigo_sala:
    st.title("👑 WORLD CUP FANTASY")
    st.subheader("Panel del administrador")
    st.info("Esta página es exclusivamente para el administrador. Los jugadores entran por la página de jugadores.")

    nombre = st.text_input("Nombre del administrador", key="admin_nombre_inicio")
    if st.button("👑 CREAR SALA", use_container_width=True):
        if not nombre.strip():
            st.error("Escribe tu nombre.")
        else:
            codigo, admin_id = crear_sala(nombre.strip())
            st.session_state.codigo_sala = codigo
            st.session_state.admin_id = admin_id
            st.session_state.admin_nombre = nombre.strip()
            st.rerun()
    st.stop()

codigo = st.session_state.codigo_sala
sala = obtener_sala(codigo)

if not sala:
    st.error("La sala ya no existe.")
    if st.button("VOLVER AL INICIO"):
        salir()
        st.rerun()
    st.stop()

jugadores_sala = sala.get("jugadores") or {}
torneo = obtener_torneo(codigo)
estado = sala.get("estado", "esperando")
jornada_actual = int(sala.get("jornada_actual", 0))
seleccion_abierta = bool(sala.get("seleccion_abierta", False))

st.title("👑 PANEL DEL ADMINISTRADOR")
st.markdown(
    f'<div class="box"><div class="small">CÓDIGO DE SALA</div>'
    f'<div class="big">{codigo}</div>'
    f'<div class="small">Comparte este código con los jugadores</div></div>',
    unsafe_allow_html=True,
)

c1,c2,c3 = st.columns(3)
with c1: st.metric("👥 JUGADORES", f"{len(jugadores_sala)} / {MAX_JUGADORES}")
with c2: st.metric("🏟️ JORNADA", f"{jornada_actual} / 7")
with c3: st.metric("ESTADO", estado.upper())

st.divider()
st.header("👥 JUGADORES")

if jugadores_sala:
    ranking = sorted(
        jugadores_sala.items(),
        key=lambda x: float(x[1].get("puntos_totales",0)),
        reverse=True
    )
    for pos,(pid,j) in enumerate(ranking,1):
        equipo = j.get("equipo") or []
        listo = "✅ LISTO" if j.get("listo") else "⏳ PENDIENTE"
        cambios = int(j.get("cambios_jornada",0))

        col_info, col_kick = st.columns([5, 1])
        with col_info:
            st.write(
                f"**{pos}. {j.get('nombre','Sin nombre')}** — {listo} — "
                f"Plantilla: {len(equipo)}/11 — ⭐ {float(j.get('puntos_totales',0)):.2f} — "
                f"🔄 Cambios: {cambios}/3"
            )
        with col_kick:
            if st.button("🗑️ QUITAR", key=f"quitar_{pid}", use_container_width=True):
                ok, mensaje = eliminar_jugador(codigo, pid)
                if not ok:
                    st.error(mensaje)
                else:
                    st.success(f"Jugador {j.get('nombre','')} eliminado.")
                    st.rerun()
else:
    st.info("Todavía no hay jugadores en la sala.")

st.divider()

if torneo is None:
    st.header("🏟️ PREPARAR TORNEO")
    st.write("8 selecciones · 7 jornadas · 28 partidos.")
    if st.button("🗓️ GENERAR TORNEO", use_container_width=True):
        calendario = {"jornadas": generar_jornadas(), "resultados": []}
        guardar_torneo(codigo, calendario, 0)
        st.success("Torneo generado.")
        st.rerun()
else:
    st.header("🎮 CONTROL DE LA PARTIDA")

    if estado in ("esperando", "seleccion") and jornada_actual == 0:
        if not seleccion_abierta:
            if st.button("🔓 ABRIR SELECCIÓN", use_container_width=True):
                abrir_seleccion(codigo)
                st.rerun()
            st.info("La selección está cerrada.")
        else:
            st.success("🟢 SELECCIÓN ABIERTA")
            if st.button("🔒 CERRAR SELECCIÓN", use_container_width=True):
                cerrar_seleccion(codigo)
                st.rerun()

            todos = todos_jugadores_listos(codigo)
            if todos:
                st.success("✅ Todos los jugadores están LISTOS.")
            else:
                st.warning("⏳ Faltan jugadores por marcar LISTO.")

            if st.button("🚀 INICIAR PARTIDA", disabled=not todos, use_container_width=True):
                ok,mensaje = iniciar_partida(codigo)
                if not ok: st.error(mensaje)
                else: st.rerun()

    elif estado in ("jugando","resultado"):
        resultados_guardados = torneo.get("resultados") or []

        if jornada_actual > 0 and len(resultados_guardados) >= jornada_actual:
            st.success(f"🏁 Jornada {jornada_actual} terminada.")
            ultima = resultados_guardados[jornada_actual-1]

            st.subheader("📋 RESULTADOS")
            for partido in ultima:
                st.write(f"**{partido['equipo_a']} {partido['goles_a']} - {partido['goles_b']} {partido['equipo_b']}**")

            if jornada_actual < 7:
                st.info("Los jugadores pueden hacer hasta 3 cambios antes de la siguiente jornada.")
                if st.button(f"▶️ SIMULAR JORNADA {jornada_actual+1}", use_container_width=True):
                    partidos = torneo["jornadas"][jornada_actual]
                    resultados = simular_jornada(partidos)
                    puntos = {}
                    for pid,j in jugadores_sala.items():
                        pj,_ = calcular_puntos_jornada(resultados, j.get("equipo") or [])
                        puntos[pid] = sum(pj.values())
                    torneo["resultados"].append(resultados)
                    guardar_torneo(codigo, torneo, jornada_actual+1)
                    guardar_resultado_jornada(codigo, jornada_actual+1, puntos)
                    st.rerun()
            else:
                st.success("🏆 TORNEO TERMINADO.")
        elif jornada_actual == 0:
            st.info("La partida todavía no ha comenzado.")
        else:
            if st.button(f"▶️ SIMULAR JORNADA {jornada_actual}", use_container_width=True):
                partidos = torneo["jornadas"][jornada_actual-1]
                resultados = simular_jornada(partidos)
                puntos = {}
                for pid,j in jugadores_sala.items():
                    pj,_ = calcular_puntos_jornada(resultados, j.get("equipo") or [])
                    puntos[pid] = sum(pj.values())
                torneo["resultados"].append(resultados)
                guardar_torneo(codigo, torneo, jornada_actual)
                guardar_resultado_jornada(codigo, jornada_actual, puntos)
                st.rerun()

st.divider()
st.header("🏆 CLASIFICACIÓN")
sala_actual = obtener_sala(codigo) or sala
ranking = sorted(
    (sala_actual.get("jugadores") or {}).items(),
    key=lambda x: float(x[1].get("puntos_totales",0)),
    reverse=True
)
if ranking:
    for i,(_,j) in enumerate(ranking,1):
        st.write(f"**{i}. {j.get('nombre','')}** — ⭐ {float(j.get('puntos_totales',0)):.2f} puntos")
else:
    st.info("Aún no hay jugadores.")

st.divider()
if st.button("🚪 SALIR DEL PANEL"):
    salir()
    st.rerun()
