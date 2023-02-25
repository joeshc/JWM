import os
from kiteconnect import KiteConnect
import time, json,  datetime, sys
import pandas as pd

try:
    # Broker Details
    api_key = ""
    access_token = ""
    
    # Strategy parameters
    trade_symbol = "NIFTY"         # NIFTY or BANKNIFTY

    upper_range = 170
    lower_range = 150
    selection_time = datetime.time(12, 44)

    buy_level = 185
    sl_level = 155
    target_level = 215
    square_off_time = datetime.time(15, 15)

    qty_to_trade = 50
except:
    print("Wrong Input !!!!")
    sys.exit()


def get_login():
    global kite, api_key, access_token
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        kite.margins()
    except Exception as e:
        print(f"Error : {e}")
        time.sleep(5)
        sys.exit()


def get_strike(symbol_name):
    global lot_size
    while True:
        try:
            df = pd.DataFrame(kite.instruments())
            df = df[df["name"] == symbol_name]
            df = df[df["segment"] == "NFO-OPT"]
            df = df[df["expiry"] == sorted(list(df["expiry"].unique()))[0]]
            lot_size = float(list(df["lot_size"])[0])
            break
        except Exception as e:
            pass
    return [f"NFO:{i}" for i in list(df["tradingsymbol"])]


def place_trade(symbol, quantity, direction):
    try:
        print(f"{direction} Order : {symbol}, Qty : {quantity}")
        order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                 exchange=symbol[0:3],
                                 tradingsymbol=symbol[4:],
                                 transaction_type=kite.TRANSACTION_TYPE_BUY if direction == "BUY" else kite.TRANSACTION_TYPE_SELL,
                                 quantity=int(quantity),
                                 product=kite.PRODUCT_MIS,
                                 order_type=kite.ORDER_TYPE_MARKET,
                                 price=0.0,
                                 validity=kite.VALIDITY_DAY,
                                 tag="TradeViaPython")
        return order
    except Exception as e:
        return f"{e}"


def strategy():
    global ltp, strike_ltp
    print("-------Algo Started-------")
    if datetime.datetime.now().time() > datetime.time(9, 16):
        print("Pls start Algo Before 9:15!!!!")
        time.sleep(5)
        sys.exit()
    while datetime.datetime.now().time() <= datetime.time(9, 16):
        time.sleep(1)

    strikes = get_strike(trade_symbol.upper())
    while selection_time > datetime.datetime.now().time():
        try:
            strike_ltp = {k: v["last_price"] for k, v in kite.ltp(strikes).items()}
        except:
            time.sleep(1)

    selected_strikes = []
    for i in strike_ltp.keys():
        if upper_range >= strike_ltp[i] >= lower_range:
            print("Selected : ", i, ", LTP : ", strike_ltp[i])
            selected_strikes.append(i)

    traded = None
    while selected_strikes:
        time.sleep(1)
        while True:
            try:
                strike_ltp = {k: v["last_price"] for k, v in kite.ltp(strikes).items()}
                break
            except:
                time.sleep(1)
        if traded is None and square_off_time > datetime.datetime.now().time():
            for i in selected_strikes:
                if strike_ltp[i] >= buy_level and traded is None:
                    traded = i
                    place_trade(traded, qty_to_trade, "BUY")
        if traded is not None:
            if strike_ltp[traded] >= target_level or strike_ltp[traded] <= sl_level or datetime.datetime.now().time() >= square_off_time:
                place_trade(traded, qty_to_trade, "SELL")
                print("Trading Done.")
                break
    else:
        print("No strike in your price range...")
    print("-----Algo Stopped-----")


# Developed by "TradeViaPython"
if __name__ == '__main__':
    get_login()
    strategy()
