import re
import torch
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import requests
from bs4 import BeautifulSoup

from train import PriceLSTM
from constants import get_items_by_depth

def fetch_price_from_wiki(item_name):
    url = f"https://runescape.wiki/w/Exchange:{item_name.replace(' ', '_')}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch data for {item_name}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    price_elem = soup.find(id="GEPrice")
    if price_elem:
        try:
            return float(price_elem.text.strip().replace(",", "").replace("coins", ""))
        except:
            return None
    return None

def fetch_price_history(item_name, seq_len=30):
    """Fetch the last seq_len days of price history from the weirdgloop API."""
    url = f"https://api.weirdgloop.org/exchange/history/rs/all?name={item_name.replace(' ', '_')}"
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "RuneCastBot/1.0"})
        resp.raise_for_status()
        data = resp.json()
        key = next((k for k in data if k.lower() == item_name.lower()), None)
        if key is None:
            return None
        records = data[key]
        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.sort_values("timestamp").tail(seq_len)
        if len(df) < seq_len:
            print(f"Warning: only {len(df)} days of history for {item_name}, expected {seq_len}")
            return None
        return df["price"].astype(float).tolist()
    except Exception as e:
        print(f"Failed to fetch history for {item_name}: {e}")
        return None


def prepare_input_sequence(items, scaler, seq_len=30):
    """
    Build the input tensor for inference using real historical price sequences.
    Fetches the last seq_len days of price history for each item and assembles
    a (1, seq_len, n_features) tensor, matching what the model was trained on.
    """
    histories = {}
    for item in items:
        history = fetch_price_history(item, seq_len=seq_len)
        if history is None:
            raise ValueError(f"Could not retrieve {seq_len} days of history for '{item}'")
        histories[item] = history

    # Shape: (seq_len, n_features)
    seq = np.array([[histories[item][t] for item in items] for t in range(seq_len)])
    seq_scaled = scaler.transform(seq)
    return torch.tensor(seq_scaled, dtype=torch.float32).unsqueeze(0)

def load_scaler_and_model(model_path, input_size=None):
    scaler_path = model_path.with_name(model_path.name.replace("_model.pt", "_scaler.pkl"))
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
    scaler = joblib.load(scaler_path)

    checkpoint = torch.load(model_path, map_location="cpu")
    if "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

    # Extract config from checkpoint or fallback
    hidden_size = checkpoint.get("hidden_size", 108)
    num_layers = checkpoint.get("num_layers", 2)
    dropout = checkpoint.get("dropout", 0.1)
    # Use checkpoint input_size if present, else fallback to passed value
    input_size = checkpoint.get("input_size", input_size)

    if input_size is None:
        raise ValueError("Input size must be specified either by checkpoint or function argument.")

    model = PriceLSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, dropout=dropout)
    model.load_state_dict(state_dict)
    model.eval()
    return model, scaler



def list_available_models(models_root):
    models = []
    for item_folder in sorted(models_root.iterdir()):
        if item_folder.is_dir():
            for model_file in sorted(item_folder.glob("depth*_model.pt")):
                match = re.match(r"depth(\d+)_model\.pt", model_file.name)
                if match:
                    depth = int(match.group(1))
                    models.append((item_folder.name, depth, model_file))
    return models

def select_model(models):
    print("Available models:")
    for i, (item, depth, _) in enumerate(models):
        print(f"{i+1}: Item = {item}, Depth = {depth}")
    idx = int(input("Select a model by number: ")) - 1
    if idx < 0 or idx >= len(models):
        raise ValueError("Invalid selection.")
    return models[idx]

def main():
    models_root = Path("models")
    if not models_root.exists():
        print(f"Models folder '{models_root}' does not exist!")
        return

    available_models = list_available_models(models_root)
    if not available_models:
        print("No models found.")
        return

    item_name, depth, model_path = select_model(available_models)
    target_item = item_name.replace("_", " ")  # adapt if your folders have underscores
    items = get_items_by_depth(depth)

    print(f"\nModel info — Item: {target_item}, Depth: {depth}")
    print(f"Using {len(items)} input items: {items}")

    print("\nFetching price histories...")
    model, scaler = load_scaler_and_model(model_path, input_size=len(items))

    try:
        input_seq = prepare_input_sequence(items, scaler)
    except ValueError as e:
        print(e)
        return

    # Current price is today's spot — fetch separately for display
    current_price = fetch_price_from_wiki(target_item)
    if current_price is None:
        print(f"Could not fetch current price for '{target_item}'.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    input_seq = input_seq.to(device)

    with torch.no_grad():
        prediction_scaled = model(input_seq).cpu().numpy().flatten()[0]

    dummy_input = np.zeros((1, len(items)))
    try:
        target_idx = items.index(target_item)
    except ValueError:
        print(f"Target item '{target_item}' not in input items list.")
        return

    dummy_input[0, target_idx] = prediction_scaled
    pred_unscaled = scaler.inverse_transform(dummy_input)[0, target_idx]

    threshold = 0.01 * current_price
    direction = (
        "up" if pred_unscaled > current_price + threshold else
        "down" if pred_unscaled < current_price - threshold else
        "stable"
    )

    print(f"\nPrediction for '{target_item}': {pred_unscaled:.2f}")
    print(f"Current price: {current_price:.2f}")
    print(f"Expected direction: {direction}")
    print(f"Difference: {pred_unscaled - current_price:.2f} ({((pred_unscaled - current_price) / current_price) * 100:.2f}%)")
    

if __name__ == "__main__":
    main()
