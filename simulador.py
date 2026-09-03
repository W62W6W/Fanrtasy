
import random
import math

from datos import jugadores, jugadores_equipo


# ============================================================
# CONFIGURACIÓN
# ============================================================

EQUIPOS = [
    "Francia",
    "España",
    "Argentina",
    "Bélgica",
    "Inglaterra",
    "Noruega",
    "Marruecos",
    "Suiza"
]


# ============================================================
# POISSON
# ============================================================

def poisson(lam):

    if lam <= 0:
        return 0

    L = math.exp(-lam)

    k = 0
    p = 1.0

    while p > L:

        k += 1
        p *= random.random()

    return k - 1


# ============================================================
# PODER DEL EQUIPO
# ============================================================

def poder_equipo(equipo):

    plantilla = jugadores_equipo(equipo)

    if not plantilla:
        return {
            "ataque": 5,
            "defensa": 5
        }

    ataque = sum(
        jugador["ataque"]
        for jugador in plantilla.values()
    ) / len(plantilla)

    defensa = sum(
        jugador["defensa"]
        for jugador in plantilla.values()
    ) / len(plantilla)

    return {
        "ataque": ataque,
        "defensa": defensa
    }


# ============================================================
# GOLES ESPERADOS
# ============================================================

def goles_esperados(equipo_a, equipo_b):

    poder_a = poder_equipo(equipo_a)
    poder_b = poder_equipo(equipo_b)

    ataque_a = poder_a["ataque"]
    ataque_b = poder_b["ataque"]

    defensa_a = poder_a["defensa"]
    defensa_b = poder_b["defensa"]

    fuerza_a = (
        ataque_a * 0.65
        +
        (10 - defensa_b) * 0.35
    )

    fuerza_b = (
        ataque_b * 0.65
        +
        (10 - defensa_a) * 0.35
    )

    media_a = (
        1.15
        +
        (fuerza_a - 5) * 0.13
    )

    media_b = (
        1.15
        +
        (fuerza_b - 5) * 0.13
    )

    media_a = max(
        0.25,
        min(media_a, 3.5)
    )

    media_b = max(
        0.25,
        min(media_b, 3.5)
    )

    return media_a, media_b


# ============================================================
# ESTADÍSTICAS VACÍAS
# ============================================================

def estadisticas_vacias():

    return {

        "minutos": 90,

        "goles": 0,
        "asistencias": 0,

        "tiros": 0,
        "tiros_a_puerta": 0,

        "regates": 0,

        "intercepciones": 0,
        "duelos_ganados": 0,

        "penaltis_provocados": 0,
        "gol_propio": 0,

        "balones_perdidos": 0,
        "balones_recuperados": 0,

        "despejes": 0,
        "tapadas": 0,

        "amarillas": 0,
        "rojas": 0,

        "penaltis_fallados": 0,
        "penaltis_parados": 0,

        "faltas": 0
    }


# ============================================================
# ESTADÍSTICAS BASE
# ============================================================

def generar_estadisticas_base(jugador):

    posicion = jugador["posicion"]

    stats = estadisticas_vacias()


    # ========================================================
    # PORTERO
    # ========================================================

    if posicion == "POR":

        stats["tapadas"] = max(
            0,
            poisson(3)
        )

        stats["balones_recuperados"] = poisson(2)

        stats["duelos_ganados"] = poisson(1)

        stats["balones_perdidos"] = poisson(1)


    # ========================================================
    # DEFENSA
    # ========================================================

    elif posicion == "DEF":

        stats["intercepciones"] = poisson(2.5)

        stats["duelos_ganados"] = poisson(5)

        stats["balones_recuperados"] = poisson(6)

        stats["despejes"] = poisson(4)

        stats["regates"] = poisson(1)

        stats["tiros"] = poisson(0.5)

        stats["balones_perdidos"] = poisson(3)

        stats["faltas"] = poisson(1.2)


    # ========================================================
    # MEDIOCAMPISTA
    # ========================================================

    elif posicion == "MED":

        stats["intercepciones"] = poisson(1.5)

        stats["duelos_ganados"] = poisson(5)

        stats["balones_recuperados"] = poisson(5)

        stats["despejes"] = poisson(1)

        stats["regates"] = poisson(3)

        stats["tiros"] = poisson(1.5)

        stats["balones_perdidos"] = poisson(4)

        stats["faltas"] = poisson(1)


    # ========================================================
    # DELANTERO
    # ========================================================

    elif posicion == "DEL":

        stats["intercepciones"] = poisson(0.8)

        stats["duelos_ganados"] = poisson(4)

        stats["balones_recuperados"] = poisson(3)

        stats["regates"] = poisson(4)

        stats["tiros"] = poisson(2.5)

        stats["balones_perdidos"] = poisson(4)

        stats["faltas"] = poisson(0.8)


    # ========================================================
    # TARJETAS
    # ========================================================

    if random.random() < 0.12:

        stats["amarillas"] = 1


    if random.random() < 0.015:

        stats["rojas"] = 1


    return stats


# ============================================================
# TIROS A PUERTA
# ============================================================

def calcular_tiros_a_puerta(stats):

    tiros = stats["tiros"]

    if tiros <= 0:

        return 0

    tiros_puerta = 0

    for _ in range(tiros):

        if random.random() < 0.35:

            tiros_puerta += 1

    return min(
        tiros_puerta,
        tiros
    )


# ============================================================
# ASIGNAR GOLES
# ============================================================

def asignar_goles(
    estadisticas,
    cantidad
):

    if cantidad <= 0:

        return []

    ids = list(
        estadisticas.keys()
    )

    goleadores = []

    for _ in range(cantidad):

        id_jugador = random.choice(ids)

        goleadores.append(
            id_jugador
        )

        estadisticas[
            id_jugador
        ]["goles"] += 1

        estadisticas[
            id_jugador
        ]["tiros"] += 1

        estadisticas[
            id_jugador
        ]["tiros_a_puerta"] += 1

    return goleadores


# ============================================================
# ASISTENCIAS
# ============================================================

def asignar_asistencias(
    estadisticas,
    goleadores
):

    if not goleadores:

        return

    ids = list(
        estadisticas.keys()
    )

    for goleador in goleadores:

        if random.random() >= 0.70:

            continue

        posibles = [
            jugador
            for jugador in ids
            if jugador != goleador
        ]

        if not posibles:

            continue

        asistente = random.choice(
            posibles
        )

        estadisticas[
            asistente
        ]["asistencias"] += 1


# ============================================================
# AJUSTAR TIROS
# ============================================================

def ajustar_tiros(
    estadisticas
):

    for stats in estadisticas.values():

        tiros = stats["tiros"]

        tiros_puerta = (
            calcular_tiros_a_puerta(
                stats
            )
        )

        tiros_puerta = max(
            tiros_puerta,
            stats["goles"]
        )

        tiros_necesarios = max(
            tiros,
            stats["goles"]
        )

        stats["tiros_a_puerta"] = min(
            tiros_puerta,
            tiros_necesarios
        )

        stats["tiros"] = max(
            stats["tiros"],
            stats["goles"]
        )


# ============================================================
# ENCONTRAR PORTERO
# ============================================================

def encontrar_portero(equipo):

    plantilla = jugadores_equipo(
        equipo
    )

    for id_jugador, jugador in plantilla.items():

        if jugador["posicion"] == "POR":

            return id_jugador

    return None


# ============================================================
# CALCULAR TAPADAS
# ============================================================

def calcular_tapadas(
    estadisticas_portero,
    tiros_puerta_rival,
    goles_recibidos
):

    tapadas = max(
        0,
        tiros_puerta_rival
        - goles_recibidos
    )

    # Pequeña variación
    if random.random() < 0.20:

        tapadas += random.choice(
            [0, 1]
        )

    estadisticas_portero[
        "tapadas"
    ] = tapadas


# ============================================================
# MINUTOS
# ============================================================

def aplicar_minutos(
    estadisticas
):

    for stats in estadisticas.values():

        minutos = stats["minutos"]

        factor = minutos / 90

        stats["tiros"] = round(
            stats["tiros"]
            * factor
        )

        stats["tiros_a_puerta"] = min(
            stats["tiros_a_puerta"],
            stats["tiros"]
        )

        stats["regates"] = round(
            stats["regates"]
            * factor
        )

        stats["intercepciones"] = round(
            stats["intercepciones"]
            * factor
        )

        stats["duelos_ganados"] = round(
            stats["duelos_ganados"]
            * factor
        )

        stats["balones_recuperados"] = round(
            stats["balones_recuperados"]
            * factor
        )

        stats["despejes"] = round(
            stats["despejes"]
            * factor
        )

        stats["faltas"] = round(
            stats["faltas"]
            * factor
        )

        stats["balones_perdidos"] = round(
            stats["balones_perdidos"]
            * factor
        )


# ============================================================
# SIMULAR ESTADÍSTICAS DE UN EQUIPO
# ============================================================

def simular_estadisticas_equipo(
    equipo,
    goles,
    goles_recibidos
):

    plantilla = jugadores_equipo(
        equipo
    )

    estadisticas = {}


    # ========================================================
    # GENERAR ESTADÍSTICAS
    # ========================================================

    for id_jugador, jugador in plantilla.items():

        estadisticas[id_jugador] = (
            generar_estadisticas_base(
                jugador
            )
        )


    # ========================================================
    # GOLES
    # ========================================================

    goleadores = asignar_goles(
        estadisticas,
        goles
    )


    # ========================================================
    # ASISTENCIAS
    # ========================================================

    asignar_asistencias(
        estadisticas,
        goleadores
    )


    # ========================================================
    # TIROS
    # ========================================================

    ajustar_tiros(
        estadisticas
    )


    # ========================================================
    # PORTERO
    # ========================================================

    portero = encontrar_portero(
        equipo
    )


    return (
        estadisticas,
        portero
    )


# ============================================================
# SIMULAR PARTIDO
# ============================================================

def simular_partido(
    equipo_a,
    equipo_b
):

    if equipo_a == equipo_b:

        raise ValueError(
            "Los equipos deben ser diferentes."
        )

    if equipo_a not in EQUIPOS:

        raise ValueError(
            f"Equipo no válido: {equipo_a}"
        )

    if equipo_b not in EQUIPOS:

        raise ValueError(
            f"Equipo no válido: {equipo_b}"
        )


    # ========================================================
    # GOLES
    # ========================================================

    media_a, media_b = goles_esperados(
        equipo_a,
        equipo_b
    )

    goles_a = poisson(
        media_a
    )

    goles_b = poisson(
        media_b
    )


    # ========================================================
    # ESTADÍSTICAS
    # ========================================================

    estadisticas_a, portero_a = (
        simular_estadisticas_equipo(
            equipo_a,
            goles_a,
            goles_b
        )
    )

    estadisticas_b, portero_b = (
        simular_estadisticas_equipo(
            equipo_b,
            goles_b,
            goles_a
        )
    )


    # ========================================================
    # TIROS A PUERTA
    # ========================================================

    tiros_puerta_a = sum(
        stats["tiros_a_puerta"]
        for stats in estadisticas_a.values()
    )

    tiros_puerta_b = sum(
        stats["tiros_a_puerta"]
        for stats in estadisticas_b.values()
    )


    # ========================================================
    # TAPADAS
    # ========================================================

    if portero_a is not None:

        calcular_tapadas(
            estadisticas_a[
                portero_a
            ],
            tiros_puerta_b,
            goles_b
        )

    if portero_b is not None:

        calcular_tapadas(
            estadisticas_b[
                portero_b
            ],
            tiros_puerta_a,
            goles_a
        )


    # ========================================================
    # MINUTOS
    # ========================================================

    aplicar_minutos(
        estadisticas_a
    )

    aplicar_minutos(
        estadisticas_b
    )


    # ========================================================
    # RESULTADO
    # ========================================================

    return {

        "equipo_a": equipo_a,
        "equipo_b": equipo_b,

        "goles_a": goles_a,
        "goles_b": goles_b,

        "estadisticas_a":
            estadisticas_a,

        "estadisticas_b":
            estadisticas_b
    }


# ============================================================
# GENERAR CALENDARIO TODOS CONTRA TODOS
# ============================================================

def generar_calendario():

    partidos = []

    for i in range(
        len(EQUIPOS)
    ):

        for j in range(
            i + 1,
            len(EQUIPOS)
        ):

            partidos.append({

                "equipo_a":
                    EQUIPOS[i],

                "equipo_b":
                    EQUIPOS[j]

            })

    return partidos


# ============================================================
# GENERAR JORNADAS
# ============================================================

def generar_jornadas():

    equipos = EQUIPOS.copy()

    jornadas = []

    # Algoritmo round-robin
    # para que cada equipo juegue
    # una vez por jornada.

    fijo = equipos[0]

    rotacion = equipos[1:]

    for jornada in range(
        len(equipos) - 1
    ):

        partidos = []

        lista = [
            fijo
        ] + rotacion

        mitad = len(lista) // 2

        izquierda = lista[
            :mitad
        ]

        derecha = lista[
            mitad:
        ][::-1]

        for i in range(
            mitad
        ):

            equipo_a = izquierda[i]
            equipo_b = derecha[i]

            partidos.append({

                "equipo_a":
                    equipo_a,

                "equipo_b":
                    equipo_b
            })

        jornadas.append(
            partidos
        )

        # Rotar todos menos el primero
        rotacion = (
            rotacion[-1:]
            +
            rotacion[:-1]
        )

    return jornadas


# ============================================================
# SIMULAR UNA JORNADA
# ============================================================

def simular_jornada(
    jornada
):

    resultados = []

    for partido in jornada:

        resultado = simular_partido(
            partido["equipo_a"],
            partido["equipo_b"]
        )

        resultados.append(
            resultado
        )

    return resultados


# ============================================================
# CREAR CLASIFICACIÓN VACÍA
# ============================================================

def crear_clasificacion():

    return {

        equipo: {

            "equipo": equipo,

            "partidos": 0,

            "victorias": 0,

            "empates": 0,

            "derrotas": 0,

            "goles_favor": 0,

            "goles_contra": 0,

            "diferencia": 0,

            "puntos": 0

        }

        for equipo in EQUIPOS
    }


# ============================================================
# ACTUALIZAR CLASIFICACIÓN
# ============================================================

def actualizar_clasificacion(
    clasificacion,
    resultado
):

    equipo_a = resultado[
        "equipo_a"
    ]

    equipo_b = resultado[
        "equipo_b"
    ]

    goles_a = resultado[
        "goles_a"
    ]

    goles_b = resultado[
        "goles_b"
    ]


    # ========================================================
    # PARTIDOS
    # ========================================================

    clasificacion[
        equipo_a
    ]["partidos"] += 1

    clasificacion[
        equipo_b
    ]["partidos"] += 1


    # ========================================================
    # GOLES
    # ========================================================

    clasificacion[
        equipo_a
    ]["goles_favor"] += goles_a

    clasificacion[
        equipo_a
    ]["goles_contra"] += goles_b

    clasificacion[
        equipo_b
    ]["goles_favor"] += goles_b

    clasificacion[
        equipo_b
    ]["goles_contra"] += goles_a


    # ========================================================
    # RESULTADO
    # ========================================================

    if goles_a > goles_b:

        clasificacion[
            equipo_a
        ]["victorias"] += 1

        clasificacion[
            equipo_a
        ]["puntos"] += 3

        clasificacion[
            equipo_b
        ]["derrotas"] += 1


    elif goles_b > goles_a:

        clasificacion[
            equipo_b
        ]["victorias"] += 1

        clasificacion[
            equipo_b
        ]["puntos"] += 3

        clasificacion[
            equipo_a
        ]["derrotas"] += 1


    else:

        clasificacion[
            equipo_a
        ]["empates"] += 1

        clasificacion[
            equipo_b
        ]["empates"] += 1

        clasificacion[
            equipo_a
        ]["puntos"] += 1

        clasificacion[
            equipo_b
        ]["puntos"] += 1


    # ========================================================
    # DIFERENCIA DE GOLES
    # ========================================================

    clasificacion[
        equipo_a
    ]["diferencia"] = (
        clasificacion[
            equipo_a
        ]["goles_favor"]
        -
        clasificacion[
            equipo_a
        ]["goles_contra"]
    )

    clasificacion[
        equipo_b
    ]["diferencia"] = (
        clasificacion[
            equipo_b
        ]["goles_favor"]
        -
        clasificacion[
            equipo_b
        ]["goles_contra"]
    )


# ============================================================
# ACTUALIZAR CLASIFICACIÓN CON VARIOS RESULTADOS
# ============================================================

def actualizar_clasificacion_jornada(
    clasificacion,
    resultados
):

    for resultado in resultados:

        actualizar_clasificacion(
            clasificacion,
            resultado
        )


# ============================================================
# ORDENAR CLASIFICACIÓN
# ============================================================

def ordenar_clasificacion(
    clasificacion
):

    return sorted(

        clasificacion.values(),

        key=lambda x: (
            x["puntos"],
            x["diferencia"],
            x["goles_favor"]
        ),

        reverse=True
    )


# ============================================================
# SIMULAR TORNEO COMPLETO
# ============================================================

def simular_torneo():

    jornadas = generar_jornadas()

    clasificacion = crear_clasificacion()

    resultados_jornadas = []


    for jornada in jornadas:

        resultados = simular_jornada(
            jornada
        )

        actualizar_clasificacion_jornada(
            clasificacion,
            resultados
        )

        resultados_jornadas.append(
            resultados
        )


    return {

        "jornadas": jornadas,

        "resultados":
            resultados_jornadas,

        "clasificacion":
            clasificacion
    }


# ============================================================
# MOSTRAR PARTIDO
# ============================================================

def mostrar_partido(
    resultado
):

    print()
    print("=" * 70)

    print(
        f"{resultado['equipo_a']} "
        f"{resultado['goles_a']} - "
        f"{resultado['goles_b']} "
        f"{resultado['equipo_b']}"
    )

    print("=" * 70)


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":

    print(
        "🏆 SIMULADOR WORLD CUP FANTASY"
    )

    print()

    print(
        "Equipos:"
    )

    for equipo in EQUIPOS:

        print(
            f"🇺🇳 {equipo}"
        )


    print()

    print(
        "Generando calendario..."
    )

    jornadas = generar_jornadas()

    print(
        f"Jornadas: {len(jornadas)}"
    )

    print(
        f"Partidos: "
        f"{sum(len(j) for j in jornadas)}"
    )


    # ========================================================
    # MOSTRAR CALENDARIO
    # ========================================================

    for numero, jornada in enumerate(
        jornadas,
        start=1
    ):

        print()

        print(
            f"JORNADA {numero}"
        )

        print(
            "-" * 50
        )

        for partido in jornada:

            print(
                f"{partido['equipo_a']} "
                f"vs "
                f"{partido['equipo_b']}"
            )


    # ========================================================
    # SIMULAR UN PARTIDO
    # ========================================================

    print()

    print(
        "Simulando un partido..."
    )

    resultado = simular_partido(
        "Francia",
        "España"
    )

    mostrar_partido(
        resultado
    )


    # ========================================================
    # SIMULAR TORNEO
    # ========================================================

    print()

    print(
        "Simulando torneo..."
    )

    torneo = simular_torneo()

    clasificacion = ordenar_clasificacion(
        torneo["clasificacion"]
    )

    print()

    print(
        "🏆 CLASIFICACIÓN"
    )

    print(
        "-" * 70
    )

    for posicion, equipo in enumerate(
        clasificacion,
        start=1
    ):

        print(
            f"{posicion}. "
            f"{equipo['equipo']} "
            f"- "
            f"{equipo['puntos']} pts"
        )

