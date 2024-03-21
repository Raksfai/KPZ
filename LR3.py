import pandas as pd
import ta
from matplotlib import pyplot as plt
from binance import Client

# Loading data
k_lines = Client().get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 day ago UTC",
    end_str="now UTC"
)

# Creating DataFrame
k_lines = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)

# Indicator calculation
k_lines['RSI'] = ta.momentum.RSIIndicator(k_lines['close']).rsi()
k_lines['CCI'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()
k_lines['MACD'] = ta.trend.MACD(k_lines['close']).macd()
k_lines['ATR'] = ta.volatility.AverageTrueRange(k_lines['high'], k_lines['low'], k_lines['close']).average_true_range()
k_lines['ADX'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()

# Creating signal columns
k_lines['RSI_buy_signal'] = (k_lines['RSI'] < 30) & (k_lines['RSI'].shift() >= 30)
k_lines['RSI_sell_signal'] = (k_lines['RSI'] > 70) & (k_lines['RSI'].shift() <= 70)
k_lines['CCI_buy_signal'] = (k_lines['CCI'] < -100) & (k_lines['CCI'].shift() >= -100)
k_lines['CCI_sell_signal'] = (k_lines['CCI'] > 100) & (k_lines['CCI'].shift() <= 100)
k_lines['MACD_buy_signal'] = (k_lines['MACD'].shift() < 0) & (k_lines['MACD'] > 0)
k_lines['MACD_sell_signal'] = (k_lines['MACD'].shift() > 0) & (k_lines['MACD'] < 0)
k_lines['ATR_buy_signal'] = k_lines['ATR'] > k_lines['ATR'].shift()
k_lines['ATR_sell_signal'] = k_lines['ATR'] < k_lines['ATR'].shift()
k_lines['ADX_buy_signal'] = (k_lines['ADX'] > 25) & (k_lines['ADX'].shift() <= 25)
k_lines['ADX_sell_signal'] = (k_lines['ADX'] < 25) & (k_lines['ADX'].shift() >= 25)

# Visualization of closing prices and indicators with signals
plt.figure(figsize=(14, 7))

plt.subplot(6, 1, 1)
plt.plot(k_lines['time'], k_lines['close'], label='Close Price')
plt.title('Close Price')

for i, (indicator, color) in enumerate(zip(['RSI', 'MACD', 'ATR', 'ADX', 'CCI'], ['purple', 'green', 'black', 'blue', 'red'])):
    plt.subplot(6, 1, i+2)
    plt.plot(k_lines['time'], k_lines[indicator], label=indicator, color=color)
    plt.scatter(k_lines.loc[k_lines[indicator+'_buy_signal'], 'time'], k_lines.loc[k_lines[indicator+'_buy_signal'], indicator], marker='^', color='green', label='Buy Signal')
    plt.scatter(k_lines.loc[k_lines[indicator+'_sell_signal'], 'time'], k_lines.loc[k_lines[indicator+'_sell_signal'], indicator], marker='v', color='red', label='Sell Signal')
    plt.title(indicator)
    plt.legend()

plt.tight_layout()
plt.show()
