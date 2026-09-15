# Historial de cambios

Formato: versión — fecha — qué cambió. Las versiones 0.x son de desarrollo.

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
