

import pandas as pd
import datetime as dt
from binance import Client

def rsi(previous_average_gain, previous_average_loss, current_gain, current_loss):
    average_gain = (previous_average_gain * 13 + current_gain) / 14
    average_loss = (previous_average_loss * 13 + current_loss) / 14
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi_first(prices, N):
    changes = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [x for x in changes if x > 0]
    losses = [-x for x in changes if x < 0]
    average_gain = sum(gains[-N:]) / N
    average_loss = sum(losses[-N:]) / N
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi_day(asset, periods):
    k_lines = Client().get_historical_klines(
        symbol=asset,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str="1 day ago UTC",
        end_str="now UTC"
    )
    k_lines = pd.DataFrame(k_lines)[[0, 4]]
    k_lines[0] = pd.to_datetime(k_lines[0], unit='ms')
    k_lines[4] = k_lines[4].astype(float)
    k_lines = k_lines.rename(columns={0: 'time', 4: 'close'})
    result = pd.DataFrame()
    result['time'] = k_lines['time']
    for period in periods:
        rsi_values = []
        rsi_values.append(rsi_first(k_lines['close'], period))
        for i in range(1, len(k_lines)):
            current_change = k_lines['close'][i] - k_lines['close'][i-1]
            if current_change > 0:
                current_gain = current_change
                current_loss = 0
            else:
                current_gain = 0
                current_loss = -current_change
            rsi_value = rsi(rsi_values[-1], rsi_values[-1], current_gain, current_loss)
            rsi_values.append(rsi_value)
        result[f'RSI {period}'] = rsi_values
    return result


try:
    df = pd.read_csv('filename.csv')
except FileNotFoundError:
    df = pd.DataFrame(columns = ['index', 'time', 'rsi_14', 'rsi_25', 'rsi_100'])

asset = "BTCUSDT"
periods = [14, 27, 100]
rsi_day(asset, periods)
print(rsi_day(asset, periods))


qwe = rsi_day(asset, periods)

for index, row in qwe.iterrows():
    df.loc[len(df)] = [index, row['time'], 
                       row[f'RSI {periods[0]}'], 
                       row[f'RSI {periods[1]}'], 
                       row[f'RSI {periods[2]}']]


df.to_csv("filename.csv", index=False)
