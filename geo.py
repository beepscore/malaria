#!/usr/bin/env python3

# In Anaconda navigator I needed to install geopandas and then update it to fix fiona / gdal error
# https://stackoverflow.com/questions/42749254/error-in-importing-geopandas#43762549
# https://github.com/GenericMappingTools/gmt-python/issues/104
import geopandas as gpd


def get_map_df():
    """
    use geopandas basemap

    alternatively could use
    http://ramiro.org/notebook/geopandas-choropleth/
    http://www.naturalearthdata.com/downloads/10m-cultural-vectors/
    :return: geopandas dataframe with country name, areas, geometry

    """

    # http://geopandas.org/mapping.html
    df_map = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    column_names_lower = [column_name.lower() for column_name in df_map.columns]
    df_map.columns = column_names_lower

    df_map.rename({'name': 'country'}, axis='columns', inplace=True)

    return df_map
