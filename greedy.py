# This is a python example algorithm using REST API for the RIT ALGO1 Case
import signal
import requests
import pandas as pd
from time import sleep


# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass

# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

API_KEY = {'X-API-Key': '33XT2ML9'}
shutdown = False

# this helper method returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        # print(case)
        return case['tick']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_status(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        # print(case)
        return case['status']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

# this helper method returns the bid and ask for a given security
# def ticker_bid_ask(session, ticker):
#     payload = {'ticker': ticker}
#     resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
#     if resp.ok:
#         book = resp.json()
#         return book['bids'][0]['price'], book['asks'][0]['price']
#     raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

# this returns all revelevant book data for a share
def get_trading_data(session,ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

#returns bid ask prices for a given book
def ticker_bid_ask(book):
    return book['bids'][0]['price'], book['asks'][0]['price']


#returns data regarding trader id first name, last name and nlv
def get_trader_data(session):
    resp = session.get('http://localhost:9999/v1/trader')
    if resp.ok:
        res = resp.json()
        return res
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')




#takes some order params and the order book, then returns price, volume and action in an array form
def parse_order(params, book):
    if params['type'] == "MARKET":
        if params['action'] == 'BUY':
            return [book['asks'][0]['price'], params['quantity'], params['action']]
        else:
            return [book['bids'][0]['price'], params['quantity'], params['action']]
    return [params['price'], params['quantitiy'], params['action']]
    
#takes the dataframe, uses the nlv to calculate profit and price
def calc_profit(data):
    for i in range(1, len(data)):
        data.loc[i, 'Profit'] = data.loc[i, 'nlv'] - data.loc[i-1, 'nlv']
        if data.loc[i-1,'crzy_a_price'] > data.loc[i-1,'crzy_m_price']:
            data.loc[i, 'Expected Profit'] = (float(data.loc[i-1,'crzy_a_price']) - float(data.loc[i-1,'crzy_m_price']))*float(data.loc[i-1,'crzy_a_qty'])
        else:
            data.loc[i, 'Expected Profit'] = (float(data.loc[i-1,'crzy_m_price']) - float(data.loc[i-1,'crzy_a_price']))*float(data.loc[i-1,'crzy_a_qty'])
    return data


    

# this function handles all trading activities
def trade_handler(s,tick):
    global data
    #get all revelant data
    crzy_m_book = get_trading_data(s, 'CRZY_M')
    crzy_a_book = get_trading_data(s, 'CRZY_A')
    #decision buy all sell
    crzy_m_bid, crzy_m_ask = ticker_bid_ask(crzy_m_book)
    crzy_a_bid, crzy_a_ask = ticker_bid_ask(crzy_a_book)
    if crzy_m_bid > crzy_a_ask:
        volume = min(crzy_m_book['bids'][0]['quantity'], crzy_a_book['asks'][0]['quantity'])
        if volume > 10000:
            volume = 10000
        print(volume)
        crzy_a_params = {'ticker': 'CRZY_A', 'type': 'MARKET', 'quantity': volume, 'action': 'BUY'}
        crzy_m_params = {'ticker': 'CRZY_M', 'type': 'MARKET', 'quantity': volume, 'action': 'SELL'}
        s.post('http://localhost:9999/v1/orders', params=crzy_a_params)
        s.post('http://localhost:9999/v1/orders', params=crzy_m_params)
    if crzy_a_bid > crzy_m_ask:
        volume = min(crzy_a_book['bids'][0]['quantity'], crzy_m_book['asks'][0]['quantity'])
        if volume > 10000:
            volume = 10000
        print(volume)
        crzy_a_params = {'ticker': 'CRZY_A', 'type': 'MARKET', 'quantity': volume, 'action': 'SELL'}
        crzy_m_params = {'ticker': 'CRZY_M', 'type': 'MARKET', 'quantity': volume, 'action': 'BUY'}
        s.post('http://localhost:9999/v1/orders', params=crzy_a_params)
        s.post('http://localhost:9999/v1/orders', params=crzy_m_params)
    #gather data and put it into the data frame
    trader_data = get_trader_data(s)
    temp = [tick, trader_data['nlv'], crzy_a_book['bids'][0]['price'],crzy_a_book['bids'][0]['quantity'], crzy_a_book['asks'][0]['price'],crzy_a_book['asks'][0]['quantity'], crzy_m_book['bids'][0]['price'],crzy_m_book['bids'][0]['quantity'], crzy_m_book['asks'][0]['price'],crzy_m_book['asks'][0]['quantity']]
    try:
        temp = temp + parse_order(crzy_a_params, crzy_a_book)
        temp = temp + parse_order(crzy_m_params, crzy_m_book)
    except UnboundLocalError:
        temp = temp + [0,0,0,0,0,0]
    temp_series = pd.Series(temp, index = data.columns)
    data = data.append(temp_series, ignore_index = True)





    
    


#this is the main we are using for testing
def test_main():
    global data
    counter = 0
    prev_tick = -1
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        status = get_status(s)
        while counter <= test_counter:
            #checks if the trading platform is running, if it is we do the trades
            if status == "ACTIVE":
                #this insures we only execute the trade_handler once a tick
                if prev_tick != tick:
                    trade_handler(s, tick)
                    prev_tick = tick
                    # data_handler(s)
                    # checks if we've finished the test, if we have we will increment the counter by 1
                    print(tick)
                tick = get_tick(s)
                status = get_status(s)
                if tick == 299:
                    counter += 1
                    print('Completed', counter, 'Full test')
                    #sleeps 1 seconds to ensure same tick isn't executed again
                    sleep(3)
                    #updates tick and status which should be INACTIVE now
                    tick = get_tick(s)
                    status = get_status(s)
                    data = calc_profit(data)
                    #writes to excel
                    data.to_excel(test_name+str(counter)+'.xlsx',
                        sheet_name='Sheet_name_1')  
                    # with pd.ExcelWriter(test_name+ '.xlsx',
                    #                     mode='a') as writer:  
                    #     data.to_excel(writer, sheet_name='Test'+counter)
                    #reinitizilze array
                    data.drop(data.index, inplace=True)
                    data.pop("Profit")
                    data.pop('Expected Profit')
            #if trading platform becomes inactive
            else:            
                tick = get_tick(s)
                status = get_status(s)
                sleep(1)
                print("Trading Platform not active")

            

#environment variables
test = True #back_test variable does various functions such as saving outputs and allows program to run in the background
test_name = 'Greedy buy sell strat'
test_counter = 5
data = pd.DataFrame(columns = ['tick','nlv', 'crzy_a_bid_price', 'crzy_a_bid_volume', 'crzy_a_ask_price', 'crzy_a_ask_volume', 'crzy_m_bid_price', 'crzy_m_bid_volume', 'crzy_m_ask_price', 'crzy_m_ask_volume', 'crzy_a_price', 'crzy_a_qty', 'crzy_a_action', 'crzy_m_price', 'crzy_m_qty', 'crzy_m_action']) #initialize dataframe used for storing all the data in a single session

if __name__ == '__main__':
    # register the custom signal handler for graceful shutdowns
    counter = 0
    signal.signal(signal.SIGINT, signal_handler)
    if test == True:
        test_main()
    # else:
    #     main()
