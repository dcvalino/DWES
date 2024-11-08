<?php
// Conectar a la base de datos
$db = mysqli_connect('localhost', 'root', '1234', 'mysitedb');
if (!$db) {
    die("Error en la conexión a la base de datos: " . mysqli_connect_error());
}

// Verificar que el formulario fue enviado
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'];
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];

    // Verificar si las contraseñas coinciden
    if ($password === $confirm_password) {
        // Verificar si el correo ya está registrado
        $stmt = $db->prepare("SELECT * FROM tUsuarios WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows == 0) {
            // Cifrar la contraseña y registrar al usuario
            $hashed_password = password_hash($password, PASSWORD_DEFAULT);
            $stmt = $db->prepare("INSERT INTO tUsuarios (email, contraseña) VALUES (?, ?)");
            $stmt->bind_param("ss", $email, $hashed_password);
            $stmt->execute();

            // Redirigir si el registro es exitoso
            header("Location: main.php");
            exit();
        } else {
            echo "El correo ya está registrado.";
        }
    } else {
        echo "Las contraseñas no coinciden.";
    }
}

$db->close();
?>
