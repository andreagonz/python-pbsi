from re import findall, search

dirIPv4 = r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}"
correo = r"[a-zA-Z0-9]+(?:[\.\_-]?[a-zA-Z0-9]+)*@(?:[a-z]+\.)+[a-z]+"

print findall(dirIPv4, "123.144.13.1 0.0.0.0")
print findall(correo, "ola.hola-2_42.dads24-dd.asAD424@hola.com.mx")
