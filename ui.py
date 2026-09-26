import time


class C:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIAN = '\033[96m'
    BLANCO = '\033[97m'
    GRIS = '\033[90m'
    RESET = '\033[0m'
    NEGRITA = '\033[1m'


BAR_FILL = "▓"
BAR_EMPTY = "░"
ANCHO_BARRA = 20


def limpiar():
    # ANSI: borra toda la pantalla (2J) y mueve cursor arriba-izq (H)
    print("\033[2J\033[H", end="", flush=True)


def banner():
    limpiar()
    print(f"{C.CIAN}")
    print("  ╔═══════════════════════════════════════════════╗")
    print("  ║            DungeonsTactics20                  ║")
    print("  ║                    DEMO                       ║")
    print("  ╚═══════════════════════════════════════════════╝")
    print(f"{C.RESET}")


def pausa():
    input(f"\n{C.GRIS}[ ENTER para continuar ]{C.RESET}")


def linea(ancho=48):
    print(f"{C.GRIS}{'─' * ancho}{C.RESET}")


def cabecera(titulo):
    limpiar()
    print(f"\n{C.CIAN}╔═══ {titulo} ═══╗{C.RESET}\n")


def subcabecera(titulo):
    print(f"{C.AMARILLO}▸ {titulo}{C.RESET}")


def bloque_ataque(nombre, idx, total):
    print(f"\n{C.CIAN}  ┌─ Acción {idx}/{total}: {nombre}{C.RESET}")


def cierre_bloque():
    print(f"{C.CIAN}  └{'─' * 46}{C.RESET}")


def barra_probabilidad(p, ancho=ANCHO_BARRA):
    p = max(0.0, min(1.0, p))
    llenos = int(round(p * ancho))
    color = C.VERDE if p > 0.7 else (C.AMARILLO if p > 0.4 else C.ROJO)
    return f"{color}{BAR_FILL * llenos}{C.GRIS}{BAR_EMPTY * (ancho - llenos)}{C.RESET}"


def pct(p):
    return int(round(p * 100))


def input_int(prompt, default=None, permitir_vacio=True):
    while True:
        v = input(prompt).strip()
        if v == "" and default is not None:
            return default
        if v == "" and permitir_vacio:
            return None
        try:
            return int(v)
        except ValueError:
            print(f"{C.ROJO}[!] Introduce un número válido{C.RESET}")


def input_str(prompt, default=None):
    v = input(prompt).strip()
    if v == "" and default is not None:
        return default
    return v


def confirmar(prompt):
    return input(f"{C.AMARILLO}{prompt} (s/n): {C.RESET}").strip().lower() == "s"


def menu(titulo, opciones, permitir_atras=True, etiqueta_atras="Atrás"):
    while True:
        cabecera(titulo)
        for i, op in enumerate(opciones, 1):
            print(f"  {C.VERDE}[{i}]{C.RESET} {op}")
        if permitir_atras:
            print(f"\n  {C.ROJO}[X]{C.RESET} {etiqueta_atras}")
        op = input(f"\n{C.CIAN}└──╼ {C.RESET}").strip().upper()
        if op == "X" and permitir_atras:
            return None
        if op.isdigit():
            idx = int(op) - 1
            if 0 <= idx < len(opciones):
                return idx
        print(f"{C.ROJO}[!] Opción no válida{C.RESET}")
        time.sleep(0.4)


def pedir_de_lista(titulo, items, permitir_atras=True, etiqueta_atras="Atrás"):
    return menu(titulo, items, permitir_atras, etiqueta_atras)