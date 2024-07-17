# -*- coding: utf-8 -*-

from scipy.interpolate import griddata
import numpy as np

class VolatilitySurface:
    def __init__(self, surface):
        """
        Initialise la surface de volatilité.

        :param surface: Un dictionnaire avec des clés (strike, maturité) et des valeurs de volatilité.
                        Les clés sont des tuples représentant la combinaison de strike et de maturité.
                        Les valeurs sont les volatilités correspondantes.
        """
        # On convertit le dictionnaire en une liste de points pour l'interpolation
        # et on sépare les strikes, les maturités, et les volatilités en trois listes distinctes
        self.points = np.array(list(surface.keys()))
        self.values = np.array(list(surface.values()))

    def get_volatility_for_strike_maturity(self, strike, maturity):
        """
        Retourne la volatilité pour une combinaison spécifique de strike et de maturité en utilisant
        une interpolation bidimensionnelle.

        :param strike: Le strike de l'option.
        :param maturity: La maturité de l'option.
        :return: La volatilité interpolée pour le strike et la maturité donnés.
        """
        # On utilise griddata pour l'interpolation bidimensionnelle
        # Le point à interpoler est un tuple (strike, maturité)
        point_to_interpolate = np.array([[strike, maturity]])
        interpolated_value = griddata(self.points, self.values, point_to_interpolate, method='linear')

        # Si l'interpolation échoue (par exemple, si le point est hors de la grille), on utilise 'nearest' :
        # On sélectionne la valeur du point plus proche du point cible.
        if np.isnan(interpolated_value):
            interpolated_value = griddata(self.points, self.values, point_to_interpolate, method='nearest')

        return interpolated_value[0]
