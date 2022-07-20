import pandas as pd
df=pd.read_csv("../time_series/rain.csv",delimiter=";")
cols=df.columns[1:]
print(cols)

for c in cols:
    df[c]=[1 if v>0 else 0 for v in df[c]]
df.to_csv("../time_series/rain_binary.csv",sep=";")