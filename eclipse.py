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

# Función para extraer polígonos de los eclipses desde KMZ
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

# Función para extraer la línea central del eclipse
def extract_central_line(kmz_path):
    with ZipFile(kmz_path, 'r') as kmz:
        kml_filename = [name for name in kmz.namelist() if name.endswith('.kml')][0]
        kmz.extract(kml_filename, '.')
        kml_path = f"./{kml_filename}"
    
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    for placemark in root.findall('.//kml:Placemark', ns):
        if 'central' in placemark.find('kml:name', ns).text.lower():  # Buscar específicamente la línea central
            line = placemark.find('.//kml:LineString', ns)
            if line is not None:
                coords_text = line.find('.//kml:coordinates', ns).text.strip()
                coords = [tuple(map(float, c.split(',')[:2])) for c in coords_text.split()]
                return LineString(coords)
    return None

# Cargar los datos de los eclipses
polygons_2026 = extract_polygons_from_kmz("TSE_2026_08_12.kmz")
polygons_2027 = extract_polygons_from_kmz("TSE_2027_08_02.kmz")
polygons_2028 = extract_polygons_from_kmz("ASE_2028_01_26.kmz")

central_line_2026 = extract_central_line("TSE_2026_08_12.kmz")
central_line_2027 = extract_central_line("TSE_2027_08_02.kmz")
central_line_2028 = extract_central_line("ASE_2028_01_26.kmz")

# Cargar mapa base
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([-15, 10, 30, 50], crs=ccrs.PlateCarree())

# Agregar datos geográficos
ax.add_feature(cfeature.LAND, color="lightgrey")
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, alpha=0.5)
ax.add_feature(cfeature.RIVERS)

# Cargar el modelo de elevación ETOPO1
etopo1_file = 'ETOPO1_Ice_g_gmt4.grd'
etopo1_data = xr.open_dataset(etopo1_file)
img_extent = (etopo1_data.x.min().values, etopo1_data.x.max().values, etopo1_data.y.min().values, etopo1_data.y.max().values)
norm = Normalize(vmin=-600, vmax=2500)
ax.imshow(etopo1_data.z, origin='lower', extent=img_extent, transform=ccrs.PlateCarree(), cmap='terrain', norm=norm, alpha=0.5, zorder=0)

# Dibujar zonas de eclipses
for coords in polygons_2026:
    x, y = zip(*coords.exterior.coords)
    ax.fill(x, y, color='red', alpha=0.5, edgecolor="black", label="Total 2026")
for coords in polygons_2027:
    x, y = zip(*coords.exterior.coords)
    ax.fill(x, y, color='blue', alpha=0.5, edgecolor="black", label="Total 2027")
for coords in polygons_2028:
    x, y = zip(*coords.exterior.coords)
    ax.fill(x, y, color='green', alpha=0.5, edgecolor="black", label="Anular 2028")

# Dibujar las líneas centrales de los eclipses
if central_line_2026:
    x, y = zip(*central_line_2026.coords)
    ax.plot(x, y, color='darkblue', linewidth=2, linestyle="dashed", label="Línea central 2026")
if central_line_2027:
    x, y = zip(*central_line_2027.coords)
    ax.plot(x, y, color='purple', linewidth=2, linestyle="dashed", label="Línea central 2027")
if central_line_2028:
    x, y = zip(*central_line_2028.coords)
    ax.plot(x, y, color='orange', linewidth=2, linestyle="dashed", label="Línea central 2028")

# Añadir título y leyenda
ax.set_title("Eclipses solares en España y regiones cercanas (2026-2028)")
plt.legend(loc="upper right")

# Guardar el mapa en formato SVG
plt.savefig("mapa_eclipses.svg", format="svg")

# Mostrar el mapa
plt.show()

