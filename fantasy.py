
import random

from simulador import simular_partido
from datos import jugadores


# ============================================================
# PUNTOS POR POSICIÓN
# ============================================================

PUNTOS_GOL = {
    "POR": 10,
    "DEF": 6,
    "MED": 5,
    "DEL": 4
}


# ============================================================
# CALCULAR DESGLOSE DE PUNTOS
# ============================================================

def calcular_desglose(
    jugador,
    stats,
    goles_recibidos,
    porteria_a_cero
):

    posicion = jugador["posicion"]

    desglose = {}

    # --------------------------------------------------------
    # PARTICIPACIÓN
    # --------------------------------------------------------

    if stats.get("minutos", 0) >= 75:

        desglose["Participación"] = 1

    elif stats.get("minutos", 0) > 0:

        desglose["Participación"] = 0.5

    else:

        desglose["Participación"] = 0


    # --------------------------------------------------------
    # GOLES
    # --------------------------------------------------------

    desglose["Goles"] = (
        stats.get("goles", 0)
        * PUNTOS_GOL[posicion]
    )


    # --------------------------------------------------------
    # ASISTENCIAS
    # --------------------------------------------------------

    desglose["Asistencias"] = (
        stats.get("asistencias", 0)
        * 3
    )


    # --------------------------------------------------------
    # TIROS A PUERTA
    # --------------------------------------------------------

    desglose["Tiros a puerta"] = (
        stats.get("tiros_a_puerta", 0)
        * 1
    )


    # --------------------------------------------------------
    # REGATES
    # --------------------------------------------------------

    desglose["Regates"] = (
        stats.get("regates", 0)
        * 0.5
    )


    # --------------------------------------------------------
    # INTERCEPCIONES
    # --------------------------------------------------------

    desglose["Intercepciones"] = (
        stats.get("intercepciones", 0) // 2
    ) * 1


    # --------------------------------------------------------
    # DUELOS GANADOS
    # --------------------------------------------------------

    desglose["Duelos ganados"] = (
        stats.get("duelos_ganados", 0)
        * 0.5
    )


    # --------------------------------------------------------
    # PENALTIS PROVOCADOS
    # --------------------------------------------------------

    desglose["Penaltis provocados"] = (
        stats.get("penaltis_provocados", 0)
        * 2
    )


    # --------------------------------------------------------
    # GOL EN PROPIA
    # --------------------------------------------------------

    desglose["Gol en propia"] = (
        stats.get("gol_propio", 0)
        * -4
    )


    # --------------------------------------------------------
    # PORTERÍA A CERO
    # --------------------------------------------------------

    porteria = 0

    if porteria_a_cero:

        if posicion in ["POR", "DEF"]:

            porteria = 4

    desglose["Portería a cero"] = porteria


    # --------------------------------------------------------
    # GOLES RECIBIDOS
    # --------------------------------------------------------

    goles_recibidos_puntos = 0

    if posicion in ["POR", "DEF"]:

        goles_recibidos_puntos = (
            goles_recibidos * -1
        )

    desglose["Goles recibidos"] = (
        goles_recibidos_puntos
    )


    # --------------------------------------------------------
    # BALONES PERDIDOS
    # --------------------------------------------------------

    desglose["Balones perdidos"] = (
        stats.get("balones_perdidos", 0)
        * -0.25
    )


    # --------------------------------------------------------
    # BALONES RECUPERADOS
    # --------------------------------------------------------

    desglose["Balones recuperados"] = (
        stats.get("balones_recuperados", 0)
        * 0.5
    )


    # --------------------------------------------------------
    # DESPEJES
    # --------------------------------------------------------

    desglose["Despejes"] = (
        stats.get("despejes", 0)
        * 0.5
    )


    # --------------------------------------------------------
    # TAPADAS
    # --------------------------------------------------------

    desglose["Tapadas"] = (
        stats.get("tapadas", 0)
        * 1
    )


    # --------------------------------------------------------
    # AMARILLA
    # --------------------------------------------------------

    desglose["Amarillas"] = (
        stats.get("amarillas", 0)
        * -1
    )


    # --------------------------------------------------------
    # ROJA
    # --------------------------------------------------------

    desglose["Rojas"] = (
        stats.get("rojas", 0)
        * -3
    )


    # --------------------------------------------------------
    # PENALTI FALLADO
    # --------------------------------------------------------

    desglose["Penaltis fallados"] = (
        stats.get("penaltis_fallados", 0)
        * -2
    )


    # --------------------------------------------------------
    # PENALTI PARADO
    # --------------------------------------------------------

    desglose["Penaltis parados"] = (
        stats.get("penaltis_parados", 0)
        * 5
    )


    # --------------------------------------------------------
    # FALTAS
    # --------------------------------------------------------

    desglose["Faltas"] = (
        stats.get("faltas", 0)
        * -0.25
    )


    return desglose


# ============================================================
# CALCULAR PUNTOS
# ============================================================

def calcular_puntos(
    jugador,
    stats,
    goles_recibidos,
    porteria_a_cero
):

    desglose = calcular_desglose(
        jugador,
        stats,
        goles_recibidos,
        porteria_a_cero
    )

    puntos = sum(
        desglose.values()
    )

    return round(
        puntos,
        2
    )


# ============================================================
# CALCULAR FANTASY
# ============================================================

def calcular_fantasy(resultado):

    goles_a = resultado["goles_a"]
    goles_b = resultado["goles_b"]

    estadisticas_a = resultado[
        "estadisticas_a"
    ]

    estadisticas_b = resultado[
        "estadisticas_b"
    ]

    fantasy = {}


    # ========================================================
    # EQUIPO A
    # ========================================================

    porteria_a_cero = (
        goles_b == 0
    )

    for id_jugador, stats in estadisticas_a.items():

        jugador = jugadores[id_jugador]

        fantasy[id_jugador] = calcular_puntos(
            jugador,
            stats,
            goles_b,
            porteria_a_cero
        )


    # ========================================================
    # EQUIPO B
    # ========================================================

    porteria_b_cero = (
        goles_a == 0
    )

    for id_jugador, stats in estadisticas_b.items():

        jugador = jugadores[id_jugador]

        fantasy[id_jugador] = calcular_puntos(
            jugador,
            stats,
            goles_a,
            porteria_b_cero
        )


    return fantasy


# ============================================================
# CALCULAR DESGLOSE FANTASY DEL PARTIDO
# ============================================================

def calcular_desgloses_partido(resultado):

    goles_a = resultado["goles_a"]
    goles_b = resultado["goles_b"]

    estadisticas_a = resultado[
        "estadisticas_a"
    ]

    estadisticas_b = resultado[
        "estadisticas_b"
    ]

    desgloses = {}


    # ========================================================
    # EQUIPO A
    # ========================================================

    porteria_a_cero = (
        goles_b == 0
    )

    for id_jugador, stats in estadisticas_a.items():

        jugador = jugadores[id_jugador]

        desgloses[id_jugador] = calcular_desglose(
            jugador,
            stats,
            goles_b,
            porteria_a_cero
        )


    # ========================================================
    # EQUIPO B
    # ========================================================

    porteria_b_cero = (
        goles_a == 0
    )

    for id_jugador, stats in estadisticas_b.items():

        jugador = jugadores[id_jugador]

        desgloses[id_jugador] = calcular_desglose(
            jugador,
            stats,
            goles_a,
            porteria_b_cero
        )


    return desgloses


# ============================================================
# MOSTRAR FANTASY EN CONSOLA
# ============================================================

def mostrar_fantasy(
    resultado,
    fantasy
):

    print()
    print("=" * 90)
    print("🏆 PUNTUACIÓN FANTASY")
    print("=" * 90)

    equipos = [
        (
            resultado["equipo_a"],
            resultado["estadisticas_a"]
        ),
        (
            resultado["equipo_b"],
            resultado["estadisticas_b"]
        )
    ]

    for nombre_equipo, estadisticas in equipos:

        print()
        print(
            nombre_equipo
        )

        print("-" * 90)

        jugadores_equipo = sorted(
            estadisticas.keys(),
            key=lambda x: fantasy[x],
            reverse=True
        )

        for id_jugador in jugadores_equipo:

            jugador = jugadores[id_jugador]

            puntos = fantasy[id_jugador]

            print(
                f"{jugador['nombre']:<25}"
                f"{puntos:>6} puntos"
            )


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":

    resultado = simular_partido(
        "Francia",
        "España"
    )

    fantasy = calcular_fantasy(
        resultado
    )

    mostrar_fantasy(
        resultado,
        fantasy
    )
