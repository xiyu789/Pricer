tax_rates = {
    "USD": 35,  # United States
    "CAD": 30,  # Canada
    "EUR": 25,  # Eurozone, assumed for multiple EMEA countries
    "GBP": 28,  # United Kingdom
    "CHF": 22,  # Switzerland
    "SEK": 30,  # Sweden
    "NOK": 27,  # Norway
    "DKK": 25,  # Denmark
    "ZAR": 30,  # South Africa
    "EGP": 20,  # Egypt
    "SAR": 5,   # Saudi Arabia
    "AED": 5,   # United Arab Emirates
    "ILS": 23,  # Israel
    "RUB": 20,  # Russia
    "TRY": 35,  # Turkey
    "PLN": 19,  # Poland
    "CZK": 18,  # Czech Republic
    "HUF": 21,  # Hungary
    "RON": 16,  # Romania
    "BGN": 10,  # Bulgaria
    "NGN": 32,  # Nigeria
    "KES": 30,  # Kenya
    "INR": 34,  # India (ACPC)
    "CNY": 25,  # China (ACPC)
    "GRD": 24,  # Greece
    "LUX": 22,  # Luxembourg
    "PTE": 20,  # Portugal
    "ESP": 28,  # Spain
    "BEL": 25,  # Belgium
    "FIN": 30,  # Finland
    "IRL": 27,  # Ireland
    "ITA": 29,  # Italy
    "VND": 25,  # Vietnam
    "THB": 15,  # Thailand
    "TWD": 20,  # Taiwan
    "LKR": 18,  # Sri Lanka
    "PHP": 32,  # Philippines
    "PKR": 17,  # Pakistan
    "NZD": 26,  # New Zealand
    "MYR": 25,  # Malaysia
    "JPY": 15,  # Japan
    "IDR": 22,  # Indonesia
    "BDT": 20   # Bangladesh
}


class FinancialInstrument:
    def __init__(self):
        self.tax_rates = {
            "USD": 35, "EUR": 25, "JPY": 15, "CNY": 25, "GBP": 28
        }

        self.rate_curves = {
            "SX5E": "ESTR", "SPX": "SOFR", "HSI": "HIBOR", "DAX": "ESTR", "NIKKEI": "TIBOR", "Global": "Multiple"
        }

        self.settlement_rules = {
            "USA": "T+1", "Other": "T+2"
        }

        self.fixed_tax_levels = {
            "SPX": 35, "SX5E": 28
        }

        self.index_aliases = {
            "ser.us": "SPX",
            "eur.dx": "SX5E",
            "asi.hk": "HSI",
            "eur.de": "DAX",
            "asi.jp": "NIKKEI"
        }

    def get_actual_index_name(self, alias):
        # Return the actual index name from an alias
        return self.index_aliases.get(alias, "Unknown Index")

    def calculate_weighted_tax(self, df, index_name):
        if index_name in self.fixed_tax_levels:
            return self.fixed_tax_levels[index_name]
        else:
            if 'Currency' not in df.columns or 'Weight' not in df.columns:
                raise ValueError("DataFrame must contain 'Currency' and 'Weight' columns")
            df['Tax Rate'] = df['Currency'].map(self.tax_rates)
            if df['Tax Rate'].isna().any():
                average_tax_rate = df['Tax Rate'].dropna().mean()
                df['Tax Rate'].fillna(average_tax_rate, inplace=True)
            df['Weighted Tax'] = df['Tax Rate'] * df['Weight']
            return (df['Weighted Tax'].sum() / df['Weight'].sum()) * 100

    def get_index_info(self, df, index_alias):
        index_name = self.get_actual_index_name(index_alias)
        if index_name == "Unknown Index":
            return {"Error": "Index alias not found."}
        curve_name = self.get_rate_curve(index_name)
        average_tax = self.calculate_weighted_tax(df, index_name)
        settlement_rule = self.get_settlement_rule(df, index_name)
        return {
            "Real Index Name": index_name,
            "Rate Curve": curve_name,
            "Weighted Tax Rate (%)": average_tax,
            "Settlement Rule": settlement_rule
        }

financial_instrument = FinancialInstrument()
data = {
    "Component": ["Company A", "Company B", "Company C", "Company D"],
    "Currency": ["USD", "EUR", "USD", "USD"],
    "Weight": [0.5, 0.2, 0.2, 0.1]
}
df = pd.DataFrame(data)

# 使用别名获取SPX指数的信息
index_info = financial_instrument.get_index_info(df, "ser.us")
print(index_info)
