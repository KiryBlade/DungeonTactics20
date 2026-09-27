# DragonsTactics

Calculadora de combate para D&D 5e. Interfaz web con ventana nativa opcional mediante pywebview.

> **Estado:** demo en desarrollo activo. El formato de datos es provisional y puede cambiar entre versiones.

---

## Índice

- [Qué es](#qué-es)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Notación de dados](#notación-de-dados)
- [Tipos de daño](#tipos-de-daño)
- [Reglas implementadas](#reglas-implementadas)
- [API](#api)
- [Tests](#tests)
- [Persistencia](#persistencia)
- [Roadmap](#roadmap)

---

## Qué es

Aplicación de escritorio para planificar y calcular turnos de combate en D&D 5e. Permite:

- Calcular daño mínimo, promedio y máximo de un turno completo
- Calcular daño esperado considerando la probabilidad de fallo
- Calcular probabilidades de impacto, fallo y crítico por acción
- Calcular probabilidades conjuntas del turno (todos impactan, al menos uno, ninguno, algún crítico)
- Aplicar resistencias, vulnerabilidades e inmunidades por tipo de daño
- Mezclar ataques y conjuros en el mismo turno
- Gestionar fichas de personaje con stats, armas, conjuros y CD/ataque de conjuros
- Gestionar criaturas con AC, stats y resistencias

---

## Requisitos

- Python 3.8 o superior
- `flask`
- `pywebview` (opcional; si no está, la app se abre en el navegador)

---

## Instalación

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:

```
flask==3.0.3
pywebview==5.1
```

Para ejecutar en modo navegador únicamente:

```bash
pip install flask
```

---

## Ejecución

```bash
python run.py
```

El script:
1. Arranca el servidor Flask en `http://127.0.0.1:5173`
2. Intenta abrir una ventana nativa con pywebview
3. Si pywebview no está disponible o falla, abre el navegador por defecto

**Plataformas soportadas:**

| Plataforma | Modo |
|---|---|
| Windows / Linux / Mac | Ventana nativa (con pywebview) |
| Android con Pydroid 3 | Navegador (pywebview no está soportado) |

---

## Estructura del proyecto

```
DragonsTactics/
├── run.py                    # Punto de entrada
├── requirements.txt
├── backend/
│   ├── app.py                # Rutas Flask
│   ├── api.py                # Endpoints JSON
│   ├── almacen.py            # Acceso a disco centralizado
│   └── logica/               # Lógica de D&D
│       ├── dados.py
│       ├── ficha.py
│       ├── equipo.py
│       ├── criatura.py
│       └── combate.py
├── frontend/
│   ├── templates/            # Plantillas HTML
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── datos/                    # (auto) Personajes, criaturas, imágenes
└── docs/                     # Documentación extendida
```

**Regla arquitectónica:** todo el acceso a disco pasa por `almacen.py`. Cuando cambie el formato de datos, solo se modifica ese archivo.

---

## Notación de dados

| Notación | Significado |
|---|---|
| `1d8` | Un dado de 8 caras |
| `2d6+3` | Dos dados de 6 caras más 3 |
| `1d12+8+9d6` | Varios grupos de dados más bonos |
| `1d8-1d4` | Dados restados |
| `1d4-10` | Resultado puede ser negativo (se corta a 0) |

---

## Tipos de daño

Los 13 tipos de D&D 5e:

```
ácido · contundente · cortante · fuego · frío · fuerza
necrótico · perforante · psíquico · radiante
relámpago · trueno · veneno
```

Las resistencias, vulnerabilidades e inmunidades se aplican automáticamente al calcular daño contra una criatura.

---

## Reglas implementadas

- 20 natural siempre impacta y es crítico; 1 natural siempre falla (en ataques)
- En salvaciones, 1 natural no es fallo automático
- En crítico solo se duplican los dados, no los bonos fijos
- Los conjuros con salvación no hacen tirada de ataque ni crítico
- Si un conjuro tiene "mitad si salva", el daño esperado lo pondera
- El daño esperado del turno tiene en cuenta la probabilidad de fallo
- El promedio por acción es condicional (daño esperado si esa acción impacta)
- El máximo incluye la posibilidad de crítico para ataques
- Umbral de crítico configurable por personaje
- GWM/Sharpshooter: −5 al ataque, +10 al daño
- Si una criatura no tiene definida la stat de salvación que requiere un conjuro, se solicita antes de calcular

---

## API

Servidor en `http://127.0.0.1:5173`. Todos los endpoints devuelven JSON.

### Meta

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/meta` | Constantes (stats, elementos, tipos) |

### Personajes

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/personajes` | Lista de personajes (resúmenes) |
| GET | `/api/personajes/<nombre>` | Ficha completa |
| POST | `/api/personajes` | Crear |
| PUT | `/api/personajes/<nombre>` | Actualizar |
| DELETE | `/api/personajes/<nombre>` | Eliminar |
| POST | `/api/personajes/<nombre>/imagen` | Subir imagen (multipart) |
| DELETE | `/api/personajes/<nombre>/imagen` | Eliminar imagen |

### Criaturas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/criaturas` | Lista |
| GET | `/api/criaturas/<nombre>` | Detalle |
| POST | `/api/criaturas` | Crear |
| PUT | `/api/criaturas/<nombre>` | Actualizar |
| DELETE | `/api/criaturas/<nombre>` | Eliminar |

### Combate

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/combate` | Calcular turno |

**Payload de `/api/combate`:**

```json
{
  "personaje": "Ryouma",
  "criatura": {
    "nombre": "Troll",
    "ac": 15,
    "resistencias": ["fuego"],
    "vulnerabilidades": ["ácido"],
    "inmunidades": [],
    "stats": { "Constitución": { "mod": 4 } }
  },
  "acciones": [
    {
      "tipo": "arma",
      "nombre": "Espada",
      "dano_str": "1d8+5",
      "elemento": "cortante",
      "bono_ataque_base": 9,
      "gwm": false,
      "extra_str": "",
      "modo": "normal"
    }
  ]
}
```

### Imágenes

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/imagenes/personajes/<nombre>` | Avatar del personaje |
| GET | `/imagenes/logo` | Logo personalizado |

---

## Tests

```bash
python test_dados.py
```

Cubre parseo de notación, mínimos, máximos, promedios, probabilidades de impacto y crítico en los tres modos, y aplicación de resistencias.

---

## Persistencia

Los datos se guardan en JSON plano:

```
datos/
├── personajes/<nombre>.json
├── criaturas/<nombre>.json
├── imagenes/personajes/<nombre>.png
└── config/logo.png
```

Todo el acceso pasa por `backend/almacen.py`. Para migrar a otro formato, solo se reescribe ese módulo.

---

## Roadmap

### Completado

- Motor de cálculo (probabilidades, críticos, resistencias, GWM/SS, conjuros con salvación)
- Fichas de personaje con armas y conjuros
- Imagen de personaje con recorte circular
- Cálculo de turno completo con daño esperado y probabilidades conjuntas
- Biblioteca de criaturas (crear, ver, editar, borrar)

### Pendiente

- Calculadora rápida (probabilidad, salvaciones)
- Manuales (biblioteca de conjuros, criaturas y equipo con paginación)
- Ejecutable `.exe` con PyInstaller
- Análisis de combates en tiempo real
- Formato de datos compartido con app externa
- Exportación a otros formatos

### A largo plazo

- Asistente táctico que estime el estado del enemigo según lo observado en combate
- Registro y análisis de partidas para refinar estimaciones
