import wetterdienst as dwd
import os
from datetime import datetime
import pandas as pd
import geopandas
import contextily as ctx
import matplotlib.pyplot as plt
# import pyproj
# import fiona


os.getcwd()
start_date = "2015-05-01"
end_date = "2020-10-13"
station_search_radius = 5000 # Meters

# root = os.getcwd() # Set to root of bike-cologne.
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
# Load Polgon of the city cologne. 
cologne = geopandas.read_file(
              os.path.join(root, 'data', 'city_polygon', 'stadt.shp')
          )
# Create a 5km buffer to also retrieve nearby stations.
cologne_big = cologne.buffer(station_search_radius)

# Print all available variable names. 
print('Variables:', [x for x in dir(dwd.Parameter) if not x.startswith('__')])
parameters = ['PRECIPITATION', 'SUNSHINE_DURATION', 'TEMPERATURE_AIR', 'WIND']

station_ids = {}
station_gdf = geopandas.GeoDataFrame()
for param in parameters:
    # Currently problems with daily data in the wetterdienst api. 
    # Thus get hourly data.
    sites = dwd.DWDObservationSites(
        parameter=dwd.Parameter[param],
        time_resolution=dwd.TimeResolution.HOURLY,
        period_type=dwd.PeriodType.HISTORICAL,
        start_date=start_date,
        end_date=end_date
    )
    site_df = sites.all()
    
    # Latitude, longitude means WGS84 (geographical crs) with epsg:4326.
    sites_gdf = geopandas.GeoDataFrame(
        site_df, 
        geometry=geopandas.points_from_xy(site_df.LON, site_df.LAT), 
        crs=4326
    )
    # Project to the same crs als cologne.
    sites_gdf = sites_gdf.to_crs(cologne.crs)
    # Select by location. 
    stations_cgn = geopandas.clip(sites_gdf, cologne_big)
    # Only select stations with recent data.
    stations_cgn = stations_cgn[stations_cgn['TO_DATE']>start_date]
    
    station_ids.update({param: list(stations_cgn.STATION_ID)})
    station_gdf = station_gdf.append(stations_cgn)

station_gdf.drop_duplicates(['STATION_ID'], inplace=True)
# Reverse the dictionary.
parameter_ids = {}
for i in  list(set([x for l in list(station_ids.values()) for x in l])):
    parameter_ids.update({i: [x for x in station_ids.keys() if i in 
                              station_ids[x]]})
has_value = pd.DataFrame.from_dict({k: pd.Series(True, v) for k, v in 
                                    parameter_ids.items()}).T.fillna(False)
has_value['STATION_ID'] = has_value.index
station_gdf = pd.merge(station_gdf, has_value, on='STATION_ID')

ndays = datetime.strptime(end_date, '%Y-%M-%d')-datetime.strptime(start_date, 
                                                                  '%Y-%M-%d')
ncols = ndays.days*24

element_dict = {'TEMPERATURE_AIR': 'TEMPERATURE_AIR_200', 
                'PRECIPITATION': 'PRECIPITATION_HEIGHT',
                'WIND': 'WIND_VELOCITY',
                'SUNSHINE_DURATION': 'SUNSHINE_DURATION'}

observations = dwd.DWDObservationData(
    station_ids=list(set([x for l in list(station_ids.values()) for x in l])),
    parameter=dwd.Parameter['CLIMATE_SUMMARY'],
    time_resolution=dwd.TimeResolution.DAILY,
    start_date=start_date,
    end_date=end_date,
    tidy_data=True,
    humanize_column_names=True
)

for df in observations.collect_data():
    df_new = df[(df['ELEMENT'].isin(list(element_dict.values()))) & 
                (df['VALUE'].notnull())]
    df_new.drop(columns='PARAMETER', inplace=True)
    station_id = df_new['STATION_ID'].mode()[0]
    df_new.to_csv(os.path.join(root, 'data', 'weather', 
                               'dwd_staion_'+str(station_id)+'.csv'))


color_dict = {'PRECIPITATION': 'blue', 'TEMPERATURE_AIR': 'red', 
              'WIND': 'black', 'SUNSHINE_DURATION': 'yellow'}

# Plot weather stations and the available observations. 
ax = cologne_big.plot(color='red', alpha=0.1)
cologne.plot(ax=ax, color='red', alpha=0.25)
ctx.add_basemap(ax, crs=cologne.crs.to_string(), attribution_size=1)
markersize=30
for i in list(color_dict.items()):
    station_gdf[station_gdf[i[0]]].plot(ax=ax, marker='o', color=i[1], 
                                        markersize=markersize)
    markersize -= 9
for i in range(len(station_gdf)):
    ax.text(station_gdf.geometry.x.iloc[i], station_gdf.geometry.y.iloc[i], 
            station_gdf['STATION_ID'].iloc[i], fontsize=8)
ax.set_axis_off()
plt.savefig(os.path.join(root, 'weather_station.png'), dpi=600)

