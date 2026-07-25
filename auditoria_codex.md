# Auditoría técnica y de seguridad de Risansym

Fecha: 2026-07-24  
Alcance: `core/`, `web/`, configuración de compilación y CI/CD  
Método: análisis topológico con Graphify, revisión dirigida de código, pruebas, análisis estático y auditoría de dependencias

## Resumen ejecutivo

Risansym tiene una arquitectura comprensible y apropiada para su tamaño: un motor Python de simulación discreta genera trazas JSON y una aplicación Next.js estática las valida y visualiza íntegramente en el navegador. No existe backend, base de datos ni flujo de autenticación en el alcance actual; por tanto, esos controles no son aplicables mientras la aplicación siga siendo un export estático y procese únicamente archivos locales.

No se identificaron hallazgos críticos ni secretos embebidos. Sí se identificaron **4 hallazgos altos, 7 medios y 6 bajos**. Las prioridades inmediatas son:

1. Actualizar dependencias web vulnerables, empezando por Next.js 16.2.11 y regenerando el lockfile.
2. Imponer límites de tamaño, cantidad y profundidad a las trazas cargadas en el navegador.
3. Acotar el número de eventos y el coste de capturar estados en el motor.
4. Sanear las rutas de exportación derivadas de `algo_name`, `topology_name` y `trace_tag`.

La suite funcional está en buen estado: **72/72 pruebas Python** y **14/14 pruebas web** pasaron. Ruff detectó cinco imports no utilizados. El grafo se construyó desde el mismo commit que `HEAD` (`19a0e722`), pero el árbol de trabajo tenía modificaciones no confirmadas; los hallazgos se contrastaron contra los archivos actuales.

## Mapa arquitectónico obtenido con Graphify

Graphify reporta **522 nodos, 1,016 aristas y 33 communities**, con 90% de relaciones extraídas y 10% inferidas. Las communities principales son:

- **Web UI Components**: carga, reproducción y render SVG de trazas.
- **Simulation Engine Core**: `Simulator`, `EventLoop`, `SimulationBuilder`, procesos y topología.
- **Trace Export Logic**: esquemas Pydantic, colector y persistencia JSON.
- **Simulation Plugin System**: plugins de consola y trazado.
- **Base Model Interface / Message Sink Protocol**: contrato de algoritmos y puerto hacia el motor.
- **Event Management System / Event Heap Management**: evento y agenda priorizada.

Flujo principal:

```text
Modelo de usuario
  → Model / MessageSink
  → Process
  → Simulator (heap de eventos)
  → EventLoop
  → plugins
  → TraceCollector / TraceExporter
  → archivo JSON
  → Uploader + Zod
  → Contextos React
  → hooks de geometría
  → visualizador SVG
```

Los principales nodos centrales son `Event` (75 aristas), `Simulator` (50), `Simulation` (47), `Model` y `Process` (30 cada uno). No se detectaron ciclos de imports. La cohesión de las communities principales es baja (0.05–0.07), en parte porque el grafo mezcla archivos, símbolos, documentación, configuración y tests; esta métrica debe usarse como señal de navegación, no como prueba aislada de mal diseño.

## Hallazgos por criticidad

### Criticidad alta

#### SEC-01 — Dependencias JavaScript con vulnerabilidades conocidas

**Evidencia:** `web/package.json:13-17`; auditoría de `web/package-lock.json` con `npm audit`.

La auditoría reportó **4 dependencias vulnerables de severidad alta**:

- `next@16.2.10`: múltiples avisos, incluidos bypass de middleware/proxy, DoS y SSRF; la corrección propuesta es `16.2.11`.
- `postcss<=8.5.17`: lectura arbitraria de archivos/path traversal mediante source maps y un aviso XSS.
- `sharp<0.35.0`: vulnerabilidades heredadas de libvips.
- `brace-expansion<=5.0.7`: expansión exponencial y agotamiento de memoria.

La aplicación actual se exporta estáticamente (`web/next.config.ts:11-14`), por lo que varios vectores server-side de Next.js no están activos en GitHub Pages. Aun así, la cadena de build y futuros despliegues dinámicos siguen expuestos, y `postcss`/`sharp` forman parte del procesamiento de artefactos.

**Recomendación:**

1. Actualizar Next.js a `16.2.11` o superior compatible y regenerar `package-lock.json`.
2. Ejecutar `npm audit` tras la actualización y verificar que se resuelvan también `postcss` y `sharp`.
3. Aplicar la actualización disponible de `brace-expansion` mediante las dependencias padre; usar `overrides` solo si la resolución normal no basta y después de probarla.
4. Añadir `npm audit --audit-level=high` a CI o habilitar revisión automática de dependencias.

#### SEC-02 — Denegación de servicio local mediante trazas sin límites

**Evidencia:** `web/src/components/Uploader.tsx:19-56`, `web/src/lib/schema.ts:3-50`, `web/src/components/visualizer/Visualizer.tsx:34-48`.

El cargador usa `FileReader.readAsText`, `JSON.parse` y validación completa sin comprobar primero el tamaño del archivo. El esquema permite arrays sin máximo, strings ilimitados y objetos `payload`/`node_state` de profundidad y tamaño arbitrarios. Una traza grande o especialmente anidada puede bloquear la pestaña o agotar memoria.

Después de validarla, el ancho del SVG crece con `maxTime × zoomScale`, y se crean elementos DOM por mensajes y grupos de eventos. Los tiempos e IDs aceptan cualquier `number`, incluidos valores negativos o no finitos según el comportamiento del validador usado, y no existen cotas de dominio.

**Recomendación:**

- Rechazar antes de leer archivos por encima de un límite explícito (por ejemplo, 25–50 MB configurable).
- Añadir `.max()` a `trace`, nombres y mensajes; validar enteros positivos para nodos y números finitos/no negativos para relojes.
- Limitar profundidad/tamaño de `payload` y `node_state` con una validación propia.
- Parsear y validar en un Web Worker; para formatos muy grandes, adoptar parsing incremental.
- Virtualizar/agregar eventos y fijar un máximo seguro para dimensiones SVG y zoom.

#### PERF-01 — Coste no acotado por evento en el motor

**Evidencia:** `core/src/risansym/engine/loop.py:31-58`, `core/src/risansym/process.py:39-48`.

Por cada evento procesado se obtiene el estado del modelo y se ejecuta `copy.deepcopy`, aunque no haya un plugin interesado en dicho estado. Al transmitir también se obtiene el estado antes de llamar al motor. Con estados grandes, el coste efectivo pasa de depender principalmente del número de eventos a depender de la suma del tamaño completo de los estados capturados.

Además, `maxtime` limita el horizonte temporal, pero no la cantidad de eventos. Un modelo puede programar eventos ilimitados al mismo instante o dentro del horizonte y consumir CPU/memoria indefinidamente.

**Recomendación:**

- Añadir `max_events_processed`, `max_pending_events` y cancelación/timeout cooperativo.
- Consultar si algún plugin requiere snapshots antes de llamar `get_state()` o copiar.
- Definir un contrato de snapshot inmutable/serializable y permitir estrategias configurables: ninguna, superficial, profunda o callback.
- Medir por separado eventos descartados, pendientes máximos y bytes aproximados de estado.

#### PERF-02 — Render completo de mensajes en cada tick de reproducción

**Evidencia:** `web/src/components/visualizer/MessageArrows.tsx:38-107`, `web/src/components/visualizer/hooks/useEventGroups.ts:75-78`, `web/src/lib/PlaybackContext.tsx:45-59`.

El reloj cambia con `requestAnimationFrame`. Cada cambio vuelve a renderizar `MessageArrows`, que recorre todos los mensajes, y filtra linealmente todos los grupos. Con trazas grandes, esto produce trabajo `O(M + G)` hasta 60 veces por segundo, además del coste del DOM/SVG.

**Recomendación:**

- Ordenar por reloj y usar búsqueda binaria para obtener el prefijo visible.
- Separar capas estáticas y animadas; mover el playhead con una propiedad SVG/CSS sin reconciliar todos los mensajes.
- Aplicar windowing temporal y espacial, canvas/WebGL para grandes volúmenes, o un modo agregado.
- Definir presupuestos de rendimiento y pruebas con 10k, 100k y 1M eventos.

### Criticidad media

#### SEC-03 — Escape del directorio de trazas mediante metadatos usados como ruta

**Evidencia:** `core/src/risansym/engine/exporter.py:35-45`.

Cuando no se proporciona `trace_path`, `algo_name` y `trace_tag` se incorporan directamente a directorios/nombres. Valores absolutos o con `../` pueden escapar de `trace_dir`; un nombre que incluya separadores también crea rutas inesperadas. Si esos valores proceden de entrada no confiable en una integración, existe escritura o sobrescritura fuera del directorio previsto.

**Recomendación:**

- Convertir componentes a slugs con una allowlist (`[A-Za-z0-9._-]`) y longitud máxima.
- Resolver la ruta final y comprobar con `Path.is_relative_to(base.resolve())` que permanece bajo el directorio autorizado.
- Crear archivos de forma exclusiva (`"x"`) o añadir suficiente entropía para evitar colisiones.
- Mantener `trace_path` explícito como API privilegiada y documentar que no debe recibir entrada no confiable.

#### SEC-04 — Falta de validación de integridad al transmitir eventos

**Evidencia:** `core/src/risansym/process.py:39-48`, `core/src/risansym/simulator.py:37-48`, `core/src/risansym/engine/loop.py:34-40`.

`Process.transmit` no verifica que `event.source == self.node_id` ni que el destino sea vecino. El destino solo se valida al consumir el evento. Un algoritmo defectuoso o no confiable puede suplantar otros nodos, saltarse la topología y llenar la agenda con destinos inválidos para provocar un fallo tardío.

Esto no constituye aislamiento de código: los modelos Python ya ejecutan dentro del proceso y se consideran de confianza. Sí compromete la fidelidad de la simulación y cualquier análisis que trate la traza como evidencia.

**Recomendación:** validar origen y vecindad en `Process.transmit`; ofrecer una opción explícita y separada para eventos administrativos/semilla que puedan saltarse esas reglas; validar el destino antes de insertar en el heap.

#### SEC-05 — Validación Pydantic omitida en el plugin de trazas

**Evidencia:** `core/src/risansym/plugins/tracer.py:33-69`.

El plugin construye `TransmitEvent`, `ReceiveEvent` y `AppLogEvent` con `model_construct`, que omite validación. Payloads o estados no serializables y valores fuera del contrato pueden permanecer en memoria hasta que la exportación falle al final de una simulación costosa.

**Recomendación:** usar constructores validados en el límite de entrada o validar una sola vez mediante una función optimizada; si el rendimiento motiva `model_construct`, imponer el contrato en `Event`/`Model.get_state` y añadir pruebas con datos no serializables y valores no finitos.

#### ARCH-01 — Encapsulación débil entre fachada, motor y plugins

**Evidencia:** `core/src/risansym/simulation.py:172-181`, `core/src/risansym/engine/loop.py:55-56`, `core/src/risansym/plugins/tracer.py:72-82`.

`Simulation` y `EventLoop` acceden directamente a `Simulator._plugins`; el tracer accede a `_topology_name` y a múltiples estructuras internas de `Simulation`. Esto contradice el prefijo privado y aumenta el acoplamiento entre las tres communities que Graphify identifica como núcleo, plugins y trazas.

`Simulation` es el mayor puente arquitectónico después de `Event`: construye, mantiene compatibilidad, inicializa modelos, gestiona plugins, ejecuta y expone métricas. No es todavía un “God Object” severo, pero está en el umbral donde nuevas responsabilidades degradarán el diseño.

**Recomendación:** encapsular notificaciones en métodos públicos de `Simulator` o en un `PluginManager`; pasar a los plugins un contexto de solo lectura; mantener `Simulation` como fachada delegando ciclo de vida y exportación.

#### REL-01 — Ciclo de vida de plugins no garantizado ante excepciones

**Evidencia:** `core/src/risansym/simulation.py:172-181`, `core/src/risansym/simulation.py:214-220`.

Si `on_start`, el bucle o un plugin falla, `on_end` no se ejecuta. `__exit__` no realiza limpieza. Esto puede perder trazas, dejar recursos de plugins abiertos y ocultar métricas parciales.

**Recomendación:** ejecutar finalización en `try/finally`, definir semántica de errores y agregar `on_error`; aislar errores de observabilidad según política configurable; hacer que `__exit__` cierre recursos o eliminar el context manager vacío.

#### PERF-03 — Generación de topología aleatoria degrada hacia O(n³)

**Evidencia:** `core/src/risansym/topology.py:133-162`.

El doble bucle sobre pares de nodos realiza `(j + 1) not in graph[i]` sobre una lista. En grafos densos esa membresía es O(n), por lo que la construcción puede aproximarse a O(n³). `mesh` es O(n²), inevitable por el tamaño de salida, pero `random` añade un factor evitable.

**Recomendación:** construir con `set[int]`, hacer membresía O(1) y convertir/ordenar al final. Añadir benchmarks para topologías de 1k, 5k y 10k nodos.

#### REL-02 — Orden no determinista para eventos con el mismo tiempo

**Evidencia:** `core/src/risansym/event.py:12-36`, `core/src/risansym/simulator.py:37-59`.

`Event` compara únicamente `time`; para dos eventos simultáneos no existe contador de secuencia ni prioridad secundaria. `heapq` no garantiza una política FIFO contractual para elementos equivalentes. El resultado de algoritmos sensibles al orden puede variar al cambiar el patrón de inserción o implementación.

**Recomendación:** almacenar entradas `(time, sequence, event)` con un contador monotónico o documentar y probar una política de desempate explícita.

### Criticidad baja

#### DEBT-01 — Cinco imports muertos rompen Ruff

**Evidencia:** Ruff sobre `core/src` y `core/tests`.

Se detectaron imports no usados en `simulation.py`, `simulator.py` y `test_topology_generator.py`. Todos son corregibles automáticamente, pero actualmente hacen fallar la misma regla configurada en CI.

**Recomendación:** eliminar los imports y exigir que `ruff`, `mypy` y tests pasen antes de integrar.

#### DEBT-02 — Compatibilidad obsoleta incrementa ramas y advertencias

**Evidencia:** `core/src/risansym/simulation.py:43-71,163-170,185-194`, `core/src/risansym/model.py:39-57`.

La suite emitió 16 warnings, principalmente por APIs deprecadas que los propios tests siguen usando. Las ramas para `debug`, `trace`, `Simulation.init`, carga directa de archivo, auto-inicialización y `Model.id` amplían el estado a probar.

**Recomendación:** definir la fecha/versión de eliminación, migrar primero tests y documentación, y borrar las rutas en v1.0.

#### DEBT-03 — Los nodos aislados de Graphify no demuestran código muerto

Graphify reportó 73 nodos aislados y 8 communities delgadas. La inspección mostró que muchos son metadatos/configuración (`package.json`, `tsconfig`), documentos o métodos especiales invocados por frameworks, no código muerto. Los candidatos más claros son el context manager vacío y los imports señalados por Ruff.

**Recomendación:** no eliminar por centralidad baja. Confirmar con cobertura, importación pública y análisis estático; mejorar la extracción del grafo para configuración y convenciones de framework.

#### ARCH-02 — Contratos duplicados Python/TypeScript susceptibles a deriva

**Evidencia:** `core/src/risansym/schemas.py:5-67`, `web/src/lib/schema.ts:3-50`.

El mismo esquema se mantiene manualmente en Pydantic y Zod. Ya existe una diferencia: web tolera `event_time` opcional en `RECEIVE`, mientras Python no lo modela, y las restricciones futuras pueden divergir.

**Recomendación:** publicar JSON Schema desde Pydantic y generar/validar el contrato TypeScript en CI; añadir fixtures contractuales compartidos.

#### REL-03 — Colisiones y sobrescritura de archivos de traza

**Evidencia:** `core/src/risansym/engine/exporter.py:37-45`, `core/src/risansym/trace.py:79-93`.

El nombre automático usa resolución de un segundo y el archivo se abre con modo `"w"`. Dos ejecuciones equivalentes en el mismo segundo pueden sobrescribirse.

**Recomendación:** incluir microsegundos/UUID o usar creación exclusiva y reintento.

#### CI-01 — Acciones fijadas solo por tag mutable

**Evidencia:** `.github/workflows/ci.yml`, `deploy.yml` y `publish.yml`.

Las GitHub Actions se referencian por tags mayores (`@v4`, `@v5`) y no por SHA. Es una práctica común, pero amplía la superficie de supply chain si un tag se mueve o una cuenta se compromete.

**Recomendación:** fijar acciones de terceros a SHA completo y usar Dependabot/Renovate para actualizar esas referencias.

## Evaluación por pilar

### 1. Arquitectura y diseño

**Fortalezas**

- Separación física clara entre motor Python y visualizador web mediante un contrato JSON.
- `Model` depende de `MessageSink` y `Process` de `EngineProtocol`, una aplicación útil de inversión de dependencias.
- `SimulationBuilder`, `EventLoop` y `TraceExporter` ya extraen responsabilidades de la fachada.
- Plugins desacoplan trazado y logging del núcleo.
- No hay ciclos de imports detectados.

**Debilidades**

- Acceso transversal a miembros privados y contexto de plugin demasiado amplio.
- `Simulation` concentra compatibilidad, construcción y lifecycle.
- Contrato duplicado entre lenguajes.
- No existe una política explícita de orden para eventos simultáneos.

### 2. Seguridad

- **Autenticación/autorización:** no aplicable en la arquitectura actual; no hay usuarios, API ni backend. Si se añade almacenamiento o ejecución remota, deberá diseñarse desde cero y no asumirse cubierta por este análisis.
- **Inputs:** existe validación estructural robusta con Zod y validación básica de topología/eventos, pero faltan límites de recursos y validación de integridad entre nodo, vecino y evento.
- **Secretos:** no se encontraron claves, tokens privados ni contraseñas embebidas. Los workflows usan OIDC (`id-token: write`) con permisos acotados.
- **Inyección:** no se observaron `eval`, `exec`, comandos de shell, deserialización insegura ni `dangerouslySetInnerHTML`. React escapa texto de trazas.
- **Rutas:** la generación automática de rutas de traza requiere saneamiento y confinamiento.
- **Supply chain:** cuatro vulnerabilidades altas en el árbol npm requieren actualización.

### 3. Deuda técnica y Clean Code

- La suite funcional es amplia para el tamaño actual, pero el lint Python falla.
- Las APIs deprecadas ya generan ruido significativo en tests.
- No hay evidencia suficiente para declarar muertos los 73 nodos aislados del grafo; la mayoría son falsos positivos estructurales.
- Los puertos/protocolos muestran una orientación SOLID positiva; el principal incumplimiento es la dependencia de privados entre lifecycle, plugins y exportador.

### 4. Rendimiento

- La agenda usa `heapq`: inserción y extracción O(log E), apropiada.
- La validación de simetría de topología usa sets para membresía O(1), una mejora correcta.
- Los mayores cuellos son snapshots profundos por evento, ausencia de presupuesto de eventos, trazas en memoria de hasta un millón de objetos y render SVG completo por frame.
- La serialización de trazas es incremental y evita construir un segundo JSON completo en memoria, lo cual es una fortaleza.
- La generación aleatoria usa listas donde sets evitarían degradación cúbica.

## Plan de remediación

### 0–48 horas

1. Actualizar dependencias npm y confirmar `npm audit` sin vulnerabilidades altas.
2. Corregir los cinco errores Ruff.
3. Añadir límite de archivo/eventos y restricciones numéricas al esquema Zod.
4. Sanear y confinar rutas de traza.

### Próximo sprint

1. Añadir presupuestos al motor: eventos procesados, agenda, timeout y tamaño de snapshot.
2. Hacer lazy la captura/copia de estado según capacidades de plugins.
3. Encapsular el lifecycle de plugins con `try/finally`.
4. Validar origen, vecino y destino antes de encolar.
5. Optimizar `TopologyGenerator.random` con sets.
6. Añadir tests adversariales: archivo enorme, profundidad JSON, tiempos extremos, path traversal, tormenta de eventos y fallo de plugin.

### Mediano plazo

1. Generar un contrato compartido JSON Schema Pydantic → TypeScript.
2. Introducir render agregado/virtualizado y benchmarks de trazas grandes.
3. Definir desempate determinista de eventos.
4. Retirar compatibilidad deprecada en v1.0.
5. Fijar GitHub Actions por SHA y automatizar auditorías de dependencias.

## Verificaciones realizadas

| Verificación | Resultado |
|---|---|
| Graphify | 522 nodos, 1,016 aristas, 33 communities |
| Frescura del grafo | Commit del grafo coincide con `HEAD`; hay cambios locales sin commit |
| Pytest | 72 pasaron, 16 warnings |
| Vitest | 14 pasaron en 6 archivos |
| Ruff | Falló: 5 imports no usados |
| Búsqueda de secretos/primitivas peligrosas | Sin hallazgos confirmados |
| `npm audit` | 4 vulnerabilidades altas, 0 críticas |
| ESLint / build Next.js | Iniciados; el entorno de ejecución no devolvió estado terminal confiable |

## Limitaciones y supuestos

- Es una revisión estática y de pruebas, no un pentest dinámico ni una auditoría formal de dependencias Python.
- Los modelos y plugins Python ejecutan código arbitrario en el proceso por diseño. Risansym **no es un sandbox** y no debe ejecutar algoritmos no confiables sin aislamiento externo (contenedor, límites de CPU/memoria, filesystem y red).
- La criticidad de path traversal y suplantación aumenta si una API o servicio remoto expone esos parámetros.
- Las relaciones inferidas por Graphify se usaron para orientar la revisión y se contrastaron con código antes de convertirlas en hallazgos.

