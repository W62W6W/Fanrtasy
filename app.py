import streamlit as st

from simulador import simular_partido
from fantasy import calcular_fantasy
from datos import jugadores


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="World Cup Fantasy",
    page_icon="⚽",
    layout="wide",
)

# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #050505;
        color: white;
    }

    [data-testid="stSidebar"] {
        background: #080808;
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }

    div[data-baseweb="select"] > div {
        background: #111111 !important;
        color: white !important;
        border: 1px solid #333333 !important;
    }

    div[data-baseweb="select"] span {
        color: white !important;
    }

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

    .player-card {
        background: linear-gradient(145deg, #171717, #090909);
        border: 1px solid #292929;
        border-radius: 14px;
        padding: 14px;
        margin: 0 0 6px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,.45);
    }

    .player-name {
        font-size: 18px;
        font-weight: 700;
        color: white;
    }

    .player-position {
        color: #aaa;
        font-size: 13px;
        margin-top: 4px;
    }

    .player-price {
        color: white;
        font-size: 16px;
        font-weight: 700;
        margin-top: 7px;
    }

    .slot {
        background: #101010;
        border: 1px dashed #444;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        text-align: center;
    }

    .slot-filled {
        background: #171717;
        border: 1px solid #444;
    }

    .money-box, .points-box {
        background: linear-gradient(135deg, #171717, #090909);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 18px;
        text-align: center;
    }

    .money-title {
        color: #999;
        font-size: 13px;
        letter-spacing: 1px;
    }

    .money-value {
        color: white;
        font-size: 30px;
        font-weight: 700;
        margin-top: 5px;
    }

    .points-value {
        color: white;
        font-size: 42px;
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background: #101010;
        border: 1px solid #292929;
        border-radius: 12px;
        padding: 10px;
    }

    [data-testid="stMetricLabel"] {
        color: #aaa !important;
    }

    [data-testid="stMetricValue"] {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNCIONES
# ============================================================

def formatear_dinero(valor):
    """25_000_000 -> 25M; 22_500_000 -> 22.5M."""
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return "0"

    if valor >= 1_000_000:
        millones = valor / 1_000_000
        if millones.is_integer():
            return f"{int(millones)}M"
        return f"{millones:.1f}M"

    if valor >= 1_000:
        miles = valor / 1_000
        if miles.is_integer():
            return f"{int(miles)}K"
        return f"{miles:.1f}K"

    return f"{int(valor)}"


def calcular_presupuesto_inicial():
    """Presupuesto = mediana del valor de todos los jugadores × 11."""
    precios = []

    for jugador in jugadores.values():
        try:
            precio = float(jugador.get("precio", 0))
        except (TypeError, ValueError):
            continue

        if precio > 0:
            precios.append(precio)

    if not precios:
        return 660_000_000

    precios.sort()
    n = len(precios)

    if n % 2:
        mediana = precios[n // 2]
    else:
        mediana = (precios[n // 2 - 1] + precios[n // 2]) / 2

    presupuesto = mediana * 11

    # Redondeo a millones.
    return int(round(presupuesto / 1_000_000) * 1_000_000)


PRESUPUESTO_INICIAL = calcular_presupuesto_inicial()


def nombre_posicion(posicion):
    return {
        "POR": "Portero",
        "DEF": "Defensa",
        "MED": "Mediocampista",
        "DEL": "Delantero",
    }.get(posicion, posicion)


def contar_posiciones(equipo):
    posiciones = {"POR": 0, "DEF": 0, "MED": 0, "DEL": 0}

    for id_jugador in equipo:
        jugador = jugadores.get(id_jugador)
        if not jugador:
            continue

        posicion = jugador.get("posicion")
        if posicion in posiciones:
            posiciones[posicion] += 1

    return posiciones


def plantilla_completa(equipo):
    p = contar_posiciones(equipo)
    return (
        p["POR"] == 1
        and p["DEF"] == 4
        and p["MED"] == 3
        and p["DEL"] == 3
    )


def tarjeta_jugador(jugador, capitán=False):
    estrella = " ⭐" if capitán else ""

    # Importante: NO dejar el HTML indentado dentro del markdown.
    html = f"""
<div class="player-card">
<div class="player-name">{jugador["nombre"]}{estrella}</div>
<div class="player-position">{jugador["equipo"]} · {nombre_posicion(jugador["posicion"])}</div>
<div class="player-price">💰 {formatear_dinero(jugador.get("precio", 0))}</div>
</div>
"""
    st.markdown(html.strip(), unsafe_allow_html=True)


def tarjeta_slot(jugador=None, posicion=""):
    if jugador is None:
        nombres = {
            "POR": "🧤 Portero vacío",
            "DEF": "🛡️ Defensa vacío",
            "MED": "⚙️ Mediocampista vacío",
            "DEL": "⚽ Delantero vacío",
        }
        st.markdown(
            f'<div class="slot">{nombres.get(posicion, "Posición vacía")}</div>',
            unsafe_allow_html=True,
        )
        return

    capitan = (
        st.session_state.capitan == next(
            (id_ for id_, j in jugadores.items() if j is jugador),
            None,
        )
    )

    estrella = " ⭐ CAPITÁN" if capitan else ""

    html = f"""
<div class="slot slot-filled">
<div class="player-name">{jugador["nombre"]}{estrella}</div>
<div class="player-position">{jugador["equipo"]} · {posicion}</div>
<div class="player-price">💰 {formatear_dinero(jugador.get("precio", 0))}</div>
</div>
"""
    st.markdown(html.strip(), unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "mi_equipo" not in st.session_state:
    st.session_state.mi_equipo = []

if "presupuesto" not in st.session_state:
    st.session_state.presupuesto = PRESUPUESTO_INICIAL

if "capitan" not in st.session_state:
    st.session_state.capitan = None

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "fantasy" not in st.session_state:
    st.session_state.fantasy = None

if "puntos_finales" not in st.session_state:
    st.session_state.puntos_finales = None

if "detalles" not in st.session_state:
    st.session_state.detalles = []


# ============================================================
# CABECERA
# ============================================================

st.title("⚽ WORLD CUP FANTASY")
st.write("Construye tu equipo con jugadores de 🇫🇷 Francia y 🇪🇸 España.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
<div class="money-box">
<div class="money-title">PRESUPUESTO DISPONIBLE</div>
<div class="money-value">💰 {formatear_dinero(st.session_state.presupuesto)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
<div class="money-box">
<div class="money-title">JUGADORES</div>
<div class="money-value">👥 {len(st.session_state.mi_equipo)} / 11</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
<div class="money-box">
<div class="money-title">FORMACIÓN</div>
<div class="money-value">4 - 3 - 3</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()


# ============================================================
# DOS COLUMNAS: EQUIPO + MERCADO
# ============================================================

col_plantilla, col_mercado = st.columns([0.95, 1.5])


# ============================================================
# TU EQUIPO
# ============================================================

with col_plantilla:
    st.header("👕 TU EQUIPO")

    equipo = st.session_state.mi_equipo

    posiciones = {"POR": [], "DEF": [], "MED": [], "DEL": []}

    for id_jugador in equipo:
        jugador = jugadores[id_jugador]
        posiciones[jugador["posicion"]].append(id_jugador)

    st.subheader("🧤 PORTERO")
    if posiciones["POR"]:
        tarjeta_slot(jugadores[posiciones["POR"][0]], "POR")
    else:
        tarjeta_slot(posicion="POR")

    st.subheader("🛡️ DEFENSAS")
    for i in range(4):
        if i < len(posiciones["DEF"]):
            tarjeta_slot(jugadores[posiciones["DEF"][i]], "DEF")
        else:
            tarjeta_slot(posicion="DEF")

    st.subheader("⚙️ MEDIOCAMPISTAS")
    for i in range(3):
        if i < len(posiciones["MED"]):
            tarjeta_slot(jugadores[posiciones["MED"][i]], "MED")
        else:
            tarjeta_slot(posicion="MED")

    st.subheader("⚽ DELANTEROS")
    for i in range(3):
        if i < len(posiciones["DEL"]):
            tarjeta_slot(jugadores[posiciones["DEL"][i]], "DEL")
        else:
            tarjeta_slot(posicion="DEL")

    if equipo:
        st.write("")
        nombres = [jugadores[i]["nombre"] for i in equipo]
        mapa = {jugadores[i]["nombre"]: i for i in equipo}

        actual = 0
        if st.session_state.capitan in equipo:
            nombre_actual = jugadores[st.session_state.capitan]["nombre"]
            if nombre_actual in nombres:
                actual = nombres.index(nombre_actual)

        seleccionado = st.selectbox(
            "⭐ Elige tu capitán",
            nombres,
            index=actual,
        )
        st.session_state.capitan = mapa[seleccionado]


# ============================================================
# MERCADO
# ============================================================

with col_mercado:
    st.header("🛒 MERCADO")
    st.write("Elige jugadores de Francia y España para completar tu 4-3-3.")

    filtro = st.selectbox(
        "Filtrar por posición",
        ["Todos", "POR", "DEF", "MED", "DEL"],
    )

    filtro_equipo = st.selectbox(
        "Filtrar por selección",
        ["Todos", "Francia", "España"],
    )

    limites = {"POR": 1, "DEF": 4, "MED": 3, "DEL": 3}

    posiciones_actuales = contar_posiciones(st.session_state.mi_equipo)

    for id_jugador, jugador in jugadores.items():

        if id_jugador in st.session_state.mi_equipo:
            continue

        posicion = jugador.get("posicion")

        if filtro != "Todos" and posicion != filtro:
            continue

        if filtro_equipo != "Todos" and jugador.get("equipo") != filtro_equipo:
            continue

        try:
            precio = float(jugador.get("precio", 0))
        except (TypeError, ValueError):
            precio = 0

        puede_posicion = posiciones_actuales.get(posicion, 0) < limites.get(posicion, 0)
        puede_comprar = precio <= st.session_state.presupuesto
        plantilla_llena = len(st.session_state.mi_equipo) >= 11

        tarjeta_jugador(jugador)

        if plantilla_llena:
            st.button(
                "PLANTILLA COMPLETA",
                key=f"full_{id_jugador}",
                disabled=True,
                use_container_width=True,
            )
        elif not puede_posicion:
            st.button(
                f"LÍMITE DE {posicion}",
                key=f"limit_{id_jugador}",
                disabled=True,
                use_container_width=True,
            )
        elif not puede_comprar:
            st.button(
                "💰 PRESUPUESTO INSUFICIENTE",
                key=f"money_{id_jugador}",
                disabled=True,
                use_container_width=True,
            )
        else:
            if st.button(
                "➕ COMPRAR",
                key=f"buy_{id_jugador}",
                use_container_width=True,
            ):
                st.session_state.mi_equipo.append(id_jugador)
                st.session_state.presupuesto -= precio
                st.rerun()


# ============================================================
# RESUMEN
# ============================================================

st.divider()
st.header("📋 RESUMEN")

posiciones = contar_posiciones(st.session_state.mi_equipo)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("🧤 POR", f"{posiciones['POR']} / 1")
with c2:
    st.metric("🛡️ DEF", f"{posiciones['DEF']} / 4")
with c3:
    st.metric("⚙️ MED", f"{posiciones['MED']} / 3")
with c4:
    st.metric("⚽ DEL", f"{posiciones['DEL']} / 3")
with c5:
    st.metric("👥 TOTAL", f"{len(st.session_state.mi_equipo)} / 11")


valor_plantilla = sum(
    float(jugadores[i].get("precio", 0))
    for i in st.session_state.mi_equipo
)

st.markdown(
    f"""
<div class="money-box">
<div class="money-title">VALOR DE TU PLANTILLA</div>
<div class="money-value">💰 {formatear_dinero(valor_plantilla)}</div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# BOTONES
# ============================================================

st.divider()

c1, c2 = st.columns(2)

with c1:
    if st.button("🔄 REINICIAR EQUIPO", use_container_width=True):
        st.session_state.mi_equipo = []
        st.session_state.presupuesto = PRESUPUESTO_INICIAL
        st.session_state.capitan = None
        st.session_state.resultado = None
        st.session_state.fantasy = None
        st.session_state.puntos_finales = None
        st.session_state.detalles = []
        st.rerun()

with c2:
    puede_simular = plantilla_completa(st.session_state.mi_equipo)

    if st.button(
        "⚽ SIMULAR FRANCIA 🇫🇷 VS ESPAÑA 🇪🇸",
        disabled=not puede_simular,
        use_container_width=True,
    ):
        resultado = simular_partido("Francia", "España")
        fantasy = calcular_fantasy(resultado)

        puntos = 0
        detalles = []

        for id_jugador in st.session_state.mi_equipo:
            puntos_jugador = fantasy.get(id_jugador, 0)

            if id_jugador == st.session_state.capitan:
                puntos_jugador *= 2

            puntos += puntos_jugador

            detalles.append({
                "id": id_jugador,
                "puntos": round(puntos_jugador, 2),
            })

        st.session_state.resultado = resultado
        st.session_state.fantasy = fantasy
        st.session_state.puntos_finales = round(puntos, 2)
        st.session_state.detalles = detalles
        st.rerun()


# ============================================================
# RESULTADO
# ============================================================

if st.session_state.resultado is not None:
    resultado = st.session_state.resultado

    st.divider()
    st.header("🏟️ RESULTADO DEL PARTIDO")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(f"🇫🇷 {resultado['equipo_a']}")

    with c2:
        st.markdown(f"# {resultado['goles_a']} - {resultado['goles_b']}")

    with c3:
        st.subheader(f"🇪🇸 {resultado['equipo_b']}")


# ============================================================
# PUNTUACIÓN
# ============================================================

if st.session_state.puntos_finales is not None:
    st.divider()
    st.header("🏆 TU PUNTUACIÓN")

    st.markdown(
        f"""
<div class="points-box">
<div class="money-title">PUNTOS FANTASY</div>
<div class="points-value">⭐ {st.session_state.puntos_finales}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# DETALLE DE PUNTOS
# ============================================================

if st.session_state.detalles:
    st.divider()
    st.header("📊 PUNTOS DE TU EQUIPO")

    detalles = sorted(
        st.session_state.detalles,
        key=lambda x: x["puntos"],
        reverse=True,
    )

    for detalle in detalles:
        jugador = jugadores[detalle["id"]]

        tarjeta = f"""
<div class="player-card">
<div class="player-name">{jugador["nombre"]}</div>
<div class="player-position">{jugador["equipo"]} · {jugador["posicion"]}</div>
<div class="player-position">💰 {formatear_dinero(jugador.get("precio", 0))}</div>
<div class="player-price">⭐ {detalle["puntos"]} puntos</div>
</div>
"""
        st.markdown(tarjeta.strip(), unsafe_allow_html=True)
