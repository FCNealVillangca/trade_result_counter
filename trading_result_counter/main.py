import pandas as pd
import types


class TradeResultCounter:
    def __init__(self, df):
        """
        A class to count and analyze trade results from a pandas DataFrame.

        Parameters:
        df (pandas.DataFrame): The input DataFrame containing trade data.

        Attributes:
        df (pandas.DataFrame): The input DataFrame containing trade data.
        spread (int): The spread value.
        tp (int): The take profit value.
        sl (int): The stop loss value.
        point_size (int): The point size value.
        entries (list): A list of trade entries.

        Methods:
        __init__(df): Initializes the TradeResultCounter object with the input DataFrame.
        check_dataframe(): Checks the input DataFrame for validity (not implemented).

        Notes:
        This class is used to count and analyze trade results from a pandas DataFrame.
        The `check_dataframe` method is not implemented and should be overridden by a subclass.
        """
        self.df = df
        self.spread = 0
        self.tp = 0
        self.sl = 0
        self.point_size = 0
        self.entries = []
        self.check_dataframe()

    def run(self, tp=400, sl=200, point_size=0):
        """
        Run the simulation with the given parameters.

        Parameters:
        tp (int, optional): Take profit value. Defaults to 400.
        sl (int, optional): Stop loss value. Defaults to 200.
        point_size (int, optional): Point size value. Defaults to 0.

        Returns:
        dict: A dictionary containing the simulation results, with the following keys:
            - "wins": The number of winning trades.
            - "lost": The number of losing trades.
            - "unfinished": The number of unfinished trades.
            - "all": A list of all trade entries.

        Notes:
        This method sets the instance variables tp, sl, and point_size, and then calls the loop_through method.
        """
        self.tp = tp
        self.sl = sl
        self.point_size = point_size
        self.loop_through()
        return {
            "wins": self.get_wins(),
            "lost": self.get_lost(),
            "unfinished": self.get_unfinished(),
            "all": self.entries
        }

    def get_long_tp(self, price, points):
        return price + (points * self.point_size)

    def get_long_sl(self, price,  points):
        return price - (points * self.point_size)

    def get_short_tp(self, price,  points):
        return price - (points * self.point_size)

    def get_short_sl(self, price,  points):
        return price + (points * self.point_size)

    def get_ask_bid(self, price, spread):
        return types.SimpleNamespace(
            ask=price + (spread * self.point_size),
            bid=price - (spread * self.point_size),
        )

    def get_wins(self):
        return list(filter(lambda obj: obj["status"] == 1, self.entries))

    def get_lost(self):
        return list(filter(lambda obj: obj["status"] == -1, self.entries))

    def get_unfinished(self):
        return list(filter(lambda obj: obj["status"] == 0, self.entries))

    def check_dataframe(self):
        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("The input is not a pandas DataFrame")
        required_columns = ['signal', 'close', 'datetime', "spread"]
        if not all(col in self.df.columns for col in required_columns):
            raise ValueError(
                "The CSV file is missing one or more of the required columns: signal, close, datetime")

    def exit_buy(self, pending, exit_price, datetime):
        for x in range(len(pending)):
            curr_trade = pending[x]
            if curr_trade['take_profit'] <= exit_price:
                curr_trade["status"] = 1
                curr_trade["time_close"] = datetime
            if curr_trade['stop_loss'] >= exit_price:
                curr_trade["status"] = -1
                curr_trade["time_close"] = datetime

    def exit_sell(self, pending, exit_price, datetime):
        for x in range(len(pending)):
            curr_trade = pending[x]
            if curr_trade['take_profit'] >= exit_price:
                curr_trade["status"] = 1
                curr_trade["time_close"] = datetime

            if curr_trade['stop_loss'] <= exit_price:
                curr_trade["status"] = -1
                curr_trade["time_close"] = datetime

    def loop_through(self):
        for x in range(len(self.df)):
            signal = self.df.iloc[x]['signal']
            price = self.df.iloc[x]['close']
            spread = self.df.iloc[x]['spread']
            time = self.df.iloc[x]['datetime']
            ask = price + (spread * self.point_size)
            bid = price - (spread * self.point_size)
            if signal == 1:
                self.entries.append({
                    "price": ask,
                    "type": 1,
                    "time_open": time,
                    "status": 0,
                    "take_profit": self.get_long_tp(price, self.tp),
                    "stop_loss": self.get_long_sl(price, self.sl),
                })
            if signal == -1:
                self.entries.append({
                    "price": bid,
                    "type": -1,
                    "status": 0,
                    "time_open": time,
                    "take_profit": self.get_short_tp(price, self.tp),
                    "stop_loss": self.get_short_sl(price, self.sl),
                })
            pending_buy = list(
                filter(lambda obj: obj["status"] ==
                       0 and obj["type"] == 1, self.entries))
            pending_sell = list(
                filter(lambda obj: obj["status"] ==
                       0 and obj["type"] == -1, self.entries))
            if len(pending_buy) > 0:
                self.exit_buy(pending_buy, bid, time)
            if len(pending_sell) > 0:
                self.exit_sell(pending_sell, ask, time)
