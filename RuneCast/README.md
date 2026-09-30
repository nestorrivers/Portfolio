# RuneCast

**Multivariate LSTM forecasting of a crafted item's price from its supply chain, using RuneScape Grand Exchange data.**

RuneCast asks a simple question: does knowing the prices of an item's *inputs* help predict the price of the item itself? It takes a finished good (the default target is the **Glorious bar**), adds price histories for progressively deeper tiers of its supply chain, and trains an LSTM to predict the target's next-day price from the previous 30 days.

> **Status.** The data pipeline, model, training loop, hyperparameter search and inference script are written, and a depth-5 model has been trained. **The evaluation is not done**: there is no baseline comparison and no reported error metrics yet. The [Evaluation](#evaluation) and [Known limitations](#known-limitations) sections say exactly what is missing and why, so you can judge the project on what it is now.

---

## The idea: precursor depth

Crafted items depend on inputs that have their own price dynamics. A model that only sees the target's own history can't see a shock upstream. RuneCast makes the supply chain an explicit, configurable input through a **depth** setting (`constants.py`):

| Depth | Tier added | Items | Cumulative features |
| --- | --- | --- | --- |
| 1 | Target | Glorious bar | 1 |
| 2 | Intermediate alloy bars | 3 | 4 |
| 3 | Standard metal bars | 10 | 14 |
| 4 | Stone spirits | 13 | 27 |
| 5 | Raw ores | 13 | 40 |

Each depth includes all shallower tiers. So the same code answers the research question directly: train at depth 1 (a univariate model) and at depth *n*, and compare.

The working hypothesis is that deeper inputs help when supply chains are tightly coupled, with diminishing returns as inputs get further from the finished good. **This is a hypothesis, not a result.**

---

## How it works

```text
price_scraper.py   Weird Gloop GE history API → one CSV per item (cached, rate-limited)
        ▼
data_utils.py      Load items for the chosen depth → align on date → standardise
                   → 30-day sliding windows: X (samples, 30, n_features), y (next-day target)
        ▼
train.py           PriceLSTM (LSTM → last timestep → linear) with MSE loss;
                   best-validation checkpoint saved with its architecture metadata
        ▼
optimise.py        Optuna search over hidden size, layers, dropout, learning rate,
                   batch size and optimiser
        ▼
predict.py         Pick a saved model → fetch the last 30 days live → scale with the
                   saved scaler → predict → inverse-transform → up / down / stable
```

### Design decisions

- **Scaler saved next to the model.** `StandardScaler` is persisted per (item, depth) as `depthN_scaler.pkl`, so inference scales live data exactly as training did, and the prediction is inverse-transformed back to coins.
- **Self-describing checkpoints.** Each `.pt` file stores `hidden_size`, `num_layers`, `input_size` and `dropout` alongside the weights, so `predict.py` can rebuild the architecture without the training code's settings.
- **Depth as data, not code.** `get_items_by_depth()` is the single source of truth for which items feed a model, used by the scraper, loader and predictor alike. Changing the supply chain is a one-file change.
- **Polite data collection.** The scraper caches each CSV, skips items already downloaded, and waits between requests, with an identifying User-Agent.
- **Aligned on common dates.** Items are joined on date and rows with any missing price are dropped, so every feature is observed on every step.

### The data

Daily prices for 40 items from the [Weird Gloop](https://api.weirdgloop.org/) exchange history API, included in `data/ge_prices/`:

| Depth | Features | Usable days | Date range |
| --- | --- | --- | --- |
| 1 to 4 | 1 to 27 | 2,479 | 2018-09-29 to 2025-07-30 |
| 5 | 40 | 2,379 | 2019-01-07 to 2025-07-30 |

Depth 5 has fewer days because some ores have shorter histories. The final step of `predict.py` also reads the current spot price from the RuneScape Wiki's exchange page, to report the expected direction.

---

## Usage

```bash
pip install -r requirements.txt

python price_scraper.py     # download price history (skips existing CSVs)
python predict.py           # choose a saved model, fetch live data, print a forecast
python optimise.py          # Optuna search (prompts for depth 1 to 5)
```

`predict.py` reports the model's next-day price, the current price, and a direction (`up` / `down` / `stable`, using a ±1% band). It's an experiment, not financial advice, and the results are not validated (below).

> `requirements.txt` is a full environment freeze saved as UTF-16, so `pip install -r` may need converting to UTF-8 first. `train.py` currently holds the model and training loop as importable code with no command-line entry point (see limitations).

---

## Evaluation

**There are no results yet.** The intended design is:

- **Metric:** RMSE and MAE in coins on a held-out test period.
- **Baselines, in increasing strength:**
  1. **Persistence**: tomorrow's price equals today's. Daily prices are very autocorrelated, so this is the baseline any forecast must beat, and models trained on price *levels* often end up learning it.
  2. **Univariate LSTM** (depth 1): the target's own history only.
  3. **Multivariate LSTM** at depths 2 to 5.
- **The comparison that matters:** each multivariate depth against the depth-1 model and against persistence, using the same split and seeds.

| Model | Depth | Features | RMSE | MAE | vs. persistence |
| --- | --- | --- | --- | --- | --- |
| Persistence | – | – | *not run* | *not run* | – |
| Univariate LSTM | 1 | 1 | *not run* | *not run* | *not run* |
| Multivariate LSTM | 2 | 4 | *not run* | *not run* | *not run* |
| Multivariate LSTM | 3 | 14 | *not run* | *not run* | *not run* |
| Multivariate LSTM | 4 | 27 | *not run* | *not run* | *not run* |
| Multivariate LSTM | 5 | 40 | *not run* | *not run* | *not run* |

---

## Known limitations

These are the gaps between what the project is for and what the code currently does. The first three would change any result, so they come first.

1. **The train/validation split leaks.** `optimise.py` uses a shuffled `train_test_split` on 30-day windows that overlap by 29 days, so near-identical windows land on both sides, and validation loss will look better than real out-of-sample performance. Time-series evaluation needs a chronological split (train on earlier dates, test on later ones), ideally with walk-forward validation.
2. **The scaler sees the future.** `StandardScaler` is fit on the *entire* series before splitting, so training statistics include test-period prices. It should be fit on the training period only.
3. **No baseline and no test metrics.** `evaluate.py` is an unfinished stub (its data-loading call is a placeholder and it points at a checkpoint path that doesn't exist), so no RMSE or MAE has been produced, and there is no persistence or univariate comparison. The results table above is empty for that reason.
4. **`train.py` has no entry point.** It defines `PriceLSTM`, `PriceDataset` and `train_model`, but nothing runs them directly; training only happens through `optimise.py`.
5. **Optuna trials overwrite the saved model.** `train_model` writes `models/<item>/depthN_model.pt` on every improvement, and each trial calls it, so the checkpoint on disk is the last trial's best, not the study's best. The `epochs` value suggested at the end of the objective is never used (training is fixed at 20 epochs), and the pruning check runs after training has finished.
6. **Scaling and level targets.** Predicting standardised price *levels* on a series that grows over seven years means test-period values fall outside the training range. Predicting returns (log differences) would be more stable and comparable across periods.
7. **Small housekeeping bugs.** The README used to call the tuner `optimize.py` (it's `optimise.py`); `PriceDataset` has an unused `item_depth` option; `suggest_loguniform` is deprecated in current Optuna; the scraper's default depth and the tuner's interactive prompt are separate code paths.

---

## Next steps

In order:

1. Chronological split and train-only scaling (fixes limitations 1 and 2).
2. Add the persistence and univariate baselines and finish `evaluate.py`, then fill in the results table (limitation 3).
3. Add a `__main__` to `train.py` and stop the tuner overwriting the final checkpoint (limitations 4 and 5).
4. Try log-return targets, and add walk-forward validation across several test periods.
5. Only then look at architecture changes such as Transformers, or extensions to other item chains.

---

## Tech stack

Python 3.10+ · PyTorch (LSTM) · pandas / NumPy · scikit-learn (scaling) · Optuna (hyperparameter search) · requests / BeautifulSoup (data collection) · Matplotlib / Seaborn (exploration)

---

## Why this project

The aim was a forecasting problem where the structure of the data can be argued for, not just a model fitted to a CSV: prices in a crafting economy are linked by known dependencies, and "depth" turns that into an experiment with a clear yes/no question. The pipeline exists to answer that question. The part still to do is the honest test.

*Inspired by earlier MSc dissertation work on time-series modelling, revisited with modern deep-learning tooling.*