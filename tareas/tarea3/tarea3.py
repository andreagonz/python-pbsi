#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from itertools import permutations, combinations, combinations_with_replacement, chain

lst_simb_esp = ['`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '{', '}', '|', '[', ']', '\\', ':', '"', ';', '\'', '<', '>', '?', ',', '.', '/', '', ' ']
dicc_letras = {'a':['4','@'], 'i':['1', '!'], 's':['$','5'], 'e':['3'], 'o':['0']}
lst_simbolos = ['#', '*', '_', '-', '.', '', ' ']

def combinaciones_str(s, comb_simb_lst):
    lst = []
    for l in comb_simb_lst[len(s.split()) - 1]:
        x = s
        for simb in l:
            x = x.replace(' ', simb, 1)
        lst.append(x)
    return lst

def escribe_contrasenas(archivo, lst):
    archivo_nuevo = archivo[:archivo.rfind(".")] + "_contrasenas.txt"
    # with open(archivo_nuevo, "w") as f:
        # map(lambda x: f.write(x + "\n"), lst)
    print lst
    print "Se generaron %d contraseñas" % len(lst)

def dicc_constrasenas(archivo):
    f = open(archivo)
    palabras = f.readlines()
    f.close()
    n = 3
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
    map(lambda s: map(lambda x: contrasenas_lst.append(x), combinaciones_str(s, comb_simb_lst)), permutaciones_lst)
    return contrasenas_lst
    
if len(sys.argv) > 1:
    archivo = sys.argv[1]
    escribe_contrasenas(archivo, set(dicc_constrasenas(archivo)))
else:
    print "Uso: python tarea3.py <archivo.txt>"
