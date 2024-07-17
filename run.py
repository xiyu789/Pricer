from RateCurve import RateCurve
from VolatilitySurface import VolatilitySurface

from Obligation import Bond
from OptionVanille import *
from Strategy import *
from OptionBarriere import OptionBarrière
from OptionBinaire import OptionBinaire
from Produit_Structure_Outperformance import *
from Produit_Structure_Reverse import *

from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
import sys

##################################################################################################
## RÉCUPÉRATION DES DONNÉES ##
##################################################################################################
path = "Data.xlsx"

## CHEMIN A MODIFIE 

underlying = "equity"   # equity / fx / index
df_underlying = pd.read_excel(path, sheet_name=0)
df_vol_equity = pd.read_excel(path, sheet_name=1)
df_vol_fx = pd.read_excel(path, sheet_name=2)
df_vol_index = pd.read_excel(path, sheet_name=3)
df_rate = pd.read_excel(path, sheet_name=4)
def get_price(date, category):
    if category == 'equity':
        return df_underlying.loc[df_underlying['Date Equity'] == pd.to_datetime(date), 'BIM FP Equity'].values[0]
    elif category == 'fx':
        return df_underlying.loc[df_underlying['Date FX'] == pd.to_datetime(date), 'EURUSD BGN Curncy'].values[0]
    elif category == 'index':
        return df_underlying.loc[df_underlying['Date Index'] == pd.to_datetime(date), 'SXXP Index'].values[0]

# Si la date saisie est un week-end ou un jour férié, le prix n'existe pas.
start_date = pd.to_datetime('2024-1-11')
end_date = pd.to_datetime('2025-1-11')
spot = get_price(start_date, underlying)
strike = spot * 1.1
maturity = (end_date - start_date).days / 365
div_type = "continous"  # continuous / discrete
opt_type = "call"       # call / put
r_foreign = 0.02

# Construction des objets pour la courbe des taux, la surface de volatilité et les dividendes
rate_curve = RateCurve(curve=[
    (1, df_rate.at[0, 'EUR OIS ESTR']),
    (2, df_rate.at[1, 'EUR OIS ESTR']),
    (3, df_rate.at[2, 'EUR OIS ESTR'])
])

if underlying.lower() == 'equity':
    df_vol = df_vol_equity
elif underlying.lower() == 'fx':
    df_vol = df_vol_fx
else:  # index
    df_vol = df_vol_index

surface = {(float(strike), row['nb_année']): row[strike] for index, row in df_vol.iterrows() for strike in df_vol.columns[1:]}

volatility_surface = VolatilitySurface(surface)
dividends = Dividends(div_type, spot, start_date, end_date, rate_curve, structure=[(datetime(2024, 1, 1), 0.02), (datetime(2024, 5, 1), 0.025), (datetime(2025, 1, 1), 0.03)])

# Affichage des valeurs des dividendes
print("the [div_disc, div_cont] list is ",  dividends.dividend_value(), ", and we take the ", div_type)
# la classe Param_options sauvegarde tous les paramètres concernant l'option sauf le strike
params_opt = Param_options(spot, r_foreign, maturity, rate_curve, underlying, dividends)

##################################################################################################
## OBLIGATION ##
##################################################################################################
print("obligation:")
# (self, maturity,rate_curve, taux_coupon, frequence_coupon, face_value=100):
T_bond = 10
tx_coupon_bond = 0.02
freq_coupon = "semi-annuel" # valeur à prendre : annuel, semi-annuel, trimestriel, s'il ne trouve pas ces valeurs, alros c'est considéré comme "annuel"
Bond_obj = Bond(T_bond, rate_curve, tx_coupon_bond, freq_coupon, face_value=100)
print("price of the bond is ", Bond_obj.price)

##################################################################################################
## OPTION VANILLE ET STRATEGIES ##
##################################################################################################
print(" OPTION VANILLE ET STRATEGIES ")
K1, K2, K3 = spot*0.9, spot, spot*1.1

if K1 >= K2 or K2 >= K3:
    print("Error: Values must be in ascending order")
    sys.exit()

# Création des objets
Call_vanille = OptionVanille(params_opt, strike, 'call', volatility_surface)
Put_vanille = OptionVanille(params_opt, strike, 'put', volatility_surface)

Spread_class = Spread(params_opt, K1, K2, volatility_surface)
SSS_class = SSS(params_opt, K1, volatility_surface)
Strangle_obj = Strangle(params_opt, K1, K2, volatility_surface)
Butterfly_obj = Butterfly(params_opt, K1, K2, K3, volatility_surface)

print("price of call option is ", Call_vanille.price)
print("price of put option is ", Put_vanille.price)
print("price of box is ", Spread_class.box_price())
print("price of call spread is ", Spread_class.call_spread_price())
print("price of put spread is ", Spread_class.put_spread_price())
print("the price of Straddle is ", SSS_class.straddle_price())
print("the price of strips is ", SSS_class.strips_price())
print("the price of Straps is ", SSS_class.straps_price())
print("the price of Strangle is ", Strangle_obj.price)
print("the price of Butterfly is ", Butterfly_obj.price)

##################################################################################################
## OPTION BINAIRE ##
##################################################################################################
print("")
# Données de test
spot = 100
strike = 110
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 1, 1)
maturity = (end_date - start_date).days/365
div_type = "continous"  # continuous / discrete
opt_type = "call"       # call / put
# Construction des objets pour la courbe des taux, la surface de volatilité et les dividendes
rate_curve = RateCurve(curve=[(1, 0.05), (2, 0.025), (3, 0.03)])
surface = {
    (90, 1): 0.19, (100, 1): 0.2, (110, 1): 0.21,
    (90, 2): 0.24, (100, 2): 0.25, (110, 2): 0.26,
    (90, 3): 0.28, (100, 3): 0.3, (110, 3): 0.32
}

volatility_surface = VolatilitySurface(surface)
dividends = Dividends(div_type, spot, start_date, end_date, rate_curve, structure=[(datetime(2024, 1, 1), 0.02), (datetime(2024, 5, 1), 0.025), (datetime(2025, 1, 1), 0.03)])

isCall = True
payoff = 1

# Création d'une option binaire de test
option_binaire = OptionBinaire(spot, strike, maturity, rate_curve, dividends, volatility_surface, isCall, payoff)
print("the price of OPTION BINAIRE equals to ", option_binaire.price)

##################################################################################################
## OPTION BARRIERE ##
##################################################################################################

option_barriere = OptionBarrière(100, maturity, 105, volatility_surface, rate_curve, "call", "KI", 108, 500, 100,dividends)
print("the price of OPTION BARRIERE equals to ", option_barriere.price)


##################################################################################################
## PRODUIT STRUCRUTE ##
##################################################################################################

print(" ")

leverage = 5
Outperformance_obj = Certificat_Outperformance(params_opt, strike, volatility_surface, leverage)

print("price of the certificate outperformance : ", Outperformance_obj.price())
print("the certificate outperformance sensi equals to ", Outperformance_obj.sensibility('delta'))
print("the certificate outperformance exercise proba equals to ", Outperformance_obj.exercise_probability())

print(" ")

Reverse_Convertible = Reverse_Convertible(Bond_obj, Put_vanille)
print("price of the reverse convertible : ", Reverse_Convertible.price())
print("the reverse convertible sensi equals to ", Reverse_Convertible.delta())
print("the reverse convertible exercise proba equals to ", Reverse_Convertible.exercise_probability())


#### =======================================================================================================
## AFFICHAGE LES RESULTATS DES PRODUITS ##
#### =======================================================================================================

# Création d'un dictionnaire vide pour sauvegarder les produits et les résultats
dictionnaire = {}

# ajout de l'obligation dans la dictionnaire
col_name = ["Nom_produit", "prix", "MacDur", "ModDur","DV01", "Sensi"]
df = pd.DataFrame(columns=col_name, index=[0])
df.iloc[0,0] = "Obligation taux fix"

df.iloc[0,1] = Bond_obj.price
df.iloc[0,2] = Bond_obj.MacDur
df.iloc[0,3] = Bond_obj.Mod_Dur
df.iloc[0,4] = Bond_obj.DV01
df.iloc[0,5] = Bond_obj.sensibility()

dictionnaire["Obligation"] = df

# ajout de la reverse convertible dans la dictionnaire
col_name = ['Nom_produit', 'prix', 'delta', "proba_exe"]
df = pd.DataFrame(columns=col_name, index=[0])
df.iloc[0,0] = "Reverse_Convertible"
df.iloc[0,1] = Reverse_Convertible.price()
df.iloc[0,2] = Reverse_Convertible.exercise_probability()
dictionnaire["Reverse_Convertible"] = df

# ici, nous distinguons 2 groupes selon le nombre d'entrées pour la fonction pnl
group_1 = {
    "Call": Call_vanille,
    "Put": Put_vanille,
    "Strangle": Strangle_obj,
    "Butterfly": Butterfly_obj,
    "Option_Binaire": option_binaire,
    "Option_Barrière": option_barriere,
    "Certificate_Outperformance": Outperformance_obj
}

group_2 = {
    "Call_Spread": Spread_class,
    "Put_Spread": Spread_class,
    "Box": Spread_class,
    "Straddle": SSS_class,
    "Strips": SSS_class,
    "Straps": SSS_class,
}

col_name = ['Nom_produit', 'Prix', 'Proba_exe', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho', 'stress_scenario']

new_spot = 110
new_date = 1.5


produits_noms = ["Call", "Put", "Call_Spread", "Put_Spread", "Box", "Straddle", "Strips", "Straps", "Strangle",
                 "Butterfly", "Option_Binaire", "Option_Barrière", "Certificate_Outperformance"]
for nom in produits_noms:
    df_nom = nom
    df = pd.DataFrame(columns=col_name, index=[0])
    df.iloc[0, 0] = nom
    if nom in group_1:
        class_utilise = group_1.get(nom)
        df.iloc[0, 1] = class_utilise.price
        df.iloc[0, 2] = class_utilise.proba_exercise
        df.iloc[0, 3] = class_utilise.sensibility("delta")
        df.iloc[0, 4] = class_utilise.sensibility("gamma")
        df.iloc[0, 5] = class_utilise.sensibility("vega")
        df.iloc[0, 6] = class_utilise.sensibility("theta")
        df.iloc[0, 7] = class_utilise.sensibility("rho")
        df.iloc[0, 8] = class_utilise.stress_scenario(new_spot, new_date)
        dictionnaire[df_nom] = df
    else:
        class_utilise = group_2.get(nom)
        df.iloc[0, 1] = class_utilise.price(nom)
        df.iloc[0, 2] = 0  # pour les stratégies, nous n'étudions pas la probabilité d'exercice
        df.iloc[0, 3] = class_utilise.sensibility(nom, "delta")
        df.iloc[0, 4] = class_utilise.sensibility(nom, "gamma")
        df.iloc[0, 5] = class_utilise.sensibility(nom, "vega")
        df.iloc[0, 6] = class_utilise.sensibility(nom, "theta")
        df.iloc[0, 7] = class_utilise.sensibility(nom, "rho")
        df.iloc[0, 8] = class_utilise.stress_scenario(nom, new_spot, new_date)
        dictionnaire[df_nom] = df

# pour afficher tous les résultats
pd.set_option('display.max_columns', None)

print(dictionnaire.get("Obligation"))
print(dictionnaire.get("Call"))
print(dictionnaire.get("Put"))
print(dictionnaire.get("Call_Spread"))
print(dictionnaire.get("Put_Spread"))
print(dictionnaire.get("Box"))
print(dictionnaire.get("Straddle"))
print(dictionnaire.get("Strips"))
print(dictionnaire.get("Straps"))
print(dictionnaire.get("Straps"))
print(dictionnaire.get("Option_Binaire"))
print(dictionnaire.get("Option_Barrière"))
print(dictionnaire.get("Certificate_Outperformance"))
print(dictionnaire.get("Reverse_Convertible"))

# Graphique PnL pour les stratégies
def graph_pnl(product_name, product):
    S_T_range = range(int(spot) - 50, int(spot) + 50)
    pnl = []
    for S_Ti in S_T_range:
        if product_name in group_1:
            pnl.append(product.pnl(S_Ti))
        else:
            pnl.append(product.pnl(product_name, S_Ti))
    plt.plot(list(S_T_range), pnl, label=f'PnL of {product_name}', color='blue')
    plt.title(f'PnL of {product_name}')
    plt.xlabel('Spot Price at Maturity')
    plt.ylabel('Profit and Loss')
    plt.axhline(0, color='red', linestyle='--')
    plt.legend()
    plt.show()
    print()

Graph_PnL_test = graph_pnl("Straps", SSS_class)

