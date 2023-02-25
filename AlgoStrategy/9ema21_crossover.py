import pandas as pd
from kiteconnect import KiteConnect

# Initialize the Kite Connect client
kite = KiteConnect(api_key="YOUR_API_KEY")

# Get request_token
data = kite.generate_session("YOUR_API_SECRET", "YOUR_REQUEST_TOKEN")

# Get the live tick data for the trading symbol
live_tick = kite.lt_ticks(["YOUR_TRADING_SYMBOL"])

# Convert the live tick data to a pandas DataFrame
df = pd.DataFrame(live_tick)

# Compute the 9 EMA
df['ema_9'] = df['last_price'].ewm(span=9).mean()

# Compute the 21 EMA
df['ema_21'] = df['last_price'].ewm(span=21).mean()

# Initialize the current position to be "neutral"
position = "neutral"

# Get the options chain for the trading symbol
options_chain = kite.options_chain("NSE", "YOUR_TRADING_SYMBOL")

# Get the current market price
market_price = df['last_price'][-1]

# Get the strikes for options
strikes = [x['strike'] for x in options_chain['CE'] + options_chain['PE']]

# Iterate over the live tick data
for i in range(len(df)):
    # If the 9 EMA crosses above the 21 EMA
    if df['ema_9'][i] > df['ema_21'][i] and df['ema_9'][i-1] <= df['ema_21'][i-1]:
        # If the current position is "neutral" or "short"
        if position in ["neutral", "short"]:
            # Place a buy order at the nearest strike price
            nearest_strike = min(strikes, key=lambda x: abs(x - market_price))
            kite.place_order(
                tradingsymbol="YOUR_TRADING_SYMBOL",
                exchange="YOUR_EXCHANGE",
                transaction_type="BUY",
                quantity=1,
                order_type="LIMIT",
                product="MIS",
                strike=nearest_strike,
                expiry="YOUR_EXPIRY_DATE",
                variety = "CE"
            )
            print("Buy order placed at strike price {}".format(nearest_strike))
            # Update the current position
            position = "long"
    # If the 9 EMA crosses below the 21 EMA
    elif df['ema_9'][i] < df['ema_21'][i] and df['ema_9'][i-1] >= df['ema_21'][i-1]:
        # If the current position is "long"
        if position == "long":
            # Place a sell order at the nearest strike price
            nearest_strike = min(strikes, key=lambda x: abs(x - market_price))
            
            kite.place_order(
                tradingsymbol="YOUR_TRADING_SYMBOL",
                exchange="YOUR_EXCHANGE",
                transaction_type="BUY",
                quantity=1,
                order_type="LIMIT",
                product="MIS",
                strike=nearest_strike,
                expiry="YOUR_EXPIRY_DATE",
                variety = "PE"
            )
            position = "short"