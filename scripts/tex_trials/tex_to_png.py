with open("st_menu_01_spa.tex", "rb") as f:
    header = f.read(0x40)  # read enough to cover critical fields

print(" ".join(f"{b:02X}" for b in header))