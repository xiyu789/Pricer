
from OptionVanille import OptionVanille

class Spread:
    # self, param_opt: Param_options, K, surface_volatility
    def __init__(self, param_opt, K1, K2, surface_volatility):
        # K1 < K2
        self.__call_K1 = OptionVanille(param_opt, K1, "Call", surface_volatility)
        self.__call_K2 = OptionVanille(param_opt, K2, "Call", surface_volatility)
        self.__put_K1 = OptionVanille(param_opt, K1, "Put", surface_volatility)
        self.__put_K2 = OptionVanille(param_opt, K2, "Put", surface_volatility)
        self.proba_exercise = "NaN"
        
    def call_spread_price(self):  
        # BULL SPREAD = long call K1 et short call K2
        price = round(self.__call_K1.price - self.__call_K2.price, 6)
        return price

    def put_spread_price(self):  
        # BEAR SPREAD = long put K2 et short put K1
        price=round(self.__put_K2.price - self.__put_K1.price, 6)
        return price

    def box_price(self):  
        # long call spread (K1,K2) + long put spread (K1, K2)
        call_spread_price = self.call_spread_price()
        put_spread_price = self.put_spread_price()
        price = round(call_spread_price + put_spread_price, 6)
        return price
    
    def price(self, strategy):
        if strategy.lower() == "call_spread":
            return self.call_spread_price()
        elif strategy.lower() == "put_spread":
            return self.put_spread_price()
        elif strategy.lower() == "box":
            return self.box_price()
        else:
            return "error in strategy"

    def pnl(self, strat, S_T):
        if strat.lower() == "call_spread":
            PNL_val = self.__call_K1.pnl(S_T) - self.__call_K2.pnl(S_T)
        elif strat.lower() == "put_spread":
            PNL_val = self.__put_K2.pnl(S_T) - self.__put_K1.pnl(S_T)
        elif strat.lower() == "box":
            call_spread_pnl = self.__call_K1.pnl(S_T) - self.__call_K2.pnl(S_T)
            put_spread_pnl = self.__put_K2.pnl(S_T) - self.__put_K1.pnl(S_T)
            PNL_val = call_spread_pnl + put_spread_pnl
        else:
            PNL_val = 0
        return PNL_val
    
    
    def sensibility(self, strat, Grecque):
        if strat.lower() == "call_spread":
            sensi = self.__call_K1.sensibility(Grecque) - self.__call_K2.sensibility(Grecque)
        elif strat.lower() == "put_spread":
            sensi = self.__put_K2.sensibility(Grecque) - self.__put_K1.sensibility(Grecque)
        elif strat.lower() == "box":
            sensi = self.__call_K1.sensibility(Grecque) - self.__call_K2.sensibility(Grecque) + self.__put_K2.sensibility(Grecque) - self.__put_K1.sensibility(Grecque)
        else:
            sensi = 0
        return sensi
    
    def stress_scenario(self, strat, new_spot, new_date):
        if strat.lower() == "call_spread":
            valeur = self.__call_K1.stress_scenario(new_spot, new_date)[0] - self.__call_K2.stress_scenario(new_spot, new_date)[0]
        elif strat.lower() == "put_spread":
            valeur = self.__put_K2.stress_scenario(new_spot, new_date)[0] - self.__put_K1.stress_scenario(new_spot, new_date)[0]   
        elif strat.lower() == "box":
            valeur = self.__call_K1.stress_scenario(new_spot, new_date)[0] - self.__call_K2.stress_scenario(new_spot, new_date) + \
                self.__put_K2.stress_scenario(new_spot, new_date)[0] - self.__put_K1.stress_scenario(new_spot, new_date)[0]  
        else:
            valeur = 0
        return valeur
    
    
class SSS: # Straddle + Strips + Straps
    def __init__(self, param_opt, K0, surface_volatility,):
        self.__call_K0 = OptionVanille(param_opt, K0, "Call", surface_volatility)
        self.__put_K0 = OptionVanille(param_opt, K0, "Put", surface_volatility)
        self.proba_exercise = "NaN"

    def straddle_price(self):  # long call K0 + long put K0
        return self.__call_K0.price + self.__put_K0.price

    def strips_price(self):  # long call K0 + 2 * long put K0
        return self.__call_K0.price + self.__put_K0.price * 2

    def straps_price(self):  # 2 * long call K0 + long put K0
        return self.__call_K0.price * 2 + self.__put_K0.price
    
    def price(self, strategy):
        if strategy.lower() == "straddle":
            return self.straddle_price()
        elif strategy.lower() == "strips":
            return self.strips_price()
        elif strategy.lower() == "straps":
            return self.straps_price()
        else:
            return "error in strategy"
    
    def pnl(self, strat, S_T):
        if strat.lower() == "straddle":
            PNL_val = self.__call_K0.pnl(S_T) + self.__put_K0.pnl(S_T)
        elif strat.lower() == "strips":
            PNL_val = self.__call_K0.pnl(S_T) + self.__put_K0.pnl(S_T) * 2
        elif strat.lower() == "straps":
            PNL_val = self.__call_K0.pnl(S_T) * 2 + self.__put_K0.pnl(S_T)
        else:
            PNL_val = 0
        return PNL_val
    
    def sensibility(self, strat, Grecque):
        if strat.lower() == "straddle":
            sensi = self.__call_K0.sensibility(Grecque) - self.__put_K0.sensibility(Grecque)
        elif strat.lower() == "strips":
            sensi = self.__call_K0.sensibility(Grecque) - self.__put_K0.sensibility(Grecque) * 2
        elif strat.lower() == "straps":
            sensi = 2 * self.__call_K0.sensibility(Grecque) - self.__put_K0.sensibility(Grecque)
        else:
            sensi = 0
        return sensi
    
    def stress_scenario(self, strat, new_spot, new_date):
        if strat.lower() == "straddle":
            valeur = self.__call_K0.stress_scenario(new_spot, new_date)[0] - self.__put_K0.stress_scenario(new_spot, new_date)[0]
        elif strat.lower() == "strips":
            valeur = self.__call_K0.stress_scenario(new_spot, new_date)[0] - self.__put_K0.stress_scenario(new_spot, new_date)[0]  * 2
        elif strat.lower() == "straps":
            valeur = 2 * self.__call_K0.stress_scenario(new_spot, new_date)[0] - self.__put_K0.stress_scenario(new_spot, new_date)[0]
        else:
            valeur = 0
        return valeur
    

class Strangle:
    # long put K1 + long call K2
    def __init__(self, param_opt, K1, K2, surface_volatility):
        self.__put_K1 = OptionVanille(param_opt, K1, "Put", surface_volatility)
        self.__call_K2 = OptionVanille(param_opt, K2, "Call", surface_volatility)
        self.proba_exercise = "NaN"

    @property
    def price(self):
        price = round(self.__put_K1.price + self.__call_K2.price, 6)
        return price

    def pnl(self,S_T):
        return self.__put_K1.pnl(S_T) + self.__call_K2.pnl(S_T)

    def sensibility(self, Grecque):
        sensi = self.__put_K1.sensibility(Grecque) + self.__call_K2.sensibility(Grecque)
        return sensi
    
    def stress_scenario(self, new_spot, new_date):
        valeur = self.__put_K1.stress_scenario(new_spot, new_date)[0] + self.__call_K2.stress_scenario(new_spot, new_date)[0]
        return valeur


class Butterfly: 
    # long call K1 + long call K3 - 2 * short call K2
    def __init__(self, param_opt, K1, K2, K3, surface_volatility):
        # K1 < K2
        self.__call_K1 = OptionVanille(param_opt, K1, "Call", surface_volatility)
        self.__call_K2 = OptionVanille(param_opt, K2, "Call", surface_volatility)
        self.__call_K3 = OptionVanille(param_opt, K3, "Call", surface_volatility)
        self.proba_exercise = "NaN"
    
    @property
    def price(self):
        price = round(self.__call_K1.price + self.__call_K3.price - self.__call_K2.price * 2, 6)
        return price

    def pnl(self,S_T):
        return self.__call_K1.pnl(S_T) + self.__call_K3.pnl(S_T) - self.__call_K2.pnl(S_T) * 2

    def sensibility(self, Grecque):
        sensi = self.__call_K1.sensibility(Grecque) - self.__call_K2.sensibility(Grecque) * 2 + self.__call_K3.sensibility(Grecque)
        return sensi
    
    def stress_scenario(self, new_spot, new_date):
        valeur = self.__call_K1.stress_scenario(new_spot, new_date)[0] - self.__call_K2.stress_scenario(new_spot, new_date)[0] * 2 + self.__call_K3.stress_scenario(new_spot, new_date)[0]
        return valeur

