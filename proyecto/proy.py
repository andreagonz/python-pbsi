import sys
import re
import optparse
import requests
import configparser
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
    parser.add_option('-c','--config', dest='config', default=None, help='File where the results will be reported, if not specified, results will default to standad output. In combination with -o, it will also print results to standard output.')
    parser.add_option('-C','--cabeceras', dest='cabeceras', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-H','--metodos-http', dest='metodos', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-m','--correos', dest='correos', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-p','--puerto', dest='puerto', type='int',  default=-1, help='Port that the HTTP server is listening to.')
    parser.add_option('-s','--servidor', dest='servidor', default=None, help='Host that will be attacked.')
    parser.add_option('-r','--reporte', dest='reporte', default=None, help='File where the results will be reported, if not specified, results will default to standad output. In combination with -o, it will also print results to standard output.')
    parser.add_option('-a','--agente', dest='agente', default=None, help='File where the results will be reported, if not specified, results will default to standad output. In combination with -o, it will also print results to standard output.')
    parser.add_option('-A','--archivos-sensibles', dest='archivos', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-M','--cms', dest='cms', default=False, action='store_true', help='If specified, prints detailed information during execution.')
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
    
def escribe_reporte(archivo, verboso):
    """
    Realiza un reporte con los resultados obtenidos, los imprime en la salida estándar o ambos.
    Recibe:
        resultados (str) - Cadena con el reporte
        archivo (str) - Nombre del archivo a crear con el reporte
        stdout (bool) - De ser True, se imprime resultados en salida estándar
    Regresa:
        None
    """
    reporta('Escribiendo reporte en archivo %s' % archivo, verboso)
    try:
        with open(archivo, "w") as f:
            f.write('\n'.join(reporte))
    except:
        error('Hubo un error al escribir reporte en el archivo %s' % archivo)

def genera_url(servidor, puerto, tls, verboso):
    """
    Regresa una cadena del url con la dirección IP, puerto y protocolos específicados.
    Recibe:
        server (str) - Dirección IP del servidor
        port (str) - Puerto a utilizar
        protocol (str) - Protocolo a utilizar
    Regresa:
        str - URL generada
    """
    reporta('Generando URL', verboso)
    protocolo = 'https' if tls else 'http'
    if '/' in servidor:
        i = servidor.index('/')
        return '%s://%s:%d%s' % (protocolo, servidor[:i], puerto, servidor[i:])
    return '%s://%s:%s' % (protocolo, servidor, puerto)

def hacer_peticion(host, sesion, agente, verboso):
    try:
        reporta('Haciendo petición con método GET al servidor', verboso)
        if agente is not None:
            reporta('Usando agente de usuario %s' % agente, verboso)
            headers = {'User-Agent': agente}
            return sesion.get(host, headers=headers)
        return sesion.get(host)
    except ConnectionError:
        error('Error en la conexion, tal vez el servidor no esta arriba.',True)
    return None

def ip_origen(sesion, verboso):
    reporta('Obteniendo dirección IP origen', verboso)
    return sesion.get('http://myexternalip.com/raw').text[:-1]

def elemento_cebecera(peticion, llave, verboso):
    reporta("Extrayendo elemento '%s' de cabecera de petición" % llave, verboso)
    return peticion.headers.get(llave, "N/A")

def obten_sesion(tor, verboso):
    """
    Regresa una sesión
    """
    if not tor:
        return requests
    reporta('Creando sesión a través de TOR', verboso)
    sesion = requests.session()
    sesion.proxies = {'http':  'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
    return sesion

def metodos_http(host, sesion, verboso):
    metodos = []
    reporta('Se intentará obtener métodos permitidos por fuerza bruta', verboso)
    metodos.append("GET")
    reporta('Realizando petición con método HEAD', verboso)
    if sesion.head(host).status_code < 400:
        metodos.append("HEAD")
    reporta('Realizando petición con método POST', verboso)
    if sesion.post(host).status_code < 400:
        metodos.append("POST")
    reporta('Realizando petición con método PUT', verboso)
    if sesion.put(host).status_code < 400:
        metodos.append("PUT")
    reporta('Realizando petición con método DELETE', verboso)
    if sesion.delete(host).status_code < 400:
        metodos.append("DELETE")
    reporta('Realizando petición con método OPTIONS', verboso)
    if sesion.options(host).status_code < 400:
        metodos.append("OPTIONS")
    reporta('Realizando petición con método PATCH', verboso)
    if sesion.patch(host).status_code < 400:
        metodos.append("PATCH")
    return metodos

def obten_cms(peticion, verboso):
    reporta('Obteniendo Content Management Service', verboso)
    tree = html.fromstring(peticion.content)
    cms = tree.xpath("//meta[@name='generator']")
    if len(cms) > 0:
        return cms[0].get('content')
    else:
        return "N/A"
    
def obten_metodos(host, sesion, verboso):
    reporta('Obteniendo métodos HTTP permitidos', verboso)
    metodos = sesion.options(host).headers.get("Allow", None)
    if metodos is None:
        reporta('No se pudo extraer métodos permitidos usando OPTIONS', verboso)
        metodos = ','.join(metodos_http(host, sesion, verboso))
    return metodos

def obten_correos(peticion, verboso):
    correo_regexp = r"[a-zA-Z0-9.!#$%&’*+/=?^_`|~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*"
    reporta('Obteniendo correos en el contenido de la petición realizada', verboso)
    return re.findall(correo_regexp, peticion.text)

def obten_bool(atributo, conf, op):
    if op:
        return op
    res = False
    try:
        res = conf.getboolean(atributo, fallback=False)
    except:
        error("El parámetro '%s' del archivo de configuración debe de ser un valor booleano" % atributo, True)
    return res
        
def obten_valores(ops, conf):
    valores = {}
    valores['reporte'] = ops.reporte if ops.reporte is not None else conf.get('reporte', 'reporte.txt')
    valores['agente'] = ops.agente if ops.agente is not None else conf.get('agente_usuario', None)
    valores['servidor'] = ops.servidor if ops.servidor is not None else conf.get('servidor', None)
    valores['verboso'] = obten_bool('modo_verboso', conf, ops.verboso)
    valores['cabeceras'] = obten_bool('cabeceras', conf, ops.cabeceras)
    valores['metodos'] = obten_bool('metodos_http', conf, ops.metodos)
    valores['correos'] = obten_bool('correos', conf, ops.correos)
    valores['archivos'] = obten_bool('archivos_sensibles', conf, ops.archivos)
    valores['cms'] = obten_bool('cms', conf, ops.cms)
    valores['tor'] = obten_bool('tor', conf, ops.tor)
    valores['tls'] = obten_bool('tls', conf, ops.tls)    
    valores['puerto'] = ops.puerto if ops.puerto >= 0 else conf.getint('puerto', -1)
    if valores['puerto'] < 0 or valores['puerto'] > 49151:
        valores['puerto'] = 443 if valores['tls'] else 80
    return valores

def leer_configuracion(archivo):
    res = {}
    try:
        config = configparser.ConfigParser()
        config.read(archivo)
        res = config['PARAMETROS']
    except:
        error("Hubo un problema al leer el archivo de configuración", True)
    return res
    
if __name__ == '__main__':
    try:
        ops = opciones()
        config = {} if ops.config is None else leer_configuracion(ops.config)
        valores = obten_valores(ops, config)
        revisa_valores(valores)
        sesion = obten_sesion(valores['tor'], valores['verboso'])
        url = genera_url(valores['servidor'], valores['puerto'], valores['tls'], valores['verboso'])
        ip = "Dirección IP origen: %s" % ip_origen(sesion, valores['verboso'])
        reporta(ip, valores['verboso'], True)
        urld = "URL destino: %s" % url
        reporta(urld, valores['verboso'], True)
        peticion = hacer_peticion(url, sesion, valores['agente'], valores['verboso'])
        if valores['cabeceras']:
            serv = "Versión servidor: %s" % elemento_cebecera(peticion, "Server", valores['verboso'])
            reporta(serv, valores['verboso'], True)
            php = "Versión PHP: %s" % elemento_cebecera(peticion, "X-Powered-By", valores['verboso'])
            reporta(php, valores['verboso'], True)
        if valores['metodos']:
            http = "Métodos HTTP permitidos: %s" % obten_metodos(url, sesion, valores['verboso'])
            reporta(http, valores['verboso'], True)
        if valores['cms']:
            cms = "Content Managment Service: %s" % obten_cms(peticion, valores['verboso'])
            reporta(cms, valores['verboso'], True)
        if valores['correos']:
            correos = "Correos encontrados: %s" % ', '.join(obten_correos(peticion, valores['verboso']))
            reporta(correos, valores['verboso'], True)
        escribe_reporte(valores['reporte'], valores['verboso'])
    except Exception as e:
        error('Ocurrió un error inesperado')
        error(e, True)

