# Reglas de Datos y Negocio — Barbarenas

## Módulo: Ocupación y Staff
- REGLA CRÍTICA: La carga de trabajo y el personal de limpieza se calculan por **Habitación / Llave ocupada**, NUNCA por cantidad de huéspedes individuales.
- El día de check-out representa el 100% de la carga de limpieza (limpieza profunda). El día de check-in no suma carga de limpieza para esa fecha específica.

## Módulo: Marketing (Mkt)
- El reporte de Maca (`Reporte Mensual Marketing - Registro Posts.tsv`) utiliza ventanas de atribución cerradas: D1, D3 y D7.
- La métrica clave de conversión en el embudo son los `Saves` (Guardados). Un post con altos saves alimenta las reservas que gestiona Lucas.
- Para datos anteriores a mayo, las visualizaciones son acumuladas. Desde mayo en adelante, evaluar el impacto inicial estrictamente con la columna D1 Views.
