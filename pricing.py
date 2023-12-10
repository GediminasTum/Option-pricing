from datetime import date, timedelta
import datetime as dt
import yfinance as yf
import pandas as pd
import numpy as np
import math
from scipy.stats import norm
import tkinter as tk
from tkinter import messagebox, simpledialog


#Getting variables
while True:
    try:
        ticker = simpledialog.askstring("Input", 'Enter the ticker of the underlying asset: ')
        price = pd.DataFrame(yf.Ticker(ticker).history(period="1d"))
        if price.empty:
            messagebox.showerror("Error", "No data found for this ticker. Please try again.")
        else:
            break
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

strike_price = float(simpledialog.askstring("Input",'Enter the strike price of the underlying asset: '))

while True:
    try:
        maturity_date = simpledialog.askstring("Input",'Enter the maturity date of the underlying asset (YYYY-MM-DD): ')
        end_date = dt.datetime.strptime(maturity_date, "%Y-%m-%d").date()
        break
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please enter tha date in the format of YYYY-MM-DD")


while True:
    try:
        option_type = simpledialog.askstring("Input",'Enter option type (call/ put): ')
        if option_type != 'call' and option_type != 'put':
            messagebox.showerror("Error", "Please enter correct option type: ")
        else:
            break
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")


#Checking country of the instrument
obj = yf.Ticker(ticker)
info = obj.info
print(info['country'])

#Get time to maturity
start_date = date.today()
time_to_maturity = (end_date - start_date).days/365.25
print(f"time to maturity: {time_to_maturity}")


#Get current price
current_price = price.iloc[0]['Close']
print(current_price)
                
# Check if today is a weekend
today = date.today()
if today.weekday() == 5:  # Saturday
    yesterday = today - timedelta(days=1)
elif today.weekday() == 6:  # Sunday
    yesterday = today - timedelta(days=2)
else:
    yesterday = today

#Get risk free rate
if info['country'] == 'United States':
    try:
        USyield = pd.DataFrame(yf.Ticker("^TNX").history(start=yesterday, end=today))
        if not USyield.empty:
            risk_free_rate = USyield.iloc[-1]['Close'] / 100
        else:
            print("Error: Risk-free rate data not available for symbol ^TNX. Please check the symbol.")
        risk_free_rate = 0 
    except IndexError:
        print("Error: Risk-free rate data not available for symbol ^TNX. Please check the symbol.")
    risk_free_rate = 0 


#Get volatility
start_date_adjusted = start_date-timedelta(days=int(time_to_maturity*365.25))
data = yf.download([ticker], start=start_date_adjusted, end=start_date)
data['Daily_Return'] = data['Adj Close'].pct_change()
volatility = np.std(data['Daily_Return'])


# Black Schols function
def black_schols_method(current_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type):
    d1 = (math.log(current_price / strike_price) + (risk_free_rate + (math.pow(volatility, 2) / 2)) * time_to_maturity) / (volatility * math.sqrt(time_to_maturity))
    d2 = d1 - volatility * math.sqrt(time_to_maturity)
    if option_type == "call":
        option_price = current_price * norm.cdf(d1) - strike_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
        return option_price
    else:
        option_price = strike_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) - current_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d1)
        return option_price

option_price = black_schols_method(current_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type)

root = tk.Tk()
root.withdraw()

messagebox.showinfo(
    "Option Price",  
    f"Underlying asset: {ticker}\n"
    f"Strike price: {strike_price}\n"
    f"Maturity date: {maturity_date}\n"
    f"Option type: {option_type}\n"
    f"The risk-free rate: {risk_free_rate}\n"
    f"Historical volatility: {volatility}\n"
    f"The calculated option price is: {option_price}"
    )

root.mainloop()

