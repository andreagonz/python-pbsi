from re import findall, search

dirIPv4 = r"([0-9]{1,3}\.){3}[0-9]{1,3}"
correo = r"[a-zA-Z0-9]+@([a-z]+\.)+[a-z]+"

print findall(dirIPv4, "123.144.13.1")
print findall(correo, "hola@hola.com")
