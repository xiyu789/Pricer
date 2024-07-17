import numpy as np
from scipy.stats import norm
from OptionBarriere import *
from OptionBinaire import *
from RateCurve import *
from VolatilitySurface import *
from OptionVanille import *
from datetime import datetime
from Strategy import *
from Obligation import *

class Reverse_Convertible:
    def __init__(self, bond: Bond, put_option: OptionVanille):
        self.bond = bond
        self.put_option = put_option
        self.spot = put_option.param_opt.S  # Utiliser le spot price de l'option
        self.maturity = put_option.param_opt.maturity  # Utiliser la maturité de l'option

    def price(self):
        bond_price = self.bond.price
        put_option_price = -self.put_option.price
        total_price = bond_price + put_option_price
        return total_price

    def exercise_probability(self):
        # Puisque nous sommes toujours short sur un put, la probabilité d'exercice du reverse convertible est de 1
        return 1

    def delta(self):
        # Calcul du delta pour le put short (négatif du delta du put)
        d1 = self.put_option.calcul_d1()
        put_delta = -norm.cdf(d1) if self.put_option.opt_type.lower() == "put" else -norm.cdf(-d1)
        return put_delta

    def stress_scenario(self, new_spot, new_date):
        original_spot = self.spot
        original_maturity = self.maturity
        self.spot = new_spot
        self.maturity = new_date
        self.put_option.param_opt.S = new_spot
        self.put_option.param_opt.maturity = new_date
        new_price = self.price()
        probability = self.exercise_probability()
        # Restaurer les valeurs originales après la simulation
        self.spot = original_spot
        self.maturity = original_maturity
        self.put_option.param_opt.S = original_spot
        self.put_option.param_opt.maturity = original_maturity
        return new_price, probability
    
    

