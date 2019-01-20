class AccountData:
    pass

class DepthData:
    def __init__(self , row):
        self.bids = []
        self.asks = []
        self.bids_vol = []
        self.asks_vol = []
        self.row = row
    
    @property
    def best_bid(self):
        return self.row[402]
    
    @property
    def best_ask(self):
        return self.row[400]

class OrderData:
    symbol = None
    direction = None
    price = None
    volume = None
    orderID = None
    orderType = None
    orderTime = None
    status = None

class TradeData:
    symbol = None
    direction = None
    dealedAvgPrice = None
    volume = None
    tradeID = None
    orderID = None
    orderTime = None
    status = None
