# this class definition allows us to print error messages and stop the program when needed
import requests

class ApiException(Exception):
    pass

def get_securities(session): 
    resp = session.get('http://localhost:9999/v1/securities')
    if resp.ok:
        case = resp.json()
        return case
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
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


def get_tas_param(session, ticker, limit):
    payload = {
        'ticker': ticker,
        'limit': limit
    }
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
    # print(id)
    resp =session.post('http://localhost:9999/v1/tenders/'+str(id))
    if resp.ok:
        # print('tender success')
        return 200
    # print(resp.json())
    # print('tender off failed')
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
        return resp.json()
    print(resp.json())
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def get_limits(session):
    resp = session.get("http://localhost:9999/v1/limits")
    if resp.ok:
        book = resp.json()
        return book[0]
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def cancel_order(session,o_id):
    resp = session.delete("http://localhost:9999/v1/orders/"+str(o_id))
    if resp.ok:
        # print('Successfully Cancled')
        return 200
    # print('Order Not Yet Executed')
    # print(resp.json())
    return None
    # raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def is_filled(session,o_id):
    resp = session.get("http://localhost:9999/v1/orders/"+str(o_id))
    if resp.ok:
        details = resp.json()
        if details['status']=="OPEN":
            return False
        else:
            # print('order_filled')
            return True
    # print(resp.json())
    return False
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

def order_exists(session, o_id):
    resp = session.get("http://localhost:9999/v1/orders/"+str(o_id))
    if resp.ok:
        return True
    else:
        return False