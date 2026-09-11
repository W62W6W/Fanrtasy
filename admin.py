
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
from simulador import generar_jornadas, simular_jornada
from fantasy import puntos_de_jornada

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
.admin-box,
.player-row {
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

# =========================
# SESIÓN
# =========================
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "admin_codigo" not in st.session_state:
    st.session_state.admin_codigo = None

if "admin_nombre" not in st.session_state:
    st.session_state.admin_nombre = None

if st.session_state.admin_logged:
    st_autorefresh(
        interval=3000,
        limit=None,
        key="admin_autorefresh",
    )

# =========================
# LOGIN / CREAR SALA
# =========================
if not st.session_state.admin_logged:
    st.title("👑 WORLD CUP FANTASY")
    st.subheader("Panel del administrador")

    st.markdown(
        """
        <div class="admin-box">
            <h2>🎮 Crear una sala</h2>
            <p>El administrador controla la partida. Los jugadores entran desde la página de jugadores.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nombre_admin = st.text_input(
        "Nombre del administrador",
        key="admin_nombre_inicio",
    )

    if st.button(
        "🚀 CREAR SALA",
        use_container_width=True,
        key="crear_sala_admin",
    ):
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

st.markdown(
    f'<div class="room-code">{codigo}</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

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
        puntos_jornada = float(jugador.get("puntos_jornada", 0) or 0)
        puntos_totales = float(jugador.get("puntos_totales", 0) or 0)

        col1, col2 = st.columns([5, 1])

        with col1:
            estado_jugador = "🟢 LISTO" if listo else "🟡 PENDIENTE"

            st.markdown(
                f"""
                <div class="player-row">
                    <strong>{jugador.get('nombre', 'Sin nombre')}</strong><br>
                    {estado_jugador} · {len(equipo)}/11 jugadores<br>
                    ⭐ Jornada: {puntos_jornada:.2f}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    🏆 Total: {puntos_totales:.2f}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            if st.button(
                "🗑️ QUITAR",
                key=f"quitar_jugador_{pid}",
                use_container_width=True,
            ):
                ok, mensaje = eliminar_jugador(codigo, pid)

                if ok:
                    st.success("Jugador eliminado.")
                    st.rerun()
                else:
                    st.error(mensaje or "No se pudo eliminar.")
else:
    st.info("Todavía no hay jugadores en la sala.")

# =========================
# TORNEO
# =========================
st.divider()

if torneo is None:
    st.header("🏟️ PREPARAR TORNEO")
    st.write("8 selecciones · 7 jornadas · todos contra todos.")

    if st.button(
        "📅 GENERAR TORNEO",
        key="generar_torneo_admin",
        use_container_width=True,
    ):
        calendario = {
            "jornadas": generar_jornadas(),
            "resultados": [],
        }

        guardar_torneo(codigo, calendario, 0)
        st.success("Torneo generado.")
        st.rerun()

    st.stop()

# =========================
# CONTROL
# =========================
st.header("🎮 CONTROL DE LA PARTIDA")

estado = sala.get("estado", "esperando")
jornada_actual = int(sala.get("jornada_actual", 0))
resultados_guardados = torneo.get("resultados") or []

# =========================
# SELECCIÓN INICIAL
# =========================
if jornada_actual == 0:

    seleccion_abierta = bool(
        sala.get("seleccion_abierta", False)
    )

    if not seleccion_abierta:

        if st.button(
            "🔓 ABRIR SELECCIÓN",
            key="abrir_seleccion_admin",
            use_container_width=True,
        ):
            abrir_seleccion(codigo)
            st.rerun()

    else:

        st.success("🟢 SELECCIÓN ABIERTA")

        jugadores_completos = (
            bool(jugadores_sala)
            and all(
                len(j.get("equipo") or []) == 11
                for j in jugadores_sala.values()
            )
        )

        todos_listos = todos_jugadores_listos(codigo)

        if todos_listos and jugadores_completos:
            st.success("✅ TODOS LOS JUGADORES ESTÁN LISTOS.")
        else:
            pendientes = sum(
                1
                for j in jugadores_sala.values()
                if not j.get("listo", False)
            )

            incompletos = sum(
                1
                for j in jugadores_sala.values()
                if len(j.get("equipo") or []) != 11
            )

            st.warning(
                f"Pendientes: {pendientes} · "
                f"Plantillas incompletas: {incompletos}"
            )

        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                "🔒 CERRAR SELECCIÓN",
                key="cerrar_seleccion_admin",
                use_container_width=True,
            ):
                cerrar_seleccion(codigo)
                st.rerun()

        with c2:
            if st.button(
                "🚀 EMPEZAR PARTIDA",
                key="empezar_partida_admin",
                disabled=not (todos_listos and jugadores_completos),
                use_container_width=True,
            ):
                ok, mensaje = iniciar_partida(codigo)

                if not ok:
                    st.error(mensaje)
                else:
                    st.success("¡Partida iniciada!")
                    st.rerun()

# =========================
# JORNADAS
# =========================
else:

    siguiente_jornada = len(resultados_guardados) + 1

    if siguiente_jornada <= 7:

        if siguiente_jornada == 1:
            st.success(
                "🚀 PARTIDA INICIADA. "
                "Las alineaciones están bloqueadas."
            )
        else:
            st.success(
                f"Jornada {siguiente_jornada - 1} terminada. "
                "Los jugadores pueden hacer hasta 3 cambios."
            )

        st.subheader(f"🏟️ JORNADA {siguiente_jornada}")

        if st.button(
            f"▶️ SIMULAR JORNADA {siguiente_jornada}",
            key=f"simular_jornada_{siguiente_jornada}",
            use_container_width=True,
        ):

            partidos = torneo["jornadas"][siguiente_jornada - 1]
            resultados = simular_jornada(partidos)

            puntos_por_usuario = {}
            puntos_jugadores = {}
            detalles_jugadores = {}

            for pid, jugador in jugadores_sala.items():

                equipo_fantasy = jugador.get("equipo") or []

                puntos_individuales, detalles = puntos_de_jornada(
                    resultados,
                    equipo_fantasy,
                )

                puntos_por_usuario[pid] = float(
                    sum(puntos_individuales.values())
                )

                puntos_jugadores[pid] = {
                    player_id: float(puntos)
                    for player_id, puntos
                    in puntos_individuales.items()
                }

                detalles_jugadores[pid] = {
                    player_id: {
                        concepto: float(valor)
                        for concepto, valor in detalle.items()
                    }
                    for player_id, detalle
                    in detalles.items()
                }

            torneo["resultados"].append(resultados)

            guardar_torneo(
                codigo,
                torneo,
                siguiente_jornada,
            )

            guardar_resultado_jornada(
                codigo,
                siguiente_jornada,
                puntos_por_usuario,
                puntos_jugadores,
                detalles_jugadores,
            )

            st.success(
                f"Jornada {siguiente_jornada} simulada."
            )
            st.rerun()

        if resultados_guardados:

            st.subheader(
                f"📋 RESULTADO JORNADA "
                f"{len(resultados_guardados)}"
            )

            for partido in resultados_guardados[-1]:

                st.write(
                    f"**{partido['equipo_a']} "
                    f"{partido['goles_a']} - "
                    f"{partido['goles_b']} "
                    f"{partido['equipo_b']}**"
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
    key=lambda x: float(
        x[1].get("puntos_totales", 0) or 0
    ),
    reverse=True,
)

if ranking:

    for posicion, (_, jugador) in enumerate(ranking, 1):

        puntos_jornada = float(
            jugador.get("puntos_jornada", 0) or 0
        )

        puntos_totales = float(
            jugador.get("puntos_totales", 0) or 0
        )

        st.markdown(
            f"""
            <div class="player-row">
                <strong>#{posicion} ·
                {jugador.get('nombre', 'Sin nombre')}</strong><br>
                ⭐ Jornada: {puntos_jornada:.2f}
                &nbsp;&nbsp;|&nbsp;&nbsp;
                🏆 Total: {puntos_totales:.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    st.info("Todavía no hay jugadores para clasificar.")

# =========================
# SALIR
# =========================
st.divider()

if st.button(
    "🚪 SALIR DEL PANEL",
    key="salir_panel_admin",
    use_container_width=True,
):
    st.session_state.admin_logged = False
    st.session_state.admin_codigo = None
    st.session_state.admin_nombre = None
    st.rerun()
