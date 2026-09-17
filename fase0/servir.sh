#!/bin/bash
# Abre el medidor de la fase 0 en el navegador.
# Hace falta un servidor local (no basta abrir el archivo): pdf.js y Tesseract
# no cargan sus piezas desde file://.
cd "$(dirname "$0")/.."
PUERTO=${1:-8765}
echo "Medidor en  http://localhost:$PUERTO/fase0/medidor.html"
echo "(Ctrl+C para cerrar)"
(sleep 1; xdg-open "http://localhost:$PUERTO/fase0/medidor.html" 2>/dev/null \
  || firefox "http://localhost:$PUERTO/fase0/medidor.html" 2>/dev/null) &
python3 -m http.server "$PUERTO" --bind 127.0.0.1
