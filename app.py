import time
import streamlit as st

from datos import jugadores, PRESUPUESTO_FANTASY
from simulador import generar_jornadas, simular_jornada
from firebase import (
    crear_sala, obtener_sala, unirse_sala, guardar_equipo, marcar_listo,
    abrir_seleccion, cerrar_seleccion, iniciar_partida, guardar_torneo,
    obtener_torneo, guardar_resultado_jornada, avanzar_jornada,
    todos_jugadores_listos,
)

st.set_page_config(page_title="World Cup Fantasy", page_icon="⚽", layout="wide")

FORMACION = {"POR": 1, "DEF": 4, "MED": 3, "DEL": 3}
POS_NAMES = {"POR": "Portero", "DEF": "Defensa", "MED": "Mediocampista", "DEL": "Delantero"}

st.markdown("""
<style>
.stApp { background:#0b0b0b; color:white; }
.block-container { max-width:1400px; padding-top:2rem; }
.card { background:#171717; border:1px solid #333; border-radius:14px; padding:14px; margin-bottom:10px; }
.room { background:#171717; border:2px solid #555; border-radius:16px; padding:18px; text-align:center; font-size:38px; font-weight:900; letter-spacing:8px; }
.admin { background:#201900; border:1px solid #765d00; border-radius:14px; padding:18px; }
</style>
""", unsafe_allow_html=True)

for k, v in {
    "codigo_sala": None, "player_id": None, "nombre_jugador": "",
    "es_admin": False, "equipo_local": [], "presupuesto_local": PRESUPUESTO_FANTASY
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


def dinero(v):
    v = float(v or 0)
    if v >= 1_000_000:
        m = v / 1_000_000
        return f"{int(m)}M" if m.is_integer() else f"{m:.1f}M"
    if v >= 1_000:
        k = v / 1_000
        return f"{int(k)}K" if k.is_integer() else f"{k:.1f}K"
    return str(int(v))


def posiciones(equipo):
    r = {p: 0 for p in FORMACION}
    for pid in equipo:
        if pid in jugadores:
            r[jugadores[pid]["posicion"]] += 1
    return r


def equipo_valido(equipo):
    p = posiciones(equipo)
    return len(equipo) == 11 and all(p[x] == n for x, n in FORMACION.items())


def precio_equipo(equipo):
    return sum(jugadores[x]["precio"] for x in equipo if x in jugadores)


def puntos_jugador(pid, stats, rival_goles):
    pos = jugadores[pid]["posicion"]
    pts = 0.0
    detalle = []
    mins = stats.get("minutos", 0)

    if mins >= 60:
        pts += 2; detalle.append(("Minutos (60+)", 2))
    elif mins > 0:
        pts += 1; detalle.append(("Minutos", 1))

    reglas_gol = {"POR": 10, "DEF": 6, "MED": 5, "DEL": 4}
    if stats.get("goles", 0):
        v = stats["goles"] * reglas_gol[pos]
        pts += v; detalle.append((f"Goles ({stats['goles']})", v))
    if stats.get("asistencias", 0):
        v = stats["asistencias"] * 3
        pts += v; detalle.append((f"Asistencias ({stats['asistencias']})", v))

    positivas = [
        ("tiros_a_puerta", "Tiros a puerta", .8),
        ("regates", "Regates", .3),
        ("intercepciones", "Intercepciones", .4),
        ("duelos_ganados", "Duelos ganados", .15),
        ("balones_recuperados", "Recuperaciones", .2),
        ("despejes", "Despejes", .3),
        ("tapadas", "Tapadas", 1),
    ]
    negativas = [
        ("balones_perdidos", "Balones perdidos", -.15),
        ("faltas", "Faltas", -.1),
        ("amarillas", "Amarillas", -1),
        ("rojas", "Rojas", -3),
    ]
    for key, name, unit in positivas + negativas:
        n = stats.get(key, 0)
        if n:
            v = n * unit
            pts += v; detalle.append((f"{name} ({n})", v))

    if mins >= 60 and rival_goles == 0 and pos in ("POR", "DEF", "MED"):
        v = 4 if pos in ("POR", "DEF") else 1
        pts += v; detalle.append(("Portería a cero", v))

    return round(pts, 2), detalle


def calcular_puntos(resultados):
    puntos, detalles = {}, {}
    for partido in resultados:
        lados = [
            ("estadisticas_a", partido.get("goles_b", 0)),
            ("estadisticas_b", partido.get("goles_a", 0)),
        ]
        for stats_key, rival_goles in lados:
            for pid, stats in (partido.get(stats_key) or {}).items():
                if pid not in jugadores:
                    continue
                p, d = puntos_jugador(pid, stats, rival_goles)
                puntos[pid] = p
                detalles[pid] = {"puntos": p, "desglose": d, "stats": stats}
    return puntos, detalles


def reset():
    for k, v in {
        "codigo_sala": None, "player_id": None, "nombre_jugador": "",
        "es_admin": False, "equipo_local": [], "presupuesto_local": PRESUPUESTO_FANTASY
    }.items():
        st.session_state[k] = v


st.title("⚽ WORLD CUP FANTASY")
st.caption("Multijugador · hasta 30 jugadores + 1 administrador")

if not st.session_state.codigo_sala:
    a, b = st.columns(2)
    with a:
        st.header("👑 Crear partida")
        nombre = st.text_input("Nombre del administrador", key="admin_name")
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

    with b:
        st.header("🚪 Unirse a partida")
        nombre = st.text_input("Tu nombre", key="join_name")
        codigo = st.text_input("Código de sala", max_chars=6, key="join_code").strip().upper()
        if st.button("🚪 UNIRSE", use_container_width=True):
            if not nombre.strip():
                st.error("Escribe tu nombre.")
            elif len(codigo) != 6:
                st.error("El código debe tener 6 caracteres.")
            else:
                ok, mensaje, pid = unirse_sala(codigo, nombre.strip())
                if ok:
                    st.session_state.codigo_sala = codigo
                    st.session_state.player_id = pid
                    st.session_state.nombre_jugador = nombre.strip()
                    st.session_state.es_admin = False
                    st.rerun()
                else:
                    st.error(mensaje)
    st.stop()

codigo = st.session_state.codigo_sala
sala = obtener_sala(codigo)
if not sala:
    st.error("La sala ya no existe.")
    if st.button("Volver al inicio"):
        reset()
        st.rerun()
    st.stop()

estado = sala.get("estado", "esperando")
abierta = bool(sala.get("seleccion_abierta", False))
jornada = int(sala.get("jornada_actual", 0))
jugadores_sala = sala.get("jugadores") or {}
torneo = obtener_torneo(codigo)

st.markdown(f'<div class="room">{codigo}</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.metric("Jugadores", f"{len(jugadores_sala)} / 30")
c2.metric("Jornada", f"{jornada} / 7")
c3.metric("Rol", "👑 ADMIN" if st.session_state.es_admin else "👤 JUGADOR")
st.divider()

if st.session_state.es_admin:
    st.markdown('<div class="admin"><h3>👑 PANEL DEL ADMINISTRADOR</h3><p>El administrador no ocupa plaza de jugador.</p></div>', unsafe_allow_html=True)
    st.subheader("👥 Jugadores")
    if not jugadores_sala:
        st.info("Esperando jugadores...")
    else:
        for j in jugadores_sala.values():
            st.write(("🟢" if j.get("listo") else "⚪") + f" **{j.get('nombre','')}**")

    if estado in ("esperando", "seleccion"):
        st.divider()
        if not abierta:
            st.warning("🔒 Selección cerrada.")
            if st.button("🔓 ABRIR SELECCIÓN", use_container_width=True):
                abrir_seleccion(codigo); st.rerun()
        else:
            st.success("🔓 Selección abierta.")
            if st.button("🔒 CERRAR SELECCIÓN", use_container_width=True):
                cerrar_seleccion(codigo); st.rerun()

        if torneo is None and st.button("🎲 GENERAR TORNEO", use_container_width=True):
            torneo_nuevo = {"jornadas": generar_jornadas(), "resultados": {}, "puntos": {}, "detalles": {}}
            guardar_torneo(codigo, torneo_nuevo)
            st.rerun()

        if torneo is not None:
            n_listos = sum(1 for j in jugadores_sala.values() if j.get("listo"))
            st.write(f"**Listos: {n_listos} / {len(jugadores_sala)}**")
            if todos_jugadores_listos(codigo):
                if st.button("🚀 INICIAR PARTIDA", use_container_width=True):
                    ok, msg = iniciar_partida(codigo)
                    if ok: st.rerun()
                    else: st.error(msg)
            else:
                st.info("Espera a que todos pulsen LISTO.")

    elif estado == "jugando":
        st.header(f"⚽ JORNADA {jornada} / 7")
        if st.button(f"⚽ SIMULAR JORNADA {jornada}", use_container_width=True):
            torneo_actual = obtener_torneo(codigo)
            resultados = simular_jornada(torneo_actual["jornadas"][jornada - 1])
            pg, dg = calcular_puntos(resultados)
            torneo_actual["resultados"][str(jornada)] = resultados
            torneo_actual["puntos"][str(jornada)] = pg
            torneo_actual["detalles"][str(jornada)] = dg

            pj = {}
            for pid, j in jugadores_sala.items():
                pj[pid] = round(sum(pg.get(x, 0) for x in j.get("equipo", [])), 2)

            guardar_torneo(codigo, torneo_actual, jornada)
            guardar_resultado_jornada(codigo, jornada, pj, dg)
            st.rerun()

    elif estado == "resultado":
        st.header(f"🏆 RESULTADO · JORNADA {jornada}")
        ranking = sorted(jugadores_sala.values(), key=lambda x: -float(x.get("puntos_totales", 0)))
        for i, j in enumerate(ranking, 1):
            st.write(f"{i}. **{j['nombre']}** — Jornada: {float(j.get('puntos_jornada',0)):.2f} · Total: {float(j.get('puntos_totales',0)):.2f}")
        if st.button(f"➡️ PREPARAR JORNADA {jornada + 1}", disabled=jornada >= 7, use_container_width=True):
            avanzar_jornada(codigo); st.rerun()

    elif estado == "final":
        st.header("🏆 FINAL DEL TORNEO")
        ranking = sorted(jugadores_sala.values(), key=lambda x: -float(x.get("puntos_totales", 0)))
        for i, j in enumerate(ranking, 1):
            st.write(f"{i}. **{j['nombre']}** — 🏆 {float(j.get('puntos_totales',0)):.2f} puntos")

    if st.button("🔄 ACTUALIZAR PANEL", use_container_width=True):
        st.rerun()
    time.sleep(2)
    st.rerun()

yo = jugadores_sala.get(st.session_state.player_id)
if yo is None:
    st.error("No se encontró tu jugador en la sala.")
    st.stop()

if estado == "esperando" and not abierta:
    st.header("⏳ ESPERANDO AL ADMINISTRADOR")
    st.info("La selección está cerrada. No puedes elegir jugadores todavía.")
    time.sleep(2); st.rerun()

if estado == "seleccion" and abierta:
    st.header("👕 TU FANTASY")
    equipo = st.session_state.equipo_local
    guardado = yo.get("equipo", [])
    if guardado and not equipo:
        equipo = list(guardado)
        st.session_state.equipo_local = equipo
        st.session_state.presupuesto_local = PRESUPUESTO_FANTASY - precio_equipo(equipo)

    pos = posiciones(equipo)
    c1, c2, c3 = st.columns(3)
    c1.metric("Jugadores", f"{len(equipo)} / 11")
    c2.metric("Presupuesto", dinero(st.session_state.presupuesto_local))
    c3.metric("Estado", "🟢 LISTO" if yo.get("listo") else "⚪ PREPARANDO")

    st.subheader("👕 Mi equipo")
    for p in FORMACION:
        st.write(f"**{POS_NAMES[p]} ({pos[p]}/{FORMACION[p]})**")
        ids = [x for x in equipo if jugadores[x]["posicion"] == p]
        for pid in ids:
            j = jugadores[pid]
            st.markdown(f'<div class="card"><b>{j["nombre"]}</b><br>{j["equipo"]} · {p}<br>💰 {dinero(j["precio"])}</div>', unsafe_allow_html=True)
            if not yo.get("listo"):
                if st.button("❌ Quitar", key=f"remove_{pid}"):
                    equipo.remove(pid)
                    st.session_state.presupuesto_local = PRESUPUESTO_FANTASY - precio_equipo(equipo)
                    guardar_equipo(codigo, st.session_state.player_id, equipo, st.session_state.presupuesto_local)
                    st.rerun()

    st.divider()
    filtro = st.selectbox("Posición", ["Todos", "POR", "DEF", "MED", "DEL"])
    for pid, j in jugadores.items():
        p = j["posicion"]
        if pid in equipo or (filtro != "Todos" and p != filtro):
            continue
        puede = (not yo.get("listo") and len(equipo) < 11 and pos[p] < FORMACION[p]
                 and precio_equipo(equipo) + j["precio"] <= PRESUPUESTO_FANTASY)
        st.markdown(f'<div class="card"><b>{j["nombre"]}</b><br>{j["equipo"]} · {POS_NAMES[p]}<br>Ataque: {j["ataque"]} · Defensa: {j["defensa"]}<br>💰 {dinero(j["precio"])}</div>', unsafe_allow_html=True)
        if puede and st.button("➕ Fichar", key=f"buy_{pid}"):
            equipo.append(pid)
            st.session_state.presupuesto_local = PRESUPUESTO_FANTASY - precio_equipo(equipo)
            guardar_equipo(codigo, st.session_state.player_id, equipo, st.session_state.presupuesto_local)
            st.rerun()

    if equipo_valido(equipo):
        st.success("✅ Equipo 4-3-3 completo.")
        if not yo.get("listo"):
            if st.button("✅ ESTOY LISTO", use_container_width=True):
                guardar_equipo(codigo, st.session_state.player_id, equipo, st.session_state.presupuesto_local)
                ok, msg = marcar_listo(codigo, st.session_state.player_id, True)
                if ok: st.rerun()
                else: st.error(msg)
        else:
            st.success("🟢 Estás listo. Esperando al administrador.")
    else:
        st.warning(f"Te faltan {11-len(equipo)} jugadores.")
    time.sleep(2); st.rerun()

if estado == "jugando":
    st.header(f"⚽ JORNADA {jornada}")
    st.info("Esperando a que el administrador simule la jornada.")
    st.metric("Puntos acumulados", f"{float(yo.get('puntos_totales',0)):.2f}")

elif estado == "resultado":
    st.header(f"🏆 RESULTADO · JORNADA {jornada}")
    st.metric("Puntos de esta jornada", f"{float(yo.get('puntos_jornada',0)):.2f}")
    st.metric("Puntos acumulados", f"{float(yo.get('puntos_totales',0)):.2f}")
    ranking = sorted(jugadores_sala.values(), key=lambda x: -float(x.get("puntos_totales",0)))
    for i, j in enumerate(ranking, 1):
        st.write(f"{i}. **{j['nombre']}** — {float(j.get('puntos_totales',0)):.2f} pts")

elif estado == "final":
    st.header("🏆 FINAL DEL TORNEO")
    ranking = sorted(jugadores_sala.values(), key=lambda x: -float(x.get("puntos_totales",0)))
    for i, j in enumerate(ranking, 1):
        st.write(f"{i}. **{j['nombre']}** — 🏆 {float(j.get('puntos_totales',0)):.2f} pts")

st.divider()
if st.button("🔄 ACTUALIZAR", use_container_width=True):
    st.rerun()
time.sleep(2)
st.rerun()
