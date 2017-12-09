import sys

dicc_letras = {'a':['4','@'], 'i':['1'], 's':['$','5'], 'e':['3'], 'o':['0']}
lst_simbolos = ['$', '*', '%', '@', '_', '-', '.', '!', '']

#lst_sim = lst_simbolos * n
#lst_sim = [x for x in conjunto_potencia(lst_sim) if len(x) == n - 1]
#for l in lst_sim:
#    for x in range(n):
#        x.replace_first(l)

def f(e, t):
    return [x + [e] for x in t]

def conjunto_potencia(l):
    if len(l) == 0:
        return [[]]
    cp = conjunto_potencia(l[1:])
    return cp + f(l[0], cp)
    
def permutaciones_str_lst(lst):
    nueval = []
    for l in lst:
        nueval.append(l + " " + ' '.join([x for x in lst if x != l]))
    return nueval

'''
for l in lst_sim:
    for x in range(n):
        x.replace_first(l)
'''

def combinaciones_lst_simb(n):
    res = []
    for x in range(1, n + 1):
        #res += [x for x in conjunto_potencia(lst_simbolos * n)
        #           if len(x) == n - 1]
    return res
    
def combinaciones_str(s):
    l = []
    for
    return l

def combinaciones_str_lst(lst):
    res = []
    for s in lst:
        res += combinaciones_str(s)
    return res

def escribe_contrasenas(archivo, lst):
    f = open(archivo[:[string.index(".")]] + "_contrasenas.txt", "w")
    for l in lst:
        f.write(l + "\n")
    f.close()
    
def dicc_constrasenas(archivo):
    f = open(archivo)
    lst = f.readlines()
    f.close()
    lst = [x[:-1] for x in lst]
    cp_lst = [x for x in conjunto_potencia(lst)
              if len(x) > 0 and len(x) <= 4]
    lst_permutaciones = []
    for l in cp_lst:
        lst_permutaciones.append(permutaciones_str_lst(l))    
    lst_combinaciones = []
    for l in lst_permutaciones:
        lst_combinaciones += combinaciones_str_lst(l)
    contrasenas = {}
    for l in lst_combinaciones:
        s = ''.join(l)
        contrasenas[s] = s        
    return contrasenas
        
if len(sys.argv) > 1:
    dicc_constrasenas(sys.argv[1])
else:
    print "Uso: python tarea3.py <archivo.txt>"

