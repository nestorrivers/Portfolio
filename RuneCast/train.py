import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import time

class PriceLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout=0.0):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)


class PriceDataset(Dataset):
    def __init__(self, X, y, item_depth=None):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

        if item_depth is not None:
            depth_tensor = torch.full((self.X.shape[0], self.X.shape[1], 1), float(item_depth))
            self.X = torch.cat((self.X, depth_tensor), dim=2)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def get_optimizer(model, optimizer_name='adam', lr=1e-3, weight_decay=0.0):
    optimizer_name = optimizer_name.lower()
    if optimizer_name == 'adam':
        return torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name == 'adamw':
        return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name == 'sgd':
        return torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=weight_decay)
    elif optimizer_name == "rmsprop":
        return torch.optim.RMSprop(model.parameters(), lr=lr, weight_decay=weight_decay)
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer_name}")



def train_model(model, train_loader, val_loader, depth, target_item, epochs, optimizer_name, lr, device, weight_decay=0.0):
    criterion = nn.MSELoss()
    optimizer = get_optimizer(model, optimizer_name, lr, weight_decay)
    model.to(device)

    best_val_loss = float('inf')

    plt.ion()
    fig, ax = plt.subplots()
    train_losses, val_losses = [], []

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * X_batch.size(0)

        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_val, y_val in val_loader:
                X_val, y_val = X_val.to(device), y_val.to(device)
                preds = model(X_val)
                loss = criterion(preds, y_val)
                val_loss += loss.item() * X_val.size(0)

        val_loss /= len(val_loader.dataset)

        train_losses.append(train_loss)
        val_losses.append(val_loss)

        # ax.clear()
        # ax.plot(train_losses, label="Train Loss")
        # ax.plot(val_losses, label="Val Loss")
        # ax.legend()
        # ax.set_xlabel("Epoch")
        # ax.set_ylabel("Loss")
        # ax.set_title("Training Progress")
        # plt.pause(0.1)

        print(f"Epoch {epoch+1}/{epochs} — Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                    'model_state_dict': model.state_dict(),
                    'hidden_size': model.lstm.hidden_size,
                    'num_layers': model.lstm.num_layers,
                    'input_size': model.lstm.input_size,
                    'dropout': model.lstm.dropout,
                    # possibly other metadata
                }, f'models/{target_item.replace(" ", "_")}/depth{depth}_model.pt')
            print("Saved best model.")

    # plt.ioff()
    # plt.show()
    print("Training complete. Best validation loss:", best_val_loss) 

    return model
