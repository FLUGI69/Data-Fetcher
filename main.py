import yfinance as yf
import pandas as pd
import numpy as np
import logging
from period_date import Date
import matplotlib.pyplot as plt

class DataFrame:
    def __init__(self,
                df: pd.DataFrame, 
                date: Date,
                ) -> None:
        
        self.df = df.copy()

        self.start = date.start

        self.end = date.end

        self.ticker = date.ticker

        self.interval = date.interval

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

        self.chart_shown = False
    
    def set_dataframe(self):

        data = yf.Ticker(self.ticker).history(start=self.start, end=self.end, interval=self.interval)

        self.df = pd.DataFrame(data)
        self.df.reset_index(inplace=True)
        self.df["Date"] = pd.to_datetime(self.df["Date"], unit="s")

        # self.logger.info(f'Data fetched for {self.df}')

        return self.df
    
    def set_candle_type(self):
        
        self.df["candle_type"] = ["bullish" if self.df.loc[i, "Open"] < self.df.loc[i, "Close"] else "bearish" for i in self.df.index]

    def iterate_dataframe(self):

        self.df["three_month_period"] = (self.df["Date"].dt.month - 1) // 3 + 1
        self.df["three_month_period"] = self.df["Date"].dt.year.astype(str) + '.' + self.df["three_month_period"].astype(str)

        for period, group in self.df.groupby("three_month_period"):

            self.logger.info(f"Three-month period: {period}")

            start_date = group["Date"].min()
            end_date = group["Date"].max()
            start_date_open = group.loc[group["Date"] == start_date, "Open"].values[0]
            end_date_close = group.loc[group["Date"] == end_date, "Close"].values[0]
            percentage_change = ((end_date_close - start_date_open) / start_date_open) * 100

            self.df.loc[group.index, "Start_Date"] = start_date
            self.df.loc[group.index, "End_Date"] = end_date

            self.df.loc[group.index[-1], "percentage_change"] = percentage_change
            self.df.loc[group.index[:-1], "percentage_change"] = np.nan
            
            self.logger.info(f"Period start date: {start_date}, Period end date: {end_date}")
            self.logger.info(f"Start Date Open: {start_date_open}, End Date Close: {end_date_close}")
            self.logger.info(f"Percentage Change: {percentage_change:.2f}%")

    def show_on_hist(self):

        negative_changes = self.df[self.df["percentage_change"] < 0]
        
        sizes = negative_changes["percentage_change"].abs()
        
        labels = []
        for index, row in negative_changes.iterrows():
            if pd.notna(row["Date"]) and pd.notna(row["End_Date"]) and pd.notna(row["percentage_change"]):
                label = f"{row["Date"]} - {row["End_Date"]} ({row["percentage_change"]:.1f}%)"
                labels.append(label)
            else:
                labels.append("N/A")
            
        plt.figure(figsize=(8, 8))
        
        wedges, _ = plt.pie(sizes, labels=labels, startangle=140, wedgeprops={"edgecolor": "black"})
        
        plt.title(f"Pie chart divided into 3-month periods showing negative percentage changes: {self.ticker}")
        
        plt.axis("equal")
        
        for wedge, label in zip(wedges, labels):
            ang = (wedge.theta2 - wedge.theta1)/2. + wedge.theta1
            y = wedge.r * 1.1 * 0.5 * plt.rcParams["font.size"]
            plt.text(wedge.r * 1.1 * 0.5 * plt.rcParams["font.size"] * 1.1 * plt.rcParams["font.size"],
                    y,
                    label,
                    horizontalalignment="center",
                    verticalalignment="center",
                    rotation=ang,
                    fontsize=10,
                    color="black"
                    )
        
        plt.tight_layout()
        plt.show()
        
        self.chart_shown = True

    def log_data_head(self):

        if self.df is not None:

            self.logger.info(f"Start Date\n{self.df.head(30)}")
            self.logger.info(f"End Date\n{self.df.tail(10)}")   

        else:

            self.logger.warning("No data to log. Fetch the data first.")

if __name__ == "__main__":

    ticker = "SNAP" # You can change it to another stock's data.
    start_date = "2014-1-1"
    end_date = "2021-1-1"
    interval = "1wk"

    date = Date(ticker=ticker, start=start_date, end=end_date, interval=interval)
    df = pd.DataFrame()
    set_df = DataFrame(df, date)
    set_df.set_dataframe()
    set_df.set_candle_type()
    set_df.iterate_dataframe()
    set_df.log_data_head()
    set_df.show_on_hist()
