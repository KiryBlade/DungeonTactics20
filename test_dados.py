"""
Tests para dados.py y lógica de resistencias.
Ejecutar: python test_dados.py
"""
from dados import (parsear_dano, min_dados, max_dados, promedio_dano,
                   floor0, probabilidad_exito, probabilidad_critico)
from criatura import aplicar_resistencias


PASADOS = 0
FALLADOS = 0


def check(nombre, cond, esperado=None, obtenido=None):
    global PASADOS, FALLADOS
    if cond:
        PASADOS += 1
        print(f"  [OK] {nombre}")
    else:
        FALLADOS += 1
        print(f"  [XX] {nombre}")
        if esperado is not None:
            print(f"       esperado: {esperado}")
            print(f"       obtenido: {obtenido}")


def casi_igual(a, b, tol=0.001):
    return abs(a - b) < tol


# ------------------------------------------------------------------
# parsear_dano
# ------------------------------------------------------------------

def test_parsear_dano():
    print("\n=== parsear_dano ===")
    d, b = parsear_dano("1d8+5")
    check("1d8+5 -> dados [(8,1)]", d == [(8, 1)])
    check("1d8+5 -> bono 5", b == 5)

    d, b = parsear_dano("2d6+3d4+2")
    check("2d6+3d4+2 -> dados [(6,2),(4,3)]", d == [(6, 2), (4, 3)])
    check("2d6+3d4+2 -> bono 2", b == 2)

    d, b = parsear_dano("1d8-2")
    check("1d8-2 -> bono -2", b == -2)

    d, b = parsear_dano("1d12+8+9d6")
    check("1d12+8+9d6 -> 2 dados + bono 8", len(d) == 2 and b == 8)

    d, b = parsear_dano("")
    check("vacío -> sin dados, bono 0", d == [] and b == 0)

    # NUEVO: dados negativos
    d, b = parsear_dano("1d8-1d4")
    check("1d8-1d4 -> [(8,1),(4,-1)]", d == [(8, 1), (4, -1)])
    check("1d8-1d4 -> bono 0", b == 0)

    d, b = parsear_dano("1d10-2d6+3")
    check("1d10-2d6+3 -> [(10,1),(6,-2)]", d == [(10, 1), (6, -2)])
    check("1d10-2d6+3 -> bono 3", b == 3)

    d, b = parsear_dano("-1d6")
    check("-1d6 -> [(6,-1)]", d == [(6, -1)])
    check("-1d6 -> bono 0", b == 0)


# ------------------------------------------------------------------
# min / max / promedio
# ------------------------------------------------------------------

def test_min_max_prom():
    print("\n=== min/max/promedio ===")
    d, b = parsear_dano("1d8+5")
    check("min 1d8+5 = 6", min_dados(d) + b == 6)
    check("max 1d8+5 = 13", max_dados(d) + b == 13)
    check("prom 1d8+5 = 9.5", casi_igual(promedio_dano(d, b), 9.5))

    d, b = parsear_dano("2d6")
    check("min 2d6 = 2", min_dados(d) == 2)
    check("max 2d6 = 12", max_dados(d) == 12)
    check("prom 2d6 = 7", casi_igual(promedio_dano(d, 0), 7.0))

    # NUEVO: dados negativos
    d, b = parsear_dano("1d8-1d4")
    check("min 1d8-1d4 = -3", min_dados(d) == -3)
    check("max 1d8-1d4 = 7", max_dados(d) == 7)
    check("prom 1d8-1d4 = 2.0", casi_igual(promedio_dano(d, 0), 2.0))

    # NUEVO: total negativo
    d, b = parsear_dano("1d4-10")
    check("prom 1d4-10 = -7.5", casi_igual(promedio_dano(d, b), -7.5))

    # NUEVO: floor0 corta negativos
    check("floor0(-7.5) = 0", floor0(-7.5) == 0)
    check("floor0(0) = 0", floor0(0) == 0)
    check("floor0(3.9) = 3", floor0(3.9) == 3)
    check("floor0(9.5) = 9", floor0(9.5) == 9)


# ------------------------------------------------------------------
# probabilidad_exito
# ------------------------------------------------------------------

def test_probabilidad_exito():
    print("\n=== probabilidad_exito (ataque) ===")
    p = probabilidad_exito(bono=5, cd=15, modo="normal", ataque=True)
    check("bono 5 vs AC 15 normal = 0.55", casi_igual(p, 0.55), 0.55, p)

    p = probabilidad_exito(bono=5, cd=15, modo="ventaja", ataque=True)
    check("bono 5 vs AC 15 ventaja = 0.7975", casi_igual(p, 0.7975), 0.7975, p)

    p = probabilidad_exito(bono=5, cd=15, modo="desventaja", ataque=True)
    check("bono 5 vs AC 15 desventaja = 0.3025", casi_igual(p, 0.3025), 0.3025, p)

    p = probabilidad_exito(bono=0, cd=30, modo="normal", ataque=True)
    check("AC 30 normal = 5%", casi_igual(p, 0.05), 0.05, p)

    p = probabilidad_exito(bono=0, cd=30, modo="ventaja", ataque=True)
    check("AC 30 ventaja = 9.75%", casi_igual(p, 0.0975), 0.0975, p)

    p = probabilidad_exito(bono=0, cd=30, modo="desventaja", ataque=True)
    check("AC 30 desventaja = 0.25%", casi_igual(p, 0.0025), 0.0025, p)

    # NUEVO: salvación (ataque=False), 1 natural NO es éxito automático
    p = probabilidad_exito(bono=0, cd=25, modo="normal", ataque=False)
    check("salvación CD 25 normal = 0%", casi_igual(p, 0.0), 0.0, p)


# ------------------------------------------------------------------
# probabilidad_critico
# ------------------------------------------------------------------

def test_probabilidad_critico():
    print("\n=== probabilidad_critico ===")
    p = probabilidad_critico(modo="normal", umbral=20, bono=10, ac=15)
    check("bono 10 vs AC 15 umbral 20 = 5%", casi_igual(p, 0.05), 0.05, p)

    p = probabilidad_critico(modo="normal", umbral=19, bono=10, ac=15)
    check("bono 10 vs AC 15 umbral 19 = 10%", casi_igual(p, 0.10), 0.10, p)

    p = probabilidad_critico(modo="normal", umbral=20, bono=5, ac=30)
    check("AC 30 umbral 20 = 5% (bug fix)", casi_igual(p, 0.05), 0.05, p)

    p = probabilidad_critico(modo="normal", umbral=19, bono=5, ac=30)
    check("AC 30 umbral 19 = 5% (bug fix)", casi_igual(p, 0.05), 0.05, p)

    p = probabilidad_critico(modo="ventaja", umbral=20, bono=10, ac=15)
    check("umbral 20 ventaja = 9.75%", casi_igual(p, 0.0975), 0.0975, p)

    p = probabilidad_critico(modo="desventaja", umbral=20, bono=10, ac=15)
    check("umbral 20 desventaja = 0.25%", casi_igual(p, 0.0025), 0.0025, p)

    # NUEVO: desventaja con necesario > 20 (solo 20+20 en ambos dados)
    p = probabilidad_critico(modo="desventaja", umbral=20, bono=0, ac=30)
    check("AC 30 umbral 20 desventaja = 0.25%", casi_igual(p, 0.0025), 0.0025, p)

    p = probabilidad_critico(modo="desventaja", umbral=19, bono=0, ac=30)
    check("AC 30 umbral 19 desventaja = 0.25%", casi_igual(p, 0.0025), 0.0025, p)

    # NUEVO: ventaja con necesario > 20
    p = probabilidad_critico(modo="ventaja", umbral=20, bono=0, ac=30)
    check("AC 30 umbral 20 ventaja = 9.75%", casi_igual(p, 0.0975), 0.0975, p)

    # NUEVO: umbral 1 (edge case, sería siempre crítico si impactas)
    p = probabilidad_critico(modo="normal", umbral=1, bono=10, ac=15)
    # necesario = 5, umbral_efectivo = max(1, min(5,20), 2) = 5
    # exitos_individuales = (21-5)/20 = 0.80
    check("umbral 1 normal = 80% (limitado por impacto)",
          casi_igual(p, 0.80), 0.80, p)


# ------------------------------------------------------------------
# aplicar_resistencias
# ------------------------------------------------------------------

def test_aplicar_resistencias():
    print("\n=== aplicar_resistencias ===")
    criatura = {
        "resistencias": ["fuego"],
        "vulnerabilidades": ["frío"],
        "inmunidades": ["veneno"],
    }
    check("fuego (resistencia) 100 -> 50",
          aplicar_resistencias(100, "fuego", criatura) == 50)
    check("frío (vulnerable) 100 -> 200",
          aplicar_resistencias(100, "frío", criatura) == 200)
    check("veneno (inmune) 100 -> 0",
          aplicar_resistencias(100, "veneno", criatura) == 0)
    check("cortante (neutral) 100 -> 100",
          aplicar_resistencias(100, "cortante", criatura) == 100)
    check("sin criatura -> daño intacto",
          aplicar_resistencias(100, "fuego", None) == 100)

    # NUEVO: impar con resistencia (floor)
    check("fuego (resistencia) 101 -> 50 (floor)",
          aplicar_resistencias(101, "fuego", criatura) == 50)

    # NUEVO: 0 con vulnerabilidad sigue siendo 0
    check("frío (vulnerable) 0 -> 0",
          aplicar_resistencias(0, "frío", criatura) == 0)

    check("criatura sin resistencias -> 100",
          aplicar_resistencias(100, "fuego", {}) == 100)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    test_parsear_dano()
    test_min_max_prom()
    test_probabilidad_exito()
    test_probabilidad_critico()
    test_aplicar_resistencias()

    print(f"\n{'=' * 40}")
    print(f"PASADOS: {PASADOS}")
    print(f"FALLADOS: {FALLADOS}")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    main()