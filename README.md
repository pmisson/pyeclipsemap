# Mapa de Zonas de Eclipse en España y Regiones Cercanas (2026-2028)

Este repositorio contiene scripts en Python para generar mapas con las zonas de los eclipses solares visibles en España y regiones cercanas en los años 2026, 2027 y 2028. Los datos de los eclipses han sido obtenidos de [Xavier Jubier](http://xjubier.free.fr/en/site_pages/SolarEclipsesGoogleEarth.html), y los mapas se generan con un fondo oscuro para mejorar la visualización en entornos nocturnos o de alto contraste.

## Características
- Carga de archivos KMZ con la información de los eclipses solares.
- Representación de las zonas de totalidad y anularidad en colores contrastantes.
- Visualización de las líneas centrales de los eclipses de 2026, 2027 y 2028.
- Uso de datos topográficos de ETOPO1 para incluir el relieve del terreno.
- Exportación del mapa en formato **SVG** con un diseño optimizado para fondos oscuros.

## Archivos
El repositorio incluye los siguientes scripts:
- `eclipse.py`: Genera el mapa de los eclipses con un fondo claro.
- `eclipse_dark.py`: Versión optimizada para un fondo oscuro.

## Requisitos
Este script requiere Python 3.x y las siguientes bibliotecas:
- `matplotlib`
- `cartopy`
- `geopy`
- `geopandas`
- `xarray`
- `shapely`
- `xml.etree.ElementTree`
- `zipfile`

Para instalar las dependencias, puedes ejecutar:
```bash
pip install matplotlib cartopy geopy geopandas xarray shapely
```

## Uso
1. Descarga los archivos KMZ de los eclipses desde [Xavier Jubier](http://xjubier.free.fr/en/site_pages/SolarEclipsesGoogleEarth.html) y colócalos en la carpeta del script.
2. Ejecuta el script en un entorno Python:
   ```bash
   python eclipse_dark.py
   ```
   o para la versión con fondo claro:
   ```bash
   python eclipse.py
   ```
3. Se generará un mapa con las zonas de eclipse y las líneas centrales, que se mostrará en pantalla y se guardará como **mapa_eclipses_dark.svg** o **mapa_eclipses.svg** según la versión utilizada.

## Licencia
Este proyecto está bajo la licencia [MIT](LICENSE).

## Autor
Alejandro Sánchez de Miguel, ChatGPT_4o y AutoGPT

## Instituciones
Instituto de Astrofísica de Andalucía-CSIC y Universidad Complutense de Madrid

