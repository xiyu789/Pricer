# -*- coding: utf-8 -*-

class RateCurve:
    def __init__(self, curve):
        """
        Initialise la courbe de taux.

        :param curve: liste de tuples (maturity, rate) représentant la maturité (en années)
                      et le taux d'intérêt correspondant, triée par maturité
        """
        self.curve = sorted(curve, key=lambda x: x[0])

    def get_rate_for_maturity(self, maturity):
        """
        Retourne le taux d'intérêt pour une maturité donnée en utilisant l'interpolation linéaire.

        :param maturity: La maturité pour laquelle le taux d'intérêt est demandé.
        :return: Le taux d'intérêt interpolé pour la maturité donnée.
        """
        # Si la maturité demandée est en dehors des bornes de la courbe, on retourne le taux le plus proche.
        if maturity <= self.curve[0][0]:
            return self.curve[0][1]
        elif maturity >= self.curve[-1][0]:
            return self.curve[-1][1]

        # On cherche les points entre lesquels interpoler
        for i in range(len(self.curve) - 1):
            if self.curve[i][0] <= maturity <= self.curve[i + 1][0]:
                # Interpolation linéaire : Si la maturité se situe entre deux points connus, 
                # nous effectuons une interpolation linéaire pour estimer le taux. 
                # y = y0 + (y1 - y0) * ((x - x0) / (x1 - x0))
                x0, y0 = self.curve[i]
                x1, y1 = self.curve[i + 1]
                return y0 + (y1 - y0) * ((maturity - x0) / (x1 - x0))

        raise ValueError("La maturité spécifiée n'est pas dans l'intervalle de la courbe de taux.")
        
        