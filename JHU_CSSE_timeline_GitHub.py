# -*- coding: utf-8 -*-
"""
Created on Feb 11  2020

@author: Alexey Kotlik
"""

import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from flask import url_for
import json
import flask
  
    
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
url_lookup = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'

# url_USA = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/04-12-2020.csv'
url_USA = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/'

geolocator = Nominatim(user_agent="covid2019")
# pd_geodata = pd.read_csv(url_lookup)

def lead0(str_m):
    if len(str_m)==1:
        str_m = "0"+str_m
        
    return str_m
   
def get_coords(location):
    try:
        lat = pd_geodata.loc[pd_geodata.Combined_Key==location, 'Lat'].iloc[0]
        long = pd_geodata.loc[pd_geodata.Combined_Key==location, 'Long_'].iloc[0]
    except:
        try:
            print('didnt find in the loockup table: '+location)
            location = geolocator.geocode(location)
            lat = location.latitude
            long = location.longitude
        except:
            print(location)
            lat = 0
            long = 0
                
    return lat, long

def fill_nans(pd_daily):
    state_exceptions = ['Diamond Princess', 'Grand Princess','Recovered','nan'] #fall back to just country
    
    pd_nans = pd_daily.loc[(pd_daily.Lat.isna()) | (pd_daily.Long.isna()) ].copy()
    pd_nans['Admin2'] = ''
    
    for state in state_exceptions:
        if state == 'nan':
            pd_nans.loc[pd_nans.State.isna(),['Lat','Long']] = 0
            pd_nans.loc[pd_nans.State.isna(),'Full_name'] = pd_nans.loc[pd_nans.State.isna(),'Country']
            pd_nans.loc[pd_nans.State.isna(),'State'] = ''
        else:
            p_n = pd_nans.loc[pd_nans.State == state,'Full_name'] = pd_nans.loc[pd_nans.State == state,'Country']
            for i in range(p_n.shape[0]):
                lat, long = get_coords(p_n.iloc[i])
                pd_nans.loc[p_n.index[i],'Lat'] = lat
                pd_nans.loc[p_n.index[i],'Long'] = long
            pd_nans.loc[pd_nans.State == state,'State'] = ''

    pd_states = pd_nans.loc[pd_nans.Lat.isna()].copy()
    p_n = pd_states.Full_name = pd_states.State +', '+ pd_states.Country
    for i in range(p_n.shape[0]):
        lat, long = get_coords(p_n.iloc[i])
        pd_states.loc[p_n.index[i],'Lat'] = lat
        pd_states.loc[p_n.index[i],'Long'] = long

    pd_nans.loc[pd_states.index] = pd_states
    pd_daily.loc[pd_nans.index] = pd_nans

    return pd_daily


def full_country_name(row):
    # print(row.State)
    if str(row.State) == 'nan':
    # if row.State.isna():
        full_name = row.Country
    else:
        full_name = row.State+", "+row.Country
    return full_name

def remove_states(pd_data_to_clean):
    # we need to combine rows for States/Provinces tates into a single row Country by combining duplicates Country rows
    pd_data = pd_data_to_clean.copy()
    duplicates = pd_data.loc[pd_data.duplicated('Country')]
    u_countries = pd.unique(duplicates.Country)
    for nu in u_countries :
        d_country = pd_data.loc[pd_data['Country'] == nu]
        d_array = np.array(d_country.iloc[:,4:]).astype(int)
        d_totals = np.sum(d_array, axis = 0)
        all_nu = pd_data.loc[pd_data['Country'] == nu]
        pd_data.loc[all_nu.index[0], pd_data.columns[4:]] = d_totals 
        pd_data.drop(all_nu.index[1:], inplace = True)
    
    return pd_data

def move_state_to_country(row):
    if str(row.State) == 'nan':
        full_name = row.Country
    else:
        full_name = row.State
    return full_name
    
def get_data():

    global pd_geodata 
    pd_population = pd.read_csv('data/population_extended_2018.csv')

    pd_confirmed = pd.read_csv(url_confirmed)
    pd_confirmed_columns = pd_confirmed.columns.tolist()
    last_update_read = pd_confirmed_columns[-1]

    cur_date = last_update_read.split("/")
    last_update_read = "2020-"+lead0(cur_date[1])+"-"+lead0(cur_date[0])
    last_update = lead0(cur_date[0])+"-"+lead0(cur_date[1])+"-2020.csv"
    
    last_US_url = url_USA + last_update
    
    print('last_update_read ' + last_update_read)
    try:
        with open('data/last_update.txt') as f:
            saved_update = json.load(f)
            print('saved_update ' + saved_update )
    except:
        saved_update = '1970-01-01'

    if last_update_read > saved_update:
# need to read the rest from github and process as usual, otherwise just read what's been saved already
        print('loading data from GitHub')
        new_data = True
        pd_geodata = pd.read_csv(url_lookup)

        pd_rec = pd.read_csv(url_recovered)
        pd_deaths = pd.read_csv(url_deaths)

        pd_USA = pd.read_csv(last_US_url)
        us_cols = ['Province_State', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Incident_Rate','People_Tested', 'People_Hospitalized', 
                   'Mortality_Rate', 'Testing_Rate', 'Hospitalization_Rate']
        pd_USA = pd_USA[us_cols]
        pd_USA = pd_USA.fillna(0)

        if (min([pd_rec.shape[1],pd_deaths.shape[1],pd_confirmed.shape[1]]) != max([pd_rec.shape[1],pd_deaths.shape[1],pd_confirmed.shape[1]])):
            min_shape = min([pd_rec.shape[1],pd_deaths.shape[1],pd_confirmed.shape[1]])
            rec_cols = pd_rec.columns.tolist()[:min_shape]
            pd_rec = pd_rec[rec_cols]
            death_cols = pd_deaths.columns.tolist()[:min_shape]
            pd_deaths = pd_deaths[death_cols]
            rec_confirmed = pd_confirmed.columns.tolist()[:min_shape]
            pd_confirmed = pd_confirmed[rec_confirmed]
    
        pd_confirmed.rename(columns={'Province/State': 'State', 'Country/Region' :'Country'}, inplace = True)
        pd_deaths.rename(columns={'Province/State': 'State', 'Country/Region' :'Country'}, inplace = True)
        pd_rec.rename(columns={'Province/State': 'State', 'Country/Region' :'Country'}, inplace = True)
    

        colonial = ['France', 'Denmark', 'United Kingdom', 'Netherlands']
        for colony in colonial:
            pd_confirmed.loc[pd_confirmed.Country == colony,'Country'] = pd_confirmed.loc[pd_confirmed.Country == colony].apply(lambda row: move_state_to_country(row), axis = 1) 
    
    
        pd_confirmed_columns = pd_confirmed.columns.tolist()

        pd_confirmed.fillna(0, inplace = True)
        pd_deaths.fillna(0, inplace = True)
        pd_rec.fillna(0, inplace = True)

        pd_deaths = pd_deaths[pd_confirmed_columns]
        pd_rec = pd_rec[pd_confirmed_columns]

        pd_confirmed = remove_states(pd_confirmed)
        pd_deaths = remove_states(pd_deaths)
        pd_rec = remove_states(pd_rec)

        dates_list = [x.split(" ")[0] for x in pd_confirmed_columns[4:]]
        # cur_date = dates_list[-1].split("/")
        # last_update = lead0(cur_date[0])+"-"+lead0(cur_date[1])+"-2020.csv"

        url_daily = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"+last_update 
        pd_daily = pd.read_csv(url_daily)
        pd_daily = pd_daily.rename(columns = {"Long_":"Long", "Province_State":"State", "Country_Region":"Country","Combined_Key":"Full_name"})
        pd_daily = pd_daily.drop(pd_daily.loc[pd_daily.Confirmed==0].index, axis=0)
    
        pd_daily = fill_nans(pd_daily)
      
        new_pd_daily = pd_daily.drop(["FIPS","Admin2","Active","Last_Update"], axis=1)
        new_pd_daily = new_pd_daily.sort_values(by = ['Confirmed'], ascending = False)

        pd_confirmed.to_csv('data/pd_confirmed.csv', index=False)
        pd_deaths.to_csv('data/pd_deaths.csv', index=False)
        pd_rec.to_csv('data/pd_rec.csv', index=False)
        new_pd_daily.to_csv('data/new_pd_daily.csv', index=False)
        pd_USA.to_csv('data/pd_usa.csv', index=False)
        # pd_geodata.to_csv('data/geodata.csv', index=False)

        with open('data/last_update.txt','w') as f:
            l_u = dates_list[-1]
            cur_date = l_u.split("/")
            last_update_write = "2020-"+lead0(cur_date[1])+"-"+lead0(cur_date[0])
            json.dump(last_update_write, f)
        
    else:
        print('loading saved data')
# read what's been saved to server locally already'        
        pd_confirmed = pd.read_csv('data/pd_confirmed.csv')
        pd_rec = pd.read_csv('data/pd_rec.csv')
        pd_deaths = pd.read_csv('data/pd_deaths.csv')
        pd_USA = pd.read_csv('data/pd_usa.csv')
        # pd_geodata = pd.read_csv('data/geodata.csv')

        new_pd_daily = pd.read_csv('data/new_pd_daily.csv')
        pd_confirmed_columns = pd_confirmed.columns.tolist()
        dates_list = [x.split(" ")[0] for x in pd_confirmed_columns[4:]]
        new_data = False
        
    return pd_confirmed, pd_deaths, pd_rec, pd_confirmed_columns, dates_list, new_pd_daily, pd_population, new_data , pd_USA

