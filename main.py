import math

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


def derive_building_block(value):
    bbl = "" + value
    return int(bbl[:6])


if __name__ == '__main__':

    file_path = 'buildings_clipped_3857.gpkg'

    # Read the GeoPackage file using GeoPandas
    data = gpd.read_file(file_path)

    data['block'] = data['BBL'].apply(derive_building_block)

    unique_blocks = data['block'].unique()

    # Initialize an empty GeoDataFrame to store dissolved polygons
    result_df = gpd.GeoDataFrame(columns=['geometry'], crs=data.crs)

    agg_function = {'NUM_FLOORS': 'mean',
                    'HEIGHTROOF': 'mean',
                    'GROUNDELEV': 'mean',
                    'NAME': lambda x: x.dropna().iloc[0] if x.notnull().any() else None}

    for block in unique_blocks:
        filtered_data = data[data['block'] == block]

        # Dissolve the filtered data based on the specified column ('BBL') to create dissolved polygons
        dissolved_polygons = filtered_data.dissolve(by='block', aggfunc=agg_function)
        dissolved_polygons['NUM_FLOORS'] = dissolved_polygons['NUM_FLOORS'].astype(int)
        dissolved_polygons['DISTRICT'] = str(block)[0]

        # Append dissolved polygons to the result GeoDataFrame
        result_df = pd.concat([result_df, dissolved_polygons], ignore_index=True)

    # Multipolygons to Singlepolygons
    exploded_rows = result_df.explode()

    # 'result_df' now contains separate GeoDataFrames for each dissolved polygon based on derived 'BBL'
    print(exploded_rows)

    # Only Manhattan
    gdf_filtered = exploded_rows[exploded_rows['DISTRICT'] == '1']

    gdf_filtered.to_file("result.shp")

