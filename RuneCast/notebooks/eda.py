# Example: basic EDA
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

item = "masterwork_bar"
df = pd.read_csv(f"data/ge_prices/{item}.csv", parse_dates=["date"])
df.set_index("date", inplace=True)
df.plot(title=item)
plt.show()
