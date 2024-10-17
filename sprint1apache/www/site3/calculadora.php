<html>
<body>
<h1>Calculadora</h1>
<p>Haz los cálculos necesarios</p>
<p>
<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $_digito1 = $_POST["digito1"];
    $_digito2 = $_POST["digito2"];
    $_Operacion = $_POST["Operaciones"];

    function Suma($_digito1, $_digito2) {
        return $_digito1 + $_digito2;
    }

    function Resta($_digito1, $_digito2) {
        return $_digito1 - $_digito2;
    }

    function Multiplicar($_digito1, $_digito2) {
        return $_digito1 * $_digito2;
    }

    function Dividir($_digito1, $_digito2) {
        if ($_digito2 != 0) {
            return $_digito1 / $_digito2;
        } else {
            return "Error: División por cero";
        }
    }

    switch ($_Operacion) {
        case "sumar":
            $resultado = Suma($_digito1, $_digito2);
            break;
        case "resta":
            $resultado = Resta($_digito1, $_digito2);
            break;
        case "multiplicar":
            $resultado = Multiplicar($_digito1, $_digito2);
            break;
        case "dividir":
            $resultado = Dividir($_digito1, $_digito2);
            break;
        default:
            $resultado = "Operación no soportada";
    }

    echo "El resultado es: " . $resultado;
}
?>
</p>
<form action="/calculadora.php" method="post">
    <label for="pdigito">Primer número:</label><br>
    <input type="text" id="pdigito" name="digito1" required><br>
    
    <label for="sdigito">Segundo número:</label><br>
    <input type="text" id="sdigito" name="digito2" required><br>

    <label for="lang">Operaciones:</label>
    <select name="Operaciones" id="lang">
        <option value="sumar">Suma</option>
        <option value="resta">Resta</option>
        <option value="multiplicar">Multiplicar</option>
        <option value="dividir">Dividir</option>
    </select>
    
    <input type="submit" value="Calcular">
</form>
</body>
</html>
