from pymongo import MongoClient
import numpy
import matplotlib.pyplot as plt
import pandas
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.algo_comp
serverStatusResult=db.command("serverStatus")
# test_times = db.lt3.distinct('time')

# volumes = []
# prices = []
# for i in test_times:
#     print(db.lt3.find({"time": i}))

x_axis = []
for i in range(1,301):
    x_axis.append(i)

for i in db.lt3.find():
    volumes = [0] * 300
    prices = [0] * 300
    count = [0]* 300
    for j in i['tame']['tas']:
        volumes[j['tick']] += j['quantity']
        prices[j['tick']] += j['price']
        count[j['tick']] += 1
    for j in range(0,300):
        if count[j]!=0:
            prices[j] = prices[j]/count[j]
    plt.subplot(2, 1, 1)
    plt.plot(x_axis, volumes, 'ob')
    plt.title("Volumes")
    plt.subplot(2,1,2)
    plt.plot(x_axis, prices, 'ob')
    plt.title('Prices')
    plt.show()
exit()

    