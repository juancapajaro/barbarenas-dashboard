#!/bin/bash

# Salir inmediatamente si ocurre un error
set -e

echo "=== 1. Procesando los datos más recientes de los CSVs ==="
python3 process_data.py

echo "=== 2. Copiando el dashboard a index.html para GitHub Pages ==="
if [ -f "dashboards/integrated_dashboard.html" ]; then
  cp dashboards/integrated_dashboard.html dashboards/index.html
  echo "✓ Copiado dashboards/integrated_dashboard.html a dashboards/index.html"
else
  echo "✗ Error: No se encontró dashboards/integrated_dashboard.html"
  exit 1
fi

echo "=== 3. Guardando y subiendo los cambios a GitHub ==="
# Añadir los cambios a Git
git add dashboards/index.html dashboards/marketing_data.js dashboards/marketing_data.json data-sources/

# Verificar si hay cambios antes de hacer commit
if git diff --cached --quiet; then
  echo "✓ No hay cambios nuevos en los datos ni en el dashboard."
else
  git commit -m "Actualización automática de datos y dashboard"
  echo "✓ Cambios guardados en Git."
fi

# Hacer push a la rama principal
echo "Pushing a GitHub..."
git push origin main

echo "=== ✓ ¡Proceso completado con éxito! ==="
echo "Los datos han sido procesados y subidos a GitHub."
echo "En unos instantes, GitHub Pages compilará el sitio y estará visible de forma pública."
