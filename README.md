# DragonsTactics

Calculadora de combate para D&D 5e con interfaz gráfica moderna. Funciona como ventana nativa (con pywebview) o en el navegador, según la plataforma.

> ⚠️ **DEMO en desarrollo.** Versión temprana. Formato de datos provisional. Pueden cambiar cosas entre versiones.

---

## Índice

- [¿Qué hace?](#qué-hace)
- [Instalación](#instalación)
- [Cómo ejecutar](#cómo-ejecutar)
- [Guía de uso](#guía-de-uso)
- [Estructura](#estructura)
- [Arquitectura](#arquitectura)
- [Notación de dados](#notación-de-dados)
- [Tipos de daño](#tipos-de-daño)
- [Reglas implementadas](#reglas-implementadas)
- [API](#api)
- [Tests](#tests)
- [Persistencia](#persistencia)
- [Roadmap](#roadmap)
- [Estado](#estado)

---

## ¿Qué hace?

- **Calcula el daño esperado** de un turno completo (mínimo, promedio, máximo)
- Muestra **probabilidad de impacto, fallo y crítico** de cada acción
- Tiene en cuenta **resistencias, vulnerabilidades e inmunidades** por tipo de daño
- Permite **mezclar ataques con armas y conjuros** en el mismo turno
- Calcula **probabilidades conjuntas del turno** (todos impactan, al menos uno, ninguno, algún crítico)
- Calcula **probabilidades de salvación** contra una CD
- Gestiona **fichas de personaje** con stats, armas, conjuros y CD/ataque de conjuros
- Gestiona **criaturas** con AC, stats, resistencias, vulnerabilidades e inmunidades
- Permite subir **imagen de personaje** con recorte circular
- Distingue claramente entre **daño si impacta** y **daño esperado real** (con probabilidades)

---

## Instalación

Solo necesitas Python 3.8 o superior.

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:

```
flask==3.0.3
pywebview==5.1
```

**Sobre pywebview:**
- En **PC (Windows, Linux, Mac)**: se instala y funciona → ventana nativa
- En **Android con Pydroid**: puede fallar al instalar o al importar → cae en modo navegador automáticamente

Si no quieres ventana nativa, puedes instalar solo Flask:

```bash
pip install flask
```

Y la app se abrirá en el navegador por defecto.

---

## Cómo ejecutar

```bash
python run.py
```

**Qué pasa:**
1. Arranca el servidor Flask en `http://127.0.0.1:5173`
2. Intenta abrir una ventana nativa con pywebview
3. Si pywebview no está disponible o falla, **abre el navegador automáticamente**

**En móvil (Pydroid 3):**
1. Copia la carpeta del proyecto a tu almacenamiento
2. Abre `run.py` desde Pydroid
3. Pulsa ejecutar
4. Se abrirá el navegador con la app

**En PC:**
1. Instala dependencias con `pip install -r requirements.txt`
2. Ejecuta `python run.py`
3. Se abre ventana nativa (si pywebview funcionó) o navegador

---

## Guía de uso

### 1. Crear una ficha de personaje

Desde el dashboard, pulsa **"Nueva ficha"** o **"+ Crear ficha"**.

La ficha se organiza en **acordeones desplegables**:

#### Información general
- **Imagen del personaje** (opcional, con recorte circular)
  - Solo disponible después de guardar la ficha por primera vez
  - Se abre un recortador: arrastra la imagen, ajusta el zoom, guarda
- **Nombre, CA, velocidad, umbral de crítico** (20 por defecto, 19 para Champion, 18 para Superior Critical)
- **Bono de competencia, bono de ataque global**

#### Stats y salvaciones
- Los 6 stats con modificador
- Checkbox de competencia en salvación por stat

#### CD y ataque de conjuros
Se aplican **a todos** los conjuros del personaje. Dos opciones para cada uno:

**CD de conjuros:**
- **Calculada** = 8 + competencia + mod de stat + bono extra (ej. canalizador)
- **Manual** = tú escribes la CD

**Ataque de conjuros:**
- **Calculado** = competencia + mod de stat + bono extra
- **Manual** = tú escribes el bono

#### Armas
Cada arma tiene:
- Nombre
- Daño en notación estándar (`1d8+5`, `2d6+3d4+2`…)
- Elemento de daño (13 tipos)
- **Bono de ataque** de 3 formas:
  1. **Global** → usa el bono de ataque de la ficha
  2. **Stat + competencia + magia** → calcula mod + comp (x1 o x2 con pericia) + bono mágico
  3. **Manual** → tú escribes el bono

#### Conjuros
Cada conjuro tiene:
- Nombre
- Daño
- Elemento
- **Tipo**:
  - **Salvación** → el enemigo tira salvación contra tu CD. Si además marcas "mitad si salva", el daño esperado lo refleja
  - **Ataque de conjuro** → tú tiras ataque con tu bono de conjuros
- Nivel (1-9)
- Área (opcional, texto libre)
- Si es de salvación: stat de la salvación

---

### 2. Calcular un turno

Desde el dashboard o la vista de personaje, pulsa **"Calcular turno"**.

#### Paso 1 — Elegir criatura objetivo
- **Guardada**: pulsa una de las que ya tienes
- **Criatura nueva**: rellena nombre, AC, stats opcionales y elige resistencias/vulnerabilidades/inmunidades con los chips
- **Solo usar** → la usa para este combate sin guardarla
- **Guardar** → la añade a tu biblioteca de criaturas

#### Paso 2 — Configurar acciones
Pulsa **"Añadir acción"**. El modal tiene 3 tabs:

**Arma:**
- Elige arma de la lista
- Marca **GWM / Sharpshooter** si aplica (−5 atk, +10 daño)
- Daño adicional opcional (ej. `2d6` para un buff)
- Modo: normal / ventaja / desventaja

**Conjuro:**
- Elige conjuro de la lista
- Daño adicional opcional
- Modo: normal / ventaja / desventaja

**Custom:**
- Nombre libre, daño, elemento, bono de ataque
- Útil para ataques improvisados o habilidades especiales

Puedes **añadir varias acciones** y **mezclar armas y conjuros** en el mismo turno.

#### Paso 3 — Calcular

Pulsa **"Calcular turno"**. Verás:

**Por acción:**
- Barras de probabilidad de impacto/fallo (o falla salvación/salva si es conjuro)
- Mínimo / Promedio (si impacta) / Máximo
- **Daño esperado** de esa acción (con probabilidad de fallo aplicada) — solo para ataques
- Probabilidad de crítico y daño promedio en crítico — solo para ataques

**Resumen del turno:**
- **Si todos impactan**: mínimo, promedio y máximo en turno perfecto
- **Daño esperado del turno**: número grande, es el valor realista
- **Probabilidades conjuntas**: todos impactan / al menos uno / ninguno / algún crítico

**Aclaración importante:**
- **"Promedio si impacta"** = daño cuando el ataque entra
- **"Daño esperado"** = promedio × probabilidad de impacto. Es el número realista para comparar opciones

---

### 3. Gestionar criaturas

Desde el sidebar, pulsa **"Criaturas"**.

- Ver grid de criaturas con AC, stats, resistencias y tags
- **"Nueva criatura"** → formulario completo
- **"Ver"** → modal con todos los detalles bonitos
- **"Editar"** → formulario precargado
- Icono de papelera → eliminar (con confirmación)

Las criaturas guardadas aquí aparecen disponibles al calcular turnos.

---

### 4. Prueba de salvación

Desde el menú, pulsa **"Prueba de salvación"**.

1. Elige stat
2. La app aplica mod + competencia
3. Bono adicional opcional
4. Elige modo (normal/ventaja/desventaja)
5. Introduce CD
6. Ves las probabilidades de éxito y fallo

---

### 5. Test de impacto

Desde el menú, pulsa **"Test de impacto"**.

1. Introduce bono de ataque del enemigo
2. Bono de CA opcional (ej. cobertura)
3. Modo
4. Ves la probabilidad de que te pegue / te falle

---

### 6. Calculadora rápida

Desde el menú, pulsa **"Calculadora"**.

1. Introduce bono y CD/AC
2. Ves las probabilidades en normal, ventaja y desventaja

---

## Estructura

```
DragonsTactics/
├── run.py                        # Punto de entrada único
├── requirements.txt
├── README.md
│
├── backend/
│   ├── app.py                    # Flask + rutas
│   ├── api.py                    # Endpoints JSON
│   ├── almacen.py                # Acceso a disco centralizado
│   └── logica/
│       ├── dados.py              # Parseo y probabilidades
│       ├── ficha.py              # Fichas de personaje
│       ├── equipo.py             # Validación de armas/conjuros
│       ├── criatura.py           # Criaturas y resistencias
│       └── combate.py            # Motor de cálculo de turno
│
├── frontend/
│   ├── templates/
│   │   ├── base.html             # Layout común
│   │   ├── dashboard.html        # Lista de personajes
│   │   ├── ficha.html            # Crear/editar ficha
│   │   ├── personaje.html        # Vista bonita del personaje
│   │   ├── combate.html          # Calcular turno
│   │   ├── criaturas.html        # Biblioteca de criaturas
│   │   ├── calculadora.html      # Calculadora rápida
│   │   └── manuales.html         # Biblioteca (en construcción)
│   └── static/
│       ├── css/
│       │   ├── base.css          # Reset, variables, tipografía
│       │   ├── components.css    # Botones, cards, modales
│       │   ├── layout.css        # Sidebar, topbar
│       │   ├── combate.css       # Vista de combate
│       │   └── criaturas.css     # Vista de criaturas
│       ├── js/
│       │   ├── alpine.min.js     # (si es local)
│       │   ├── api.js            # Cliente HTTP
│       │   ├── ui.js             # Toasts, modales
│       │   ├── cropper.js        # Recortador de imágenes
│       │   ├── app.js            # Estado global del layout
│       │   └── views/
│       │       ├── dashboard.js
│       │       ├── ficha.js
│       │       ├── personaje.js
│       │       ├── combate.js
│       │       └── criaturas.js
│       └── img/
│           └── logo.svg          # Dragón + engranaje
│
├── datos/                        # (auto) Todo lo que se guarda
│   ├── personajes/               # Fichas JSON
│   ├── criaturas/                # Criaturas JSON
│   ├── manuales/                 # Manuales (futuro)
│   ├── imagenes/
│   │   └── personajes/           # Avatares recortados
│   └── config/
│       └── logo.png              # Logo custom (fase dev)
│
└── docs/
    ├── estructura-datos.md
    └── roadmap.md
```

---

## Arquitectura

**Flask + HTML/CSS/JS con Alpine.js.** Sin frameworks pesados, sin build step.

- **Backend (`backend/`)**: toda la lógica de D&D, aislada de la UI
- **Frontend (`frontend/`)**: HTML + CSS moderno + Alpine.js para reactividad
- **Almacén (`almacen.py`)**: TODO el acceso a disco pasa por aquí. Cuando cambie el formato de datos, solo se toca este archivo
- **API (`api.py`)**: funciones puras que reciben y devuelven dicts. No saben de HTTP
- **App (`app.py`)**: traduce HTTP ↔ funciones de `api.py`

**Ventajas:**
- Lógica reutilizable (la misma función sirve para la API y para scripts)
- Testeable (no hay dependencias de Flask en la lógica)
- Migrable (cambiar de Flask a FastAPI o a CLI solo afecta a `app.py`)
- Cero instalación de dependencias pesadas

---

## Notación de dados

Los daños se escriben con notación estándar:

| Notación | Significado |
|---|---|
| `1d8` | Un dado de 8 caras |
| `2d6+3` | Dos dados de 6 caras más 3 |
| `1d12+8+9d6` | Varios grupos de dados más bonos |
| `1d8-1d4` | Dados restados |
| `1d4-10` | Resultado puede ser negativo (se corta a 0 al aplicar) |

---

## Tipos de daño

Soporta los **13 tipos** de D&D 5e:

```
ácido · contundente · cortante · fuego · frío · fuerza
necrótico · perforante · psíquico · radiante
relámpago · trueno · veneno
```

Cada arma y cada conjuro tiene su tipo. Al calcular daño contra una criatura, se aplica **automáticamente**:

- **Resistencia** → mitad del daño
- **Vulnerabilidad** → doble del daño
- **Inmunidad** → cero

---

## Reglas implementadas

- **20 natural siempre impacta, 1 natural siempre falla** (en ataques)
- **En salvaciones, 1 natural NO es éxito ni fallo automático** (solo cuenta el total)
- **En crítico solo se duplican los dados**, no los bonos fijos
- Los **conjuros con salvación no hacen tirada de ataque ni crítico**
- Si un conjuro tiene **"mitad si salva"**, el daño esperado lo refleja (pondera por la probabilidad de que el enemigo salve)
- El **máximo mostrado** incluye la posibilidad de crítico (para ataques)
- **El promedio por acción es condicional**: daño esperado **si la acción impacta**
- **El daño esperado del turno** ya tiene en cuenta la probabilidad de fallar
- **Umbral de crítico configurable** (20 por defecto, 19 para Champion, 18 para Superior Critical)
- **GWM/Sharpshooter**: −5 al ataque, +10 al daño
- Si una criatura **no tiene definida la stat de salvación** que necesita un conjuro, te la pide antes de calcular

---

## API

Todos los endpoints devuelven JSON. Base: `http://127.0.0.1:5173`

### Meta
- `GET /api/meta` — stats, elementos, tipos disponibles

### Personajes
- `GET /api/personajes` — lista (resúmenes)
- `GET /api/personajes/<nombre>` — ficha completa
- `POST /api/personajes` — crear
- `PUT /api/personajes/<nombre>` — actualizar
- `DELETE /api/personajes/<nombre>` — eliminar
- `POST /api/personajes/<nombre>/imagen` — subir imagen (multipart)
- `DELETE /api/personajes/<nombre>/imagen` — borrar imagen

### Criaturas
- `GET /api/criaturas` — lista
- `GET /api/criaturas/<nombre>` — detalle
- `POST /api/criaturas` — crear
- `PUT /api/criaturas/<nombre>` — actualizar
- `DELETE /api/criaturas/<nombre>` — eliminar

### Combate
- `POST /api/combate` — calcular turno

**Payload ejemplo:**
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

### Utilidades
- `POST /api/arma/resumen` — calcula bono de ataque de un arma contra una ficha

### Imágenes
- `GET /imagenes/personajes/<nombre>` — devuelve el PNG del avatar
- `GET /imagenes/logo` — devuelve el logo custom (fase dev)

---

## Tests

```bash
python test_dados.py
```

Cubre:
- Parseo de notación de dados (incluyendo negativos: `1d8-1d4`, `-1d6`)
- Mínimos, máximos y promedios
- `floor0` con valores negativos
- Probabilidades de impacto en normal/ventaja/desventaja
- Probabilidades de crítico en normal/ventaja/desventaja
- Casos extremos: AC inalcanzable, salvaciones imposibles
- Aplicación de resistencias/vulnerabilidades/inmunidades

Total: ~45 asserts. Todos deben pasar en verde.

---

## Persistencia

Todo se guarda en JSON plano dentro de `datos/`.

```
datos/
├── personajes/<nombre>.json       # Ficha del personaje
├── criaturas/<nombre>.json        # Criatura con stats y resistencias
├── imagenes/personajes/<nombre>.png  # Avatar recortado
└── config/logo.png                # Logo custom (fase dev)
```

Puedes editarlos a mano, copiarlos entre dispositivos o versionarlos con git sin problema.

**Migración de formato:**
Todo el acceso a disco pasa por `backend/almacen.py`. Cuando definas un formato compartido con otra app, solo hay que tocar ese archivo y escribir un script de migración.

---

## Roadmap

### ✅ Entrega 1 — Fundación
- Estructura de carpetas
- Flask + pywebview en un solo `run.py`
- Sistema de diseño completo (colores, tipografía, componentes)
- Dashboard funcional: listar, crear, borrar personajes
- `almacen.py` centralizando el acceso a disco
- Lógica de D&D separada del frontend

### ✅ Entrega 2a — Ficha completa
- Vista de ficha con acordeones desplegables
- Formulario de creación/edición con validación
- Añadir/editar/borrar armas y conjuros
- Vista bonita del personaje con avatar, métricas y cartas
- Imagen de personaje con recorte circular

### ✅ Entrega 2b — Calcular turno
- Selección de criatura objetivo (guardada o custom)
- Configuración de acciones (arma/conjuro/custom)
- Ajustes por acción (GWM/SS, daño extra, modo)
- Resultado visual con barras de probabilidad
- Cálculo de daño esperado con probabilidades de fallo
- Probabilidades conjuntas del turno
- Distinción clara entre "si impacta" y "daño esperado real"

### ✅ Entrega 3a — Criaturas
- Biblioteca de criaturas con listar, crear, ver, editar, borrar
- Modal de creación con stats opcionales
- Chips de selección de resistencias/vulnerabilidades/inmunidades
- Vista de detalle bonita

### 🚧 Entrega 3b — Calculadora
- Pantalla de calculadora rápida (probabilidad, salvaciones)
- Estética consistente con el resto

### 🚧 Entrega 3c — Manuales
- Biblioteca con estructura de carpetas por manual
- Paginación A/D
- Import/export de manuales
- Editor de manuales homebrew

### 🔮 Futuro
- **Interfaz gráfica**: ejecutable `.exe` con PyInstaller
- **Oráculo**: análisis de combates en tiempo real, estimación del estado del enemigo según lo observado, sugerencias de jugadas
- **Aprendizaje**: registro de partidas para refinar estimaciones y adaptarse al estilo del jugador
- **Formato de datos compartido** con la app amiga
- **Exportación** a PDF, texto plano u otros formatos

---

## Estado

Proyecto personal en desarrollo activo. La base actual está **estable y verificada con tests**. 

- **Motor de cálculo**: exacto, testeado, correcto
- **UI**: pulida, responsive, con identidad visual propia
- **Arquitectura**: agnóstica al formato de datos, lista para migrar
- **Faltan**: calculadora, manuales, Oráculo, aprendizaje

**Lo que hace único a este proyecto a futuro**: el Oráculo. Nadie ha hecho un asistente táctico de D&D que **infiera información del enemigo observando el combate** y **recomiende acciones sin metarol**. Ese es el diferencial.
