<?php

$db = mysqli_connect('localhost', 'root', '1234', 'mysitedb');
if (!$db) {
    error_log('Connection error: ' . mysqli_connect_error());
    echo "Error en la conexión a la base de datos.";
    exit;
}//conexion hacia la base de datos


$query = 'SELECT * FROM tJuegos';
$result = mysqli_query($db, $query) or die('Error en la consulta');
//solicito la consulta a la base de datos
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Consulta Tabla Juegos</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        img {
            max-width: 200px;
            height: auto;
        }
    </style>
</head>
<body>
<h1>Consulta tabla Juegos</h1>
<table>
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Precio</th>
            <th>Genero</th>
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
                    <td><a href="/detail.php?id=<?php echo $id; ?>"><?php echo $id; ?></a></td>
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
