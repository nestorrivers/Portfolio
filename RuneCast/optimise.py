import optuna
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import numpy as np

from data_utils import load_item_data
from train import PriceLSTM, PriceDataset, train_model

def objective(trial, X, y):
    # Hyperparameters to tune
    hidden_size = trial.suggest_int("hidden_size", 16, 128)
    num_layers = trial.suggest_int("num_layers", 1, 3)
    dropout = trial.suggest_float("dropout", 0.0, 0.5)
    lr = trial.suggest_loguniform("lr", 1e-4, 1e-2)
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Prepare datasets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    train_dataset = PriceDataset(X_train, y_train)
    val_dataset = PriceDataset(X_val, y_val)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    model = PriceLSTM(input_size=X.shape[2], hidden_size=hidden_size, num_layers=num_layers, dropout=dropout)
    model.to(device)

    # Train for a small number of epochs for speed
    optimiser_name = trial.suggest_categorical("optimizer", ["Adam", "SGD", "rmsprop"])
    train_model(model, train_loader, val_loader, depth, target_item, epochs=20, lr=lr, device=device, optimizer_name=optimiser_name)

    # Evaluate on val set
    model.eval()
    criterion = nn.MSELoss()
    val_loss = 0
    with torch.no_grad():
        for X_val_batch, y_val_batch in val_loader:
            X_val_batch, y_val_batch = X_val_batch.to(device), y_val_batch.to(device)
            preds = model(X_val_batch)
            loss = criterion(preds, y_val_batch)
            val_loss += loss.item() * X_val_batch.size(0)


    epochs = trial.suggest_int("epochs", 5, 20)
    trial.report(val_loss, step=epochs)
    if trial.should_prune():
        raise optuna.TrialPruned()

    val_loss /= len(val_loader.dataset)
    return val_loss

if __name__ == "__main__":

        
    paths = 1
    target_item = "Glorious bar"  # Example target item

    print('Depth 1: Glorious bar')
    print('Depth 2: Concentrated alloy bar, Enriched alloy bar, Immaculate alloy bar')
    print('Depth 3: Bronze bar, Iron bar, Steel bar, Mithril bar, Adamant bar, Rune bar, \nOrikalkum bar, Necronium bar, Bane bar, Elder rune bar')
    print('Depth 4: Copper stone spirit, Tin stone spirit, Iron stone spirit, Coal stone spirit, \nMithril stone spirit, Adamantite stone spirit, Runite stone spirit, Luminite stone spirit, Orichalcite stone spirit, Drakolith stone spirit, Banite stone spirit, Light animica stone spirit, Dark animica stone spirit')
    print('Depth 5: Copper ore, Tin ore, Iron ore, Coal, Mithril ore, Adamantite ore, Runite ore, \nLuminite, Orichalcite ore, Drakolith, Banite ore, Light animica, Dark animica')
    depth = input('Please enter the depth of items to include (1-5): ')

    X, y, scaler = load_item_data(depth, target_item, base_path="data/ge_prices", seq_len=30)

    study = optuna.create_study(direction="minimize")
    func = lambda trial: objective(trial, X, y)
    study.optimize(func, n_trials=30)

    print("Best hyperparameters:", study.best_params)

