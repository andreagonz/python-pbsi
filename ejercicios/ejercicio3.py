#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-CERT
from random import choice

calificacion_alumno = {}
calificaciones = (0,1,2,3,4,5,6,7,8,9,10)
becarios = ['Alonso',
            'Eduardo',
            'Gerardo',
            'Rafael',
            'Antonio',
            'Fernanda',
            'Angel',
            'Itzel',
            'Karina',
            'Esteban',
            'Alan',
            'Samuel',
            'Jose',
            'Guadalupe',
            'Angel',
            'Ulises']

def asigna_calificaciones():
    for b in becarios:
        calificacion_alumno[b] = choice(calificaciones)

def imprime_calificaciones():
    for alumno in calificacion_alumno:
        print '%s tiene %s\n' % (alumno,calificacion_alumno[alumno])

asigna_calificaciones()
imprime_calificaciones()

def aprobados_reprobados():
    reprobados = []
    aprobados = []    
    for alumno in calificacion_alumno:
        if calificacion_alumno[alumno] >= 8:
            aprobados.append(alumno)
        else:
            reprobados.append(alumno)
    return tuple(aprobados), tuple(reprobados)

print aprobados_reprobados()

def promedio():
    p = 0.0
    calificaciones = calificacion_alumno.values()
    for calif in calificaciones:
        p += calif
    return p / len(calificaciones)

print promedio()

def conjunto_calificaciones():
    return set(calificacion_alumno.values())

print conjunto_calificaciones()
