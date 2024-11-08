<?php

$db = mysqli_connect('localhost', 'root', '1234', 'mysitedb');
if (!$db) {
    error_log('Connection error: ' . mysqli_connect_error());
    echo "Error en la conexión a la base de datos.";
    exit;
}

// Solicito la consulta a la base de datos
$query = 'SELECT * FROM tJuegos';
$result = mysqli_query($db, $query) or die('Error en la consulta');
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Consulta Tabla Juegos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        a {
            display: block;
            text-align: right;
            margin-bottom: 20px;
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            color: #0056b3;
            text-decoration: underline;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:hover td {
            background-color: #f1f1f1;
            transform: scale(1.02); /* Aumenta el tamaño al pasar el ratón */
        }
        img {
            max-width: 150px;
            height: auto;
        }
    </style>
</head>
<body>
    <a href="/logout.php">Logout</a>
    <h1>Consulta tabla Juegos</h1>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Precio</th>
                <th>Género</th>
                <th>Imagen</th>
            </tr>
        </thead>
        <tbody>
            <?php
            // Compruebo si hay resultados
            if (mysqli_num_rows($result) > 0) {
                // Recorro los resultados
                while ($row = mysqli_fetch_array($result)) {
                    $id = $row['id'];
                    $nombre = $row['nombre'];
                    $precio = $row['precio'];
                    $genero = $row['genero'];
                    $url_imagen = $row['url_imagen'];
                    ?>
                    <tr>
                        <td><a href="/detail.php?juego_id=<?php echo $id; ?>"><?php echo $id; ?></a></td>
                        <td><?php echo $nombre; ?></td>
                        <td><?php echo $precio; ?></td>
                        <td><?php echo $genero; ?></td>
                        <td><img src="<?php echo $url_imagen; ?>" alt="Imagen de <?php echo $nombre; ?>"></td>
                    </tr>
                    <?php
                }
            } else {
                echo "<tr><td colspan='5'>No se encontraron resultados.</td></tr>";
            }
            ?>
        </tbody>
    </table>
</body>
</html>

<?php
// Cierro la conexión
mysqli_close($db);
?>
