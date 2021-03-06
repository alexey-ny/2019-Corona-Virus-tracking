# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:41:41 2020

@author: Alexey Kotlik
"""

from JHU_CSSE_data import *

renew_data()

from mapping_data import *


map = folium.Map(location=start_point, tiles='CartoDB dark_matter', zoom_start=5)


# Add a bubble map to the base map
for idx, row in current_states.iterrows():
#for idx, row in un_states.iterrows():
        CircleMarker([row['Latitude'], row['Longitude']],
               radius = radius_producer(row['Name'], '', 'Confirmed'),
               popup = row['Name'] + ' '  + '(Confirmed='+str(10) + ' Deaths=' + str(5) + ' Recovered=' + str(5) + ')',
               fill_opacity = 0.3,
               weight = 2, 
               fill = True, 
               color=color_producer(2),
               fillColor = color_producer(2)
               ).add_to(map)
        CircleMarker([row['Latitude'], row['Longitude']],
               radius = radius_producer(row['Name'], '', 'Deaths'),
               fill_opacity = 0.3,
               weight = 1, 
               fill = False, 
               color=color_producer(1),
               ).add_to(map)

for idx, row in current_countries.iterrows():
#for idx, row in un_countries.iterrows():
        CircleMarker([row['Latitude'], row['Longitude']],
               radius = radius_producer('', row['Name'], 'Deaths'),
               popup = row['Name'] + ' '  + '(Confirmed='+str(10) + ' Deaths=' + str(5) + ' Recovered=' + str(5) + ')',
               fill_opacity = 0.3,
               weight = 2, 
               fill = True, 
               color=color_producer(2),
               fillColor = color_producer(2)
               ).add_to(map)
        CircleMarker([row['Latitude'], row['Longitude']],
               radius = radius_producer(row['Name'], '', 'Deaths'),
               fill_opacity = 0.3,
               weight = 1, 
               fill = False, 
               color=color_producer(1),
               ).add_to(map)

# Display the map
map.save("2019_nCoV_bubbles5.html")
