import pandas as pd
import numpy as np

# Importing data from the source

import yfinance as yf
import backtrader as bt
import matplotlib.pyplot as plt

# Baixa dados da ação (PETR4 ou AAPL)
# Note que para PETR4, o ticker no Yahoo é 'PETR4.SA'
ticker = 'PETR4.SA'  
data = yf.download(ticker, start='2022-01-01', end='2023-12-31')
print(data.columns)
# Corrige os nomes das colunas para o formato esperado
data.columns = [col[0].lower() for col in data.columns]
data.columns = data.columns.map(str)

# backtrader espera os dados num formato específico,
# então vamos usar o feed PandasData que o backtrader oferece:
datafeed = bt.feeds.PandasData(dataname=data)

# Estratégia simples de cruzamento de médias móveis
class SmaCrossStrategy(bt.Strategy):
    params = (('short_window', 10), ('long_window', 30),)

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_window)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_window)
        self.crossover = bt.indicators.CrossOver(self.sma_short, self.sma_long)

    def next(self):
        if not self.position:
            # Compra quando a média curta cruza pra cima da longa
            if self.crossover > 0:
                self.buy()
        else:
            # Vende quando a média curta cruza pra baixo da longa
            if self.crossover < 0:
                self.sell()

# Inicializa o engine do backtrader
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCrossStrategy)
cerebro.adddata(datafeed)
cerebro.broker.setcash(10000)  # saldo inicial 10.000

# Executa o backtest
print(f'Saldo inicial: {cerebro.broker.getvalue():.2f}')
cerebro.run()
print(f'Saldo final: {cerebro.broker.getvalue():.2f}')

# Plota o gráfico com backtrader
cerebro.plot(style='candlestick')
