
class Bond:
    def __init__(self, maturity,rate_curve, taux_coupon, frequence_coupon, face_value=100):
        self.__maturity = maturity
        self.__r = rate_curve.get_rate_for_maturity(self.__maturity)  # taux domestique
        self.__tx_coupon = taux_coupon
        self.__freq_coupon = frequence_coupon
        self.__face_value = face_value
        self.MacDur = 0.0
    
    @property
    def price(self):
        PVCF = 0 # cash_flow cumulative
        sum_PVCF = 0
        if self.__freq_coupon == "semi-annuel":
            t=0.5
            discount_factor = (1 + self.__r)**(-t)
            N = self.__maturity * 2
        elif self.__freq_coupon == "trimestriel":
            t=0.25
            discount_factor = (1 + self.__r)**(-t)
            N = self.__maturity * 2
        else : 
            # sinon on considere que le coupon est payé annuel
            t=1
            discount_factor = (1 + self.__r)**(-t)
            N = self.__maturity
        for i in range(1, N+1):
            PMT = t * self.__tx_coupon * self.__face_value
            PVCF += PMT * (discount_factor**i)
            sum_PVCF += PVCF * t * i
        #ajout de la face_value actualisé à t0
        PVCF += self.__face_value * (discount_factor**N)
        self.MacDur = sum_PVCF / PVCF
        return PVCF
    
    @property
    def Mod_Dur(self):
        # ModDur = MacDur / (1+r)
        return self.MacDur / (1 + self.__r)
    
    @property
    def DV01(self):
        return (self.Mod_Dur * self.price)/10000
        
    def sensibility(self):
        # ici on calcule le DV01 de l'obligation
        taux = self.__r
        # on calcule le prix de l'obligation avec taux +/- 1 bp 
        self.__r = taux + 0.0001
        px_1 = self.price
        self.__r = taux - 0.0001
        px_2 = self.price
        self.__r = taux
        sensi = (px_2 - px_1)/2
        return sensi
    
"""
from RateCurve import RateCurve
rate_curve = RateCurve(curve=[(1, 0.02), (2, 0.025), (3, 0.03)])
test_bond = Bond(10, rate_curve, 0.02,"annual",100)
print(test_bond.sensibility())
print(test_bond.MacDur)
print(test_bond.price)
print(test_bond.Mod_Dur)
print(test_bond.DV01)
"""