from constans import *
import h5py
import numpy as np
import datetime

class Exchange:
    def __init__(self , account):
        self.dt = None      # 最新的时间
        self.tick = 0    # 最新的tick
        
        self.symbol = symbol
        self.depthData = {symbol:None for symbol in self.symbols}
        self.tradesData = {symbol:None for symbol in self.symbols}
        self.time = time

        self.limitOrderCount = 0                    # 限价单编号
        self.limitOrderDict = OrderedDict()         # 限价单字典
        self.workingLimitOrderDict = OrderedDict()  # 活动限价单字典，用于进行撮合用
        
        self.tradeCount = 0             # 成交编号
        self.tradeDict = OrderedDict()  # 成交字典

        self.account = self.initAccount(account)
    
    #----------------------------------------------------------------------
    
    def initAccount(self):
        raise NotImplementedError
    
    
    
    def newTick(self):
        """新的Tick(一轮)"""
        self.tick += 1
        self.strategy.onTick(tick)
        self.crossLimitOrder()
        self.updateInfo()
    
    #----------------------------------------------------------------------    
    def newTime(self , strategy_round_time):
        """新的Time(一轮）"""
        selt.dt += strategy_round_time
        self.strategy.onTime(self.dt)
        self.crossLimitOrder()
        self.updateInfo()

    def updateInfo(self):
        pass

    def initDepthData(self, symbol, date):
        with h5py.File(f'/raid_disk/Caijiawen/data_saver/data/{symbol}/depth/{date}_depth.h5', 'r') as hf:
            self.depthData[symbol] = hf['data'][:]
    
    def initTradesData(self, symbol, date):
        with h5py.File(f'/raid_disk/Caijiawen/data_saver/data/btc_usdt/1541568360004_depth.h5', 'r') as hf:
            self.tradesData[symbol] = hf['data'][:]

    def getDepth(self, symbol):
        pass
    
    def getTrades(self, symbol):
        pass
        
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
        order.orderTime = self.dt.strftime('%H:%M:%S')
        
        
        # 保存到限价单字典中
        self.workingLimitOrderDict[orderID] = order
        self.limitOrderDict[orderID] = order
        
        return [orderID]
    
    #----------------------------------------------------------------------
    def cancelOrder(self, vtOrderID):
        """撤单"""
        if vtOrderID in self.workingLimitOrderDict:
            order = self.workingLimitOrderDict[vtOrderID]
            
            order.status = STATUS_CANCELLED
            order.cancelTime = self.dt.strftime('%H:%M:%S')
            
            self.strategy.onOrder(order)
            
            del self.workingLimitOrderDict[vtOrderID]
    
    #----------------------------------------------------------------------
    def subscribe(self, symbol):
        """"""
        self.symbols.append(symbol)
        self.depthData[symbol] = None
        self.tradesData[symbol] = None
    
    #----------------------------------------------------------------------
    def buy(self, symbol, price, volume, priceType=None):
        """"""
        self.sendOrder(symbol, DIRECTION_LONG, price, volume, orderType)
    
    #----------------------------------------------------------------------
    def sell(self, symbol, price, volume, priceType=None):
        """"""
        self.sendOrder(symbol, DIRECTION_SHORT, price, volume, orderType)
    
    #----------------------------------------------------------------------
    def cancelOrder(self, OrderID):
        """"""
        if OrderID in self.workingLimitOrderDict:
            order = self.workingLimitOrderDict[OrderID]
            
            order.status = STATUS_CANCELLED
            order.cancelTime = self.dt.strftime('%H:%M:%S')
            
            self.strategy.onOrder(order)
            
            del self.workingLimitOrderDict[OrderID]
    
    #----------------------------------------------------------------------
    def putVarEvent(self, d):
        """更新变量"""
        d['active'] = self.active
        self.engine.putVarEvent(self, d)
    
    
    
    