"""
URL configuration for RestAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Proyecto import views
urlpatterns = [
    path('admin/', admin.site.urls),


    # Endpoints de eventos
    path("eventos/listar/", views.ListarEventos, name="listar_evento"),
    path("eventos/crear/", views.CrearEvento, name="crear_evento"),
    path("eventos/actualizar/<int:id>/", views.ActualizarEvento, name="actualizar_evento"),
    path("eventos/borrar/<int:id>/", views.BorrarEvento, name="borrar_evento"),

    # Endpoints de reservas
    path("reservas/crear/", views.CrearReserva, name="crear_reserva"),
    path("reservas/actualizar/<int:id>/", views.ActualizarReserva, name="actualizar_reserva"),
    path("reservas/cancelar/<int:id>/", views.CancelarReserva, name="cancelar_reserva"),
    path("reservas/listar/<int:id>/", views.listarReservas, name="listar_reservas"),

    # Endpoints de comentarios
    path("comentarios/crear/<int:id>/", views.CrearComentario, name="crear_comentario"),
    path("comentarios/listar/<int:id>/", views.ListarComentarios, name="listar_comentarios"),

    #Endpoint de registrar
    path("register/", views.Register, name="Register"),
    path("login/", views.Login, name="login"),
]

