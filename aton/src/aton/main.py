import pandas as pd
import seaborn as sns
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parents[2]

data_folder = BASE_DIR / "data"

# 1
df = pd.read_csv(data_folder / "corporate_links_raw.csv")

new_df = df["FIO_owner"].str.split(",", expand=True)
new_df.columns = [
    "FIO_owner",
    "Company_name",
    "INN_company",
    "Ownership",
    "Region",
    "Source",
    "Ownership_date"
]

def normalize_fio(fio):
    if not fio or pd.isna(fio):
        return None

    fio = re.sub(r"\s+", " ", fio.strip())
    parts = fio.split()

    if len(parts) == 3:
        return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
    
    if len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."

    return fio.replace("  ", " ").replace(". ", ".")

new_df["FIO_owner"] = new_df["FIO_owner"].apply(normalize_fio)

def normalize_company(company):
    if pd.isna(company) or company == "":
        return None

    company = company.replace('"', "")
    company = re.sub(r"\s+", " ", company.strip())
    return company

new_df["Company_name"] = new_df["Company_name"].apply(normalize_company)

def normalize_inn(inn):
    if pd.isna(inn) or inn == "":
        return None
    return str(inn)

new_df["INN_company"] = new_df["INN_company"].apply(normalize_inn)

def normalize_ownership(value):
    if pd.isna(value) or value == "":
        return None
    value = value.replace(" ", "").replace("%", "").replace(",", ".")
    try:
        num = float(value)
    except:
        return None
    if num <= 1:
        num *= 100
    return num
new_df["Ownership"] = new_df["Ownership"].apply(normalize_ownership)

def normalize_date(date):
    if pd.isna(date) or date == "":
        return None
    try:
        return pd.to_datetime(date, errors="coerce", dayfirst=True).strftime("%Y-%m-%d")
    except:
        return None
new_df["Ownership_date"] = new_df["Ownership_date"].apply(normalize_date)

print(new_df)
