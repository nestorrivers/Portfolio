import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path

import joblib

from constants import get_items_by_depth

def load_data_by_depth(depth, base_path="data/ge_prices"):
    items = get_items_by_depth(depth)

    # Load and merge all items' CSVs
    dfs = []
    for item in items:
        filename = item.lower().replace(" ", "_") + ".csv"
        filepath = Path(base_path) / filename
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file for '{item}' not found at {filepath}")

        df = pd.read_csv(filepath, parse_dates=["date"])
        df = df[["date", "price"]].rename(columns={"price": item}).set_index("date")
        dfs.append(df)

    combined_df = pd.concat(dfs, axis=1).sort_index().dropna()

    return combined_df


def load_item_data(depth, target_item, base_path="data/ge_prices", seq_len=30):
    data = load_data_by_depth(depth, base_path=base_path)

    if target_item not in data.columns:
        raise ValueError(f"Target item '{target_item}' not found in loaded data columns.")

    scaler = StandardScaler()
    data_scaled = pd.DataFrame(scaler.fit_transform(data), columns=data.columns, index=data.index)
    
    save_scaler(scaler, depth, target_item)

    X, y, timestamps = create_sequences(data_scaled, seq_len=seq_len, target_col=target_item)

    print("Features:", list(data.columns))
    print("Example sequence shape:", X[0].shape)
    print("Example target value:", y[0])

    return np.array(X), np.array(y), scaler



def save_scaler(scaler, depth, target_item):
    filename = f'models/{target_item.replace(" ", "_")}/depth{depth}_scaler.pkl'
    dirpath = Path(filename).parent
    dirpath.mkdir(parents=True, exist_ok=True)

    joblib.dump(scaler, filename)
    print(f"Scaler saved to {filename}")


def create_sequences(data: pd.DataFrame, seq_len: int = 30, target_col: str = None):
    """
    Create sequences for multivariate time series data from a pandas DataFrame.

    Args:
        data (pd.DataFrame): DataFrame with time as index and features as columns.
        seq_len (int): Length of each input sequence.
        target_col (str): Name of the column to use as prediction target.

    Returns:
        X: (samples, seq_len, features) numpy array
        y: (samples, 1) numpy array
        timestamps: list of timestamps corresponding to each sample's target
    """
    if target_col is None:
        target_col = data.columns[0]  # default to first column if not specified

    X, y, timestamps = [], [], []

    for i in range(len(data) - seq_len):
        seq_x = data.iloc[i:i+seq_len].values  # shape: (seq_len, features)
        target_y = data.iloc[i + seq_len][target_col]  # scalar target value
        timestamp = data.index[i + seq_len]

        X.append(seq_x)
        y.append(target_y)
        timestamps.append(timestamp)

    return np.array(X), np.array(y).reshape(-1, 1), timestamps




if __name__ == "__main__":
    depth = 3  # example depth to include core + intermediate + precursor
    target_item = "Glorious bar"  # your target to predict

    X, y, scaler = load_item_data(depth, target_item)
