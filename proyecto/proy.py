import sys
import re
import optparse
import requests
from lxml import html
from requests.exceptions import ConnectionError

reporte = []

def error(msg, exit=False):
    """
    Imprime msg en la salida de errores, termina el programa si se le indica.
    Recibe:
        msg (str) - Mensaje a imprimir
        exit (bool) - Se termina el programa syss es True
    Regresa:
        None
    """
    sys.stderr.write('Error:\t%s\n' % msg)
    if exit:
        sys.exit(1)

def reporta(msg, verboso, reporta=False):
    if verboso:
        print(msg)
    if reporta:
        reporte.append(msg)
        
def opciones():
    """
    Regresa un objeto que permite leer argumentos ingresados al ejecutar el programa.
    Regresa:
        optparse.OptionParser - Objeto analizador de argumentos
    """
    parser = optparse.OptionParser()
    parser.add_option('-v','--verboso', dest='verboso', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-c','--cabeceras', dest='cabeceras', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-H','--metodos-http', dest='metodos', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-C','--correos', dest='correos', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-p','--puerto', dest='puerto', type='int',  default=-1, help='Port that the HTTP server is listening to.')
    parser.add_option('-s','--servidor', dest='servidor', default=None, help='Host that will be attacked.')
    parser.add_option('-r','--reporte', dest='reporte', default=None, help='File where the results will be reported, if not specified, results will default to standad output. In combination with -o, it will also print results to standard output.')
    parser.add_option('-a','--agente', dest='agente', default=None, help='File where the results will be reported, if not specified, results will default to standad output. In combination with -o, it will also print results to standard output.')
    parser.add_option('-A','--archivos-sensibles', dest='archivos', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-t','--tls', dest='tls', default=False, action='store_true', help='If specified, HTTPS protocol will be used instead of default HTTP.')
    parser.add_option('-T','--tor', dest='tor', default=False, action='store_true', help='If specified, requests will be done over TOR.')
    opts, args = parser.parse_args()
    return opts
    
def revisa_valores(valores):
    """
    Revisa si hay algún error con las opciones recibidas.
    Recibe:
        options (optparse.OptionParser) - Objeto con opciones ingresadas al ejecutar programa
    Regresa:
        None
    """
    if valores['servidor'] is None:
        error('Se debe especificar un servidor.', True)
    
def escribe_reporte(archivo):
    """
    Realiza un reporte con los resultados obtenidos, los imprime en la salida estándar o ambos.
    Recibe:
        resultados (str) - Cadena con el reporte
        archivo (str) - Nombre del archivo a crear con el reporte
        stdout (bool) - De ser True, se imprime resultados en salida estándar
    Regresa:
        None
    """
    with open(archivo, "w") as f:
        f.write('\n'.join(reporte))

def genera_url(servidor, puerto, tls):
    """
    Regresa una cadena del url con la dirección IP, puerto y protocolos específicados.
    Recibe:
        server (str) - Dirección IP del servidor
        port (str) - Puerto a utilizar
        protocol (str) - Protocolo a utilizar
    Regresa:
        str - URL generada
    """
    protocolo = 'https' if tls else 'http'
    if '/' in servidor:
        i = servidor.index('/')
        return '%s://%s:%d%s' % (protocolo, servidor[:i], puerto, servidor[i:])
    return '%s://%s:%s' % (protocolo, servidor, puerto)

def hacer_peticion(host, sesion, agente):
    try:
        if agente is not None:
            headers = {'User-Agent': agente}
            return sesion.get(host, headers=headers)
        return sesion.get(host)
    except ConnectionError:
        error('Error en la conexion, tal vez el servidor no esta arriba.',True)
    return None

def ip_origen(sesion):
    return sesion.get('http://myexternalip.com/raw').text[:-1]

def elemento_cabezera(peticion, llave):
    return peticion.headers.get(llave, "N/A")

def obten_sesion(tor):
    """
    Regresa una sesión
    """
    if not tor:
        return requests
    sesion = requests.session()
    sesion.proxies = {'http':  'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
    return sesion

def metodos_http(host, sesion):
    metodos = []
    if sesion.get(host).status_code < 400:
        metodos.append("GET")
    if sesion.head(host).status_code < 400:
        metodos.append("HEAD")
    if sesion.post(host).status_code < 400:
        metodos.append("POST")
    if sesion.put(host).status_code < 400:
        metodos.append("PUT")
    if sesion.delete(host).status_code < 400:
        metodos.append("DELETE")
    if sesion.options(host).status_code < 400:
        metodos.append("OPTIONS")
    if sesion.patch(host).status_code < 400:
        metodos.append("PATCH")
    return metodos

def obten_cms(peticion):
    tree = html.fromstring(peticion.content)
    cms = tree.xpath("//meta[@name='generator']")
    if len(cms) > 0:
        return cms[0].get('content')
    else:
        return "N/A"
    
def obten_metodos(host, sesion):
    metodos = sesion.options(host).headers.get("Allow", None)
    if metodos is None:
        metodos = ','.join(metodos_http(host, sesion))
    return metodos

def obten_correos(peticion):
    correo_regexp = r"[a-zA-Z0-9.!#$%&’*+/=?^_`|~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*"
    return re.findall(correo_regexp, peticion.text)
    
def obten_valores(conf):
    valores = {}
    ops = opciones()
    valores['reporte'] = ops.reporte if ops.reporte is not None else conf.get('reporte', 'reporte.txt')
    valores['agente'] = ops.agente if ops.agente is not None else conf.get('agente', None)
    valores['servidor'] = ops.servidor if ops.servidor is not None else conf.get('servidor', None)
    valores['tls'] = conf['tls'] if conf.get('tls', None) is not None else ops.tls
    if ops.tls:
        valores['tls'] = ops.tls
    valores['puerto'] = ops.puerto if ops.puerto else conf.get('puerto', -1)
    if valores['puerto'] < 0 or valores['puerto'] > 49151:
        valores['puerto'] = 443 if valores['tls'] else 80
    valores['tor'] = conf['tor'] if conf.get('tor', None) is not None else ops.tor
    if ops.tor:
        valores['tor'] = ops.tor
    valores['verboso'] = conf['verboso'] if conf.get('verboso', None) is not None else ops.verboso
    if ops.verboso:
        valores['verboso'] = ops.verboso
    valores['cabeceras'] = conf['cabeceras'] if conf.get('cabeceras', None) is not None else ops.cabeceras
    if ops.cabeceras:
        valores['cabeceras'] = ops.cabeceras
    valores['metodos'] = conf['metodos'] if conf.get('metodos', None) is not None else ops.metodos
    if ops.metodos:
        valores['metodos'] = ops.metodos
    valores['correos'] = conf['correos'] if conf.get('correos', None) is not None else ops.correos
    if ops.correos:
        valores['correos'] = ops.correos
    valores['archivos'] = conf['archivos'] if conf.get('archivos', None) is not None else ops.archivos
    if ops.archivos:
        valores['archivos'] = ops.archivos
    return valores
            
if __name__ == '__main__':
    try:
        valores = obten_valores({})
        revisa_valores(valores)
        sesion = obten_sesion(valores['tor'])
        url = genera_url(valores['servidor'], valores['puerto'], valores['tls'])
        ip = "Dirección IP origen: %s" % ip_origen(sesion)
        reporta(ip, valores['verboso'], True)
        urld = "URL destino: %s" % url
        reporta(urld, valores['verboso'], True)
        peticion = hacer_peticion(url, sesion, valores['agente'])
        serv = "Versión servidor: %s" % elemento_cabezera(peticion, "Server")
        reporta(serv, valores['verboso'], True)
        php = "Versión PHP: %s" % elemento_cabezera(peticion, "X-Powered-By")
        reporta(php, valores['verboso'], True)
        http = "Métodos HTTP permitidos: %s" % obten_metodos(url, sesion)
        reporta(http, valores['verboso'], True)
        cms = "Content Managment Service: %s" % obten_cms(peticion)
        reporta(cms, valores['verboso'], True)
        correos = "Correos encontrados: %s" % ', '.join(obten_correos(peticion))
        reporta(correos, valores['verboso'], True)
        escribe_reporte(valores['reporte'])
    except Exception as e:
        error('Ocurrió un error inesperado')
        error(e, True)

