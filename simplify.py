import math
import geopandas as gpd
from shapely.geometry import Polygon
import alphashape


def simplify_geometry(geometry):
    return geometry.simplify(tolerance=1, preserve_topology=True)


def calculate_angle(a, b, c):
    ang = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
    return ang + 360 if ang < 0 else ang


# Function to filter out vertices that create sharp angles or 180-degree angles
def cleanup_vertices(geometry):
    if isinstance(geometry, Polygon):
        filtered_coords = []

        # TODO Interior Ring
        coords = list(geometry.exterior.coords)
        if len(coords) <= 4:
            return geometry

        for i in range(len(coords)):
            # Window
            p1 = coords[i - 1]
            p2 = coords[i]
            p3 = coords[(i + 1) % len(coords)]

            angle = calculate_angle(p1, p2, p3)

            if angle > 360 - angle:
                angle = 360 - angle

            if 165 > angle > 10:
                filtered_coords.append(p2)

        if len(filtered_coords) <= 4:
            return geometry

        # Create a new polygon with the filtered vertices
        return Polygon(filtered_coords)
    else:
        return geometry  # Return unchanged for other geometry types


def apply_alpha_hull(geometry):
    if isinstance(geometry, Polygon):
        coords = list(geometry.exterior.coords)
        alpha_shape = alphashape.alphashape(coords, 0)
        if alpha_shape.is_empty:
            return geometry
        else:
            return alpha_shape


if __name__ == '__main__':
    file_path = 'result.shp'

    # Read the GeoPackage file using GeoPandas
    data = gpd.read_file(file_path)
    data['geometry'] = data['geometry'].apply(simplify_geometry)

    # modified_geometries = [cleanup_vertices(geometry) for geometry in data.geometry]

    modified_geometries = []
    for index, row in data.iterrows():
        modified_geom = cleanup_vertices(row['geometry'])
        if not row['NAME']:
            modified_geom = apply_alpha_hull(row['geometry'])

        modified_geometries.append(modified_geom)

    # Create a new GeoDataFrame with the modified geometries
    modified_df = gpd.GeoDataFrame(data.drop(columns='geometry'), geometry=modified_geometries, crs=data.crs)

    modified_df.to_file("result_simplified.shp")
