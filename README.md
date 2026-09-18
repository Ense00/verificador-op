# Verificador de Órdenes de Pago

Herramienta web para verificar Órdenes de Pago escaneadas (PDF) contra un Excel de órdenes solicitadas: número de orden, ejercicio, montos, firmas y sellos.

**Privacidad:** todo el procesamiento ocurre en el navegador de quien la usa. Los PDFs y el Excel nunca se suben a ningún servidor.

**Estado:** las dos etapas funcionan. *Preparar Layout* genera el archivo para la plataforma; *Verificar órdenes* lee los PDFs escaneados y arma la tabla de resultados. Sigue habiendo una demostración con datos ficticios para ver la interfaz sin archivos.

- Requisitos y reglas: [`docs/requisitos.md`](docs/requisitos.md)
- Historial de cambios: [`CHANGELOG.md`](CHANGELOG.md)
- Página: [`boceto/index.html`](boceto/index.html) (publicada en GitHub Pages). `boceto/fuente-artifact.html` es la misma página sin `<!doctype>/<head>/<body>`, para republicarla como artifact de Claude; editar esa y regenerar `index.html`.

> Reglas del repositorio (es público):
> - Nunca subir PDFs, Excels ni ZIPs reales (bloqueados en `.gitignore`).
> - Nunca poner números de orden, montos, nombres de personas ni de la institución reales en código, pruebas, documentación o mensajes de commit. Usar datos ficticios (p. ej. `1900000001`).
> - La plantilla de alineación sale de un escaneo real, así que no vive en el repo: el usuario la carga en la página.
