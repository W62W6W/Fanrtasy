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


jugadores = {"maignan": {"nombre": "Mike Maignan", "equipo": "Francia", "posicion": "POR", "precio": 55000000, "ataque": 2, "defensa": 9}, "saliba": {"nombre": "William Saliba", "equipo": "Francia", "posicion": "DEF", "precio": 95000000, "ataque": 7, "defensa": 9}, "konate": {"nombre": "Ibrahima Konaté", "equipo": "Francia", "posicion": "DEF", "precio": 50000000, "ataque": 6, "defensa": 8}, "theo": {"nombre": "Theo Hernández", "equipo": "Francia", "posicion": "DEF", "precio": 65000000, "ataque": 8, "defensa": 8}, "kounde": {"nombre": "Jules Koundé", "equipo": "Francia", "posicion": "DEF", "precio": 60000000, "ataque": 6, "defensa": 8}, "tchouameni": {"nombre": "Aurélien Tchouaméni", "equipo": "Francia", "posicion": "MED", "precio": 75000000, "ataque": 7, "defensa": 7}, "rabiot": {"nombre": "Adrien Rabiot", "equipo": "Francia", "posicion": "MED", "precio": 30000000, "ataque": 6, "defensa": 6}, "olise": {"nombre": "Michael Olise", "equipo": "Francia", "posicion": "MED", "precio": 85000000, "ataque": 8, "defensa": 8}, "dembele": {"nombre": "Ousmane Dembélé", "equipo": "Francia", "posicion": "DEL", "precio": 120000000, "ataque": 8, "defensa": 8}, "mbappe": {"nombre": "Kylian Mbappé", "equipo": "Francia", "posicion": "DEL", "precio": 200000000, "ataque": 10, "defensa": 8}, "doue": {"nombre": "Désiré Doué", "equipo": "Francia", "posicion": "DEL", "precio": 75000000, "ataque": 8, "defensa": 6}, "joan_garcia": {"nombre": "Joan García", "equipo": "España", "posicion": "POR", "precio": 45000000, "ataque": 1, "defensa": 9}, "carvajal": {"nombre": "Dani Carvajal", "equipo": "España", "posicion": "DEF", "precio": 15000000, "ataque": 4, "defensa": 4}, "le_normand": {"nombre": "Robin Le Normand", "equipo": "España", "posicion": "DEF", "precio": 35000000, "ataque": 6, "defensa": 7}, "cubarsi": {"nombre": "Pau Cubarsí", "equipo": "España", "posicion": "DEF", "precio": 90000000, "ataque": 7, "defensa": 9}, "grimaldo": {"nombre": "Alejandro Grimaldo", "equipo": "España", "posicion": "DEF", "precio": 55000000, "ataque": 7, "defensa": 8}, "rodri": {"nombre": "Rodri", "equipo": "España", "posicion": "MED", "precio": 130000000, "ataque": 8, "defensa": 8}, "pedri": {"nombre": "Pedri", "equipo": "España", "posicion": "MED", "precio": 110000000, "ataque": 8, "defensa": 8}, "fabian": {"nombre": "Fabián Ruiz", "equipo": "España", "posicion": "MED", "precio": 55000000, "ataque": 7, "defensa": 7}, "lamine": {"nombre": "Lamine Yamal", "equipo": "España", "posicion": "DEL", "precio": 190000000, "ataque": 10, "defensa": 8}, "nico": {"nombre": "Nico Williams", "equipo": "España", "posicion": "DEL", "precio": 85000000, "ataque": 9, "defensa": 6}, "morata": {"nombre": "Álvaro Morata", "equipo": "España", "posicion": "DEL", "precio": 25000000, "ataque": 4, "defensa": 4}, "emiliano_martinez": {"nombre": "Emiliano Martínez", "equipo": "Argentina", "posicion": "POR", "precio": 60000000, "ataque": 2, "defensa": 10}, "romero": {"nombre": "Cristian Romero", "equipo": "Argentina", "posicion": "DEF", "precio": 65000000, "ataque": 7, "defensa": 9}, "lisandro": {"nombre": "Lisandro Martínez", "equipo": "Argentina", "posicion": "DEF", "precio": 45000000, "ataque": 6, "defensa": 8}, "senesi": {"nombre": "Marcos Senesi", "equipo": "Argentina", "posicion": "DEF", "precio": 30000000, "ataque": 6, "defensa": 8}, "molina": {"nombre": "Nahuel Molina", "equipo": "Argentina", "posicion": "DEF", "precio": 35000000, "ataque": 5, "defensa": 8}, "paredes": {"nombre": "Leandro Paredes", "equipo": "Argentina", "posicion": "MED", "precio": 30000000, "ataque": 5, "defensa": 7}, "enzo": {"nombre": "Enzo Fernández", "equipo": "Argentina", "posicion": "MED", "precio": 85000000, "ataque": 7, "defensa": 9}, "mac_allister": {"nombre": "Alexis Mac Allister", "equipo": "Argentina", "posicion": "MED", "precio": 90000000, "ataque": 8, "defensa": 8}, "messi": {"nombre": "Lionel Messi", "equipo": "Argentina", "posicion": "DEL", "precio": 70000000, "ataque": 8, "defensa": 5}, "julian_alvarez": {"nombre": "Julián Alvarez", "equipo": "Argentina", "posicion": "DEL", "precio": 105000000, "ataque": 9, "defensa": 6}, "lautaro": {"nombre": "Lautaro Martínez", "equipo": "Argentina", "posicion": "DEL", "precio": 100000000, "ataque": 9, "defensa": 6}, "courtois": {"nombre": "Thibaut Courtois", "equipo": "Bélgica", "posicion": "POR", "precio": 60000000, "ataque": 3, "defensa": 10}, "debast": {"nombre": "Zeno Debast", "equipo": "Bélgica", "posicion": "DEF", "precio": 35000000, "ataque": 7, "defensa": 6}, "theate": {"nombre": "Arthur Theate", "equipo": "Bélgica", "posicion": "DEF", "precio": 30000000, "ataque": 5, "defensa": 9}, "de_winter": {"nombre": "Koni De Winter", "equipo": "Bélgica", "posicion": "DEF", "precio": 25000000, "ataque": 5, "defensa": 6}, "castagne": {"nombre": "Timothy Castagne", "equipo": "Bélgica", "posicion": "DEF", "precio": 15000000, "ataque": 3, "defensa": 5}, "onana": {"nombre": "Amadou Onana", "equipo": "Bélgica", "posicion": "MED", "precio": 55000000, "ataque": 6, "defensa": 8}, "tielemans": {"nombre": "Youri Tielemans", "equipo": "Bélgica", "posicion": "MED", "precio": 45000000, "ataque": 6, "defensa": 6}, "de_ketelaere": {"nombre": "Charles De Ketelaere", "equipo": "Bélgica", "posicion": "MED", "precio": 55000000, "ataque": 8, "defensa": 6}, "doku": {"nombre": "Jérémy Doku", "equipo": "Bélgica", "posicion": "DEL", "precio": 80000000, "ataque": 9, "defensa": 6}, "trossard": {"nombre": "Leandro Trossard", "equipo": "Bélgica", "posicion": "DEL", "precio": 45000000, "ataque": 7, "defensa": 4}, "lukaku": {"nombre": "Romelu Lukaku", "equipo": "Bélgica", "posicion": "DEL", "precio": 35000000, "ataque": 6, "defensa": 4}, "pickford": {"nombre": "Jordan Pickford", "equipo": "Inglaterra", "posicion": "POR", "precio": 55000000, "ataque": 3, "defensa": 9}, "guehi": {"nombre": "Marc Guéhi", "equipo": "Inglaterra", "posicion": "DEF", "precio": 60000000, "ataque": 5, "defensa": 9}, "konsa": {"nombre": "Ezri Konsa", "equipo": "Inglaterra", "posicion": "DEF", "precio": 50000000, "ataque": 5, "defensa": 9}, "stones": {"nombre": "John Stones", "equipo": "Inglaterra", "posicion": "DEF", "precio": 25000000, "ataque": 4, "defensa": 7}, "walker": {"nombre": "Kyle Walker", "equipo": "Inglaterra", "posicion": "DEF", "precio": 20000000, "ataque": 5, "defensa": 6}, "rice": {"nombre": "Declan Rice", "equipo": "Inglaterra", "posicion": "MED", "precio": 110000000, "ataque": 7, "defensa": 9}, "bellingham": {"nombre": "Jude Bellingham", "equipo": "Inglaterra", "posicion": "MED", "precio": 160000000, "ataque": 8, "defensa": 8}, "eze": {"nombre": "Eberechi Eze", "equipo": "Inglaterra", "posicion": "MED", "precio": 60000000, "ataque": 7, "defensa": 7}, "saka": {"nombre": "Bukayo Saka", "equipo": "Inglaterra", "posicion": "DEL", "precio": 120000000, "ataque": 7, "defensa": 9}, "gordon": {"nombre": "Anthony Gordon", "equipo": "Inglaterra", "posicion": "DEL", "precio": 75000000, "ataque": 7, "defensa": 7}, "kane": {"nombre": "Harry Kane", "equipo": "Inglaterra", "posicion": "DEL", "precio": 95000000, "ataque": 9, "defensa": 6}, "nyland": {"nombre": "Ørjan Nyland", "equipo": "Noruega", "posicion": "POR", "precio": 5000000, "ataque": 1, "defensa": 8}, "ajer": {"nombre": "Kristoffer Ajer", "equipo": "Noruega", "posicion": "DEF", "precio": 25000000, "ataque": 6, "defensa": 5}, "ostigard": {"nombre": "Leo Østigård", "equipo": "Noruega", "posicion": "DEF", "precio": 15000000, "ataque": 5, "defensa": 3}, "ryerson": {"nombre": "Julian Ryerson", "equipo": "Noruega", "posicion": "DEF", "precio": 40000000, "ataque": 6, "defensa": 7}, "wolfe": {"nombre": "David Møller Wolfe", "equipo": "Noruega", "posicion": "DEF", "precio": 12000000, "ataque": 4, "defensa": 4}, "berge": {"nombre": "Sander Berge", "equipo": "Noruega", "posicion": "MED", "precio": 30000000, "ataque": 7, "defensa": 5}, "aursnes": {"nombre": "Fredrik Aursnes", "equipo": "Noruega", "posicion": "MED", "precio": 25000000, "ataque": 5, "defensa": 5}, "odegaard": {"nombre": "Martin Ødegaard", "equipo": "Noruega", "posicion": "MED", "precio": 90000000, "ataque": 7, "defensa": 9}, "nusa": {"nombre": "Antonio Nusa", "equipo": "Noruega", "posicion": "DEL", "precio": 45000000, "ataque": 6, "defensa": 5}, "bobb": {"nombre": "Oscar Bobb", "equipo": "Noruega", "posicion": "DEL", "precio": 40000000, "ataque": 7, "defensa": 4}, "haaland": {"nombre": "Erling Haaland", "equipo": "Noruega", "posicion": "DEL", "precio": 200000000, "ataque": 9, "defensa": 9}, "bounou": {"nombre": "Yassine Bounou", "equipo": "Marruecos", "posicion": "POR", "precio": 35000000, "ataque": 2, "defensa": 8}, "hakimi": {"nombre": "Achraf Hakimi", "equipo": "Marruecos", "posicion": "DEF", "precio": 85000000, "ataque": 7, "defensa": 9}, "mazraoui": {"nombre": "Noussair Mazraoui", "equipo": "Marruecos", "posicion": "DEF", "precio": 35000000, "ataque": 4, "defensa": 9}, "chadi_riad": {"nombre": "Chadi Riad", "equipo": "Marruecos", "posicion": "DEF", "precio": 20000000, "ataque": 4, "defensa": 7}, "el_ouahdi": {"nombre": "Zakaria El Ouahdi", "equipo": "Marruecos", "posicion": "DEF", "precio": 18000000, "ataque": 4, "defensa": 4}, "amrabat": {"nombre": "Sofyan Amrabat", "equipo": "Marruecos", "posicion": "MED", "precio": 30000000, "ataque": 4, "defensa": 8}, "el_khannouss": {"nombre": "Bilal El Khannouss", "equipo": "Marruecos", "posicion": "MED", "precio": 45000000, "ataque": 5, "defensa": 7}, "saibari": {"nombre": "Ismael Saibari", "equipo": "Marruecos", "posicion": "MED", "precio": 50000000, "ataque": 7, "defensa": 7}, "brahim": {"nombre": "Brahim Díaz", "equipo": "Marruecos", "posicion": "DEL", "precio": 65000000, "ataque": 8, "defensa": 5}, "rahimi": {"nombre": "Soufiane Rahimi", "equipo": "Marruecos", "posicion": "DEL", "precio": 25000000, "ataque": 3, "defensa": 5}, "el_kaabi": {"nombre": "Ayoub El Kaabi", "equipo": "Marruecos", "posicion": "DEL", "precio": 18000000, "ataque": 4, "defensa": 4}, "kobel": {"nombre": "Gregor Kobel", "equipo": "Suiza", "posicion": "POR", "precio": 65000000, "ataque": 1, "defensa": 10}, "akanji": {"nombre": "Manuel Akanji", "equipo": "Suiza", "posicion": "DEF", "precio": 45000000, "ataque": 5, "defensa": 9}, "elvedi": {"nombre": "Nico Elvedi", "equipo": "Suiza", "posicion": "DEF", "precio": 25000000, "ataque": 3, "defensa": 8}, "schar": {"nombre": "Fabian Schär", "equipo": "Suiza", "posicion": "DEF", "precio": 20000000, "ataque": 6, "defensa": 5}, "muheim": {"nombre": "Miro Muheim", "equipo": "Suiza", "posicion": "DEF", "precio": 12000000, "ataque": 3, "defensa": 5}, "jashari": {"nombre": "Ardon Jashari", "equipo": "Suiza", "posicion": "MED", "precio": 40000000, "ataque": 6, "defensa": 6}, "zakaria": {"nombre": "Denis Zakaria", "equipo": "Suiza", "posicion": "MED", "precio": 40000000, "ataque": 5, "defensa": 7}, "xhaka": {"nombre": "Granit Xhaka", "equipo": "Suiza", "posicion": "MED", "precio": 35000000, "ataque": 6, "defensa": 6}, "ndoye": {"nombre": "Dan Ndoye", "equipo": "Suiza", "posicion": "DEL", "precio": 45000000, "ataque": 8, "defensa": 3}, "okafor": {"nombre": "Noah Okafor", "equipo": "Suiza", "posicion": "DEL", "precio": 35000000, "ataque": 5, "defensa": 5}, "embolo": {"nombre": "Breel Embolo", "equipo": "Suiza", "posicion": "DEL", "precio": 30000000, "ataque": 7, "defensa": 4}} AUXILIARES
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

    return 615_000_000


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
