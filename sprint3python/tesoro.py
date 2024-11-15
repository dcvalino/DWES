import random

class Tesoro:
    def __init__(self):
        self.beneficios = ["aumento_ataque", "aumento_defensa", "restaurar_salud"]

    def encontrar_tesoro(self, heroe):
        beneficio = random.choice(self.beneficios)
        print(f"Héroe ha encontrado un tesoro: {beneficio}.")
        if beneficio == "aumento_ataque":
            heroe.ataque += 5
            print(f"El ataque de {heroe.nombre} aumenta a {heroe.ataque}.")
        elif beneficio == "aumento_defensa":
            heroe.defensa += 5
            print(f"La defensa de {heroe.nombre} aumenta a {heroe.defensa}.")
        elif beneficio == "restaurar_salud":
            heroe.salud = heroe.salud_maxima
            print(f"La salud de {heroe.nombre} ha sido restaurada a {heroe.salud_maxima}.")
