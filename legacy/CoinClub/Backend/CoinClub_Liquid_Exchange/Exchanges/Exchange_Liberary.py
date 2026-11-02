from FORMAT import Call_API
from FORMAT import Json

import json

#XDCXRP
#XLMXRP

class Bitrue_API:
    def __init__(self):
        print("STart Bitrue API")
        self.Biture_Main()

    def Biture_Main(self):  
        Asset_list = ["XDCXRP","XLMXRP"]

        #while True:
        output = Call_API.API_GET_Call("https://www.bitrue.com/","api/v1/ticker/24hr")

        for i in range(0,len(output)):
            name = output[i]["symbol"]
            final_name = "DATA/%s.json" % name
            Json.json_write(final_name ,output[i])

            READ = Json.read_json(final_name)

            [symbol,priceChange,priceChangePercent,
            weightedAvgPrice,prevClosePrice,lastPrice,
            lastQty,bidPrice,askPrice,openPrice,highPrice,
            lowPrice,volume,quoteVolume,openTime,closeTime,
            firstId,lastId,count]= self.ticker24hrOutput(READ)

            #print(symbol)
            #print(i)

            self.Selector(symbol,i,Asset_list)

    def Selector(self,Asset,Asset_Index,Aproved_Asset_list):
        #print("test selector")
        for i in Aproved_Asset_list:
            if Asset == i:
                READ = Json.read_json("DATA/%s.json" % Asset)
                
                [symbol,priceChange,priceChangePercent,
                weightedAvgPrice,prevClosePrice,lastPrice,
                lastQty,bidPrice,askPrice,openPrice,highPrice,
                lowPrice,volume,quoteVolume,openTime,closeTime,
                firstId,lastId,count]= self.ticker24hrOutput(READ)            

                print(Asset,Asset_Index,lastPrice)    
                return [Asset,Asset_Index,lastPrice]

################ TEST ################
    def Signed_Endpoint(self,symbol,side,type,timeInForce,quantity,price,recvWindow,timestamp):
        query_string = """
        symbol=%s&side=%s&type=%s&timeInForce=%s&quantity=%s&price=%s&recvWindow=%s&timestamp=%s
        """ % (symbol,side,type,timeInForce,quantity,price,recvWindow,timestamp)

    def Trigger_Buy(self):
        print("Trigger Buy")

    def Trigger_Sell(self):
        print("Trigger Sell")

    def Current_Open_Orders(self):
        #GET /api/v1/openOrders  (HMAC SHA256)
        #GET /api/v1/allOrders (HMAC SHA256) [ALL]
        print("current outstanding orders")

    def Cancel_Order(self):
        #DELETE /api/v1/order  (HMAC SHA256)
        print("Cancel Order")

    def Account_Info(self):
        # GET /api/v1/account (HMAC SHA256)
        print("current account info")

################ TEST ################

    def ticker24hrOutput(self,Data):
        #Data = json.loads(json_file)

        symbol = Data["symbol"]
        priceChange = Data["priceChange"]
        priceChangePercent = Data["priceChangePercent"]
        weightedAvgPrice = Data["weightedAvgPrice"]
        prevClosePrice = Data["prevClosePrice"]
        lastPrice = Data["lastPrice"]
        lastQty = Data["lastQty"]
        bidPrice  = Data["bidPrice"]
        askPrice = Data["askPrice"]
        openPrice = Data["openPrice"]
        highPrice = Data["highPrice"]
        lowPrice = Data["lowPrice"]
        volume = Data["volume"]
        quoteVolume = Data["quoteVolume"]
        openTime = Data["openTime"]
        closeTime = Data["closeTime"]
        firstId = Data["firstId"]
        lastId = Data["lastId"]
        count = Data["count"]

        return [symbol,priceChange,priceChangePercent,
                weightedAvgPrice,prevClosePrice,lastPrice,
                lastQty,bidPrice,askPrice,openPrice,highPrice,
                lowPrice,volume,quoteVolume,openTime,closeTime,
                firstId,lastId,count]



if __name__ == '__main__':
    Bitrue_API()
