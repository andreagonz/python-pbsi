#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-CERT
class Humano(object):
    def __init__(self,nombre,edad,sexo):
        """
        Inicializa los objetos de la clase Humano
        """
        self.nombre = nombre
        self.edad = edad
        self.sexo = sexo

    def juega_videojuegos(self):
        """
        Imprime una cadena
        """
        print 'Soy %s y puedo jugar videojuegos' % (self.nombre)

    def respira(self):
        """
        Imprime una cadena
        """
        print 'Estoy respirando'


class Becario(Humano):
    def __init__(self,nombre,calificacion):
        """
        Metodo que permite inicializar los objetos de la clase Becario
        """
        self.nombre = nombre
        self.calificacion = calificacion
    

    def __str__(self):
        """
        Metodo que permite indicar como imprimir el objeto
        """
        return '%s -> %s' % (self.nombre, self.calificacion)


    def ve_calificacion(self):
        """
        Imprime una cadena dependiendo de la calificacion del objeto
        """
        if self.calificacion < 8: print 'Soy %s y voy mal, debo estudiar mas' % (self.nombre)
        else: print 'Soy %s y voy bien pero aun debo estudiar mucho' % (self.nombre)


    def juega_videojuegos(self):
        """
        Imprime una cadena
        """
        print 'Soy becario y no tengo tiempo de jugar videojuegos'


    #Para usar un metodo de la clase padre, se crea un nuevo metodo que use la palabra "super"
    def juega_videojuegos_vacaciones(self):
        """
        Manda a llamar la funcion juega_videojuegos de la clase padre
        """
        super(Becario, self).juega_videojuegos()


if __name__ == "__main__":
    
    b1 = Becario('Ulises',8)
    b2 = Becario('Antonio',7)

    b1.ve_calificacion()
    b2.ve_calificacion()

    b1.juega_videojuegos()
    b1.juega_videojuegos_vacaciones()
    b1.respira()

    h1 = Humano('Doroteo Arango',21,'Hombre')
    print h1
    print b1
