import requests
import pandas as pd
from datetime import datetime

# CoinGecko Pro API key
API_KEY = "CG-MfMJsvzUhR8PtJfvvSRi1UEm"
COINGECKO_URL = "https://pro-api.coingecko.com/api/v3/"

# Target exchanges
EXCHANGES = [
    {"name": "Binance", "id": "binance"},
    {"name": "Bitget", "id": "bitget"},
    {"name": "Bybit", "id": "bybit_spot"},
    {"name": "Gate.io", "id": "gate"},
    {"name": "KuCoin", "id": "kucoin"},
    {"name": "MEXC", "id": "mxc"},
    {"name": "OKX", "id": "okx"},
]

# Load coin list
def load_coin_list(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, usecols=["Coin ID"])
        else:
            print("Invalid file format. Use CSV.")
            return []
        return df.iloc[:, 0].dropna().tolist()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# Fetch general market data
def get_current_market_data(coin_id):
    url = f"{COINGECKO_URL}coins/{coin_id}?x_cg_pro_api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        market_cap = data.get("market_data", {}).get("market_cap", {}).get("usd", None)
        fdv = data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd", None)
        volume24h = data.get("market_data", {}).get("total_volume", {}).get("usd", None)
        token_name = data.get("name", None)
        token_symbol = data.get("symbol", "").upper()
        return market_cap, fdv, volume24h, token_name, token_symbol
    except Exception as e:
        print(f"Error fetching market data for {coin_id}: {e}")
        return None, None, None, None, None

# Fetch coin category
def get_coin_categories(coin_id):
    url = f"{COINGECKO_URL}coins/{coin_id}?x_cg_pro_api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return ', '.join(data.get("categories", []))
    except Exception as e:
        print(f"Error fetching categories for {coin_id}: {e}")
        return "Unknown"

# Fetch depth data from a given exchange (default: USDT pair)
def fetch_depth(coin_id, exchange_id, target_pair="USDT"):
    url = f"{COINGECKO_URL}coins/{coin_id}/tickers?exchange_ids={exchange_id}&depth=true&x_cg_pro_api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tickers = response.json().get("tickers", [])
        
        for ticker in tickers:
            if ticker.get("target") == target_pair and ticker.get("market", {}).get("identifier") == exchange_id:
                bid_ask_spread = ticker.get("bid_ask_spread_percentage", None)
                depth_plus_2 = ticker.get("cost_to_move_up_usd", None)
                depth_minus_2 = ticker.get("cost_to_move_down_usd", None)
                return bid_ask_spread, depth_plus_2, depth_minus_2

        return None, None, None
    except Exception as e:
        print(f"Error fetching depth for {coin_id} on {exchange_id}: {e}")
        return None, None, None

# Main script
def main():
    input_file = "CoinGeckoTop5000.csv"  # Your input file with "Coin ID" column
    coin_list = load_coin_list(input_file)
    if not coin_list:
        print("No coin IDs found.")
        return

    results = []

    for coin_id in coin_list:
        print(f"📦 Fetching: {coin_id}")

        # General token data
        market_cap, fdv, volume24h, token_name, token_symbol = get_current_market_data(coin_id)
        category = get_coin_categories(coin_id)

        for exchange in EXCHANGES:
            exchange_name = exchange["name"]
            exchange_id = exchange["id"]
            bid_ask_spread, depth_plus_2, depth_minus_2 = fetch_depth(coin_id, exchange_id)

            results.append({
                "Exchange": exchange_name,
                "Category": category,
                "Token CEX": coin_id,
                "Token Name": token_name,
                "Ticker": token_symbol,
                "Market Cap Today": market_cap,
                "FDV Today": fdv,
                "Depth +2%": depth_plus_2,
                "Depth -2%": depth_minus_2,
                "Bid Ask Spread Percentage": round(bid_ask_spread, 2) if bid_ask_spread else "N/A",
                "24H Volume (USD)": volume24h
            })

    df_output = pd.DataFrame(results)
    output_filename = "Top500_MultiExchange_Depth.csv"
    df_output.to_csv(output_filename, index=False, encoding="utf-8")
    print(f"✅ Done. Results saved to {output_filename}")

if __name__ == "__main__":
    main()
