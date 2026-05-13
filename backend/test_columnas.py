import pandas as pd; df = pd.read_csv('Books_Dataset_GoodReads.csv'); df.columns = df.columns.str.strip().str.lower(); print(df.columns.tolist())
