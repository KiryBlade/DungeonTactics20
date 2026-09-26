from ui import (C, cabecera, subcabecera, pausa,
                limpiar, bloque_ataque, cierre_bloque, barra_probabilidad,
                pct, input_int, input_str, menu, confirmar)
from dados import (parsear_dano, min_dados, max_dados, promedio_dano,
                   floor0, probabilidad_exito, probabilidad_critico, preguntar_modo)
from ficha import (calcular_bono_ataque_arma, cargar_ficha,
                   cd_conjuros_efectiva, atk_conjuros_efectivo)
from equipo import pedir_elemento
from criatura import (aplicar_resistencias, describir_criatura,
                      bono_salvacion_criatura, pedir_criatura,
                      pedir_stat_faltante)


def _elegir_accion():
    return menu("TIPO DE ACCIÓN", [
        "Ataque con arma",
        "Lanzar conjuro",
        "Acción custom",
    ])


def _elegir_de_lista(titulo, items):
    return menu(titulo, items)


def _config_arma(ficha, arma):
    return {
        "tipo": "arma",
        "nombre": arma['nombre'],
        "dano_str": arma['dano'],
        "elemento": arma.get('elemento', 'cortante'),
        "bono_ataque_base": calcular_bono_ataque_arma(arma, ficha),
        "arma": arma,
    }


def _config_conjuro(ficha, conj):
    return {
        "tipo": "conjuro",
        "subtipo": conj.get('tipo', 'salvacion'),
        "nombre": conj['nombre'],
        "dano_str": conj['dano'],
        "elemento": conj.get('elemento', 'fuerza'),
        "bono_ataque_base": atk_conjuros_efectivo(ficha),
        "conjuro": conj,
    }


def _config_custom(ficha):
    cabecera("ACCIÓN CUSTOM")
    nombre = input_str(f"{C.AMARILLO}Nombre: {C.RESET}", "Custom")
    dano_str = input_str(f"{C.AMARILLO}Daño: {C.RESET}")
    if not dano_str:
        return None
    elemento = pedir_elemento("fuerza")
    bono_atk = input_int(f"{C.AMARILLO}Bono de ataque: {C.RESET}", ficha['bono_ataque'])
    return {
        "tipo": "custom",
        "subtipo": "ataque",
        "nombre": nombre,
        "dano_str": dano_str,
        "elemento": elemento,
        "bono_ataque_base": bono_atk,
    }


def _elegir_objetivo(ficha, cfg):
    cabecera(f"CONFIGURAR: {cfg['nombre']}")
    gwm_on = False
    if cfg['tipo'] == 'arma':
        gwm_on = confirmar(f"{C.AMARILLO}¿GWM/SS?{C.RESET}")

    extra_str = input_str(f"{C.AMARILLO}Daño adicional (ENTER si no): {C.RESET}", "")

    modo = preguntar_modo()

    cfg['gwm'] = gwm_on
    cfg['extra_str'] = extra_str
    cfg['modo'] = modo
    return cfg


def _calcular_ataque(cfg, ficha, criatura):
    ac = criatura['ac'] if criatura else 15
    crit_min = ficha.get('crit_min', 20)

    bono_atk = cfg['bono_ataque_base']
    if cfg.get('gwm'):
        bono_atk -= 5
    cfg['bono_ataque_efectivo'] = bono_atk
    cfg['bono_dano_gwm'] = 10 if cfg.get('gwm') else 0

    dados, bono = parsear_dano(cfg['dano_str'])
    extra_str = cfg.get('extra_str', '')
    dados_extra, bono_extra = parsear_dano(extra_str) if extra_str else ([], 0)

    es_salvacion = (cfg['tipo'] == 'conjuro' and cfg.get('subtipo') == 'salvacion')

    if es_salvacion:
        cd = cd_conjuros_efectiva(ficha)
        stat_salv = cfg['conjuro']['stat_salvacion']
        if not pedir_stat_faltante(criatura, stat_salv):
            return None
        bono_salv_enemigo = bono_salvacion_criatura(criatura, stat_salv)
        p_enemigo_salva = probabilidad_exito(bono_salv_enemigo, cd,
                                              modo="normal", ataque=False)
        p_hit = 1 - p_enemigo_salva
        cfg['p_enemigo_salva'] = p_enemigo_salva
        cfg['cd_usada'] = cd
    else:
        p_hit = probabilidad_exito(bono_atk, ac, cfg['modo'], ataque=True)
        cfg['p_enemigo_salva'] = None
        cfg['cd_usada'] = None

    cfg['p_impacto'] = p_hit

    # ---- Daño base ----
    prom_dados = promedio_dano(dados, 0)
    prom_extra = promedio_dano(dados_extra, 0) if dados_extra else 0
    min_normal = (min_dados(dados) + bono + cfg['bono_dano_gwm']
                  + (min_dados(dados_extra) + bono_extra if dados_extra else 0))
    max_normal = (max_dados(dados) + bono + cfg['bono_dano_gwm']
                  + (max_dados(dados_extra) + bono_extra if dados_extra else 0))
    prom_normal = (prom_dados + bono + cfg['bono_dano_gwm']
                   + prom_extra + bono_extra)

    # ---- Daño en crítico: se duplican SOLO los dados, no los bonos ----
    min_crit = (min_dados(dados) * 2 + bono + cfg['bono_dano_gwm']
                + (min_dados(dados_extra) * 2 + bono_extra if dados_extra else 0))
    max_crit = (max_dados(dados) * 2 + bono + cfg['bono_dano_gwm']
                + (max_dados(dados_extra) * 2 + bono_extra if dados_extra else 0))
    prom_crit = (prom_dados * 2 + bono + cfg['bono_dano_gwm']
                 + prom_extra * 2 + bono_extra)

    # ---- Probabilidad de crítico ----
    if es_salvacion:
        p_crit = 0.0
    else:
        p_crit = probabilidad_critico(cfg['modo'], crit_min, bono_atk, ac)
    cfg['p_crit'] = p_crit

    # ---- Valores mostrados ----
    # min/max son extremos absolutos (incluyendo la posibilidad de crítico en max)
    min_hit = min_normal
    max_hit = max_crit
    # promedio mezclado (condicionado a impactar):  p(no crit)*prom_normal + p(crit)*prom_crit
    prom_mezcla = prom_normal * (1 - p_crit) + prom_crit * p_crit

    cfg['promedio_normal'] = prom_normal
    cfg['promedio_critico'] = prom_crit
    cfg['promedio_sin_crit'] = prom_normal   # alias explícito
    cfg['promedio_con_crit'] = prom_mezcla

    # ---- Mitad si salva ----
    if es_salvacion and cfg['conjuro'].get('mitad_si_salva'):
        p_salva = cfg.get('p_enemigo_salva', 0)
        factor = 1 - p_salva * 0.5
        prom_mezcla *= factor
        prom_normal *= factor
        prom_crit *= factor
        min_hit = min_hit // 2

    # ---- Aplicar resistencias ----
    elemento = cfg['elemento']
    cfg['minimo'] = aplicar_resistencias(floor0(min_hit), elemento, criatura)
    cfg['promedio'] = aplicar_resistencias(floor0(prom_mezcla), elemento, criatura)
    cfg['maximo'] = aplicar_resistencias(floor0(max_hit), elemento, criatura)

    cfg['dados'] = dados
    cfg['bono'] = bono
    cfg['dados_extra'] = dados_extra
    cfg['bono_extra'] = bono_extra
    return cfg


def _flujo_accion(ficha, armas, conjuros, idx, total):
    while True:
        tipo = _elegir_accion()
        if tipo is None:
            return None

        if tipo == 0:
            if not armas:
                print(f"{C.ROJO}[!] No tienes armas{C.RESET}")
                pausa()
                continue
            items = []
            for a in armas:
                bono = calcular_bono_ataque_arma(a, ficha)
                items.append(f"{a['nombre']:15s} {a['dano']:12s} {a.get('elemento', '—'):11s} +{bono} atk")
            k = _elegir_de_lista(f"ARMAS DISPONIBLES ({idx}/{total})", items)
            if k is None:
                continue
            cfg = _config_arma(ficha, armas[k])
            return _elegir_objetivo(ficha, cfg)

        elif tipo == 1:
            if not conjuros:
                print(f"{C.ROJO}[!] No tienes conjuros{C.RESET}")
                pausa()
                continue
            items = []
            for cj in conjuros:
                tipo_c = cj.get('tipo', 'salvacion')
                if tipo_c == 'salvacion':
                    salv = cj.get('stat_salvacion')
                    info = f"salv {salv}" if salv else "salvación"
                else:
                    info = "ataque"
                area = cj.get('area', '')
                area_txt = f" [{area}]" if area else ""
                items.append(f"{cj['nombre']:15s} {cj['dano']:12s} {cj.get('elemento', '—'):11s} {info}{area_txt}")
            k = _elegir_de_lista(f"CONJUROS DISPONIBLES ({idx}/{total})", items)
            if k is None:
                continue
            cfg = _config_conjuro(ficha, conjuros[k])
            return _elegir_objetivo(ficha, cfg)

        elif tipo == 2:
            cfg = _config_custom(ficha)
            if cfg is None:
                continue
            return _elegir_objetivo(ficha, cfg)


def _mostrar_resultado(ficha, criatura, ataques):
    cabecera("RESULTADO DEL TURNO")
    print(f"  {C.GRIS}Atacante:{C.RESET} {C.AMARILLO}{ficha['nombre']}{C.RESET}")
    print(f"  {C.GRIS}Objetivo:{C.RESET} {C.AMARILLO}{describir_criatura(criatura)}{C.RESET}")

    total_esperado = 0
    total_min = 0
    total_max = 0

    for i, a in enumerate(ataques):
        bloque_ataque(a['nombre'], i + 1, len(ataques))

        es_salvacion = (a['tipo'] == 'conjuro' and a.get('subtipo') == 'salvacion')

        print(f"    {C.GRIS}Elemento:{C.RESET} {a['elemento']}")
        print(f"    {C.GRIS}Daño base:{C.RESET} {a['dano_str']}")
        if a.get('extra_str'):
            print(f"    {C.GRIS}Extra:{C.RESET} {a['extra_str']}")
        if a.get('gwm'):
            print(f"    {C.MAGENTA}GWM/SS activo{C.RESET}")

        if es_salvacion:
            print(f"    {C.GRIS}CD conjuro:{C.RESET} {a['cd_usada']}   "
                  f"{C.GRIS}Salvación:{C.RESET} {a['conjuro']['stat_salvacion']}")
            p_salva = a.get('p_enemigo_salva', 0)
            p_falla = a['p_impacto']
            print()
            print(f"    {C.AMARILLO}Enemigo falla salvación{C.RESET}")
            print(f"      {barra_probabilidad(p_falla)}  {C.VERDE}{pct(p_falla):3d}%{C.RESET}")
            print(f"    {C.AMARILLO}Enemigo salva{C.RESET}")
            print(f"      {barra_probabilidad(p_salva)}  {C.ROJO}{pct(p_salva):3d}%{C.RESET}")
        else:
            print(f"    {C.GRIS}Bono ataque:{C.RESET} {a['bono_ataque_efectivo']:+d}  ({a['modo'].upper()})")
            p_hit = a['p_impacto']
            p_fail = 1 - p_hit
            print()
            print(f"    {C.AMARILLO}Impacto{C.RESET}")
            print(f"      {barra_probabilidad(p_hit)}  {C.VERDE}{pct(p_hit):3d}%{C.RESET}")
            print(f"    {C.AMARILLO}Fallo{C.RESET}")
            print(f"      {barra_probabilidad(p_fail)}  {C.ROJO}{pct(p_fail):3d}%{C.RESET}")

        print()
        print(f"    {C.GRIS}Mínimo:{C.RESET}   {C.VERDE}{a['minimo']}{C.RESET}")
        print(f"    {C.GRIS}Promedio:{C.RESET} {C.VERDE}{a['promedio']}{C.RESET}")
        print(f"    {C.GRIS}Máximo:{C.RESET}   {C.VERDE}{a['maximo']}{C.RESET}")

        if not es_salvacion:
            print()
            print(f"    {C.GRIS}Crítico:{C.RESET}   "
                  f"{barra_probabilidad(a['p_crit'])}  {C.MAGENTA}{pct(a['p_crit']):3d}%{C.RESET}")
            print(f"      {C.GRIS}Daño sin crítico:{C.RESET} ~{floor0(a['promedio_sin_crit'])}")
            print(f"      {C.GRIS}Daño con crítico:{C.RESET} ~{floor0(a['promedio_critico'])}")

        cierre_bloque()

        if es_salvacion:
            total_esperado += a['promedio']
        else:
            total_esperado += a['p_impacto'] * a['promedio']
        total_min += a['minimo']
        total_max += a['maximo']

    print(f"\n{C.CIAN}  ╔════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CIAN}  ║  {C.NEGRITA}RESUMEN DEL TURNO{C.CIAN}                          ║{C.RESET}")
    print(f"{C.CIAN}  ╚════════════════════════════════════════════╝{C.RESET}\n")

    print(f"    {C.AMARILLO}Mínimo:   {C.VERDE}{total_min}{C.RESET}")
    print(f"    {C.AMARILLO}Promedio: {C.VERDE}{floor0(total_esperado)}{C.RESET}")
    print(f"    {C.AMARILLO}Máximo:   {C.VERDE}{total_max}{C.RESET}")
    print()


def modulo_calcular_dano(nombre_ficha, ficha):
    ficha = cargar_ficha(nombre_ficha)
    if not ficha:
        return pausa()

    cabecera("CALCULAR DAÑO")
    print(f"  Personaje: {C.AMARILLO}{ficha['nombre']}{C.RESET}")
    print(f"  Crítico en: {C.AMARILLO}{ficha.get('crit_min', 20)}-20{C.RESET}")
    print(f"  CD conjuros: {C.AMARILLO}{cd_conjuros_efectiva(ficha)}{C.RESET}")
    print(f"  Atk conjuros: {C.AMARILLO}+{atk_conjuros_efectivo(ficha)}{C.RESET}\n")

    armas = ficha.get('armas', [])
    conjuros = ficha.get('conjuros', [])
    if not armas and not conjuros:
        print(f"{C.ROJO}[!] No hay armas ni conjuros en la ficha{C.RESET}")
        return pausa()

    criatura = pedir_criatura()
    if criatura is None:
        return

    cabecera("ACCIÓN DEL TURNO")
    n_acciones = input_int(f"{C.AMARILLO}¿Cuántas acciones este turno? {C.RESET}", 1)

    ataques = []
    for i in range(n_acciones):
        cfg = _flujo_accion(ficha, armas, conjuros, i + 1, n_acciones)
        if cfg is None:
            if not ataques:
                return
            break
        ataques.append(cfg)

    if not ataques:
        return

    for cfg in ataques:
        resultado = _calcular_ataque(cfg, ficha, criatura)
        if resultado is None:
            return pausa()

    _mostrar_resultado(ficha, criatura, ataques)
    pausa()