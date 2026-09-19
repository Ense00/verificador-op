#!/bin/bash
# Comprobaciones antes de publicar. Se me olvidó dos veces el sello de versión de la
# página y una vez regenerar index.html; esto lo caza en un segundo.
cd "$(dirname "$0")/.."
fallas=0
aviso(){ echo "  ✗ $1"; fallas=$((fallas+1)); }

ver_changelog=$(grep -m1 -oE "^## (v[0-9]+\.[0-9]+\.[0-9]+)" CHANGELOG.md | cut -d' ' -f2)
ver_pagina=$(grep -m1 -oE '<span class="stamp">v[0-9]+\.[0-9]+\.[0-9]+</span>' boceto/fuente-artifact.html | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+')

echo "CHANGELOG: $ver_changelog · página: $ver_pagina"
[ -n "$ver_changelog" ] || aviso "no se encontró la versión en CHANGELOG.md"
[ -n "$ver_pagina" ] || aviso "no se encontró el sello de versión en la página"
[ "$ver_changelog" = "$ver_pagina" ] || aviso "el sello de la página no coincide con el CHANGELOG"

# index.html se genera envolviendo la fuente: si no coincide, falta regenerarlo
tmp=$(mktemp)
{ printf '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
  cat boceto/fuente-artifact.html
  printf '\n</body>\n</html>\n'; } > "$tmp"
cmp -s "$tmp" boceto/index.html || aviso "boceto/index.html no está regenerado a partir de fuente-artifact.html"
rm -f "$tmp"

# el repo es público: nada de datos reales
if git grep -nIE "(BOMBEROS|Bomberos|CRUZ ROJA|Cruz Roja|Caborca)" -- . ':!tests/revisar.sh' > /dev/null 2>&1; then
  aviso "hay nombres de entidad reales en el repo (usar Caso A/B/C)"
fi

if [ "$fallas" -eq 0 ]; then echo "todo en orden"; else echo "$fallas problema(s)"; fi
exit $((fallas > 0))
