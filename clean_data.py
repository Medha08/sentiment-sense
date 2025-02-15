# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 01:37:58 2018

@author: Saurabh
"""

import numpy as np

import pandas as pd
from textblob import TextBlob

import csv
import requests
import json
from datetime import date
import calendar
my_date = date.today()

from sklearn.preprocessing import MinMaxScaler



url = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/latest?period_id=1DAY&limit=7'
headers = {'X-CoinAPI-Key' : 'B1F03F85-01B1-408C-A128-F39602EEB90D'}
response = requests.get(url, headers=headers)

text_parsed = json.loads(response.text)
c=0

with open('test.csv', 'w', newline='') as csvfile:
    fieldnames = ["Date", "OpenPrice", "ClosePrice", "Difference"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for x in text_parsed:
        try:
            y = (my_date.weekday()-c)%7
            writer.writerow({'Date': calendar.day_name[y][0:3], 'OpenPrice': x['price_open'],'ClosePrice':x['price_close'],'Difference':x['price_open']-x['price_close']})
            c= c+1
        except:
            y=1
            writer.writerow({'Date': calendar.day_name[y][0:3], 'OpenPrice': x['price_open'],'ClosePrice':x['price_close'],'Difference':x['price_open']-x['price_close']})
            c= c+1

def find_Sentiment(filename = "Data_Set.csv"):
    df = pd.read_csv(filename)
    scaler = MinMaxScaler(feature_range =(0,1))
    X = df['followers_count']
    Z = df['retweet_count']
    
    X = X.reshape(len(X),1)
    Z = Z.reshape(len(X),1)
    # print (Z)

    #print ('\n\n\n\n\n',Y)

    data = scaler.fit_transform(X)
    data = data.flatten()
    df['followers_count'] = data
    data = scaler.fit_transform(Z)
    #data = to_list()
    data = data.flatten()
    df['retweet_count'] = data
    #print (df['retweet_count'])
    #print ('\n\n\n\n\n\n\n\n\n\n')
    sentiment_df = []
    # print(len(data);)
    for i in range(len(data)):
        try:

            temp = []
            analysis = TextBlob(df.loc[i]['text'])
            usr = df.loc[i]['name']
            day = df.loc[i]['created_at']
            followers = df.loc[i]['followers_count']
            retweet = df.loc[i]['retweet_count']
            temp.append(usr)
            temp.append(day)
            temp.append(followers)
            temp.append(retweet)
            temp.append(analysis.sentiment.polarity)
            temp.append(df.loc[i]['text'])
            # print (temp)
            sentiment_df.append(temp)

        except:
            print("Faulty Data")
        
    # print (sentiment_df) 
    
    # sentiment_df.to_csv("Dataset_SA_Tweet.csv")
    with open("Dataset_SA_Tweet.csv", 'w') as myfile:
        for obj in sentiment_df:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(obj)
    return sentiment_df

def find_Correlation(sentiment_df,price_Change):
    
    Final_corr = {}
    
    for i in range(len(sentiment_df)):
        try: 
            usr = sentiment_df[i][0]
            day = sentiment_df[i][1]
            follower = sentiment_df[i][2]
            retweet = sentiment_df[i][3]
            val = float(sentiment_df[i][4])

            diff_index = price_Change[price_Change['Date']==day].index
            
            for index in diff_index:
                val = val*price_Change.loc[index]['Difference']

            #val = val*diff
            try:
                Final_corr.update({usr:[Final_corr[usr][0] + val,Final_corr[usr][1]+1,follower,Final_corr[usr][3]+retweet]})
            except:
                Final_corr.update({usr:[val,1,0,0]})
        except:
            print("Faulty Data")
    
    for i in Final_corr.keys():
        Final_corr[i][0] = Final_corr[i][0]/Final_corr[i][1]          
    
    return Final_corr
            
        
            
    
    

if __name__=='__main__':
    
    

    sentiment_df = find_Sentiment()
    price_Change = pd.read_csv('test.csv')
    
    
    Final_corr = find_Correlation(sentiment_df,price_Change)
    
    
    # print (Final_corr)
    
    User_rank = pd.DataFrame(columns = ['username','value'])
    t  = 0
    for i in Final_corr.keys():

        User_rank = pd.DataFrame({'username':i,'value':(0.4*Final_corr[i][0]+0.2*Final_corr[i][2]+0.4*Final_corr[i][3])}, index=[0])
        # print ("Tempxx::\n\n"  , User_rank)
        break

        
        #User_rank.append(tempxx,ignore_index = True)

    for i in Final_corr.keys():
        if t==0:
            t = 1
            # print ("Never")
            continue

        tempxx = pd.DataFrame({'username':i,'value':0.4*Final_corr[i][0]+0.2*Final_corr[i][2]+0.4*Final_corr[i][3]}, index=[0])
        # print('username'+i +'sentiment'+Final_corr[i][0]+ 'followers_count:'+Final_corr[i][2]+ 'retweets:' + Final_corr[i][3])
        
        #print ("Tempxx::\n\n"  , tempxx)
        User_rank = User_rank.append(tempxx,ignore_index = True)

        ##User_rank = pd.concat(User_rank,[i,0.6*Final_corr[i][0]+0.2*Final_corr[i][2]+0.2*Final_corr[i][3]])
        #User_rank.loc[t] = [i,0.6*Final_corr[i][0]+0.2*Final_corr[i][2]+0.2*Final_corr[i][3]]
        t+=1#({i:0.6*Final_corr[i][0]+0.2*Final_corr[i][2]+0.2*Final_corr[i][3]})
    
    #import operator
    #x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
    #pdf = pd.DataFrame(User_rank)

    # check = User_rank.sort_values(by = 'value', ascending = False)
    #sorted_x = sorted(User_rank.items(), key=operator.itemgetter(1))
    #sorted_names = sorted(User_rank, key=User_rank.__getitem__)
    #rank = sorted(User_rank.values())
    #print (type(check),'\n\n\n\n\n\n\n\n\n')
    # print (User_rank.head())
    # print(sorted(User_rank))
    check = User_rank.sort_values("value",ascending = False)
    # print ("Sorted List")
    Top_users = (check.head(30))

    top = list()

    for i in Top_users['username']:
        for j in sentiment_df:
            if j[0]==i:
                top.append(j)

    # print ("Top Users")
    # print (top)   

    with open("Top_Dataset_SA_Tweet.csv", 'w') as myfile:
        for obj in top:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(obj)



    # User and SA
    check.to_csv("Top_Influencers.csv")
    
    # 

