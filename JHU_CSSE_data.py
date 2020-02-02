# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 09:43:16 2020

@author: Alexey Kotlik
"""

import pandas as pd
import requests
from lxml import etree
import datetime

field_names = {
        'Province/State': 'State',
        'Country/Region': 'Country',
        'Last Update'   : 'Update',
        'Confirmed'     : 'Confirmed',
        'Deaths'        : 'Deaths',
        'Recovered'     : 'Recovered',
        'Demised'       : 'Deaths',
        ''              : 'Update',
        'Country'       : 'Country',
        'Suspected'     : 'Suspected'
        }

fColumns =  ['Country', 'State', 'Confirmed', 'Deaths', 'Recovered', 'Suspected', 'Update_date', 'Update_time', 'Report']
       
url = 'https://docs.google.com/spreadsheets/d/1yZv9w9zRKwrGTaR-YzmAqMefw4wMlaXocejdxZaTs6w'

# helper functions to clean some messy data 
def fix_china(row):
    if row == 'Mainland China': 
        row = 'China'
    return row

def fix_UAE(row):
    if row == '': 
        row = 'United Arab Emirates'
    return row

def fix_Chicago(row):
    if row == 'Chicago': 
        row = 'Illinois'
    return row
#---------------------------------
    
# helper function to transform dates/time 
def date_conversion(temp_date):
    d_list = temp_date.split(" ")
    if len(d_list) == 0:
        dt = datetime.datetime(0)
    else:
        date1 = d_list[0].split("/")
        dt = datetime.date(int(date1[2]),int(date1[0]),int(date1[1]))
                       
    return dt   
 
# helper function to transform dates/time 
def time_conversion(temp_date):
    d_list = temp_date.split(" ")
    dtime = ''
    if len(d_list) > 1:
        time1 = d_list[1].split(":")
        if len(d_list) == 2:
            dtime = datetime.time(int(time1[0]),int(time1[1]))
        else:
            if d_list[2] == 'PM':
                time1[0] = int(time1[0]) + 12
                if time1[0] == 24: time1[0]=0
            dtime = datetime.time(int(time1[0]),int(time1[1]))                       
    return dtime

# main function to get the data from the link, reorganize and clean it
def renew_data():
    r = requests.get(url, allow_redirects=True)
    open('JHU_CSSE_coronavirus.html', 'wb').write(r.content)

    parser = etree.HTMLParser()
    tree   = etree.parse('JHU_CSSE_coronavirus.html', parser)
    root = tree.getroot()

    days = []
    r_num = 0
    for report in root.iter("tbody"):
        r_num += 1

    rep_cnt = r_num        
    for report in root.iter("tbody"):
        regions = []
        header = []
        head_cell = report[0]
        for cell in head_cell[1:]:
            if ((rep_cnt == 1) and (cell.text == None)):
                header.append('Update')                 # the only case of missing field name on Jan 21st report
            elif (cell.text != None):
                header.append(field_names[cell.text])
            else:
                header.append('ttt')                    # fix problem with comment added on Feb 1st causing extra empty columns

#        print(header)
        regions.append(header)
        
        for row in report[1:]:
            region = []
            for cell in row[1:]:
                if cell.text == None:
                    if len(cell) > 1:
                        div = cell[0]
                        region.append(div.text)
                    else:
                        region.append("")
                else:
                    region.append(cell.text)
            regions.append(region)
        days.append(regions)
        rep_cnt -= 1
    
    report_N = len(days)
    df = pd.DataFrame(days[0][1:], columns = days[0][0])
    df['Suspected'] = ''
    df['Report'] = report_N

    for report in days[1:]:
#        print(report[0])
        report_N -= 1
        t_list = [x for x in report[0] if x!='ttt']     # fix problem with comment added on Feb 1st causing extra empty columns
        df_day = pd.DataFrame(report[1:], columns = report[0])
        df_day = df_day[t_list]                         # fix problem with comment added on Feb 1st causing extra empty columns
        df_day['Report'] = report_N
        df = df.append(df_day, ignore_index = False)      
            
    df.fillna(0, inplace = True)
    df["Suspected"].replace({"": 0}, inplace=True)
    df["Deaths"].replace({"": 0}, inplace=True)
    df["Recovered"].replace({"": 0}, inplace=True)
    df["Confirmed"].replace({"": 0}, inplace=True)
    df = df.astype({'Suspected': 'int','Recovered': 'int','Deaths': 'int','Confirmed': int, 'Report': int, 'State':str,'Country':str})
#    df = df.astype({'Suspected': 'int','Recovered': 'int','Deaths': 'int','Confirmed': 'int'})
          
    df['Update_date'] = df.Update.apply(lambda x : date_conversion(x))    
    df['Update_time'] = df.Update.apply(lambda x : time_conversion(x))    
    
    full_df = df[fColumns]
#    full_df.to_csv('reports.csv')    
        
    reports = full_df.Report.unique()
    confirmed = []
    deaths = []
    recovered = []
    timeline = []
    for rep in reports:
        cur_slice = full_df[full_df.Report == rep]
        confirmed.append(cur_slice.Confirmed.sum(axis=0))
        deaths.append(cur_slice.Deaths.sum(axis=0))
        recovered.append(cur_slice.Recovered.sum(axis=0))
        timeline.append(str(cur_slice.iloc[0].Update_date)+' '+str(cur_slice.iloc[0].Update_time))
        
    full_geo = full_df.copy()
        
    full_geo['Country'] = full_geo['Country'].apply(lambda x: fix_china(x))
    full_geo['Country'] = full_geo['Country'].apply(lambda x: fix_UAE(x))
    full_geo['State'] = full_geo['State'].apply(lambda x: fix_Chicago(x))

    full_geo.to_csv('reports.csv', index = False)    

#renew_data()
#full_geo[full_geo['State']=='']
#df.info()
