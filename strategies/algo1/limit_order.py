import api_calls

def agg_volume(book, price, o_type):
    try:
        data = book[o_type]
        volume = 0
    except:
        print(data)
        print(o_type)
        print('Invalid Order Type')
        return volume
    if o_type == 'bids':
        for i in range(len(data)):
            if data[i]['price']>=price:
                volume += (data[i]['quantity']-data[i]['quantity_filled'])
            else:
                break
    else:
        for i in range(len(data)):
            if data[i]['price']<=price:
                volume += (data[i]['quantity']-data[i]['quantity_filled'])
            else:
                break
    return volume

def ticker_bid_ask(book):
    try:
        return book['bids'][0]['price'], book['asks'][0]['price']   
    except IndexError:
        return -1,-1


def tick_handler(s, tick,tickers):
    payload = get_max_vol(s)
    if payload == -1:
        return
    target_volume = payload['volume']
    curr_tick = tick
    while target_volume!=0 and curr_tick == tick:
        #make the order
        if target_volume >=10000:
            o_id1 = api_calls.send_order(s, "CRZY_M", 10000, "LIMIT", payload['CRZY_M']['ACTION'], payload['CRZY_M']['PRICE'])['order_id']
            o_id2 = api_calls.send_order(s, "CRZY_A", 10000, "LIMIT", payload['CRZY_A']['ACTION'], payload['CRZY_A']['PRICE']  )['order_id']
            target_volume -= 10000
        else: 
            o_id1 = api_calls.send_order(s, "CRZY_M", target_volume, "LIMIT", payload['CRZY_M']['ACTION'], payload['CRZY_M']['PRICE']  )['order_id']
            o_id2 = api_calls.send_order(s, "CRZY_A", target_volume, "LIMIT", payload['CRZY_A']['ACTION'], payload['CRZY_A']['PRICE']  )['order_id']
            target_volume = 0
        #wait for order to be completed
        while api_calls.is_filled(s,o_id1)!= True and curr_tick == tick and api_calls.is_filled(s,o_id2)!= True:
            curr_tick = api_calls.get_tick(s)
            continue
        api_calls.cancel_order(s,o_id1)
        api_calls.cancel_order(s,o_id2)
        #get positions and liquidate
        securities = api_calls.get_securities(s)
        for security in securities:
            if security['ticker'] in tickers:
                if security['position']!=0:
                    print('position')
                    if security['position'] >0:
                        api_calls.send_order(s, security['ticker'], security['position'], "MARKET", "SELL", 0)
                    else:
                        api_calls.send_order(s, security['ticker'], -security['position'], "MARKET", "BUY", 0)

        
        
def get_max_vol(s):
    crzy_m_book = api_calls.get_trading_data(s, 'CRZY_M')
    crzy_a_book = api_calls.get_trading_data(s, 'CRZY_A')
    crzy_m_bid, crzy_m_ask = ticker_bid_ask(crzy_m_book)
    crzy_a_bid, crzy_a_ask = ticker_bid_ask(crzy_a_book)
    if crzy_m_bid == -1 or crzy_a_bid == -1:
        return -1
    if crzy_m_bid > crzy_a_ask:
        crzy_m_vol = agg_volume(crzy_m_book, crzy_m_bid, 'bids')
        crzy_a_vol = agg_volume(crzy_a_book, crzy_a_ask, 'asks')
        volume = min(crzy_m_vol, crzy_a_vol)
        mid_point = (crzy_m_bid+crzy_a_ask)/2
        payload = {
            "CRZY_M": {
                "ACTION": "SELL",
                "PRICE": mid_point
                    },
            "CRZY_A": {
                "ACTION": "BUY",
                "PRICE": mid_point
            },
            'volume': volume
        }
        return payload
    if crzy_a_bid > crzy_m_ask:
        crzy_a_vol = agg_volume(crzy_a_book, crzy_a_bid, 'bids')
        crzy_m_vol = agg_volume(crzy_m_book, crzy_m_ask, 'asks')
        volume = min(crzy_a_vol, crzy_m_vol)
        mid_point = (crzy_a_bid+crzy_m_ask)/2
        payload = {
            "CRZY_A": {
                "ACTION": "SELL",
                "PRICE": mid_point
                    },
            "CRZY_M": {
                "ACTION": "BUY",
                "PRICE": mid_point
            },
            'volume': volume
        }
        return payload
    return -1
