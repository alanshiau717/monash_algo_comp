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

def trade_handler(s):
    #get all revelant data
    crzy_m_book = api_calls.get_trading_data(s, 'CRZY_M')
    crzy_a_book = api_calls.get_trading_data(s, 'CRZY_A')
    #decision buy all sell
    crzy_m_bid, crzy_m_ask = ticker_bid_ask(crzy_m_book)
    crzy_a_bid, crzy_a_ask = ticker_bid_ask(crzy_a_book)
    if crzy_m_bid == -1 or crzy_a_bid == -1:
        return
    if crzy_m_bid > crzy_a_ask:
        print("M BID Greater than A ask")
        print(crzy_m_bid, crzy_a_ask)
        crzy_m_vol = agg_volume(crzy_m_book, crzy_m_bid, 'bids')
        crzy_a_vol = agg_volume(crzy_a_book, crzy_a_ask, 'asks')
        volume = min(crzy_m_vol, crzy_a_vol)
        if volume > 10000:
            volume = 10000
        print(volume)
        crzy_a_params = {'ticker': 'CRZY_A', 'type': 'MARKET', 'quantity': volume, 'action': 'BUY'}
        crzy_m_params = {'ticker': 'CRZY_M', 'type': 'MARKET', 'quantity': volume, 'action': 'SELL'}
        s.post('http://localhost:9999/v1/orders', params=crzy_a_params)
        s.post('http://localhost:9999/v1/orders', params=crzy_m_params)
    if crzy_a_bid > crzy_m_ask:
        print("A BID Greater than M ask")
        crzy_a_vol = agg_volume(crzy_a_book, crzy_a_bid, 'bids')
        crzy_m_vol = agg_volume(crzy_m_book, crzy_m_ask, 'asks')
        volume = min(crzy_a_vol, crzy_m_vol)
        print(crzy_a_bid, crzy_m_ask)
        if volume > 10000:
            volume = 10000
        print(volume)
        crzy_a_params = {'ticker': 'CRZY_A', 'type': 'MARKET', 'quantity': volume, 'action': 'SELL'}
        crzy_m_params = {'ticker': 'CRZY_M', 'type': 'MARKET', 'quantity': volume, 'action': 'BUY'}
        s.post('http://localhost:9999/v1/orders', params=crzy_a_params)
        s.post('http://localhost:9999/v1/orders', params=crzy_m_params)

def get_max_vol(s):
    crzy_m_book = api_calls.get_trading_data(s, 'CRZY_M')
    crzy_a_book = api_calls.get_trading_data(s, 'CRZY_A')
    crzy_m_bid, crzy_m_ask = ticker_bid_ask(crzy_m_book)
    crzy_a_bid, crzy_a_ask = ticker_bid_ask(crzy_a_book)
    if crzy_m_bid == -1 or crzy_a_bid == -1:
        return
    if crzy_m_bid > crzy_a_ask:
        crzy_m_vol = agg_volume(crzy_m_book, crzy_m_bid, 'bids')
        crzy_a_vol = agg_volume(crzy_a_book, crzy_a_ask, 'asks')
        volume = min(crzy_m_vol, crzy_a_vol)
        payload = {
            "CRZY_A": "BUY",
            "CRZY_M": "SELL",
            "vol": volume
        }
    if crzy_a_bid > crzy_m_ask:
        crzy_a_vol = agg_volume(crzy_a_book, crzy_a_bid, 'bids')
        crzy_m_vol = agg_volume(crzy_m_book, crzy_m_ask, 'asks')
        volume = min(crzy_a_vol, crzy_m_vol)
        payload = {
            "CRZY_A": "BUY",
            "CRZY_M": "SELL",
            "vol": volume
        }
