import requests
import pandas as pd

# Your CoinGecko API Key (replace with your actual key)
API_KEY = "CG-MfMJsvzUhR8PtJfvvSRi1UEm"

# CoinGecko API endpoint
URL = "https://pro-api.coingecko.com/api/v3/coins/markets"

# API request parameters
params = {
    "vs_currency": "usd",  
    "order": "market_cap_desc",  
    "per_page": 250,  
    "page": 1,  
    "sparkline": "false",  
    "locale": "en"
}

# Headers for authentication
HEADERS = {"x-cg-pro-api-key": API_KEY}

# List to store filtered coins
filtered_coins = []
page = 1  # Start from page 1

# Fetch until we have at least 500 coins with market cap < $1B
while len(filtered_coins) < 500:
    params["page"] = page
    response = requests.get(URL, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Filter coins with market cap < 1B
        coins_below_1b = [coin for coin in data if coin.get("market_cap") and coin["market_cap"] < 1_000_000_000]
        
        # Add to the list
        filtered_coins.extend(coins_below_1b)
        
        # Stop if no more data is available
        if not data:
            break  
    else:
        print(f"Error: {response.status_code}, {response.text}")
        break  

    page += 1  # Go to next page

# Keep only the top 500 from the filtered list
filtered_coins = filtered_coins[:500]

# Convert to a Pandas DataFrame
df = pd.DataFrame(filtered_coins)

# Select and rename columns
df = df[["id", "symbol", "name", "market_cap", "fully_diluted_valuation", 
         "total_volume"]]

df.rename(columns={
    "id": "Coin ID",
    "symbol": "Symbol",
    "name": "Name",
    "market_cap": "Market Cap (USD)",
    "fully_diluted_valuation": "FDV (USD)",
    "total_volume": "24H Volume (USD)",
}, inplace=True)

# Save to csv
excel_filename = "CoinGeckoTop500.csv"
df.to_excel(excel_filename, index=False, engine="csv")
print(f"✅ Data saved to {excel_filename}")

# Print top 10 rows
print(df.head(10))
