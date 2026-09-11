import gpib

for address in (1, 2, 3):
    inst = gpib.dev(0, address)
    gpib.write(inst, "*IDN?\n")
    print(address, gpib.read(inst, 1000).decode().strip())