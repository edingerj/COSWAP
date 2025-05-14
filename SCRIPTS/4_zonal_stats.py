import time, arcpy
from arcpy import env
from arcpy.sa import *

### Notes: the output of this can be imported as an asset in GEE to classify segments by lidar-derived canopy cover %
# Use Python 3.11 interpreter "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe"

start_time = time.perf_counter()

###########################################################################

# Set environment settings
env.workspace = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\WORKSPACE"
env.overwriteOutput = True

# Set input paths
zone_polygon = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\JEFFERSON_MID\Jefferson_Mid_segments_test.shp"
zone_field = "id"
value_raster = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\DATA\output_canopy_cover\merged_canopy_cover.tif"
zonal_table = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\JEFFERSON_MID\canopy_stats.dbf"
output_shapefile = r"C:\CFRI\Spatial_Heterogeneity\COSWAP\LiDAR\JEFFERSON_MID\JEFFERSON_MID_zonal_stats_test2.shp"

arcpy.CheckOutExtension("Spatial")

# Run Zonal Statistics as Table
ZonalStatisticsAsTable(zone_polygon, zone_field, value_raster, zonal_table, "DATA", "MEAN")
print("Zonal statistics completed.")

# Join the table to the original shapefile
arcpy.MakeFeatureLayer_management(zone_polygon, "zones_lyr")    # temporary layer
arcpy.AddJoin_management("zones_lyr", zone_field, zonal_table, zone_field)

# Export to new shapefile with joined data
arcpy.CopyFeatures_management("zones_lyr", output_shapefile)

print(f"Saved zonal statistics to: {output_shapefile}")


mean_field = "canopy_s_4"    # this is what the mean field was called
canopy_cover_field = "CanopyPct"
forest_type_field = "CoverType"
forest_code_field = "ForestCode"
arcpy.AddField_management(output_shapefile, canopy_cover_field, "DOUBLE")
arcpy.AddField_management(output_shapefile, forest_type_field, "TEXT")
arcpy.AddField_management(output_shapefile, forest_code_field, "SHORT")

# Calculate the new field (100 * mean)
expression = f"!{mean_field}! * 100"
arcpy.CalculateField_management(output_shapefile, canopy_cover_field, expression, "PYTHON3")

print(f"New field '{canopy_cover_field}' added and calculated.")

# Create an update cursor to populate the new field
with arcpy.da.UpdateCursor(output_shapefile, [canopy_cover_field, forest_type_field, forest_code_field]) as cursor:
    for row in cursor:
        canopy_pct_value = row[0]
        #
        if canopy_pct_value is None:
            row[1] = "No Data"
            row[2] = -1
        elif 0 <= canopy_pct_value < 5:
            row[1] = "Meadow"
            row[2] = 1
        elif 5 <= canopy_pct_value < 15:
            row[1] = "Savannah"
            row[2] = 2
        elif 15 <= canopy_pct_value < 30:
            row[1] = "Open Forest"
            row[2] = 3
        elif 30 <= canopy_pct_value < 60:
            row[1] = "Closed Forest"
            row[2] = 4
        elif canopy_pct_value >= 60:
            row[1] = "Dense Forest"
            row[2] = 5
        else:
            row[1] = "No Data"
            row[2] = -1
        # # Assign forest type based on the canopy cover (mean) value
        # if 0 <= canopy_pct_value < 5:
        #     row[1] = "Meadow"
        # elif 5 <= canopy_pct_value < 15:
        #     row[1] = "Savannah"
        # elif 15 <= canopy_pct_value < 30:
        #     row[1] = "Open Forest"
        # elif 30 <= canopy_pct_value < 60:
        #     row[1] = "Closed Forest"
        # elif canopy_pct_value >= 60:
        #     row[1] = "Dense Forest"
        # else:
        #     row[1] = "No Data"  # In case there's a null or negative value (if needed)

        # Update the row in the shapefile
        cursor.updateRow(row)

# print(f"Forest Type field '{forest_type_field}' added and populated.")
print(f"Fields '{forest_type_field}' and '{forest_code_field}' added and populated.")

##############################################################################

end_time = time.perf_counter()

execution_time = end_time - start_time
print(f"The script took {execution_time:.4f} seconds to run.")