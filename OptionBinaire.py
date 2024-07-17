# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import norm
class OptionBinaire:
    def __init__(self, spot, K, maturity, rate_curve, dividends, surface_volatility, isCall=True, payoff=1):
        self.spot = spot
        self.K = K
        self.maturity = maturity
        self.rate_curve = rate_curve
        self.dividends = dividends
        self.surface_volatility = surface_volatility
        self.isCall = isCall
        self.payoff = payoff
        self.proba_exercise = self.exercise_probability()

    def d1(self):
        rate = self.rate_curve.get_rate_for_maturity(self.maturity)
        dividend = self.dividends.dividend_value()
        div_disc, div_cont = dividend[0], dividend[1]
        volatility = self.surface_volatility.get_volatility_for_strike_maturity(self.K, self.maturity)
        return (np.log((self.spot - div_disc) / self.K) + (rate - div_cont + 0.5 * volatility ** 2) * self.maturity) / (
                volatility * np.sqrt(self.maturity))

    @property
    def price(self):
        rate = self.rate_curve.get_rate_for_maturity(self.maturity)
        d1 = self.d1()
        if self.isCall:
            return self.payoff * np.exp(-rate * self.maturity) * norm.cdf(d1)
        else:
            return self.payoff * np.exp(-rate * self.maturity) * norm.cdf(-d1)

    def __delta(self):
        d1 = self.d1()
        if self.isCall:
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    def __vega(self):
        return self.spot * norm.pdf(self.d1()) * np.sqrt(self.maturity)

    def __theta(self):
        d1 = self.d1()
        rate = self.rate_curve.get_rate_for_maturity(self.maturity)
        return -self.spot * norm.pdf(d1) * self.surface_volatility.get_volatility_for_strike_maturity(self.K,
                                                                                                      self.maturity) / (
                2 * np.sqrt(self.maturity)) - rate * self.payoff * np.exp(-rate * self.maturity) * norm.cdf(d1)

    def __rho(self):
        d1 = self.d1()
        rate = self.rate_curve.get_rate_for_maturity(self.maturity)
        return self.maturity * self.payoff * np.exp(-rate * self.maturity) * norm.cdf(d1)

    def __gamma(self):
        """
        Pour une option binaire, le gamma est négligeable, mais on peut essayer de l'approximer, avec une petit variation du Delta.'
        Il doit être proche de 0.
        """
        original_spot = self.spot
        epsilon = 0.01  # Un petit changement dans le prix du sous-jacent

        # Calcul du Delta pour le spot original
        self.spot = original_spot + epsilon
        delta_plus = self.__delta()

        # Calcul du Delta pour le spot diminué de epsilon
        self.spot = original_spot - epsilon
        delta_minus = self.__delta()

        # Réinitialisation du spot à sa valeur originale
        self.spot = original_spot

        # Calcul et retour du Gamma
        gamma_approx = (delta_plus - delta_minus) / (2 * epsilon)
        return gamma_approx

    def sensibility(self, Grecque):
        if Grecque == "delta":
            return self.__delta()
        elif Grecque == "gamma":
            return self.__gamma()
        elif Grecque == "vega":
            return self.__vega()
        elif Grecque == "theta":
            return self.__theta()
        elif Grecque == "rho":
            return self.__rho()
        else:
            return "error"

    def exercise_probability(self):
        d1 = self.d1()
        if self.isCall:
            return norm.cdf(d1)
        else:
            return norm.cdf(-d1)

    def stress_scenario(self, new_spot, new_date):
        original_spot = self.spot
        original_maturity = self.maturity
        self.spot = new_spot
        self.maturity = new_date
        new_price = self.price
        probability = self.exercise_probability()
        self.spot = original_spot
        self.maturity = original_maturity
        return new_price, probability