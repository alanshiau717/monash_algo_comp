# this class definition allows us to print error messages and stop the program when needed
import requests

class ApiException(Exception):
    pass

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

def get_trading_data(session,ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_trader_data(session):
    resp = session.get('http://localhost:9999/v1/trader')
    if resp.ok:
        res = resp.json()
        return res
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_tas(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        return book
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_history(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/history', params = payload)
    if resp.ok:
        book = resp.json()
        return book
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_tenders(session): 
    resp = session.get('http://localhost:9999/v1/tenders')
    if resp.ok:
        book = resp.json()
        return book
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_orders(session, status):
    payload = {'status': status}
    resp = session.get('http://localhost:9999/v1/orders', params = payload)
    if resp.ok:
        book = resp.json()
        return book
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_all_orders(session):
    types = ['OPEN', 'TRANSACTED', 'CANCELLED']
    orders = {}
    for i in types:
        orders[i] = get_orders(session, i)
    return orders

def accept_tender(session, id):
    payload = {'id', id}
    resp = session.post('http://localhost:9999/v1/tenders', params = payload)
    if resp.ok:
        return 200
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    
def send_order(session, ticker, volume, o_type, action, price):
    if o_type == 'MARKET':
        payload = {
            'ticker':ticker,
            'type':o_type,
            'quantity' :volume,
            'action' : action,
        }
    else:
        payload = {
            'ticker' :ticker,
            'type' : o_type,
            'quantity': volume,
            'action' : action,
            'price' : price
        }
    resp = session.post('http://localhost:9999/v1/orders', params= payload)
    if resp.ok:
        return 200
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
