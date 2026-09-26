import os
import json
from ui import (C, cabecera, subcabecera, pausa,
                limpiar, input_int, input_str, confirmar, menu)
from ficha import ELEMENTOS, STATS


CRIATURAS_DIR = "criaturas"


def asegurar_dir():
    if not os.path.exists(CRIATURAS_DIR):
        os.makedirs(CRIATURAS_DIR)


def listar_criaturas():
    asegurar_dir()
    return sorted([f[:-5] for f in os.listdir(CRIATURAS_DIR) if f.endswith(".json")])


def ruta_criatura(nombre):
    return os.path.join(CRIATURAS_DIR, f"{nombre}.json")


def guardar_criatura(criatura):
    asegurar_dir()
    with open(ruta_criatura(criatura['nombre']), "w", encoding="utf-8") as f:
        json.dump(criatura, f, ensure_ascii=False, indent=2)


def cargar_criatura(nombre):
    ruta = ruta_criatura(nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def eliminar_criatura(nombre):
    ruta = ruta_criatura(nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        return True
    return False


def _elegir_elementos(titulo, ya_elegidos=None):
    elegidos = list(ya_elegidos or [])
    while True:
        items = [e for e in ELEMENTOS if e not in elegidos]
        cabecera(titulo)
        if elegidos:
            print(f"  {C.GRIS}Elegidos: {', '.join(elegidos)}{C.RESET}\n")
        else:
            print(f"  {C.GRIS}(ninguno todavía){C.RESET}\n")
        for i, e in enumerate(items, 1):
            print(f"  {C.VERDE}[{i}]{C.RESET} {e}")
        print(f"\n  {C.ROJO}[X]{C.RESET} Omitir")
        op = input(f"\n{C.CIAN}└──╼ {C.RESET}").strip().upper()
        if op == "X":
            return elegidos
        if op.isdigit():
            idx = int(op) - 1
            if 0 <= idx < len(items):
                elegidos.append(items[idx])
                continue
        print(f"{C.ROJO}[!] Opción no válida{C.RESET}")


def _pedir_stats_opcional():
    print(f"\n{C.GRIS}--- STATS (opcional, ENTER para omitir) ---{C.RESET}")
    stats = {}
    for s in STATS:
        v = input_str(f"  {s:15s} mod (ENTER = omitir): {C.RESET}", "")
        if v:
            try:
                stats[s] = {"mod": int(v)}
            except ValueError:
                pass
    return stats


def _criatura_custom():
    cabecera("CRIATURA CUSTOM (un solo uso)")
    nombre = input_str(f"{C.AMARILLO}Nombre: {C.RESET}", "Enemigo")
    ac = input_int(f"{C.AMARILLO}AC: {C.RESET}", 15)

    stats = _pedir_stats_opcional()

    resistencias = _elegir_elementos("RESISTENCIAS")
    vulnerabilidades = _elegir_elementos("VULNERABILIDADES")
    inmunidades = _elegir_elementos("INMUNIDADES")

    return {
        "nombre": nombre,
        "ac": ac,
        "stats": stats,
        "resistencias": resistencias,
        "vulnerabilidades": vulnerabilidades,
        "inmunidades": inmunidades,
        "custom": True,
    }


def _criatura_nueva_guardada():
    cabecera("NUEVA CRIATURA (guardar)")
    nombre = input_str(f"{C.AMARILLO}Nombre: {C.RESET}", "Enemigo")
    if os.path.exists(ruta_criatura(nombre)):
        if not confirmar(f"{C.ROJO}Ya existe '{nombre}'. ¿Sobrescribir?{C.RESET}"):
            return None
    ac = input_int(f"{C.AMARILLO}AC: {C.RESET}", 15)

    stats = _pedir_stats_opcional()

    resistencias = _elegir_elementos("RESISTENCIAS")
    vulnerabilidades = _elegir_elementos("VULNERABILIDADES")
    inmunidades = _elegir_elementos("INMUNIDADES")

    criatura = {
        "nombre": nombre,
        "ac": ac,
        "stats": stats,
        "resistencias": resistencias,
        "vulnerabilidades": vulnerabilidades,
        "inmunidades": inmunidades,
    }
    guardar_criatura(criatura)
    print(f"{C.VERDE}[+] Guardada como '{nombre}'{C.RESET}")
    return criatura


def pedir_criatura():
    while True:
        cabecera("CRIATURA OBJETIVO")
        print(f"  {C.GRIS}[1] Cargar criatura guardada")
        print(f"  {C.GRIS}[2] Criatura custom (un solo uso)")
        print(f"  {C.GRIS}[3] Criatura nueva (guardar)")
        print(f"  {C.ROJO}[X]{C.RESET} Cancelar")
        op = input(f"\n{C.CIAN}└──╼ {C.RESET}").strip().upper()

        if op == "X":
            return None

        if op == "1":
            criaturas = listar_criaturas()
            if not criaturas:
                print(f"{C.AMARILLO}[!] No hay criaturas guardadas{C.RESET}")
                pausa()
                continue
            idx = menu("CRIATURAS GUARDADAS", criaturas)
            if idx is None:
                continue
            return cargar_criatura(criaturas[idx])

        if op == "2":
            return _criatura_custom()

        if op == "3":
            c = _criatura_nueva_guardada()
            if c:
                return c
            continue


def aplicar_resistencias(dano_base, elemento, criatura):
    if not criatura:
        return dano_base
    if elemento in criatura.get("inmunidades", []):
        return 0
    if elemento in criatura.get("resistencias", []):
        return dano_base // 2
    if elemento in criatura.get("vulnerabilidades", []):
        return dano_base * 2
    return dano_base


def tiene_stat(criatura, stat):
    if not criatura:
        return False
    return stat in (criatura.get("stats") or {})


def bono_salvacion_criatura(criatura, stat):
    if not criatura or not criatura.get("stats"):
        return 0
    info = criatura["stats"].get(stat)
    if not info:
        return 0
    return info.get("mod", 0)


def pedir_stat_faltante(criatura, stat):
    if tiene_stat(criatura, stat):
        return True
    cabecera(f"STAT FALTANTE: {stat}")
    print(f"  La criatura '{criatura.get('nombre', '?')}' no tiene definida")
    print(f"  la stat '{stat}', necesaria para calcular su salvación.\n")
    print(f"  {C.GRIS}[1] Definir ahora (mod manual)")
    print(f"  {C.GRIS}[2] Asumir mod 0 (sin bono)")
    print(f"  {C.ROJO}[X]{C.RESET} Cancelar acción")
    op = input(f"\n{C.CIAN}└──╼ {C.RESET}").strip().upper()

    if op == "X":
        return False
    if op == "1":
        mod = input_int(f"{C.AMARILLO}Modificador de {stat}: {C.RESET}", 0)
        criatura.setdefault("stats", {})[stat] = {"mod": mod}
        return True
    if op == "2":
        criatura.setdefault("stats", {})[stat] = {"mod": 0}
        return True
    return False


def describir_criatura(criatura):
    if not criatura:
        return "—"
    partes = [f"{criatura['nombre']} (AC {criatura['ac']})"]
    if criatura.get("resistencias"):
        partes.append(f"resiste: {', '.join(criatura['resistencias'])}")
    if criatura.get("vulnerabilidades"):
        partes.append(f"vulnerable: {', '.join(criatura['vulnerabilidades'])}")
    if criatura.get("inmunidades"):
        partes.append(f"inmune: {', '.join(criatura['inmunidades'])}")
    return "  |  ".join(partes)