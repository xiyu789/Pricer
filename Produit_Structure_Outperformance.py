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
from matplotlib import pyplot as plt
import pandas as pd
import sys


class Certificat_Outperformance:
    def __init__(self, param_opt: Param_options, K, surface_volatility, leverage):
        self.short_put = OptionVanille(param_opt, K, 'Put', surface_volatility)
        self.long_call = OptionVanille(param_opt, K, 'Call', surface_volatility)
        self.leverage = leverage
        self.proba_exercise = self.exercise_probability()

    def price(self):
        price_put = -self.short_put.price
        price_call = self.leverage * self.long_call.price
        return price_put + price_call

    # Calculate the Greeks for the certificate
    def delta(self):
        return -self.short_put.delta() + self.leverage * self.long_call.delta()

    def gamma(self):
        return -self.short_put.gamma() + self.leverage * self.long_call.gamma()

    def vega(self):
        return -self.short_put.vega() + self.leverage * self.long_call.vega()

    def theta(self):
        return -self.short_put.theta() + self.leverage * self.long_call.theta()

    def rho(self):
        return -self.short_put.rho() + self.leverage * self.long_call.rho()

    def exercise_probability(self):
        return self.long_call.exercise_probability()


    
    # Additional methods from OptionVanille to manage sensitivity and scenarios
    def sensibility(self, sensi_type):
        # Combine sensitivities of the put and the call, adjusted by leverage
        put_sensitivity = getattr(self.short_put, 'sensibility')(sensi_type)
        call_sensitivity = getattr(self.long_call, 'sensibility')(sensi_type)
        if sensi_type in ["delta", "gamma", "vega", "theta", "rho"]:
            return -put_sensitivity + self.leverage * call_sensitivity
        return "Invalid sensitivity type"

    def stress_scenario(self, new_spot, new_date):
        # Combine stress scenario effects of both options
        put_scenario = self.short_put.stress_scenario(new_spot, new_date)
        call_scenario = self.long_call.stress_scenario(new_spot, new_date)
        combined_price = -put_scenario[0] + self.leverage * call_scenario[0]
        combined_probability = call_scenario[1]  # As specified, use long call's exercise probability
        return combined_price, combined_probability


    
    

