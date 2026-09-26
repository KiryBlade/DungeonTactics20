import re
import math


def parsear_dano(notacion):
    notacion = notacion.replace(" ", "").lower()
    dados = []
    bono = 0
    terminos = re.findall(r'[+-]?\d+d\d+|[+-]?\d+', notacion)
    for t in terminos:
        if 'd' in t:
            signo = -1 if t.startswith('-') else 1
            t_limpio = t.lstrip('+-')
            cant, caras = t_limpio.split('d')
            dados.append((int(caras), int(cant) * signo))
        else:
            bono += int(t)
    return dados, bono


def min_dados(dados):
    total = 0
    for caras, cant in dados:
        if cant > 0:
            total += cant * 1
        else:
            total += cant * caras
    return total


def max_dados(dados):
    total = 0
    for caras, cant in dados:
        if cant > 0:
            total += cant * caras
        else:
            total += cant * 1
    return total


def promedio_dano(dados, bono):
    total = float(bono)
    for caras, cant in dados:
        total += ((caras + 1) / 2.0) * cant
    return total


def floor0(x):
    return int(max(0, math.floor(x)))


def probabilidad_exito(bono, cd, modo="normal", ataque=True):
    necesario = cd - bono

    def p_normal(n):
        if ataque:
            if n > 20:
                return 0.05
            n_efectivo = max(n, 2)
            return (21 - n_efectivo) / 20.0
        else:
            if n > 20:
                return 0.0
            n_efectivo = max(n, 1)
            return (21 - n_efectivo) / 20.0

    def p_ventaja(n):
        if ataque:
            if n > 20:
                return 1 - (19 / 20) ** 2
            n_efectivo = max(n, 2)
            fallo = (n_efectivo - 1) / 20.0
            return 1 - fallo ** 2
        else:
            if n > 20:
                return 0.0
            n_efectivo = max(n, 1)
            fallo = (n_efectivo - 1) / 20.0
            return 1 - fallo ** 2

    def p_desventaja(n):
        if ataque:
            if n > 20:
                return (1 / 20) ** 2
            n_efectivo = max(n, 2)
            exitos = (21 - n_efectivo) / 20.0
            return exitos ** 2
        else:
            if n > 20:
                return 0.0
            n_efectivo = max(n, 1)
            return ((21 - n_efectivo) / 20.0) ** 2

    if modo == "normal":
        return p_normal(necesario)
    elif modo == "ventaja":
        return p_ventaja(necesario)
    elif modo == "desventaja":
        return p_desventaja(necesario)


def probabilidad_critico(modo, umbral, bono, ac):
    """
    Probabilidad de crítico teniendo en cuenta que:
    - Un 20 natural SIEMPRE impacta (aunque necesites >20)
    - Un 20 natural SIEMPRE es crítico (si umbral <= 20)
    - El crítico necesita impactar: umbral_efectivo = max(umbral, necesario)
      pero nunca puede pasar de 20 (un 20 siempre impacta)
    """
    necesario = ac - bono
    umbral_efectivo = max(umbral, min(necesario, 20), 2)
    if umbral_efectivo > 20:
        return 0.0
    exitos_individuales = (21 - umbral_efectivo) / 20.0
    if modo == "normal":
        return exitos_individuales
    elif modo == "ventaja":
        fallo_individual = (umbral_efectivo - 1) / 20.0
        return 1 - fallo_individual ** 2
    elif modo == "desventaja":
        return exitos_individuales ** 2


def preguntar_modo():
    from ui import C
    while True:
        r = input(f"{C.AMARILLO}Modo (v=ventaja, d=desventaja, n=normal): {C.RESET}").strip().lower()
        if r in ("v", "ventaja"):
            return "ventaja"
        elif r in ("d", "desventaja"):
            return "desventaja"
        elif r in ("n", "normal", ""):
            return "normal"