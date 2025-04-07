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
def fetch_depth(coin_id, exchange_id):
    url = f"{COINGECKO_URL}coins/{coin_id}/tickers?exchange_ids={exchange_id}&depth=true&x_cg_pro_api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tickers = response.json().get("tickers", [])

        for ticker in tickers:
            if ticker.get("target") == "USDT" and ticker.get("market", {}).get("identifier") == exchange_id:
                return {
                    "pair": f"{ticker.get('base')}/{ticker.get('target')}",
                    "price": ticker.get("last"),
                    "spread": ticker.get("bid_ask_spread_percentage"),
                    "+2% depth": ticker.get("cost_to_move_up_usd"),
                    "-2% depth": ticker.get("cost_to_move_down_usd"),
                    "volume_24h": ticker.get("converted_volume", {}).get("usd")
                }
        return None
    except Exception as e:
        print(f"Error fetching USDT pair data for {coin_id} on {exchange_id}: {e}")
        return None

# Main script
def main():
    input_file = "CoinGeckoTop500.csv"  # Your input file with "Coin ID" column
    coin_list = load_coin_list(input_file)
    if not coin_list:
        print("No coin IDs found.")
        return

    results = []

    for coin_id in coin_list:
        print(f"Fetching: {coin_id}")

        market_cap, fdv, volume24h, token_name, token_symbol = get_current_market_data(coin_id)
        category = get_coin_categories(coin_id)

        for exchange in EXCHANGES:
            exchange_name = exchange["name"]
            exchange_id = exchange["id"]
            depth_data = fetch_depth(coin_id, exchange_id)

            if depth_data:
                results.append({
                    "Exchange": exchange_name,
                    "Category": category,
                    "Token CEX": coin_id,
                    "Token Name": token_name,
                    "Ticker": token_symbol,
                    "Market Cap Today": market_cap,
                    "FDV Today": fdv,
                    "Pair": depth_data.get("pair"),
                    "Price": depth_data.get("price"),
                    "Depth +2%": depth_data.get("+2% depth"),
                    "Depth -2%": depth_data.get("-2% depth"),
                    "Bid Ask Spread Percentage": round(depth_data.get("spread", 0), 2) if depth_data.get("spread") else "N/A",
                    "24H Volume (USD) on USDT": depth_data.get("volume_24h")
                })

    df_output = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Top500MultiExchange_USDT_{timestamp}.csv"
    df_output.to_csv(output_filename, index=False, encoding="utf-8")
    print(f"Done. Results saved to {output_filename}")

if __name__ == "__main__":
    main()
