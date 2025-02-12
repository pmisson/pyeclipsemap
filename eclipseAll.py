import os
import geopy
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from matplotlib.colors import Normalize
from shapely.geometry import Polygon, LineString
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import geopandas as gpd

# ---------------------------
# Funciones de extracción KMZ
# ---------------------------
def extract_polygons_from_kmz(kmz_path):
    with ZipFile(kmz_path, 'r') as kmz:
        kml_filename = [name for name in kmz.namelist() if name.endswith('.kml')][0]
        kmz.extract(kml_filename, '.')
        kml_path = f"./{kml_filename}"

    # Parsear el archivo KML
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    polygons = []
    for placemark in root.findall('.//kml:Placemark', ns):
        polygon = placemark.find('.//kml:Polygon', ns)
        if polygon is not None:
            coords_text = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns).text.strip()
            coords = [tuple(map(float, c.split(',')[:2])) for c in coords_text.split()]
            if len(coords) > 3:
                polygons.append(Polygon(coords))
    
    return polygons

def extract_central_line(kmz_path):
    with ZipFile(kmz_path, 'r') as kmz:
        kml_filename = [name for name in kmz.namelist() if name.endswith('.kml')][0]
        kmz.extract(kml_filename, '.')
        kml_path = f"./{kml_filename}"
    
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    for placemark in root.findall('.//kml:Placemark', ns):
        name_element = placemark.find('kml:name', ns)
        if name_element is not None and 'central' in name_element.text.lower():
            line = placemark.find('.//kml:LineString', ns)
            if line is not None:
                coords_text = line.find('.//kml:coordinates', ns).text.strip()
                coords = [tuple(map(float, c.split(',')[:2])) for c in coords_text.split()]
                return LineString(coords)
    return None

# ------------------------------------------------------
# Funciones para tratar el cruce del meridiano (dateline)
# ------------------------------------------------------
def split_line_on_dateline(line, threshold=180):
    """
    Divide una LineString en segmentos cuando hay un salto brusco en la longitud.
    """
    coords = list(line.coords)
    if not coords:
        return []

    segments = []
    current_segment = [coords[0]]

    for i in range(1, len(coords)):
        prev_lon, prev_lat = coords[i - 1]
        curr_lon, curr_lat = coords[i]
        # Si la diferencia es mayor que el umbral, se asume que hay cruce del dateline.
        if abs(curr_lon - prev_lon) > threshold:
            if len(current_segment) > 1:
                segments.append(LineString(current_segment))
            current_segment = [coords[i]]
        else:
            current_segment.append(coords[i])
    if len(current_segment) > 1:
        segments.append(LineString(current_segment))
    return segments

def plot_line_with_dateline(ax, line, **kwargs):
    """
    Dibuja una línea en el eje 'ax', dividiéndola en segmentos si cruza el dateline.
    """
    segments = split_line_on_dateline(line)
    for segment in segments:
        x, y = zip(*segment.coords)
        ax.plot(x, y, **kwargs)

# -----------------------------------------------------------
# Función para procesar y dibujar todos los KMZ de una carpeta
# -----------------------------------------------------------
def plot_kmz_files(ax, folder, polygon_style=None, line_style=None):
    """
    Recorre todos los archivos KMZ en 'folder', extrae sus polígonos y línea central,
    y los dibuja en el eje 'ax'.
    
    Parámetros:
      - ax: eje de matplotlib (por ejemplo, creado con Cartopy) donde se dibuja.
      - folder: ruta a la carpeta que contiene los archivos KMZ.
      - polygon_style: diccionario con parámetros de estilo para los polígonos (opcional).
      - line_style: diccionario con parámetros de estilo para las líneas (opcional).
    """
    if polygon_style is None:
        polygon_style = {"alpha": 0.5, "edgecolor": "black"}
    if line_style is None:
        line_style = {"linewidth":2, "linestyle":"dashed"}

    # Listar archivos KMZ en la carpeta
    kmz_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.kmz')]
    
    # Usamos un ciclo de colores para diferenciarlos
    colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', ['red', 'blue', 'green', 'orange', 'purple'])
    
    for idx, kmz_file in enumerate(kmz_files):
        color = colors[idx % len(colors)]
        label_base = os.path.splitext(os.path.basename(kmz_file))[0]
        
        # Extraer polígonos y línea central
        polygons = extract_polygons_from_kmz(kmz_file)
        central_line = extract_central_line(kmz_file)
        
        # Dibujar cada polígono
        for polygon in polygons:
            x, y = zip(*polygon.exterior.coords)
            ax.fill(x, y, color=color, **polygon_style, label=f"Zona {label_base}")
        
        # Dibujar la línea central, si existe
        if central_line:
            plot_line_with_dateline(ax, central_line, color=color, **line_style, label=f"Línea central {label_base}")

# -----------------------------------------------------------
# Ejemplo de uso: Crear mapa base, cargar ETOPO1 y dibujar KMZs
# -----------------------------------------------------------
# Crear figura y eje con Cartopy
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([-180, 180, -89, 89], crs=ccrs.PlateCarree())

# Agregar características geográficas
ax.add_feature(cfeature.LAND, color="lightgrey")
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, alpha=0.5)
ax.add_feature(cfeature.RIVERS)

# Cargar el modelo de elevación ETOPO1 (ajusta la ruta al archivo si es necesario)
etopo1_file = 'ETOPO1_Ice_g_gmt4.grd'
etopo1_data = xr.open_dataset(etopo1_file)
img_extent = (etopo1_data.x.min().values, etopo1_data.x.max().values, etopo1_data.y.min().values, etopo1_data.y.max().values)
norm = Normalize(vmin=-600, vmax=2500)
ax.imshow(etopo1_data.z, origin='lower', extent=img_extent, transform=ccrs.PlateCarree(), cmap='terrain', norm=norm, alpha=0.5, zorder=0)

# Usar la función para procesar y dibujar todos los KMZ de la carpeta local
kmz_folder = "."  # Carpeta actual
plot_kmz_files(ax, kmz_folder)

# Añadir título y leyenda
ax.set_title("Eclipses: Zonas y Líneas Centrales de archivos KMZ (Carpeta local)")
plt.legend(loc="upper right", fontsize='small')

# Guardar el mapa en formato SVG (opcional)
plt.savefig("mapa_eclipses.svg", format="svg")

# Mostrar el mapa
plt.show()


