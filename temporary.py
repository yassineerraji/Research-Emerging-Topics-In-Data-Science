import pandas as pd 

owid = pd.read_csv("data/raw/owid-co2-data.csv")
print(f"OWID columns : {owid.columns}")

iea = pd.read_csv("data/raw/WEO2025_AnnexA_Free_Dataset_World.csv")
print(f"IEA columns : {iea.columns}")