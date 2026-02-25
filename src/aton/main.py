import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re
import logging

BASE_DIR = Path(__file__).resolve().parents[2]

data_folder = BASE_DIR / "data"

logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DataNormalize:
    def __init__(self, df):
        self.df = self._new_df_(df) 
        self.df_normalize(self.df)

    def _new_df_(self, df):
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

        return new_df

    def df_normalize(self, new_df):
        new_df["FIO_owner"] = new_df["FIO_owner"].apply(self.normalize_fio)
        new_df["Company_name"] = new_df["Company_name"].apply(self.normalize_company)
        new_df["INN_company"] = new_df["INN_company"].apply(self.normalize_inn)
        new_df["Ownership"] = new_df["Ownership"].apply(self.normalize_ownership)
        new_df["Ownership_date"] = new_df["Ownership_date"].apply(self.normalize_date)
        logging.info("Normalize is done")
        
    @staticmethod
    def normalize_fio(fio):
        if not fio or pd.isna(fio):
            return None

        fio = re.sub(r"\s+", " ", fio.strip()).replace(". ", ".")
        parts = fio.split()

        if not fio.endswith("."):
            fio += "."
        
        if len(parts) > 1 and "." in parts[1]:
            return fio
            
        if len(parts) == 3:
            fio = f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
        
        if len(parts) == 2:
            fio = f"{parts[0]} {parts[1][0]}."

        return fio

    @staticmethod
    def normalize_company(company):
        if pd.isna(company) or company == "":
            return None

        company = company.replace('"', "")
        company = re.sub(r"\s+", " ", company.strip())
        return company

    @staticmethod
    def normalize_inn(inn):
        if pd.isna(inn) or inn == "":
            return None
        return str(inn)

    @staticmethod
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
    
    @staticmethod
    def normalize_date(date):
        if pd.isna(date) or date == "":
            return None
        try:
            return pd.to_datetime(date, errors="coerce", dayfirst=True).strftime("%Y-%m-%d")
        except:
            return None

class DataAnalyze:
    def __init__(self, df):
        self.df = df
        self.start_analyzing()

    def start_analyzing(self):
        logging.info("Starting analyze...")
        print(f"Result of first analyze ------------- \n{self.analyze_ownership(self.df)}")
        print(f"Result of second analyze ------------- \n{self.analyze_ownership_changes(self.df)}")
        print(f"Result of third analyze ------------- \n{self.analyze_multi_owners(self.df)}")

    @staticmethod
    def analyze_ownership(df, plot=True):
        df_valid = df.dropna(subset=["Ownership"])
        company_sum = df_valid.groupby("Company_name")["Ownership"].sum()
        over_100 = company_sum[company_sum > 100]

        if plot:
            over_100.sort_values().plot(kind="barh", color="tomato")
            plt.title("Companies with total ownership > 100%")
            plt.show()
        return over_100
    
    @staticmethod
    def analyze_ownership_changes(df, plot=True):
        df_valid = df.dropna(subset=["Ownership", "Ownership_date"])
        ownership_changes = df_valid.groupby("Company_name")["Ownership"].nunique()
        changed_companies = ownership_changes[ownership_changes > 1]

        if plot:
            for company in changed_companies.index:
                subset = df_valid[df_valid["Company_name"] == company]
                plt.plot(subset["Ownership_date"], subset["Ownership"], marker="o", label=company)
            plt.xlabel("Date")
            plt.ylabel("Ownership %")
            plt.title("Ownership changes over time")
            plt.legend()
            plt.show()
        return changed_companies
    
    @staticmethod
    def analyze_multi_owners(df):
        df_valid = df.dropna(subset=["FIO_owner", "Company_name"])
        owner_counts = df_valid.groupby("FIO_owner")["Company_name"].nunique()
        multi_company_owners = owner_counts[owner_counts > 1]
        return multi_company_owners


if __name__ == "__main__":
    df = pd.read_csv(data_folder / "corporate_links_raw.csv")
    df_normalizer = DataNormalize(df)
    data_analyzer = DataAnalyze(df_normalizer.df)

