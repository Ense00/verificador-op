# Historial de cambios

Formato: versión — fecha — qué cambió. Las versiones 0.x son de desarrollo.

## v0.9.1 — 2026-09-17

- **El folio ya no se ignora** (aclaración del usuario): hay órdenes que usan el
  folio como número de orden. Ahora todos los números de la página, folio
  incluido, se comparan contra el documento base: si el folio coincide con la
  orden buscada, la orden queda identificada; si no coincide, no concluye nada y
  se sigue buscando el número en el resto de la hoja. La etiqueta "Folio" deja de
  tener efecto propio.
- El medidor muestra el folio de cada página y marca si tiene forma de número de
  orden; el resumen dice cuántas páginas se identificaron por el folio.
- El PDF de prueba trae una orden que usa el folio como número de orden.
- Guía de la página y `docs/requisitos.md` actualizados con la regla nueva.

## v0.9.0 — 2026-09-17

- **Medidor de la fase 0** (`fase0/medidor.html`): abre un PDF y reporta, página
  por página, si ya trae texto, tiempo de render y de OCR, número de orden leído
  (incluido `-A`), montos, fechas, clase de página (orden / soporte / dudosa),
  líneas de firma y cuáles traen tinta, tinta, color e inclinación. Resumen con
  la proyección a 500 y 3,000 páginas y exportación a JSON. Todo en el navegador.
- Vista de revisión: muestra la página **ya enderezada** con las líneas
  detectadas y la franja donde se busca la firma, para ver dónde se equivoca.
- `fase0/servir.sh` levanta el servidor local y abre el medidor;
  `fase0/generar-pdf-de-prueba.py` genera un PDF sintético con datos inventados
  para probarlo sin documentos reales.
- Detección de líneas: se endereza la página antes de buscarlas (si no, una raya
  inclinada 1.5° no cae en una sola fila y no se detecta ninguna), se toman todas
  las corridas de cada fila (las tres líneas de firma están a la misma altura) y
  se exige que sean sólidas, para no confundir renglones de texto con rayas.

## v0.8.0 — 2026-09-16
- Guía de uso dentro de la página: botón **Guía** en el encabezado, índice lateral que marca la sección en lectura, 10 secciones para quien nunca ha usado la herramienta, accesos directos a cada etapa. Lo que aún no funciona va marcado "Próximamente".

## v0.7.3 — 2026-09-16
- Al verificar una parte, el Excel y la carpeta de resultados terminan en ` ｜ Parte K` (como el Layout de esa parte) y la fila de datos del Excel indica `Parte K de N`. Antes se llamaban igual que una verificación completa.

## v0.7.2 — 2026-09-16
- "Parte a verificar" rehecho: antes era una lista fija de 5 partes sin relación con nada. Ahora "Layout partido en N partes" usa el mismo número que "Partir Layout" (sincronizados entre etapas) y la lista ofrece Parte 1..N. Con el documento base cargado muestra cuántas órdenes tiene la parte elegida y su rango. El resumen de configuración indica la parte.

## v0.7.1 — 2026-09-15
- Se quita "Plantilla" de la configuración: las órdenes no respetan un acomodo fijo (varias hojas, firmas aparte, folio o no), así que el análisis se basará en el contenido de cada página y no en posiciones de una plantilla.

## v0.7.0 — 2026-09-15
- Limpieza para parecerse a la versión final: se quitan el sello "Boceto", los avisos de boceto/privacidad, el documento de ejemplo del Layout y las explicaciones en mensajes.
- Verificar órdenes arranca vacía ("Todavía no hay resultados"); un botón discreto "Ver demostración" carga los datos de muestra, marcados con "Demostración" y botón "Salir".
- Acciones aún no disponibles (elegir PDFs, verificar, abrir página, descargar carpeta) muestran "Próximamente.".

## v0.6.5 — 2026-09-15
- Se quita del encabezado el aviso "Los archivos se procesan en esta computadora…".

## v0.6.4 — 2026-09-15
- Encabezado: el aviso de privacidad y el selector de tema van juntos a la derecha, apilados; ya no bajan debajo del título en ventanas medianas.

## v0.6.3 — 2026-09-14
- Layout: incluye órdenes ADEFA (`-A`) como texto con formato General (antes se omitían); acepta variantes como `1900000000 - a`. Aviso con cuántas hay. Documento de ejemplo con algunas ADEFA.

## v0.6.2 — 2026-09-14
- Selector de tema Claro / Oscuro / Automático en el encabezado, recordado en el navegador.
- Los controles nativos (casillas, listas, barras de desplazamiento) siguen el tema.

## v0.6.1 — 2026-09-14
- Corrige el color del texto de la nota de corrección (salía negro en modo oscuro).

## v0.6.0 — 2026-09-14
- Corrección manual de estado: elegir estado nuevo + nota obligatoria, aplicar a todas las filas de la orden, editar o deshacer. Marca ✎ en la tabla, filtro "Corregidas a mano", conteos actualizados.
- Excel: columnas Estado final, Estado detectado y Nota de corrección.
- En el boceto las correcciones se recuerdan en el navegador.

## v0.5.3 — 2026-09-14
- Datos ficticios con la frecuencia real de firmas: casi siempre falta 1; sin firmas es raro; 1 de 3 casi nunca.

## v0.5.2 — 2026-09-14
- Firmas: se contempla 0, 1, 2 o 3 firmas; el motivo dice el conteo ("Sin firmas (0 de 3)", "Solo 1 de 3 firmas"…). Datos ficticios con los tres casos.

## v0.5.1 — 2026-09-14
- La casilla se llama "Partir Layout".
- Preparación de Layout probada por el usuario con un documento base real: funciona.

## v0.5.0 — 2026-09-14
- **Primera parte funcional:** etapa "Preparar Layout". Lee el documento base real (.xlsx) en el navegador, localiza columnas por nombre, ignora filas sin orden (totales), toma el ejercicio del año de la Fecha Contable, quita órdenes repetidas y genera el Layout con la plantilla de la plataforma (números enteros).
- Partir Layout en N partes iguales, descarga por parte o todas en ZIP, con ` ｜ Parte K` en el nombre.
- Resumen del documento: filas, órdenes únicas, ejercicio, filas ignoradas, columnas encontradas y avisos (repetidas, negativos, sin fecha, años mezclados).
- Página organizada en dos etapas (1 Preparar Layout, 2 Verificar órdenes); el nombre de la entidad queda arriba para ambas.
- Verificación (boceto): "Documento base" en lugar de "Excel de órdenes", selector de parte a verificar y montos negativos marcados como Revisar.

## v0.4.4 — 2026-09-14
- Excel de prueba con diseño (ExcelJS en lugar de SheetJS): título y datos de la corrida en banda azul, encabezados de color, filas alternadas, estados con color, formato de moneda, filtros, paneles fijos, sin cuadrícula y pestañas de color.

## v0.4.3 — 2026-09-14
- Separador en nombres de archivo: ` ｜ ` (barra de ancho completo, porque Windows no permite `|`) en lugar de `_`.

## v0.4.2 — 2026-09-14
- Fecha en nombres de archivo como `DD-MM-AAAA` (antes `AAAA-MM-DD`) para no confundirla con el ejercicio.

## v0.4.1 — 2026-09-14
- "Nombre de la entidad" pasa a una franja destacada de ancho completo al inicio de la configuración: paso 1, etiqueta "Obligatorio", campo grande con borde azul y vista previa de los nombres de archivo al lado.

## v0.4.0 — 2026-09-14
- Identidad visual: encabezado en banda azul tinta con sello de fondo, fondo cuadriculado tipo papel contable, tipografía Archivo en títulos, paneles con sombra, pestañas tipo carpeta, filas alternadas, franja de color por estado en cada fila, conteos con fondo de color y vista previa como hoja sobre escritorio.
- Campo "Nombre de la entidad" en la configuración (se recuerda en el navegador) y nombres de archivo `[Tipo]_[Entidad]_[Ejercicio]_[Fecha]_[Hora]` con vista previa; el Excel de prueba ya se descarga con ese nombre.

## v0.3.0 — 2026-09-14
- 3,000 órdenes ficticias generadas (semilla fija, siempre los mismos datos): varios montos por orden, archivos con 1 a 400 órdenes, todos los estados y casos (firmas, año, número, sello sobre firma, escaneo borroso, tabla ilegible, 1 centavo, revisión manual).
- Tabla virtualizada: solo dibuja las filas visibles; encabezado y columna Orden fijos; contador de filas filtradas.
- Navegación con ↑ ↓ RePág AvPág; arrastre en ambas direcciones.
- Exportación real del Excel de prueba (hojas Verificación, No encontradas, Revisión manual, Duplicados omitidos y Renombres opcional) con filtros y formato de moneda.
- Motivo y Archivo en una sola línea con texto completo al pasar el mouse y en la vista previa.

## Sin versión — 2026-09-14
- Requisitos: sección "Recomendaciones para la versión real" (volumen de 3,000 órdenes, tabla virtualizada, velocidad, progreso reanudable, tiempo estimado, evitar suspensión, memoria, uso).

## v0.2.0 — 2026-09-14
- Nuevo acomodo: configuración arriba en horizontal (se puede ocultar y deja un resumen de lo elegido), resumen compacto, tabla abajo y vista previa a la derecha siempre visible.
- Vista previa compacta: orden, estado, archivo/página/monto, resultado de cada validación, hoja con zonas detectadas y botones.
- Navegar entre órdenes con ↑ ↓ (teclado o botones de la vista previa).
- Se quita "Ampliar tabla" (ya no hace falta).

## v0.1.2 — 2026-09-14
- Regla de firmas: basta con que sean 3 firmas en total; los cargos varían y no se valida quién firma. Motivo: "Solo 2 de 3 firmas".

## v0.1.1 — 2026-09-14
- Filtros por estado visibles arriba de la tabla (Todos, Correcto, Incorrecto, Revisar, Ilegible).
- Archivo y Página en columnas separadas; se corrige la columna de archivo aplastada.
- Tabla más compacta: columnas de validación agrupadas bajo "Validación".
- Barra de desplazamiento también arriba de la tabla, arrastre con clic izquierdo, columna Orden fija al desplazar y botón "Ampliar tabla" que oculta la configuración.

## v0.1.0 — 2026-09-14
- Boceto visual de la interfaz en `boceto/` (datos ficticios, no procesa archivos): carga de archivos, casillas de "Qué revisar", opciones de salida, resumen por estado, tabla de resultados con filtros, pestañas de hojas del Excel y detalle por orden.

## v0.0.0 — 2026-09-14
- Arranque del proyecto: requisitos iniciales definidos en `docs/requisitos.md`.
- Sin código todavía; pendiente PDF de ejemplo para la fase 0 (medición).
