# Proyecto final para el curso de Programación en Python
Se utilizó `python3` para la realización de este proyecto. Para poder ejecutar el programa se debe tener instalada la última versión disponible del módulo `requests`, lo cual se logra con el siguiente comando:
```
$ pip3 install requests requests[socks] [--upgrade]
```
usando el argumento `--upgrade` si se tiene instalada una versión anterior de este módulo.
El programa permite utilizar un archivo de configuración que debe de tener el siguiente formato:
``` 
[PARAMETROS]
param1 = valor1
param2 = valor2
``` 
En el archivo `config.cnf` se muestra un ejemplo de configuración, con los parámetros permitidos por el programa.
Ejemplo de ejecución del programa:
```
$ python3 proy.py -c config.cnf -s python.org -t -T -r reporte_py.txt
```
El siguiente comando pemite listar todas las opciones disponibles:
```
$ python3 proy.py -h
```
