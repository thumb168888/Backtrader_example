import backtrader as bt
import pandas as pd
import datetime
import datetime as dt
import backtrader.indicators as btind
from pandas_datareader import data as web
import yfinance as yf

#choose stockNo fastma,slowma
stockNo="2330"
fast_ma=20
slow_ma=60

stock_id=stockNo+".TW"
yf.pdr_override()

# date
start = dt.datetime(2000, 1, 1)
end = datetime.datetime.today()


# save to csv
df = web.get_data_yahoo([stock_id],start, end)
stock_csv_path=r'D:\jack\python\code\stock\backtest\stock.csv'
df.to_csv(stock_csv_path)



class TestStrategy(bt.Strategy):
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        # Write down: no pending order
        self.order = None

        
    alias = ('SMA_CrossOver',)

    params = (
        # period for the fast Moving Average
        ('fast', fast_ma),
        # period for the slow moving average
        ('slow', slow_ma),
        # moving average to use
        ('_movav', btind.MovAv.SMA)
    )

 

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        sma_fast = self.p._movav(period=self.p.fast)
        sma_slow = self.p._movav(period=self.p.slow)

        self.buysig = btind.CrossOver(sma_fast, sma_slow)

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.position.size:
            if self.buysig < 0:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.sell()
        elif self.buysig > 0:
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.buy()
			# elif self.buysig>0:
			# 	self.log('BUY CREATE, %.2f' % self.dataclose[0])
			# 	self.buy()           
                    
if __name__ == '__main__':    

    
    cerebro = bt.Cerebro()
    
    cerebro.addstrategy(TestStrategy)
    
    cerebro.broker.setcash(10000.0)

    #load csv
    dataframe = pd.read_csv(stock_csv_path,index_col=0,parse_dates=True)
    data0 = bt.feeds.PandasData(dataname=dataframe,
                                   fromdate = datetime.datetime(2000, 1, 1),
                                   todate = datetime.datetime.today()
                                    )
    cerebro.adddata(data0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
    
    #save pic
    figure = cerebro.plot(style ='candlebars')[0][0]
    figure.savefig('example.png')
