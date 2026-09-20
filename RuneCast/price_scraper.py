import os
import time
import pandas as pd
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

from constants import get_items_by_depth

BASE_URL = "https://api.weirdgloop.org/exchange/history/rs/all?name="
DATA_DIR = "data/ge_prices"
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "RuneCastBot/1.0 (https://github.com/raefr-io/runecast)"
}

def get_price_history(item_name):
    url = BASE_URL + quote(item_name.replace(" ", "_"))
    print(f"Fetching: {url}")
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print(f"Failed to fetch {item_name}: HTTP {r.status_code}")
        return None

    try:
        data = r.json()
        # The key is the exact item name (case sensitive)
        key = None
        for k in data.keys():
            # Sometimes keys might differ slightly in spacing/capitalization
            if k.lower() == item_name.lower():
                key = k
                break

        records = data[key]
        if not records:
            print(f"No records found for {item_name}")
            return None
        df = pd.DataFrame(records)


        # timestamps are in milliseconds, convert to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d")


        df = df.rename(columns={"price": "price", "timestamp": "date"})
        df = df[["date", "price"]]
        return df

    except Exception as e:
        print(f"Error fetching price table for {item_name}: {e}")
        return None

def save_item_price_history(item_name):
    df = get_price_history(item_name)
    if df is not None:
        filename = os.path.join(DATA_DIR, f"{item_name.replace(' ', '_').lower()}.csv")
        df.to_csv(filename, index=False)
        print(f"Saved: {filename}")
    else:
        print(f"Skipped: {item_name}")

def batch_fetch(items, delay=5):
    seen = set()
    # Check if item.csv already exists, and if not, fetch it
    
    for item in items:
        filename = os.path.join(DATA_DIR, f"{item.replace(' ', '_').lower()}.csv")
        if not os.path.exists(filename):
            save_item_price_history(item)
            seen.add(item)
            time.sleep(delay)



def main(depth=5):
    items = get_items_by_depth(depth)
    batch_fetch(items)
    return items


if __name__ == "__main__":
    main()