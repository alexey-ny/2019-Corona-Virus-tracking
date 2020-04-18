# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 21:04:38 2020

@author: alex
"""

from twitterscraper import query_tweets, query_tweets_from_user

from twitterscraper import Tweet
import collections
import datetime as dt
import pandas as pd

import twitterscraper 
import json, codecs


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        elif isinstance(obj, collections.Iterable):
            return list(obj)
        elif isinstance(obj, dt.datetime):
            return obj.isoformat()
        elif hasattr(obj, '__getitem__') and hasattr(obj, 'keys'):
            return dict(obj)
        elif hasattr(obj, '__dict__'):
            return {member: getattr(obj, member)
                    for member in dir(obj)
                    if not member.startswith('_') and
                    not hasattr(getattr(obj, member), '__call__')}

        return json.JSONEncoder.default(self, obj)

def parse_tweet(row):
    links = row.links
    hashtags = row.hashtags 
    t_text = row.text
    parsed = ''
    for l in links:
        found = t_text.find(l)
        parsed = t_text[:found]
        link_text = ' <a href="'+l+'">'+l+'</a>'
        t_text = parsed + link_text+ t_text[found+len(l):]

    parsed = ''
    for h in hashtags:
        found = t_text.find(h)
        parsed = t_text[:found]
        link_text = '<a href="https://twitter.com/hashtag/'+h+'">'+h+'</a>'
        t_text = parsed + link_text+ t_text[found+len(h):]

    return t_text

def tweet_parsing(df):
    df['parsed_text'] = df.apply(lambda row: parse_tweet(row), axis = 1)
    return df

def new_tweets():
    list_of_tweets_UN = query_tweets_from_user('UN',10)
    list_of_tweets_CDC = query_tweets_from_user('CDCgov',10)
    list_of_tweets_WHO = query_tweets_from_user('WHO',10)

    file = open('data/WHO_twitter_new.json','w')
    json.dump(list_of_tweets_WHO, file, cls=JSONEncoder)
    file.close()
    file = open('data/UN_twitter_new.json','w')
    json.dump(list_of_tweets_UN, file, cls=JSONEncoder)
    file.close()
    file = open('data/CDC_twitter_new.json','w')
    json.dump(list_of_tweets_CDC, file, cls=JSONEncoder)
    file.close()

    twit_CDC = pd.read_json('data/CDC_twitter_output.json', encoding='utf-8')
    new_twit_CDC = pd.read_json('data/CDC_twitter_new.json', encoding='utf-8')
    new_twit_CDC = tweet_parsing(new_twit_CDC)
    twit_df = pd.concat([twit_CDC, new_twit_CDC], ignore_index = True) 
    new_twit_CDC = twit_df.drop_duplicates('tweet_id')
    new_twit_CDC.to_json('data/CDC_twitter_output.json', orient = 'records')
    
    
    twit_UN = pd.read_json('data/UN_twitter_output.json', encoding='utf-8')
    new_twit_UN = pd.read_json('data/UN_twitter_new.json', encoding='utf-8')
    new_twit_UN = tweet_parsing(new_twit_UN)
    twit_df = pd.concat([twit_UN, new_twit_UN], ignore_index = True) 
    new_twit_UN = twit_df.drop_duplicates('tweet_id')
    new_twit_UN.to_json('data/UN_twitter_output.json', orient = 'records')

    twit_WHO = pd.read_json('data/WHO_twitter_output.json', encoding='utf-8')
    new_twit_WHO = pd.read_json('data/WHO_twitter_new.json', encoding='utf-8')
    new_twit_WHO = tweet_parsing(new_twit_WHO)
    twit_df = pd.concat([twit_WHO, new_twit_WHO], ignore_index = True) 
    new_twit_WHO = twit_df.drop_duplicates('tweet_id')
    new_twit_WHO.to_json('data/WHO_twitter_output.json', orient = 'records')

    twit_df = pd.concat([new_twit_CDC, new_twit_UN, new_twit_WHO], ignore_index = True) 

    return twit_df 
