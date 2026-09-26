from ui import (C, cabecera, subcabecera, pausa,
                limpiar, input_int, input_str, confirmar, menu)
from ficha import STATS, ELEMENTOS


def pedir_elemento(elemento_default=None):
    from ui import pedir_de_lista
    items = [f"{e}" for e in ELEMENTOS]
    idx = pedir_de_lista("ELEMENTO DEL DAÑO", items, permitir_atras=True, etiqueta_atras="Cancelar")
    if idx is None:
        return elemento_default
    return ELEMENTOS[idx]


def pedir_arma(indice, elemento_default=None):
    cabecera(f"NUEVA ARMA {indice}")
    nombre = input_str(f"{C.AMARILLO}Nombre (ENTER para terminar): {C.RESET}")
    if not nombre:
        return None
    dano = input_str(f"{C.AMARILLO}Daño (ej. 1d12+8+9d6): {C.RESET}")
    if not dano:
        return None

    elemento = pedir_elemento(elemento_default or "cortante")

    print(f"\n  {C.GRIS}[1] Global  [2] Stat+comp+magia  [3] Manual{C.RESET}")
    op = input_str(f"  {C.AMARILLO}Elige: {C.RESET}")
    arma = {"nombre": nombre, "dano": dano, "elemento": elemento}
    if op == "2":
        for i, s in enumerate(STATS, 1):
            print(f"    [{i}] {s}")
        try:
            idx = int(input_str(f"  {C.AMARILLO}Stat: {C.RESET}")) - 1
            arma['stat'] = STATS[idx]
        except (ValueError, IndexError):
            arma['stat'] = "Fuerza"
        print(f"  [1] Sin comp  [2] Competente  [3] Pericia")
        comp_op = input_str(f"  {C.AMARILLO}Elige: {C.RESET}")
        if comp_op == "1":
            arma['competencia'] = 'ninguna'
        elif comp_op == "3":
            arma['competencia'] = 'pericia'
        else:
            arma['competencia'] = 'competente'
        bono_mag = input_str(f"  {C.AMARILLO}Bono mágico (0 si no): {C.RESET}")
        try:
            arma['bono_magico'] = int(bono_mag) if bono_mag else 0
        except ValueError:
            arma['bono_magico'] = 0
    elif op == "3":
        bono_manual = input_str(f"  {C.AMARILLO}Bono manual: {C.RESET}")
        try:
            arma['bono_ataque_manual'] = int(bono_manual) if bono_manual else None
        except ValueError:
            arma['bono_ataque_manual'] = None
    return arma


def pedir_conjuro(indice):
    cabecera(f"NUEVO CONJURO {indice}")
    nombre = input_str(f"{C.AMARILLO}Nombre (ENTER para terminar): {C.RESET}")
    if not nombre:
        return None
    dano = input_str(f"{C.AMARILLO}Daño (ej. 8d6): {C.RESET}")
    if not dano:
        return None

    elemento = pedir_elemento("fuerza")

    print(f"\n  {C.GRIS}Tipo de conjuro:{C.RESET}")
    print(f"  {C.VERDE}[1]{C.RESET} Salvación (el enemigo tira salvación)")
    print(f"  {C.VERDE}[2]{C.RESET} Ataque (tú tiras ataque de conjuro)")
    tipo_op = input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "1")
    tipo = "ataque" if tipo_op == "2" else "salvacion"

    stat_salv = None
    mitad = False
    if tipo == "salvacion":
        print(f"  {C.GRIS}Stat de la salvación:{C.RESET}")
        for i, s in enumerate(STATS, 1):
            print(f"    [{i}] {s}")
        try:
            idx = int(input_str(f"  {C.AMARILLO}Elige: {C.RESET}")) - 1
            stat_salv = STATS[idx]
        except (ValueError, IndexError):
            stat_salv = "Destreza"
        mitad = confirmar("¿Mitad si salva?")

    area = input_str(f"{C.AMARILLO}Área (ej. esfera 6m, ENTER si no): {C.RESET}", "")
    nivel = input_int(f"{C.AMARILLO}Nivel (1-9): {C.RESET}", 1)

    return {
        "nombre": nombre,
        "dano": dano,
        "elemento": elemento,
        "tipo": tipo,
        "area": area,
        "nivel": nivel,
        "stat_salvacion": stat_salv,
        "mitad_si_salva": mitad,
    }