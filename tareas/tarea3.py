#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from itertools import permutations, combinations, combinations_with_replacement
import re
from random import random, randint

# Diccionario de caracteres cuyo valor representa una lista de los caracteres por los que se puede cambiar
dicc_letras = {'a':['4','@'], 'i':['1', '!'], 's':['$','5'], 'e':['3'], 'o':['0'], '0':['o'], '1':['i', '!'], '4':['a','@'], '$':['5','s'], '5':['$','s'], '@':['a','4'], '!':['i','1'], '3':['e'], 't':['7'], '7':['t']}
# Lista de símbolos a insertar entre la concatenación de palabras
lst_simbolos = ['*', '_', '-', '.', '']
# Lista de probabilidades con las que se modificará un carácter
lst_probabilidades = [0.2, 0.5, 0.8]
# Número máximo de palabras a combinar en una sóla contraseña (si es mayor a 2 salen números extremadamente grandes)
COMB_MAX = 2
    
def aplica_funcion_lst(lst, fun):
    """
    Regresa una lista de cadenas a las que se les aplica la función fun.
    Se utiliza lst_probabilidades para modificar cada carácter en cada palabra con cierta probabilidad.
    Recibe:
        lst (list) - Lista con cadenas a modificar
        fun (function) - Función a aplicar a cada cadena
    Regresa:
        list - Lista de cadenas modificadas
    """
    res = lst[:]
    for p in lst_probabilidades:
        for s in lst:
            t = fun(s, p)
            if s != t:
                res.append(t)
        lst = res[:]
    return res

def cambia_simbolo_str(s, p):
    """
    Modifica cada carácter en la cadena s con probabilidad p, de acuerdo a dicc_letras.
    Recibe:
        s (str) - Cadena a modificar
        p (float) - Probabilidad con la que se modifica cada carácter
    Regresa:
        str - Cadena modificada
    """
    return ''.join(map(lambda x:
                       x if not dicc_letras.get(x, None) or random() >= p
                       else dicc_letras[x][randint(0, len(dicc_letras[x]) - 1)], s))

def cambia_maymin_str(s, p):
    """
    Cambia a minúscula o mayúscula cada carácter en la cadena s, con probabilidad p.
    Recibe:
        s (str) - Cadena a modificar
        p (float) - Probabilidad con la que se modifica cada carácter
    Regresa:
        str - Cadena modificada
    """
    return ''.join(map(lambda x:
                       x if random() >= p
                       else str.swapcase(x), s))

def combinaciones_str(s, comb_simb_lst):
    """
    Regresa un conjunto de palabras generadas a partir de ciertas modificaciones
    posibles realizadas a la cadena s.
    Recibe:
        s (str) - Cadena a utilizar para generar palabras similares
        comb_simb_lst (lst) - Lista de combinaciones de símbolos que se utilizarán para
                                             llenar los posibles espacios en s
    Regresa:
        set - Conjunto de palabras generadas
    """
    lst = []
    for l in comb_simb_lst[len(s.split()) - 1]:
        x = s
        for simb in l:
            x = x.replace(' ', simb, 1)
        lst.append(x)
    for k in dicc_letras:
        patron = re.compile(k, re.IGNORECASE)
        for s in dicc_letras[k]:
            for p in lst:
                if k in p.lower():
                    lst.append(patron.sub(s, p))
    # Se cambia aleatoriamente alguna letra de acuerdo a dicc_letras por cada palabra
    lst = aplica_funcion_lst(lst, cambia_simbolo_str)
    # Se cambia aleatoriamente a minúsculas o mayúculas por cada palabra
    lst = aplica_funcion_lst(lst, cambia_maymin_str)
    return set(lst + [x.swapcase() for x in lst])

def escribe_contrasenas(archivo, contrasenas):
    """
    Escribe la lista de contraseñas recibida en un archivo.
    Recibe:
        archivo (str) - Nombre del archivo a crear
        contrasenas (lst) - Lista de contrasenas a escribir
    Regresa:
        None
    """
    archivo_nuevo = archivo[:archivo.rfind(".")] + "_contrasenas.txt"
    with open(archivo_nuevo, "w") as f:
        map(lambda x: f.write(x + "\n"), contrasenas)
    print "Se generaron %d contraseñas" % len(contrasenas)

def genera_constrasenas(archivo):
    """
    Genera un conjunto de contraseñas posibles a partir de una lista de
    palabras guardadas en el archivo recibido.
    Recibe:
        archivo (str) - Nombre del archivo de contraseñas
    Regresa:
        set - Conjunto de contraseñas posibles
    """
    f = open(archivo)
    palabras = f.readlines()
    f.close()
    palabras = [x[:-1].lower() for x in palabras]
    # Lista de combinaciones de tamaño 0 a COMB_MAX con repetición de la lista de símbolos
    comb_simb_lst = [list(combinations_with_replacement(lst_simbolos, x)) for x in range(0, COMB_MAX)]
    # Lista de tuplas de combinaciones de palabras posibles de 1 a COMB_MAX tamaño
    combinaciones_lst = []
    map(lambda x: map(lambda s: combinaciones_lst.append(s), combinations(palabras, x)), range(1, COMB_MAX + 1))
    # Lista de permutaciones posibles para cada tupla de la lista de combinaciones
    permutaciones_lst = []
    map(lambda l: map(lambda x: permutaciones_lst.append(' '.join(x)), permutations(l)), combinaciones_lst)
    # Lista de contraseñas posibles por cada permutación
    contrasenas_lst = []
    map(lambda s: map(lambda x: contrasenas_lst.append(x), combinaciones_str(s, comb_simb_lst)), permutaciones_lst)
    return set(contrasenas_lst)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        escribe_contrasenas(archivo, genera_constrasenas(archivo))
    else:
        sys.stderr.write("Uso: python tarea3.py <archivo.txt>")
