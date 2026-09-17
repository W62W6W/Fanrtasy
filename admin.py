import streamlit as st
from streamlit_autorefresh import st_autorefresh

from firebase import (
    crear_sala,
    obtener_sala,
    guardar_torneo,
    obtener_torneo,
    abrir_seleccion,
    cerrar_seleccion,
    todos_jugadores_listos,
    iniciar_partida,
    guardar_resultado_jornada,
    eliminar_jugador,
)
from datos import jugadores
from simulador import generar_jornadas, simular_jornada
from fantasy import calcular_fantasy, calcular_desgloses_partido

st.set_page_config(
    page_title="World Cup Fantasy — Admin",
    page_icon="👑",
    layout="wide",
)

MAX_JUGADORES = 30

# =========================
# ESTILO AZUL / ÍNDIGO
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #061226 0%, #0b1730 55%, #101d40 100%);
    color: white;
}
[data-testid="stSidebar"] {
    background: #08152b;
}
h1,h2,h3,h4,h5,h6,p,label,span {
    color: white !important;
}
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    color: white !important;
    border: 1px solid #6366f1 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: #101f3d !important;
    color: white !important;
    border: 1px solid #31518a !important;
}
input {
    color: white !important;
}
.admin-box,.player-row {
    background: linear-gradient(145deg, #122957, #0b1835);
    border: 1px solid #315ca8;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
}
.room-code {
    background: #172f67;
    border: 2px solid #4f7cff;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    font-size: 36px;
    font-weight: 900;
    letter-spacing: 8px;
    color: #dbeafe;
}
</style>
""", unsafe_allow_html=True)

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "admin_codigo" not in st.session_state:
    st.session_state.admin_codigo = None
if "admin_nombre" not in st.session_state:
    st.session_state.admin_nombre = None

if st.session_state.admin_logged:
    st_autorefresh(interval=3000, limit=None, key="admin_autorefresh")

# =========================
# CREAR SALA
# =========================
if not st.session_state.admin_logged:
    st.title("👑 WORLD CUP FANTASY")
    st.subheader("Panel del administrador")

    st.markdown(
        '<div class="admin-box"><h2>🎮 Crear una sala</h2>'
        '<p>El administrador controla la partida. Los jugadores entran desde la página de jugadores.</p></div>',
        unsafe_allow_html=True,
    )

    nombre_admin = st.text_input("Nombre del administrador", key="admin_nombre_inicio")

    if st.button("🚀 CREAR SALA", use_container_width=True, key="crear_sala_admin"):
        if not nombre_admin.strip():
            st.error("Escribe tu nombre.")
        else:
            try:
                codigo, _ = crear_sala(nombre_admin.strip())
                st.session_state.admin_logged = True
                st.session_state.admin_codigo = codigo
                st.session_state.admin_nombre = nombre_admin.strip()
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo crear la sala: {e}")

    st.caption("1 administrador + hasta 30 jugadores.")
    st.stop()

# =========================
# SALA
# =========================
codigo = st.session_state.admin_codigo
sala = obtener_sala(codigo)

if not sala:
    st.error("La sala ya no existe.")
    st.stop()

jugadores_sala = sala.get("jugadores") or {}
torneo = obtener_torneo(codigo)

st.title("👑 WORLD CUP FANTASY — ADMIN")
st.write(f"Administrador: **{st.session_state.admin_nombre}**")
st.markdown(f'<div class="room-code">{codigo}</div>', unsafe_allow_html=True)

c1,c2,c3 = st.columns(3)
with c1:
    st.metric("👥 JUGADORES", f"{len(jugadores_sala)} / {MAX_JUGADORES}")
with c2:
    st.metric("🏟️ JORNADA", sala.get("jornada_actual", 0))
with c3:
    st.metric("🎮 ESTADO", str(sala.get("estado", "esperando")).upper())

# =========================
# JUGADORES
# =========================
st.divider()
st.header("👥 JUGADORES")

if jugadores_sala:
    for pid, jugador in jugadores_sala.items():
        equipo = jugador.get("equipo") or []
        listo = jugador.get("listo", False)
        pj = float(jugador.get("puntos_jornada", 0) or 0)
        pt = float(jugador.get("puntos_totales", 0) or 0)

        x,y = st.columns([5,1])
        with x:
            estado_jugador = "🟢 LISTO" if listo else "🟡 PENDIENTE"
            st.markdown(
                f'<div class="player-row"><strong>{jugador.get("nombre","Sin nombre")}</strong><br>'
                f'{estado_jugador} · {len(equipo)}/11 jugadores · '
                f'⭐ Jornada: {pj:.2f} · 🏆 Total: {pt:.2f}</div>',
                unsafe_allow_html=True,
            )
        with y:
            if st.button("🗑️ QUITAR", key=f"quitar_jugador_{pid}", use_container_width=True):
                ok,msg = eliminar_jugador(codigo,pid)
                if ok:
                    st.rerun()
                else:
                    st.error(msg or "No se pudo eliminar.")
else:
    st.info("Todavía no hay jugadores en la sala.")

# =========================
# TORNEO
# =========================
st.divider()

if torneo is None:
    st.header("🏟️ PREPARAR TORNEO")
    st.write("8 selecciones · 7 jornadas · todos contra todos.")

    if st.button("📅 GENERAR TORNEO", key="generar_torneo_admin", use_container_width=True):
        calendario = {"jornadas": generar_jornadas(), "resultados": []}
        guardar_torneo(codigo, calendario, 0)
        st.success("Torneo generado.")
        st.rerun()

    st.stop()

# =========================
# CONTROL DE PARTIDA
# =========================
st.header("🎮 CONTROL DE LA PARTIDA")

estado = sala.get("estado", "esperando")
jornada_actual = int(sala.get("jornada_actual", 0))
resultados_guardados = torneo.get("resultados") or []

if jornada_actual == 0:
    abierta = bool(sala.get("seleccion_abierta", False))

    if not abierta:
        if st.button("🔓 ABRIR SELECCIÓN", key="abrir_seleccion_admin", use_container_width=True):
            abrir_seleccion(codigo)
            st.rerun()
    else:
        st.success("🟢 SELECCIÓN ABIERTA")

        completos = bool(jugadores_sala) and all(
            len(j.get("equipo") or []) == 11 for j in jugadores_sala.values()
        )
        listos = todos_jugadores_listos(codigo)

        if listos and completos:
            st.success("✅ TODOS LOS JUGADORES ESTÁN LISTOS.")
        else:
            pendientes = sum(not j.get("listo",False) for j in jugadores_sala.values())
            incompletos = sum(len(j.get("equipo") or []) != 11 for j in jugadores_sala.values())
            st.warning(f"Pendientes: {pendientes} · Plantillas incompletas: {incompletos}")

        if st.button(
            "🚀 EMPEZAR PARTIDA",
            key="empezar_partida_admin",
            disabled=not (listos and completos),
            use_container_width=True,
        ):
            # Al iniciar la partida la selección se cierra automáticamente.
            ok, msg = iniciar_partida(codigo)
            if not ok:
                st.error(msg)
            else:
                st.success("¡Partida iniciada! La selección se ha cerrado automáticamente.")
                st.rerun()

else:
    siguiente = len(resultados_guardados) + 1

    if siguiente <= 7:
        if siguiente == 1:
            st.success("🚀 PARTIDA INICIADA. Las alineaciones están bloqueadas.")
        else:
            st.success(f"Jornada {siguiente-1} terminada. Los jugadores pueden hacer hasta 3 cambios.")

        st.subheader(f"🏟️ JORNADA {siguiente}")

        if st.button(f"▶️ SIMULAR JORNADA {siguiente}",
                     key=f"simular_jornada_{siguiente}",
                     use_container_width=True):

            partidos = torneo["jornadas"][siguiente-1]
            resultados = simular_jornada(partidos)

            puntos_por_usuario = {}
            puntos_jugadores = {}
            detalles_jugadores = {}

            # Calculamos los puntos usando la plantilla que EXISTE
            # en el momento exacto de esta jornada.
            for pid, jugador_sala in jugadores_sala.items():
                equipo_fantasy = jugador_sala.get("equipo") or []

                puntos_individuales = {jugador_id: 0.0 for jugador_id in equipo_fantasy}
                detalles_individuales = {jugador_id: {} for jugador_id in equipo_fantasy}

                for resultado in resultados:
                    fantasy_resultado = calcular_fantasy(resultado)
                    desglose_resultado = calcular_desgloses_partido(resultado)

                    for jugador_id in equipo_fantasy:
                        if jugador_id in fantasy_resultado:
                            puntos_individuales[jugador_id] += float(
                                fantasy_resultado.get(jugador_id, 0)
                            )

                            for concepto, valor in desglose_resultado.get(jugador_id, {}).items():
                                detalles_individuales[jugador_id][concepto] = (
                                    detalles_individuales[jugador_id].get(concepto, 0)
                                    + float(valor)
                                )

                puntos_por_usuario[pid] = float(sum(puntos_individuales.values()))
                puntos_jugadores[pid] = puntos_individuales
                detalles_jugadores[pid] = detalles_individuales

            torneo["resultados"].append(resultados)

            guardar_torneo(codigo, torneo, siguiente)

            guardar_resultado_jornada(
                codigo,
                siguiente,
                puntos_por_usuario,
                puntos_jugadores,
                detalles_jugadores,
            )

            st.success(f"Jornada {siguiente} simulada.")
            st.rerun()

        if resultados_guardados:
            st.subheader(f"📋 RESULTADO JORNADA {len(resultados_guardados)}")
            for partido in resultados_guardados[-1]:
                st.write(
                    f"**{partido['equipo_a']} {partido['goles_a']} - "
                    f"{partido['goles_b']} {partido['equipo_b']}**"
                )
    else:
        st.success("🏆 TORNEO TERMINADO")
        st.write("Se han disputado las 7 jornadas.")

# =========================
# CLASIFICACIÓN
# =========================
st.divider()
st.header("🏆 CLASIFICACIÓN")

sala_actualizada = obtener_sala(codigo) or sala

ranking = sorted(
    (sala_actualizada.get("jugadores") or {}).items(),
    key=lambda x: float(x[1].get("puntos_totales",0) or 0),
    reverse=True,
)

if ranking:
    for i,(_,jugador) in enumerate(ranking,1):
        pj = float(jugador.get("puntos_jornada",0) or 0)
        pt = float(jugador.get("puntos_totales",0) or 0)
        st.markdown(
            f'<div class="player-row"><strong>#{i} · {jugador.get("nombre","Sin nombre")}</strong><br>'
            f'⭐ Jornada: {pj:.2f} &nbsp;&nbsp;|&nbsp;&nbsp; 🏆 Total: {pt:.2f}</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("Todavía no hay jugadores para clasificar.")

st.divider()

if st.button("🚪 SALIR DEL PANEL", key="salir_panel_admin", use_container_width=True):
    st.session_state.admin_logged = False
    st.session_state.admin_codigo = None
    st.session_state.admin_nombre = None
    st.rerun()
