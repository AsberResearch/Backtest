import backtrader as bt

class LowestCloseOfLast5Candles(bt.Strategy):
    params = (
        ('period', 5),  
    )
    
    def __init__(self):
        self.lowest_close = bt.ind.Lowest(self.data.close, period=self.params.period)  
        self.starting_balance = self.broker.get_cash()  
        self.trades = []
        self.order = None 

    def next(self):
        if self.data.close[0] == self.lowest_close[0]:  
            if not self.position:  
                self.buy()  
        elif self.position: 
            if self.data.close[0] > self.data.close[-1]: 
                self.close() 

    def notify_order(self, order):
        if order.status in [order.Completed]: 
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.sellprice = order.executed.price
                self.sellcomm = order.executed.comm

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trades.append(trade)

    def stop(self):
        final_balance = self.broker.get_value()  
        performance_vs_usd = final_balance - self.starting_balance
        buy_and_hold_performance = self.data.close[0] - self.data.close[-len(self.data) + 1]  
        performance_vs_buy_and_hold = performance_vs_usd - buy_and_hold_performance

        total_trades = len(self.trades)
        positive_trades = sum(1 for trade in self.trades if trade.pnl > 0)
        negative_trades = total_trades - positive_trades
        win_rate_ratio = positive_trades / total_trades if total_trades > 0 else 0

        print("----- General Information -----")
        print(f"Pair Symbol: {self.data._name}")
        print(f"Period: {self.params.period}")
        print(f"Starting balance: {self.starting_balance:.2f}")
        print(f"Final balance: {final_balance:.2f}")
        print(f"Performance vs US Dollar: {performance_vs_usd:.2f}")
        print(f"Buy and Hold Performance: {buy_and_hold_performance:.2f}")
        print(f"Performance vs Buy and Hold: {performance_vs_buy_and_hold:.2f}")
        print(f"Best trade: {max(trade.pnl for trade in self.trades):0.2f}")
        print(f"Worst trade: {min(trade.pnl for trade in self.trades):0.2f}")

        print("----- Trades Information -----")
        print(f"Total trades on period: {total_trades}")
        print(f"Number of positive trades: {positive_trades}")
        print(f"Number of negative trades: {negative_trades}")
        print(f"Trades win rate ratio: {win_rate_ratio:.2%}")
        print(f"Average trades performance: {sum(trade.pnl for trade in self.trades) / total_trades:.2f}")
        print(f"Average positive trades: {sum(trade.pnl for trade in self.trades if trade.pnl > 0) / positive_trades:.2f}" if positive_trades > 0 else "Average positive trades: 0.00")
        print(f"Average negative trades: {sum(trade.pnl for trade in self.trades if trade.pnl < 0) / negative_trades:.2f}" if negative_trades > 0 else "Average negative trades: 0.00")

cerebro = bt.Cerebro()

data = bt.feeds.GenericCSVData(
    dataname='/Users/marnocapitalgroup/nico/algoTrading/backtests/MR_BL_SH/btc_usdc_data.csv',
    dtformat='%Y-%m-%d',
    datetime=0,
    close=4,
    openinterest=-1,
    timeframe=bt.TimeFrame.Days,
    compression=1,
)

cerebro.adddata(data)
cerebro.addstrategy(LowestCloseOfLast5Candles)

cerebro.broker.setcash(1000)
cerebro.addsizer(bt.sizers.PercentSizer, percents=100)

results = cerebro.run()

# Plot the strategy
cerebro.plot()
