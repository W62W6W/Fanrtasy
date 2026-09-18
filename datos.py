import statistics


# ============================================================
# DATOS DE JUGADORES
# ============================================================
#
# 8 selecciones · 11 jugadores por selección
# 1 POR · 4 DEF · 3 MED · 3 DEL
#
# Las estadísticas se ajustan por valor de mercado Fantasy.
# Reglas principales:
# - DEF: ataque máximo 5
# - DEL: defensa máxima 5
# - MED: sin límite adicional
# - POR: ataque 1-3 y defensa 8-10
#
# Ejemplos:
# - Mbappé (200M): 10 ataque / 5 defensa
# - Jugador DEL de 120M: 9 ataque / 3 defensa
#
# ============================================================


jugadores = {'maignan': {'nombre': 'Mike Maignan', 'equipo': 'Francia', 'posicion': 'POR', 'precio': 55000000, 'ataque': 2, 'defensa': 9}, 'saliba': {'nombre': 'William Saliba', 'equipo': 'Francia', 'posicion': 'DEF', 'precio': 95000000, 'ataque': 5, 'defensa': 10}, 'konate': {'nombre': 'Ibrahima Konaté', 'equipo': 'Francia', 'posicion': 'DEF', 'precio': 50000000, 'ataque': 4, 'defensa': 8}, 'theo': {'nombre': 'Theo Hernández', 'equipo': 'Francia', 'posicion': 'DEF', 'precio': 65000000, 'ataque': 5, 'defensa': 9}, 'kounde': {'nombre': 'Jules Koundé', 'equipo': 'Francia', 'posicion': 'DEF', 'precio': 60000000, 'ataque': 5, 'defensa': 9}, 'tchouameni': {'nombre': 'Aurélien Tchouaméni', 'equipo': 'Francia', 'posicion': 'MED', 'precio': 75000000, 'ataque': 8, 'defensa': 7}, 'rabiot': {'nombre': 'Adrien Rabiot', 'equipo': 'Francia', 'posicion': 'MED', 'precio': 30000000, 'ataque': 5, 'defensa': 6}, 'olise': {'nombre': 'Michael Olise', 'equipo': 'Francia', 'posicion': 'MED', 'precio': 85000000, 'ataque': 8, 'defensa': 7}, 'dembele': {'nombre': 'Ousmane Dembélé', 'equipo': 'Francia', 'posicion': 'DEL', 'precio': 120000000, 'ataque': 9, 'defensa': 3}, 'mbappe': {'nombre': 'Kylian Mbappé', 'equipo': 'Francia', 'posicion': 'DEL', 'precio': 200000000, 'ataque': 10, 'defensa': 5}, 'doue': {'nombre': 'Désiré Doué', 'equipo': 'Francia', 'posicion': 'DEL', 'precio': 75000000, 'ataque': 8, 'defensa': 4}, 'joan_garcia': {'nombre': 'Joan García', 'equipo': 'España', 'posicion': 'POR', 'precio': 45000000, 'ataque': 2, 'defensa': 9}, 'carvajal': {'nombre': 'Dani Carvajal', 'equipo': 'España', 'posicion': 'DEF', 'precio': 15000000, 'ataque': 2, 'defensa': 5}, 'le_normand': {'nombre': 'Robin Le Normand', 'equipo': 'España', 'posicion': 'DEF', 'precio': 35000000, 'ataque': 3, 'defensa': 7}, 'cubarsi': {'nombre': 'Pau Cubarsí', 'equipo': 'España', 'posicion': 'DEF', 'precio': 90000000, 'ataque': 5, 'defensa': 10}, 'grimaldo': {'nombre': 'Alejandro Grimaldo', 'equipo': 'España', 'posicion': 'DEF', 'precio': 55000000, 'ataque': 4, 'defensa': 8}, 'rodri': {'nombre': 'Rodri', 'equipo': 'España', 'posicion': 'MED', 'precio': 130000000, 'ataque': 9, 'defensa': 9}, 'pedri': {'nombre': 'Pedri', 'equipo': 'España', 'posicion': 'MED', 'precio': 110000000, 'ataque': 8, 'defensa': 8}, 'fabian': {'nombre': 'Fabián Ruiz', 'equipo': 'España', 'posicion': 'MED', 'precio': 55000000, 'ataque': 7, 'defensa': 7}, 'lamine': {'nombre': 'Lamine Yamal', 'equipo': 'España', 'posicion': 'DEL', 'precio': 190000000, 'ataque': 10, 'defensa': 5}, 'nico': {'nombre': 'Nico Williams', 'equipo': 'España', 'posicion': 'DEL', 'precio': 85000000, 'ataque': 8, 'defensa': 4}, 'morata': {'nombre': 'Álvaro Morata', 'equipo': 'España', 'posicion': 'DEL', 'precio': 25000000, 'ataque': 5, 'defensa': 1}, 'emiliano_martinez': {'nombre': 'Emiliano Martínez', 'equipo': 'Argentina', 'posicion': 'POR', 'precio': 60000000, 'ataque': 3, 'defensa': 10}, 'romero': {'nombre': 'Cristian Romero', 'equipo': 'Argentina', 'posicion': 'DEF', 'precio': 66000000, 'ataque': 5, 'defensa': 9}, 'lisandro': {'nombre': 'Lisandro Martínez', 'equipo': 'Argentina', 'posicion': 'DEF', 'precio': 45000000, 'ataque': 4, 'defensa': 8}, 'senesi': {'nombre': 'Marcos Senesi', 'equipo': 'Argentina', 'posicion': 'DEF', 'precio': 30000000, 'ataque': 3, 'defensa': 7}, 'molina': {'nombre': 'Nahuel Molina', 'equipo': 'Argentina', 'posicion': 'DEF', 'precio': 36000000, 'ataque': 3, 'defensa': 7}, 'paredes': {'nombre': 'Leandro Paredes', 'equipo': 'Argentina', 'posicion': 'MED', 'precio': 31000000, 'ataque': 5, 'defensa': 6}, 'enzo': {'nombre': 'Enzo Fernández', 'equipo': 'Argentina', 'posicion': 'MED', 'precio': 86000000, 'ataque': 8, 'defensa': 7}, 'mac_allister': {'nombre': 'Alexis Mac Allister', 'equipo': 'Argentina', 'posicion': 'MED', 'precio': 90000000, 'ataque': 8, 'defensa': 8}, 'messi': {'nombre': 'Lionel Messi', 'equipo': 'Argentina', 'posicion': 'DEL', 'precio': 70000000, 'ataque': 8, 'defensa': 4}, 'julian_alvarez': {'nombre': 'Julián Alvarez', 'equipo': 'Argentina', 'posicion': 'DEL', 'precio': 105000000, 'ataque': 9, 'defensa': 3}, 'lautaro': {'nombre': 'Lautaro Martínez', 'equipo': 'Argentina', 'posicion': 'DEL', 'precio': 100000000, 'ataque': 9, 'defensa': 3}, 'courtois': {'nombre': 'Thibaut Courtois', 'equipo': 'Bélgica', 'posicion': 'POR', 'precio': 61000000, 'ataque': 3, 'defensa': 10}, 'debast': {'nombre': 'Zeno Debast', 'equipo': 'Bélgica', 'posicion': 'DEF', 'precio': 37000000, 'ataque': 3, 'defensa': 7}, 'theate': {'nombre': 'Arthur Theate', 'equipo': 'Bélgica', 'posicion': 'DEF', 'precio': 31000000, 'ataque': 3, 'defensa': 7}, 'de_winter': {'nombre': 'Koni De Winter', 'equipo': 'Bélgica', 'posicion': 'DEF', 'precio': 25000000, 'ataque': 3, 'defensa': 7}, 'castagne': {'nombre': 'Timothy Castagne', 'equipo': 'Bélgica', 'posicion': 'DEF', 'precio': 16000000, 'ataque': 2, 'defensa': 5}, 'onana': {'nombre': 'Amadou Onana', 'equipo': 'Bélgica', 'posicion': 'MED', 'precio': 56000000, 'ataque': 7, 'defensa': 7}, 'tielemans': {'nombre': 'Youri Tielemans', 'equipo': 'Bélgica', 'posicion': 'MED', 'precio': 45000000, 'ataque': 6, 'defensa': 6}, 'de_ketelaere': {'nombre': 'Charles De Ketelaere', 'equipo': 'Bélgica', 'posicion': 'MED', 'precio': 57000000, 'ataque': 7, 'defensa': 7}, 'doku': {'nombre': 'Jérémy Doku', 'equipo': 'Bélgica', 'posicion': 'DEL', 'precio': 80000000, 'ataque': 8, 'defensa': 4}, 'trossard': {'nombre': 'Leandro Trossard', 'equipo': 'Bélgica', 'posicion': 'DEL', 'precio': 45000000, 'ataque': 6, 'defensa': 2}, 'lukaku': {'nombre': 'Romelu Lukaku', 'equipo': 'Bélgica', 'posicion': 'DEL', 'precio': 35000000, 'ataque': 6, 'defensa': 2}, 'pickford': {'nombre': 'Jordan Pickford', 'equipo': 'Inglaterra', 'posicion': 'POR', 'precio': 56000000, 'ataque': 2, 'defensa': 9}, 'guehi': {'nombre': 'Marc Guéhi', 'equipo': 'Inglaterra', 'posicion': 'DEF', 'precio': 61000000, 'ataque': 5, 'defensa': 9}, 'konsa': {'nombre': 'Ezri Konsa', 'equipo': 'Inglaterra', 'posicion': 'DEF', 'precio': 51000000, 'ataque': 4, 'defensa': 8}, 'stones': {'nombre': 'John Stones', 'equipo': 'Inglaterra', 'posicion': 'DEF', 'precio': 26000000, 'ataque': 3, 'defensa': 7}, 'walker': {'nombre': 'Kyle Walker', 'equipo': 'Inglaterra', 'posicion': 'DEF', 'precio': 20000000, 'ataque': 2, 'defensa': 5}, 'rice': {'nombre': 'Declan Rice', 'equipo': 'Inglaterra', 'posicion': 'MED', 'precio': 111000000, 'ataque': 8, 'defensa': 8}, 'bellingham': {'nombre': 'Jude Bellingham', 'equipo': 'Inglaterra', 'posicion': 'MED', 'precio': 160000000, 'ataque': 9, 'defensa': 9}, 'eze': {'nombre': 'Eberechi Eze', 'equipo': 'Inglaterra', 'posicion': 'MED', 'precio': 60000000, 'ataque': 7, 'defensa': 7}, 'saka': {'nombre': 'Bukayo Saka', 'equipo': 'Inglaterra', 'posicion': 'DEL', 'precio': 121000000, 'ataque': 9, 'defensa': 3}, 'gordon': {'nombre': 'Anthony Gordon', 'equipo': 'Inglaterra', 'posicion': 'DEL', 'precio': 76000000, 'ataque': 8, 'defensa': 4}, 'kane': {'nombre': 'Harry Kane', 'equipo': 'Inglaterra', 'posicion': 'DEL', 'precio': 95000000, 'ataque': 8, 'defensa': 4}, 'nyland': {'nombre': 'Ørjan Nyland', 'equipo': 'Noruega', 'posicion': 'POR', 'precio': 5000000, 'ataque': 1, 'defensa': 8}, 'ajer': {'nombre': 'Kristoffer Ajer', 'equipo': 'Noruega', 'posicion': 'DEF', 'precio': 27000000, 'ataque': 3, 'defensa': 7}, 'ostigard': {'nombre': 'Leo Østigård', 'equipo': 'Noruega', 'posicion': 'DEF', 'precio': 17000000, 'ataque': 2, 'defensa': 5}, 'ryerson': {'nombre': 'Julian Ryerson', 'equipo': 'Noruega', 'posicion': 'DEF', 'precio': 40000000, 'ataque': 4, 'defensa': 8}, 'wolfe': {'nombre': 'David Møller Wolfe', 'equipo': 'Noruega', 'posicion': 'DEF', 'precio': 12000000, 'ataque': 2, 'defensa': 5}, 'berge': {'nombre': 'Sander Berge', 'equipo': 'Noruega', 'posicion': 'MED', 'precio': 32000000, 'ataque': 5, 'defensa': 6}, 'aursnes': {'nombre': 'Fredrik Aursnes', 'equipo': 'Noruega', 'posicion': 'MED', 'precio': 25000000, 'ataque': 5, 'defensa': 6}, 'odegaard': {'nombre': 'Martin Ødegaard', 'equipo': 'Noruega', 'posicion': 'MED', 'precio': 91000000, 'ataque': 8, 'defensa': 8}, 'nusa': {'nombre': 'Antonio Nusa', 'equipo': 'Noruega', 'posicion': 'DEL', 'precio': 46000000, 'ataque': 6, 'defensa': 2}, 'bobb': {'nombre': 'Oscar Bobb', 'equipo': 'Noruega', 'posicion': 'DEL', 'precio': 40000000, 'ataque': 6, 'defensa': 2}, 'haaland': {'nombre': 'Erling Haaland', 'equipo': 'Noruega', 'posicion': 'DEL', 'precio': 201000000, 'ataque': 10, 'defensa': 5}, 'bounou': {'nombre': 'Yassine Bounou', 'equipo': 'Marruecos', 'posicion': 'POR', 'precio': 35000000, 'ataque': 2, 'defensa': 9}, 'hakimi': {'nombre': 'Achraf Hakimi', 'equipo': 'Marruecos', 'posicion': 'DEF', 'precio': 85000000, 'ataque': 5, 'defensa': 10}, 'mazraoui': {'nombre': 'Noussair Mazraoui', 'equipo': 'Marruecos', 'posicion': 'DEF', 'precio': 38000000, 'ataque': 3, 'defensa': 7}, 'chadi_riad': {'nombre': 'Chadi Riad', 'equipo': 'Marruecos', 'posicion': 'DEF', 'precio': 21000000, 'ataque': 2, 'defensa': 5}, 'el_ouahdi': {'nombre': 'Zakaria El Ouahdi', 'equipo': 'Marruecos', 'posicion': 'DEF', 'precio': 18000000, 'ataque': 2, 'defensa': 5}, 'amrabat': {'nombre': 'Sofyan Amrabat', 'equipo': 'Marruecos', 'posicion': 'MED', 'precio': 33000000, 'ataque': 5, 'defensa': 6}, 'el_khannouss': {'nombre': 'Bilal El Khannouss', 'equipo': 'Marruecos', 'posicion': 'MED', 'precio': 46000000, 'ataque': 6, 'defensa': 6}, 'saibari': {'nombre': 'Ismael Saibari', 'equipo': 'Marruecos', 'posicion': 'MED', 'precio': 50000000, 'ataque': 7, 'defensa': 7}, 'brahim': {'nombre': 'Brahim Díaz', 'equipo': 'Marruecos', 'posicion': 'DEL', 'precio': 65000000, 'ataque': 7, 'defensa': 3}, 'rahimi': {'nombre': 'Soufiane Rahimi', 'equipo': 'Marruecos', 'posicion': 'DEL', 'precio': 26000000, 'ataque': 5, 'defensa': 1}, 'el_kaabi': {'nombre': 'Ayoub El Kaabi', 'equipo': 'Marruecos', 'posicion': 'DEL', 'precio': 18000000, 'ataque': 5, 'defensa': 1}, 'kobel': {'nombre': 'Gregor Kobel', 'equipo': 'Suiza', 'posicion': 'POR', 'precio': 65000000, 'ataque': 3, 'defensa': 10}, 'akanji': {'nombre': 'Manuel Akanji', 'equipo': 'Suiza', 'posicion': 'DEF', 'precio': 46000000, 'ataque': 4, 'defensa': 8}, 'elvedi': {'nombre': 'Nico Elvedi', 'equipo': 'Suiza', 'posicion': 'DEF', 'precio': 28000000, 'ataque': 3, 'defensa': 7}, 'schar': {'nombre': 'Fabian Schär', 'equipo': 'Suiza', 'posicion': 'DEF', 'precio': 22000000, 'ataque': 2, 'defensa': 5}, 'muheim': {'nombre': 'Miro Muheim', 'equipo': 'Suiza', 'posicion': 'DEF', 'precio': 13000000, 'ataque': 2, 'defensa': 5}, 'jashari': {'nombre': 'Ardon Jashari', 'equipo': 'Suiza', 'posicion': 'MED', 'precio': 40000000, 'ataque': 6, 'defensa': 6}, 'zakaria': {'nombre': 'Denis Zakaria', 'equipo': 'Suiza', 'posicion': 'MED', 'precio': 41000000, 'ataque': 6, 'defensa': 6}, 'xhaka': {'nombre': 'Granit Xhaka', 'equipo': 'Suiza', 'posicion': 'MED', 'precio': 35000000, 'ataque': 6, 'defensa': 6}, 'ndoye': {'nombre': 'Dan Ndoye', 'equipo': 'Suiza', 'posicion': 'DEL', 'precio': 47000000, 'ataque': 6, 'defensa': 2}, 'okafor': {'nombre': 'Noah Okafor', 'equipo': 'Suiza', 'posicion': 'DEL', 'precio': 36000000, 'ataque': 6, 'defensa': 2}, 'embolo': {'nombre': 'Breel Embolo', 'equipo': 'Suiza', 'posicion': 'DEL', 'precio': 30000000, 'ataque': 6, 'defensa': 2}}

# ============================================================
# AUXILIARES
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
