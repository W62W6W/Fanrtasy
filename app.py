import streamlit as st
from streamlit_autorefresh import st_autorefresh
from firebase import (
    obtener_sala,
    unirse_sala,
    guardar_equipo,
    guardar_cambio_equipo,
    marcar_listo,
    obtener_torneo,
)
from datos import jugadores
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
NOMBRES_POSICION = {"POR": "Portero", "DEF": "Defensa", "MED": "Mediocampista", "DEL": "Delantero"}

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
                {jugador.get('equipo','')} · {NOMBRES_POSICION.get(jugador.get('posicion',''), jugador.get('posicion',''))}
            </div>
            <div class="player-info">⚔️ Ataque: {jugador.get('ataque', jugador.get('atk', '—'))} · 🛡️ Defensa: {jugador.get('defensa', jugador.get('def', '—'))}</div>
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
                    f'<span style="color:#aaa">{j["equipo"]} · {NOMBRES_POSICION.get(j["posicion"], j["posicion"])} · '
                    f'{dinero(j.get("precio",0))}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="slot">{NOMBRES_POSICION.get(pos, pos)} vacío</div>',
                    unsafe_allow_html=True,
                )


def limpiar_sesion():
    for clave in [
        "rol", "codigo_sala", "player_id", "nombre_usuario",
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

# ============================================================
# ACTUALIZACIÓN AUTOMÁTICA MULTIJUGADOR
# ============================================================
# Mientras un usuario está dentro de una sala, la pantalla se
# actualiza cada 3 segundos para detectar nuevos jugadores,
# cambios del administrador, jugadores listos y resultados.
if st.session_state.get("rol") == "player":
    st_autorefresh(
        interval=3000,
        limit=None,
        key="fantasy_sala_autorefresh",
    )

# ============================================================
# PANTALLA INICIAL — SOLO JUGADORES
# ============================================================

if not st.session_state.rol:
    st.title("⚽ WORLD CUP FANTASY")
    st.subheader("Multijugador")

    st.markdown(
        '<div class="box"><div class="big">👤 Unirse a sala</div>'
        '<div class="small">Entra con el código que te dé el administrador.</div></div>',
        unsafe_allow_html=True,
    )

    codigo_inicio = st.text_input(
        "Código de sala",
        max_chars=6,
        key="codigo_inicio",
    ).strip().upper()
    nombre_inicio = st.text_input(
        "Tu nombre",
        key="nombre_inicio",
    )

    if st.button("UNIRME A LA SALA", use_container_width=True):
        if not codigo_inicio or not nombre_inicio.strip():
            st.error("Escribe el código y tu nombre.")
        else:
            ok, mensaje, player_id = unirse_sala(
                codigo_inicio,
                nombre_inicio.strip(),
            )
            if ok:
                st.session_state.rol = "player"
                st.session_state.codigo_sala = codigo_inicio
                st.session_state.player_id = player_id
                st.session_state.nombre_usuario = nombre_inicio.strip()
                st.rerun()
            else:
                st.error(mensaje or "No se pudo entrar.")

    st.divider()
    st.caption("🎮 Página de jugadores · El administrador controla la partida.")
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
                f"Necesitas 1 Portero, 4 Defensas, 3 Mediocampistas y 3 Delanteros. "
                f"Actualmente: {p['POR']} Portero · {p['DEF']} Defensa · "
                f"{p['MED']} Mediocampista · {p['DEL']} Delantero."
            )

    # ---------------- MERCADO ----------------
    with col_mercado:
        st.header("🛒 MERCADO")

        filtro_pos = st.selectbox(
            "Posición",
            ["Todos", "Portero", "Defensa", "Mediocampista", "Delantero"],
        )
        filtro_pos_map = {
            "Todos": "Todos",
            "Portero": "POR",
            "Defensa": "DEF",
            "Mediocampista": "MED",
            "Delantero": "DEL",
        }
        filtro_pos_codigo = filtro_pos_map[filtro_pos]

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

            if filtro_pos_codigo != "Todos" and pos != filtro_pos_codigo:
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
                    f"LÍMITE DE {NOMBRES_POSICION.get(pos, pos)}",
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
                    nuevo_equipo = list(mi_equipo)
                    nuevo_equipo.append(pid)

                    nuevo_valor = valor_equipo(nuevo_equipo)
                    nuevo_restante = PRESUPUESTO - nuevo_valor

                    ok, mensaje = guardar_equipo(
                        codigo,
                        player_id,
                        nuevo_equipo,
                        nuevo_restante,
                    )

                    if not ok:
                        st.error(mensaje)
                    else:
                        st.rerun()


# ============================================================
# QUITAR JUGADORES DURANTE LA SELECCIÓN
# ============================================================

# Mientras la selección está abierta y la plantilla aún no se ha
# guardado definitivamente, el jugador puede quitar fichajes.
# Al quitarlo, el presupuesto disponible aumenta automáticamente
# porque se vuelve a calcular sobre los 540M.
if seleccion_abierta and not ya_seleccionado and mi_equipo:
    st.divider()
    st.subheader("🗑️ QUITAR JUGADORES")

    st.caption(
        "Puedes quitar un jugador que hayas comprado. "
        "El dinero vuelve automáticamente a tu presupuesto."
    )

    for pid in list(mi_equipo):
        jugador_quitar = jugadores[pid]
        col_info, col_quitar = st.columns([4, 1])

        with col_info:
            st.write(
                f"**{jugador_quitar['nombre']}** · "
                f"{NOMBRES_POSICION.get(jugador_quitar.get('posicion',''), jugador_quitar.get('posicion',''))} · "
                f"💰 {dinero(jugador_quitar.get('precio', 0))}"
            )

        with col_quitar:
            if st.button(
                "🗑️ QUITAR",
                key=f"quitar_jugador_{pid}",
                use_container_width=True,
            ):
                nuevo_equipo = [x for x in mi_equipo if x != pid]
                nuevo_valor = valor_equipo(nuevo_equipo)
                nuevo_restante = PRESUPUESTO - nuevo_valor

                ok, mensaje = guardar_equipo(
                    codigo,
                    player_id,
                    nuevo_equipo,
                    nuevo_restante,
                )

                if not ok:
                    st.error(mensaje)
                else:
                    st.success(
                        f"Se ha quitado a {jugador_quitar['nombre']}. "
                        f"Has recuperado {dinero(jugador_quitar.get('precio', 0))}."
                    )
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
# CAMBIOS DESPUÉS DE CADA JORNADA
# ============================================================

if estado == "resultado" and len(mi_equipo) == 11:
    st.divider()
    st.header("🔄 CAMBIOS DE PLANTILLA")

    cambios_usados = int(yo.get("cambios_jornada", 0))
    cambios_restantes = max(0, 3 - cambios_usados)

    st.info(
        f"Puedes hacer hasta **3 cambios** después de esta jornada. "
        f"Te quedan **{cambios_restantes}**."
    )

    if cambios_restantes > 0:
        col_vender, col_comprar = st.columns(2)

        with col_vender:
            pid_venta = st.selectbox(
                "🔴 VENDER JUGADOR",
                mi_equipo,
                format_func=lambda pid: (
                    f"{jugadores[pid]['nombre']} · "
                    f"{NOMBRES_POSICION.get(jugadores[pid].get('posicion',''), jugadores[pid].get('posicion',''))} · "
                    f"{dinero(jugadores[pid].get('precio', 0))}"
                ),
                key=f"venta_jornada_{jornada_actual}_{cambios_usados}",
            )

        posicion_venta = jugadores[pid_venta].get("posicion")

        candidatos = [
            pid for pid, jugador in jugadores.items()
            if pid not in mi_equipo
            and jugador.get("posicion") == posicion_venta
        ]

        with col_comprar:
            if candidatos:
                pid_compra = st.selectbox(
                    "🟢 COMPRAR JUGADOR",
                    candidatos,
                    format_func=lambda pid: (
                        f"{jugadores[pid]['nombre']} · "
                        f"{NOMBRES_POSICION.get(jugadores[pid].get('posicion',''), jugadores[pid].get('posicion',''))} · "
                        f"{dinero(jugadores[pid].get('precio', 0))}"
                    ),
                    key=f"compra_jornada_{jornada_actual}_{cambios_usados}",
                )
            else:
                pid_compra = None
                st.warning("No hay sustitutos disponibles para esa posición.")

        if pid_compra:
            equipo_nuevo = list(mi_equipo)
            equipo_nuevo.remove(pid_venta)
            equipo_nuevo.append(pid_compra)

            valor_nuevo = valor_equipo(equipo_nuevo)
            presupuesto_nuevo = PRESUPUESTO - valor_nuevo

            st.metric(
                "💰 PRESUPUESTO DESPUÉS DEL CAMBIO",
                dinero(presupuesto_nuevo),
            )

            if presupuesto_nuevo < 0:
                st.error("No puedes superar los 540M de presupuesto.")
            elif st.button(
                "🔄 CONFIRMAR CAMBIO",
                key=f"confirmar_cambio_{jornada_actual}_{cambios_usados}",
                use_container_width=True,
            ):
                ok, mensaje = guardar_cambio_equipo(
                    codigo,
                    player_id,
                    equipo_nuevo,
                    presupuesto_nuevo,
                )
                if not ok:
                    st.error(mensaje)
                else:
                    st.success("✅ Cambio realizado correctamente.")
                    st.rerun()
    else:
        st.success("✅ Ya has utilizado los 3 cambios disponibles en esta jornada.")

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