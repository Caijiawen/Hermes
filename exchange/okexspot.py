from .constants import *
from .exchange_datastructure import *

import h5py
import numpy as np
import datetime
from collections import OrderedDict
import time

class OkexSpot(object):
    def __init__(self,symbol,account,fee,initTrades=False):
        # super.__init__()
        self.time = None

        self.symbol = symbol
        self.coin_a , self.coin_b = self.symbol.split("_")
        self.account = account
        self.fee = fee

        self.depthData = None
        self.tradesData = None

        self.thisDepth = None
        
        self.depthPointer = None
        self.tradesPointer = None
        self.depthRow = None
        self.tradesRow = None

        self.limitOrderCount = 0                    # 限价单编号
        self.limitOrderDict = OrderedDict()         # 限价单字典
        self.workingLimitOrderDict = OrderedDict()  # 活动限价单字典，用于进行撮合用
        

        self.initTrades = initTrades
        self.tradeCount = 0             # 成交编号
        self.workingTradeDict = OrderedDict()  # 成交字典

    
    #----------------------------------------------------------------------
    
    def initDataHandler(self, startTime ):
        self.startTime = datetime.datetime.strptime(startTime, '%Y-%m-%d')
        self.time = self.startTime
        self.date = self.time.date()
        print(self.date)
        self.initDepthData( str(self.date) )
        if self.initTrades:
            self.initTradesData( str(self.date) )

    def checkDataHandler(self):
        if self.time.date() != self.date:
            self.date = self.time.date()
            self.initDepthData( str(self.date) )
            if self.initTrades:
                self.initTradesData( str(self.date) )


    def checkExitHandler(self, endTime):

        if self.time.date() > datetime.datetime.strptime(endTime, '%Y-%m-%d').date():
            return True
        return False
        
    def initDepthData(self, date):
        with h5py.File(f'/raid_disk/Caijiawen/data_saver/data/{self.symbol}/depth/{date}_depth.h5', 'r') as hf:
            self.depthData = hf['data'][:]
        self.depthPointer = 0
        self.depthRow = self.depthData.shape[0]
    
    def initTradesData(self, date):
        with h5py.File(f'/raid_disk/Caijiawen/data_saver/data/{self.symbol}/trade/{date}_trade.h5', 'r') as hf:
            self.tradesData = hf['data'][:]
        self.tradesPointer = 0
        self.tradesRow = self.tradesData.shape[0]
        self.filterLastdayTrade()
        print(self.tradesPointer)
    #----------------------------------------------------------------------


    def filterLastdayTrade(self):
        while True:
            if int(self.tradesData[self.tradesPointer,4]) > int(self.tradesData[self.tradesPointer+1,4]):
                self.tradesPointer += 1
            else:
                break


    
    def getTime(self):
        return self.time

    def getAccount(self):
        return self.account
    
    def getDepth(self):
        self.thisDepth = DepthData(self.depthData[self.depthPointer, :])
        return self.thisDepth
    
    def getOrders(self):
        return self.workingLimitOrderDict
    
    def getTrades(self):
        return self.workingTradeDict
    
    #----------------------------------------------------------------------
    
    def newTick(self):
        """新的Tick(一轮) not implemented yet"""
        self.newTick_updateDepth()
        self.newTick_updateTrades()


    def newTick_updateDepth(self):
        self.depthPointer += 1

        if self.depthPointer <= self.depthRow - 1:
            machineTime = self.depthData[self.depthPointer, 1]
            machineTime = datetime.datetime.fromtimestamp(machineTime)
            self.time = machineTime
        else:
            new_date = self.date + datetime.timedelta(days=1)
            # print(new_date)
            self.time = datetime.datetime(new_date.year, new_date.month, new_date.day)
            self.checkDataHandler()

    def newTick_updateTrades(self):

        self.workingTradeDict = OrderedDict()

        if self.tradesPointer > self.tradesRow - 1:
            return

        machineTime = self.tradesData[self.tradesPointer , 0]
        machineTime = datetime.datetime.fromtimestamp(machineTime)

        while machineTime <= self.time and self.tradesPointer <= self.tradesRow - 1:
            self.addTrades()
            self.tradesPointer += 1
            if self.tradesPointer <= self.tradesRow - 1:
                machineTime = self.tradesData[self.tradesPointer, 0]
                machineTime = datetime.datetime.fromtimestamp(machineTime)

    def addTrades(self):
        """把trades加入字典"""

        self.tradeCount += 1
        tradeID = str(self.tradeCount)

        trade = TradeData()
        trade.symbol = self.symbol
        trade.machineTime = self.tradesData[self.tradesPointer, 0]
        trade.direction = self.tradesData[self.tradesPointer , 5]
        trade.price = self.tradesData[self.tradesPointer , 2]
        trade.volume = self.tradesData[self.tradesPointer , 3]
        trade.exchangeID = self.tradesData[self.tradesPointer , 1]

        h,m,s = self.number_to_hour_minute_second(self.tradesData[self.tradesPointer, 4])
        trade.exchangeTime = time.mktime(datetime.datetime(self.date.year , self.date.month , self.date.day , h , m , s).timetuple())

        # 保存到限价单字典中
        self.workingTradeDict[tradeID] = trade

        return [tradeID]

    def number_to_hour_minute_second(self, num):
        num = str(int(num))
        str_num = (6 - len(num)) * '0' + num
        h = int(str_num[0:2])
        m = int(str_num[2:4])
        s = int(str_num[4:6])
        return h, m, s




    def newTime(self , strategy_round_time):
        """新的Time(一轮）"""
        # update time
        self.time += datetime.timedelta(0,strategy_round_time)
        self.checkDataHandler()
        # update depth pointer

        machineTime = self.depthData[self.depthPointer,1]
        machineTime = datetime.datetime.fromtimestamp(machineTime)

        if self.depthPointer == 0:
            while machineTime > self.time:
                self.time += datetime.timedelta(0, strategy_round_time)

        while machineTime <= self.time and self.depthPointer <= self.depthRow - 1:
            self.crossLimitOrder()
            self.depthPointer += 1
            machineTime = self.depthData[self.depthPointer,1]
            machineTime = datetime.datetime.fromtimestamp(machineTime)
        self.depthPointer -= 1
        assert self.depthPointer > 0
        
        
    #----------------------------------------------------------------------
    def buy(self, price, volume, priceType=None):
        """"""
        self.sendOrder(self.symbol , DIRECTION_LONG, price, volume, priceType)
    
    #----------------------------------------------------------------------
    def sell(self, price, volume, priceType=None):
        """"""
        self.sendOrder(self.symbol , DIRECTION_SHORT, price, volume, priceType)


    #----------------------------------------------------------------------
    def cancelOrder(self, vtOrderID):
        """撤单"""
        if vtOrderID in self.workingLimitOrderDict:
            order = self.workingLimitOrderDict[vtOrderID]
            order.status = STATUS_CANCELLED
            del self.workingLimitOrderDict[vtOrderID]
    
    #----------------------------------------------------------------------
    def sendOrder(self, symbol, direction, price, volume, orderType):
        """发单"""
        self.limitOrderCount += 1
        orderID = str(self.limitOrderCount)
        
        order = OrderData()
        order.symbol = symbol
        order.direction = direction
        order.price = price
        order.volume = volume
        order.orderID = orderID
        order.orderType = orderType
        order.orderTime = self.time.strftime('%H:%M:%S')
        
        
        # 保存到限价单字典中
        self.workingLimitOrderDict[orderID] = order
        self.limitOrderDict[orderID] = order
        
        return [orderID]
    
    #----------------------------------------------------------------------    
    def crossLimitOrder(self):
        #match engine
        for o in self.workingLimitOrderDict:
            order = self.workingLimitOrderDict[o]
            if order.direction == DIRECTION_LONG:
                if order.price > self.getDepth().best_ask:
                    # buy dealed
                    order.status = STATUS_ALLTRADED
                    # print("bid order traded.  price:" + str(order.price) + " amount: " + str(order.volume) )
                    self.account[self.coin_a] += order.volume
                    self.account[self.coin_b] -= order.volume * order.price
                    # print("new account " + str(self.account))
                    # print("balance: " + str(self.account[self.coin_a]*self.getDepth().best_bid+self.account[self.coin_b]))
                    del self.workingLimitOrderDict[o]
            if order.direction == DIRECTION_SHORT:
                if order.price < self.getDepth().best_bid:
                    # sell dealed
                    order.status = STATUS_ALLTRADED
                    # print("ask order traded.  price:" + str(order.price) + " amount: " + str(order.volume) )
                    self.account[self.coin_a] -= order.volume
                    self.account[self.coin_b] += order.volume * order.price
                    # print("new account " + str(self.account))
                    # print("balance: " + str(self.account[self.coin_a] * self.getDepth().best_bid + self.account[self.coin_b]))

                    del self.workingLimitOrderDict[o]
    
    
    
        
    
    
    
    
    
    
    