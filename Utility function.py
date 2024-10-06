tax_rates = {
    "US": 35,  # United States
    "CA": 30,  # Canada
    "EU": 25,  # Eurozone, assumed for multiple EMEA countries
    "GB": 28,  # United Kingdom
    "CH": 22,  # Switzerland
    "SE": 30,  # Sweden
    "NO": 27,  # Norway
    "DK": 25,  # Denmark
    "ZA": 30,  # South Africa
    "EG": 20,  # Egypt
    "SA": 5,   # Saudi Arabia
    "AE": 5,   # United Arab Emirates
    "IL": 23,  # Israel
    "RU": 20,  # Russia
    "TR": 35,  # Turkey
    "PL": 19,  # Poland
    "CZ": 18,  # Czech Republic
    "HU": 21,  # Hungary
    "RO": 16,  # Romania
    "BG": 10,  # Bulgaria
    "NG": 32,  # Nigeria
    "KE": 30,  # Kenya
    "IN": 34,  # India
    "CN": 25,  # China
    "GR": 24,  # Greece
    "LU": 22,  # Luxembourg
    "PT": 20,  # Portugal
    "ES": 28,  # Spain
    "BE": 25,  # Belgium
    "FI": 30,  # Finland
    "IE": 27,  # Ireland
    "IT": 29,  # Italy
    "VN": 25,  # Vietnam
    "TH": 15,  # Thailand
    "TW": 20,  # Taiwan
    "LK": 18,  # Sri Lanka
    "PH": 32,  # Philippines
    "PK": 17,  # Pakistan
    "NZ": 26,  # New Zealand
    "MY": 25,  # Malaysia
    "JP": 15,  # Japan
    "ID": 22,  # Indonesia
    "BD": 20   # Bangladesh
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
