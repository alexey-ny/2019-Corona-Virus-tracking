# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 10:04:50 2020

@author: Alexey Kotlik
"""

import pandas as pd
import numpy as np

import folium
from folium import Choropleth, Circle, Marker, CircleMarker
from folium.plugins import HeatMap, MarkerCluster

from geopandas.tools import geocode
import geopandas as gpd

full_geo = pd.read_csv('reports.csv')
full_geo.State = full_geo.State.fillna('')
#full_geo.info()

def my_geocoder(row):
    print(row)
    try:
        point = geocode(row, provider='nominatim').geometry.iloc[0]
        return pd.Series({'Latitude': point.y, 'Longitude': point.x, 'geometry': point})
    except:
        return None


def color_producer(val):
    if val == 1:
        return 'forestgreen'
    else:
        return 'darkred'

def radius_producer(state, country, number):
    print(number)
    try:
        if country in unque_countries:
#            print(country)
            num = Last_Report[(Last_Report.Country == country)][number].array[0]
        else:
#            print(country,' ', state)
            num = Last_Report[(Last_Report.State == state)][number].array[0]
    except:
        num = 0
    num = int(np.sqrt(num))
    print(num)
    return int(num)

max_report = max(full_geo.Report)
Last_Report = full_geo[full_geo.Report == max_report]
last_deaths = Last_Report.Deaths.sum(axis=0)
last_recovered = Last_Report.Recovered.sum(axis=0)
last_confirmed = Last_Report.Confirmed.sum(axis=0)

unque_states =  full_geo.State.unique().tolist()
unque_countries =  full_geo[full_geo.State == ''].Country.unique().tolist()
un_states = pd.DataFrame(unque_states, columns = ['Name'])
un_countries = pd.DataFrame(unque_countries, columns = ['Name'])

un_states[['Latitude', 'Longitude', 'geometry']] = un_states.apply(lambda x: my_geocoder(x['Name']), axis=1)
un_states.dropna(axis = 0, inplace = True)
un_countries[['Latitude', 'Longitude', 'geometry']] = un_countries.apply(lambda x: my_geocoder(x['Name']), axis=1)

start_point = [un_states.iloc[0].Latitude, un_states.iloc[0].Longitude]

