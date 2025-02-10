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
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    #Endpoints de Eventos
    path("eventos/listar/", views.ListarEventosView.as_view(), name="listar_evento"),
    path("eventos/crear/", views.CrearEventoView.as_view(), name="crear_evento"),
    path("eventos/actualizar/<int:id>/", views.ActualizarEventoView.as_view(), name="actualizar_evento"),
    path("eventos/borrar/<int:id>/", views.BorrarEventoView.as_view(), name="borrar_evento"),
    #Endpoints de Reservas
    path("reservas/listar/<int:id>/", views.ListarReservasView.as_view(), name="listar_reservas"),
    path("reservas/crear/", views.CrearReservaView.as_view(), name="crear_reserva"),
    path("reservas/actualizar/<int:id>/", views.ActualizarReservaView.as_view(), name="actualizar_reserva"),
    path("reservas/cancelar/<int:id>/", views.CancelarReservaView.as_view(), name="cancelar_reserva"),
    #Endpoints de Comentarios
    path("comentarios/listar/<int:id>/", views.ListarComentariosView.as_view(), name="listar_comentarios"),
    path("comentarios/crear/<int:id>/", views.CrearComentarioView.as_view(), name="crear_comentario"),
    #Endpoints de Login
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
]


