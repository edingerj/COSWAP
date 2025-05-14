import pdal, json, os, time
from osgeo import gdal

### Notes: need to add filter to remove points above 60m, and change radius to 1.0
# Use Python 3.10 (2) interpreter: "C:/Users/purpl/anaconda3/envs/lidar/python.exe"
# PDAL = Point Data Abstraction Library

start_time = time.perf_counter()

# Input and output folders
input_folder = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\input_laz"
output_folder = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_chm"

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Loop through all .laz files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".laz"):
        input_path = os.path.join(input_folder, filename)
        print(input_path)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}_chm.tif")

        # Define the pipeline
        pipeline_json = {
            "pipeline": [
                {"type": "readers.las", "filename": input_path},
                {"type": "filters.smrf", "scalar": 1.25, "slope": 0.15, "threshold": 0.5, "window": 16.0},
                {"type": "filters.hag_delaunay"},
                {"type": "filters.range", "limits": "HeightAboveGround[0:]"},
                {"type": "filters.ferry", "dimensions": "HeightAboveGround => Z"},
                {
                    "type": "writers.gdal",
                    "filename": output_path,
                    "resolution": 1.0,
                    "radius": 0.5,
                    "output_type": "max",
                    "data_type": "float"
                }
            ]
        }

        # Run the pipeline
        pipeline = pdal.Pipeline(json.dumps(pipeline_json))
        try:
            pipeline.execute()
            print(f"✅ CHM written: {output_path}")
        except RuntimeError as e:
            print(f"❌ Failed on {input_path}: {e}")


########### merge CHMs into one raster

input_CHMs = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_chm"
output_CHM = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_chm\merged_chm.tif"

# Get a list of all .tif files in the folder
tif_files = [os.path.join(input_CHMs, f) for f in os.listdir(input_CHMs) if f.endswith(".tif")]

# Create a virtual raster (VRT) from the input files
vrt_path = "/vsimem/temp.vrt"  # In-memory virtual file
vrt = gdal.BuildVRT(vrt_path, tif_files)

# Translate (convert) the VRT into a single output GeoTIFF
gdal.Translate(output_CHM, vrt)

# Clean up
vrt = None
print(f"Merged CHM saved to: {output_CHM}")


end_time = time.perf_counter()

execution_time = end_time - start_time
print(f"The script took {execution_time:.4f} seconds to run.")
