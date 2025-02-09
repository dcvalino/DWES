from django.db import models
from django.contrib.auth.models import AbstractUser


class UsuarioPersonalizado(AbstractUser):
    TIPO_USUARIO = [
        ('organizador', 'Organizador'),
        ('asistente', 'Asistente')
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='asistente')
    nombre = models.CharField(max_length=25)
    email = models.CharField(max_length=100, unique=True)
    contrasenha = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Eventos(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    fecha = models.DateField()
    capacidad = models.PositiveIntegerField()
    url = models.URLField(max_length=200, blank=True, null=True)  # Asignamos correctamente el tipo de campo
    organizador = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, related_name="eventos",
                                    limit_choices_to={'tipo': 'organizador'})

    def __str__(self):
        return self.titulo


class Reservas(models.Model):
    Estado_Reserva = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada')
    ]
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, related_name="reservas", limit_choices_to={'tipo': 'asistente'})
    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE, related_name="reservas")
    entradas_reservadas = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=Estado_Reserva, default='pendiente')

    def __str__(self):
        return f"Reserva para el evento '{self.evento.titulo}' a nombre de {self.usuario.username}"


class Comentarios(models.Model):
    texto = models.TextField()
    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE, related_name="comentarios")
    FechaC = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario en el evento '{self.evento.titulo}'"
