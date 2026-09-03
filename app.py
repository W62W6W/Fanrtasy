import streamlit as st
from streamlit_autorefresh import st_autorefresh
from firebase import (
    crear_sala,
    obtener_sala,
    unirse_sala,
    guardar_equipo,
    marcar_listo,
    abrir_seleccion,
    cerrar_seleccion,
    todos_jugadores_listos,
    iniciar_partida,
    guardar_torneo,
    obtener_torneo,
    guardar_resultado_jornada,
)
from datos import jugadores
from simulador import generar_jornadas, simular_jornada
from fantasy import calcular_fantasy, calcular_desgloses_partido

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="World Cup Fantasy",
    page_icon="⚽",
    layout="wide",
)

PRESUPUESTO = 540_000_000
MAX_JUGADORES = 30
FORMACION = {"POR": 1, "DEF": 4, "MED": 3, "DEL": 3}

# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .stApp { background: #050505; color: white; }
    [data-testid="stSidebar"] { background: #080808; }
    h1,h2,h3,h4,h5,h6,p,label { color: white !important; }

    div[data-baseweb="select"] > div {
        background: #111 !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    div[data-baseweb="select"] span { color: white !important; }

    .stButton > button {
        background: #151515 !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        min-height: 42px !important;
    }
    .stButton > button:hover {
        background: #222 !important;
        border-color: white !important;
    }

    .box {
        background: linear-gradient(145deg,#171717,#090909);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 12px;
    }
    .big {
        font-size: 30px;
        font-weight: 700;
    }
    .small {
        color: #999;
        font-size: 13px;
        letter-spacing: 1px;
    }
    .player-card {
        background: linear-gradient(145deg,#171717,#090909);
        border: 1px solid #292929;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 7px;
    }
    .player-name {
        font-size: 18px;
        font-weight: 700;
    }
    .player-info {
        color: #aaa;
        font-size: 13px;
        margin-top: 4px;
    }
    .slot {
        background: #101010;
        border: 1px dashed #444;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        text-align: center;
    }
    .filled {
        border-style: solid;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def dinero(valor):
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return "0"

    if valor >= 1_000_000:
        n = valor / 1_000_000
        return f"{int(n)}M" if n.is_integer() else f"{n:.1f}M"
    if valor >= 1_000:
        n = valor / 1_000
        return f"{int(n)}K" if n.is_integer() else f"{n:.1f}K"
    return str(int(valor))


def contar_posiciones(equipo):
    resultado = {p: 0 for p in FORMACION}
    for pid in equipo or []:
        jugador = jugadores.get(pid)
        if jugador and jugador.get("posicion") in resultado:
            resultado[jugador["posicion"]] += 1
    return resultado


def plantilla_completa(equipo):
    p = contar_posiciones(equipo)
    return all(p[pos] == cantidad for pos, cantidad in FORMACION.items())


def valor_equipo(equipo):
    total = 0
    for pid in equipo or []:
        try:
            total += float(jugadores[pid].get("precio", 0))
        except (KeyError, TypeError, ValueError):
            pass
    return total


def jugador_html(jugador):
    st.markdown(
        f"""
        <div class="player-card">
            <div class="player-name">{jugador['nombre']}</div>
            <div class="player-info">
                {jugador.get('equipo','')} · {jugador.get('posicion','')}
            </div>
            <div class="player-info">💰 {dinero(jugador.get('precio', 0))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_alineacion(equipo, titulo="TU ALINEACIÓN"):
    st.subheader(titulo)
    posiciones = {p: [] for p in FORMACION}

    for pid in equipo or []:
        if pid in jugadores:
            posiciones[jugadores[pid]["posicion"]].append(pid)

    nombres = {
        "POR": "🧤 PORTERO",
        "DEF": "🛡️ DEFENSAS",
        "MED": "⚙️ MEDIOCAMPISTAS",
        "DEL": "⚽ DELANTEROS",
    }

    for pos in ["POR", "DEF", "MED", "DEL"]:
        st.caption(nombres[pos])
        for i in range(FORMACION[pos]):
            if i < len(posiciones[pos]):
                j = jugadores[posiciones[pos][i]]
                st.markdown(
                    f'<div class="slot filled"><b>{j["nombre"]}</b><br>'
                    f'<span style="color:#aaa">{j["equipo"]} · '
                    f'{dinero(j.get("precio",0))}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="slot">{pos} vacío</div>',
                    unsafe_allow_html=True,
                )


def limpiar_sesion():
    for clave in [
        "rol", "codigo_sala", "player_id", "nombre_usuario",
        "admin_id", "admin_nombre"
    ]:
        st.session_state.pop(clave, None)


def puntos_de_jornada(resultado_partidos, equipo_fantasy):
    """
    Suma los puntos Fantasy de los 11 jugadores del usuario
    para todos los partidos de la jornada.
    """
    ids = set(equipo_fantasy or [])
    puntos = {pid: 0.0 for pid in ids}
    detalles = {pid: {} for pid in ids}

    for resultado in resultado_partidos:
        fantasy = calcular_fantasy(resultado)
        desgloses = calcular_desgloses_partido(resultado)

        for pid in ids:
            if pid in fantasy:
                puntos[pid] += float(fantasy[pid])
                for concepto, valor in desgloses.get(pid, {}).items():
                    detalles[pid][concepto] = (
                        detalles[pid].get(concepto, 0) + float(valor)
                    )

    return puntos, detalles


def calcular_puntos_todos_jugadores(sala, torneo):
    """
    Calcula, desde cero, los puntos acumulados de cada jugador de la sala
    usando los resultados ya guardados en el torneo.
    """
    jugadores_sala = sala.get("jugadores") or {}
    acumulados = {pid: 0.0 for pid in jugadores_sala}

    resultados = torneo.get("resultados") or []
    for jornada_resultados in resultados:
        for resultado in jornada_resultados:
            fantasy = calcular_fantasy(resultado)
            for pid, datos_jugador in jugadores_sala.items():
                if pid in (datos_jugador.get("equipo") or []):
                    acumulados[pid] += sum(
                        fantasy.get(player_id, 0)
                        for player_id in datos_jugador.get("equipo") or []
                    )

    return acumulados


# ============================================================
# SESSION STATE
# ============================================================

if "rol" not in st.session_state:
    st.session_state.rol = None

if "codigo_sala" not in st.session_state:
    st.session_state.codigo_sala = None

if "player_id" not in st.session_state:
    st.session_state.player_id = None

if "admin_id" not in st.session_state:
    st.session_state.admin_id = None

# ============================================================
# ACTUALIZACIÓN AUTOMÁTICA MULTIJUGADOR
# ============================================================
# Mientras un usuario está dentro de una sala, la pantalla se
# actualiza cada 3 segundos para detectar nuevos jugadores,
# cambios del administrador, jugadores listos y resultados.
if st.session_state.get("rol") in ("admin", "player"):
    st_autorefresh(
        interval=3000,
        limit=None,
        key="fantasy_sala_autorefresh",
    )

# ============================================================
# PANTALLA INICIAL
# ============================================================

if not st.session_state.rol:
    st.title("⚽ WORLD CUP FANTASY")
    st.subheader("Multijugador")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            '<div class="box"><div class="big">👑 Crear sala</div>'
            '<div class="small">Eres el administrador y controlas la partida.</div></div>',
            unsafe_allow_html=True,
        )
        nombre_admin = st.text_input(
            "Nombre del administrador",
            key="nombre_admin_inicio",
        )
        if st.button("CREAR SALA", use_container_width=True):
            if not nombre_admin.strip():
                st.error("Escribe tu nombre.")
            else:
                codigo, admin_id = crear_sala(nombre_admin.strip())
                st.session_state.rol = "admin"
                st.session_state.codigo_sala = codigo
                st.session_state.admin_id = admin_id
                st.session_state.admin_nombre = nombre_admin.strip()
                st.rerun()

    with c2:
        st.markdown(
            '<div class="box"><div class="big">👤 Unirse a sala</div>'
            '<div class="small">Entra con el código que te dé el administrador.</div></div>',
            unsafe_allow_html=True,
        )
        codigo = st.text_input(
            "Código de sala",
            max_chars=6,
            key="codigo_inicio",
        ).strip().upper()
        nombre = st.text_input(
            "Tu nombre",
            key="nombre_inicio",
        )
        if st.button("UNIRME A LA SALA", use_container_width=True):
            if not codigo or not nombre.strip():
                st.error("Escribe el código y tu nombre.")
            else:
                ok, mensaje, player_id = unirse_sala(codigo, nombre.strip())
                if ok:
                    st.session_state.rol = "player"
                    st.session_state.codigo_sala = codigo
                    st.session_state.player_id = player_id
                    st.session_state.nombre_usuario = nombre.strip()
                    st.rerun()
                else:
                    st.error(mensaje or "No se pudo entrar.")

    st.divider()
    st.caption("1 administrador + hasta 30 jugadores.")
    st.stop()

# ============================================================
# OBTENER SALA
# ============================================================

codigo = st.session_state.codigo_sala
sala = obtener_sala(codigo)

if not sala:
    st.error("La sala ya no existe.")
    if st.button("VOLVER AL INICIO"):
        limpiar_sesion()
        st.rerun()
    st.stop()

# ============================================================
# ADMINISTRADOR
# ============================================================

if st.session_state.rol == "admin":
    st.title("👑 PANEL DEL ADMINISTRADOR")
    st.markdown(
        f'<div class="box"><div class="small">CÓDIGO DE SALA</div>'
        f'<div class="big">{codigo}</div></div>',
        unsafe_allow_html=True,
    )

    jugadores_sala = sala.get("jugadores") or {}
    torneo = obtener_torneo(codigo)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("👥 JUGADORES", f"{len(jugadores_sala)} / {MAX_JUGADORES}")
    with c2:
        st.metric("🏟️ JORNADA", sala.get("jornada_actual", 0))
    with c3:
        estado = sala.get("estado", "esperando")
        st.metric("ESTADO", estado.upper())

    st.divider()
    st.header("👥 JUGADORES")

    if jugadores_sala:
        for pid, jugador in jugadores_sala.items():
            equipo = jugador.get("equipo") or []
            estado_listo = "✅ LISTO" if jugador.get("listo") else "⏳ PENDIENTE"
            st.write(
                f"**{jugador.get('nombre','Sin nombre')}** — "
                f"{estado_listo} — {len(equipo)}/11 jugadores"
            )
    else:
        st.info("Todavía no hay jugadores en la sala.")

    st.divider()

    # Crear el calendario una sola vez.
    if torneo is None:
        st.header("🏟️ Preparar torneo")
        st.write("Hay 8 selecciones y 7 jornadas.")
        if st.button("GENERAR TORNEO", use_container_width=True):
            calendario = {
                "jornadas": generar_jornadas(),
                "resultados": [],
            }
            guardar_torneo(codigo, calendario, 0)
            st.success("Torneo generado.")
            st.rerun()
    else:
        st.header("🎮 CONTROL DE LA PARTIDA")

        seleccion_abierta = bool(sala.get("seleccion_abierta", False))
        jornada_actual = int(sala.get("jornada_actual", 0))

        # Antes de empezar: abrir selección.
        if sala.get("estado") == "esperando" and jornada_actual == 0:
            if not seleccion_abierta:
                if st.button("🔓 ABRIR SELECCIÓN", use_container_width=True):
                    abrir_seleccion(codigo)
                    st.rerun()
            else:
                st.success("🟢 Selección abierta.")
                if st.button("🔒 CERRAR SELECCIÓN", use_container_width=True):
                    cerrar_seleccion(codigo)
                    st.rerun()

                todos_listos = todos_jugadores_listos(sala)
                if todos_listos:
                    st.success("Todos los jugadores están LISTOS.")
                else:
                    st.warning("Faltan jugadores por marcar LISTO.")

                if st.button(
                    "🚀 INICIAR PARTIDA",
                    disabled=not todos_listos,
                    use_container_width=True,
                ):
                    ok, mensaje = iniciar_partida(codigo)
                    if not ok:
                        st.error(mensaje)
                    else:
                        st.rerun()

        # Partida en curso: el admin controla cada jornada.
        elif sala.get("estado") in ("jugando", "resultado"):
            resultados_guardados = torneo.get("resultados") or []

            # Si la jornada actual ya tiene resultado, mostramos resultado
            # y ofrecemos la siguiente jornada. NO abrimos selección otra vez.
            if len(resultados_guardados) >= jornada_actual:
                st.success(
                    f"Jornada {jornada_actual} terminada. "
                    "Las alineaciones permanecen bloqueadas."
                )

                ultima = resultados_guardados[jornada_actual - 1]
                for partido in ultima:
                    st.write(
                        f"**{partido['equipo_a']} {partido['goles_a']} - "
                        f"{partido['goles_b']} {partido['equipo_b']}**"
                    )

                if jornada_actual < 7:
                    if st.button(
                        f"▶️ SIMULAR JORNADA {jornada_actual + 1}",
                        use_container_width=True,
                    ):
                        partidos = torneo["jornadas"][jornada_actual]
                        resultados = simular_jornada(partidos)
                        puntos = {}

                        for pid, jugador in jugadores_sala.items():
                            equipo_fantasy = jugador.get("equipo") or []
                            puntos_jugador, _ = puntos_de_jornada(
                                resultados, equipo_fantasy
                            )
                            puntos[pid] = sum(puntos_jugador.values())

                        # Guardamos los nuevos resultados en el torneo.
                        torneo["resultados"].append(resultados)
                        guardar_torneo(
                            codigo,
                            torneo,
                            jornada_actual + 1,
                        )

                        guardar_resultado_jornada(
                            codigo,
                            jornada_actual + 1,
                            puntos,
                        )
                        st.rerun()
                else:
                    st.success("🏆 TORNEO TERMINADO.")

            else:
                # Jornada pendiente de simular.
                if jornada_actual == 0:
                    st.info("La partida todavía no ha comenzado.")
                else:
                    if st.button(
                        f"▶️ SIMULAR JORNADA {jornada_actual}",
                        use_container_width=True,
                    ):
                        partidos = torneo["jornadas"][jornada_actual - 1]
                        resultados = simular_jornada(partidos)
                        puntos = {}

                        for pid, jugador in jugadores_sala.items():
                            equipo_fantasy = jugador.get("equipo") or []
                            puntos_jugador, _ = puntos_de_jornada(
                                resultados, equipo_fantasy
                            )
                            puntos[pid] = sum(puntos_jugador.values())

                        torneo["resultados"].append(resultados)
                        guardar_torneo(codigo, torneo, jornada_actual)
                        guardar_resultado_jornada(
                            codigo,
                            jornada_actual,
                            puntos,
                        )
                        st.rerun()

        st.divider()
        st.header("🏆 CLASIFICACIÓN")

        sala_actualizada = obtener_sala(codigo) or sala
        ranking = sorted(
            (sala_actualizada.get("jugadores") or {}).items(),
            key=lambda x: float(x[1].get("puntos_totales", 0)),
            reverse=True,
        )

        if ranking:
            for i, (_, jugador) in enumerate(ranking, 1):
                st.write(
                    f"**{i}. {jugador.get('nombre','')}** — "
                    f"⭐ {float(jugador.get('puntos_totales',0)):.2f} puntos"
                )

    st.divider()
    if st.button("🚪 SALIR DEL PANEL"):
        limpiar_sesion()
        st.rerun()

    st.stop()

# ============================================================
# JUGADOR
# ============================================================

player_id = st.session_state.player_id
jugadores_sala = sala.get("jugadores") or {}
yo = jugadores_sala.get(player_id)

if not yo:
    st.error("No se encontró tu jugador en la sala.")
    st.stop()

st.title("⚽ WORLD CUP FANTASY")
st.write(
    f"Hola, **{yo.get('nombre','')}** · Sala **{codigo}**"
)

estado = sala.get("estado", "esperando")
seleccion_abierta = bool(sala.get("seleccion_abierta", False))
mi_equipo = yo.get("equipo") or []
ya_seleccionado = len(mi_equipo) == 11

# ============================================================
# ESPERA
# ============================================================

if estado == "esperando" and not seleccion_abierta:
    st.info("⏳ Esperando a que el administrador abra la selección.")
    st.divider()
    st.subheader("👥 Jugadores conectados")
    for jugador in jugadores_sala.values():
        st.write(f"• {jugador.get('nombre','')}")
    st.stop()

# ============================================================
# SELECCIÓN
# ============================================================

if seleccion_abierta and not ya_seleccionado:
    st.success("🟢 SELECCIÓN ABIERTA")
    st.write("Construye tu 4-3-3. Una vez guardada, **NO podrás cambiarla**.")

    col_plantilla, col_mercado = st.columns([1, 1.35])

    # ---------------- TU ALINEACIÓN ----------------
    with col_plantilla:
        mostrar_alineacion(mi_equipo)

        st.divider()
        posiciones = contar_posiciones(mi_equipo)
        valor = valor_equipo(mi_equipo)
        restante = PRESUPUESTO - valor

        c1, c2 = st.columns(2)
        with c1:
            st.metric("💰 RESTANTE", dinero(restante))
        with c2:
            st.metric("👥 JUGADORES", f"{len(mi_equipo)} / 11")

        st.divider()

        # El botón queda debajo de la alineación, como pidió el usuario.
        puede_guardar = (
            plantilla_completa(mi_equipo)
            and valor <= PRESUPUESTO
        )

        if st.button(
            "💾 GUARDAR ALINEACIÓN",
            disabled=not puede_guardar,
            use_container_width=True,
        ):
            ok, mensaje = guardar_equipo(
                codigo,
                player_id,
                mi_equipo,
                PRESUPUESTO - valor,
            )
            if not ok:
                st.error(mensaje)
            else:
                st.rerun()

        if not plantilla_completa(mi_equipo):
            p = contar_posiciones(mi_equipo)
            st.caption(
                f"Necesitas 1 POR, 4 DEF, 3 MED y 3 DEL. "
                f"Actualmente: {p['POR']} POR · {p['DEF']} DEF · "
                f"{p['MED']} MED · {p['DEL']} DEL."
            )

    # ---------------- MERCADO ----------------
    with col_mercado:
        st.header("🛒 MERCADO")

        filtro_pos = st.selectbox(
            "Posición",
            ["Todos", "POR", "DEF", "MED", "DEL"],
        )
        filtro_eq = st.selectbox(
            "Selección",
            ["Todos"] + sorted(
                {j.get("equipo") for j in jugadores.values()}
            ),
        )

        limites = FORMACION
        actuales = contar_posiciones(mi_equipo)

        for pid, jugador in jugadores.items():
            if pid in mi_equipo:
                continue

            pos = jugador.get("posicion")
            eq = jugador.get("equipo")

            if filtro_pos != "Todos" and pos != filtro_pos:
                continue
            if filtro_eq != "Todos" and eq != filtro_eq:
                continue

            jugador_html(jugador)

            try:
                precio = float(jugador.get("precio", 0))
            except (TypeError, ValueError):
                precio = 0

            if actuales.get(pos, 0) >= limites.get(pos, 0):
                st.button(
                    f"LÍMITE DE {pos}",
                    key=f"lim_{pid}",
                    disabled=True,
                    use_container_width=True,
                )
            elif valor_equipo(mi_equipo) + precio > PRESUPUESTO:
                st.button(
                    "💰 PRESUPUESTO INSUFICIENTE",
                    key=f"money_{pid}",
                    disabled=True,
                    use_container_width=True,
                )
            elif len(mi_equipo) >= 11:
                st.button(
                    "PLANTILLA COMPLETA",
                    key=f"full_{pid}",
                    disabled=True,
                    use_container_width=True,
                )
            else:
                if st.button(
                    "➕ AÑADIR",
                    key=f"add_{pid}",
                    use_container_width=True,
                ):
                    mi_equipo.append(pid)
                    st.rerun()

# ============================================================
# ALINEACIÓN YA GUARDADA: BLOQUEADA
# ============================================================

elif ya_seleccionado:
    st.success(
        "🔒 Tu alineación está guardada y bloqueada. "
        "No puedes cambiar jugadores durante el torneo."
    )

    mostrar_alineacion(mi_equipo)

    st.divider()

    # ESTE BOTÓN ESTÁ DEBAJO DE LA ALINEACIÓN.
    if not yo.get("listo", False):
        if st.button(
            "✅ ESTOY LISTO",
            use_container_width=True,
        ):
            ok, mensaje = marcar_listo(codigo, player_id, True)
            if not ok:
                st.error(mensaje)
            else:
                st.rerun()
    else:
        st.success("✅ Ya estás marcado como LISTO.")

    st.metric("💰 VALOR DE PLANTILLA", dinero(valor_equipo(mi_equipo)))

# ============================================================
# PARTIDA / RESULTADOS
# ============================================================

if estado in ("jugando", "resultado", "final"):
    st.divider()
    st.header("🏟️ PARTIDA")

    jornada = int(sala.get("jornada_actual", 0))
    st.subheader(f"Jornada {jornada} / 7")

    torneo = obtener_torneo(codigo)
    resultados = (torneo or {}).get("resultados") or []

    if jornada > 0 and len(resultados) >= jornada:
        resultados_jornada = resultados[jornada - 1]

        for resultado in resultados_jornada:
            st.write(
                f"**{resultado['equipo_a']} "
                f"{resultado['goles_a']} - {resultado['goles_b']} "
                f"{resultado['equipo_b']}**"
            )

        puntos_jornada, detalles = puntos_de_jornada(
            resultados_jornada,
            mi_equipo,
        )

        total_jornada = sum(puntos_jornada.values())

        st.markdown(
            f'<div class="box"><div class="small">PUNTOS DE LA JORNADA</div>'
            f'<div class="big">⭐ {total_jornada:.2f}</div></div>',
            unsafe_allow_html=True,
        )

        st.subheader("📊 Desglose de tus jugadores")

        for pid in sorted(
            mi_equipo,
            key=lambda x: puntos_jornada.get(x, 0),
            reverse=True,
        ):
            jugador = jugadores[pid]
            puntos = puntos_jornada.get(pid, 0)

            with st.expander(
                f"{jugador['nombre']} · ⭐ {puntos:.2f}"
            ):
                detalle = detalles.get(pid, {})
                if detalle:
                    for concepto, valor in detalle.items():
                        st.write(f"{concepto}: **{valor:+.2f}**")
                else:
                    st.write("Sin puntos en esta jornada.")

    # Clasificación de la sala.
    st.divider()
    st.header("🏆 CLASIFICACIÓN")

    sala_actual = obtener_sala(codigo) or sala
    ranking = sorted(
        (sala_actual.get("jugadores") or {}).items(),
        key=lambda x: float(x[1].get("puntos_totales", 0)),
        reverse=True,
    )

    for i, (_, jugador) in enumerate(ranking, 1):
        marca = " 👈 TÚ" if _ == player_id else ""
        st.write(
            f"**{i}. {jugador.get('nombre','')}** — "
            f"⭐ {float(jugador.get('puntos_totales',0)):.2f}{marca}"
        )

# ============================================================
# SALIR
# ============================================================

st.divider()
if st.button("🚪 SALIR"):
    limpiar_sesion()
    st.rerun()