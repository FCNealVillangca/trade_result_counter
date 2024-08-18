# Trading Result Counter

just a simple script to count win or losing trades from csv

## Getting Started

Must have to prepare a Dataframe with the following columns

- close - the closed price
- signal - value should be 1 for buy 0 for no entry and -1 for sell
- spread - the in points can put value of 0 if not needed

### Installing

```
pip install trading_result_counter
```

## Example
example data
```csv
,datetime,open,high,low,close,tick_volume,volume,spread
0,2024-05-01 00:00:00,1.06649,1.06724,1.06649,1.06714,214,0,21
1,2024-05-01 00:15:00,1.06714,1.06719,1.06669,1.06671,108,0,34
2,2024-05-01 00:30:00,1.06672,1.06684,1.06662,1.06666,163,0,26
3,2024-05-01 00:45:00,1.06665,1.06688,1.06665,1.06677,139,0,30
4,2024-05-01 01:00:00,1.06678,1.0669,1.06662,1.06671,154,0,21
5,2024-05-01 01:15:00,1.0667,1.06674,1.06664,1.06664,58,0,21
6,2024-05-01 01:30:00,1.06664,1.06689,1.06664,1.06684,117,0,10
7,2024-05-01 01:45:00,1.06678,1.0668,1.06658,1.06674,278,0,10
```

example code

```python
import pandas as pd
import pandas_ta as ta
import time
from trading_result_counter import TradeResultCounter

data = pd.read_csv('EUR_USD.csv')
data.set_index('datetime')
data = data.drop(data.columns[0], axis=1)

# Custom indicator strategy
def ma_ma_crossover(df, ma_1=20, ma_2=50):
    short_ma = ta.sma(df['close'], length=ma_1)
    short_ma = short_ma.drop(short_ma.head(ma_1-1).index)

    long_ma = ta.sma(df['close'], length=ma_2)
    long_ma = long_ma.drop(long_ma.head(ma_2-1).index)

    df['signal'] = 0

    for x in range(len(long_ma)-2):
        current_short_ma = short_ma.iloc[x]
        current_long_ma = long_ma.iloc[x]
        previous_short_ma = short_ma.iloc[x + 1]
        previous_long_ma = long_ma.iloc[x + 1]

        if current_short_ma > current_long_ma and previous_short_ma < previous_long_ma:
            df.loc[x, "signal"] = 1

        if current_short_ma < current_long_ma and previous_short_ma > previous_long_ma:
            df.loc[x, "signal"] = -1

    return df

backtrading = TradeResultCounter(df=data).run(tp=400, sl=200, point_size=0.00001)

print(backtrading)
```
