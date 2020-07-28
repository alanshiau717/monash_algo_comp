# This is a python example algorithm using REST API for the RIT ALGO1 Case
import signal
import requests
import os
from time import sleep
import datetime
import api_calls
import strategies.algo1.limit_order as limit_order

# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass

# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True



#this is the main we are using for testing
def test_main():
    counter = 0
    time = datetime.datetime.today()
    prev_tick = -1
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = api_calls.get_tick(s)
        status = api_calls.get_status(s)
        # while status == "ACTIVE":
        #     print('Waiting for test to complete')
        #     status = api_calls.get_status(s)
        #     sleep(1)
        #     pass
        # status = api_calls.get_status(s)
        # print('Finished Waiting test to complete')
        while counter <= test_counter:
            #checks if the trading platform is running, if it is we do the trades
            if status == "ACTIVE":
                # market_order.trade_handler(s)
                #this insures we only execute the trade_handler once a tick
                if prev_tick != tick:
                    print(tick)
                    prev_tick = tick
                    limit_order.tick_handler(s, tick, tickers)
                    # checks if we've finished the test, if we have we will increment the counter by 1
                tick = api_calls.get_tick(s)
                status = api_calls.get_status(s)
                if tick == 299:
                    # market_order.trade_handler(s)
                    counter += 1
                    time = datetime.datetime.today()
                    print('Completed', counter, 'Full test')
                    #sleeps 1 seconds to ensure same tick isn't executed again
                    sleep(3)
                    #updates tick and status which should be INACTIVE now
                    tick = api_calls.get_tick(s)
                    status = api_calls.get_status(s)
                    print(tick)
                    print(status)
            #if trading platform becomes inactive
            else:            
                tick = api_calls.get_tick(s)
                status = api_calls.get_status(s)
                sleep(1)
                print("Trading Platform not active")
            

#environment variables
test = True #back_test variable does various functions such as saving outputs and allows program to run in the background
algorithm = 'algo1'
test_name = 'limit order low vol'
test_counter = 100
API_KEY = {'X-API-Key': '33XT2ML9'}
shutdown = False
db_endpoint = 'mongodb://127.0.0.1:27017'
tickers = ["CRZY_A", "CRZY_M"]




if __name__ == '__main__':
    # register the custom signal handler for graceful shutdowns
    print('hit')
    counter = 0
    signal.signal(signal.SIGINT, signal_handler)
    if test == True:
        test_main()
    # else:
    #     main()
