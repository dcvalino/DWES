import json

from django.shortcuts import render
from django.http import JsonResponse
from .models import UsuarioPersonalizado, Eventos, Comentarios, Reservas
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import F


# Create your views here.

# CRUD de eventos:
# GET: Listas todos los eventos disponibles
def ListarEentos(request):
    Eventos.titulo = request.GET.get("titulo", "")  # Filtrar por nombre
    Eventos.fecha = request.GET.get("fecha", "")  # Filtrar por nombre
    limite = int(request.GET.get("limite", 5))  # Resultados por página
    pagina = int(request.GET.get("pagina", 1))  # Página actual

    eventos = Eventos.objects.all()

    # Filtrar y ordenar productos
    eventos = Eventos.objects.filter(nombre__icontains=Eventos.titulo).order_by()

    eventos = Eventos.objects.filter(nombre__icontains=F(Eventos.fecha)).order_by()

    # Paginación
    paginator = Paginator(eventos, limite)  # Dividir productos en páginas de tamaño `limite`

    try:
        eventos_pagina = paginator.page(pagina)  # Obtener los productos de la página actual
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)  # Manejar errores de paginación

    # Crear respuesta con datos paginados
    data = {
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": pagina,
        "next": pagina + 1 if eventos_pagina.has_next() else None,
        "previous": pagina - 1 if eventos_pagina.has_previous() else None,
        "results": [
            {"id": e.titulo, "descripcion": e.descripcion, "fecha": e.fecha, "capacidad": e.capacidad, "url": e.url,
             "organizador": e.organizador} for e in eventos_pagina
        ]  # Resultados actuales
    }

    return JsonResponse(data, safe=False)


# POST: Crear un evento(solo organizadores)
def CrearEvento(request):
    if request.method == "POST":
        data = json.loads(request.body)

        if request.user.tipo != "organizador":
            return JsonResponse(
                {"error": "¡No eres un organizador"},
                status=403
            )
        evento = Eventos.objects.create(
            titulo=data["titulo"],
            descripcion=data["descripcion"],
            fecha=data["fecha"],
            capacidad=data["capacidad"],
            url=data["url"],
            organizador=["organizador"]

        )
        return JsonResponse({"id": evento.id, "mensaje": "Se ha creado el evento"})


# PUT/PATCH: Actualizar un evento (solo organizadores)º
@csrf_exempt

def ActualizarEvento(request, id):
    if request.method in ["PUT", "PATCH"]:
        data = json.loads(request.body)
        if request.user.tipo != "organizador":
            return JsonResponse(
                {"error": "¡No eres un organizador"},
                status=403
            )
            data = json.loads(request.body)
            evento = Eventos.objects.get(id=id)
            evento.titulo = data.get("titulo", evento.titulo)
            evento.descripcion = data.get("descripcion", evento.descripcion)
            evento.fecha = data.get("fecha", evento.fecha)
            evento.capacidad = data.get("capacidad", evento.capacidad)
            evento.url = data.get("url", evento.url)
            evento.organizador = data.get("organizador", evento.organizador)

            evento.save()
            return JsonResponse({"mensaje": "Evento actualizado"})


# DELETE: Eliminar un evento (solo organizadores)
@csrf_exempt

def BorrarEvento(request, id):
    if request.method == "DELETE":
        evento = Eventos.objects.get(id=id)
        if request.user.tipo != "organizador":
            return JsonResponse(
                {"error": "¡No eres un organizador!"},
                status=403
            )

        evento.delete()
        return JsonResponse({"mensaje": "Evento eliminado"})