#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import sys
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import matplotlib.pyplot as plt

def hashes(archivo):
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    with open(archivo, 'rb') as f:
        s = f.read(BUF_SIZE)
        while s:
            md5.update(s)
            sha1.update(s)
            s = f.read(BUF_SIZE)
    salida = "MD5: %s\n" % md5.hexdigest()
    salida += "SHA1: %s\n" % sha1.hexdigest()
    return salida

def hosts_prendidos(hosts):
    return [x for x in hosts if x.find('status').get('state') == "up"]

def hosts_apagados(hosts):
    return [x for x in hosts if x.find('status').get('state') == "down"]

def puerto22_abierto(host):
    for port in host.find("ports").findall("port"):
        if port.get('portid') == "22" and port.find("state").get('state') == "open":
            return True
    return False
        
def hosts_puerto22(hosts):    
    return [x for x in hosts if puerto22_abierto(x)]

def hosts_puertos(hosts):
    dicc = {}
    for host in hosts:
        for port in host.find("ports").findall("port"):
            if port.find("state").get('state') == "open":
                dicc[port.get('portid')] = dicc.get(port.get('portid'), 0) + 1
    return dicc

def hosts_dominio(hosts):
    return [host for host in hosts
                if host.find("hostnames") is not None
                and len(host.find("hostnames").findall("hostname")) > 0]

def hosts_servidores(hosts):
    l = []
    for host in hosts:
        puerto80 = next((p for p in host.find("ports").findall("port") if p.get("portid") == "80"
                         and p.find("state").get("state") == "open"), None)
        puerto443 = next((p for p in host.find("ports").findall("port") if p.get("portid") == "443"
                          and p.find("state").get("state") == "open"), None)
        servidor80 = (lambda x: None if x is None else x.find("service")) (puerto80)
        servidor443 = (lambda x: None if x is None else x.find("service")) (puerto443)
        servidor = (lambda x, y: y if x is None else x) (servidor80, servidor443) 
        if servidor is not None:
            l.append((host, servidor))
    return l

def hosts_servidor(servidores, regexp):
    return [x[0] for x in servidores
            if x[1].get("product") and regexp.match(x[1].get("product"))]

def dicc_servidores(hosts):
    dicc = {}
    apache = re.compile(".*apache.*", re.IGNORECASE)
    nginx = re.compile(".*nginx.*", re.IGNORECASE)
    honeypot = re.compile(".*dionaea.*", re.IGNORECASE)
    servidores = hosts_servidores(hosts)
    dicc["apache"] = len(hosts_servidor(servidores, apache))
    dicc["nginx"] = len(hosts_servidor(servidores, nginx))
    dicc["honeypot"] = len(hosts_servidor(servidores, honeypot))
    # Número de hosts en los que se detectó un servidor http que no
    # entra en las categorías anteriores                
    dicc["otro"] = len(servidores) - dicc["apache"] - dicc["nginx"] - dicc["honeypot"]
    return dicc

def hosts(archivo):
    with open(archivo,'r') as f:
        root = ET.fromstring(f.read())
        return root.findall('host')
    
def genera_reporte(hosts):
    salida =""
    prendidos =  hosts_prendidos(hosts)
    puertos_abiertos = hosts_puertos(prendidos)
    servidores = dicc_servidores(prendidos)
    salida += "Hosts prendidos: %d\n" % len(prendidos)
    salida += "Hosts apagados: %d\n" % (len(hosts) - len(prendidos))
    salida += "Hosts con puerto 22 abierto: %d\n" % puertos_abiertos["22"]
    salida += "Hosts con puerto 53 abierto: %d\n" % puertos_abiertos["53"]
    salida += "Hosts con puerto 80 abierto: %d\n" % puertos_abiertos["80"]
    salida += "Hosts con puerto 443 abierto: %d\n" % puertos_abiertos["443"]
    salida += "Hosts con nombre de dominio: %d\n" % len(hosts_dominio(hosts))
    salida += "Hosts que usan Apache: %d\n" % servidores["apache"]
    salida += "Hosts que usan Nginx: %d\n" % servidores["nginx"]
    salida += "Hosts que usan Dionaea: %d\n" % servidores["honeypot"]
    salida += "Hosts que usan otro servicio: %d\n" % servidores["otro"]
    grafica(servidores)
    return salida
            
def escribe_reporte(archivo, salida):
    with open(archivo,'w') as f:
        f.write(salida)

def genera_csv(nombre, atributo, hosts):
    csv = atributo + ",\n"
    for host in hosts:
        csv += host.find("address").get("addr")  + ",\n"
    escribe_reporte(nombre, csv[:-2])
    
def archivos_csv(hosts):
    prendidos = hosts_prendidos(hosts)
    honeypot = re.compile(".*dionaea.*", re.IGNORECASE)
    servidores = hosts_servidores(prendidos)
    genera_csv("hosts_apagados.csv", "HostApagado", hosts_apagados(hosts))
    genera_csv("hosts_prendidos.csv", "HostPrendido", prendidos)
    genera_csv("hosts_puerto22.csv", "HostPuerto22Abierto", hosts_puerto22(prendidos))
    genera_csv("hosts_honeypot.csv", "HostHoneypot", hosts_servidor(servidores, honeypot))
    genera_csv("hosts_dominio.csv", "HostConNombreDominio", hosts_dominio(hosts))

def grafica(dicc):
    labels = 'Apache', 'Nginx', 'Honeypot', 'Otro'
    sizes = [dicc["apache"], dicc["nginx"], dicc["honeypot"], dicc["otro"]]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    plt.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140) 
    plt.axis('equal')
    plt.title('Porcentaje de Servidores Web')
    plt.savefig('grafica.svg')
    
if __name__ == '__main__':
    archivo = "nmap.xml"
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    hosts = hosts(archivo)
    salida = "Fecha: %s\n" % datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    salida += hashes(archivo)
    salida += genera_reporte(hosts)
    escribe_reporte("reporte.txt", salida)
    archivos_csv(hosts)
    print salida
