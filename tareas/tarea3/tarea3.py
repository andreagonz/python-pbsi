#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from itertools import permutations, combinations

lst_simb_esp = ['`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '{', '}', '|', '[', ']', '\\', ':', '"', ';', '\'', '<', '>', '?', ',', '.', '/', '', ' ']
dicc_letras = {'a':['4','@'], 'i':['1', '!'], 's':['$','5'], 'e':['3'], 'o':['0']}
lst_simbolos = ['#', '*', '_', '-', '.', '', ' ']
    
def permutaciones_str_lst(lst):
    nueval = []
    for l in lst:
        nueval.append((l + " " + ' '.join([x for x in lst if x != l])).strip())
    return nueval

# Regresa lista de listas de tamaño n con combinaciones posibles de lista de símbolos
def simb_comb_lst(n):
    res = []
    for x in range(1, n + 1):
        res += [x for x in conjunto_potencia(lst_simbolos * n)
                if len(x) == n - 1]
    return res
    
def simb_comb_str(s):
    lst = []
    for l in simb_comb_lst(len(s)):
        ns = s
        for simb in l:
            ns.replace(' ', simb, 1)
        lst.append(ns)
    return lst

def combinaciones_str_lst(lst):
    res = []
    for s in lst:
        res += simb_comb_str(s)
    return res

def escribe_contrasenas(archivo, lst):
    f = open(archivo[:[string.index(".")]] + "_contrasenas.txt", "w")
    for l in lst:
        f.write(l + "\n")
    f.close()

def comb_palabras(lst, n):
    l = []
    for x in range(1, n + 1):
        l += combinations(lst, x)
    return l

def dicc_constrasenas(archivo):
    f = open(archivo)
    lst = f.readlines()
    f.close()
    lst = [x[:-1].lower() for x in lst]
    # Conjunto potencia, lista de listas de cadenas
    cp_lst = comb_palabras(lst, 3)
    # Posibles permutaciones de listas del conjunto potencia, lista de cadenas con palabras
    # separadas por espacios
    lst_permutaciones = []
    for l in cp_lst:
        lst_permutaciones.append(permutaciones_str_lst(l))
    return lst_permutaciones
    # Combinaciones posibles de palabras cambiando letras por otros caracteres, lista de cadenas
    lst_contrasenas = []
    for l in lst_permutaciones:
        lst_contrasenas += combinaciones_str_lst(l)
    return lst_contrasenas

    
if len(sys.argv) > 1:
    print dicc_constrasenas(sys.argv[1])
else:
    print "Uso: python tarea3.py <archivo.txt>"

