#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from itertools import permutations, combinations, combinations_with_replacement
import re
from random import random, randint

lst_simb_esp = ['`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '{', '}', '|', '[', ']', '\\', ':', '"', ';', '\'', '<', '>', '?', ',', '.', '/', '', ' ']
dicc_letras = {'a':['4','@'], 'i':['1', '!'], 's':['$','5'], 'e':['3'], 'o':['0'], '0':['o'], '1':{'i', '!'}, '4':['a','@'], '$':['5','s'], '5':['$','s'], '@':['a','4'], '!':['i','1'], '3':['e'], 't':'7', '7':'t'}
lst_simbolos = ['*', '_', '-', '.', '']
#lst_simbolos = ['#', '*', '_', '-', '.', '', ' ']

def combinaciones_str(s, comb_simb_lst, prob_list):
    lst = []
    for l in comb_simb_lst[len(s.split()) - 1]:
        x = s
        for simb in l:
            x = x.replace(' ', simb, 1)
        lst.append(x)
    for k in dicc_letras:
        for s in dicc_letras[k]:
            for p in lst:
                if k in p.lower():
                    patron = re.compile(k, re.IGNORECASE)
                    lst.append(patron.sub(s, p))

    contrasenas = lst[:]    
    # Se cambia aleatoriamente alguna letra de acuerdo a dicc_letras por cada palabra
    for prob in prob_list:
        for p in lst:
            np = ''.join(map(lambda x:
                             x if not dicc_letras.get(x, None) or random() >= prob
                             else list(dicc_letras[x])[randint(0, len(dicc_letras[x]) - 1)], p))
            if p != np:
                contrasenas.append(np)
        lst = contrasenas[:]

    # Se cambia aleatoriamente a minúsculas o mayúculas por cada palabra
    for prob in prob_list:
        for p in lst:
            contrasenas.append(''.join(map(lambda x:
                                           x if random() >= prob
                                           else str.swapcase(x), p)))
        lst = contrasenas[:]
    # Insertar de lst_simb_esp aleatoriamente (tentativo)
    # ...
    map(lambda s: contrasenas.append(s.swapcase()), lst)    
    return set(contrasenas)

def escribe_contrasenas(archivo, contrasenas):
    archivo_nuevo = archivo[:archivo.rfind(".")] + "_contrasenas.txt"
    with open(archivo_nuevo, "w") as f:
        map(lambda x: f.write(x + "\n"), contrasenas)
    # print contrasenas    
    print "Se generaron %d contraseñas" % len(contrasenas)

def dicc_constrasenas(archivo):
    f = open(archivo)
    palabras = f.readlines()
    f.close()
    n = 3
    prob_lst = [0.2, 0.5, 0.8]
    palabras = [x[:-1].lower() for x in palabras]
    # Lista de combinaciones de tamaño 0 a n con repetición de la lista de símbolos
    comb_simb_lst = [list(combinations_with_replacement(lst_simbolos, x)) for x in range(0, n)]
    # Lista de tuplas de combinaciones de palabras posibles de 1 a n tamaño
    combinaciones_lst = []
    map(lambda x: map(lambda s: combinaciones_lst.append(s), combinations(palabras, x)), range(1, n + 1))
    # Lista de permutaciones posibles para cada tupla de la lista de combinaciones
    permutaciones_lst = []
    map(lambda l: map(lambda x: permutaciones_lst.append(' '.join(x)), permutations(l)), combinaciones_lst)
    # Lista de contraseñas posibles por cada permutación
    contrasenas_lst = []
    map(lambda s: map(lambda x: contrasenas_lst.append(x), combinaciones_str(s, comb_simb_lst, prob_lst)), permutaciones_lst)
    return contrasenas_lst
    
if len(sys.argv) > 1:
    archivo = sys.argv[1]
    escribe_contrasenas(archivo, dicc_constrasenas(archivo))
else:
    print "Uso: python tarea3.py <archivo.txt>"
