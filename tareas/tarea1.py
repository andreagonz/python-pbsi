#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def palindromo_mas_grande(cadena):
    """
    Regresa la subcadena de la cadena recibida
    que tiene la longitud más larga y es palíndromo.
    Recibe:
        cadena (str) - Cadena de la que se extrae el palíndromo más grande
    Regresa:
        str - Palíndromo encontrado
    """
    cadena = cadena.replace(" ", "").upper()
    if not cadena:
        return ""
    lst = [cadena[i:j]
           for i in range(len(cadena))
           for j in range(i + 1, len(cadena) + 1)
           if cadena[i:j] == cadena[i:j][::-1]]
    return max(lst, key=len)

def es_primo(n):
    """
    Dice si un número es primo.
    Recibe:
        n (int) - Número a decidir si es primo
    Regresa:
        bool - True si n es primo, False en caso contrario
    """
    if n < 2:
        return False
    for x in range(int(math.sqrt(n)), 1, -1):
        if n % x == 0:
            return False
    return True

def primo_lst_aux(n, i, lst):
    """
    Función auxiliar recursiva para primo_lst.
    """
    if len(lst) < n:
        if es_primo(i):
            lst.append(i)
        return primo_lst_aux(n, i + 1, lst)
    return lst

def primo_lst(n):
    """
    Regresa una lista con los primeros n números primos.
    Recibe:
        n (int) - Número que define la longitud de la lista
    Regresa:
        list - Lista con los primeros n primos
    """
    return primo_lst_aux(n, 2, [])

s = "Susanita Lava La Tina Vacia"
print "Palíndromo más grande de '%s'" % s
print palindromo_mas_grande("Susanita Lava La Tina Vacia")

n = 50
print "\nPrimeros %d números primos" % n
l =  primo_lst(n)
print l, " Longitud: ", len(l)
