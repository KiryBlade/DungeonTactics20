from ui import (C, cabecera, subcabecera, pausa,
                limpiar, linea, barra_probabilidad, pct,
                input_int, input_str, menu, confirmar)
from dados import probabilidad_exito, preguntar_modo
from ficha import STATS, cargar_ficha, cd_conjuros_efectiva


def modulo_salvaciones(nombre_ficha, ficha):
    ficha = cargar_ficha(nombre_ficha)
    if not ficha:
        return pausa()

    items = []
    for s in STATS:
        info = ficha['stats'][s]
        bono = info['mod'] + (ficha['bono_competencia'] if info['comp'] else 0)
        items.append(f"{s:15s} {bono:+d}")
    idx = menu("PRUEBA DE SALVACIÓN — ELIGE STAT", items)
    if idx is None:
        return

    stat_nombre = STATS[idx]
    info = ficha['stats'][stat_nombre]
    bono_base = info['mod'] + (ficha['bono_competencia'] if info['comp'] else 0)

    cabecera(f"SALVACIÓN DE {stat_nombre.upper()}")
    print(f"  Bono base: {C.VERDE}{bono_base:+d}{C.RESET}\n")
    bono_extra_str = input_str(f"{C.AMARILLO}Bono adicional (opcional): {C.RESET}", "")
    try:
        bono_extra = int(bono_extra_str) if bono_extra_str else 0
    except ValueError:
        bono_extra = 0
    bono_total = bono_base + bono_extra

    modo = preguntar_modo()
    cd = input_int(f"{C.AMARILLO}CD: {C.RESET}", None)
    if cd is None:
        return

    p_exito = probabilidad_exito(bono_total, cd, modo, ataque=False)
    p_fallo = 1 - p_exito

    cabecera("RESULTADO")
    print(f"  Salvación: {C.AMARILLO}{stat_nombre}{C.RESET}")
    print(f"  Bono total: {C.AMARILLO}{bono_total:+d}{C.RESET}   CD: {C.AMARILLO}{cd}{C.RESET}   Modo: {C.AMARILLO}{modo.upper()}{C.RESET}")
    linea()
    print()
    print(f"    Éxito  {barra_probabilidad(p_exito)}  {C.VERDE}{pct(p_exito):3d}%{C.RESET}")
    print(f"    Fallo  {barra_probabilidad(p_fallo)}  {C.ROJO}{pct(p_fallo):3d}%{C.RESET}")
    print()
    pausa()


def modulo_test_impacto(nombre_ficha, ficha):
    ficha = cargar_ficha(nombre_ficha)
    if not ficha:
        return pausa()

    cabecera("TEST DE IMPACTO")
    print(f"  Tu CA base: {C.AMARILLO}{ficha['ca']}{C.RESET}\n")

    bono_ataque_enemigo = input_int(f"{C.AMARILLO}Bono de ataque enemigo: {C.RESET}", None)
    if bono_ataque_enemigo is None:
        return

    bono_ca_str = input_str(f"{C.AMARILLO}Bono de CA (opcional): {C.RESET}", "")
    try:
        bono_ca = int(bono_ca_str) if bono_ca_str else 0
    except ValueError:
        bono_ca = 0

    ca_efectiva = ficha['ca'] + bono_ca
    modo = preguntar_modo()
    p_impacto = probabilidad_exito(bono_ataque_enemigo, ca_efectiva, modo, ataque=True)
    p_fallo = 1 - p_impacto

    cabecera("RESULTADO")
    print(f"  CA efectiva: {C.AMARILLO}{ca_efectiva}{C.RESET}   Bono enemigo: {C.AMARILLO}+{bono_ataque_enemigo}{C.RESET}")
    print(f"  Modo: {C.AMARILLO}{modo.upper()}{C.RESET}")
    linea()
    print()
    print(f"    Te pega   {barra_probabilidad(p_impacto)}  {C.ROJO}{pct(p_impacto):3d}%{C.RESET}")
    print(f"    Te falla  {barra_probabilidad(p_fallo)}  {C.VERDE}{pct(p_fallo):3d}%{C.RESET}")
    print()
    pausa()


def modulo_probabilidad():
    cabecera("CALCULADORA DE PROBABILIDADES")
    bono = input_int(f"{C.AMARILLO}Bono: {C.RESET}", None)
    cd = input_int(f"{C.AMARILLO}CD/AC: {C.RESET}", None)
    if bono is None or cd is None:
        return pausa()

    print()
    for modo in ["normal", "ventaja", "desventaja"]:
        p = probabilidad_exito(bono, cd, modo, ataque=True)
        print(f"  {modo.capitalize():12s} {barra_probabilidad(p)} {pct(p):3d}%")
    pausa()


def modulo_criaturas():
    from criatura import (listar_criaturas, cargar_criatura,
                          eliminar_criatura, _criatura_nueva_guardada)
    while True:
        criaturas = listar_criaturas()
        opciones = ["+ Crear criatura"]
        if criaturas:
            opciones += criaturas
        idx = menu("CRIATURAS GUARDADAS", opciones)
        if idx is None:
            return
        if idx == 0:
            _criatura_nueva_guardada()
            pausa()
        else:
            nombre = criaturas[idx - 1]
            c = cargar_criatura(nombre)
            cabecera(f"CRIATURA: {nombre}")
            print(f"  AC: {c.get('ac', '—')}")
            if c.get("stats"):
                print(f"  Stats:")
                for s, info in c["stats"].items():
                    print(f"    {s:15s} {info.get('mod', 0):+d}")
            if c.get("resistencias"):
                print(f"  Resiste: {', '.join(c['resistencias'])}")
            if c.get("vulnerabilidades"):
                print(f"  Vulnerable: {', '.join(c['vulnerabilidades'])}")
            if c.get("inmunidades"):
                print(f"  Inmune: {', '.join(c['inmunidades'])}")
            print()
            if confirmar(f"{C.ROJO}¿Eliminar '{nombre}'?{C.RESET}"):
                eliminar_criatura(nombre)
                print(f"{C.VERDE}[+] Eliminada{C.RESET}")
            pausa()


def modulo_guia():
    cabecera("GUÍA DE USO")
    secciones = [
        ("FICHAS", [
            "Varias fichas en 'fichas/'. Eliges una al iniciar.",
            "CD y ataque de conjuros globales (calculados o manuales).",
        ]),
        ("ARMAS Y CONJUROS", [
            "Armas: 3 modos de bono de ataque (global / stat+comp / manual).",
            "Conjuros: salvación o ataque, elemento, área, mitad si salva.",
            "Se pueden mezclar en el mismo turno.",
        ]),
        ("ELEMENTOS", [
            "13 tipos: ácido, contundente, cortante, fuego, frío,",
            "fuerza, necrótico, perforante, psíquico, radiante,",
            "relámpago, trueno, veneno.",
            "Se usan para aplicar resistencias/vulnerabilidades.",
        ]),
        ("CRIATURAS", [
            "Guardadas o custom (un solo uso).",
            "AC + stats opcionales + resistencias/vulnerabilidades/inmunidades.",
            "Si falta la stat de salvación, te la pide al calcular.",
        ]),
        ("CALCULAR DAÑO", [
            "1. Eliges criatura objetivo (guardada o custom).",
            "2. Número de acciones (puedes mezclar armas y conjuros).",
            "3. Por acción: arma / conjuro / custom.",
            "4. GWM/SS, daño extra, modo.",
            "5. Resultado con min/prom/max.",
        ]),
        ("REGLAS", [
            "20 natural siempre impacta, 1 natural siempre falla.",
            "En crítico solo los dados se duplican.",
            "Resistencia: mitad. Vulnerabilidad: doble. Inmunidad: 0.",
            "El máximo mostrado es SIN críticos.",
        ]),
    ]
    for titulo, lineas in secciones:
        subcabecera(titulo)
        for l in lineas:
            print(f"   {l}")
        print()
    pausa()