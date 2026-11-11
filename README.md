# Noticiero CrewAI — equipo de 2 agentes

Equipo de dos agentes hecho con **CrewAI** que trabajan en secuencia: un **investigador** busca titulares reales y recientes sobre un tema, y un **redactor** escribe con ellos un resumen corto, citando las fuentes.

## Framework y por qué

> He usado **CrewAI** porque permite definir cada agente (rol, objetivo, personalidad) y cada tarea en archivos YAML legibles, y conectarlos en secuencia con muy poco código. Además, crear una herramienta propia (`BaseTool`) es sencillo, lo que me permitió que el investigador trabajara con noticias reales en lugar de inventarlas.

## Cómo funciona

```
 tema (input) ──▶ 🕵️ Investigador ──(lista de titulares)──▶ ✍️ Redactor ──▶ resumen final
                       │
                       └─ usa la herramienta "Buscador de noticias" (Google News RSS)
```

| Agente | Rol | Herramientas | Entrega |
|---|---|---|---|
| `investigador_noticias` | Busca titulares recientes sobre el tema, sin inventar ninguno | `BuscarNoticiaTool` | Lista numerada: título, medio, fecha y enlace → `output/1_noticias.md` |
| `redactor_noticias` | Escribe un resumen en prosa usando **solo** lo que recibe | Ninguna | Resumen de 150-200 palabras + fuentes → `output/2_resumen.md` |

**Traspaso (handoff):** el proceso es secuencial (`Process.sequential`) y la tarea del redactor declara `context=[investigar_noticias_tarea]`, así que recibe como entrada la lista del investigador. El redactor no tiene herramientas: solo puede trabajar con lo que le pasan.

**Herramienta propia** (`src/noticias_crewai/tools/buscar_noticias.py`): consulta el RSS de Google News en español (no necesita API key) usando solo la librería estándar (`urllib` + `xml.etree`). Valida sus parámetros con Pydantic (de 2 a 9 noticias) y devuelve los errores como texto para que el agente pueda reintentar.

## Estructura

```
src/noticias_crewai/
├── config/
│   ├── agents.yaml      # quién es cada agente (role, goal, backstory)
│   └── tasks.yaml       # qué entrega cada tarea (description, expected_output)
├── tools/
│   └── buscar_noticias.py
├── crew.py              # une agentes, tareas, herramienta y handoff
└── main.py              # pide el tema y lanza el equipo
output/                  # resultados de la última ejecución
```

## Cómo ejecutarlo

Requisitos: Python 3.10-3.13, [uv](https://docs.astral.sh/uv/) y CrewAI CLI (`uv tool install crewai`).

1. Copia la plantilla `.env.example` como `.env` y pon tu clave de Gemini:
   ```bash
   cp .env.example .env
   ```
2. Instala las dependencias y ejecuta desde la raíz del proyecto:
   ```bash
   crewai install
   crewai run
   ```
3. Escribe un tema (o pulsa Enter para usar "inteligencia artificial").

## Observar cómo se pasan el trabajo

Cada ejecución deja tres evidencias en `output/`:

- `1_noticias.md`: lo que entrega el investigador.
- `2_resumen.md`: lo que el redactor hace con ello (la salida final).
- `ejecucion.json`: la traza con horas. Ejemplo real:

```
00:18:15  investigar_noticias_tarea  started
00:18:21  investigar_noticias_tarea  completed   ← el investigador entrega su lista
00:18:21  redactar_noticias_tarea    started     ← el redactor empieza en el mismo segundo
00:18:26  redactar_noticias_tarea    completed
```

En la consola (`verbose=True`) se ve además la llamada a la herramienta con los argumentos que eligió el LLM, por ejemplo `{'palabras_clave': 'inteligencia artificial', 'num_noticias': 5}`.

## Salida final del equipo (12/11/2026, tema: "inteligencia artificial")

> La inteligencia artificial está acaparando titulares en diversos ámbitos de la sociedad, generando tanto preocupación por sus riesgos como expectativas de grandes cambios. En el terreno político y laboral, la tecnología ha irrumpido con fuerza en la campaña electoral del 29-N (Expansión) y plantea debates económicos profundos, como la advertencia de UGT sobre cómo la IA incrementa la producción con menos personal, lo que exige reducir el tiempo de trabajo (El Confidencial). Además, se empiezan a tomar medidas legales y de control frente a sus fallos, abriendo información a los jueces tras registrarse errores en el uso de IA en sentencias (El Mundo), al tiempo que se alertan sobre las trampas ocultas en los chats de consultas cotidianas (Antena 3 Noticias). Por otro lado, su impacto se extiende al ocio y el deporte, anticipando una auténtica revolución en el fútbol (Diario AS).

Las fuentes con sus enlaces están en [`output/2_resumen.md`](output/2_resumen.md).

## Limitaciones

- El investigador trabaja solo con **titulares**: no lee el contenido de los artículos, así que el resumen no puede ir más allá de lo que dicen los titulares.
