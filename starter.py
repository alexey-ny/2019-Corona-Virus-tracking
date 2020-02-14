# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:41:41 2020

@author: Alexey Kotlik
"""
import folium
from folium import CircleMarker
from folium.plugins import MarkerCluster
import numpy as np
import matplotlib.pyplot as plt
import json

# from mpld3 import plugins
# import base64
# from io import BytesIO

from JHU_CSSE_timeline_GitHub import *

from flask import Flask, render_template, redirect, url_for, request

confirmed_data, deaths_data, recovered_data, columns, dates_list = get_data()


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

xlabels = np.array(dates_list)


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
        num = np.sqrt(int(number))
        # num = int(np.sqrt(int(number)))
    return num

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')


# @app.route('/main', methods=['GET'])
# def main():
#     return render_template('main.html')
#     # return render_template('main.html', messages=messages)


confirmed_data.State[confirmed_data.State==0] = '- '
recovered_data.State[recovered_data.State==0] = '- '
deaths_data.State[deaths_data.State==0] = '- '

@app.route('/virus-ncov2019')
def virus_ncov2019():
    cur_url = url_for('static', filename='')

    start_point = ['30.97564', '112.2707'] # Hubei province
    f_map = folium.Map(location=start_point, tiles='CartoDB dark_matter', zoom_start=5)

    #map all confirmed cases
    row =42
    for row in range(confirmed_data.shape[0]):
        cur_row = confirmed_data.iloc[row]
        s_rad = radius_producer(cur_row[-1])
        if s_rad > 0 :
            if s_rad >70:
                s_rad = s_rad / 3
                if s_rad >150:
                    s_rad = s_rad / 4

            CircleMarker([cur_row[2], cur_row[3]],
                   radius = s_rad * 2,
                   # popup = str(cur_row[0]) + ' ' + str(cur_row[1])+ ' ' + '(Confirmed = '+ str(cur_row[-1]) + ')',
                   tooltip = str(cur_row[0]) + ' ' + str(cur_row[1])+ ' ' + '(Confirmed = '+ str(cur_row[-1]) + ')',
                   fill_opacity = 0.3,
                   weight = 2,
                   fill = True,
                   color=color_producer(1),
                   fillColor = color_producer(1)
                   ).add_to(f_map)

    #map all deaths cases
    for row in range(deaths_data.shape[0]):
        cur_row = deaths_data.iloc[row]
        s_rad = radius_producer(cur_row[-1])
        if s_rad > 0 :
            CircleMarker([cur_row[2], cur_row[3]],
                   radius = s_rad * 2,
                   # popup = str(cur_row[0]) + ' ' + str(cur_row[1])+ ' ' + '(Deaths = '+ str(cur_row[-1]) + ')',
                   tooltip = str(cur_row[0]) + ' ' + str(cur_row[1])+ ' ' + '(Deaths = '+ str(cur_row[-1]) + ')',
                   fill_opacity = 0.3,
                   weight = 2,
                   fill = True,
                   color=color_producer(2),
                   fillColor = color_producer(2)
                   ).add_to(f_map)

    return render_template('virus-ncov2019.html', main_css = cur_url, map_html = f_map._repr_html_(), x_Labels = json.dumps(dates_list), confirmed_totals = json.dumps(confirmed_totals.tolist()), recovered_totals = json.dumps(recovered_totals.tolist()), deaths_totals = json.dumps(deaths_totals.tolist()), total_conf = f'{cur_confirmed:,}', total_recov = f'{cur_recovered:,}', total_deaths = f'{cur_deaths:,}')
