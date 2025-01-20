# Proyecto/admin.py
from django.contrib import admin
from .models import UsuarioPersonalizado, Eventos, Reservas, Comentarios

admin.site.register(UsuarioPersonalizado)
admin.site.register(Eventos)
admin.site.register(Reservas)
admin.site.register(Comentarios)
