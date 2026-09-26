import os
import time
from ui import (C, banner, pausa, limpiar, menu, input_int, input_str,
                cabecera, subcabecera, confirmar)
from ficha import (listar_fichas, cargar_ficha, guardar_ficha,
                   eliminar_ficha, ficha_mostrar, ruta_ficha,
                   STATS)
from equipo import pedir_arma, pedir_conjuro
from combate import modulo_calcular_dano
from modulos import (modulo_salvaciones, modulo_test_impacto,
                     modulo_probabilidad, modulo_guia, modulo_criaturas)


def _config_conjuros_ficha():
    cabecera("CD DE CONJUROS")
    print(f"  {C.GRIS}Se aplica a TODOS tus conjuros.{C.RESET}\n")
    print(f"  {C.VERDE}[1]{C.RESET} Calculada (8 + competencia + stat + bono extra)")
    print(f"  {C.VERDE}[2]{C.RESET} Manual (la pongo yo)")
    modo_cd = input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "1")

    if modo_cd == "2":
        cd_manual = input_int(f"  {C.AMARILLO}CD: {C.RESET}", 15)
        cd_stat = "Inteligencia"
        cd_extra = 0
    else:
        cd_manual = 15
        print(f"  {C.GRIS}Stat usada para la CD:{C.RESET}")
        for i, s in enumerate(STATS, 1):
            print(f"    [{i}] {s}")
        try:
            idx = int(input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "4")) - 1
            cd_stat = STATS[idx]
        except (ValueError, IndexError):
            cd_stat = "Inteligencia"
        cd_extra = input_int(f"  {C.AMARILLO}Bono extra (0 si no): {C.RESET}", 0)

    cabecera("ATAQUE DE CONJUROS")
    print(f"  {C.VERDE}[1]{C.RESET} Calculado (competencia + stat + bono extra)")
    print(f"  {C.VERDE}[2]{C.RESET} Manual (lo pongo yo)")
    modo_atk = input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "1")

    if modo_atk == "2":
        atk_manual = input_int(f"  {C.AMARILLO}Bono de ataque: {C.RESET}", 5)
        atk_stat = "Inteligencia"
        atk_extra = 0
    else:
        atk_manual = 5
        print(f"  {C.GRIS}Stat usada para el ataque:{C.RESET}")
        for i, s in enumerate(STATS, 1):
            print(f"    [{i}] {s}")
        try:
            idx = int(input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "4")) - 1
            atk_stat = STATS[idx]
        except (ValueError, IndexError):
            atk_stat = "Inteligencia"
        atk_extra = input_int(f"  {C.AMARILLO}Bono extra (0 si no): {C.RESET}", 0)

    return {
        "cd_conjuros_modo": "manual" if modo_cd == "2" else "calculada",
        "cd_conjuros_base": cd_manual,
        "cd_conjuros_stat": cd_stat,
        "cd_conjuros_bono_extra": cd_extra,
        "atk_conjuros_modo": "manual" if modo_atk == "2" else "calculada",
        "atk_conjuros_manual": atk_manual,
        "atk_conjuros_stat": atk_stat,
        "atk_conjuros_bono_extra": atk_extra,
    }


def ficha_nueva():
    cabecera("CREAR FICHA")
    nombre = input_str(f"{C.AMARILLO}Nombre de la ficha: {C.RESET}")
    if not nombre:
        return None
    if os.path.exists(ruta_ficha(nombre)):
        print(f"{C.ROJO}[!] Ya existe una ficha con ese nombre{C.RESET}")
        return None

    bono_comp = input_int(f"{C.AMARILLO}Bono de competencia: {C.RESET}", 2)
    bono_ataque = input_int(f"{C.AMARILLO}Bono de ataque global: {C.RESET}", 5)
    ca = input_int(f"{C.AMARILLO}CA: {C.RESET}", 15)
    velocidad = input_int(f"{C.AMARILLO}Velocidad (pies): {C.RESET}", 30)
    crit_min = input_int(f"{C.AMARILLO}Umbral de crítico (20 por defecto): {C.RESET}", 20)
    crit_min = max(1, min(20, crit_min))

    subcabecera("STATS Y SALVACIONES")
    stats = {}
    for s in STATS:
        print(f"{C.AMARILLO}{s}:{C.RESET}")
        mod = input_int(f"  Modificador: ", 0)
        comp = confirmar("  ¿Competencia en salvación?")
        stats[s] = {"mod": mod, "comp": comp}

    cfg_conj = _config_conjuros_ficha()

    cabecera("ARMAS")
    print(f"  {C.GRIS}ENTER en nombre para terminar.{C.RESET}\n")
    armas = []
    i = 1
    while True:
        a = pedir_arma(i)
        if a is None:
            break
        armas.append(a)
        i += 1

    cabecera("CONJUROS")
    print(f"  {C.GRIS}ENTER en nombre para terminar.{C.RESET}\n")
    conjuros = []
    i = 1
    while True:
        cj = pedir_conjuro(i)
        if cj is None:
            break
        conjuros.append(cj)
        i += 1

    ficha = {
        "nombre": nombre,
        "bono_competencia": bono_comp,
        "bono_ataque": bono_ataque,
        "ca": ca,
        "velocidad": velocidad,
        "crit_min": crit_min,
        "stats": stats,
        "armas": armas,
        "conjuros": conjuros,
    }
    ficha.update(cfg_conj)
    return ficha


def _editar_lista_generica(ficha, clave, etiqueta):
    lista = ficha.get(clave, [])
    if not lista:
        print(f"{C.GRIS}No hay elementos.{C.RESET}")
        return pausa()
    items = [x['nombre'] for x in lista]
    idx = menu(f"ELIMINAR {etiqueta}", items, etiqueta_atras="Cancelar")
    if idx is None:
        return
    eliminado = lista.pop(idx)
    guardar_ficha(ficha)
    print(f"{C.VERDE}[+] Eliminado: {eliminado['nombre']}{C.RESET}")
    pausa()


def ficha_editar_equipo(ficha):
    while True:
        idx = menu("EDITAR EQUIPO", [
            "Eliminar arma",
            "Eliminar conjuro",
            "Añadir arma",
            "Añadir conjuro",
        ])
        if idx is None:
            return
        if idx == 0:
            _editar_lista_generica(ficha, 'armas', "ARMA")
        elif idx == 1:
            _editar_lista_generica(ficha, 'conjuros', "CONJURO")
        elif idx == 2:
            a = pedir_arma(len(ficha.get('armas', [])) + 1)
            if a:
                ficha.setdefault('armas', []).append(a)
                guardar_ficha(ficha)
                pausa()
        elif idx == 3:
            cj = pedir_conjuro(len(ficha.get('conjuros', [])) + 1)
            if cj:
                ficha.setdefault('conjuros', []).append(cj)
                guardar_ficha(ficha)
                pausa()


def ficha_editar_general(ficha):
    while True:
        idx = menu("EDITAR DATOS GENERALES", [
            "Umbral de crítico",
            "Velocidad",
            "CD de conjuros",
            "Ataque de conjuros",
        ])
        if idx is None:
            return
        if idx == 0:
            nuevo = input_str(f"{C.AMARILLO}Nuevo umbral de crítico: {C.RESET}", "")
            if nuevo:
                try:
                    ficha['crit_min'] = max(1, min(20, int(nuevo)))
                    guardar_ficha(ficha)
                except ValueError:
                    print(f"{C.ROJO}[!] Valor inválido{C.RESET}")
            pausa()
        elif idx == 1:
            nueva_vel = input_str(f"{C.AMARILLO}Nueva velocidad (pies): {C.RESET}", "")
            if nueva_vel:
                try:
                    ficha['velocidad'] = int(nueva_vel)
                    guardar_ficha(ficha)
                except ValueError:
                    print(f"{C.ROJO}[!] Valor inválido{C.RESET}")
            pausa()
        elif idx == 2:
            _editar_cd_conjuros(ficha)
        elif idx == 3:
            _editar_atk_conjuros(ficha)


def _editar_cd_conjuros(ficha):
    from ficha import cd_conjuros_efectiva
    cabecera("EDITAR CD DE CONJUROS")
    print(f"  CD actual: {cd_conjuros_efectiva(ficha)} ({ficha.get('cd_conjuros_modo')})\n")
    print(f"  {C.VERDE}[1]{C.RESET} Calculada")
    print(f"  {C.VERDE}[2]{C.RESET} Manual")
    op = input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "1")
    if op == "2":
        ficha['cd_conjuros_modo'] = 'manual'
        ficha['cd_conjuros_base'] = input_int(f"  {C.AMARILLO}CD: {C.RESET}", 15)
    else:
        ficha['cd_conjuros_modo'] = 'calculada'
        print(f"  {C.GRIS}Stat:{C.RESET}")
        for i, s in enumerate(STATS, 1):
            print(f"    [{i}] {s}")
        try:
            idx = int(input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "4")) - 1
            ficha['cd_conjuros_stat'] = STATS[idx]
        except (ValueError, IndexError):
            ficha['cd_conjuros_stat'] = "Inteligencia"
        ficha['cd_conjuros_bono_extra'] = input_int(f"  {C.AMARILLO}Bono extra: {C.RESET}", 0)
    guardar_ficha(ficha)
    pausa()


def _editar_atk_conjuros(ficha):
    from ficha import atk_conjuros_efectivo
    cabecera("EDITAR ATAQUE DE CONJUROS")
    print(f"  Ataque actual: +{atk_conjuros_efectivo(ficha)} ({ficha.get('atk_conjuros_modo')})\n")
    print(f"  {C.VERDE}[1]{C.RESET} Calculado")
    print(f"  {C.VERDE}[2]{C.RESET} Manual")
    op = input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "1")
    if op == "2":
        ficha['atk_conjuros_modo'] = 'manual'
        ficha['atk_conjuros_manual'] = input_int(f"  {C.AMARILLO}Bono: {C.RESET}", 5)
    else:
        ficha['atk_conjuros_modo'] = 'calculada'
        print(f"  {C.GRIS}Stat:{C.RESET}")
        for i, s in enumerate(STATS, 1):
            print(f"    [{i}] {s}")
        try:
            idx = int(input_str(f"  {C.AMARILLO}Elige: {C.RESET}", "4")) - 1
            ficha['atk_conjuros_stat'] = STATS[idx]
        except (ValueError, IndexError):
            ficha['atk_conjuros_stat'] = "Inteligencia"
        ficha['atk_conjuros_bono_extra'] = input_int(f"  {C.AMARILLO}Bono extra: {C.RESET}", 0)
    guardar_ficha(ficha)
    pausa()


def ficha_menu(nombre_ficha):
    while True:
        ficha = cargar_ficha(nombre_ficha)
        if not ficha:
            return
        idx = menu(f"GESTIÓN: {ficha['nombre']}", [
            "Ver ficha",
            "Editar equipo (armas/conjuros)",
            "Editar datos generales",
        ])
        if idx is None:
            return
        if idx == 0:
            ficha_mostrar(ficha)
        elif idx == 1:
            ficha_editar_equipo(ficha)
        elif idx == 2:
            ficha_editar_general(ficha)


def _eliminar_ficha_ui(fichas):
    idx = menu("ELIMINAR FICHA", fichas, etiqueta_atras="Cancelar")
    if idx is None:
        return
    nombre = fichas[idx]
    if confirmar(f"{C.ROJO}¿Eliminar '{nombre}'?{C.RESET}"):
        eliminar_ficha(nombre)
        print(f"{C.VERDE}[+] Eliminada{C.RESET}")
        time.sleep(0.5)


def seleccionar_ficha():
    while True:
        fichas = listar_fichas()
        opciones = list(fichas) + ["+ Crear nueva ficha"]
        if fichas:
            opciones.append("- Eliminar una ficha")
        idx = menu("SELECCIÓN DE FICHA", opciones)
        if idx is None:
            return None, None
        if idx < len(fichas):
            nombre = fichas[idx]
            f = cargar_ficha(nombre)
            if f:
                return nombre, f
        elif idx == len(fichas):
            # Crear ficha: la guardamos y entramos directamente
            f = ficha_nueva()
            if f:
                guardar_ficha(f)
                pausa()
                return f['nombre'], f
        else:
            _eliminar_ficha_ui(fichas)


def menu_jugador(nombre_ficha):
    while True:
        ficha = cargar_ficha(nombre_ficha)
        if not ficha:
            return
        banner()
        print(f"  {C.GRIS}Sesión: {C.VERDE}{ficha['nombre']}{C.RESET}\n")
        idx = menu("MENÚ PRINCIPAL", [
            "Calcular daño",
            "Prueba de salvación",
            "Test de impacto (¿me pegan?)",
            "Gestión de ficha",
            "Gestionar criaturas",
            "Calculadora de probabilidades",
            "Guía de uso",
            "Cambiar de ficha",
        ])
        if idx is None:
            return "salir"
        if idx == 0:
            modulo_calcular_dano(nombre_ficha, ficha)
        elif idx == 1:
            modulo_salvaciones(nombre_ficha, ficha)
        elif idx == 2:
            modulo_test_impacto(nombre_ficha, ficha)
        elif idx == 3:
            ficha_menu(nombre_ficha)
        elif idx == 4:
            modulo_criaturas()
        elif idx == 5:
            modulo_probabilidad()
        elif idx == 6:
            modulo_guia()
        elif idx == 7:
            return "cambiar"


def main():
    while True:
        nombre, ficha = seleccionar_ficha()
        if nombre is None:
            limpiar()
            print(f"{C.VERDE}[*] Cerrando sesión...{C.RESET}")
            time.sleep(0.4)
            print(f"{C.VERDE}[*] Que los dados te sean favorables.{C.RESET}")
            break
        resultado = menu_jugador(nombre)
        if resultado == "salir":
            limpiar()
            print(f"{C.VERDE}[*] Cerrando sesión...{C.RESET}")
            time.sleep(0.4)
            print(f"{C.VERDE}[*] Que los dados te sean favorables.{C.RESET}")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C.ROJO}[!] Sesión interrumpida{C.RESET}")