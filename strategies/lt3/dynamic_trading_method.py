from pymongo import MongoClient
import pandas as pd
import requests
import datetime
import api_calls
import numpy

class trade_handler:
    def __init__(self, tickers):
        self.data = {}
        self.tickers = tickers
        self.limits = {}
        for i in tickers:
            self.data[i] = {
                'VWAP': 0,
                'estimated_max_vol': 0,
                'current_stock': 0,
                'average_volume': 0,
                'time_to_sell': 0,
                'current_price': 0
            }
            if i =="TAME":
                self.data[i]['std'] = 0.189412361
            if i =="CRZY":
                self.data[i]['std'] = 0.23686543
        
    def tick_handler(self, session, tick):
        securities = api_calls.get_securities(session)
        for ticker in self.tickers:
            tas_data = api_calls.get_tas(session, ticker)
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
            for h in securities:
                if h['ticker'] == ticker:
                    self.data[ticker]['current_price'] = (h['bid']+h['ask'])/2
                    self.data[ticker]['bid'] = h['bid']
                    self.data[ticker]['ask'] = h['ask']
            
            self.data[ticker]['estimated_max_vol'] = total_volume * (300/tick)
            
            for j in securities:
                if j['ticker']==ticker:
                    self.data[ticker]['current_stock']=j['position']

            if tick >= 50:
                history = api_calls.get_history(session,ticker)
                stdev = []
                for i in history:
                    stdev.append(i['close'])
                self.data[ticker]['std'] = numpy.std(stdev)
        self.limits = api_calls.get_limits(session)
        tenders = api_calls.get_tenders(session)
        for i in tenders:
            if i['action'] == "BUY":
                self.buy_handler(i, session, tick)
            else:
                self.sell_handler(i, session, tick)
        self.unwind_handler(tick, session)
        
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
        print('Current Stock', curr_total)
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
                    return (abs(delta)-net_remaining)
            else:
                print('rejected due to gross limits')
                return(abs_delta - gross_remaining)
        return False

    def buy_handler(self, tender,session, tick):
        print('hit the buy handler')
        price = tender['price']
        volume = tender['quantity']
        ticker = tender['ticker']
        curr_price = self.data[ticker]['current_price']
        volatility = self.data[ticker]['std']
        max_vol = self.data[ticker]['estimated_max_vol']
        print(price,volume,ticker)
        print('Current Price',curr_price)
        print('Estimated Volatility',volatility)
        print('Maximum Volume', max_vol)
        print('Tick', tick)
        if tick < 240:
            time = 60
        else:
            time = 300-tick
        temp_impact = 0.142*(volatility)*(volume/(max_vol*(time/300)))**(0.6)
        expected_cost = volume*price*temp_impact
        expected_profit = volume*(curr_price-price)
        print('Expected Cost', expected_cost)
        print('Expected Profit', expected_profit) 
        if expected_profit>expected_cost:
            if self.limit_check(tender)== True:
                api_calls.accept_tender(session, tender['tender_id'])
                if self.data[ticker]['current_stock']>0:
                    print("Stock Already Exists adding additional stock")
                    print("Previous Time to Sell", self.data[ticker]['time_to_sell'])
                    new_volume = self.data[ticker]['current_stock'] + volume
                    print("Volume", volume)
                    print("New_Volume", new_volume)
                    print("Time", time)
                    self.data[ticker]['time_to_sell'] = (volume/new_volume)*time + (self.data[ticker]['current_stock']/new_volume)*self.data[ticker]['time_to_sell'] 
                    self.data[ticker]['current_stock'] = new_volume
                    self.data[ticker]['time_to_sell'] = round(self.data[ticker]['time_to_sell'],0)
                    print("Time to sell now", self.data[ticker]['time_to_sell'])
                elif self.data[ticker]['current_stock']==0:
                    self.data[ticker]['current_stock'] = volume
                    self.data[ticker]['time_to_sell'] = time
                else:
                    print("Negative stock exists offsetting")
                    print("Previous Time to Sell", self.data[ticker]['time_to_sell'])
                    if abs(self.data[ticker]['current_stock']) > volume:
                        old_volume = abs(self.data[ticker]['current_stock'])
                        self.data[ticker]['current_stock'] = self.data[ticker]['current_stock'] + volume
                        self.data[ticker]['time_to_sell'] = (self.data[ticker]['current_stock']/old_volume)*self.data[ticker]['time_to_sell']
                    else:
                        self.data[ticker]['current_stock'] = self.data[ticker]['current_stock'] + volume
                        self.data[ticker]['time_to_sell'] = (self.data[ticker]['current_stock']/volume)*time
                    self.data[ticker]['time_to_sell'] = round(self.data[ticker]['time_to_sell'],0)
                    print("Time to sell now", self.data[ticker]['time_to_sell'])
            else:
                print("Rejected Due to Limit Constraints")

 
                
    def sell_handler(self,tender,session,tick):
        print('hit the sell handler')
        price = tender['price']
        volume = tender['quantity']
        ticker = tender['ticker']
        curr_price = self.data[ticker]['current_price']
        volatility = self.data[ticker]['std']
        max_vol = self.data[ticker]['estimated_max_vol']
        print(price,volume,ticker)
        print('Current Price',curr_price)
        print('Estimated Volatility',volatility)
        print('Maximum Volume', max_vol)
        print('Tick', tick)
        if tick < 240:
            time = 60
        else:
            time = 300-tick
        temp_impact = 0.142*(volatility)*(volume/(max_vol*(time/300)))**(0.6)
        expected_cost = volume*price*temp_impact
        expected_profit = volume*(price-curr_price)
        print('Expected Cost', expected_cost)
        print('Expected Profit', expected_profit)
        print(temp_impact) 
        if expected_profit>expected_cost:
            if self.limit_check(tender)== True:
                api_calls.accept_tender(session, tender['tender_id'])
                if self.data[ticker]['current_stock']<0:
                    print("Stock Already Exists adding additional stock")
                    print("Previous Time to Sell", self.data[ticker]['time_to_sell'])
                    new_volume = self.data[ticker]['current_stock'] - volume
                    print("Volume", volume)
                    print("New_Volume", new_volume)
                    print("Time", time)
                    self.data[ticker]['time_to_sell'] = (-volume/new_volume)*time + abs((self.data[ticker]['current_stock']/new_volume))*self.data[ticker]['time_to_sell'] 
                    self.data[ticker]['current_stock'] = new_volume
                    self.data[ticker]['time_to_sell'] = round(self.data[ticker]['time_to_sell'],0)
                    print("Now Time to Sell", self.data[ticker]['time_to_sell'])
                elif self.data[ticker]['current_stock']==0:
                    self.data[ticker]['current_stock'] = -volume
                    self.data[ticker]['time_to_sell'] = time
                else:
                    print("Can offset stock")
                    print("Previous Time to Sell", self.data[ticker]['time_to_sell'])
                    #if we have more than we can offload
                    if abs(self.data[ticker]['current_stock']) > volume:
                        old_volume = abs(self.data[ticker]['current_stock'])
                        self.data[ticker]['current_stock'] = self.data[ticker]['current_stock'] - volume
                        self.data[ticker]['time_to_sell'] = (self.data[ticker]['current_stock']/old_volume)*self.data[ticker]['time_to_sell']
                    else:
                        self.data[ticker]['current_stock'] = self.data[ticker]['current_stock'] - volume
                        self.data[ticker]['time_to_sell'] = (self.data[ticker]['current_stock']/-volume)*time
                    self.data[ticker]['time_to_sell'] = round(self.data[ticker]['time_to_sell'],0)
                    print("Now Time to Sell", self.data[ticker]['time_to_sell'])
            else:
                print("Rejected Due to Limit Constraints")




    
    def unwind_handler(self, tick, session):
        print('hit unwind_handler')
        print(self.data)
        #first sell required amount to clear in required time
        for ticker in self.tickers:
            if self.data[ticker]["time_to_sell"]!=0:
                amount_required = self.data[ticker]['current_stock']//self.data[ticker]["time_to_sell"]
                print("Amount Required", amount_required)
                if amount_required>0:
                    api_calls.send_order(session, ticker, abs(amount_required), "MARKET", "SELL", 0)
                    self.data[ticker]["time_to_sell"] -=1
                elif amount_required<0:
                    api_calls.send_order(session, ticker, abs(amount_required), "MARKET", "BUY", 0)
                    self.data[ticker]["time_to_sell"] -=1
            else:
                pass
        #then scalp any remaining volume of the same length of time
        # prev_tick = tick 
        # tick = api_calls.get_tick(session)
        # ending_vols = {
        #     "CRZY": 0,
        #     "TAME": 0
        # }
        # original_vols = {
        #     "CRZY": 0,
        #     "TAME": 0
        # }
        # #initilize temp volums
        # securities = api_calls.get_securities(session)
        # for ticker in self.tickers:
        #     for i in securities:
        #         if i['ticker']==ticker:
        #             original_vols[ticker]=i['position']
        # while prev_tick == tick:
        #     for ticker in self.tickers:
        #         #make orders
        #         if self.data[ticker]['current_stock']>0:
        #             o_id = self.microtrade(ticker,"SELL",self.data[ticker]['bid'], session,self.data[ticker]['current_stock'])
        #             if api_calls.is_filled(session,o_id) == False:
        #                 api_calls.cancel_order(session,o_id)
        #         elif self.data[ticker]['current_stock']<0:
        #             o_id = self.microtrade(ticker,"BUY",self.data[ticker]['ask'], session,self.data[ticker]['current_stock'])
        #             if api_calls.is_filled(session,o_id) == False:
        #                 api_calls.cancel_order(session,o_id)
        #     tick = api_calls.get_tick(session)
        # #check volumes
        # securities = api_calls.get_securities(session)
        # for ticker in self.tickers:
        #     for i in securities:
        #         if i['ticker']==ticker:
        #             ending_vols[ticker]=i['position']
        #     if abs(ending_vols[ticker])!=0:
        #         self.data[ticker]['time_to_sell'] = (abs(original_vols[ticker])//abs(ending_vols[ticker]))*self.data[ticker]['time_to_sell']
        #     else:
        #         self.data[ticker]['time_to_sell'] = 0
            

    def microtrade(self, ticker, action, price, session,vol):
        book = api_calls.get_trading_data(session, ticker)
        #if we want to sell, check is buying price has stayed same or gone higher
        quantity = 0
        if action == "SELL":
            if price >= book['bids'][0]['price']:
                bid_price = book['bids'][0]['price']
                for i in book['bids']:
                    if i['price'] == bid_price:
                        quantity += (i['quantity'] - i['quantity_filled'])
                if quantity >=25000:
                    quantity = 25000
                resp = api_calls.send_order(session, ticker, min(quantity,abs(vol)), "LIMIT", "SELL", bid_price)
                if resp != -1:
                    return resp['order_id']
        elif action == "BUY":
            if price <= book['asks'][0]['price']:
                ask_price = book['asks'][0]['price']
                for i in book['asks']:
                    if i['price'] == ask_price:
                        quantity = i['quantity'] - i['quantity_filled']
                    if quantity >=25000:
                        quantity = 25000
                resp = api_calls.send_order(session, ticker, min(quantity,abs(vol)), "LIMIT", "BUY", ask_price)
                if resp != -1:
                    return resp['order_id']

