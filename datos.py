import statistics


# ============================================================
# DATOS DE JUGADORES
# ============================================================
#
# CADA SELECCIÓN:
#
# 1 POR
# 4 DEF
# 3 MED
# 3 DEL
#
# El presupuesto Fantasy se calcula como:
#
# MEDIANA DE TODOS LOS PRECIOS × 12
#
# ============================================================


jugadores = {

    # ========================================================
    # FRANCIA
    # ========================================================

    "maignan": {
        "nombre": "Mike Maignan",
        "equipo": "Francia",
        "posicion": "POR",
        "precio": 55000000,
        "ataque": 6,
        "defensa": 9
    },

    "saliba": {
        "nombre": "William Saliba",
        "equipo": "Francia",
        "posicion": "DEF",
        "precio": 95000000,
        "ataque": 7,
        "defensa": 10
    },

    "konate": {
        "nombre": "Ibrahima Konaté",
        "equipo": "Francia",
        "posicion": "DEF",
        "precio": 50000000,
        "ataque": 5,
        "defensa": 8
    },

    "theo": {
        "nombre": "Theo Hernández",
        "equipo": "Francia",
        "posicion": "DEF",
        "precio": 65000000,
        "ataque": 9,
        "defensa": 8
    },

    "kounde": {
        "nombre": "Jules Koundé",
        "equipo": "Francia",
        "posicion": "DEF",
        "precio": 60000000,
        "ataque": 7,
        "defensa": 9
    },

    "tchouameni": {
        "nombre": "Aurélien Tchouaméni",
        "equipo": "Francia",
        "posicion": "MED",
        "precio": 75000000,
        "ataque": 7,
        "defensa": 9
    },

    "rabiot": {
        "nombre": "Adrien Rabiot",
        "equipo": "Francia",
        "posicion": "MED",
        "precio": 30000000,
        "ataque": 6,
        "defensa": 7
    },

    "olise": {
        "nombre": "Michael Olise",
        "equipo": "Francia",
        "posicion": "MED",
        "precio": 85000000,
        "ataque": 9,
        "defensa": 6
    },

    "dembele": {
        "nombre": "Ousmane Dembélé",
        "equipo": "Francia",
        "posicion": "DEL",
        "precio": 120000000,
        "ataque": 10,
        "defensa": 5
    },

    "mbappe": {
        "nombre": "Kylian Mbappé",
        "equipo": "Francia",
        "posicion": "DEL",
        "precio": 200000000,
        "ataque": 10,
        "defensa": 5
    },

    "doue": {
        "nombre": "Désiré Doué",
        "equipo": "Francia",
        "posicion": "DEL",
        "precio": 75000000,
        "ataque": 9,
        "defensa": 4
    },


    # ========================================================
    # ESPAÑA
    # ========================================================

    "joan_garcia": {
        "nombre": "Joan García",
        "equipo": "España",
        "posicion": "POR",
        "precio": 45000000,
        "ataque": 4,
        "defensa": 8
    },

    "carvajal": {
        "nombre": "Dani Carvajal",
        "equipo": "España",
        "posicion": "DEF",
        "precio": 15000000,
        "ataque": 6,
        "defensa": 8
    },

    "le_normand": {
        "nombre": "Robin Le Normand",
        "equipo": "España",
        "posicion": "DEF",
        "precio": 35000000,
        "ataque": 5,
        "defensa": 8
    },

    "cubarsi": {
        "nombre": "Pau Cubarsí",
        "equipo": "España",
        "posicion": "DEF",
        "precio": 90000000,
        "ataque": 7,
        "defensa": 9
    },

    "grimaldo": {
        "nombre": "Alejandro Grimaldo",
        "equipo": "España",
        "posicion": "DEF",
        "precio": 55000000,
        "ataque": 9,
        "defensa": 7
    },

    "rodri": {
        "nombre": "Rodri",
        "equipo": "España",
        "posicion": "MED",
        "precio": 130000000,
        "ataque": 9,
        "defensa": 10
    },

    "pedri": {
        "nombre": "Pedri",
        "equipo": "España",
        "posicion": "MED",
        "precio": 110000000,
        "ataque": 9,
        "defensa": 7
    },

    "fabian": {
        "nombre": "Fabián Ruiz",
        "equipo": "España",
        "posicion": "MED",
        "precio": 55000000,
        "ataque": 8,
        "defensa": 7
    },

    "lamine": {
        "nombre": "Lamine Yamal",
        "equipo": "España",
        "posicion": "DEL",
        "precio": 190000000,
        "ataque": 10,
        "defensa": 5
    },

    "nico": {
        "nombre": "Nico Williams",
        "equipo": "España",
        "posicion": "DEL",
        "precio": 85000000,
        "ataque": 9,
        "defensa": 5
    },

    "morata": {
        "nombre": "Álvaro Morata",
        "equipo": "España",
        "posicion": "DEL",
        "precio": 25000000,
        "ataque": 7,
        "defensa": 3
    },


    # ========================================================
    # ARGENTINA
    # ========================================================

    "emiliano_martinez": {
        "nombre": "Emiliano Martínez",
        "equipo": "Argentina",
        "posicion": "POR",
        "precio": 60000000,
        "ataque": 5,
        "defensa": 10
    },

    "romero": {
        "nombre": "Cristian Romero",
        "equipo": "Argentina",
        "posicion": "DEF",
        "precio": 65000000,
        "ataque": 6,
        "defensa": 10
    },

    "lisandro": {
        "nombre": "Lisandro Martínez",
        "equipo": "Argentina",
        "posicion": "DEF",
        "precio": 45000000,
        "ataque": 6,
        "defensa": 9
    },

    "senesi": {
        "nombre": "Marcos Senesi",
        "equipo": "Argentina",
        "posicion": "DEF",
        "precio": 30000000,
        "ataque": 6,
        "defensa": 8
    },

    "molina": {
        "nombre": "Nahuel Molina",
        "equipo": "Argentina",
        "posicion": "DEF",
        "precio": 35000000,
        "ataque": 8,
        "defensa": 8
    },

    "paredes": {
        "nombre": "Leandro Paredes",
        "equipo": "Argentina",
        "posicion": "MED",
        "precio": 30000000,
        "ataque": 7,
        "defensa": 8
    },

    "enzo": {
        "nombre": "Enzo Fernández",
        "equipo": "Argentina",
        "posicion": "MED",
        "precio": 85000000,
        "ataque": 9,
        "defensa": 8
    },

    "mac_allister": {
        "nombre": "Alexis Mac Allister",
        "equipo": "Argentina",
        "posicion": "MED",
        "precio": 90000000,
        "ataque": 9,
        "defensa": 8
    },

    "messi": {
        "nombre": "Lionel Messi",
        "equipo": "Argentina",
        "posicion": "DEL",
        "precio": 70000000,
        "ataque": 10,
        "defensa": 4
    },

    "julian_alvarez": {
        "nombre": "Julián Alvarez",
        "equipo": "Argentina",
        "posicion": "DEL",
        "precio": 105000000,
        "ataque": 10,
        "defensa": 5
    },

    "lautaro": {
        "nombre": "Lautaro Martínez",
        "equipo": "Argentina",
        "posicion": "DEL",
        "precio": 100000000,
        "ataque": 10,
        "defensa": 4
    },


    # ========================================================
    # BÉLGICA
    # ========================================================

    "courtois": {
        "nombre": "Thibaut Courtois",
        "equipo": "Bélgica",
        "posicion": "POR",
        "precio": 60000000,
        "ataque": 4,
        "defensa": 10
    },

    "debast": {
        "nombre": "Zeno Debast",
        "equipo": "Bélgica",
        "posicion": "DEF",
        "precio": 35000000,
        "ataque": 6,
        "defensa": 8
    },

    "theate": {
        "nombre": "Arthur Theate",
        "equipo": "Bélgica",
        "posicion": "DEF",
        "precio": 30000000,
        "ataque": 6,
        "defensa": 8
    },

    "de_winter": {
        "nombre": "Koni De Winter",
        "equipo": "Bélgica",
        "posicion": "DEF",
        "precio": 25000000,
        "ataque": 6,
        "defensa": 8
    },

    "castagne": {
        "nombre": "Timothy Castagne",
        "equipo": "Bélgica",
        "posicion": "DEF",
        "precio": 15000000,
        "ataque": 6,
        "defensa": 7
    },

    "onana": {
        "nombre": "Amadou Onana",
        "equipo": "Bélgica",
        "posicion": "MED",
        "precio": 55000000,
        "ataque": 7,
        "defensa": 9
    },

    "tielemans": {
        "nombre": "Youri Tielemans",
        "equipo": "Bélgica",
        "posicion": "MED",
        "precio": 45000000,
        "ataque": 8,
        "defensa": 8
    },

    "de_ketelaere": {
        "nombre": "Charles De Ketelaere",
        "equipo": "Bélgica",
        "posicion": "MED",
        "precio": 55000000,
        "ataque": 9,
        "defensa": 6
    },

    "doku": {
        "nombre": "Jérémy Doku",
        "equipo": "Bélgica",
        "posicion": "DEL",
        "precio": 80000000,
        "ataque": 10,
        "defensa": 5
    },

    "trossard": {
        "nombre": "Leandro Trossard",
        "equipo": "Bélgica",
        "posicion": "DEL",
        "precio": 45000000,
        "ataque": 9,
        "defensa": 4
    },

    "lukaku": {
        "nombre": "Romelu Lukaku",
        "equipo": "Bélgica",
        "posicion": "DEL",
        "precio": 35000000,
        "ataque": 9,
        "defensa": 4
    },


    # ========================================================
    # INGLATERRA
    # ========================================================

    "pickford": {
        "nombre": "Jordan Pickford",
        "equipo": "Inglaterra",
        "posicion": "POR",
        "precio": 55000000,
        "ataque": 4,
        "defensa": 9
    },

    "guehi": {
        "nombre": "Marc Guéhi",
        "equipo": "Inglaterra",
        "posicion": "DEF",
        "precio": 60000000,
        "ataque": 6,
        "defensa": 9
    },

    "konsa": {
        "nombre": "Ezri Konsa",
        "equipo": "Inglaterra",
        "posicion": "DEF",
        "precio": 50000000,
        "ataque": 6,
        "defensa": 8
    },

    "stones": {
        "nombre": "John Stones",
        "equipo": "Inglaterra",
        "posicion": "DEF",
        "precio": 25000000,
        "ataque": 6,
        "defensa": 8
    },

    "walker": {
        "nombre": "Kyle Walker",
        "equipo": "Inglaterra",
        "posicion": "DEF",
        "precio": 20000000,
        "ataque": 6,
        "defensa": 8
    },

    "rice": {
        "nombre": "Declan Rice",
        "equipo": "Inglaterra",
        "posicion": "MED",
        "precio": 110000000,
        "ataque": 8,
        "defensa": 10
    },

    "bellingham": {
        "nombre": "Jude Bellingham",
        "equipo": "Inglaterra",
        "posicion": "MED",
        "precio": 160000000,
        "ataque": 10,
        "defensa": 9
    },

    "eze": {
        "nombre": "Eberechi Eze",
        "equipo": "Inglaterra",
        "posicion": "MED",
        "precio": 60000000,
        "ataque": 9,
        "defensa": 5
    },

    "saka": {
        "nombre": "Bukayo Saka",
        "equipo": "Inglaterra",
        "posicion": "DEL",
        "precio": 120000000,
        "ataque": 10,
        "defensa": 5
    },

    "gordon": {
        "nombre": "Anthony Gordon",
        "equipo": "Inglaterra",
        "posicion": "DEL",
        "precio": 75000000,
        "ataque": 9,
        "defensa": 5
    },

    "kane": {
        "nombre": "Harry Kane",
        "equipo": "Inglaterra",
        "posicion": "DEL",
        "precio": 95000000,
        "ataque": 10,
        "defensa": 4
    },


    # ========================================================
    # NORUEGA
    # ========================================================

    "nyland": {
        "nombre": "Ørjan Nyland",
        "equipo": "Noruega",
        "posicion": "POR",
        "precio": 5000000,
        "ataque": 3,
        "defensa": 7
    },

    "ajer": {
        "nombre": "Kristoffer Ajer",
        "equipo": "Noruega",
        "posicion": "DEF",
        "precio": 25000000,
        "ataque": 6,
        "defensa": 8
    },

    "ostigard": {
        "nombre": "Leo Østigård",
        "equipo": "Noruega",
        "posicion": "DEF",
        "precio": 15000000,
        "ataque": 5,
        "defensa": 7
    },

    "ryerson": {
        "nombre": "Julian Ryerson",
        "equipo": "Noruega",
        "posicion": "DEF",
        "precio": 40000000,
        "ataque": 8,
        "defensa": 8
    },

    "wolfe": {
        "nombre": "David Møller Wolfe",
        "equipo": "Noruega",
        "posicion": "DEF",
        "precio": 12000000,
        "ataque": 6,
        "defensa": 7
    },

    "berge": {
        "nombre": "Sander Berge",
        "equipo": "Noruega",
        "posicion": "MED",
        "precio": 30000000,
        "ataque": 7,
        "defensa": 8
    },

    "aursnes": {
        "nombre": "Fredrik Aursnes",
        "equipo": "Noruega",
        "posicion": "MED",
        "precio": 25000000,
        "ataque": 7,
        "defensa": 8
    },

    "odegaard": {
        "nombre": "Martin Ødegaard",
        "equipo": "Noruega",
        "posicion": "MED",
        "precio": 90000000,
        "ataque": 10,
        "defensa": 6
    },

    "nusa": {
        "nombre": "Antonio Nusa",
        "equipo": "Noruega",
        "posicion": "DEL",
        "precio": 45000000,
        "ataque": 9,
        "defensa": 4
    },

    "bobb": {
        "nombre": "Oscar Bobb",
        "equipo": "Noruega",
        "posicion": "DEL",
        "precio": 40000000,
        "ataque": 9,
        "defensa": 4
    },

    "haaland": {
        "nombre": "Erling Haaland",
        "equipo": "Noruega",
        "posicion": "DEL",
        "precio": 200000000,
        "ataque": 10,
        "defensa": 5
    },


    # ========================================================
    # MARRUECOS
    # ========================================================

    "bounou": {
        "nombre": "Yassine Bounou",
        "equipo": "Marruecos",
        "posicion": "POR",
        "precio": 35000000,
        "ataque": 3,
        "defensa": 9
    },

    "hakimi": {
        "nombre": "Achraf Hakimi",
        "equipo": "Marruecos",
        "posicion": "DEF",
        "precio": 85000000,
        "ataque": 10,
        "defensa": 9
    },

    "mazraoui": {
        "nombre": "Noussair Mazraoui",
        "equipo": "Marruecos",
        "posicion": "DEF",
        "precio": 35000000,
        "ataque": 7,
        "defensa": 8
    },

    "chadi_riad": {
        "nombre": "Chadi Riad",
        "equipo": "Marruecos",
        "posicion": "DEF",
        "precio": 20000000,
        "ataque": 5,
        "defensa": 8
    },

    "el_ouahdi": {
        "nombre": "Zakaria El Ouahdi",
        "equipo": "Marruecos",
        "posicion": "DEF",
        "precio": 18000000,
        "ataque": 7,
        "defensa": 7
    },

    "amrabat": {
        "nombre": "Sofyan Amrabat",
        "equipo": "Marruecos",
        "posicion": "MED",
        "precio": 30000000,
        "ataque": 6,
        "defensa": 9
    },

    "el_khannouss": {
        "nombre": "Bilal El Khannouss",
        "equipo": "Marruecos",
        "posicion": "MED",
        "precio": 45000000,
        "ataque": 8,
        "defensa": 6
    },

    "saibari": {
        "nombre": "Ismael Saibari",
        "equipo": "Marruecos",
        "posicion": "MED",
        "precio": 50000000,
        "ataque": 9,
        "defensa": 6
    },

    "brahim": {
        "nombre": "Brahim Díaz",
        "equipo": "Marruecos",
        "posicion": "DEL",
        "precio": 65000000,
        "ataque": 9,
        "defensa": 4
    },

    "rahimi": {
        "nombre": "Soufiane Rahimi",
        "equipo": "Marruecos",
        "posicion": "DEL",
        "precio": 25000000,
        "ataque": 8,
        "defensa": 4
    },

    "el_kaabi": {
        "nombre": "Ayoub El Kaabi",
        "equipo": "Marruecos",
        "posicion": "DEL",
        "precio": 18000000,
        "ataque": 7,
        "defensa": 3
    },


    # ========================================================
    # SUIZA
    # ========================================================

    "kobel": {
        "nombre": "Gregor Kobel",
        "equipo": "Suiza",
        "posicion": "POR",
        "precio": 65000000,
        "ataque": 4,
        "defensa": 10
    },

    "akanji": {
        "nombre": "Manuel Akanji",
        "equipo": "Suiza",
        "posicion": "DEF",
        "precio": 45000000,
        "ataque": 6,
        "defensa": 9
    },

    "elvedi": {
        "nombre": "Nico Elvedi",
        "equipo": "Suiza",
        "posicion": "DEF",
        "precio": 25000000,
        "ataque": 5,
        "defensa": 8
    },

    "schar": {
        "nombre": "Fabian Schär",
        "equipo": "Suiza",
        "posicion": "DEF",
        "precio": 20000000,
        "ataque": 6,
        "defensa": 8
    },

    "muheim": {
        "nombre": "Miro Muheim",
        "equipo": "Suiza",
        "posicion": "DEF",
        "precio": 12000000,
        "ataque": 7,
        "defensa": 7
    },

    "jashari": {
        "nombre": "Ardon Jashari",
        "equipo": "Suiza",
        "posicion": "MED",
        "precio": 40000000,
        "ataque": 7,
        "defensa": 8
    },

    "zakaria": {
        "nombre": "Denis Zakaria",
        "equipo": "Suiza",
        "posicion": "MED",
        "precio": 40000000,
        "ataque": 7,
        "defensa": 9
    },

    "xhaka": {
        "nombre": "Granit Xhaka",
        "equipo": "Suiza",
        "posicion": "MED",
        "precio": 35000000,
        "ataque": 8,
        "defensa": 8
    },

    "ndoye": {
        "nombre": "Dan Ndoye",
        "equipo": "Suiza",
        "posicion": "DEL",
        "precio": 45000000,
        "ataque": 9,
        "defensa": 4
    },

    "okafor": {
        "nombre": "Noah Okafor",
        "equipo": "Suiza",
        "posicion": "DEL",
        "precio": 35000000,
        "ataque": 8,
        "defensa": 4
    },

    "embolo": {
        "nombre": "Breel Embolo",
        "equipo": "Suiza",
        "posicion": "DEL",
        "precio": 30000000,
        "ataque": 8,
        "defensa": 4
    }
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def jugadores_equipo(equipo):

    return {
        id_jugador: jugador
        for id_jugador, jugador in jugadores.items()
        if jugador["equipo"] == equipo
    }


def jugadores_posicion(posicion):

    return {
        id_jugador: jugador
        for id_jugador, jugador in jugadores.items()
        if jugador["posicion"] == posicion
    }


def precio_jugador(id_jugador):

    return jugadores[id_jugador]["precio"]


def precio_total():

    return sum(
        jugador["precio"]
        for jugador in jugadores.values()
    )


# ============================================================
# MEDIANA DE PRECIOS
# ============================================================

def mediana_precios():

    precios = [
        jugador["precio"]
        for jugador in jugadores.values()
    ]

    return statistics.median(precios)


# ============================================================
# PRESUPUESTO FANTASY
# ============================================================

def presupuesto_fantasy():

    return int(
        mediana_precios() * 12
    )


# ============================================================
# EQUIPOS DISPONIBLES
# ============================================================

def equipos_disponibles():

    return sorted(
        set(
            jugador["equipo"]
            for jugador in jugadores.values()
        )
    )


# ============================================================
# FORMATO DE PRECIOS
# ============================================================

def formato_precio(precio):

    if precio >= 1_000_000_000:

        return f"{precio / 1_000_000_000:.1f}B"

    if precio >= 1_000_000:

        return f"{precio / 1_000_000:.1f}M"

    if precio >= 1_000:

        return f"{precio / 1_000:.0f}K"

    return str(precio)


# ============================================================
# PRESUPUESTO GLOBAL
# ============================================================

PRESUPUESTO_FANTASY = presupuesto_fantasy()