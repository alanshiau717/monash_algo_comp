from pymongo import MongoClient
import pandas as pd
import os
import numpy


client = MongoClient('mongodb://127.0.0.1:27017')
db = client['algo1']
serverStatusResult=db.command("serverStatus")
test_name = 'limit order full vol'
summary_stat = pd.DataFrame(columns = ['Test Time', "NLV","NLV Stdev", "CRZY_A Price Stdev", "CRZY_A Average Volume", "CRZY_M Price Stdev", "CRZY_M Average Volume"])           
for db_entry in db[test_name].find():
    temp = [db_entry['time']]
    temp.append(db_entry['trader']['tick_data'][-1]['nlv'])
    nlv = []
    tame_volume = []
    tame_price = []
    crzy_volume = []
    crzy_price = []
    for i in db_entry['trader']['tick_data']:
        nlv.append(i['nlv'])
    for i in db_entry['CRZY_M']["tas"]:
        tame_volume.append(i['quantity'])
        tame_price.append(i['price'])
    for i in db_entry['CRZY_A']['tas']:
        crzy_volume.append(i['quantity'])
        crzy_price.append(i['price'])
    temp.append(numpy.std(nlv))
    temp.append(numpy.std(crzy_price))
    temp.append(numpy.mean(crzy_volume))
    temp.append(numpy.std(tame_price))
    temp.append(numpy.mean(tame_volume))
    temp_series = pd.Series(temp, index = summary_stat.columns)
    summary_stat = summary_stat.append(temp_series, ignore_index = True)
temp = []
temp.append("Totals") 
temp.append(summary_stat['NLV'].mean())
temp.append(summary_stat['NLV'].std())
temp.append(summary_stat['CRZY_A Price Stdev'].mean())
temp.append(summary_stat['CRZY_A Average Volume'].std())
temp.append(summary_stat['CRZY_M Price Stdev'].mean())
temp.append(summary_stat['CRZY_M Average Volume'].std())
temp_series = pd.Series(temp, index = summary_stat.columns)
summary_stat = summary_stat.append(temp_series, ignore_index= True)
dir = os.path.join("Results",test_name)
if not os.path.exists(dir):
    os.mkdir(dir)
summary_stat.to_excel("Results/"+test_name+"/"+"Summary Stats.xlsx")



    
    