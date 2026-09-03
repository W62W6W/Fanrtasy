import time

import streamlit as st

from datos import jugadores, PRESUPUESTO_FANTASY
from simulador import simular_jornada, generar_jornadas
from firebase import (
    crear_sala,
    obtener_sala,
    unirse_sala,
    guardar_equipo,
    marcar_listo,
    abrir_seleccion,
    cerrar_seleccion,
    iniciar_partida,
    guardar_torneo,
    obtener_torneo,
    guardar_resultado_jornada,
    avanzar_jornada,
    todos_jugadores_listos,
)

st.set_page_config(
    page_title="World Cup Fantasy",
    page_icon="⚽",
    layout="wide",
)

FORMACION = {"POR": 1, "DEF": 4, "MED": 3, "DEL": 3}
NOMBRES_POSICION = {
    "POR": "Portero",
    "DEF": "Defensa",
    "MED": "Mediocampista",
    "DEL": "Delantero",
}

st.markdown("""
<style>
.stApp { background: #0b0b0b; color: white; }
[data-testid="stHeader"] { background: #0b0b0b; }
.block-container { max-width: 1400px; padding-top: 2rem; }
.player-card, .room-card, .score-card {
    background: #171717; border: 1px solid #333;
    border-radius: 14px; padding: 14px; margin-bottom: 10px;
}
.player-name { font-size: 18px; font-weight: 750; }
.player-info { color: #aaa; margin-top: 4px; }
.player-price { font-size: 17px; font-weight: 750; margin-top: 7px; }
.room-code {
    background: #171717; border: 2px solid #555;
    border-radius: 16px; padding: 18px; text-align: center;
    font-size: 38px; font-weight: 900; letter-spacing: 8px;
}
.points { font-size: 28px; font-weight: 850; }
.admin-box {
    background: #201900; border: 1px solid #765d00;
    border-radius: 14px; padding: 18px; margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

defaults = {
    "codigo_sala": None,
    "player_id": None,
    "nombre_jugador": "",
    "es_admin": False,
    "equipo_local": [],
    "presupuesto_local": PRESUPUESTO_FANTASY,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def dinero(valor):
    valor = float(valor or 0)
    if valor >= 1_000_000:
        m = valor / 1_000_000
        return f"{int(m)}M" if m.is_integer() else f"{m:.1f}M"
    if valor >= 1_000:
        k = valor / 1_000
        return f"{int(k)}K" if k.is_integer() else f"{k:.1f}K"
    return str(int(valor))


def contar_posiciones(equipo):
    resultado = {"POR": 0, "DEF": 0, "MED": 0, "DEL": 0}
    for id_jugador in equipo:
        if id_jugador in jugadores:
            resultado[jugadores[id_jugador]["posicion"]] += 1
    return resultado


def equipo_valido(equipo):
    if len(equipo) != 11:
        return False
    posiciones = contar_posiciones(equipo)
    return all(posiciones[p] == n for p, n in FORMACION.items())


def precio_equipo(equipo):
    return sum(
        jugadores[x]["precio"] for x in equipo if x in jugadores
    )


def calcular_puntos_jugador(id_jugador, stats, rival_goles):
    posicion = jugadores[id_jugador]["posicion"]
    puntos = 0
    desglose = []
    minutos = stats.get("minutos", 0)

    if minutos >= 60:
        puntos += 2
        desglose.append(("Minutos (60+)", 2))
    elif minutos > 0:
        puntos += 1
        desglose.append(("Minutos", 1))

    goles = stats.get("goles", 0)
    if goles:
        valor = goles * {"POR": 10, "DEF": 6, "MED": 5, "DEL": 4}[posicion]
        puntos += valor
        desglose.append((f"Goles ({goles})", valor))

    asistencias = stats.get("asistencias", 0)
    if asistencias:
        valor = asistencias * 3
        puntos += valor
        desglose.append((f"Asistencias ({asistencias})", valor))

    acciones = [
        ("tiros_a_puerta", "Tiros a puerta", 0.8),
        ("regates", "Regates", 0.3),
        ("intercepciones", "Intercepciones", 0.4),
        ("duelos_ganados", "Duelos ganados", 0.15),
        ("balones_recuperados", "Recuperaciones", 0.2),
        ("despejes", "Despejes", 0.3),
        ("tapadas", "Tapadas", 1),
    ]

    for clave, nombre, unidad in acciones:
        cantidad = stats.get(clave, 0)
        if cantidad:
            valor = cantidad * unidad
            puntos += valor
            desglose.append((f"{nombre} ({cantidad})", valor))

    for clave, nombre, unidad in [
        ("balones_perdidos", "Balones perdidos", -0.15),
        ("faltas", "Faltas", -0.1),
        ("amarillas", "Amarillas", -1),
        ("rojas", "Rojas", -3),
    ]:
        cantidad = stats.get(clave, 0)
        if cantidad:
            valor = cantidad * unidad
            puntos += valor
            desglose.append((f"{nombre} ({cantidad})", valor))

    if minutos >= 60 and rival_goles == 0:
        if posicion in ["POR", "DEF"]:
            puntos += 4
            desglose.append(("Portería a cero", 4))
        elif posicion == "MED":
            puntos += 1
            desglose.append(("Portería a cero", 1))

    return round(puntos, 2), desglose


def calcular_puntos_jornada(resultados):
    puntos, detalles = {}, {}

    for partido in resultados:
        for stats_key, rival_goles in [
            ("estadisticas_a", partido["goles_b"]),
            ("estadisticas_b", partido["goles_a"]),
        ]:
            for id_jugador, stats in partido.get(stats_key, {}).items():
                if id_jugador not in jugadores:
                    continue
                pts, desglose = calcular_puntos_jugador(
                    id_jugador, stats, rival_goles
                )
                puntos[id_jugador] = pts
                detalles[id_jugador] = {
                    "puntos": pts,
                    "desglose": desglose,
                    "stats": stats,
                }

    return puntos, detalles


def puntos_de_equipo(equipo, puntos_globales):
    return round(
        sum(puntos_globales.get(x, 0) for x in equipo),
        2,
    )


def resetear_sesion():
    st.session_state.codigo_sala = None
    st.session_state.player_id = None
    st.session_state.nombre_jugador = ""
    st.session_state.es_admin = False
    st.session_state.equipo_local = []
    st.session_state.presupuesto_local = PRESUPUESTO_FANTASY


# ============================================================
# INICIO
# ============================================================

st.title("⚽ WORLD CUP FANTASY")
st.caption("Multijugador · hasta 30 jugadores + 1 administrador")

if not st.session_state.codigo_sala:
    col1, col2 = st.columns(2)

    with col1:
        st.header("👑 Crear partida")
        nombre = st.text_input(
            "Nombre del administrador",
            key="crear_nombre",
            placeholder="Ej: Juan",
        )

        if st.button("🏠 CREAR SALA", use_container_width=True):
            if not nombre.strip():
                st.error("Escribe tu nombre.")
            else:
                codigo, admin_id = crear_sala(nombre.strip())
                st.session_state.codigo_sala = codigo
                st.session_state.player_id = admin_id
                st.session_state.nombre_jugador = nombre.strip()
                st.session_state.es_admin = True
                st.rerun()

    with col2:
        st.header("🚪 Unirse a partida")
        nombre = st.text_input(
            "Tu nombre",
            key="unirse_nombre",
            placeholder="Ej: Carlos",
        )
        codigo = st.text_input(
            "Código de sala",
            key="codigo_unirse",
            max_chars=6,
            placeholder="ABC123",
        ).upper()

        if st.button("🚪 UNIRSE", use_container_width=True):
            if not nombre.strip():
                st.error("Escribe tu nombre.")
            elif len(codigo.strip()) != 6:
                st.error("El código debe tener 6 caracteres.")
            else:
                ok, mensaje, player_id = unirse_sala(
                    codigo, nombre.strip()
                )
                if ok:
                    st.session_state.codigo_sala = codigo
                    st.session_state.player_id = player_id
                    st.session_state.nombre_jugador = nombre.strip()
                    st.session_state.es_admin = False
                    st.rerun()
                else:
                    st.error(mensaje)

    st.stop()


# ============================================================
# SALA
# ============================================================

codigo = st.session_state.codigo_sala
sala = obtener_sala(codigo)

if sala is None:
    st.error("La sala ya no existe.")
    if st.button("Volver al inicio"):
        resetear_sesion()
        st.rerun()
    st.stop()

estado = sala.get("estado", "esperando")
seleccion_abierta = bool(sala.get("seleccion_abierta", False))
jornada_actual = int(sala.get("jornada_actual", 0))
jugadores_sala = sala.get("jugadores") or {}
torneo = obtener_torneo(codigo)

st.markdown(
    f'<div class="room-code">{codigo}</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Jugadores", f"{len(jugadores_sala)} / 30")
with c2:
    st.metric("Jornada", f"{jornada_actual} / 7")
with c3:
    st.metric(
        "Rol",
        "👑 ADMIN" if st.session_state.es_admin else "👤 JUGADOR",
    )

st.divider()


# ============================================================
# ADMIN
# ============================================================

if st.session_state.es_admin:
    st.markdown(
        '<div class="admin-box"><h3>👑 PANEL DEL ADMINISTRADOR</h3>'
        '<p>El administrador no es jugador y no ocupa una plaza.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.subheader("👥 Jugadores")

    if not jugadores_sala:
        st.info("Esperando jugadores...")
    else:
        for jugador in jugadores_sala.values():
            icono = "🟢" if jugador.get("listo") else "⚪"
            st.write(
                f"{icono} **{jugador['nombre']}**"
            )

    if estado in ["esperando", "seleccion"]:
        st.divider()
        st.subheader("🎮 Control")

        if not seleccion_abierta:
            st.warning("🔒 Selección cerrada.")
            if st.button(
                "🔓 ABRIR SELECCIÓN",
                use_container_width=True,
            ):
                ok, mensaje = abrir_seleccion(codigo)
                if ok:
                    st.rerun()
                st.error(mensaje)
        else:
            st.success("🔓 Selección abierta.")
            if st.button(
                "🔒 CERRAR SELECCIÓN",
                use_container_width=True,
            ):
                ok, mensaje = cerrar_seleccion(codigo)
                if ok:
                    st.rerun()
                st.error(mensaje)

        if torneo is None:
            if st.button(
                "🎲 GENERAR TORNEO",
                use_container_width=True,
            ):
                torneo_nuevo = {
                    "jornadas": generar_jornadas(),
                    "resultados": {},
                    "puntos": {},
                    "detalles": {},
                }
                guardar_torneo(codigo, torneo_nuevo)
                st.rerun()

        if torneo is not None:
            listos = sum(
                1 for j in jugadores_sala.values()
                if j.get("listo", False)
            )

            st.write(
                f"**Listos: {listos} / {len(jugadores_sala)}**"
            )

            if todos_jugadores_listos(sala):
                st.success("🎉 Todos están listos.")
                if st.button(
                    "🚀 INICIAR PARTIDA",
                    use_container_width=True,
                ):
                    ok, mensaje = iniciar_partida(codigo)
                    if ok:
                        st.rerun()
                    else:
                        st.error(mensaje)
            else:
                st.info("Espera a que todos pulsen LISTO.")

    elif estado == "jugando":
        st.header(f"⚽ JORNADA {jornada_actual} / 7")

        if st.button(
            f"⚽ SIMULAR JORNADA {jornada_actual}",
            use_container_width=True,
        ):
            sala_actual = obtener_sala(codigo)
            torneo_actual = obtener_torneo(sala_actual)
            resultados = simular_jornada(
                torneo_actual["jornadas"][jornada_actual - 1]
            )

            puntos_globales, detalles_globales = (
                calcular_puntos_jornada(resultados)
            )

            torneo_actual["resultados"][str(jornada_actual)] = resultados
            torneo_actual["puntos"][str(jornada_actual)] = puntos_globales
            torneo_actual["detalles"][str(jornada_actual)] = detalles_globales

            puntos_jugadores = {}
            for player_id, jugador in (
                sala_actual.get("jugadores") or {}
            ).items():
                puntos_jugadores[player_id] = puntos_de_equipo(
                    jugador.get("equipo", []),
                    puntos_globales,
                )

            guardar_torneo(codigo, torneo_actual)
            guardar_resultado_jornada(
                codigo,
                jornada_actual,
                resultados,
                puntos_jugadores,
            )
            st.rerun()

    elif estado == "resultado":
        st.header(f"🏆 RESULTADO · JORNADA {jornada_actual}")

        ranking = sorted(
            jugadores_sala.values(),
            key=lambda x: (
                -float(x.get("puntos_totales", 0)),
                x.get("nombre", ""),
            ),
        )

        for i, jugador in enumerate(ranking, 1):
            medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            st.markdown(
                f'<div class="score-card"><b>{medalla} '
                f'{jugador["nombre"]}</b><br>'
                f'Jornada: ⭐ {jugador.get("puntos_jornada", 0):.2f}'
                f' &nbsp;|&nbsp; Total: 🏆 '
                f'{jugador.get("puntos_totales", 0):.2f}</div>',
                unsafe_allow_html=True,
            )

        if st.button(
            f"➡️ PREPARAR JORNADA {jornada_actual + 1}",
            disabled=jornada_actual >= 7,
            use_container_width=True,
        ):
            ok, mensaje = avanzar_jornada(codigo)
            if ok:
                st.rerun()
            else:
                st.error(mensaje)

    elif estado == "final":
        st.header("🏆 FINAL DEL TORNEO")
        st.success("¡Han terminado las 7 jornadas!")

        ranking = sorted(
            jugadores_sala.values(),
            key=lambda x: (
                -float(x.get("puntos_totales", 0)),
                x.get("nombre", ""),
            ),
        )

        for i, jugador in enumerate(ranking, 1):
            medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            st.markdown(
                f'<div class="score-card"><div class="points">'
                f'{medalla} {jugador["nombre"]}</div>'
                f'🏆 {jugador.get("puntos_totales", 0):.2f} puntos'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.balloons()

    st.divider()
    if st.button("🔄 ACTUALIZAR PANEL", use_container_width=True):
        st.rerun()

    time.sleep(2)
    st.rerun()


# ============================================================
# JUGADOR
# ============================================================

yo = jugadores_sala.get(st.session_state.player_id)

if yo is None:
    st.error("No se encontró tu jugador en la sala.")
    st.stop()


# ----------------------- ESPERA -----------------------------

if estado == "esperando" and not seleccion_abierta:
    st.header("⏳ ESPERANDO AL ADMINISTRADOR")
    st.info(
        "La selección está cerrada. No puedes elegir jugadores "
        "hasta que el administrador la abra."
    )

    for jugador in jugadores_sala.values():
        st.write(
            f"👤 **{jugador['nombre']}**"
        )

    st.caption("La pantalla se actualizará automáticamente.")
    time.sleep(2)
    st.rerun()


# ----------------------- SELECCIÓN --------------------------

if estado == "seleccion" and seleccion_abierta:
    st.header(
        "👕 TU FANTASY"
        if jornada_actual == 0
        else f"👕 TU FANTASY · JORNADA {jornada_actual}"
    )

    equipo = st.session_state.equipo_local

    equipo_guardado = yo.get("equipo", [])
    if equipo_guardado and not equipo:
        st.session_state.equipo_local = list(equipo_guardado)
        st.session_state.presupuesto_local = (
            PRESUPUESTO_FANTASY - precio_equipo(equipo_guardado)
        )
        equipo = st.session_state.equipo_local

    presupuesto = st.session_state.presupuesto_local
    posiciones = contar_posiciones(equipo)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Jugadores", f"{len(equipo)} / 11")
    with c2:
        st.metric("Presupuesto", dinero(presupuesto))
    with c3:
        st.metric(
            "Estado",
            "🟢 LISTO" if yo.get("listo") else "⚪ PREPARANDO",
        )

    st.subheader("👕 Mi equipo")

    for posicion in ["POR", "DEF", "MED", "DEL"]:
        st.write(
            f"**{NOMBRES_POSICION[posicion]} "
            f"({posiciones[posicion]}/{FORMACION[posicion]})**"
        )

        ids = [
            x for x in equipo
            if jugadores[x]["posicion"] == posicion
        ]

        if ids:
            columnas = st.columns(min(len(ids), 4))
            for i, id_jugador in enumerate(ids):
                jugador = jugadores[id_jugador]
                with columnas[i % len(columnas)]:
                    st.markdown(
                        f'<div class="player-card">'
                        f'<div class="player-name">{jugador["nombre"]}</div>'
                        f'<div class="player-info">{jugador["equipo"]} · {posicion}</div>'
                        f'<div class="player-price">💰 {dinero(jugador["precio"])}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    if not yo.get("listo", False):
                        if st.button(
                            "❌ Quitar",
                            key=f"quitar_{id_jugador}",
                            use_container_width=True,
                        ):
                            equipo.remove(id_jugador)
                            st.session_state.presupuesto_local = (
                                PRESUPUESTO_FANTASY - precio_equipo(equipo)
                            )
                            guardar_equipo(
                                codigo,
                                st.session_state.player_id,
                                equipo,
                                st.session_state.presupuesto_local,
                            )
                            st.rerun()

    st.divider()
    st.subheader("🛒 Mercado")

    filtro = st.selectbox(
        "Posición",
        ["Todos", "POR", "DEF", "MED", "DEL"],
    )

    for id_jugador, jugador in jugadores.items():
        if id_jugador in equipo:
            continue

        posicion = jugador["posicion"]

        if filtro != "Todos" and posicion != filtro:
            continue

        puede_comprar = (
            not yo.get("listo", False)
            and len(equipo) < 11
            and posiciones[posicion] < FORMACION[posicion]
            and precio_equipo(equipo) + jugador["precio"]
            <= PRESUPUESTO_FANTASY
        )

        st.markdown(
            f'<div class="player-card">'
            f'<div class="player-name">{jugador["nombre"]}</div>'
            f'<div class="player-info">{jugador["equipo"]} · '
            f'{NOMBRES_POSICION[posicion]}</div>'
            f'<div class="player-info">Ataque: {jugador["ataque"]} · '
            f'Defensa: {jugador["defensa"]}</div>'
            f'<div class="player-price">💰 {dinero(jugador["precio"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if puede_comprar:
            if st.button(
                "➕ Fichar",
                key=f"fichar_{id_jugador}",
                use_container_width=True,
            ):
                equipo.append(id_jugador)
                st.session_state.presupuesto_local = (
                    PRESUPUESTO_FANTASY - precio_equipo(equipo)
                )
                guardar_equipo(
                    codigo,
                    st.session_state.player_id,
                    equipo,
                    st.session_state.presupuesto_local,
                )
                st.rerun()

    st.divider()

    if equipo_valido(equipo):
        st.success("✅ Tu equipo 4-3-3 está completo.")

        if not yo.get("listo", False):
            if st.button(
                "✅ ESTOY LISTO",
                use_container_width=True,
            ):
                guardar_equipo(
                    codigo,
                    st.session_state.player_id,
                    equipo,
                    st.session_state.presupuesto_local,
                )
                ok, mensaje = marcar_listo(
                    codigo,
                    st.session_state.player_id,
                    True,
                )
                if ok:
                    st.rerun()
                st.error(mensaje)
        else:
            st.success(
                "🟢 Estás listo. Esperando al administrador."
            )
    else:
        st.warning(
            f"Te faltan {11 - len(equipo)} jugadores "
            "para completar el 4-3-3."
        )

    time.sleep(2)
    st.rerun()


# ----------------------- RESULTADOS -------------------------

if estado == "jugando":
    st.header(f"⚽ JORNADA {jornada_actual}")
    st.info("Esperando a que el administrador simule la jornada.")
    st.metric(
        "Puntos acumulados",
        f"{yo.get('puntos_totales', 0):.2f}",
    )

elif estado == "resultado":
    st.header(f"🏆 RESULTADO · JORNADA {jornada_actual}")

    st.metric(
        "Puntos de esta jornada",
        f"{yo.get('puntos_jornada', 0):.2f}",
    )
    st.metric(
        "Puntos acumulados",
        f"{yo.get('puntos_totales', 0):.2f}",
    )

    ranking = sorted(
        jugadores_sala.values(),
        key=lambda x: (
            -float(x.get("puntos_totales", 0)),
            x.get("nombre", ""),
        ),
    )

    st.subheader("🏆 Clasificación")

    for i, jugador in enumerate(ranking, 1):
        medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        st.write(
            f"{medalla} **{jugador['nombre']}** — "
            f"{jugador.get('puntos_totales', 0):.2f} pts"
        )

elif estado == "final":
    st.header("🏆 FINAL DEL TORNEO")
    st.success("¡Han terminado las 7 jornadas!")

    ranking = sorted(
        jugadores_sala.values(),
        key=lambda x: (
            -float(x.get("puntos_totales", 0)),
            x.get("nombre", ""),
        ),
    )

    for i, jugador in enumerate(ranking, 1):
        medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        st.markdown(
            f'<div class="score-card"><div class="points">'
            f'{medalla} {jugador["nombre"]}</div>'
            f'🏆 {jugador.get("puntos_totales", 0):.2f} puntos'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()
if st.button("🔄 ACTUALIZAR", use_container_width=True):
    st.rerun()

time.sleep(2)
st.rerun()
