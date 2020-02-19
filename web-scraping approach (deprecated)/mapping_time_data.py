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

def my_geocoder(row):
    print(row)
    try:
        point = geocode(row, provider='nominatim').geometry.iloc[0]
        return pd.Series({'Latitude': point.y, 'Longitude': point.x, 'geometry': point})
    except:
        return None


def color_producer(val):
    if val == 2:
        return 'red'
    elif val == 1 :
        return 'darkred'
    else:
        return 'lightgreen'

def radius_producer(number):
    if number == '':
        num = 0
    else:
        num = int(np.sqrt(int(number)))
    return num

#def radius_producer(state, country, number):
##    print(number)
#    try:
#        if country in unque_countries:
##            print(country)
#            num = Last_Report[(Last_Report.Country == country)][number].array[0]
#        else:
##            print(country,' ', state)
#            num = Last_Report[(Last_Report.State == state)][number].array[0]
#    except:
#        num = 0
#    num = int(np.sqrt(num))
#    print(num)
#    return int(num)
#
#max_report = max(full_geo.Report)
#Last_Report = full_geo[full_geo.Report == max_report]
#last_deaths = Last_Report.Deaths.sum(axis=0)
#last_recovered = Last_Report.Recovered.sum(axis=0)
#last_confirmed = Last_Report.Confirmed.sum(axis=0)
#
#unque_states =  full_geo.State.unique().tolist()
#unque_countries =  full_geo[full_geo.State == ''].Country.unique().tolist()
#un_states = pd.DataFrame(unque_states, columns = ['Name'])
#un_countries = pd.DataFrame(unque_countries, columns = ['Name'])
#
#un_states[['Latitude', 'Longitude', 'geometry']] = un_states.apply(lambda x: my_geocoder(x['Name']), axis=1)
#un_states.dropna(axis = 0, inplace = True)
#un_countries[['Latitude', 'Longitude', 'geometry']] = un_countries.apply(lambda x: my_geocoder(x['Name']), axis=1)
#uc_nan = un_countries[un_countries.geometry.isnull()]
#if uc_nan.shape[0] >0:
#    uc_nan[['Latitude', 'Longitude', 'geometry']] = uc_nan.apply(lambda x: my_geocoder(x['Name']), axis=1)
#    un_countries.loc[uc_nan.index] = uc_nan
#
#last_states = Last_Report.State.unique().tolist()
#if '' in last_states:     last_states.remove('')
#last_countries = Last_Report.Country.unique().tolist()
#
#
#start_point = [un_states.iloc[0].Latitude, un_states.iloc[0].Longitude]
#
#current_states = un_states[un_states.Name.isin(last_states)]
#current_countries = un_countries[un_countries.Name.isin(last_countries)]
#
#current_states['Confirmed'] = Last_Report[Last_Report.State.isin(current_states.Name)].Confirmed
#c_states = Last_Report[Last_Report.State.isin(current_states.Name)]
#c_states = c_states[['Country', 'State', 'Confirmed', 'Deaths', 'Recovered', 'Update_date', 'Update_time']]
#c_countries = Last_Report[Last_Report.Country.isin(current_countries.Name)]
#c_countries = c_countries[['Country', 'State', 'Confirmed', 'Deaths', 'Recovered', 'Update_date', 'Update_time']]
#c_countries.columns
