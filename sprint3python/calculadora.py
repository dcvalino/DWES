from operaciones import suma, resta, multiplicacion, division

def calculadora():
    while True:
        # Solicitar números al usuario
        try:
            num1 = float(input("Introduce el primer número: "))
            num2 = float(input("Introduce el segundo número: "))
        except ValueError:
            print("Por favor, introduce valores numéricos válidos.")
            continue

        # Solicitar la operación
        print("Selecciona la operación a realizar:")
        print("1. Suma")
        print("2. Resta")
        print("3. Multiplicación")
        print("4. División")

        operacion = input("Introduce el número de la operación (1/2/3/4): ")

        # Ejecutar la operación
        if operacion == "1":
            resultado = suma(num1, num2)
            print(f"El resultado de la suma es: {resultado}")
        elif operacion == "2":
            resultado = resta(num1, num2)
            print(f"El resultado de la resta es: {resultado}")
        elif operacion == "3":
            resultado = multiplicacion(num1, num2)
            print(f"El resultado de la multiplicación es: {resultado}")
        elif operacion == "4":
            resultado = division(num1, num2)
            print(f"El resultado de la división es: {resultado}")
        else:
            print("Operación no válida. Por favor, selecciona una opción correcta.")
            continue

        # Preguntar si el usuario quiere realizar otra operación
        repetir = input("¿Deseas realizar otra operación? (s/n): ").lower()
        if repetir != "s":
            print("Gracias por usar la calculadora. ¡Hasta pronto!")
            break

# Iniciar el programa
if __name__ == "__main__":
    calculadora()

