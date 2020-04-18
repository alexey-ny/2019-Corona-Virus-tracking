# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:41:41 2020

@author: Alexey Kotlik
"""
import folium
from folium import CircleMarker
from folium.plugins import MarkerCluster
import branca
import numpy as np
import json
import logging
from logging import FileHandler, WARNING
import time

from JHU_CSSE_timeline_GitHub import *
from twitter_update import *

from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

file_handler = FileHandler('flask_error.txt')
file_handler.setLevel(WARNING)
app.logger.addHandler(file_handler)

#helper functions
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
        num = max(1, int(np.sqrt(int(number+64))/5))
        # num = max(1, int(np.sqrt(int(number))/10))
    s_rad = num
    if s_rad > 0 :
        if s_rad >30:
            s_rad = 30
            if s_rad >70:
                s_rad = 70
    return s_rad

def country_stat(cd):
    country_name = cd.Country
    stat = [f'{cd[-1]:,}',country_name]
    return stat

def get_country_pop(countries_pops, country_name):
    try:
        n_pop = countries_pops.loc[countries_pops['Country Name'] == country_name,'2018']
        n = n_pop[n_pop.index[0]]
    except:
        try:
            n_pop = countries_pops.loc[countries_pops['Alt'] == country_name,'2018']
            n = n_pop[n_pop.index[0]]
        except: n = 0.00001
    return n

# list of all countries stats from Worldbank, and a row from Confirmed_data
def country_stat_ext(countries_pops, confirmed, deaths):
    # country_name = 'Germany'
    country_name = confirmed.Country

    try:
        row_pop = countries_pops.loc[countries_pops['Country Name'] == country_name]
        row_pop = row_pop.iloc[0]
    except:
        try:
            row_pop = countries_pops.loc[countries_pops['Alt'] == country_name]
            row_pop = row_pop.iloc[0]
        except:
            row_pop = pd.Series()

    row_pop = row_pop.fillna(0)

    try:
        death_row = deaths.loc[deaths.Country == country_name]
        death_row = death_row.iloc[0]
        dr = death_row[-1]
    except:
        dr = 0

    if row_pop.size>0:
        stat = [country_name, f'{confirmed[-1]:,}', f'{dr:,}', f'{int(row_pop["2018"]):,}', f'{row_pop["Hospital beds"]:3.1f}', f'{row_pop["Physicians"]:3.1f}', 
                f'{row_pop["Nurses"]:3.1f}', f'{row_pop["Above 65"]:3.1f}'+'%', f'{row_pop["Female above 80"]:3.1f}'+'%', f'{row_pop["Male above 80"]:3.1f}'+'%', 
                f'{row_pop["Smoking"]:3.1f}'+'%', f'{row_pop["Diabetes"]:3.1f}'+'%',f'{dr/confirmed[-1] *100 :2.2f}'+'%']
    else:
        stat = [country_name, f'{confirmed[-1]:,}', f'{dr:,}']
    return stat

# list of all states stats
def US_state_ext(state):
    # country_name = 'Germany'
    state_name = state.Province_State

    stat = [state_name, f'{state.Confirmed:,}', f'{state.Deaths:,}',f'{int(state.Recovered):,}',  f'{state.Incident_Rate:4.2f}', f'{int(state.People_Tested):,}',  
                f'{int(state.People_Hospitalized):,}', f'{state.Mortality_Rate:4.2f}', f'{state.Testing_Rate:4.2f}', f'{state.Hospitalization_Rate:4.2f}']
    return stat

def tweet_to_list(tweet):
    t_list = [tweet[0],tweet[1],tweet[2]]
    
    return t_list

@app.route('/_load_twitter')
def load_twitter():
    print('load new tweets')
    tic = time.perf_counter()


    twit_df = new_tweets().sort_values('timestamp', ascending = False)
    
    twit_to_list = twit_df.loc[:999,['screen_name', 'parsed_text', 'timestamp']]
    # twit_to_list = twit_df[['screen_name', 'parsed_text', 'timestamp']]
    # twit_to_list = twit_df[['screen_name', 'text', 'timestamp']]
    # twit_to_list = twit_to_list.sort_values('timestamp', ascending = False)
    # twit_to_list.sort_values('timestamp', ascending = False, inplace = True)
    
    twit_to_list = twit_to_list.apply(lambda row: tweet_to_list(row), axis = 1)
    # tl = twit_to_list.to_json(orient='values')

    toc = time.perf_counter()
    print(f"Processed tweets in {toc - tic:0.4f} seconds")

    # return tl
    return  jsonify(tweets_list = twit_to_list.tolist() )


@app.route('/_get_country')
def get_country():
    tic = time.perf_counter()
    country_name='US'

    country_name = request.args.get('country', '', type=str)
    print(country_name)
    confirmed_data, deaths_data, recovered_data, columns, dates_list, latest_data, countries_pops, new_data, US_data = get_data()
    # confirmed_data, deaths_data, recovered_data, columns, dates_list, latest_data, countries_pops, new_data = get_data()
    deaths_data = deaths_data.loc[deaths_data.Country==country_name]
    deaths_array = np.array(deaths_data.iloc[:,4:]).astype(int)
    deaths_totals = np.sum(deaths_array, axis = 0)
    print('ajax request is fine')

    confirmed_data = confirmed_data.loc[confirmed_data.Country==country_name]
    confirmed_array = np.array(confirmed_data.iloc[:,4:]).astype(int)
    confirmed_totals = np.sum(confirmed_array, axis = 0)

    country_deaths = deaths_totals[-1]
    country_confs = confirmed_totals[-1]

    c_pop = int(get_country_pop(countries_pops, country_name) )
    deaths_per_pop = deaths_totals[-1] / c_pop # to convert to %%
    cases_per_pop =  confirmed_totals[-1] / c_pop  # to convert to %%
    mortality = deaths_totals[-1] / confirmed_totals[-1]

    confirmed_diffs = confirmed_data[columns[0:4]].copy()
    for i in range(5,len(columns)):
        confirmed_diffs[columns[i]] = confirmed_data[columns[i]] - confirmed_data[columns[i-1]]

    # converting to 2d arrrays and getting totals
    confirmed_diffs_array = np.array(confirmed_diffs.iloc[:,4:]).astype(int)
    confirmed_diffs_totals = np.sum(confirmed_diffs_array, axis = 0)

    toc = time.perf_counter()
    print(f"Processed country's info in {toc - tic:0.4f} seconds")

    return  jsonify(dates = dates_list, confirmed_totals = confirmed_totals.tolist(), confirmed_diffs_totals = confirmed_diffs_totals.tolist(), 
                    deaths_totals = deaths_totals.tolist(), flag_pop = c_pop, confirmed_country = f'{country_confs:,}', deaths_country = f'{country_deaths:,}', 
                    country_population = f'{c_pop:,}', death_pct = f'{deaths_per_pop:.4%}', cases_pct = f'{cases_per_pop:.4%}' , mortality_rate = f'{mortality:.4%}' )


@app.route('/')
# @app.route('/virus-ncov2019')
def virus_ncov2019():
    tic = time.perf_counter()

    print('getting data')
    # confirmed_data, deaths_data, recovered_data, columns, dates_list, latest_data, countries_pops, new_data  = get_data()
    confirmed_data, deaths_data, recovered_data, columns, dates_list, latest_data, countries_pops, new_data, US_data = get_data()
    print('data is fine')
    toc = time.perf_counter()
    print(f"Loaded data in {toc - tic:0.4f} seconds")

    # converting to 2d arrrays and getting totals
    confirmed_array = np.array(confirmed_data.iloc[:,4:]).astype(int)
    confirmed_totals = np.sum(confirmed_array, axis = 0)
    cur_confirmed = confirmed_totals[-1]

    recovered_array = np.array(recovered_data.iloc[:,4:]).astype(int)
    recovered_totals = np.sum(recovered_array, axis = 0)
    cur_recovered = recovered_totals[-1]

    deaths_array = np.array(deaths_data.iloc[:,4:]).astype(int)
    deaths_totals = np.sum(deaths_array, axis = 0)
    cur_deaths = deaths_totals[-1]

    confirmed_data.loc[confirmed_data.State==0,'State'] = '- '
    recovered_data.loc[recovered_data.State==0,'State'] = '- '
    deaths_data.loc[deaths_data.State==0,'State'] = '- '

    start_point = ['40.7672726', '-73.9715264'] # new epicentre - NYC
    f_map = folium.Map(location=start_point, tiles='CartoDB dark_matter', zoom_start=8)

    sort_col = confirmed_data.columns[-1]
    confirmed_data = confirmed_data.sort_values(by = [sort_col], ascending = False)

    stats = confirmed_data.apply(lambda row: country_stat(row), axis = 1)
    extended_stats = confirmed_data.apply(lambda row: country_stat_ext(countries_pops, row, deaths_data), axis = 1)

    confirmed_diffs = confirmed_data[columns[0:4]].copy()
    for i in range(5,len(columns)):
        confirmed_diffs[columns[i]] = confirmed_data[columns[i]] - confirmed_data[columns[i-1]]

    # converting to 2d arrrays and getting totals
    confirmed_diffs_array = np.array(confirmed_diffs.iloc[:,4:]).astype(int)
    confirmed_diffs_totals = np.sum(confirmed_diffs_array, axis = 0)

    toc = time.perf_counter()
    print(f"Prepared data in {toc - tic:0.4f} seconds")

    #map all confirmed cases
    # row =4
    tac = time.perf_counter()
    if new_data:
        for row in range(latest_data.shape[0]):
            cur_row = latest_data.iloc[row]
            if cur_row.Confirmed>0:
                s_rad = radius_producer(cur_row.Confirmed)
            elif cur_row.Deaths>0:
                s_rad = radius_producer(cur_row.Deaths)
            elif cur_row.Recovered>0:
                s_rad = radius_producer(cur_row.Recovered)
            else: s_rad =0
    
            if s_rad > 0 :
                html_popup = "<div class='code' style='background: rgba(212, 212, 255, 0.035)'><b>{}</b> <br>".format(cur_row.Full_name) +  "Confirmed = {}".format(str(cur_row.Confirmed)) +  " <br> Deaths = {}".format(str(cur_row.Deaths))
                iframe = branca.element.IFrame(html=html_popup, width='250px', ratio="30%")
                popup = folium.Popup(iframe, max_width=500)
    
                CircleMarker([cur_row.Lat, cur_row.Long],
                        radius = max(3, s_rad * 2),
                        popup = popup,
                        parse_html  = True,
    
                        fill_opacity = 0.5,
                        weight = 0,
                        fill = True,
                        color=color_producer(1),
                        fillColor = color_producer(1)
                        ).add_to(f_map)
        fast_map_html = f_map._repr_html_()
        f = open('data/map.html', 'w')
        f.write(fast_map_html)
        f.close()
    else:
        f = open('data/map.html', 'r')
        fast_map_html = f.read()
        f.close()

    toc = time.perf_counter()
    print(f"Processed main part in {toc - tic:0.4f} seconds")
    print(f"Made the map in {toc - tac:0.4f} seconds")

    ext_USA_states = US_data.apply(lambda row: US_state_ext(row), axis = 1)

    return render_template('covid19.html', map_html = fast_map_html, last_update = dates_list[-1], x_Labels = dates_list, x_d_Labels = dates_list[1:],
                           confirmed_totals = json.dumps(confirmed_totals.tolist()), recovered_totals = json.dumps(recovered_totals.tolist()),
                           deaths_totals = json.dumps(deaths_totals.tolist()), confirmed_diffs_totals = json.dumps(confirmed_diffs_totals.tolist()),
                           total_conf = f'{cur_confirmed:,}', total_recov = f'{cur_recovered:,}', total_deaths = f'{cur_deaths:,}',
                           countries_list = json.dumps(stats.to_numpy().tolist()), ext_countries_list = json.dumps(extended_stats.to_numpy().tolist()), 
                           USA_data = json.dumps(ext_USA_states.to_numpy().tolist()))
                           # USA_data = json.dumps(US_data.to_numpy().tolist()))
