def palindromo(s):
    s = s.replace(" ","").lower()
    return s == s[::-1]

print "'Anita Lava La Tina' es palindromo: ", palindromo("Anita Lava La Tina")
print "'Hola' es palindromo: ", palindromo("Hola")
