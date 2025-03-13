import requests
import pandas as pd
from datetime import datetime

# Replace with your CoinGecko API Key
API_KEY = "CG-MfMJsvzUhR8PtJfvvSRi1UEm"

# CoinGecko API Base URL
COINGECKO_URL = "https://pro-api.coingecko.com/api/v3/"

# Exchange Details
EXCHANGE_NAME = "Binance"
EXCHANGE_ID = "binance"

# Function to fetch market data (Market Cap, FDV, Volume)
def get_current_market_data(coin_id):
    url = f"{COINGECKO_URL}coins/{coin_id}?x_cg_pro_api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        market_cap = data.get("market_data", {}).get("market_cap", {}).get("usd", None)
        fdv = data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd", None)
        volume24h = data.get("market_data", {}).get("total_volume", {}).get("usd", None)
        return market_cap, fdv, volume24h
    except Exception as e:
        print(f"Error fetching market data for {coin_id}: {e}")
        return None, None, None
        
# Function to fetch Order Book Depth (±2%) from Binance
def fetch_depth(coin_id):
    url = f"{COINGECKO_URL}coins/{coin_id}/tickers?exchange_ids={EXCHANGE_ID}&depth=true&x_cg_pro_api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        tickers = data.get("tickers", {})

        if tickers:
            ticker = tickers[0]
            bid_ask_spread = ticker.get("bid_ask_spread_percentage", None)
            depth_plus_2 = ticker.get("cost_to_move_up_usd", None)
            depth_minus_2 = ticker.get("cost_to_move_down_usd", None)
            return bid_ask_spread, depth_plus_2, depth_minus_2
        return None, None, None
    except Exception as e:
        print(f"Error fetching depth data for {coin_id}: {e}")
        return None, None, None

# Function to fetch categories of a coin
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

# Function to load coin list from column A of an Excel/CSV file
def load_coin_list(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, usecols=["Coin ID"])  # Extract column A
        else:
            print("Invalid file format. Use CSV or Excel.")
            return []
        
        return df.iloc[:, 0].dropna().tolist()  # Convert column C to list
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# Main function to fetch & save data
def main():
    input_file = "CoinGeckoTop500.csv"  # Change this to your input file name

    # Load coin list from column C
    coin_list = load_coin_list(input_file)

    if not coin_list:
        print("No coin IDs found in column.")
        return

    results = []

    for coin_id in coin_list:
        print(f"Fetching data for: {coin_id}")

        # Get Market Cap, FDV, and 24H Volume
        market_cap_today, fdv_today, volume24h = get_current_market_data(coin_id)

        # Get Order Book Depth & Spread
        bid_ask_spread, depth_plus_2, depth_minus_2 = fetch_depth(coin_id)

        # Get Coin Category
        category = get_coin_categories(coin_id)

        # Store data
        results.append({
            "Exchange": EXCHANGE_NAME,
            "Category": category,
            "Token CEX": coin_id,
            "Market Cap Today": market_cap_today,
            "FDV Today": fdv_today,
            "Depth +2%": depth_plus_2,
            "Depth -2%": depth_minus_2, 
            "Bid Ask Spread Percentage": round(bid_ask_spread, 2) if bid_ask_spread else "N/A",
            "24H Volume (USD)": volume24h
        })

    
    # Convert results to DataFrame
    df_output = pd.DataFrame(results)

    # Save to CSV
    csv_filename = "CoinGeckoTop500.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"✅ Data saved to {csv_filename}")

if __name__ == "__main__":
    main()

