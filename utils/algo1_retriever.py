#this function should be a holistic solution to storing all trading related data
from pymongo import MongoClient
import pandas as pd
import requests
import datetime
import api_calls

class retriever:
    def __init__(self, date, db_name, db_collection, db_endpoint):
        self.date = date
        self.db_name = db_name
        self.db_collection = db_collection
        self.db_endpoint = db_endpoint
        self.client = None
        self.db = None
        self.connect_db(db_endpoint)
        self.payload = {
        "time": self.date, 
        "tenders": {'tick_data': []}, 
        "orders": {},
        "trader": {"tick_data": []}
        }
    
    def connect_db(self, endpoint):
        self.client = MongoClient(endpoint)
        self.db = self.client[self.db_name]

    #reason why we are passing a session instead of initing is because we already have a session
    def gather_data(self, tick, tickers, s):
        if tick == 300:
            for ticker in tickers:
                self.payload[ticker]['tas'] = api_calls.get_tas(s, ticker)
                self.payload[ticker]['history'] = api_calls.get_history(s, ticker)
            self.payload['trader']['tick_data'].append(
                {
                    "tick": tick,
                    "nlv": api_calls.get_trader_data(s)['nlv']
                }
            )
            self.payload['orders'] = api_calls.get_all_orders(s)
            self.db_insert()
        else:

            for ticker in tickers:
                if ticker not in self.payload:
                    self.payload[ticker] = {"tick_data": []}
                self.payload[ticker]["tick_data"].append(
                        {"tick": tick,
                        "book": api_calls.get_trading_data(s,ticker)}
                    )

            self.payload['tenders']['tick_data'].append(
                {"tick": tick,
                "tenders": api_calls.get_tenders(s)
                }
            )
            securities = api_calls.get_securities(s)
            temp = {}
            for security in securities:
                temp[security['ticker']] = {
                    "VWAP": security['vwap'],
                    "Position": security['position'],
                    "Volume": security['volume']
                }
            self.payload['trader']['tick_data'].append(
                {
                    "tick": tick,
                    "nlv": api_calls.get_trader_data(s)['nlv'],
                    "securities_data": temp
                }
            )



    def db_insert(self):
        print('inserted payload')
        self.db[self.db_collection].insert_one(self.payload)


            
            
        
            


    
