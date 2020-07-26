#aim of this file is to retrieve data from the server and store it into mongodb
from pymongo import MongoClient
# This is a python example algorithm using REST API for the RIT ALGO1 Case
import signal
import requests
import pandas as pd 
import os
from time import sleep
import utils.data_retriever as dr
import datetime

# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass

# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

# this helper method returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_status(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        # print(case)
        return case['status']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

#this is the main we are using for testing
def test_main():
    counter = 0
    time = datetime.datetime.today()
    prev_tick = -1
    retriever = dr.retriever(time, 'algo_trader', test_name, db_endpoint)
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        status = get_status(s)
        while counter <= test_counter:
            #checks if the trading platform is running, if it is we do the trades
            if status == "ACTIVE":
                #this insures we only execute the trade_handler once a tick
                if prev_tick != tick:
                    prev_tick = tick
                    retriever.gather_data(tick, tickers,s)
                    # checks if we've finished the test, if we have we will increment the counter by 1
                    print(tick)
                tick = get_tick(s)
                status = get_status(s)
                if tick == 300:
                    retriever.gather_data(tick, tickers,s)
                    counter += 1
                    time = datetime.datetime.today()
                    retriever = dr.retriever(time, 'algo_trader', test_name, db_endpoint)
                    print('Completed', counter, 'Full test')
                    #sleeps 1 seconds to ensure same tick isn't executed again
                    sleep(3)
                    #updates tick and status which should be INACTIVE now
                    tick = get_tick(s)
                    status = get_status(s)
                    print(tick)
                    print(status)
            #if trading platform becomes inactive
            else:            
                tick = get_tick(s)
                status = get_status(s)
                sleep(1)
                print("Trading Platform not active")
            

#environment variables
test = True #back_test variable does various functions such as saving outputs and allows program to run in the background
test_name = 'data_retriever_test'
test_counter = 10
API_KEY = {'X-API-Key': '33XT2ML9'}
shutdown = False
db_endpoint = 'mongodb://127.0.0.1:27017'
tickers = ["CRZY", "TAME"]
# client = MongoClient('mongodb://127.0.0.1:27017')
# db = client.algo_comp
# serverStatusResult=db.command("serverStatus")




if __name__ == '__main__':
    # register the custom signal handler for graceful shutdowns
    counter = 0
    signal.signal(signal.SIGINT, signal_handler)
    if test == True:
        test_main()
    # else:
    #     main()
