#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 19:28:40 2023

@author: vc
"""

#Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime as dt


#Load the raw datasets
raw1_df = pd.read_excel('/Users/vc/Library/CloudStorage/OneDrive-Personal/200 My Private/500 Digital Certificate/22 Portfolio/4 Python - RFM Customer Segmentation/online_retail_II.xlsx', sheet_name = 'Year 2009-2010')
raw2_df = pd.read_excel('/Users/vc/Library/CloudStorage/OneDrive-Personal/200 My Private/500 Digital Certificate/22 Portfolio/4 Python - RFM Customer Segmentation/online_retail_II.xlsx', sheet_name = 'Year 2010-2011')


#Merge the raw dataset
retail_df = pd.concat([raw1_df, raw2_df], ignore_index = True)
  
#Explore the raw dataset
retail_df.info()

#Display the raw dataset
retail_df.head()


### Data pre-processing ###

#Replace variable name which has space with deleting space
retail_df.columns = [s.strip().replace(' ','') for s in retail_df.columns]

#Remove the returned products (Invoice starting with C) from the raw dataset
retail_df = retail_df[~retail_df['Invoice'].str.contains('C', na = False)]
retail_df.dropna(inplace = True)

#Convert customer id to an integer
retail_df['CustomerID'] = retail_df['CustomerID'].astype(int)

#Convert invoice date to datetime type
retail_df['InvoiceDate'] = pd.to_datetime(retail_df['InvoiceDate'])

#Display the cleaned dataset
retail_df.info()


### RFM Analysis ###

## Recency ##

#Last invoice date
retail_df['InvoiceDate'].max()

#Last invoice date is assigned to new variable (today_date)
today_date = dt(2011,12,9)

#Grouping the last invoice dates by customer id, subtracting them from today_date --> recency
recency = (today_date - retail_df.groupby('CustomerID').agg({'InvoiceDate' : 'max'}))
           
#Rename column name as Recency
recency.rename(columns = {'InvoiceDate' : 'Recency'}, inplace = True)

#Change the values to day format
recency_df = recency['Recency'].apply(lambda x : x.days).to_frame()

#Display recency dataset
recency_df.head()


## Frequency ##

#Grouping the unique invoice dates by customer id --> freq_df
freq_df = retail_df.groupby('CustomerID').agg({'InvoiceDate' : 'nunique'})

#Rename column name as Frequency
freq_df.rename(columns = {'InvoiceDate' : 'Frequency'}, inplace = True)

#Display frequency dataset
freq_df.head()


## Monetary ##

#Multiplying the prices and qty of orders --> TotalPrice
retail_df['TotalPrice'] = retail_df['Quantity'] * retail_df['Price']

#Grouping and sum up the total price of each customer id
monetary_df = retail_df.groupby('CustomerID').agg({'TotalPrice' : 'sum'})

#Rename column name as Monetary
monetary_df.rename(columns = {'TotalPrice' : 'Monetary'}, inplace = True)

#Display frequency dataset
monetary_df.head()


## Concatenate RFM ##
rfm_df = pd.concat([recency_df, freq_df, monetary_df], axis = 1)

#Display rfm dataset
rfm_df.head()


## Scoring RFM Values ##

#Dividing the recency values into recency scores (from the lowest recency value as 5 to the highest as 1)
rfm_df['RecencyScore'] = pd.qcut(rfm_df['Recency'], 5, labels = [5, 4, 3, 2, 1])

#Dividing the frequency values into recency scores (from the lowest frequency value as 1 to the highest as 5)
rfm_df['FrequencyScore'] = pd.qcut(rfm_df['Frequency'].rank(method = 'first'), 5, labels = [1, 2, 3, 4, 5])

#Dividing the monetary values into recency scores (from the lowest monetary value as 5 to the highest as 1)
rfm_df['MonetaryScore'] = pd.qcut(rfm_df['Monetary'], 5, labels = [1, 2, 3, 4, 5])

#Combining Recency, Frequency, and Monetary Scores into staring format
rfm_df['RFM_Score'] = (rfm_df['RecencyScore'].astype(str) +
                       rfm_df['FrequencyScore'].astype(str) +
                       rfm_df['MonetaryScore'].astype(str))

#Customers with the best scores
best_rfm_df = rfm_df[rfm_df['RFM_Score'] == '555']
best_rfm_df.head()

#Customers with the worst scores
worst_rfm_df = rfm_df[rfm_df['RFM_Score'] == '111']
worst_rfm_df.head()


## Customer segmentation ##

#Mapping customer segment according to recency and frequency scores of customers
segment_df = {
    r'[1-2][1-2]' : 'Hibernating',
    r'[1-2][3-4]' : 'At Risk',
    r'[1-2]5' : 'Can\'t Loose',
    r'3[1-2]' : 'About to Sleep',
    r'33' : 'Need Attention',
    r'[3-4][4-5]' : 'Loyal Customers',
    r'41' : 'Promising',
    r'51' : 'New Customers',
    r'[4-5][2-3]' : 'Potential Loyalists',
    r'5[4-5]' : 'Champions'
    }

#Recency and Frequency scores are turned into string format, combined and assigned to Segment
rfm_df['Segment'] = rfm_df['RecencyScore'].astype(str) + rfm_df['FrequencyScore'].astype(str)

#Segments are changed with the definitions of segment_df
rfm_df['Segment'] = rfm_df['Segment'].replace(segment_df, regex = True)

#Display mean, median, count statistics of different segments
stat_df = rfm_df[['Segment', 'Recency', 'Frequency', 'Monetary']].groupby('Segment').agg(['mean', 'median', 'count'])


## Display data visualization ##

#Bar graph
plt.figure(figsize=(15, 5))
sns.countplot(data = rfm_df, x ='Segment')
plt.xlabel('Customer Segment')
plt.ylabel('No. of Customers')
plt.title('No. of Customers by Customer Segmentation')
plt.xticks(rotation = 45)
