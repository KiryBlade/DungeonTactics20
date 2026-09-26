import os
import json
from ui import (C, cabecera, subcabecera, pausa,
                input_int, input_str, confirmar, limpiar)
from dados import parsear_dano, promedio_dano, floor0


FICHAS_DIR = "fichas"
STATS = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]

ELEMENTOS = [
    "ácido", "contundente", "cortante", "fuego", "frío",
    "fuerza", "necrótico", "perforante", "psíquico",
    "radiante", "relámpago", "trueno", "veneno"
]


def asegurar_dir():
    if not os.path.exists(FICHAS_DIR):
        os.makedirs(FICHAS_DIR)


def listar_fichas():
    asegurar_dir()
    return sorted([f[:-5] for f in os.listdir(FICHAS_DIR) if f.endswith(".json")])


def ruta_ficha(nombre):
    return os.path.join(FICHAS_DIR, f"{nombre}.json")


def guardar_ficha(ficha):
    asegurar_dir()
    with open(ruta_ficha(ficha['nombre']), "w", encoding="utf-8") as f:
        json.dump(ficha, f, ensure_ascii=False, indent=2)
    print(f"{C.VERDE}[+] Ficha '{ficha['nombre']}' guardada{C.RESET}")


def _migrar(ficha):
    ficha.setdefault('crit_min', 20)
    ficha.setdefault('velocidad', 30)
    ficha.setdefault('conjuros', [])
    ficha.setdefault('cd_conjuros_modo', 'calculada')
    ficha.setdefault('cd_conjuros_base', 15)
    ficha.setdefault('cd_conjuros_stat', 'Inteligencia')
    ficha.setdefault('cd_conjuros_bono_extra', 0)
    ficha.setdefault('atk_conjuros_modo', 'calculada')
    ficha.setdefault('atk_conjuros_manual', 5)
    ficha.setdefault('atk_conjuros_stat', 'Inteligencia')
    ficha.setdefault('atk_conjuros_bono_extra', 0)

    for arma in ficha.get('armas', []):
        arma.setdefault('elemento', 'cortante')
    for conj in ficha.get('conjuros', []):
        conj.setdefault('elemento', 'fuerza')
        conj.setdefault('area', '')
        conj.setdefault('nivel', 1)
        conj.setdefault('mitad_si_salva', False)
        conj.setdefault('stat_salvacion', None)
        conj.setdefault('tipo', 'salvacion')
        conj.pop('cd_salvacion', None)
    return ficha


def cargar_ficha(nombre):
    ruta = ruta_ficha(nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        ficha = json.load(f)
    return _migrar(ficha)


def eliminar_ficha(nombre):
    ruta = ruta_ficha(nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        return True
    return False


def cd_conjuros_efectiva(ficha):
    if ficha.get('cd_conjuros_modo') == 'manual':
        return ficha.get('cd_conjuros_base', 15)
    comp = ficha.get('bono_competencia', 2)
    stat = ficha.get('cd_conjuros_stat', 'Inteligencia')
    mod = ficha.get('stats', {}).get(stat, {}).get('mod', 0)
    extra = ficha.get('cd_conjuros_bono_extra', 0)
    return 8 + comp + mod + extra


def atk_conjuros_efectivo(ficha):
    if ficha.get('atk_conjuros_modo') == 'manual':
        return ficha.get('atk_conjuros_manual', 5)
    comp = ficha.get('bono_competencia', 2)
    stat = ficha.get('atk_conjuros_stat', 'Inteligencia')
    mod = ficha.get('stats', {}).get(stat, {}).get('mod', 0)
    extra = ficha.get('atk_conjuros_bono_extra', 0)
    return comp + mod + extra


def calcular_bono_ataque_arma(arma, ficha):
    if arma.get('bono_ataque_manual') is not None:
        return arma['bono_ataque_manual']
    stat = arma.get('stat')
    if stat is None:
        return ficha['bono_ataque']
    mod_stat = ficha['stats'][stat]['mod']
    comp = ficha['bono_competencia']
    nivel_comp = arma.get('competencia', 'competente')
    if nivel_comp == 'pericia':
        bono_comp = comp * 2
    elif nivel_comp == 'competente':
        bono_comp = comp
    else:
        bono_comp = 0
    bono_magico = arma.get('bono_magico', 0) or 0
    return mod_stat + bono_comp + bono_magico


def describir_arma(arma, ficha):
    partes = []
    if arma.get('bono_ataque_manual') is not None:
        partes.append(f"manual +{arma['bono_ataque_manual']}")
    else:
        stat = arma.get('stat')
        if stat:
            partes.append(stat)
            nivel = arma.get('competencia', 'competente')
            if nivel == 'pericia':
                partes.append("pericia")
            elif nivel == 'competente':
                partes.append("comp")
            else:
                partes.append("sin comp")
            if arma.get('bono_magico'):
                partes.append(f"+{arma['bono_magico']}")
        else:
            partes.append("global")
    return ", ".join(partes)


def ficha_mostrar(ficha):
    cabecera(f"FICHA: {ficha['nombre']}")
    print(f"  {C.GRIS}┌─ Datos generales ──────────────────────┐{C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} Bono competencia:   {C.VERDE}+{ficha['bono_competencia']}{C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} Bono ataque global: {C.VERDE}+{ficha['bono_ataque']}{C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} CA:                 {C.VERDE}{ficha['ca']}{C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} Velocidad:          {C.VERDE}{ficha.get('velocidad', 30)} pies{C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} Crítico en:         {C.VERDE}{ficha.get('crit_min', 20)}-20{C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} CD conjuros:        {C.VERDE}{cd_conjuros_efectiva(ficha)}{C.RESET} "
          f"{C.GRIS}({ficha.get('cd_conjuros_modo', 'calculada')}){C.RESET}")
    print(f"  {C.GRIS}│{C.RESET} Ataque conjuros:    {C.VERDE}+{atk_conjuros_efectivo(ficha)}{C.RESET} "
          f"{C.GRIS}({ficha.get('atk_conjuros_modo', 'calculada')}){C.RESET}")
    print(f"  {C.GRIS}└────────────────────────────────────────┘{C.RESET}")

    subcabecera("Stats y salvaciones")
    print(f"  {C.GRIS}┌────────────────┬──────┬────────────┐{C.RESET}")
    print(f"  {C.GRIS}│ Stat           │ Mod  │ Salvación  │{C.RESET}")
    print(f"  {C.GRIS}├────────────────┼──────┼────────────┤{C.RESET}")
    for s in STATS:
        info = ficha['stats'][s]
        bono_salv = info['mod'] + (ficha['bono_competencia'] if info['comp'] else 0)
        print(f"  {C.GRIS}│{C.RESET} {s:14s} {C.GRIS}│{C.RESET} "
              f"{info['mod']:+3d}  {C.GRIS}│{C.RESET} {bono_salv:+3d}        {C.GRIS}│{C.RESET}")
    print(f"  {C.GRIS}└────────────────┴──────┴────────────┘{C.RESET}")

    subcabecera("Armas")
    if not ficha.get('armas'):
        print(f"    {C.GRIS}(ninguna){C.RESET}")
    for i, arma in enumerate(ficha.get('armas', [])):
        bono = calcular_bono_ataque_arma(arma, ficha)
        desc = describir_arma(arma, ficha)
        dados, bono_d = parsear_dano(arma['dano'])
        prom = floor0(promedio_dano(dados, bono_d))
        elem = arma.get('elemento', '—')
        print(f"    {C.VERDE}[{i+1}]{C.RESET} {arma['nombre']}")
        print(f"        {C.GRIS}Daño:{C.RESET} {arma['dano']:15s}  "
              f"{C.GRIS}Elem:{C.RESET} {elem:11s}  "
              f"{C.GRIS}~{C.RESET}{prom}")
        print(f"        {C.GRIS}Ataque:{C.RESET} +{bono} ({desc})")

    subcabecera("Conjuros")
    if not ficha.get('conjuros'):
        print(f"    {C.GRIS}(ninguno){C.RESET}")
    for i, conj in enumerate(ficha.get('conjuros', [])):
        dados, bono_d = parsear_dano(conj['dano'])
        prom = floor0(promedio_dano(dados, bono_d))
        elem = conj.get('elemento', '—')
        area = conj.get('area', '')
        tipo = conj.get('tipo', 'salvacion')
        if tipo == 'salvacion':
            salv = conj.get('stat_salvacion')
            info = f"salv {salv}" if salv else "salvación"
            if conj.get('mitad_si_salva'):
                info += " (mitad si salva)"
        else:
            info = "ataque de conjuro"
        print(f"    {C.VERDE}[{i+1}]{C.RESET} {conj['nombre']}")
        print(f"        {C.GRIS}Daño:{C.RESET} {conj['dano']:15s}  "
              f"{C.GRIS}Elem:{C.RESET} {elem:11s}  "
              f"{C.GRIS}~{C.RESET}{prom}")
        print(f"        {C.GRIS}{info}{C.RESET}")
        if area:
            print(f"        {C.GRIS}Área:{C.RESET} {area}")
    pausa()