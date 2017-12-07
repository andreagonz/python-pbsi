#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

def contrasena_segura_aux(nmin, nmay, ndig, lst):
    """
    Función auxiliar recursiva para contrasena_segura.
    """
    c = None
    if nmin > 0:
        c = chr(random.randint(ord('a'), ord('z')))
        nmin -= 1
    elif nmay > 0:
        c = chr(random.randint(ord('A'), ord('Z')))
        nmay -= 1
    elif ndig > 0:
        c = chr(random.randint(ord('0'), ord('9')))
        ndig -= 1
    if not c is None:
        lst.append(c)
        return contrasena_segura_aux(nmin, nmay, ndig, lst)
    return lst

def contrasena_segura(nmin, nmay, ndig):
    """
    Regresa una cadena con nmin letras minúsculas, nmay letras
    mayúsculas y ndig dígitos.
    Recibe:
        nmin (int) - Número de letras minúsculas
        nmay (int) - Número de letras mayúsculas
        ndig (int) - Número de dígitos
    Regresa:
        str - Cadena con el número de letras y dígitos especificados
    """
    lst = contrasena_segura_aux(nmin, nmay, ndig, [])
    random.shuffle(lst)
    return ''.join(lst)

l = contrasena_segura(10,11,12)
print l
print "Número de letras minúsculas: ", len([x for x in l if  x.isalpha() and x.islower()])
print "Número de letras mayúsculas: ", len([x for x in l if  x.isalpha() and x.isupper()])
print "Número de dígitos: ", len([x for x in l if  x.isdigit()])
