class GridStrategy(object):
    #----------------------------------------------------------------------
    def __init__(self, exchange):
        """Constructor"""
        self.exchange = exchange
        self.symbol = self.exchange.symbol
        self.coin_a , self.coin_b = self.symbol.split("_")
        
        self.account = None
        self.depth = None

        self.init_bid = None
        self.init_ask = None

        # self.targetPos = {[-float('inf'),-10]:1 , [-10,-5]:0.7 , [-5,-1]:0.6 , [-1,1]:0.5,  [1,5]:0.4  [5,10]:0.3, [10,float('inf')]:0}
    
    def onInit(self):
        self.account = self.exchange.getAccount()
        self.init_depth = self.exchange.getDepth()
        
        self.init_ask = self.init_depth.best_ask
        self.init_bid = self.init_depth.best_bid
        self.init_middle = (self.init_ask + self.init_bid) / 2

    def cancelAll(self):
        for o in self.exchange.getOrders():
            self.exchange.cancelOrder(o)

    
    def main(self):
        
        self.cancelAll()

        self.account = self.exchange.getAccount()
        self.depth = self.exchange.getDepth()
        
        self.ask = self.depth.best_ask
        self.bid = self.depth.best_bid
        self.middle = (self.ask + self.bid) / 2

        self.balance = (self.account[self.coin_a] * self.bid + self.account[self.coin_b])
        self.coin_a_rate = (self.account[self.coin_a] * self.bid) / self.balance


        if self.middle < self.init_middle*(1-0.1):
            self.target_coin_a_rate = 1
        elif self.middle > self.init_middle*(1-0.1) and self.middle < self.init_middle*(1-0.05):
            self.target_coin_a_rate = 0.7
        elif self.middle > self.init_middle*(1-0.05) and self.middle < self.init_middle*(1-0.01):
            self.target_coin_a_rate = 0.6
        elif self.middle > self.init_middle*(1-0.01) and self.middle < self.init_middle*(1+0.01):
            self.target_coin_a_rate = 0.5
        elif self.middle > self.init_middle*(1+0.01) and self.middle < self.init_middle*(1+0.05):
            self.target_coin_a_rate = 0.4
        elif self.middle > self.init_middle*(1+0.05) and self.middle < self.init_middle*(1+0.1):
            self.target_coin_a_rate = 0.3
        elif self.middle > self.init_middle*(1+0.1):
            self.target_coin_a_rate = 0

        if abs(self.coin_a_rate - self.target_coin_a_rate) > 0.05:
            if self.coin_a_rate < self.target_coin_a_rate:
                #buy
                amount = round( self.balance*(self.target_coin_a_rate - self.coin_a_rate)/self.bid , 2)
                self.exchange.buy( self.bid , amount )
            if self.coin_a_rate > self.target_coin_a_rate:
                #sell
                amount = round( self.balance*(self.coin_a_rate - self.target_coin_a_rate)/self.ask , 2)
                self.exchange.sell( self.ask , amount )
        self.exchange.newTime(60)
            
        
    
