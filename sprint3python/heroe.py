class Heroe:
    def __init__(self, nombre):
        self.nombre = nombre
        self.ataque = 10
        self.defensa = 5
        self.salud = 100
        self.salud_maxima = 100

    def atacar(self, enemigo):
        print(f"Héroe ataca a {enemigo.nombre}.")
        dano = max(0, self.ataque - enemigo.defensa)
        if dano > 0:
            enemigo.salud -= dano
            print(f"El enemigo {enemigo.nombre} ha recibido {dano} puntos de daño.")
        else:
            print("El enemigo ha bloqueado el ataque.")

    def curarse(self):
        curacion = 20
        self.salud = min(self.salud + curacion, self.salud_maxima)
        print(f"Héroe se ha curado. Salud actual: {self.salud}")

    def defenderse(self):
        self.defensa += 5
        print(f"Héroe se defiende. Defensa aumentada temporalmente a {self.defensa}.")

    def reset_defensa(self):
        self.defensa = 5
        print(f"La defensa de {self.nombre} vuelve a la normalidad.")

    def esta_vivo(self):
        return self.salud > 0
