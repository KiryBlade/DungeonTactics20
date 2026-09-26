# DungeonTactics20

Calculadora de combate para D&D 5e. Funciona en terminal, sin dependencias externas.

> ⚠️ **DEMO en desarrollo.** Esta es una versión temprana con lo esencial funcionando, pero el proyecto está en construcción activa. Pueden cambiar formatos de archivo, aparecer bugs o faltar funciones. Úsala con eso en mente.

---

## Índice

- [¿Qué hace?](#qué-hace)
- [Instalación](#instalación)
- [Estructura](#estructura)
- [Uso básico](#uso-básico)
- [Notación de dados](#notación-de-dados)
- [Tipos de daño](#tipos-de-daño)
- [Reglas implementadas](#reglas-implementadas)
- [Módulos disponibles](#módulos-disponibles)
- [Tests](#tests)
- [Persistencia](#persistencia)
- [Roadmap](#roadmap)
- [Estado](#estado)

---

## ¿Qué hace?

- Calcula el daño esperado de un turno completo (mínimo, promedio, máximo)
- Muestra la probabilidad de impacto, fallo y crítico de cada acción
- Tiene en cuenta resistencias, vulnerabilidades e inmunidades por tipo de daño
- Permite mezclar ataques con armas y conjuros en el mismo turno
- Calcula probabilidades de salvación contra una CD
- Guarda fichas de personaje y criaturas para reutilizarlas

---

## Instalación

Solo necesitas Python 3.8 o superior. No hay dependencias externas.

```bash
git clone <url-del-repo>
cd DungeonTactics20
python main.py
```

---

## Estructura

```
DungeonTactics20/
├── main.py              # Menú principal
├── ui.py                # Colores, menús, entradas
├── dados.py             # Parseo de notación de dados y probabilidades
├── ficha.py             # Gestión de fichas de personaje
├── equipo.py            # Armas y conjuros
├── criatura.py          # Criaturas (guardadas y custom)
├── combate.py           # Cálculo de daño por turno
├── modulos.py           # Salvaciones, test de impacto, calculadora
├── test_dados.py        # Tests de la lógica de dados
├── fichas/              # (auto) Personajes guardados en JSON
└── criaturas/           # (auto) Criaturas guardadas en JSON
```

---

## Uso básico

### Crear una ficha

Al arrancar, elige **"+ Crear nueva ficha"**. Te pide:

- Nombre, bonos, CA, velocidad, umbral de crítico
- Los 6 stats con modificador y competencia en salvación
- CD y ataque de conjuros (calculados o manuales)
- Armas (nombre, daño, elemento, bono de ataque)
- Conjuros (nombre, daño, elemento, tipo, área, salvación)

### Calcular daño

Elige **"Calcular daño"**, y el flujo es:

1. Elige criatura objetivo (guardada, custom o nueva)
2. Indica cuántas acciones haces este turno
3. Por cada acción: arma, conjuro o custom
4. Ajustes: GWM/SS, daño extra, modo (ventaja/desventaja)
5. Ves el resultado por acción y el resumen del turno

### Ejemplo de resultado

```
┌─ Acción 1/2: Espada de Quarion
    Elemento: frío
    Daño base: 1d8+1d6+7
    Bono ataque: +12  (VENTAJA)

    Impacto
      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░  99%
    Fallo
      ░░░░░░░░░░░░░░░░░░░░   1%

    Mínimo:   9
    Promedio: 15
    Máximo:   29

    Crítico:
      ▓▓░░░░░░░░░░░░░░░░░░  10%
      Daño sin crítico: ~15
      Daño con crítico: ~20
  └──────────────────────────────────────────────

RESUMEN DEL TURNO
    Mínimo:   9
    Promedio: 15
    Máximo:   29
```

---

## Notación de dados

Los daños se escriben con notación estándar:

| Notación | Significado |
|---|---|
| `1d8` | Un dado de 8 caras |
| `2d6+3` | Dos dados de 6 caras más 3 |
| `1d12+8+9d6` | Varios grupos de dados más bonos |
| `1d8-1d4` | Dados restados |

---

## Tipos de daño

Soporta los 13 tipos de D&D 5e:

```
ácido · contundente · cortante · fuego · frío · fuerza
necrótico · perforante · psíquico · radiante
relámpago · trueno · veneno
```

Cada arma y cada conjuro tiene su tipo. Al calcular daño contra una criatura, se aplica automáticamente:

- **Resistencia** → mitad del daño
- **Vulnerabilidad** → doble del daño
- **Inmunidad** → cero

---

## Reglas implementadas

- 20 natural siempre impacta, 1 natural siempre falla
- En crítico solo se duplican los dados, no los bonos fijos
- Los conjuros con salvación no hacen tirada de ataque ni crítico
- Si un conjuro tiene "mitad si salva", el daño esperado lo refleja
- El máximo mostrado **no** incluye críticos
- Si una criatura no tiene definida la stat de salvación que necesita un conjuro, te la pide

---

## Módulos disponibles

Desde el menú principal:

| Opción | Qué hace |
|---|---|
| Calcular daño | Turno completo con armas y/o conjuros |
| Prueba de salvación | Probabilidad de éxito contra una CD |
| Test de impacto | Con tu CA, ¿cuánto te pega un enemigo? |
| Gestión de ficha | Ver, editar armas, conjuros, datos |
| Gestionar criaturas | Listar, crear, borrar criaturas guardadas |
| Calculadora | Probabilidad genérica bono vs CD |
| Guía de uso | Resumen de todo lo anterior |

---

## Tests

```bash
python test_dados.py
```

Cubre parseo de notación de dados (incluyendo negativos), mínimos, máximos, promedios, probabilidades de impacto y crítico en normal/ventaja/desventaja, y aplicación de resistencias.

---

## Persistencia

Todo se guarda en JSON plano dentro de las carpetas `fichas/` y `criaturas/`. Puedes editarlos a mano, copiarlos entre dispositivos o versionarlos con git sin problema.

---

## Roadmap

Funciones planeadas para próximas versiones:

### Manuales

Biblioteca de conjuros, criaturas y equipo con paginación. Importables y editables, incluyendo contenido homebrew. Cada manual es una carpeta con subcarpetas de conjuros, criaturas y equipo.

### Interfaz gráfica

Versión con UI visual usando HTML embebido y ejecutable de escritorio para quienes no quieran usar la terminal. Misma lógica, otra presentación.

### Análisis de combates en tiempo real

Seguimiento de un combate en curso: estimación de la situación de cada enemigo a partir de lo observado, y sugerencias de jugadas según lo que se sabe. Solo usa información que el personaje podría conocer.

### Aprendizaje de partidas

Registro de combates anteriores para refinar estimaciones, corregir errores y adaptarse al estilo de cada jugador. Cuanto más se usa, mejor se ajusta.

### Exportación

Fichas y criaturas a PDF, texto plano y otros formatos.

---

## Estado

Proyecto personal en desarrollo activo. La base actual (cálculo de daño, fichas, criaturas) está estable y verificada con tests. Lo que viene encima todavía no está implementado.
