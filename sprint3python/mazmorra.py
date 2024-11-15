from heroe import Heroe
from monstruo import Monstruo
from tesoro import Tesoro

class Mazmorra:
    def __init__(self, heroe):
        self.heroe = heroe
        self.monstruos = [
            Monstruo("Impuestos", 8, 3, 30),
            Monstruo("Hacienda", 12, 5, 50),
            Monstruo("NicolBolas", 20, 10, 100),
        ]
        self.tesoro = Tesoro()

    def jugar(self):
        print("Héroe entra en la mazmorra.")
        while self.monstruos and self.heroe.esta_vivo():
            enemigo = self.monstruos.pop(0)
            print(f"Te has encontrado con un {enemigo.nombre}.")
            self.enfrentar_enemigo(enemigo)
            if self.heroe.esta_vivo():
                self.buscar_tesoro()
        if self.heroe.esta_vivo():
            print(f"¡{self.heroe.nombre} ha derrotado a todos los monstruos y ha conquistado la mazmorra!")
        else:
            print("Héroe ha sido derrotado en la mazmorra.")

    def enfrentar_enemigo(self, enemigo):
        while enemigo.esta_vivo() and self.heroe.esta_vivo():
            print("¿Qué deseas hacer?")
            print("1. Atacar")
            print("2. Defender")
            print("3. Curarse")
            opcion = input("Selecciona una opción: ")
            if opcion == "1":
                self.heroe.atacar(enemigo)
            elif opcion == "2":
                self.heroe.defenderse()
            elif opcion == "3":
                self.heroe.curarse()
            else:
                print("Opción no válida.")
                continue
            if enemigo.esta_vivo():
                enemigo.atacar(self.heroe)
            self.heroe.reset_defensa()

    def buscar_tesoro(self):
        print("Buscando tesoro...")
        self.tesoro.encontrar_tesoro(self.heroe)

