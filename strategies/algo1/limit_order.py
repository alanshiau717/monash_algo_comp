import api_calls
import time
def agg_volume(book, price, o_type):
    try:
        data = book[o_type]
        volume = 0
    except:
        # print(data)
        # print(o_type)
        # print('Invalid Order Type')
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
    continue_arb = True
    while target_volume!=0 and curr_tick == tick and continue_arb == True:
        #make the order
        if target_volume >=10000:
            # print("Arbiting 10000")
            o_id1 = api_calls.send_order(s, "CRZY_M", 10000, "LIMIT", payload['CRZY_M']['ACTION'], payload['CRZY_M']['PRICE'])['order_id']
            o_id2 = api_calls.send_order(s, "CRZY_A", 10000, "LIMIT", payload['CRZY_A']['ACTION'], payload['CRZY_A']['PRICE']  )['order_id']
            target_volume -= 10000
        else: 
            # print("Arbiting", target_volume)
            o_id1 = api_calls.send_order(s, "CRZY_M", target_volume, "LIMIT", payload['CRZY_M']['ACTION'], payload['CRZY_M']['PRICE']  )['order_id']
            o_id2 = api_calls.send_order(s, "CRZY_A", target_volume, "LIMIT", payload['CRZY_A']['ACTION'], payload['CRZY_A']['PRICE']  )['order_id']
            target_volume = 0
        #wait for trades to be be on the order books
        order1_exist = False
        order2_exist = False
        while (order1_exist == False) and (order2_exist == False):
            order1_exist = api_calls.order_exists(s, o_id1)
            order2_exist = api_calls.order_exists(s, o_id2)
        time.sleep(0.1)
        #wait for order to be completed
        order1_filled = False
        order2_filled = False
        order1_filled = api_calls.is_filled(s,o_id1)
        order2_filled = api_calls.is_filled(s,o_id2)
        if order1_filled and order2_filled:
            continue_arb = True
            # print("ORDERS ALL FILLED")
        else:
            while (order1_filled == False) and (order2_filled == False):
                order1_filled = api_calls.is_filled(s,o_id1)
                order2_filled = api_calls.is_filled(s,o_id2)
            # print('after filled')
            api_calls.cancel_order(s,o_id1)
            api_calls.cancel_order(s,o_id2)
        
            #get positions and liquidate
            liquidate(s)
            continue_arb = False
        
        
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
        # print(volume//2)
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
        # print(volume)
        return payload
    return -1

def liquidate(s):
    #get all orders
    #cancel all orders
    orders = api_calls.get_orders(s,"OPEN")
    while len(orders)>0:
        for order in orders:
            api_calls.cancel_order(s, order['order_id'])
        orders = api_calls.get_orders(s,"OPEN")
    print('hit liquidate, no open orders found')
    securities = api_calls.get_securities(s)
    position = securities[0]['position']
    if position !=0:
        print('position', position)
        if position >0:
            max_bid = max(securities[0]['bid'], securities[1]['bid'])
            for security in securities:
                if security['bid'] == max_bid:
                    api_calls.send_order(s, security['ticker'], security['position'], "MARKET", "SELL", 0)
                    print('sent offsetting sell order')
                    break
        else:
            min_ask = min(securities[0]['ask'], securities[1]['ask'])
            for security in securities:
                if security['ask'] == min_ask:
                    api_calls.send_order(s, security['ticker'], -security['position'], "MARKET", "BUY", 0)
                    print('sent offsetting buy order')
                    break
    securities = api_calls.get_securities(s)
    position = securities[0]['position']
    if position != 0:
        time.sleep(1)
        if api_calls.get_status(s) == "ACTIVE":
            securities = api_calls.get_securities(s)
            position = securities[0]['position']
            if position !=0:
                print('position', position)
                if position >0:
                    max_bid = max(securities[0]['bid'], securities[1]['bid'])
                    for security in securities:
                        if security['bid'] == max_bid:
                            try:
                                api_calls.send_order(s, security['ticker'], security['position'], "MARKET", "SELL", 0)
                            except:
                                print('order failed')
                            print('sent offsetting sell order')
                            break
                else:
                    min_ask = min(securities[0]['ask'], securities[1]['ask'])
                    for security in securities:
                        if security['ask'] == min_ask:
                            try:
                                api_calls.send_order(s, security['ticker'], -security['position'], "MARKET", "BUY", 0)
                            except:
                                print('order failed')
                            print('sent offsetting buy order')
                            break
