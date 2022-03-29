
# %%
import numpy as np
import pandas as pd
import plotly.express as px

from pathlib import Path

# %%
folder = Path('timings')
csv_files = [e for e in folder.iterdir() if e.as_posix().endswith('.csv')]
csv_files

# %%
file_path = csv_files[-1].as_posix()
print(file_path)

file_name = csv_files[-1].name
table = pd.read_csv(file_path, index_col=0)
table = table.iloc[5:]


# %%
delay = np.array(table['time'])[1:] - np.array(table['time'])[:-1]
delay = np.concatenate([[0.1], delay])

table['delay'] = delay - 0.1

table

# %%
_table = table.copy()
_table['color'] = table['uid'].map(lambda x: str(x))
fig = px.scatter(_table, y='delay', color='color', title='Scatter')
fig.show()

# %%
fig = px.box(_table, y='delay', title='Box')
fig.show()

# %%
