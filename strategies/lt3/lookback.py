from pymongo import MongoClient
import pandas as pd
import requests
import datetime
import api_calls

class vwap_lookback:
    def __init__(self, tickers,lookback):
        self.data = {}
        self.tickers = tickers
        self.limits = {}
        self.lookback = lookback
        for i in tickers:
            self.data[i] = {
                'VWAP': 0,
                'estimated_max_vol': 0,
                'current_stock': 0,
                'average_volume': 0
            }


    def tick_handler(self, session, tick):
        securities = api_calls.get_securities(session)
        for ticker in self.tickers:
            tas_data = api_calls.get_tas_param(session, ticker, self.lookback)
            total_volume = 0
            self.data[ticker]['VWAP'] = 0
            for j in tas_data:
                self.data[ticker]['VWAP'] += (j['quantity']*j['price'])
                total_volume += j['quantity']  
            if total_volume > 0:
                self.data[ticker]['VWAP'] = self.data[ticker]['VWAP']/total_volume
            else:
                for h in securities:
                    if h['ticker']==ticker:
                        self.data[ticker]['VWAP']= h['start_price']
                
            self.data[ticker]['estimated_max_vol'] = total_volume * (tick/300)
            for j in securities:
                if j['ticker']==ticker:
                    self.data[ticker]['current_stock']=j['position']
        self.limits = api_calls.get_limits(session)
        tenders = api_calls.get_tenders(session)
        for i in tenders:
            if i['action'] == "BUY":
                self.buy_handler(i, session)
            else:
                self.sell_handler(i, session)
        for i in self.tickers:
            self.trading(i, tick, session)
        
    def limit_check(self,tender):
        print('hit limit checker')
        net_remaining = self.limits['net_limit']-abs(self.limits['net'])
        gross_remaining = self.limits['gross_limit']-self.limits['gross']
        print('Net Limit', self.limits['net_limit'])
        print("Gross Limit", self.limits['gross_limit'])
        if tender['action']=="BUY":
            stock_change = tender['quantity']
        else:
            stock_change = -tender['quantity']
        curr_total = self.data[tender['ticker']]['current_stock']
        total_after = self.data[tender['ticker']]['current_stock'] + stock_change
        print('Current Stock', total_after)
        print('Total After tender', total_after)
        if abs(curr_total)<=total_after:
            return True
        else:
            delta = total_after - curr_total
            abs_delta = abs(total_after - curr_total)
            if abs_delta<=gross_remaining:
                if abs(delta)<=net_remaining:
                    return True
                else:
                    print('rejected due to net limits')
            else:
                print('rejected due to gross limits')
        return False




    def buy_handler(self, tender,session):
        print('hit the buy handler')
        price = tender['price']
        volume = tender['quantity']
        ticker = tender['ticker']
        print(price,volume,ticker)
        print('Calculated VWAP',self.data[ticker]['VWAP'] )
        if self.limit_check(tender):
            if price <= self.data[ticker]['VWAP']:
                if (volume+self.data[ticker]['current_stock'])<self.data[ticker]['estimated_max_vol']/10:
                    api_calls.accept_tender(session, tender['tender_id'])
                    self.data[ticker]['current_stock'] += volume
                else:
                    print('failed due to stock constaints')
            else:
                print('failed due to VWAP constaints')
        else:
            print('failed due to limit constaints')
    def sell_handler(self,tender,session):
        print('hit the sell handler')
        price = tender['price']
        volume = tender['quantity']
        ticker = tender['ticker']
        print('Calculated VWAP',self.data[ticker]['VWAP'] )
        print(price,volume,ticker)
        if self.limit_check(tender):
            if price >= self.data[ticker]['VWAP']:
                if (-volume+self.data[ticker]['current_stock'])<self.data[ticker]['estimated_max_vol']/10:
                    api_calls.accept_tender(session, tender['tender_id'])
                    self.data[ticker]['current_stock'] -= volume
                else:
                    print('failed due to stock constains')
            else:
                print('failed due to VWAP constaints')
        else:
            print('failed due to limit constaints')
            pass


    
    def trading(self, ticker, tick, session):
        #for each time period, sell x units 
        #assume volume is the same
        rem_ticks = (299 - tick)
        action = None
        print(self.data[ticker]['current_stock'])
        if self.data[ticker]['current_stock']>0:
            action = "SELL"
        elif self.data[ticker]['current_stock']<0:
            action = "BUY"
        if self.data[ticker]['current_stock']!=0:
            if rem_ticks==0:
                api_calls.send_order(session, ticker, abs(self.data[ticker]['current_stock']), "MARKET", action, 0)
            else:
                api_calls.send_order(session, ticker, abs(self.data[ticker]['current_stock']//rem_ticks), "MARKET", action, 0)
        