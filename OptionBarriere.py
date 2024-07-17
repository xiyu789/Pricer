import math
from random import random

class OptionBarrière:
    def __init__(self, S0, T, K, surface_volatility, rate_curve, option_type, barrière_type, barrière, n_simul, steps,
                 dividends):
        self.__S0 = S0
        self.__T = T
        self.__K = K
        self.__surface_volatility = surface_volatility
        self.__rate_curve = rate_curve
        self.__option_type = option_type  # Put/Call
        self.__barrière = barrière
        self.__barrière_type = barrière_type  # KI/KO
        self.__n_simul = n_simul
        self.__steps = steps
        self.__dividends = dividends
        self.__vol = self.__surface_volatility.get_volatility_for_strike_maturity(self.__K, self.__T)
        self.__rate = self.__rate_curve.get_rate_for_maturity(self.__T)
        self.proba_exercise = 0

    # Generate random number
    def box_muller_rand(self):
        while True:
            x = random() * 2.0 - 1
            y = random() * 2.0 - 1
            d = x * x + y * y
            if d < 1:
                return x * math.sqrt(-2 * math.log(d) / d)

    # Generate a path for the underlying
    def __create_path(self):
        dt = self.__T / self.__steps
        sdt = math.sqrt(dt)
        rate = self.__rate_curve.get_rate_for_maturity(self.__T)
        vol = self.__surface_volatility.get_volatility_for_strike_maturity(self.__K, self.__T)
        div_rate = self.__dividends.dividend_value()[1]  # div continue

        path = []
        current = self.__S0
        for i in range(self.__steps):
            path.append(current)
            current = current * math.exp((rate - div_rate - 0.5 * vol ** 2) * dt + vol * sdt * self.box_muller_rand())

        return path

    @property
    # Compute option price
    def price(self):
        sum_payoff = 0
        i = 0  # compter le nombre de fois que le produit soit validé
        for _ in range(self.__n_simul):

            path = self.__create_path()

            # Vérifier si la barrière a été touchée et si elle correspond au type de barrière de l'option
            if (self.__barrière_type == "KI" and self.__barrière > self.__S0 and max(path) <= self.__barrière):
                payoff_option = 0
            elif (self.__barrière_type == "KI" and self.__barrière < self.__S0 and min(path) > self.__barrière):
                payoff_option = 0
            elif (self.__barrière_type == "KO" and self.__barrière < self.__S0 and min(path) <= self.__barrière):
                payoff_option = 0
            elif (self.__barrière_type == "KO" and self.__barrière > self.__S0 and max(path) > self.__barrière):
                payoff_option = 0
            elif self.__option_type.lower() == "call":
                payoff_option = max(path[-1] - self.__K, 0)
                i += 1
            elif self.__option_type.lower() == "put":
                payoff_option = max(self.__K - path[-1], 0)
                i += 1

            sum_payoff += payoff_option
        # Calculer le prix moyen en fonction des simulations
        self.proba_exercise = i / self.__n_simul
        prix = sum_payoff / self.__n_simul * math.exp(-self.__rate * self.__T)

        return prix

    def __delta(self):
        spot = self.__S0
        self.__S0 = spot * 1.01
        px_h = self.price
        self.__S0 = spot * 0.99
        px_l = self.price
        self.__S0 = spot  # remet à l'ancien niveau
        return (px_h - px_l) / (spot * 0.02)

    def __gamma(self):
        spot = self.__S0
        px = self.price
        self.__S0 = spot * 1.01
        px_h = self.price
        self.__S0 = spot * 0.99
        px_l = self.price
        self.__S0 = spot  # remet à l'ancien niveau
        return (px_h + px_l - 2 * px) / ((spot * 0.01) ** 2)

    def __vega(self):
        vol = self.__vol
        self.__vol = vol * 1.01
        px_h = self.price
        self.__vol = vol * 0.99
        px_l = self.price
        self.__vol = vol  # remet à l'ancien niveau
        return (px_h - px_l) / (vol * 0.02)

    def __theta(self):
        T = self.__T
        self.__T = T * 1.01
        px_h = self.price
        self.__T = T * 0.99
        px_l = self.price
        self.__T = T  # remet à l'ancien niveau
        return (px_h - px_l) / (T * 0.02)

    def __rho(self):
        rf = self.__rate
        self.__rate = rf * 1.01
        px_h = self.price
        self.__rate = rf * 0.99
        px_l = self.price
        self.__rate = rf  # remet à l'ancien niveau
        return (px_h - px_l) / (rf * 0.02)

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

    def stress_scenario(self, new_spot, new_date):
        original_spot = self.__S0
        original_maturity = self.__T
        self.__S0 = new_spot
        self.__T = new_date
        new_price = self.price
        probability = self.proba_exercise
        self.__S0 = original_spot
        self.__T = original_maturity
        return new_price, probability

