import numpy as np
from scipy.stats import norm
N = norm.cdf

class BS:
    def __init__(self, S, K, r, vol, ct, mod):
        self.S = S
        self.K = K
        self.r = r
        self.vol = vol
        self.ct = ct
        self.mod = mod
        self.deltaT = self.calculdeltaT()

    def calculdeltaT(self):
        self.deltaT = (self.ct.matu-self.mod.pridate).days/365
        return self.deltaT
    def calcul_d1(self):
        return (np.log(self.S/self.K)+(self.r+self.vol**2/2)*self.deltaT)/(self.vol*np.sqrt(self.deltaT))

    def calcul_d2(self):
        return self.calcul_d1()-self.vol*np.sqrt(self.deltaT)

    def opt_price(self):
        if self.ct.is_call():
            return self.S*N(self.calcul_d1())-self.K*np.exp(-self.r*self.deltaT)*N(self.calcul_d2())
        else:
            return self.K*np.exp(-self.r*self.deltaT)*N(-self.calcul_d2())-self.S*N(-self.calcul_d1())