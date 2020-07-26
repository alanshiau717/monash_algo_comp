from pymongo import MongoClient
import numpy
import matplotlib.pyplot as plt
import pandas
import datetime
import os

def zero_to_null(array):
    for i in range(len(array)):
        if array[i]==0:
            array[i]= None
    return array

#takes ticker and db_entry, then creates a chart with useful data
def create_ticker_chart(ticker,db_entry, test_name):
    x_axis = []
    for i in range(1,301):
        x_axis.append(i)
    volume = 0
    volumes = [0] * 300
    buy_transactions = [0]* 300
    sell_transactions = [0] * 300
    transaction_sequence = [[]] * 300
    bid = [0] * 300
    ask = [0] * 300
    count = [0]* 300
    tenders = [0] * 300
    #populate all the bid and ask prices
    for i in db_entry[ticker]['tick_data']:
        bid[i['tick']] = i['book']['bids'][0]['price']
        ask[i['tick']] = i['book']['asks'][0]['price']
    #populate all buy and sell transactions
    #put into array for volume calculations
    for i in db_entry['orders']['TRANSACTED']:
        if i['ticker'] == ticker:
            if i['action'] == 'BUY':
                buy_transactions[i['tick']] = i['vwap']
            else:
                sell_transactions[i['tick']] = i['vwap']
            transaction_sequence[i['tick']] = {'action':i['action'],
                                                'quantity':i['quantity_filled']}
    for i in db_entry['trader']['tick_data']:
            if 'securities_data' in i:
                volumes[i['tick']]=i['securities_data'][ticker]['Position']
    
    for i in db_entry['tenders']['tick_data']:
        if len(i['tenders'])>=1:
            if i['tenders'][0]['ticker'] == ticker:
                tick = i['tick']
                tenders[tick] = i['tenders'][0]['price']
    fig,ax=plt.subplots()
    bid = zero_to_null(bid)
    ask = zero_to_null(ask)
    tenders = zero_to_null(tenders)
    buy_transactions = zero_to_null(buy_transactions)
    sell_transactions = zero_to_null(sell_transactions)
    ax.plot(x_axis, volumes, '-')
    ax.set_ylabel("volume", fontsize=14)
    ax.set_xlabel('ticks', fontsize = 14)
    ax2 = ax.twinx()
    ax2.plot(x_axis, bid, '-', color = 'green')
    ax2.plot(x_axis,ask,'-', color = 'red')
    ax2.plot(x_axis, tenders, 'D', color = 'blue')
    ax2.plot(x_axis, buy_transactions, '.', color = 'green')
    ax2.plot(x_axis, sell_transactions, '.', color = 'red')
    ax2.set_ylabel('bid price')
    plt.title("Volumes and bid price")
    fig.savefig('Results'+"/"+test_name+"/"+str(db_entry['time']).replace(":","-")+'/'+ticker+".svg",
            format='svg',
            dpi=100,
            bbox_inches='tight')
    plt.close('all')

def create_trader_chart(db_entry,test_name):
    x_axis = []
    for i in range(1,302):
        x_axis.append(i)
    nlv = [0]*301
    for i in db_entry['trader']['tick_data']:
        nlv[i['tick']] = i['nlv']
    nlv = zero_to_null(nlv)
    fig,ax = plt.subplots()
    ax.plot(x_axis, nlv, '-')
    fig.savefig('Results'+"/"+test_name+"/"+str(db_entry['time']).replace(":","-")+'/'+"nlv.svg",
            format='svg',
            dpi=100,
            bbox_inches='tight')
    plt.close('all')


client = MongoClient('mongodb://127.0.0.1:27017')
db = client['lt3']
serverStatusResult=db.command("serverStatus")
test_name = 'lookback 50 fixed'           
for i in db[test_name].find():
    dir = os.path.join("Results",test_name, str(i['time']).replace(":","-"))
    if not os.path.exists(dir):
        os.mkdir(dir)
    create_ticker_chart("CRZY",i, test_name)
    create_ticker_chart("TAME",i, test_name)
    create_trader_chart(i, test_name)


        
    
    
        
