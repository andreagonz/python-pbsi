import hashlib
import sys
import re
import xml.etree.ElementTree as ET
from datetime import datetime

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

def hosts_puertos(hosts):
    dicc = {}
    for host in hosts:
        for port in host.find("ports").findall("port"):
            if port.find("state").get('state') == "open":
                dicc[port.get('portid')] = dicc.get(port.get('portid'), 0) + 1
    return dicc

def hosts_dominio(hosts):
    return len([host for host in hosts
                if host.find("hostnames") is not None
                and len(host.find("hostnames").findall("hostname")) > 0])

def hosts_servidores(hosts):
    dicc = {}
    apache = re.compile(".*apache.*", re.IGNORECASE)
    nginx = re.compile(".*nginx.*", re.IGNORECASE)
    honeypot = re.compile(".*dionaea.*", re.IGNORECASE)
    for host in hosts:
        puerto80 = next((p for p in host.find("ports").findall("port") if p.get("portid") == "80"
                         and p.find("state").get("state") == "open"), None)
        puerto443 = next((p for p in host.find("ports").findall("port") if p.get("portid") == "443"
                          and p.find("state").get("state") == "open"), None)
        servidor80 = (lambda x: None if x is None else x.find("service").get("product")) (puerto80)
        servidor443 = (lambda x: None if x is None else x.find("service").get("product")) (puerto443)
        servidor = (lambda x, y: y if x is None else x) (servidor80, servidor443) 
        if servidor is not None:
            if apache.match(servidor):
                dicc["apache"] = dicc.get("apache", 0) + 1
            elif nginx.match(servidor):
                dicc["nginx"] = dicc.get("nginx", 0) + 1
            elif honeypot.match(servidor):
                dicc["honeypot"] = dicc.get("honeypot", 0) + 1
    # IDK
    num_servidores = len([host for host in hosts if len([p for p in host.find("ports").findall("port")
                                                         if (p.get("portid") == "80" or p.get("portid") == "443")
                                                         and p.find("state").get("state") == "open"]) > 0])
    dicc["otro"] = num_servidores - dicc.get("apache", 0) - dicc.get("nginx", 0) - dicc.get("honeypot", 0)
    return dicc

def lee_xml(archivo):
    salida =""
    with open(archivo,'r') as f:
        root = ET.fromstring(f.read())
        hosts = root.findall('host')
        prendidos =  hosts_prendidos(hosts)
        puertos_abiertos = hosts_puertos(prendidos)
        servidores = hosts_servidores(prendidos)
        salida += "Hosts prendidos: %d\n" % len(prendidos)
        salida += "Hosts apagados: %d\n" % (len(hosts) - len(prendidos))
        salida += "Hosts con puerto 22 abierto: %d\n" % puertos_abiertos["22"]
        salida += "Hosts con puerto 53 abierto: %d\n" % puertos_abiertos["53"]
        salida += "Hosts con puerto 80 abierto: %d\n" % puertos_abiertos["80"]
        salida += "Hosts con puerto 443 abierto: %d\n" % puertos_abiertos["443"]
        salida += "Hosts con nombre de dominio: %d\n" % hosts_dominio(hosts)
        salida += "Hosts que usan Apache: %d\n" % servidores["apache"]
        salida += "Hosts que usan Nginx: %d\n" % servidores["nginx"]
        salida += "Hosts que usan Dionaea: %d\n" % servidores["honeypot"]
        # DUDA
        salida += "Hosts que usan otro servicio: %d\n" % servidores["otro"]
    return salida
            
def escribe_reporte(archivo, salida):
    archivo_nuevo = archivo[:archivo.rfind(".")] + "_reporte.txt"
    with open(archivo_nuevo,'w') as f:
        f.write(salida)

if __name__ == '__main__':
    archivo = "nmap.xml"
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    salida = "Fecha: %s\n" % datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    salida += hashes(archivo)
    salida += lee_xml(archivo)
    escribe_reporte(archivo, salida)
    print salida    
