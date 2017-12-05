import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from influxdb import InfluxDBClient
import basc_py4chan,requests,re,json,csv

def getCoinNames():
    #Gather Coins names from coinmarketcap ticker
    r=requests.get('https://api.coinmarketcap.com/v1/ticker/')
    return r.json()

def getBoard():
    #Get all information about a fchan board
    elements={}
    board=basc_py4chan.Board('biz',https=True,session=None)
    thread_ids = board.get_all_thread_ids() 
    #getAllthreads(board,thread_ids)
    i=0
    for id in thread_ids:
        elements[i]={}
        if board.thread_exists(id):
            thread=board.get_thread(id,update_if_cached=True,raise_404=False)
            data=thread.topic
            elements[i]['comment']=data.comment
            i=i+1
    return elements

def sendToDB(data):
    #Sends data to influxdb name 'fchan', should be created before running this
    client=InfluxDBClient('localhost',8086,'root','root','fchan')
    client.write_points(data)


#TODO:
#Figure out how to display infomration
##may require that i send data in different format so DB no final yet

#Gather information
coins=getCoinNames()
comments=getBoard()

#Set variables
results={}
i=0
for coin in coins:
    results[coin['symbol']]=0

#Preform Parsing
for number in comments:
    try:
        for coin in coins:
            if str(coin['symbol']).lower() not in str(comments[number]['comment']).lower() or str(coin['symbol']).lower() not in str(coments[number]['subject']):
                continue
            else:
                check='.*?'+"("+str(coin['symbol'])+")"
                rg=re.compile(check,re.IGNORECASE|re.DOTALL)
                c=rg.search(str(comments[number]['comment']))
                s=rg.search(str(comments[number]['subject']))
                if c:
                    #if match in comment
                    results[coin['symbol']]=results[coin['symbol']]+1
                elif s:
                    #if match in subject
                    results[coin['symbol']]=results[coin['symbol']]+1
    except:
        #Should some kind of error occur, here is the 
        print "------------------ERROR-------------------"
        print "Coin: " + coin['symbol']
        print "Comment: " + comments[number]['comment']
        #print "Subject: " + comments[number]['subject']
        print "------------------ERROR-------------------"
        continue


coins_data=open('/tmp/coindata.csv','w')
#Load information into influxDB
print results
for coin in results:
    print("name=",coin)
    #json_body=[{"measurement":coin,"fields":{"value":results[coin]}}]
    json_body='{"coinDetail":[{"coinName":'+str(coin)+',"occ":'+str(results[str(coin)])+'}]}'
    #json_body="[{"+"coindDetail"+":{"+str(coin)+":"+str(results[coin])+"}}]"
    #sendToDB(json_body)
    coin_parsed=json.loads(json_body)
    coin_data=coin_parsed['coinDetail']
    csvwriter=csv.writer(coins_data)
    
    count=0
    for cin in coin_data:
        if count==0:
            header=cin.keys()
            cswriter.writerow(header)
            count += 1
        cswriter.writerow(cin.values())
coins_data.close()
