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
    """
    Permite decidir si msg se va a imprimir en la salida estándar y si
    se va a incluir en el reporte.
    Recibe:
        msg (str) - Mensaje a imprimir
        verboso (bool) - Si es True, imprime msg en salida estándar.
        reporta (bool) - Si es True, se guarda msg en la lista reporte
    Regresa:
        None
    """
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
    parser.add_option('-v','--verboso', dest='verboso', default=False, action='store_true', help='Bandera que de ser usada, permite que se imprima en salida estándar información referente a la ejecución del programa.')
    parser.add_option('-c','--config', dest='config', default=None, help='Archivo de configuración.')
    parser.add_option('-C','--cabeceras', dest='cabeceras', default=False, action='store_true', help='Bandera que indica que se obtenga la versión del servidor y de PHP de la cabecera.')
    parser.add_option('-H','--metodos-http', dest='metodos', default=False, action='store_true', help='Bandera que indica que se determine los métodos HTTP habilitados en el servidor.')
    parser.add_option('-m','--correos', dest='correos', default=False, action='store_true', help='Bandera que indica que se extraiga la lista de correos del contenido.')
    parser.add_option('-p','--puerto', dest='puerto', type='int',  default=-1, help='Puerto al que se realizarán las peticiones, de no ser especificado de utilizará el puerto 80, o el 443 en caso de utilizar -t.')
    parser.add_option('-s','--servidor', dest='servidor', default=None, help='Servidor a ser analizado.')
    parser.add_option('-r','--reporte', dest='reporte', default=None, help='Archivo en donde serán registrados los resultados obtenidos del análisis.')
    parser.add_option('-a','--agente-usuario', dest='agente', default=None, help='Agente de usuario a ser utilizado para las peticiones.')
    parser.add_option('-A','--archivos-sensibles', dest='archivos', default=None, help='De ser especificado se hará una búsqueda en el servidor de los archivos listados en este archivo.')
    parser.add_option('-M','--cms', dest='cms', default=False, action='store_true', help='Bandera que indica que se obtenga el CMS utilizado por el servidor.')
    parser.add_option('-t','--tls', dest='tls', default=False, action='store_true', help='Bandera que indica que se utilice el protocolo HTTPS en vez de HTTP.')
    parser.add_option('-T','--tor', dest='tor', default=False, action='store_true', help='Bandera que indica que se realicen las peticiones a través de TOR.')
    opts, args = parser.parse_args()
    return opts
    
def revisa_valores(valores):
    """
    Revisa si hay algún error en los valores recibidos.
    Recibe:
        valores (dict) - Diccionario con los valores a ser utilizados
    Regresa:
        None
    """
    if valores['servidor'] is None:
        error('Se debe especificar un servidor.', True)
    
def escribe_reporte(archivo, verboso):
    """
    Guarda el reporte en un archivo.
    Recibe:
        archivo (str) - Nombre del archivo a crear con el reporte
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        None
    """
    reporta('Escribiendo reporte en archivo %s' % archivo, verboso)
    try:
        with open(archivo, "w") as f:
            f.write('\n'.join(reporte) + "\n")
    except:
        error('Hubo un error al escribir reporte en el archivo %s' % archivo)

def genera_url(servidor, puerto, tls, verboso):
    """
    Regresa una cadena del url con la dirección IP, puerto y protocolos específicados.
    Recibe:
        servidor (str) - Dirección IP del servidor
        puerto (str) - Puerto a utilizar
        tls (str) - De ser True se utilizará el protocolo HTTPS en ves de HTTP
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        str - URL generada
    """
    reporta('Generando URL', verboso)
    protocolo = 'https' if tls else 'http'
    if '/' in servidor:
        i = servidor.index('/')
        return '%s://%s:%d%s' % (protocolo, servidor[:i], puerto, servidor[i:])
    return '%s://%s:%s' % (protocolo, servidor, puerto)

def hacer_peticion(url, sesion, agente, verboso):
    """
    Hace una petición al servidor.
    Recibe:
        url (str) - URL a la cuál se hace la petición
        sesion (requests.session) - Sesión a utilizar
        agente (str) - Agente de usuario a utilizar
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        requests.models.Response - Respuesta a la petición
    """
    try:
        reporta('Haciendo petición con método GET al servidor', verboso)
        if agente is not None:
            reporta('Usando agente de usuario %s' % agente, verboso)
            headers = {'User-Agent': agente}
            return sesion.get(url, headers=headers)
        return sesion.get(url)
    except ConnectionError:
        error('Error en la conexion, tal vez el servidor no esta arriba.',True)
    return None

def ip_origen(sesion, verboso):
    """
    Regresa la dirección IP desde la que se hacen las peticiones
    Recibe:
        sesion (requests.session) - Sesión a utilizar
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        str - Dirección IP origen
    """
    reporta('Obteniendo dirección IP origen', verboso)
    return sesion.get('http://myexternalip.com/raw').text[:-1]

def elemento_cebecera(peticion, llave, verboso):
    """
    Regresa el elemento de la cabecera expecificado
    Recibe:
        peticion (requests.models.Response) - Petición de la que se extraerá la cabecera
        llave (str) - Elemento de la cabecera a obtener
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        str - Elemento buscado
    """
    reporta("Extrayendo elemento '%s' de cabecera de petición" % llave, verboso)
    return peticion.headers.get(llave, "N/A")

def obten_sesion(tor, verboso):
    """
    Regresa una sesión para realizar peticiones.
    Recibe:
        tor (bool) - De ser True se crea una sesión para usar TOR
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        sesión
    """
    if not tor:
        return requests
    reporta('Creando sesión a través de TOR', verboso)
    sesion = requests.session()
    sesion.proxies = {'http':  'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
    return sesion

def metodos_http(url, sesion, verboso):
    """
    Regresa los métodos HTTP habilitados en el servidor usando
    fuerza bruta.
    Recibe:
        url (str) - URL a ser utilizada
        sesion - Sesión a ser utilizada
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        list - Lista con métodos habilitados
    """
    metodos = []
    reporta('Se intentará obtener métodos permitidos por fuerza bruta', verboso)
    metodos.append("GET")
    reporta('Realizando petición con método HEAD', verboso)
    if sesion.head(url).status_code < 400:
        metodos.append("HEAD")
    reporta('Realizando petición con método POST', verboso)
    if sesion.post(url).status_code < 400:
        metodos.append("POST")
    reporta('Realizando petición con método PUT', verboso)
    if sesion.put(url).status_code < 400:
        metodos.append("PUT")
    reporta('Realizando petición con método DELETE', verboso)
    if sesion.delete(url).status_code < 400:
        metodos.append("DELETE")
    reporta('Realizando petición con método OPTIONS', verboso)
    if sesion.options(url).status_code < 400:
        metodos.append("OPTIONS")
    reporta('Realizando petición con método PATCH', verboso)
    if sesion.patch(url).status_code < 400:
        metodos.append("PATCH")
    return metodos

def obten_cms(peticion, verboso):
    """
    Regresa el nombre del Content Management System utilizado por el servidor.
    Recibe:
        peticion (requests.models.Response) - Petición cuyo contenido será analizado
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        str - Nombre de CMS
    """
    reporta('Obteniendo Content Management System', verboso)
    tree = html.fromstring(peticion.content)
    cms = tree.xpath("//meta[@name='generator']")
    if len(cms) > 0:
        return cms[0].get('content')
    else:
        return "N/A"
    
def obten_metodos(url, sesion, verboso):
    """
    Regresa una lista con los métodos HTTP habilitados en el servidor.
    Recibe:
        url (str) - URL a ser utilizada
        sesion - Sesión a ser utilizada
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        str - Métodos habilitados
    """
    reporta('Obteniendo métodos HTTP permitidos', verboso)
    metodos = sesion.options(url).headers.get("Allow", None)
    if metodos is None:
        reporta('No se pudo extraer métodos permitidos usando OPTIONS', verboso)
        metodos = ','.join(metodos_http(url, sesion, verboso))
    return metodos

def obten_correos(peticion, verboso):
    """
    Regresa una lista con los correos encontrados la página.
    Recibe:
        peticion (requests.models.Response) - Petición cuyo contenido será analizado
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        list - Lista con los correos
    """
    correo_regexp = r"[a-zA-Z0-9.!#$%&’*+/=?^_`|~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*"
    reporta('Obteniendo correos en el contenido de la petición realizada', verboso)
    return re.findall(correo_regexp, peticion.text)

def obten_bool(atributo, conf, op):
    """
    Regresa el valor del atributo booleano de acuerdo a su valor op
    en las opciones de la terminal y el archivo de configuración conf
    Recibe:
        atributo (str) - Nombre del atributo
        conf (dict) - Diccionario con los valores del archivo de configuración
        op (bool) - Valor del atributo en las opciones de la terminal
    Regresa:
        bool - Valor final del atributo
    """
    if op or conf is None:
        return op
    res = False
    try:
        res = conf.getboolean(atributo, fallback=False)
    except:
        error("El parámetro '%s' del archivo de configuración debe de ser un valor booleano" % atributo, True)
    return res
        
def obten_valores(ops, conf):
    """
    Regresa un diccionario con los valores de los parámetros finales a ser utilizados en el programa.
    Recibe:
        ops (optparse.OptionParser) - Objeto con los valores de los parámetro obtenidos de la terminal
        conf (dict) - Diccionario con los valores del archivo de configuración
    Regresa:
        dict - Diccionario con los valores de los parámetros
    """
    valores = {}
    valores['reporte'] = ops.reporte if ops.reporte is not None or conf is None else conf.get('reporte', 'reporte.txt')
    valores['agente'] = ops.agente if ops.agente is not None or conf is None else conf.get('agente_usuario', None)
    valores['servidor'] = ops.servidor if ops.servidor is not None or conf is None else conf.get('servidor', None)
    valores['archivos'] = ops.archivos if ops.archivos is not None or conf is None else conf.get('archivos', None)
    valores['verboso'] = obten_bool('modo_verboso', conf, ops.verboso)
    valores['cabeceras'] = obten_bool('cabeceras', conf, ops.cabeceras)
    valores['metodos'] = obten_bool('metodos_http', conf, ops.metodos)
    valores['correos'] = obten_bool('correos', conf, ops.correos)
    valores['cms'] = obten_bool('cms', conf, ops.cms)
    valores['tor'] = obten_bool('tor', conf, ops.tor)
    valores['tls'] = obten_bool('tls', conf, ops.tls)    
    valores['puerto'] = ops.puerto if ops.puerto >= 0 or conf is None else conf.getint('puerto', -1)
    if valores['puerto'] < 0 or valores['puerto'] > 49151:
        valores['puerto'] = 443 if valores['tls'] else 80
    if valores['reporte'] is None:
        valores['reporte'] = 'reporte.txt'
    return valores

def leer_configuracion(archivo):
    """
    Lee el archivo de configuración y regresa un diccionario con los valores que éste indica.
    Recibe:
        archivo (str) - Nombre del archivo de configuración
    Regresa:
        dict - Diccionario con los valores de los parámetros
    """
    res = {}
    try:
        config = configparser.ConfigParser()
        config.read(archivo)
        res = config['PARAMETROS']
    except:
        error("Hubo un problema al leer el archivo de configuración", True)
    return res

def obten_archivos(sesion, url, archivo, agente, verboso):
    """
    Regresa una lista con los archivos sensibles encontrados en el servidor,
    los nombres de éstos se extraen de un archivo.
    Recibe:
        sesion - Sesion a utilizar para hacer las peticiones
        url (str) - URL a utilizar        
        archivo (str) - Nombre del archivo donde se listan los archivos sensibles a buscar
        agente (str) - Agente de usuario a utilizar.
        verboso (bool) - De ser True se utiliza el modo verboso
    Regresa:
        dict - Diccionario con los valores de los parámetros
    """
    encontrados = []
    if url[-1] != '/':
        url = url + "/"
    try:
        with open(archivo) as f:
            archivos = [x[:-1] for x in f.readlines()]
            for a in archivos:
                path = '%s%s' % (url, a)
                reporta('Buscando archivo %s' % path, valores['verboso'])
                peticion = hacer_peticion(path, sesion, agente, verboso)
                historial = [str(x.status_code)[0] for x in peticion.history]
                if peticion.status_code == 200 and '3' not in historial:
                    reporta('Archivo %s encontrado' % path, valores['verboso'])
                    encontrados.append(a)
                else:
                    reporta('Archivo %s no encontrado' % path, valores['verboso'])
    except IOError:
        error('Hubo un problema al abrir archivo %s' % archivo)
    return encontrados
    
if __name__ == '__main__':
    try:
        ops = opciones()
        config = None if ops.config is None else leer_configuracion(ops.config)
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
            cms = "Content Management System: %s" % obten_cms(peticion, valores['verboso'])
            reporta(cms, valores['verboso'], True)
        if valores['correos']:
            correos = "Correos encontrados: %s" % ', '.join(obten_correos(peticion, valores['verboso']))
            reporta(correos, valores['verboso'], True)
        if valores['archivos'] is not None:
            archivos = "Archivos sensibles encontrados: %s" % ', '.join(obten_archivos(sesion, url, valores['archivos'], valores['agente'], valores['verboso']))
            reporta(archivos, valores['verboso'], True)
        escribe_reporte(valores['reporte'], valores['verboso'])
    except Exception as e:
        error('Ocurrió un error inesperado')
        error(e, True)
