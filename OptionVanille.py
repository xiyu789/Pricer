import numpy as np
from Dividends import Dividends
from scipy.stats import norm

N = norm.cdf
pdf = norm.pdf

# la classe Param_options sauvegarde tous les paramètres concernés l'option sauf strike
class Param_options:
    def __init__(self, S, r_foreign, maturity, rate_curve, underlying, Dividend: Dividends):
        self.S = S
        self.r_foreign = r_foreign  # taux étranger
        self.maturity = maturity
        self.r = rate_curve.get_rate_for_maturity(self.maturity)  # taux domestique
        self.underlying = underlying  # Equity/Index/FX
        self.dividends = Dividend

class OptionVanille:
    def __init__(self, param_opt: Param_options, K, opt_type, surface_volatility):
        self.__S = param_opt.S
        self.__K = K
        self.__r_foreign = param_opt.r_foreign  # taux étranger
        self.opt_type = opt_type  # Call/Put
        self.__maturity = param_opt.maturity
        self.__vol = surface_volatility.get_volatility_for_strike_maturity(self.__K, self.__maturity)
        self.__r = param_opt.r  # taux domestique
        self.__underlying = param_opt.underlying  # Equity/Index/FX
        self.__dividend = param_opt.dividends
        self.__div = self.div_value()
        self.proba_exercise = self.exercise_probability()
        self.param_opt = param_opt

    def div_value(self):
        # si le sous-jacent n'est pas une action, pas de dividende
        if self.__underlying.lower() == "equity":
            div = self.__dividend.dividend_value()
        else:
            div = [0, 0]
        return div

    def calcul_d1(self):
        if self.__underlying.lower() == "fx":
            rate = self.__r - self.__r_foreign
        else:
            rate = self.__r
        d1 = (np.log((self.__S - self.__div[0]) / self.__K) + (
                rate - self.__div[1] + 0.5 * self.__vol ** 2) * self.__maturity) / (
                     self.__vol * np.sqrt(self.__maturity))
        return d1

    def calcul_d2(self, d1):
        return d1 - self.__vol * np.sqrt(self.__maturity)

    # fonction pour le calcul de proba exercise
    def exercise_probability(self):
        d1 = self.calcul_d1()
        if self.opt_type.lower() == "call":
            return norm.cdf(d1)
        else:
            return norm.cdf(-d1)

    @property
    def price(self):
        d1 = self.calcul_d1()
        d2 = self.calcul_d2(d1)
        # div = [div_disc, div_ cont]
        div_disc = self.__div[0]
        div_cont = self.__div[1]
        if self.opt_type.lower() == "call":
            if self.__underlying.lower() == "fx":
                price = self.__S * np.exp(-self.__r_foreign * self.__maturity) * N(d1) - self.__K * np.exp(
                    -self.__r * self.__maturity) * N(d2)
            else:  # Equity & Index
                price = ((self.__S - div_disc) * np.exp(-div_cont * self.__maturity) * N(d1) -
                         self.__K * np.exp(-self.__r * self.__maturity) * N(d2))

        else:  # "Put"
            if self.__underlying.lower() == "fx":
                price = self.__K * np.exp(-self.__r * self.__maturity) * N(-d2) - self.__S * np.exp(
                    -self.__r_foreign * self.__maturity) * N(-d1)
            else:  # Equity & Index
                price = self.__K * np.exp(-self.__r * self.__maturity) * N(-d2) - (self.__S - div_disc) * np.exp(
                    -div_cont * self.__maturity) * N(-d1)

        price = round(price, 6)
        return price

    def pnl(self, S_T):
        if self.opt_type.lower() == "call":
            payoff = max(S_T - self.__K, 0)
        elif self.opt_type.lower() == "put":
            payoff = max(self.__K - S_T, 0)
        cost = self.price
        return payoff - cost

    def __delta(self):
        d1 = self.calcul_d1()
        if self.opt_type.lower() == "equity":
            if self.opt_type.lower() == "call":
                return N(d1)
            else:
                return N(d1) - 1
        else:
            spot = self.__S
            self.__S = spot * 1.01
            px_h = self.price
            self.__S = spot * 0.99
            px_l = self.price
            self.__S = spot  # remet à l'ancien niveau
            return (px_h - px_l) / (spot * 0.02)

    def __gamma(self):
        if self.opt_type.lower() == "equity":
            d1 = self.calcul_d1()
            return pdf(d1) / (self.__S * self.__vol * np.sqrt(self.__maturity))
        else:
            spot = self.__S
            px = self.price
            self.__S = spot * 1.01
            px_h = self.price
            self.__S = spot * 0.99
            px_l = self.price
            self.__S = spot  # remet à l'ancien niveau
            return (px_h + px_l - 2 * px) / ((spot * 0.01) ** 2)

    def __vega(self):
        if self.opt_type.lower() == "equity":
            d1 = self.calcul_d1()
            return self.__S * pdf(d1) * np.sqrt(self.__maturity)
        vol = self.__vol
        self.__vol = vol * 1.01
        px_h = self.price
        self.__vol = vol * 0.99
        px_l = self.price
        self.__vol = vol  # remet à l'ancien niveau
        return (px_h - px_l) / (vol * 0.02)

    def __theta(self):
        if self.opt_type.lower() == "equity":
            d1 = self.calcul_d1()
            d2 = self.calcul_d2(d1)
            if self.opt_type.lower() == "call":
                return -self.__S * pdf(d1) * self.__vol / (2 * np.sqrt(self.__maturity)) - self.__r * self.__K * np.exp(
                    -self.__r * self.__maturity) * N(d2)
            else:
                return -self.__S * pdf(d1) * self.__vol / (2 * np.sqrt(self.__maturity)) + self.__r * self.__K * np.exp(
                    -self.__r * self.__maturity) * N(-d2)

        else:
            T = self.__maturity
            self.__maturity = T * 1.01
            px_h = self.price
            self.__maturity = T * 0.99
            px_l = self.price
            self.__maturity = T  # remet à l'ancien niveau

            return (px_h - px_l) / (T * 0.02)

    def __rho(self):
        if self.opt_type.lower() == "equity":
            d2 = self.calcul_d2(self.calcul_d1())
            if self.opt_type.lower() == "call":
                return self.__K * self.__maturity * np.exp(-self.__r * self.__maturity) * N(d2)
            else:
                return -self.__K * self.__maturity * np.exp(-self.__r * self.__maturity) * N(-d2)
        else:
            rf = self.__r
            self.__r = rf * 1.01
            px_h = self.price
            self.__r = rf * 0.99
            px_l = self.price
            self.__r = rf  # remet à l'ancien niveau
            return (px_h - px_l) / (rf * 0.02)

    def sensibility(self, sensi):
        if sensi == "delta":
            return self.__delta()
        elif sensi == "gamma":
            return self.__gamma()
        elif sensi == "vega":
            return self.__vega()
        elif sensi == "theta":
            return self.__theta()
        elif sensi == "rho":
            return self.__rho()
        else:
            return "error"

    def stress_scenario(self, new_spot, new_date):
        original_spot = self.__S
        original_maturity = self.__maturity
        self.__S = new_spot
        self.__maturity = new_date
        new_price = self.price
        probability = self.exercise_probability()
        self.__S = original_spot
        self.__maturity = original_maturity
        return new_price, probability