from rasterstats import zonal_stats
import geopandas as gpd
import time, rasterio, fiona
from rasterio.crs import CRS
from pyproj import CRS

### Notes:
# Use Python 3.10 (2) interpreter: "C:/Users/purpl/anaconda3/envs/lidar/python.exe"

start_time = time.perf_counter()

###########################################################################

# Check if raster CHM and polygons are in the same projection

canopy_cover = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_canopy_cover\merged_canopy_cover.tif"
polygons = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\JEFFERSON_MID\test_polygons.shp"
polygons_data = gpd.read_file(polygons)
print("CRS of the vector data:", polygons_data.crs)

shapefile = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\JEFFERSON_MID\Jefferson_Mid_segments_test1.shp"
gdf = gpd.read_file(shapefile)
print(gdf.head())

with rasterio.open(canopy_cover) as src:
    data = src.read()
    profile = src.profile.copy()
    raster_crs = profile.get("crs")
    print("CRS of canopy cover raster: ", raster_crs)

with fiona.open(polygons) as vector:
    vector_crs = vector.crs
    print("Vector CRS:", vector_crs)

# Manually setting the CRS for the raster if you know it
raster_crs = CRS.from_epsg(2877)
print("Raster CRS manually set to:", raster_crs)

# Manually setting the CRS for the vector if you know it
vector_crs = CRS.from_epsg(2877)
print("Vector CRS manually set to:", vector_crs)


# Reproject vector data to match raster's CRS

# Check if CRS can be converted to EPSG codes
try:
    # raster_epsg = CRS.from_string(raster_crs).to_epsg()
    raster_epsg = raster_crs
    print(f"Raster EPSG code: {raster_epsg}")
except:
    print("Could not extract EPSG from raster CRS.")

try:
    # vector_epsg = CRS.from_string(polygons_data.crs).to_epsg()
    vector_epsg = vector_crs
    print(f"Vector EPSG code: {vector_epsg}")
except:
    print("Could not extract EPSG from vector CRS.")

# If the CRS are different, reproject vector to raster's CRS
if raster_epsg != vector_epsg:
    print("Reprojecting vector data...")
    polygons_data_reprojected = polygons_data.to_crs(raster_crs)
    print("Reprojected vector data CRS:", polygons_data_reprojected.crs)
else:
    print("Vector and raster have the same CRS.")

##############################################################################

end_time = time.perf_counter()

execution_time = end_time - start_time
print(f"The script took {execution_time:.4f} seconds to run.")
