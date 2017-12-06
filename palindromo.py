def palindromo(s):
    s = s.replace(" ","").lower()
    return s == s[::-1]

print palindromo("Anita Lava La tina")
