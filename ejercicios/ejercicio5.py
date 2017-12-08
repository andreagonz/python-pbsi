#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-CERT

sistemas = ['angie','juan','jonatan']
op_interna = ['quintero','fernando','yeudiel']
incidentes = ['demian','anduin','diana','victor','vacante']
auditorias = ['juan','fernando','oscar','daniel','gonzalo','cristian','jorge','virgilio']

print (lambda a,b,c,d: map((lambda x:x.upper()), filter((lambda n: 'i' in n), (a + b + c + d)))) (sistemas,op_interna,incidentes,auditorias)

print (lambda a,b,c,d: ','.join(map((lambda x:x.upper()), filter((lambda n: 'i' in n), (a + b + c + d))))) (sistemas,op_interna,incidentes,auditorias)

#expresion funcional:
# 1) funcion lambda que sume las cuatro listas
# 2) filtre la lista resultante para obtener todos los nombres que tienen una "i"
# 3) convierta a mayusculas el resultado anterior
#UNA SOLA EXPRESION
