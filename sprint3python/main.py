from heroe import Heroe
from mazmorra import Mazmorra

def main():
    nombre = input("Introduce el nombre de tu héroe: ")
    heroe = Heroe(nombre)
    mazmorra = Mazmorra(heroe)
    mazmorra.jugar()

if __name__ == "__main__":
    main()
