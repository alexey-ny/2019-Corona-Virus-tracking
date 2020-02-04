# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:41:41 2020

@author: Alexey Kotlik
"""

import folium
from folium import Choropleth, Circle, Marker, CircleMarker
from folium.plugins import HeatMap, MarkerCluster
import numpy as np

from mapping_time_data import color_producer, radius_producer

from JHU_CSSE_timeline_data import *
confirmed_list, recovered_list, deaths_list = refresh_time_data()

start_point = ['30.97564', '112.2707'] # Hubei province

map = folium.Map(location=start_point, tiles='CartoDB dark_matter', zoom_start=5)

#map all confirmed cases
for row in confirmed_list[1:]:
    s_rad = radius_producer(row[-1])
    if s_rad > 0 :
        if s_rad < 3:
            s_rad = s_rad * 2
        CircleMarker([row[3], row[4]],
               radius = s_rad * 2,
#               radius = radius_producer(s_rad),
               popup = row[0] + ' ' + row[1]+ ' ' + '(Confirmed = '+ row[-1] + ')',
               fill_opacity = 0.3,
               weight = 2, 
               fill = True, 
               color=color_producer(1),
               fillColor = color_producer(1)
               ).add_to(map)

#map all deaths cases
for row in deaths_list[1:]:
    s_rad = radius_producer(row[-1])
    if s_rad > 0 :
        CircleMarker([row[3], row[4]],
               radius = s_rad * 2,
#               radius = radius_producer(s_rad) * 2,
               popup = row[0] + ' ' + row[1]+ ' ' + '(Deaths = '+ row[-1] + ')',
               fill_opacity = 0.3,
               weight = 2, 
               fill = True, 
               color=color_producer(2),
               fillColor = color_producer(2)
               ).add_to(map)

map.save("2019_nCoV_bubbles.html")

