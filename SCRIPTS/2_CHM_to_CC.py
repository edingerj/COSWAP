import time, arcpy
from arcpy import env
from arcpy.sa import *

### Notes: need to adjust canopy height threshold (3-40m), maybe set minimum of 4m
# Use Python 3.11 interpreter "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe"

start_time = time.perf_counter()

###########################################################################

# Set environment settings
env.workspace = "C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_chm"
env.overwriteOutput = True

# Set local variables
inRaster = "merged_chm.tif"  # Input CHM raster file
outputRaster = "C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_canopy_cover\merged_canopy_cover.tif"  # Output file path

# Define reclassification ranges:
# Values between 3 and 40 meters are reclassified to 1 (canopy)
# Values between 0 and 3 meters are reclassified to 0 (non-canopy)
# Other values (outside the range) are reclassified to -9999 (NoData)
remap = RemapRange([[0, 3, 0], [3, 40, 1]])

# Execute Reclassify
outReclassify = Reclassify(inRaster, "Value", remap, "NODATA")

###########################################################################

# Save the output raster
outReclassify.save(outputRaster)

print(f"Reclassification completed. Output saved to: {outputRaster}")


##############################################################################

end_time = time.perf_counter()

execution_time = end_time - start_time
print(f"The script took {execution_time:.4f} seconds to run.")


