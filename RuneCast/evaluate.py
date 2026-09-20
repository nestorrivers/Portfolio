import torch
from train import PriceLSTM
import numpy as np
from data_utils import load_item_data
from sklearn.metrics import mean_squared_error

# Load best model and data

checkpoint = torch.load("best_model_depth5_Glorious_bar.pt")
hidden_size = checkpoint['hidden_size']
num_layers = checkpoint['num_layers']
input_size = checkpoint['input_size']
dropout = checkpoint.get('dropout', 0.0)

model = PriceLSTM(input_size, hidden_size, num_layers, dropout)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

X_test, y_test, _ = load_item_data(...)

# Convert and run inference
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32)

with torch.no_grad():
    preds = model(X_test).squeeze().numpy()

print("RMSE:", np.sqrt(mean_squared_error(y_test, preds)))
