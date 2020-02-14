# -*- coding: utf-8 -*-
"""
Created on Feb 11  2020

@author: Alexey Kotlik
"""

import pandas as pd

       
url_recovered = 'https://github.com/CSSEGISandData/COVID-19/raw/master/time_series/time_series_2019-ncov-Recovered.csv'
url_deaths = 'https://github.com/CSSEGISandData/COVID-19/raw/master/time_series/time_series_2019-ncov-Deaths.csv'
url_confirmed = 'https://github.com/CSSEGISandData/COVID-19/raw/master/time_series/time_series_2019-ncov-Confirmed.csv'

def get_data():
    pd_rec = pd.read_csv(url_recovered)
    pd_rec.fillna(0, inplace = True)
    pd_deaths = pd.read_csv(url_deaths)
    pd_deaths.fillna(0, inplace = True)
    pd_confirmed = pd.read_csv(url_confirmed)
    pd_confirmed.fillna(0, inplace = True)
    
    pd_confirmed.rename(columns={'Province/State': 'State', 'Country/Region' :'Country'}, inplace = True)
    pd_deaths.rename(columns={'Province/State': 'State', 'Country/Region' :'Country'}, inplace = True)
    pd_rec.rename(columns={'Province/State': 'State', 'Country/Region' :'Country'}, inplace = True)

    pd_confirmed_columns = pd_confirmed.columns.tolist()
    
    dates_list = [x.split(" ")[0] for x in pd_confirmed_columns[4:]]

    return pd_confirmed, pd_deaths, pd_rec, pd_confirmed_columns, dates_list