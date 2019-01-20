from okexspot import *
from grid_strategy import *

class Backtest:
    def __init__(self , exchange , strategy  , time_range):
        """
        symbols : []
        time_range : (t1 , t2)
        
        """
        self.time_range = time_range
        self.start_time = time_range[0]
        self.end_time = time_range[1]
        self.exchange = exchange
        self.strategy = strategy
    
    def run_backtesting(self):
        print(u'开始回测')
        

        exitFlag = False
        self.exchange.initDataHandler(self.start_time)
        self.strategy.onInit()

        while not exitFlag:
            self.strategy.main()
            exitFlag = self.exchange.checkExitHandler(self.end_time)
        
        print(u'结束回测')
        
    def show_backest_result(self):
        # strategy类里有result dictionary
        # 例子 {time : []  pnl : []}
        pass

def test_backtest():

    account = {'eos':1000 , 'usdt':2000}
    symbol = 'eos_usdt'
    fee = {'maker':0 , 'taker':0.005}
    okexspot = OkexSpot(symbol , account , fee)

    
    strategy = GridStrategy(okexspot)
    
    backtest = Backtest(okexspot , strategy , ('2018-12-15' , '2019-01-05'))
    backtest.run_backtesting()


test_backtest()