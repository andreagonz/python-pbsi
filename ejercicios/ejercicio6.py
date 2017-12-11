print {x : (bin(x), hex(x)) for x in range(50) if bin(x)[2:].count("1") & 1}
