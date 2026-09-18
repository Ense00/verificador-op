# Requisitos — Verificador de Órdenes de Pago

Documento vivo: aquí se registra lo que la herramienta debe hacer. Cada cambio de criterio se anota también en `CHANGELOG.md`.

## Problema

Se descarga una carpeta de PDFs **escaneados** con Órdenes de Pago (OP). Un PDF puede traer 1 OP en pocas páginas o cientos de OP en 500–3000+ páginas. Hay que comprobar, contra un Excel, que cada OP solicitada esté en la carpeta y sea válida.

## Flujo completo del proceso

1. **Documento base** (Excel exportado del sistema, uno por entidad y ejercicio): trae órdenes de pago, montos y muchas columnas más. Es la fuente de **todo**: del Layout y de la verificación.
2. **Layout:** a partir del documento base se genera un Excel con formato fijo que se sube a una plataforma externa.
3. **Plataforma:** con el Layout, extrae y entrega los PDFs de las órdenes solicitadas.
4. **Verificación:** se revisan esos PDFs contra el documento base (lo descrito en el resto de este documento).

### Documento base (estructura observada en un ejemplo real)

- Una hoja, encabezados en la fila 1. Columnas relevantes: `Contribución` (nombre de la entidad), `Orden de Pago` (10 dígitos, guardada como texto), `Fecha Contable` (fecha), `Importe en moneda de la entidad CP` (monto). Otras columnas (`DocReferencia`, `Período`, `Status Actual`, `Centro gestor`, etc.) no se usan para verificar.
- `DocReferencia` **no** es la orden de pago; no usarla.
- La última fila puede ser un **total con fórmula** sin orden de pago: se ignora toda fila sin orden de pago.
- Puede haber **montos negativos**: se verifican y se marcan como *Revisar* ("Monto negativo en el documento base").
- Una orden de pago puede repetirse en varias filas con montos distintos.
- **Formato del número de orden (medido en dos documentos base reales, 2026-09-17): siempre 10 dígitos.** 73 de 73 órdenes en un archivo y 481 de 481 en otro. Las series observadas son varias (`19` la mayoría, también `51`, `71` y `50`): **no se filtra por prefijo**, un número de orden es cualquier grupo de 10 dígitos, con `-A` opcional.
- En esos dos archivos no apareció ninguna orden con sufijo `-A`.
- Pueden aparecer órdenes **con y sin** sufijo `-A` (ADEFA).
- **Ejercicio = año de la `Fecha Contable`** de cada fila.
- **Las columnas pueden cambiar de posición, pero no de nombre:** se localizan por el nombre del encabezado (sin distinguir mayúsculas, acentos ni espacios extra).
- El nombre de la entidad se escribe **a mano** en la página (la columna `Contribución` no siempre trae el nombre completo).

### Layout para la plataforma

Plantilla: hoja `Hoja1`, 8 columnas con estos encabezados exactos. La plataforma es imperfecta: **no** llenar según el nombre de la columna, sino así:

| Columna | Valor |
|---|---|
| `DocumentoReferencia` | Orden de pago |
| `OrdenPago` | Orden de pago |
| `FechaContable` | vacío |
| `Periodo` | Año del ejercicio |
| `CentroGestor` | vacío |
| `PeriodoPresupuesto` | Año del ejercicio |
| `Importe` | vacío |
| `PartidaGasto` | vacío |

- **Todo en formato número, sin decimales** (enteros). **Excepción:** las órdenes ADEFA (`-A`) van tal cual como texto, con formato **General**.
- **Sin órdenes repetidas:** la plataforma marca error. Una fila por orden de pago única (la original y su `-A` cuentan como órdenes distintas; ambas van). (En la verificación sí se conservan las repeticiones con montos distintos.)
- Nombre de archivo: `Layout ｜ [Entidad] ｜ [Ejercicio] ｜ [Fecha] ｜ [Hora].xlsx`.
- La plataforma no tiene límite práctico de filas.
- **Partir Layout** (opcional): N partes iguales (difieren en máximo 1 orden), sin órdenes repetidas, en el orden en que aparecen en el documento base. Cada archivo termina en ` ｜ Parte K` y se pueden descargar juntas en un ZIP o una por una. Mismo documento + mismo N = mismas partes.
- En la verificación se puede elegir **qué parte se está verificando**, para que las órdenes de otras partes no salgan como "No encontradas" (idea propuesta en v0.5.0, aprobada por el usuario el 2026-09-16):
  - "Layout partido en N partes" es **el mismo número** que "Partir Layout" en la etapa 1: cambiarlo en una etapa lo cambia en la otra. 1 = sin partir.
  - "Parte a verificar": Todas las órdenes, o Parte K de N (la lista sale de N, no es fija).
  - Las órdenes de cada parte se calculan con el **mismo reparto** que "Partir Layout" sobre el documento base, así que coinciden con el Layout que se subió a la plataforma. Si el documento base está cargado, se muestra cuántas órdenes se esperan y de cuál a cuál.
  - Requisito: usar el mismo documento base con el que se generó el Layout; con otro documento las partes no coinciden.
  - Las partes se reparten por **órdenes únicas** (cada orden en la parte de su primera aparición). Al verificar una parte se toman esas órdenes **con todas sus filas** del documento base (todos sus montos), aunque las filas repetidas estén lejos en el Excel. Ejemplo: 10 órdenes con repeticiones partidas en 10 → cada parte es 1 orden con todas sus filas.

### PDFs: órdenes de pago mezcladas con documentos de soporte

- Los PDFs **no traen solo órdenes de pago**: cada orden va acompañada de su documentación de soporte (transferencias bancarias, detalles, etc.), todo en el mismo archivo.
- La herramienta debe **distinguir qué páginas son orden de pago** y cuáles son soporte, y validar solo las de orden de pago.
- Riesgo a cuidar: el soporte puede mencionar el número de orden (p. ej. la referencia de una transferencia). El número, el ejercicio, los montos, las firmas y los sellos se leen **solo de la página de la orden**, nunca del soporte.
- Ventaja: identificar las páginas de soporte antes de leerlas permite **saltarse su OCR** y acelerar el análisis.
- **El orden de las páginas varía:** el soporte puede ir antes, después o entre páginas de la orden. No se puede asumir "orden → soporte".
- **Una orden puede ocupar varias hojas:** listas de montos largas que continúan en otras páginas y firmas en una página aparte. La orden se arma como un solo documento (primera hoja + continuaciones + hoja de firmas); montos se buscan en todas sus hojas y firmas en la hoja de firmas.
- **Orden partida y desordenada** (sus hojas regadas entre la documentación, sin orden): poco común. No se intenta rearmar: **Incorrecto** con motivo "Orden partida y desordenada en el PDF: revisar manualmente".
- **Ubicación del número:** no siempre está en la esquina superior. Puede haber un **número de folio** arriba y el número de orden debajo o cerca del centro.
- **El folio cuenta como candidato** (aclaración del usuario, 2026-09-17): hay órdenes que usan el folio *como* número de orden. Entonces no se descarta ningún número por venir etiquetado como folio:
  - Se juntan **todos** los números de la página (folio incluido) y se comparan contra las órdenes del documento base.
  - Si el folio coincide con la orden buscada, la orden queda identificada y el número se da por **Correcto**.
  - Si el folio **no** coincide, no concluye nada: no genera "número distinto", solo se sigue buscando el número en el resto de la hoja y en las demás hojas de la orden.
  - Solo cuando ningún número de la orden coincide con el documento base se reporta que no se encontró.
  - En la práctica la etiqueta "Folio" deja de importar: lo que decide es si el número corresponde a una orden solicitada.
- **Órdenes ADEFA** (Adeudos de Ejercicios Fiscales Anteriores), con sufijo `-A` (p. ej. `1900000000-A`): continuación de una orden original cuyo monto no se pagó completo; se siguen pagando en ejercicios posteriores. Solo existe el sufijo `-A` (no `-B`, `-C`).
  - Son **órdenes distintas** de su original: montos propios y pueden tener firmas diferentes.
  - En los PDFs suelen venir junto a la original sin sufijo.
  - **Verificación exacta:** si se pide `…-A` se busca la `-A`; si se pide la original, la original. Nunca se cruzan.
  - La original y su `-A` **no** son duplicados (son números distintos): no van a Revisión manual por eso.
  - Que una página de `-A` muestre también el número original **no** es "número distinto".
  - Riesgo de lectura: si no se puede confirmar si el sufijo `-A` está o no, el resultado es *Ilegible*, nunca se asume.
- **Soporte:** no se valida (solo en casos extraordinarios de datos incorrectos, que se revisan a mano).
- **Orden sin soporte** o **soporte sin orden:** **Revisar**.

## Principios

- **Privacidad:** los PDFs y el Excel se procesan en la computadora del usuario (en el navegador). Nada se sube a servidores ni a servicios de IA.
- **Nunca adivinar:** si no hay certeza, el resultado es *Revisar* o *Ilegible*, nunca *Correcto*.
- **Los archivos originales no se modifican.** Todo cambio (renombres, carpetas) se aplica en la salida.

## Entrada

- Carpeta con PDFs escaneados (mismo formato de OP en todos).
- Excel con las OP solicitadas. Columnas habituales: `Op`, `Ejercicio`, `Monto` (opcional), `Notas` (texto libre del usuario, no estructurado).
  - Una misma OP puede aparecer en varias filas con montos distintos.
  - La celda de monto puede venir vacía → ese renglón no se valida por monto.

## Qué revisar (casillas elegibles por corrida)

| Casilla | Regla |
|---|---|
| Orden de pago | El número mencionado y el mostrado en el documento coinciden, y corresponden al Excel |
| Ejercicio | Solo importa el **año**; debe ser el del Excel |
| Monto | El monto solicitado debe aparecer **en algún lugar de la lista** de montos de la OP (una línea o el total), al centavo. Si hay uno casi igual, se menciona (p. ej. "difiere por $0.01") |
| Firmas | Deben ser **3 firmas en total**, a mano, en la parte inferior. Los cargos de quienes firman varían, así que no se valida quién firma, solo que sean 3. Una orden puede traer **0, 1, 2 o 3 firmas**: se reporta el conteo ("Sin firmas (0 de 3)", "Solo 1 de 3 firmas", "Solo 2 de 3 firmas"). Frecuencia real: lo común es que **falte 1 firma**; **sin firmas** es raro y suele estar justificado, pero se marca como **Incorrecto** con su motivo (el usuario lo corrige con "Corregir estado" si está justificado); **1 de 3** prácticamente no ocurre. Solo se detecta presencia, no autenticidad |
| Sellos | Azules o negros, en cualquier posición, a veces encima de firmas. Se verifica que **haya sello**. Un sello encima de una firma **no** es motivo de revisión por sí mismo (aclaración del usuario, 2026-09-17: era una preocupación técnica, no una regla); solo si por culpa del sello **no se puede saber** si la celda está firmada, esa firma queda sin determinar y la orden va a *Revisar* |

Localizar la OP en los PDFs se hace siempre (es la base de todo). Lo no marcado sale como "No revisado".

## Estados

| Estado | Significado |
|---|---|
| **Correcto** | Se leyó con certeza y cumple |
| **Incorrecto** | Se leyó con certeza y no cumple (con motivo) |
| **Revisar** | Se leyó pero hay ambigüedad, o hay copias de la OP en conflicto |
| **Ilegible** | Mala calidad: no se puede leer con certeza. Se reporta por dato, no por orden completa |

Señales de ilegibilidad: confianza del OCR, que la lista de montos no sume el total, calidad de imagen (borrosa, clara, chueca).

## Procesamiento de imagen

Se **descarta la plantilla fija** (una orden bien escaneada como referencia de posiciones): las órdenes no respetan un solo acomodo (hojas de continuación, firmas en hoja aparte, folio arriba o no, número en distintas posiciones). Nada depende de coordenadas fijas.

Por página: enderezar → limpiar → clasificar → leer → validar.

1. **Enderezar sin plantilla:** rotación 90°/180° y corrección de inclinación a partir de las líneas de texto y los bordes de tablas de la propia página.
2. **Limpiar:** binarización adaptativa, contraste.
3. **Clasificar la página por su contenido**, no por posición: orden de pago (primera hoja), continuación de lista de montos, hoja de firmas o soporte. Señales: textos que siempre aparecen (título, etiquetas de campos, "TOTAL"), estructura de tabla, líneas de firma con nombre y cargo debajo.
4. **Leer buscando, no en zonas fijas:** número de orden = cualquier número de la página que coincida con una orden del documento base (incluido `-A`); montos = importes en la tabla/lista; firmas = trazos sobre las líneas de firma que se detecten, estén donde estén; sellos = manchas circulares/rectangulares de tinta azul o negra.
5. **OCR completo de la página** cuando haga falta (las zonas ya no son fijas); para compensar velocidad, primero una clasificación barata para saltarse el soporte.

*A validar en la fase 0 con PDFs reales:* qué elementos aparecen siempre en todas las variantes (para clasificar) y si alguna variante sí conviene tratarla con plantilla.

## Duplicados

1. **Archivo idéntico** (misma huella de bytes): se omite sin leerlo.
2. **Página idéntica** (misma huella visual): no se vuelve a leer.
3. **OP ya verificada como Correcta** en otro archivo: no se revisa de nuevo.
4. **Dos o más archivos distintos con la misma OP y el mismo ejercicio:** los archivos van a una carpeta aparte para revisión manual, y el Excel lleva una nota explicando la situación.

## Renombres

Si un archivo trae más de una OP, se renombra con todas sus OP en orden de aparición, separadas por `_`:

- `1900000001_1900000002_1900000003.pdf`
- Si son más de 20 OP o el nombre no cabe (límite de Windows ~255 caracteres): `PrimeraOP_al_UltimaOP_(N OPs).pdf`, p. ej. `1900000001_al_1900000087_(87 OPs).pdf`

## Salida

### Nombre de la entidad y nombres de archivo

- La configuración tiene un campo **Nombre de la entidad** (obligatorio para descargar). Se recuerda en el navegador para la siguiente vez.
- Formato: `[Tipo] ｜ [Entidad] ｜ [Ejercicio] ｜ [Fecha] ｜ [Hora]`
  - **Separador:** ` ｜ ` (espacio, barra de ancho completo U+FF5C, espacio). El usuario pidió `|`, pero Windows no lo permite en nombres de archivo; U+FF5C se ve igual y sí está permitido. Contras aceptados: no se puede teclear para buscar y algún programa viejo podría mostrarlo raro.
  - **Tipo:** `Tabla` para el Excel de resultados; *vacío* para la carpeta o comprimido (el nombre empieza directo con la entidad, sin separador inicial); `Layout` para un archivo que el usuario explicará más adelante.
  - **Ejercicio:** el del Excel de entrada; si trae varios, rango `2021-2022`.
  - **Fecha y hora:** momento en que se crea el archivo. Formato `DD-MM-AAAA` y `HH-MM` (24 h). Día primero para que el año de la fecha no se confunda con el ejercicio que va justo antes; la hora con guion porque Windows no permite `:` en nombres. *Confirmado.*
  - Se quitan de la entidad los caracteres que Windows no permite: `\ / : * ? " < > |`, y también `｜` para no confundir el separador.
- Ejemplos: `Tabla ｜ Entidad de Ejemplo ｜ 2021 ｜ 14-09-2026 ｜ 16-05.xlsx` y `Entidad de Ejemplo ｜ 2021 ｜ 14-09-2026 ｜ 16-05.zip`.
- **Parte:** si se verifica una parte de un Layout partido, el Excel y la carpeta terminan en ` ｜ Parte K`, igual que el Layout de esa parte (pedido del usuario, 2026-09-16: si no, no se distingue de una verificación completa). La fila de datos del Excel también dice `Parte K de N`. Ejemplo: `Tabla ｜ ENTIDAD DEMO ｜ 2021 ｜ 16-09-2026 ｜ 17-54 ｜ Parte 10.xlsx`.

### Excel de resultados

- **Con diseño**, misma identidad que la página: título en banda azul tinta, fila con entidad/ejercicio/fecha de generación/conteos, encabezados con color (validaciones en otro tono), filas alternadas, bordes finos, Estado y validaciones con color por estado, montos con formato `$#,##0.00`, filtros, encabezado y primera columna fijos, sin cuadrícula y color de pestaña por hoja. (La librería gratuita SheetJS no escribe estilos; se usa ExcelJS.)

- **Verificación:** columnas de lo marcado en "Qué revisar" + Estado + Motivo + Archivo (nombre nuevo) + Página.
- **No encontradas.**
- **Duplicados omitidos:** archivo omitido y de cuál es copia.
- **Renombres** *(opcional, casilla)*: nombre original → nombre nuevo.

### Carpeta de archivos

PDFs sin duplicados y ya renombrados, más la subcarpeta de revisión manual. Formato elegible, **ZIP por defecto**; otras opciones de formatos universales (por definir tras medir). RAR descartado: formato propietario que no se puede generar libremente.

## Recomendaciones para la versión real

Acordadas durante el diseño del boceto. No son opcionales: son parte de lo que la herramienta debe cumplir.

### Volumen

- Debe soportar corridas especiales de hasta **3,000 órdenes** (estimado: 6,000–15,000 páginas únicas) y archivos individuales de 3,000+ páginas.

### Tabla

- **Tabla virtualizada:** solo se dibujan las filas visibles (~40) y se reemplazan al desplazarse. Filtrar, buscar, cambiar casillas y navegar con ↑ ↓ debe sentirse instantáneo con 3,000 filas o más.
- La vista previa y la navegación con teclado funcionan igual sin importar la cantidad de filas.

### Velocidad del análisis

- **Duplicados primero:** descartar archivos idénticos por huella antes de leer cualquier página.
- **Clasificar primero** con un análisis barato para no leer a detalle las páginas de soporte; firmas y sellos se revisan por análisis de imagen, sin OCR.
- **Procesamiento en paralelo:** usar varios núcleos del procesador a la vez (Web Workers).
- **Medir antes de prometer:** el tiempo por página se mide con escaneos reales en la computadora del trabajo. Estimación inicial muy gruesa para 10,000 páginas: 20 min a 1 h.

### Corridas largas sin fragilidad

- **Progreso guardado en el navegador:** si se cierra la pestaña, se reinicia la computadora o se va la luz, el análisis se reanuda donde se quedó.
- **Avance con tiempo estimado:** p. ej. "Página 4,210 de 11,380 · faltan ~18 min".
- **Evitar que la computadora se suspenda** mientras analiza (Wake Lock).
- **Memoria bajo control:** no guardar imágenes de páginas; la vista previa vuelve a dibujar la página desde el PDF al seleccionarla.

### Uso

- La configuración se oculta sola al terminar la verificación y deja una línea con lo elegido.
- **Corrección manual de estado** (desde la vista previa, "Corregir estado"):
  - Se elige el nuevo estado y se escribe una **nota obligatoria** (p. ej. "Sin firmas, justificado por oficio 123/2021").
  - Si la orden tiene varias filas, se puede aplicar a todas.
  - En la tabla: estado nuevo + marca ✎; filtro "Corregidas a mano"; los conteos del resumen se actualizan.
  - Se puede editar o deshacer (vuelve el estado detectado).
  - En el Excel, hoja Verificación: **Estado final**, **Estado detectado** y **Nota de corrección**; el título incluye cuántas se corrigieron.
  - Las correcciones forman parte del progreso guardado.
- Página instalable (app web) para que funcione sin internet incluso al abrirla.
- Selector de tema **Claro / Oscuro / Automático** en el encabezado; se recuerda en el navegador. Automático sigue el tema del sistema (o del visor de Claude).

## Guía de uso

- Botón **Guía** en el encabezado (junto al tema): abre una vista con índice lateral y 10 secciones para compañeros que nunca han usado la herramienta: qué es, antes de empezar, Preparar Layout, subir a la plataforma, Verificar órdenes, leer resultados, corregir estado, descargas, reglas y preguntas frecuentes. Botones para ir directo a cada etapa y "Volver a la herramienta".
- Lo que depende de la fase 0 (elegir PDFs y documento base en la etapa 2, Verificar, carpeta de archivos) va marcado **Próximamente**; la guía remite a "Ver demostración".
- **Mantenerla al día:** todo cambio de interfaz o de reglas se refleja también en la guía.
- Aprobada por el usuario tal cual (2026-09-16): "Está muy bien, déjalo así". No hace falta el Word descargable.

## Fase 0 — medición sobre un PDF real (2026-09-17)

`fase0/medidor.html` (se abre con `fase0/servir.sh`) mide un PDF en el navegador y
reporta página por página. Todo local; el PDF no se sube a ningún lado. Detalle en
[`fase0/README.md`](../fase0/README.md).

### Lo que resultó ser el PDF de la plataforma

Medido en un PDF real de 23 páginas (no vive en el repo):

- Escaneado con PaperStream (escáner Fujitsu), **200 ppp, a color, sin capa de texto**: el OCR es obligatorio.
- **La orientación cambia entre páginas:** la primera venía apaisada y el resto vertical.
- **Un PDF puede traer varias órdenes.** Ese archivo, nombrado con una sola orden, traía **siete**, y el patrón se repite: `ORDEN DE PAGO → SOLICITUD DE PAGO → LIBERACIÓN DE TRANSFERENCIAS`, una terna por orden.
- La primera página es un **listado** que menciona las siete órdenes juntas. Una página de soporte puede nombrar muchas órdenes: por eso "la página trae un número de orden" **no** alcanza para decir que es una orden.
- La página de la orden se reconoce por el encabezado (`GOBIERNO DEL ESTADO DE …` / `ORDEN DE PAGO`) y trae el número en una caja arriba a la derecha, rotulada `Orden de Pago`, con `ORIGINAL` debajo.
- Hay muchos números de 10 dígitos que **no** son órdenes: cuenta CME, centro gestor, cuenta contable, documento compensatorio, folio interbancario del banco. Sin el documento base no se puede decidir cuál es la orden.
- **Las firmas no van sobre una raya:** van en tres celdas al pie (`SOLICITANTE`, `AUTORIZACIÓN DEL TITULAR`, `PÁGUESE`), escritas encima del nombre impreso.
- Sellos grandes (`REVISADO`, `RECIBIDO`, `PAGADO`) atraviesan el documento, a veces de cabeza o encima de una firma.
- Hay marcas de pluma a mano por toda la hoja, y en una de las siete **una raya roja cruzaba los dígitos del número**.

### Cómo se lee, y por qué así

1. **Render a 300 ppp.** El escaneo es de 200 ppp; a menos de 300 el número chico no se lee.
2. **Borrar la tinta de color.** La impresión es negra o gris; pluma y sellos traen color. Se blanquea todo píxel con color y el OCR deja de tropezar: fue lo que destrabó la página con la raya roja encima del número.
3. **Franja del encabezado** (una tira angosta de arriba, OCR barato) para decidir qué documento es. Clasificó **7 de 7 órdenes sin un solo falso positivo** entre 23 páginas.
4. **Solo en las páginas de orden**, la caja del número: recorte chico, OCR con `PSM 4` y lista de caracteres `0123456789-A`. Se intenta con hasta cinco recortes/escalas porque la caja se mueve con el escaneo; **6 de 7 salieron al primer intento**.
   - `PSM 6` **no sirve** aquí: fue lo que hacía fallar todas las lecturas al principio.
   - Ampliar el recorte al doble ayuda en unas páginas y arruina otras: por eso se prueban varias escalas en vez de buscar una receta única.
   - La `A` de ADEFA debe ir en la lista de caracteres; si no, `…-A` se lee como su original, que es justo el cruce prohibido. Tiene que venir pegada al número (si no, la `A` de `ORIGINAL` se cuela).
5. **El documento base decide.** Cada candidato se confirma contra la lista de órdenes solicitadas. Si coincide más de uno (por ejemplo una orden y su `-A`), no se adivina: queda ambiguo, para revisar.
6. **Firmas por tinta de color** en las tres celdas del pie: la firma es de pluma, el nombre impreso es negro. Umbral de partida 0.8 % de píxeles con color por celda.

### Los demás campos

Cada campo vive en su zona y se lee igual que el número: recorte chico, sin color y
con la lista de caracteres que le toca.

- **Monto:** banda de la tabla de importes y los totales. Se toma el mayor (el neto a pagar) y se guarda la lista completa, porque la regla permite que el monto pedido esté en una línea o en el total.
- **Fecha:** caja de `Fecha de expedición`, arriba a la derecha. Lo que importa es el **año**: en una de las siete el OCR erró el día (`65/06/2021`) y el año salió bien en todas.
- **Hojas:** el `Página X / Y` del pie solo se leyó en 2 de 7 (renglón chico y hoja chueca). **No hace falta:** si dos páginas de orden seguidas traen el mismo número, es una orden de varias hojas. Se deja como dato extra, no como base de la regla.

### Resultados

El usuario confirmó que las siete órdenes de ese PDF son de **una página y están
completas** (número, montos, 3 firmas): sirve como caso de prueba con respuesta
conocida, y el resultado esperado es **Correcto en las siete**.

| Medida | Resultado |
|---|---|
| Páginas clasificadas como orden | 7 de 7, sin falsos positivos entre 23 |
| Número de orden confirmado | **7 de 7** (5–6 al primer intento) |
| Monto correcto | **7 de 7**, cotejado contra el listado de la primera página |
| Ejercicio (año de la fecha) | **7 de 7** |
| Firmas detectadas | **3 de 3 en las siete** (21 celdas de 21) |
| `Página X / Y` | 2 de 7 (no se usa; ver arriba) |
| Tiempo por página | **0.95 s** con todos los campos (0.55 s si solo se clasifica y se lee el número) |
| Proyección | 500 páginas ≈ 8 min · **3,000 páginas ≈ 47 min** |

Con un PDF sintético del mismo formato (`fase0/generar-pdf-de-prueba.py`) el conteo
de firmas acierta en las seis órdenes (3, 2, 1, 0, 3 y 2 firmas) y el número sale
en 5 de 6; falla la orden que lleva una raya de pluma gruesa encima de los dígitos,
que queda como "no se leyó" → Revisar, nunca adivinado.

**Decisión: la página web alcanza.** 27 minutos por 3,000 páginas en esta máquina
(Intel i5-9500, gráficos integrados) no justifica un programa instalable. La clave
fue dejar de hacer OCR de la página completa (2.9 s por página, y ni así leía el
número) y leer solo dos zonas chicas.

### Sellos (medido el 2026-09-17)

El usuario confirmó que **la presencia del sello cuenta**, no solo si tapa una firma.
Lo que se midió en las siete órdenes reales:

| Elemento | Color (máx−mín de RGB) | Tinta más oscura |
|---|---|---|
| Texto y reja impresos | 2 (nada) | llega a negro (p10 ≈ 25) |
| Sello azul (`RECIBIDO`) | 45 | gris medio (p10 ≈ 125) |
| Sello despintado (`REVISADO`) | 37 — **sí tiene color** | gris medio (p10 ≈ 125) |
| Sello `PAGADO` diagonal | 2 — de verdad gris | nunca llega a negro (p10 ≈ 99) |

De ahí sale la regla: **tinta añadida = la que tiene color, o la que es gris parejo y
nunca llega a negro**. Lo impreso siempre tiene núcleo negro; el sello, aunque se vea
gris, no. Así se detectan sellos de cualquier color, en cualquier posición y de cabeza,
porque no se busca forma ni texto, sino manchas de tinta añadida.

Después se limpian dos cosas que no son sellos:

- **Las rayas del formato:** se borran las corridas largas y rectas. Un sello son arcos cortos; la reja de la tabla, líneas largas.
- **El escudo del membrete:** mide 0.09 del ancho de la hoja y cualquier sello pasa de 0.13, así que basta un mínimo de tamaño.
- **Las firmas:** una mancha que **nace** dentro de la banda de firmas es la firma, aunque su lazo se salga de la celda (corregido el 2026-09-17 tras revisión del usuario: la firma del *Páguese* tiene un lazo grande que cruzaba a la celda vecina y se contaba como sello). Medido: las firmas empiezan en y ≥ 0.84; un sello que llega a taparlas viene bajando y empieza en y ≈ 0.66-0.71.
- **Las rayas de pluma:** aunque sean largas y diagonales, no encierran nada. Se exige que la mancha **encierre hueco**, porque un sello es un aro. Eso descartó unas rayas de pluma azul que cruzaban la tabla de una orden.

### Contar sellos, no solo detectarlos (2026-09-17)

El usuario revisó la salida dibujada y pidió el **conteo**: cada orden trae 3 sellos, y
la versión por manchas contaba 2, 2 y 1 en tres hojas porque **dos sellos encimados son
una sola mancha**, y porque un `PAGADO` muy despintado no aparecía.

La solución es mirar **aros en vez de manchas**: dos sellos encimados siguen siendo dos
aros. Cada píxel de tinta añadida vota por el centro de un posible aro (transformada de
Hough circular), los votos se concentran en los centros reales, y cada candidato se
verifica preguntando **qué fracción del anillo tiene tinta** — eso es lo que separa un
sello de un garabato o de un renglón.

Umbrales calibrados con este PDF: cobertura del anillo ≥ 0.75 y fuerza del pico ≥ 0.60
del máximo de la hoja. Los sellos legítimos dan cobertura 0.79–0.98; el candidato falso
que apareció daba 0.71.

**Resultado: 3 sellos en las 7 órdenes, que es el conteo del usuario.**

### Pero el conteo no es confiable, y por eso no decide nada (2026-09-17)

Se probó con más de tres sellos, pegando sellos **reales** del propio PDF en hojas
nuevas (misma geometría, tinta encima como un sello de verdad):

| Hoja | Sellos reales | Detectados |
|---|---|---|
| 3 originales + 1 pegado | 4 | 5 |
| 3 + 2 pegados | 5 | 6 |
| 3 + 3 pegados | 6 | 7 |
| 3 + 2 pegados muy encimados | 5 | 6 |

Siempre uno de más: el sello pegado cayó sobre la tabla y **se partió en dos
detecciones**, una sobre cada extremo de la palabra. Y no se puede arreglar juntando
detecciones cercanas, porque en la orden de la página 21 **dos sellos distintos tienen
sus centros más cerca** (10 % del ancho) que las dos mitades del sello partido (15 %):
por geometría, un sello ancho partido y dos sellos encimados se ven igual.

**Decisión del usuario (2026-09-17): lo que se verifica es que HAYA sello**, no cuántos.
La presencia es robusta (7 de 7, sin confundir firmas, rayas de pluma ni la reja). El
número de aros se muestra en la tabla marcado como aproximado y **no afecta al estado**.

Contar bien exigiría reconocer el dibujo de cada sello (comparar contra recortes de los
sellos de la dependencia, en varios giros), que es bastante más caro y necesita esos
recortes. Queda como posibilidad si algún día el conteo importa.

Quedan dos miradas al mismo problema, cada una para lo suyo:

- **Aros** → cuántos sellos hay.
- **Manchas** (la detección anterior) → hasta dónde llega la tinta de cada sello, que es
  lo que se descuenta de las celdas de firma. Una mancha solo cuenta como sello si tiene
  un aro detectado dentro, para que la mancha de una firma no se descuente a sí misma.

**Límites conocidos:** los radios de búsqueda están calibrados al tamaño de sello de
este documento; sellos mucho más grandes o más chicos necesitarían reajuste, y con un
PDF de prueba de geometría distinta el conteo se infla. Hace falta otro PDF real, de
otra entidad, para saber si los umbrales aguantan.

### Sello encima de firma: sí se pueden separar (probado el 2026-09-17)

La duda del usuario era técnica: si un sello cae sobre una firma, ¿se puede saber
todavía si la celda está firmada? Se probó fabricando el caso que no existe en el PDF
real: una orden **sin ninguna firma** con dos sellos grandes encima de las tres celdas,
y la misma orden **con las tres firmas** y los mismos sellos.

- Sin descontar el sello, la orden sin firmas reportaba **3 de 3 firmas**: un falso grave.
- Descontando del conteo la tinta que cae dentro del recuadro de un sello detectado:
  la orden sin firmas da **0 de 3** y la firmada da **3 de 3**. La firma se reconoce
  debajo del sello porque sus trazos salen del aro.
- Dentro de la banda de firmas se le exige más hueco a una mancha para contarla como
  sello (medido: el lazo de una firma encierra ~31; un sello encima, ~484).
- Si una celda queda cubierta por un sello y no queda tinta de pluma fuera de él, no se
  adivina: la firma se marca **tapada** (sin determinar) y eso manda la orden a *Revisar*.

Cuesta ~68 ms por orden; como solo se hace en las páginas de orden, sobre el total son
unos 20 ms por página: el proceso completo pasa de ~150 a ~170 ms por página.

Resultado: **7 de 7 órdenes con sello detectado**, entre uno y tres por orden (cuando
dos sellos vienen encimados se cuentan como una sola mancha), sin confundir la reja, el
escudo, las firmas ni las rayas de pluma. El usuario revisó la salida dibujada sobre las
hojas y ya no encontró falsos. 
**Frecuencia (dicha por el usuario, 2026-09-17):** casi siempre traen sello; sin sello
es muy raro. Aun así no hay en este PDF ninguna orden sin sellar, así que no está
medido cuántas veces diría "hay sello" donde no lo hay. Como el caso es raro, conviene
que la falta de sello mande a **Revisar** y no a Incorrecto, hasta tener un ejemplo.

### Velocidad: de 47 minutos a 7 (medido el 2026-09-17)

El usuario pidió exprimirlo. Cuatro cambios, todos dentro del navegador:

| Cambio | Antes | Después |
|---|---|---|
| **Decodificar el JPEG con el navegador.** Cada página del escaneo es un JPEG entero dentro del PDF; pdf.js lo decodifica en JavaScript, `createImageBitmap` usa el decodificador del navegador | 229 ms | **25–35 ms** |
| **Repartir el OCR en los seis núcleos** con trabajadores | 1 hilo | **4.05× más rápido** |
| **Renderizar a 200 ppp** (la resolución real del escaneo) en vez de 300 | — | menos trabajo, misma lectura |
| **Banda de montos recortada**, con la banda ancha solo cuando un sello tapa las cifras | 1,005 ms por orden | **317 ms** |

El resultado, sobre el mismo PDF real de 23 páginas y sin perder nada:

| | Antes | Ahora |
|---|---|---|
| Tiempo por página | 946 ms | **~150 ms** (150–220 según qué tan caliente esté el equipo) |
| 3,000 páginas | 47 min | **~8 min** |
| Número, monto, ejercicio | 7 / 7 | 7 / 7 |
| Firmas | 21 / 21 celdas | 21 / 21 celdas |

Cómo queda repartido el trabajo: el hilo principal solo decodifica (≈32 ms) y recorta
(≈74 ms); todo el OCR (≈600 ms por página) se va a los seis trabajadores, que lo
convierten en ≈100 ms. El piso teórico con este diseño es ~140 ms por página.

**Nota sobre los tiempos:** con los seis núcleos al tope el procesador baja su
frecuencia, así que la misma corrida da entre 150 y 220 ms por página. Los números
de arriba son corridas en frío.

### ¿Y un programa instalable? (medido el 2026-09-17)

Ya no: la ventaja se evaporó al usar bien el navegador.

| Parte | Navegador | Nativo |
|---|---|---|
| Decodificar la página | **25–35 ms** (`createImageBitmap`) | 103 ms (Pillow/C sobre el mismo JPEG) |
| OCR, 1 hilo | 235 ms | ~1.5× más rápido (estimado; no hay Tesseract nativo instalado para medirlo) |
| Repartir en 6 núcleos | 4.05× (medido) | similar |

El navegador **le gana** al código nativo decodificando, porque usa el mismo
decodificador en C++ del sistema. Lo único donde pierde es el OCR, por ser WebAssembly.
Un programa instalable quedaría alrededor de 5–6 minutos contra los ~8 de la página:
no paga el costo de instalarlo en la computadora del trabajo.

## Lo que está calibrado con una sola muestra (2026-09-17)

Advertencia del usuario: el PDF con el que se midió todo trae **órdenes de una sola
página y completas**, de una dependencia, un ejercicio y un escáner. Falta ver la
variedad real. Lo que sigue es qué supone la lectura hoy y **cómo se rompe** con otras
variedades, para saber qué ejemplos conviene conseguir.

| Lo que se supone hoy | Con qué variedad se rompe | Qué pasaría |
|---|---|---|
| El número vive arriba a la derecha (se prueban 5 recortes) | Otro formato de orden, otra dependencia | No se lee el número → la orden no se identifica |
| La fecha está en la caja de arriba a la derecha | Ídem | Sin ejercicio → Revisar |
| Los montos están en la mitad derecha de la tabla (con respaldo a la banda ancha) | Ídem, u orden con la lista de montos en otra hoja | Monto incompleto o ausente |
| Tres celdas de firma al pie, en `y` 0.82–0.98 | Firmas en hoja aparte, u otro acomodo | Reporta 0 de 3 firmas y marca Incorrecto una orden que sí está firmada |
| Una orden = una página | **Orden de varias hojas** | Los montos de las hojas siguientes no se suman, y la hoja de firmas se clasifica como soporte |
| El encabezado dice `ORDEN DE PAGO` | Continuación sin encabezado | La hoja se toma como soporte y no se lee |
| Página vertical | Orden apaisada o girada 90° | Todas las zonas quedan fuera de lugar |
| **Escaneo a color** | **Escaneo en gris o blanco y negro** | Se cae lo más valioso: sin color no se separan sellos ni firmas de la tinta impresa |
| Sellos de ~0.26 del ancho | Sellos mucho más grandes o chicos | Se dejan de detectar (la presencia es lo que decide, así que iría a Revisar) |
| 200 ppp, un JPEG por página | Otro escáner o PDF con varias imágenes por hoja | Se cae solo a pdf.js: más lento, pero sigue leyendo |

**Ejemplos que más falta conseguir**, en orden de valor:

1. Una **orden de varias hojas** (lista de montos larga o firmas en hoja aparte).
2. Un PDF de **otra dependencia o otro ejercicio**, para ver si el formato se mueve.
3. Una orden **sin sello** y otra con **firmas faltantes**, para calibrar los umbrales con el caso negativo (hoy solo está probado con casos completos).
4. Una **ADEFA** real (`-A`), que no apareció en ningún archivo revisado.
5. Si existen, un escaneo **en gris** y una hoja **girada**.

El arreglo estructural para los cuatro primeros renglones de la tabla es dejar de usar
zonas fijas y **ubicar cada dato por su rótulo** (buscar "Orden de Pago", "Fecha de
expedición", "Monto Neto a Pagar", "SOLICITANTE" con OCR y leer al lado). Se probó una
primera versión con anclas y salió peor que las zonas fijas (1 de 7 contra 7 de 7),
porque leer una franja grande diluye el texto chico; la vía es buscar el rótulo en una
franja angosta y de ahí saltar al dato.

## Pendiente

Estado al 2026-09-17 (v0.10.0):

- **Etapa 1, Preparar Layout: funcional** y probada por el usuario con un documento base real.
- **Etapa 2, Verificar órdenes:** interfaz lista con demostración; todavía no procesa PDFs.
- **Fase 0: terminada.** La lectura de PDFs reales está medida y resuelta (arriba).

Siguiente paso:

1. Llevar la receta de la fase 0 a la etapa 2 de la página: cargar los PDFs, clasificar
   páginas, leer el número, confirmarlo contra el documento base y armar el resultado.
2. Reglas que ya se pueden decidir con lo medido: una orden se arma con su página de
   orden (el soporte que la acompaña no se valida) y el estado sale de número +
   ejercicio + montos + firmas.
3. Falta medir, cuando haya ejemplos: montos y fecha de la orden (hoy solo se leen con
   el OCR completo, que es lento), órdenes de varias hojas reales, una ADEFA real (no
   hubo ninguna en los documentos base revisados) y páginas giradas 90°.
