from setuptools import setup, find_packages

setup(
    name='v20-python-samples',
    version='0.1.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'import requests
import pandas as pd
import time

# Broker API information
API_URL = "https://api-fxpractice.oanda.com/v3"
TOKEN = "596e44118c40416fcf9f9a736cdb58d8-56a708e2bf4ecae7c783e125843f221a"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"  # Replace with your actual account ID
INSTRUMENT = "EUR_USD"  # Currency pair
UNITS = 1000  # Amount to buy/sell
STOP_LOSS_PIPS = 20  # Stop loss distance in pips
TAKE_PROFIT_PIPS = 50  # Take profit distance in pips
PIP_VALUE = 0.0001  # Pip value for most pairs like EUR/USD

# Headers for authorization with Bearer token
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def get_price_data(instrument, granularity="M5", count=100):
    """Fetch historical price data for given instrument and granularity."""
    endpoint = f"/instruments/{instrument}/candles"
    params = {
        "granularity": granularity,
        "count": count,
        "price": "M"
    }
    response = requests.get(API_URL + endpoint, headers=headers, params=params)
    data = response.json()
    return pd.DataFrame([{
        'time': candle['time'],
        'close': float(candle['mid']['c'])
    } for candle in data['candles']])

def calculate_sma(data, period):
    """Calculate Simple Moving Average (SMA) for the specified period."""
    return data['close'].rolling(window=period).mean()

def place_order(units, entry_price):
    """Place a market order with specified units, stop-loss, and take-profit."""
    stop_loss_price = entry_price - STOP_LOSS_PIPS * PIP_VALUE if units > 0 else entry_price + STOP_LOSS_PIPS * PIP_VALUE
    take_profit_price = entry_price + TAKE_PROFIT_PIPS * PIP_VALUE if units > 0 else entry_price - TAKE_PROFIT_PIPS * PIP_VALUE
    
    order_data = {
        "order": {
            "units": str(units),
            "instrument": INSTRUMENT,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {
                "price": str(round(stop_loss_price, 5))
            },
            "takeProfitOnFill": {
                "price": str(round(take_profit_price, 5))
            }
        }
    }

    endpoint = f"/accounts/{ACCOUNT_ID}/orders"
    response = requests.post(API_URL + endpoint, headers=headers, json=order_data)
    print("Order placed:", response.json())

def trading_bot():
    """Main function to run the trading bot."""
    print("Starting trading bot...")
    
    while True:
        # Fetch the latest data
        data = get_price_data(INSTRUMENT)
        
        # Calculate SMAs
        data['SMA_50'] = calculate_sma(data, 50)
        data['SMA_200'] = calculate_sma(data, 200)
        
        # Get the last row (most recent data)
        latest_data = data.iloc[-1]
        
        # Trading logic: SMA Crossover
        if latest_data['SMA_50'] > latest_data['SMA_200']:
            print("Buy signal detected.")
            entry_price = latest_data['close']
            place_order(UNITS, entry_price)  # Buy order with stop-loss and take-profit
        elif latest_data['SMA_50'] < latest_data['SMA_200']:
            print("Sell signal detected.")
            entry_price = latest_data['close']
            place_order(-UNITS, entry_price)  # Sell order with stop-loss and take-profit
        else:
            print("No clear signal.")
        
        # Wait before the next check
        time.sleep(300)  # Wait for 5 minutes

# Run the trading bot
if __name__ == "__main__":
    trading_bot()

