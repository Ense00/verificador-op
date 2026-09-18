# Historial de cambios

Formato: versión — fecha — qué cambió. Las versiones 0.x son de desarrollo.

## v0.16.0 — 2026-09-17

- **El conteo de sellos deja de decidir; lo que decide es que haya sello.** Probado con
  más de tres sellos (pegando sellos reales del propio PDF en hojas nuevas), el conteo
  da uno de más: un sello ancho que cae sobre la tabla se parte en dos detecciones, y no
  se puede distinguir de dos sellos encimados, porque en una orden real dos sellos
  distintos están más cerca entre sí que las dos mitades del sello partido.
- La tabla ahora muestra **sí / no** y el número de aros al lado, marcado como
  aproximado. La presencia sí es robusta: 7 de 7 en las órdenes reales.
- En la vista de revisión los sellos se dibujan como elipse (el aro detectado), no como
  recuadro, para no dar a entender que ese es el contorno real del sello.

## v0.15.0 — 2026-09-17

- **Los sellos ahora se cuentan, no solo se detectan.** La versión por manchas contaba 2
  donde había 3 (dos sellos encimados son una sola mancha) y se le perdía un `PAGADO`
  despintado. Ahora se buscan **aros**: cada píxel de tinta añadida vota por el centro de
  un posible aro y cada candidato se verifica midiendo qué fracción del anillo tiene
  tinta. **3 sellos en las 7 órdenes reales**, que es el conteo correcto.
- Se mantienen las dos miradas: los aros cuentan los sellos; las manchas marcan hasta
  dónde llega su tinta para descontarla de las celdas de firma. Una mancha solo cuenta
  como sello si tiene un aro dentro, así la mancha de una firma no se descuenta a sí
  misma (eso hacía perder una firma en una orden).
- Verificado en los dos sentidos: el PDF real da 3 sellos y 3 firmas en las siete
  órdenes; el caso fabricado con sellos encima de celdas vacías da 0 firmas, y con
  celdas firmadas da 3.

## v0.14.0 — 2026-09-17

- **Un sello encima de una firma ya no la inventa.** Se probó el caso a propósito: una
  orden sin ninguna firma con sellos sobre las tres celdas se reportaba como *3 de 3
  firmas*. Ahora la tinta que cae dentro de un sello detectado no cuenta como firma: esa
  orden da 0 de 3 y la misma orden firmada sigue dando 3 de 3, porque los trazos de la
  firma salen del aro del sello.
- Nuevo estado de firma **tapada**: celda cubierta por un sello y sin tinta de pluma
  fuera de él. No se decide, se manda a revisar.
- Dentro de la banda de firmas se exige más hueco para contar una mancha como sello
  (una firma enlazada encierra ~31; un sello encima, ~484), así que ya se detectan los
  sellos que caen ahí sin confundirlos con las firmas.
- Aclaración de reglas: que un sello tape una firma **no** es motivo de revisión por sí
  mismo; solo cuando impide saber si la celda está firmada.

## v0.13.1 — 2026-09-17

Correcciones a la detección de sellos, tras revisar la salida dibujada sobre las hojas:

- **Las firmas ya no cuentan como sello.** La regla anterior ("si la mancha se sale de
  su celda de firma, es un sello") fallaba con la firma del *Páguese*, que tiene un lazo
  grande. Ahora manda dónde **nace** la mancha: dentro de la banda de firmas es firma;
  un sello que las tapa viene bajando desde arriba.
- **Las rayas de pluma tampoco.** Se exige que la mancha encierre hueco, porque un sello
  es un aro. Unas rayas azules que cruzaban la tabla de una orden ya no se cuentan.
- Siguen detectándose las 7 de 7 órdenes con sello.

## v0.13.0 — 2026-09-17

- **Detección de sellos.** Se separa la *tinta añadida* de la del formato impreso: lo
  impreso no tiene color y siempre llega a negro; un sello o trae color, o es un gris
  parejo que nunca llega a negro. Con eso se detectan sellos de cualquier color, en
  cualquier posición y de cabeza, sin buscar forma ni texto.
- Se descartan la reja de la tabla (corridas largas y rectas), el escudo del membrete
  (más chico que cualquier sello) y las firmas (manchas que caben dentro de su celda).
- **7 de 7 órdenes reales con sello detectado.** Se marca aparte cuando un sello
  traslapa una celda de firma, que según las reglas manda la orden a *Revisar*.
- El análisis corre solo en las páginas de orden, en una segunda vuelta: ~68 ms por
  orden en vez de pagarlo en todas las páginas.
- Pendiente para confiar en el dato: no hay ninguna orden **sin** sello en el PDF de
  ejemplo, así que no está medido cuántos falsos positivos daría.

## v0.12.0 — 2026-09-17

De 47 minutos a ~8 por cada 3,000 páginas, sin perder precisión (7/7 en número,
monto y ejercicio; 21/21 celdas de firma en el PDF real).

- **El JPEG lo decodifica el navegador, no pdf.js.** Cada página del escaneo es un
  JPEG entero dentro del PDF: se extraen los JPEG crudos y se decodifican con
  `createImageBitmap` (25–35 ms contra 229 ms). Si el PDF no es de ese tipo, se
  regresa solo a pdf.js.
- **El OCR se reparte en los núcleos disponibles** (hasta 6): 4.05× más rápido. El
  hilo principal solo decodifica y recorta; las filas de la tabla se llenan conforme
  cada trabajador termina.
- **Render a 200 ppp**, la resolución real del escaneo: subir a 300 no agrega detalle.
- **Banda de montos recortada a la mitad derecha** (317 ms contra 1 s por orden), con
  la banda ancha como respaldo cuando un sello tapa las cifras y no sale ningún monto
  mayor que cero.
- Umbral de firma bajado a 0.6 % y estado intermedio "dudosa" entre 0.2 % y 0.6 %: en
  una orden real la celda del *Páguese* midió 0.78 %, demasiado cerca del umbral viejo.
  Lo dudoso no se decide solo, se marca para revisar.

## Sin versión — 2026-09-17

- Medido si conviene un programa instalable en vez de la página: el navegador
  reparte el OCR en los seis núcleos casi perfecto (4.05× con 6 trabajadores) y
  solo pierde ~1.9× contra código nativo al decodificar la página. Un programa
  instalable saldría más o menos el doble de rápido que una web bien hecha, pero
  la web todavía no usa el paralelismo que ya tiene. Detalle en
  `docs/requisitos.md` § ¿Un programa instalable sería más rápido?

## v0.11.0 — 2026-09-17

- El medidor lee ahora **todos los campos de la orden**, cada uno en su zona: monto
  (tabla de importes y totales), fecha de expedición (de ahí el ejercicio) y el
  `Página X / Y` del pie.
- Validado contra el PDF real, cuyas siete órdenes el usuario confirmó completas y
  de una sola página: **7 de 7 en número, monto, ejercicio y 3 de 3 firmas**, y
  ningún falso positivo en las 16 páginas de soporte. Los montos se cotejaron
  contra el listado de la primera página del propio PDF.
- El `Página X / Y` solo se lee en 2 de 7: queda como dato extra. Para detectar
  órdenes de varias hojas basta con que dos páginas de orden seguidas traigan el
  mismo número.
- Con todos los campos son 0.95 s por página: 3,000 páginas en ~47 minutos.

## v0.10.0 — 2026-09-17

Fase 0 terminada: el medidor se rehízo con lo aprendido de un PDF real de la
plataforma y ahora lee lo que hay que leer.

- **Clasificación por encabezado:** una tira angosta de arriba basta para separar
  órdenes de soporte. 7 de 7 órdenes en 23 páginas, sin falsos positivos.
- **Lectura del número por zona, no por página completa:** recorte de la caja de
  arriba a la derecha, `PSM 4` y lista `0123456789-A`, con hasta cinco
  recortes/escalas porque la caja se mueve con el escaneo. 7 de 7, 6 al primer
  intento.
- **Se borra la tinta de color antes de leer:** la impresión es negra y la pluma y
  los sellos tienen color. Sin esto, una raya de pluma encima de los dígitos
  arruina la lectura.
- **Confirmación contra el documento base:** los PDF están llenos de números de 10
  dígitos que no son órdenes (cuentas, centros gestores, folios del banco). Si más
  de un candidato coincide, queda ambiguo: no se adivina.
- **Firmas por tinta de color** en las tres celdas del pie, que es como están en el
  formato real (no sobre una raya, como suponía la versión anterior).
- 0.55 s por página contra 2.9 s del OCR de página completa: **3,000 páginas en ~27
  minutos**. Con eso, la página web alcanza y no hace falta un programa instalable.
- El generador de PDF de prueba imita el formato real, con sus casos difíciles
  (raya de pluma sobre el número, sello encima de una firma, ADEFA, dos hojas).

## v0.9.2 — 2026-09-17

- **El número de orden ya no se filtra por prefijo.** Medido en dos documentos
  base reales: las órdenes son **siempre de 10 dígitos** (73/73 y 481/481), pero
  las series son varias (`19` la mayoría, también `51`, `71` y `50`). Antes el
  medidor solo reconocía `19…` y `71…` y se le habrían escapado series enteras.
- El medidor reporta también los números de 8 a 12 dígitos que no son de 10, que
  son los que delatan al OCR cuando pierde o inventa un dígito.
- El PDF de prueba trae una orden de la serie `51`.

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
