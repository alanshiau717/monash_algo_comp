from pymongo import MongoClient
import pandas as pd
import requests
import datetime
import api_calls

class simple_algo:
    def __init__(self, tickers):
        self.data = {}
        self.tickers = tickers
        for i in tickers:
            self.data[i] = {
                'VWAP': 0,
                'estimated_max_vol': 0,
                'current_stock': 0,
                'average_volume': 0
            }

    def tick_handler(self, session, tick):
        for ticker in self.tickers:
            tas_data = api_calls.get_tas(session, ticker)
            total_volume = 0
            self.data[ticker]['VWAP'] = 0
            for j in tas_data:
                self.data[ticker]['VWAP'] += j['quantity']
                total_volume += j['quantity']
            self.data[ticker]['VWAP'] = self.data[ticker]['VWAP']/total_volume
            self.data[ticker]['estimated_max_vol'] = total_volume * (tick/300)
        tenders = api_calls.get_tenders(session)
        for i in tenders:
            self.decision(i,session)
        
        for i in self.tickers:
            self.trading(ticker, tick, session)
        


    def decision(self, tender,session):
        price = tender['price']
        volume = tender['quantity']
        ticker = tender['ticker']
        if price >= self.data[ticker]['VWAP'] and (volume+self.data[ticker]['current_stock'])<self.data[ticker]['estimated_max_vol']/10:
            api_calls.accept_tender(session, tender['id'])
            self.data[ticker]['current_stock'] += volume
        else:
            pass
    
    def trading(self, ticker, tick, session):
        #for each time period, sell x units 
        #assume volume is the same
        rem_ticks = (299 - tick)
        if rem_ticks==0:
            api_calls.send_order(session, ticker, self.data[ticker]['current_stock'], "MARKET", "SELL", 0)
        else:
            api_calls.send_order(session, ticker, self.data[ticker]['current_stock']/rem_ticks, "MARKET", "SELL", 0)
        