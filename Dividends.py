# -*- coding: utf-8 -*-
import numpy as np

class Dividends:
    def __init__(self, div_type, S0, start_date, end_date, rate_curve, structure):
        """
        Initialise la structure des dividendes.

        :param structure: Un dictionnaire ou une liste de tuples (maturity, dividend rate)
                          représentant la maturité (en années) et le taux de dividende correspondant.
        """
        self.__div_type = div_type.lower()
        self.__S0 = S0
        self.__start_date = start_date
        self.__end_date = end_date
        self.__rate_curve = rate_curve
        self.__structure = sorted(structure, key=lambda x: x[0])

    def __get_div_continue(self):
        """
        Retourne le taux de dividende pour une maturité donnée en utilisant l'interpolation linéaire.

        :param maturity: La maturité pour laquelle le taux de dividende est demandé.
        :return: Le taux de dividende interpolé pour la maturité donnée.
        """
        if self.__end_date <= self.__structure[0][0]:
            return self.__structure[0][1]
        elif self.__end_date >= self.__structure[-1][0]:
            return self.__structure[-1][1]

        for i in range(len(self.__structure) - 1):
            if self.__structure[i][0] <= self.__end_date <= self.__structure[i + 1][0]:
                x0, y0 = self.__structure[i]
                x1, y1 = self.__structure[i + 1]
                return y0 + (y1 - y0) * ((self.__end_date - x0) / (x1 - x0))

        raise ValueError("La maturité spécifiée n'est pas dans l'intervalle de la structure des dividendes.")


    def __get_div_discrete(self):
        div = 0
        # si end_date < le 1e dividende, alors on renvoie une liste vide
        if self.__end_date<self.__structure[0][0]:
            return div
        else:
            # pour chaque date de dividende, on evalue s'il est dans la periode du contrat option
            for i in range(0, len(self.__structure)):
                if self.__start_date < self.__structure[i][0] and self.__end_date > self.__structure[i][0]:
                    maturity = (self.__structure[i][0]-self.__start_date).days/365
                    rf = self.__rate_curve.get_rate_for_maturity(maturity)
                    # on cumule les dividendes discretes
                    div += self.__S0 * self.__structure[i][1] * np.exp(-rf*maturity)
            return div

    def dividend_value(self):
        value = [0, 0]
        # value = [disc_value, cont_value]
        if self.__div_type == "continuous":
            value[1] = self.__get_div_continue()
        else:
            value[0] = self.__get_div_discrete()
        return value










