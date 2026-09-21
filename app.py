import streamlit as st
import time
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

PRESUPUESTO = 615_000_000
MAX_JUGADORES = 30
FORMACION = {"POR": 1, "DEF": 4, "MED": 3, "DEL": 3}
NOMBRES_POSICION = {"POR": "Portero", "DEF": "Defensa", "MED": "Mediocampista", "DEL": "Delantero"}

# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .stApp {background:radial-gradient(circle at 20% 0%,rgba(37,99,235,.18),transparent 30%),linear-gradient(180deg,#061226 0%,#08172f 52%,#0b1b38 100%);color:#fff}
    [data-testid="stHeader"]{background:rgba(0,0,0,0)}
    [data-testid="stSidebar"]{background:#07152c;border-right:1px solid #244c91}
    h1,h2,h3,h4,h5,h6,p,label,span{color:#fff!important}

    /* Campos del jugador: etiquetas y valores en negro para que se lean bien */
    .stTextInput label, .stSelectbox label, .stMultiSelect label,
    .stNumberInput label, .stSlider label {
        color:#111827!important;
        font-weight:800!important;
    }
    .stTextInput input {
        color:#111827!important;
        background:#ffffff!important;
        border:1px solid #7aa2e8!important;
    }
    .stTextInput input::placeholder {
        color:#374151!important;
        opacity:1!important;
    }
    div[data-baseweb="select"]>div {
        background:#ffffff!important;
        color:#111827!important;
        border:1px solid #7aa2e8!important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        color:#111827!important;
    }
    /* Menú desplegable abierto */
    [role="listbox"], [role="option"],
    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {
        background:#ffffff!important;
        color:#111827!important;
    }
    [role="option"] * {
        color:#111827!important;
    }
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] * {
        color:#111827!important;
    }
    .hero{background:linear-gradient(135deg,#0b2d69,#153b88 55%,#312e81);border:1px solid #4f7cff;border-radius:18px;padding:18px 22px;margin-bottom:16px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
    .hero-title{font-size:30px;font-weight:900}.hero-sub{color:#bfdbfe;font-size:14px}
    .panel,.player-card{background:linear-gradient(145deg,#122957,#0b1835);border:1px solid #315ca8;border-radius:14px;padding:12px;margin-bottom:7px}
    .section-title{font-size:18px;font-weight:850;color:#dbeafe;margin:2px 0 10px}
    .market-head{display:grid;grid-template-columns:58px 1.8fr 1fr 90px;gap:10px;color:#93c5fd;font-size:12px;font-weight:800;padding:6px 12px 8px;text-transform:uppercase}
    .market-row{display:grid;grid-template-columns:58px 1.8fr 1fr 90px;gap:10px;align-items:center;background:linear-gradient(145deg,#102b59,#0b1d3b);border:1px solid #244a83;border-radius:12px;padding:8px 10px;margin-bottom:7px}
    .market-name{font-weight:800;font-size:14px}.market-team{color:#bfdbfe;font-size:12px}.market-price{font-weight:900;color:#e0e7ff;font-size:15px}
    .shirt-wrap{display:flex;justify-content:center;align-items:center}.shirt{width:48px;height:54px;filter:drop-shadow(0 4px 5px rgba(0,0,0,.28))}.mini-shirt{width:40px;height:45px}
    .lineup-panel{background:linear-gradient(145deg,#0d2349,#08162e);border:1px solid #2e5ca6;border-radius:16px;padding:14px;box-shadow:0 8px 24px rgba(0,0,0,.22)}
    .lineup-title{font-size:20px;font-weight:900}.formation{color:#93c5fd;font-size:12px;font-weight:800;margin-bottom:12px}
    .position-title{color:#bfdbfe;font-size:12px;font-weight:900;margin:10px 0 6px;text-transform:uppercase}
    .slot{background:#0d2345;border:1px dashed #4167a7;border-radius:11px;padding:6px;margin-bottom:6px;text-align:center;min-height:62px}.slot-filled{border-style:solid;background:linear-gradient(145deg,#15366c,#0d2143)}
    .slot-name{font-size:11px;font-weight:800;line-height:1.1}.slot-team{color:#93c5fd;font-size:9px;margin-top:2px}
    .budget-card{background:linear-gradient(135deg,#0e326d,#182e72);border:1px solid #4f7cff;border-radius:14px;padding:12px;margin-top:10px}
    .tutorial-box{background:linear-gradient(145deg,#eaf2ff,#ffffff);border:1px solid #7aa2e8;border-radius:14px;padding:16px 18px;margin:12px 0;color:#111827!important;box-shadow:0 5px 18px rgba(0,0,0,.12)}
    .tutorial-title{font-size:18px;font-weight:900;color:#111827!important;margin-bottom:9px}
    .tutorial-step{font-size:13px;color:#111827!important;margin:6px 0;line-height:1.35}
    .tutorial-step b{color:#111827!important}
    .slot-points{font-size:12px;font-weight:900;color:#fbbf24!important;margin-top:5px}
    .stats-legend{display:flex;gap:18px;flex-wrap:wrap;background:#eaf2ff;border:1px solid #7aa2e8;border-radius:12px;padding:10px 14px;margin:10px 0 14px;color:#111827!important;font-size:13px}
    .stats-legend span,.stats-legend b{color:#111827!important}
    @media (max-width: 768px){
        .hero-title{font-size:24px}
        .hero-sub{font-size:12px}
        .market-head{grid-template-columns:42px 1.5fr 80px 65px;gap:5px;font-size:9px;padding-left:5px;padding-right:5px}
        .market-row{grid-template-columns:42px 1.5fr 80px 65px;gap:5px;padding:7px 5px}
        .market-name{font-size:12px}
        .market-team{font-size:10px}
        .market-price{font-size:12px}
        .shirt{width:42px;height:48px}
        .mini-shirt{width:34px;height:39px}
        .slot{padding:5px}
        .slot-name{font-size:10px}
        .stats-legend{font-size:12px;gap:8px}
    }
    .selection-toast{background:#d1fae5;border:1px solid #10b981;color:#065f46!important;border-radius:10px;padding:12px 16px;font-weight:800;text-align:center;margin:8px 0 12px;animation:selectionFade 2s forwards;}
    @keyframes selectionFade{0%,85%{opacity:1}100%{opacity:0}}
    .budget-label{color:#bfdbfe;font-size:11px;font-weight:800;text-transform:uppercase}.budget-value{font-size:25px;font-weight:900}
    .filter-card{background:#0b1d3b;border:1px solid #244a83;border-radius:13px;padding:12px}
    .small{color:#93c5fd;font-size:12px}.box{background:linear-gradient(145deg,#12316b,#0a1737);border:1px solid #315ca8;border-radius:15px;padding:18px;margin-bottom:12px}.big{font-size:30px;font-weight:800}
    .stButton>button{background:linear-gradient(135deg,#2563eb,#4f46e5)!important;color:white!important;border:1px solid #6385ff!important;border-radius:9px!important;font-weight:800!important;min-height:40px!important;box-shadow:0 4px 12px rgba(37,99,235,.22)}
    .stButton>button:hover{background:linear-gradient(135deg,#3b82f6,#6366f1)!important;border-color:#bfdbfe!important}
    /* Los controles de entrada permanecen con texto negro */
    input{color:#111827!important}
    /* Filtros: fondo claro y texto negro para que Buscar jugador y Posición se lean bien */
    div[data-testid="column"]:has([data-testid="stTextInput"]) {background:#eaf2ff!important;border:1px solid #7aa2e8!important;border-radius:14px!important;padding:12px!important;}
    div[data-testid="column"]:has([data-testid="stTextInput"]) label {color:#111827!important;font-weight:800!important;}
    div[data-testid="column"]:has([data-testid="stTextInput"]) input {background:#ffffff!important;color:#111827!important;border:1px solid #7aa2e8!important;}
    div[data-testid="column"]:has([data-testid="stTextInput"]) input::placeholder {color:#111827!important;opacity:1!important;}
    div[data-testid="column"]:has([data-testid="stTextInput"]) [data-baseweb="select"]>div {background:#ffffff!important;color:#111827!important;border:1px solid #7aa2e8!important;}
    div[data-testid="column"]:has([data-testid="stTextInput"]) [data-baseweb="select"] span {color:#111827!important;}
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
        return "€ 0"

    signo = "-" if valor < 0 else ""
    valor = abs(valor)

    if valor >= 1_000_000:
        n = valor / 1_000_000
        texto = f"€ {int(n)}M" if n.is_integer() else f"€ {n:.1f}M"
        return signo + texto

    if valor >= 1_000:
        n = valor / 1_000
        texto = f"€ {int(n)}K" if n.is_integer() else f"€ {n:.1f}K"
        return signo + texto

    return signo + f"€ {int(valor)}"


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


def camiseta_svg(equipo, mini=False):
    colores = {
        "Francia": ("#173b9b","#ffffff","#e63946"),
        "España": ("#d90429","#ffcc00","#aa001c"),
        "Argentina": ("#75bde8","#ffffff","#75bde8"),
        "Bélgica": ("#111111","#f1c40f","#d90429"),
        "Inglaterra": ("#ffffff","#173b9b","#d90429"),
        "Noruega": ("#d90429","#173b9b","#ffffff"),
        "Marruecos": ("#c1121f","#006233","#ffffff"),
        "Suiza": ("#d90429","#ffffff","#d90429"),
    }
    c1,c2,c3 = colores.get(equipo,("#2563eb","#ffffff","#4f46e5"))
    cls = "mini-shirt" if mini else "shirt"
    return (
        f'<svg class="{cls}" viewBox="0 0 80 90" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="M23 10L7 21L15 39L25 33L25 78Q40 85 55 78L55 33L65 39L73 21L57 10Q50 17 40 17Q30 17 23 10Z" fill="{c1}" stroke="#dbeafe" stroke-width="2"/>'
        f'<path d="M25 33L25 78Q40 85 55 78L55 33L50 35L50 75Q40 79 30 75L30 35Z" fill="{c2}" opacity=".88"/>'
        f'<path d="M31 16Q40 22 49 16L47 26Q40 30 33 26Z" fill="{c3}"/>'
        f'<path d="M7 21L15 39L22 35L14 19Z" fill="{c3}"/><path d="M73 21L65 39L58 35L66 19Z" fill="{c3}"/>'
        f'</svg>'
    )

def jugador_html(jugador):
    st.markdown(
        f'<div class="market-row"><div class="shirt-wrap">{camiseta_svg(jugador.get("equipo",""),True)}</div>'
        f'<div><div class="market-name">{jugador.get("nombre","")}</div>'
        f'<div class="market-team">{jugador.get("equipo","")} · {NOMBRES_POSICION.get(jugador.get("posicion",""),jugador.get("posicion",""))}</div></div>'
        f'<div class="market-team">⚔️ {jugador.get("ataque",jugador.get("atk","—"))} &nbsp; 🛡️ {jugador.get("defensa",jugador.get("def","—"))}</div>'
        f'<div class="market-price">💰 {dinero(jugador.get("precio",0))}</div></div>',
        unsafe_allow_html=True,
    )


def mostrar_alineacion(equipo, titulo="TU ALINEACIÓN"):
    st.markdown(f'<div class="lineup-title">👕 {titulo}</div><div class="formation">4 - 3 - 3</div>', unsafe_allow_html=True)
    posiciones={p:[] for p in FORMACION}
    for pid in equipo or []:
        if pid in jugadores:
            posiciones[jugadores[pid]["posicion"]].append(pid)
    nombres={"POR":"🧤 PORTEROS","DEF":"🛡️ DEFENSAS","MED":"⚙️ MEDIOCAMPISTAS","DEL":"⚽ DELANTEROS"}
    for pos in ["POR","DEF","MED","DEL"]:
        st.markdown(f'<div class="position-title">{nombres[pos]} ({len(posiciones[pos])}/{FORMACION[pos]})</div>',unsafe_allow_html=True)
        for i in range(FORMACION[pos]):
            if i < len(posiciones[pos]):
                j=jugadores[posiciones[pos][i]]
                st.markdown(
                    f'<div class="slot slot-filled">{camiseta_svg(j.get("equipo",""),True)}<div class="slot-name">{j["nombre"]}</div><div class="slot-team">{j["equipo"]} · {dinero(j.get("precio",0))}</div></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="slot"><div style="font-size:22px">👕</div><div class="slot-name">{NOMBRES_POSICION.get(pos,pos)} vacío</div></div>',unsafe_allow_html=True)


def mostrar_alineacion_interactiva(equipo, codigo, player_id):
    """Muestra la alineación y permite quitar jugadores desde la propia alineación."""
    st.markdown(
        '<div class="lineup-panel">'
        '<div class="lineup-title">👕 TU ALINEACIÓN</div>'
        '<div class="formation">1 PORTERO · 4 DEFENSAS · 3 MEDIOCAMPISTAS · 3 DELANTEROS</div>'
        '</div>',
        unsafe_allow_html=True,
    )

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
        st.markdown(
            f'<div class="position-title">{nombres[pos]} '
            f'({len(posiciones[pos])}/{FORMACION[pos]})</div>',
            unsafe_allow_html=True,
        )

        ids = posiciones[pos]
        cantidad = max(FORMACION[pos], len(ids))

        for inicio in range(0, cantidad, 4):
            fila = ids[inicio:inicio + 4]
            cols = st.columns(min(4, max(1, len(fila))))

            for col, pid in zip(cols, fila):
                j = jugadores[pid]
                with col:
                    st.markdown(
                        f'<div class="slot slot-filled">'
                        f'{camiseta_svg(j.get("equipo",""), True)}'
                        f'<div class="slot-name">{j["nombre"]}</div>'
                        f'<div class="slot-team">{j["equipo"]} · {dinero(j.get("precio",0))}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "🗑️ QUITAR",
                        key=f"quitar_alineacion_{pid}",
                        use_container_width=True,
                    ):
                        nuevo_equipo = [x for x in equipo if x != pid]
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

        if not ids:
            st.markdown(
                f'<div class="slot"><div style="font-size:22px">👕</div>'
                f'<div class="slot-name">{NOMBRES_POSICION.get(pos,pos)} vacío</div></div>',
                unsafe_allow_html=True,
            )



def mostrar_desglose_alineacion(equipo, puntos, detalles, jornada, guardado=True):
    """Muestra puntos + desglose en la misma estructura visual de la alineación."""
    st.subheader("📊 TUS JUGADORES")
    st.caption(
        "Aquí ves los puntos y el desglose de cada jugador en la misma alineación. "
        "Los puntos históricos permanecen guardados aunque hagas cambios."
    )

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

    etiquetas = {
        "minutos": "Minutos",
        "minutos_jugados": "Minutos",
        "goles": "Goles",
        "asistencias": "Asistencias",
        "asistencia": "Asistencias",
        "tiros_a_puerta": "Tiros a puerta",
        "shots_on_target": "Tiros a puerta",
        "regates": "Regates",
        "dribbles": "Regates",
        "intercepciones": "Intercepciones",
        "duelos_ganados": "Duelos ganados",
        "recuperaciones": "Recuperaciones",
        "despejes": "Despejes",
        "paradas": "Paradas",
        "saves": "Paradas",
        "balones_perdidos": "Balones perdidos",
        "faltas": "Faltas",
        "amarillas": "Tarjetas amarillas",
        "tarjetas_amarillas": "Tarjetas amarillas",
        "rojas": "Tarjetas rojas",
        "tarjetas_rojas": "Tarjetas rojas",
        "portería_a_cero": "Portería a cero",
        "clean_sheet": "Portería a cero",
    }

    orden = list(etiquetas.keys())

    for pos in ["POR", "DEF", "MED", "DEL"]:
        st.markdown(
            f'<div class="position-title">{nombres[pos]} '
            f'({len(posiciones[pos])}/{FORMACION[pos]})</div>',
            unsafe_allow_html=True,
        )

        ids = posiciones[pos]
        for inicio in range(0, len(ids), 4):
            fila = ids[inicio:inicio + 4]
            cols = st.columns(min(4, len(fila)))

            for col, pid in zip(cols, fila):
                jugador = jugadores[pid]
                pts = float((puntos or {}).get(pid, 0.0))
                detalle = (detalles or {}).get(pid, {}) or {}

                with col:
                    st.markdown(
                        f'<div class="slot slot-filled">'
                        f'{camiseta_svg(jugador.get("equipo",""), True)}'
                        f'<div class="slot-name">{jugador["nombre"]}</div>'
                        f'<div class="slot-team">{jugador["equipo"]} · '
                        f'{dinero(jugador.get("precio",0))}</div>'
                        f'<div class="slot-points">⭐ {pts:.2f} PTS</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    with st.expander("📊 VER DESGLOSE", expanded=False):
                        if detalle:
                            claves = []
                            for clave in orden:
                                if clave in detalle and clave not in claves:
                                    claves.append(clave)
                            for clave in detalle:
                                if clave not in claves:
                                    claves.append(clave)

                            for concepto in claves:
                                valor = detalle.get(concepto, 0)
                                try:
                                    valor_num = float(valor)
                                    st.write(
                                        f"**{etiquetas.get(concepto, concepto.replace('_', ' ').title())}:** "
                                        f"{valor_num:+.2f}"
                                    )
                                except (TypeError, ValueError):
                                    st.write(
                                        f"**{etiquetas.get(concepto, concepto.replace('_', ' ').title())}:** "
                                        f"{valor}"
                                    )
                        elif not guardado:
                            st.info(
                                "El desglose de esta jornada todavía no está guardado."
                            )
                        else:
                            st.write("Sin puntos en esta jornada.")


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


def puntos_jugador_en_jornada(resultados_jornada, player_id):
    """Calcula los puntos históricos de un jugador en una jornada.
    Se usa para mostrar a quién comprar y no modifica ningún total del usuario.
    """
    total = 0.0
    for resultado in resultados_jornada or []:
        fantasy = calcular_fantasy(resultado)
        total += float(fantasy.get(player_id, 0) or 0)
    return total


def puntos_guardados_usuario_jornada(sala, player_id, jornada):
    """Devuelve los puntos individuales guardados para una jornada.
    No recalcula jornadas históricas con la plantilla actual.
    """
    datos = sala.get("puntos_jugadores_jornadas") or {}
    jornada_data = datos.get(f"jornada_{jornada}", {}) or {}
    jugador_data = jornada_data.get(player_id, {}) or {}
    return {pid: float(valor) for pid, valor in jugador_data.items()}


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

# Partido cuyas estadísticas están abiertas en la sección de resultados.
# Es independiente de las claves de los widgets de Streamlit.
if "partido_estadisticas_abierto" not in st.session_state:
    st.session_state.partido_estadisticas_abierto = None

# ============================================================
# ACTUALIZACIÓN AUTOMÁTICA MULTIJUGADOR
# ============================================================
# La página del jugador se actualiza cada 3 segundos durante toda la sala.
# Esto permite detectar automáticamente cuando el administrador:
# - abre/cierra la selección
# - inicia la partida
# - simula una jornada
# - publica los resultados
# - cambia el estado de la sala
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
    # El administrador te quitó de la sala.
    # Volvemos directamente a la pantalla inicial para poder entrar de nuevo.
    limpiar_sesion()
    st.rerun()

st.markdown(
    f'<div class="hero"><div class="hero-title">⚽ WORLD CUP FANTASY</div>'
    f'<div class="hero-sub">Hola, <b>{yo.get("nombre","")}</b> · Sala <b>{codigo}</b></div></div>',
    unsafe_allow_html=True,
)

estado = sala.get("estado", "esperando")
seleccion_abierta = bool(sala.get("seleccion_abierta", False))
jornada_actual = int(sala.get("jornada_actual", 0))
mi_equipo = yo.get("equipo") or []
ya_seleccionado = len(mi_equipo) == 11

# ============================================================
# ESPERA
# ============================================================

if estado == "esperando" and not seleccion_abierta:
    st.info("⏳ Esperando a que el administrador abra la selección.")

    st.markdown(
        """
        <div class="tutorial-box">
            <div class="tutorial-title">📖 MINI TUTORIAL</div>
            <div class="tutorial-step"><b>1.</b> Espera a que el administrador abra la selección.</div>
            <div class="tutorial-step"><b>2.</b> Forma tu equipo con <b>1 portero · 4 defensas · 3 mediocampistas · 3 delanteros</b>.</div>
            <div class="tutorial-step"><b>3.</b> Tienes <b>€ 615M</b> para construir tu plantilla.</div>
            <div class="tutorial-step"><b>4.</b> ⚔️ <b>Ataque:</b> indica la capacidad ofensiva del jugador. Cuanto mayor sea el número, mayor es su capacidad de ataque.</div>
            <div class="tutorial-step"><b>5.</b> 🛡️ <b>Defensa:</b> indica la capacidad defensiva del jugador. Cuanto mayor sea el número, mayor es su capacidad de defensa.</div>
            <div class="tutorial-step"><b>6.</b> Pulsa <b>＋ AÑADIR</b> para seleccionar jugadores. Cuando un jugador esté en tu equipo aparecerá como <b>🟢 SELECCIONADO</b>.</div>
            <div class="tutorial-step"><b>7.</b> Usa <b>🗑️ QUITAR</b> para sacar un jugador de tu alineación.</div>
            <div class="tutorial-step"><b>8.</b> Cuando completes el 4-3-3, pulsa <b>✓ GUARDAR ALINEACIÓN</b> y después <b>✅ ESTOY LISTO</b>.</div>
            <div class="tutorial-step"><b>9.</b> Después de cada jornada podrás hacer hasta <b>3 cambios</b>.</div>
            <div class="tutorial-step"><b>10.</b> Los puntos de jornadas anteriores quedan guardados y no cambian con tus fichajes.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("👥 Jugadores conectados")
    for jugador in jugadores_sala.values():
        st.write(f"• {jugador.get('nombre','')}")
    st.stop()

# ============================================================
# SELECCIÓN
# ============================================================

if seleccion_abierta and not ya_seleccionado:
    st.markdown(
        '<div class="hero"><div class="hero-title">👕 SELECCIONAR EQUIPO</div>'
        '<div class="hero-sub">Arma tu 4-3-3 · 1 PORTERO · 4 DEFENSAS · 3 MEDIOCAMPISTAS · 3 DELANTEROS · Presupuesto máximo € 615M</div></div>',
        unsafe_allow_html=True,
    )

    # La alineación queda arriba para que se vea fácilmente tanto en computador
    # como en celular. Los botones para quitar están dentro de la propia alineación.
    mostrar_alineacion_interactiva(mi_equipo, codigo, player_id)

    st.markdown(
        '<div class="stats-legend">'
        '<span>⚔️ <b>ATAQUE</b> = capacidad ofensiva</span>'
        '<span>🛡️ <b>DEFENSA</b> = capacidad defensiva</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_filtros, col_mercado = st.columns([0.95, 2.0], gap="small")

    with col_filtros:
        st.markdown('<div class="section-title">🔎 FILTRAR JUGADORES</div>', unsafe_allow_html=True)
        filtro_busqueda = st.text_input("Buscar jugador", placeholder="Buscar jugador...", key="buscar_jugador")
        filtro_pos = st.selectbox("POSICIÓN", ["Todos","Portero","Defensa","Mediocampista","Delantero"], key="filtro_posicion")
        mapa={"Todos":"Todos","Portero":"POR","Defensa":"DEF","Mediocampista":"MED","Delantero":"DEL"}
        filtro_pos_codigo=mapa[filtro_pos]
        equipos=sorted({j.get("equipo") for j in jugadores.values() if j.get("equipo")})
        filtro_eq=st.selectbox("SELECCIÓN", ["Todos"]+equipos, key="filtro_equipo")
        precios=[float(j.get("precio",0)) for j in jugadores.values()]
        precio_max=max(precios) if precios else PRESUPUESTO
        precio_max_millones = int(max(precios) / 1_000_000) if precios else 615
        filtro_precio=st.select_slider(
            "PRECIO MÁXIMO",
            options=list(range(0, precio_max_millones + 1)),
            value=precio_max_millones,
            format_func=lambda millones: dinero(float(millones) * 1_000_000),
            key="filtro_precio",
        )
        st.markdown(
            f'<div class="filter-card"><div class="small">PRESUPUESTO RESTANTE</div>'
            f'<div style="font-size:24px;font-weight:900">{dinero(PRESUPUESTO-valor_equipo(mi_equipo))}</div></div>',
            unsafe_allow_html=True)

    with col_mercado:
        st.markdown(f'<div class="section-title">JUGADORES DISPONIBLES <span class="small">· {len(jugadores)} jugadores</span></div>',unsafe_allow_html=True)
        st.markdown('<div class="market-head"><div></div><div>JUGADOR</div><div>ESTADÍSTICAS</div><div>PRECIO</div></div>',unsafe_allow_html=True)
        actuales=contar_posiciones(mi_equipo)
        valor_actual=valor_equipo(mi_equipo)
        mostrados=0

        for pid,jugador in jugadores.items():
            pos=jugador.get("posicion"); eq=jugador.get("equipo"); nombre=jugador.get("nombre","")
            esta_seleccionado = pid in mi_equipo
            precio=float(jugador.get("precio",0) or 0)
            if filtro_pos_codigo!="Todos" and pos!=filtro_pos_codigo: continue
            if filtro_eq!="Todos" and eq!=filtro_eq: continue
            if precio>filtro_precio*1_000_000: continue
            if filtro_busqueda and filtro_busqueda.lower() not in nombre.lower(): continue
            mostrados+=1
            jugador_html(jugador)

            if esta_seleccionado:
                st.button(
                    "🟢 SELECCIONADO",
                    key=f"selected_{pid}",
                    disabled=True,
                    use_container_width=True,
                )
                continue

            if actuales.get(pos,0)>=FORMACION.get(pos,0):
                st.button(f"LÍMITE DE {NOMBRES_POSICION.get(pos,pos).upper()}",key=f"lim_{pid}",disabled=True,use_container_width=True)
            elif valor_actual+precio>PRESUPUESTO:
                st.button("💰 PRESUPUESTO INSUFICIENTE",key=f"money_{pid}",disabled=True,use_container_width=True)
            elif len(mi_equipo)>=11:
                st.button("PLANTILLA COMPLETA",key=f"full_{pid}",disabled=True,use_container_width=True)
            elif st.button("＋ AÑADIR",key=f"add_{pid}",use_container_width=True):
                nuevo=list(mi_equipo); nuevo.append(pid)
                nuevo_valor=valor_equipo(nuevo)
                ok,mensaje=guardar_equipo(codigo,player_id,nuevo,PRESUPUESTO-nuevo_valor)
                if not ok:
                    st.error(mensaje)
                else:
                    st.session_state["jugador_seleccionado_mensaje"] = jugador.get("nombre", "Jugador")
                    st.session_state["jugador_seleccionado_hasta"] = time.time() + 2

        if mostrados==0:
            st.info("No hay jugadores que coincidan con los filtros.")

    # Aviso temporal: aparece en verde durante exactamente 2 segundos.
    mensaje_nombre = st.session_state.get("jugador_seleccionado_mensaje")
    mensaje_hasta = st.session_state.get("jugador_seleccionado_hasta", 0)
    if mensaje_nombre and time.time() < mensaje_hasta:
        st.markdown(
            f"""<div class="selection-toast">✅ Jugador seleccionado: {mensaje_nombre}</div>""",
            unsafe_allow_html=True,
        )
    elif mensaje_nombre:
        st.session_state.pop("jugador_seleccionado_mensaje", None)
        st.session_state.pop("jugador_seleccionado_hasta", None)

    # Presupuesto y guardado quedan debajo de la selección, sin crear una
    # segunda lista de jugadores.
    valor=valor_equipo(mi_equipo)
    restante=PRESUPUESTO-valor
    posiciones=contar_posiciones(mi_equipo)

    st.markdown(
        f'<div class="budget-card">'
        f'<div class="budget-label">PRESUPUESTO RESTANTE</div>'
        f'<div class="budget-value">{dinero(restante)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"👥 {len(mi_equipo)}/11 · "
        f"1 PORTERO {posiciones['POR']}/1 · "
        f"4 DEFENSAS {posiciones['DEF']}/4 · "
        f"3 MEDIOCAMPISTAS {posiciones['MED']}/3 · "
        f"3 DELANTEROS {posiciones['DEL']}/3"
    )

    puede_guardar=plantilla_completa(mi_equipo) and valor<=PRESUPUESTO
    if st.button(
        "✓ GUARDAR ALINEACIÓN",
        disabled=not puede_guardar,
        use_container_width=True,
        key="guardar_alineacion_principal",
    ):
        ok,mensaje=guardar_equipo(codigo,player_id,mi_equipo,restante)
        if not ok:
            st.error(mensaje)
        else:
            st.rerun()

    if not plantilla_completa(mi_equipo):
        st.caption("Completa: 1 portero · 4 defensas · 3 mediocampistas · 3 delanteros.")

# ============================================================
# ALINEACIÓN YA GUARDADA: BLOQUEADA
# ============================================================

elif ya_seleccionado:
    st.success(
        "✅ Tu alineación está guardada. "
        "Después de cada jornada puedes hacer hasta 3 cambios de jugadores."
    )

    mostrar_alineacion(mi_equipo)

    st.divider()

    # ESTE BOTÓN ESTÁ DEBAJO DE LA ALINEACIÓN.
    if estado != "resultado" and not yo.get("listo", False):
        if st.button(
            "✅ ESTOY LISTO",
            key=f"listo_alineacion_{player_id}",
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
    puntos_actuales = puntos_guardados_usuario_jornada(sala, player_id, jornada_actual)

    # Puntos de TODOS los jugadores de la jornada recién terminada.
    # Esto permite comparar, por ejemplo, a Lamine Yamal con Messi
    # antes de confirmar un cambio, sin alterar los puntos históricos.
    torneo_cambios = obtener_torneo(codigo) or {}
    resultados_cambios = torneo_cambios.get("resultados") or []
    resultados_ultima_jornada = (
        resultados_cambios[jornada_actual - 1]
        if 0 < jornada_actual <= len(resultados_cambios)
        else []
    )

    puntos_ultima_jornada = {
        pid: puntos_jugador_en_jornada(resultados_ultima_jornada, pid)
        for pid in jugadores
    }

    st.info(
        f"Puedes hacer hasta **3 cambios** después de esta jornada. "
        f"Has usado **{cambios_usados}/3**."
    )

    # No es obligatorio hacer cambios: se puede continuar directamente.
    if cambios_restantes > 0:
        col_vender, col_comprar = st.columns(2)

        with col_vender:
            opciones_venta = [""] + list(mi_equipo)
            pid_venta = st.selectbox(
                "🔴 VENDER JUGADOR",
                opciones_venta,
                index=0,
                format_func=lambda pid: (
                    "Selecciona un jugador..." if not pid else
                    f"{jugadores[pid]['nombre']} · "
                    f"{NOMBRES_POSICION.get(jugadores[pid].get('posicion',''), jugadores[pid].get('posicion',''))} · "
                    f"{dinero(jugadores[pid].get('precio', 0))} · "
                    f"⭐ {puntos_actuales.get(pid, 0):.2f}"
                ),
                key=f"venta_jornada_{jornada_actual}_{cambios_usados}",
            )

        pid_compra = ""
        if pid_venta:
            posicion_venta = jugadores[pid_venta].get("posicion")
            candidatos = [
                pid for pid, jugador in jugadores.items()
                if pid not in mi_equipo
                and jugador.get("posicion") == posicion_venta
            ]

            with col_comprar:
                if candidatos:
                    opciones_compra = [""] + candidatos
                    pid_compra = st.selectbox(
                        "🟢 COMPRAR JUGADOR",
                        opciones_compra,
                        index=0,
                        format_func=lambda pid: (
                            "Selecciona un jugador..." if not pid else
                            f"{jugadores[pid]['nombre']} · "
                            f"{NOMBRES_POSICION.get(jugadores[pid].get('posicion',''), jugadores[pid].get('posicion',''))} · "
                            f"{dinero(jugadores[pid].get('precio', 0))} · "
                            f"⭐ {puntos_ultima_jornada.get(pid, 0):.2f}"
                        ),
                        key=f"compra_jornada_{jornada_actual}_{cambios_usados}",
                    )
                else:
                    st.warning("No hay sustitutos disponibles para esa posición.")
        else:
            with col_comprar:
                st.selectbox(
                    "🟢 COMPRAR JUGADOR",
                    [""],
                    index=0,
                    format_func=lambda _: "Primero selecciona a quién vender...",
                    key=f"compra_jornada_{jornada_actual}_{cambios_usados}",
                )

        if pid_venta and pid_compra:
            equipo_nuevo = list(mi_equipo)
            equipo_nuevo.remove(pid_venta)
            equipo_nuevo.append(pid_compra)

            valor_nuevo = valor_equipo(equipo_nuevo)
            presupuesto_nuevo = PRESUPUESTO - valor_nuevo

            st.metric(
                "💰 PRESUPUESTO DESPUÉS DEL CAMBIO",
                dinero(presupuesto_nuevo),
            )

            st.info(
                f"⭐ **{jugadores[pid_compra]['nombre']} hizo "
                f"{puntos_ultima_jornada.get(pid_compra, 0):.2f} puntos "
                f"en la jornada recién terminada.**"
            )

            if presupuesto_nuevo < 0:
                st.error("No puedes superar los € 615M de presupuesto.")
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

    # Puedes pulsar ESTOY LISTO con 0, 1, 2 o 3 cambios.
    st.divider()
    if not yo.get("listo", False):
        if st.button("✅ ESTOY LISTO", key=f"listo_cambios_{jornada_actual}_{player_id}", use_container_width=True):
            ok, mensaje = marcar_listo(codigo, player_id, True)
            if not ok:
                st.error(mensaje)
            else:
                st.rerun()
    else:
        st.success("🟢 Ya estás listo para la siguiente jornada.")

# ============================================================
# ESTADÍSTICAS DEL PARTIDO
# ============================================================

def mostrar_estadisticas_partido(resultado, clave):
    """Muestra goleadores y tarjetas del partido al pulsar el botón."""
    equipo_a = resultado.get("equipo_a", "")
    equipo_b = resultado.get("equipo_b", "")
    stats_a = resultado.get("estadisticas_a") or {}
    stats_b = resultado.get("estadisticas_b") or {}

    eventos = []

    for pid, stats in stats_a.items():
        jugador = jugadores.get(pid, {})
        nombre = jugador.get("nombre", pid)
        goles_penalti = int(stats.get("goles_penalti", 0) or 0)
        for numero_gol in range(int(stats.get("goles", 0) or 0)):
            penal = numero_gol < goles_penalti
            eventos.append(("gol", f"⚽ {nombre}{' (P)' if penal else ''}", equipo_a))
        if int(stats.get("amarillas", 0) or 0):
            eventos.append(("amarilla", f"🟨 {nombre}", equipo_a))
        if int(stats.get("rojas", 0) or 0):
            eventos.append(("roja", f"🟥 {nombre}", equipo_a))

    for pid, stats in stats_b.items():
        jugador = jugadores.get(pid, {})
        nombre = jugador.get("nombre", pid)
        goles_penalti = int(stats.get("goles_penalti", 0) or 0)
        for numero_gol in range(int(stats.get("goles", 0) or 0)):
            penal = numero_gol < goles_penalti
            eventos.append(("gol", f"⚽ {nombre}{' (P)' if penal else ''}", equipo_b))
        if int(stats.get("amarillas", 0) or 0):
            eventos.append(("amarilla", f"🟨 {nombre}", equipo_b))
        if int(stats.get("rojas", 0) or 0):
            eventos.append(("roja", f"🟥 {nombre}", equipo_b))

    if not eventos:
        st.info("No hubo goles ni tarjetas en este partido.")
        return

    for tipo, texto, equipo in eventos:
        st.write(f"{texto} — {equipo}")


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

        for indice_partido, resultado in enumerate(resultados_jornada):
            st.write(
                f"**{resultado['equipo_a']} "
                f"{resultado['goles_a']} - {resultado['goles_b']} "
                f"{resultado['equipo_b']}**"
            )

            clave_partido = f"estadisticas_partido_{jornada}_{indice_partido}"

            # El botón y el estado de apertura deben tener claves distintas.
            # Si se usa la misma clave en session_state y en st.button,
            # Streamlit lanza StreamlitWidgetAlreadyInstantiatedError.
            if st.button(
                "📊 VER ESTADÍSTICAS DEL PARTIDO",
                key=f"ver_stats_{clave_partido}",
                use_container_width=True,
            ):
                if st.session_state.partido_estadisticas_abierto == clave_partido:
                    st.session_state.partido_estadisticas_abierto = None
                else:
                    st.session_state.partido_estadisticas_abierto = clave_partido

            if st.session_state.partido_estadisticas_abierto == clave_partido:
                with st.container(border=True):
                    st.markdown("**📊 ESTADÍSTICAS DEL PARTIDO**")
                    mostrar_estadisticas_partido(resultado, clave_partido)

        # Los puntos de esta jornada se toman de Firebase, donde quedaron
        # guardados en el momento de la simulación. Así un cambio de plantilla
        # posterior NO modifica los puntos que ya ganó el jugador.
        # Firebase guarda los puntos de CADA jugador en el momento de
        # simular la jornada. Los leemos de ahí para que un cambio posterior
        # de plantilla jamás modifique los puntos históricos.
        # Estos datos se guardan en la SALA de Firebase (no dentro del torneo).
        sala_actualizada = obtener_sala(codigo) or sala
        resultados_guardados = sala_actualizada.get("resultados_jornadas") or {}
        puntos_guardados_usuario = resultados_guardados.get(
            f"jornada_{jornada}", {},
        ) or {}

        # El admin guarda los puntos de CADA jugador de CADA usuario.
        # Esto evita que un cambio de plantilla altere jornadas ya jugadas.
        puntos_jugadores_guardados = (
            sala_actualizada.get("puntos_jugadores_jornadas") or {}
        )
        puntos_jornada_por_usuario = puntos_jugadores_guardados.get(
            f"jornada_{jornada}", {},
        ) or {}
        puntos_jornada = puntos_jornada_por_usuario.get(player_id)

        if isinstance(puntos_jornada, dict):
            puntos_jornada = {
                pid: float(puntos_jornada.get(pid, 0))
                for pid in mi_equipo
            }
        else:
            # Compatibilidad con salas antiguas: calcula solo como respaldo.
            calculados, _ = puntos_de_jornada(resultados_jornada, mi_equipo)
            puntos_jornada = {
                pid: float(calculados.get(pid, 0))
                for pid in mi_equipo
            }

        detalles_guardados = sala_actualizada.get("detalles_jornadas") or {}
        detalles_usuario = detalles_guardados.get(
            f"jornada_{jornada}", {},
        ) or {}
        detalles = detalles_usuario.get(player_id)

        # IMPORTANTE: usar el desglose guardado en Firebase.
        # Así, si después vendes a un jugador, su jornada histórica
        # no cambia por la nueva plantilla.
        detalles_guardados_disponibles = isinstance(detalles, dict)

        if not detalles_guardados_disponibles:
            detalles = {}

        total_jornada = float(yo.get("puntos_jornada", 0))
        total_torneo = float(yo.get("puntos_totales", 0))

        col_pts1, col_pts2 = st.columns(2)
        with col_pts1:
            st.markdown(
                f'<div class="box"><div class="small">PUNTOS DE LA JORNADA</div>'
                f'<div class="big">⭐ {total_jornada:.2f}</div></div>',
                unsafe_allow_html=True,
            )
        with col_pts2:
            st.markdown(
                f'<div class="box"><div class="small">PUNTOS TOTALES</div>'
                f'<div class="big">🏆 {total_torneo:.2f}</div></div>',
                unsafe_allow_html=True,
            )

        mostrar_desglose_alineacion(
            mi_equipo,
            puntos_jornada,
            detalles,
            jornada,
            guardado=detalles_guardados_disponibles,
        )

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