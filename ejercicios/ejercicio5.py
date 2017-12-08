#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-CERT

sistemas = ['angie','juan','jonatan']
op_interna = ['quintero','fernando','yeudiel']
incidentes = ['demian','anduin','diana','victor','vacante']
auditorias = ['juan','fernando','oscar','daniel','gonzalo','cristian','jorge','virgilio']


print (lambda x: map(lambda x:x.upper(),x)) (filter((lambda n: 'i' in n),(lambda a,b,c,d: a + b + c + d)(sistemas,op_interna,incidentes,auditorias)))

#expresion funcional:
# 1) funcion lambda que sume las cuatro listas
# 2) filtre la lista resultante para obtener todos los nombres que tienen una "i"
# 3) convierta a mayusculas el resultado anterior
#UNA SOLA EXPRESION
