import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import UsuarioPersonalizado, Eventos, Comentarios, Reservas
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import F


# Create your views here.

# CRUD de eventos:
# GET: Listas todos los eventos disponibles

def ListarEventos(request):
    titulo_filtro = request.GET.get("titulo", "")
    fecha_filtro = request.GET.get("fecha", "")
    limite = int(request.GET.get("limite", 5))
    pagina = int(request.GET.get("pagina", 1))

    eventos = Eventos.objects.all()

    # Aplicar filtros
    if titulo_filtro:
        eventos = eventos.filter(titulo__icontains=titulo_filtro)
    if fecha_filtro:
        eventos = eventos.filter(fecha=fecha_filtro)

    # Ordenar por fecha
    eventos = eventos.order_by('fecha')

    # Paginación
    paginator = Paginator(eventos, limite)

    try:
        eventos_pagina = paginator.page(pagina)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Crear respuesta con datos paginados
    data = {
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": pagina,
        "next": pagina + 1 if eventos_pagina.has_next() else None,
        "previous": pagina - 1 if eventos_pagina.has_previous() else None,
        "results": [
            {
                "id": e.id,
                "titulo": e.titulo,
                "descripcion": e.descripcion,
                "fecha": e.fecha.strftime("%Y-%m-%d"),
                "capacidad": e.capacidad,
                "url": e.url,
                "organizador": {
                    "id": e.organizador.id,
                    "nombre": e.organizador.nombre,
                    "email": e.organizador.email
                } if e.organizador else None
            }
            for e in eventos_pagina
        ]
    }

    return JsonResponse(data, safe=False)


# POST: Crear un evento(solo organizadores)
@csrf_exempt
def CrearEvento(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Datos JSON inválidos"}, status=400)


    # Buscar organizador en los datos (opcional)
    organizador_name = data.get("organizador", request.user.id)
    organizador = get_object_or_404(UsuarioPersonalizado, id=organizador_name)

    evento = Eventos.objects.create(
        titulo=data.get("titulo", ""),
        descripcion=data.get("descripcion", ""),
        fecha=data.get("fecha"),
        capacidad=data.get("capacidad", 0),
        url=data.get("url", ""),
        organizador=organizador  # Asigna el organizador correctamente
    )

    return JsonResponse({"id": evento.id, "mensaje": "Evento creado"}, status=201)



# PUT/PATCH: Actualizar un evento (solo organizadores)º
@csrf_exempt
def ActualizarEvento(request, id):
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Datos JSON inválidos"}, status=400)

    evento = get_object_or_404(Eventos, id=id)

    # Actualizar solo los campos proporcionados
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
        evento.delete()
        return JsonResponse({"mensaje": "Evento eliminado"})

            ##################################
# Gestion de reservas:

#GET: Listar reservas de un usuario autenticado.
@csrf_exempt

def listarReservas(request,id):
    if (request.method == 'GET'):
        reservas = Reservas.objects.all()

        evento = get_object_or_404(Eventos, id=id)

        reservas = Reservas.objects.filter(evento=evento)

        data = [
            {
                "id": reserva.id,
                "usuario": reserva.usuario.id if reserva.usuario else None,
                "evento": reserva.evento.id,
                "entradas_reservadas": reserva.entradas_reservadas,
                "estado": reserva.estado,
            }
            for reserva in reservas
        ]

        return JsonResponse(data, safe=False)

#POST: Crear una nueva reserva.
@csrf_exempt
def CrearReserva(request):
    if request.method == "POST":
        data = json.loads(request.body)
        usuario = get_object_or_404(UsuarioPersonalizado, id=data["usuario"])
        evento = get_object_or_404(Eventos, id=data["evento"])

        reserva = Reservas.objects.create(
            usuario=usuario,
            evento=evento,
            entradas_reservadas=data["entradas_reservadas"],
            estado=data["estado"],
        )
        return JsonResponse({"id": reserva.id, "mensaje": "Se ha creado la reserva"})

#PUT/PATCH: Actualizar el estado de una reserva (solo organizadores).
@csrf_exempt
def ActualizarReserva(request, id):
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Datos inválidos"}, status=400)

    reserva = get_object_or_404(Reservas, id=id)

    if "usuario" in data:
        reserva.usuario = get_object_or_404(UsuarioPersonalizado, id=data["usuario"])

    if "evento" in data:
        reserva.evento = get_object_or_404(Eventos, id=data["evento"])

    reserva.entradas_reservadas = data.get("entradas_reservadas", reserva.entradas_reservadas)
    reserva.estado = data.get("estado", reserva.estado)

    reserva.save()

    return JsonResponse({"mensaje": "Reserva Actualizada"})

#DELETE: Cancelar una reserva (solo participantes para sus reservas).
@csrf_exempt
def CancelarReserva(request, id):
    if request.method == "DELETE":
        reserva = Reservas.objects.get(id=id)
        if request.user != reserva.usuario:
            return JsonResponse(
                {"error": "¡No eres el titular!"},
                status=403
            )

        reserva.delete()
        return JsonResponse({"mensaje": "Reserva eliminado"})
            ###################################
#Comentario:
#GET: Listar comentarios de un evento.
@csrf_exempt
def ListarComentarios(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    evento = get_object_or_404(Eventos, id=id)
    comentarios = Comentarios.objects.filter(evento=evento)

    data = [
        {
            "id": comentario.id,
            "texto": comentario.texto,
            "FechaC": comentario.FechaC.strftime("%Y-%m-%d %H:%M:%S")
        }
        for comentario in comentarios
    ]

    return JsonResponse(data, safe=False)
#POST: Crear un comentario asociado a un evento (solo usuarios autenticados).
@csrf_exempt
def CrearComentario(request, id):
    if (request.method == "POST"):
        evento = get_object_or_404(Eventos, id=id)
        data = json.loads(request.body)

        comentario = Comentarios.objects.create(
            texto=data.get("texto", ""),
            evento=evento,
        )
        return JsonResponse({"id": comentario.id, "mensaje": "Se ha creado el comentario"})

            ###################################
#Usuario:
#POST: Login
@csrf_exempt
def Login(request):
    if request.method != 'POST':
        return JsonResponse({"error": "El cuerpo de la solicitud no es un JSON válido."}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "El cuerpo de la solicitud no es un JSON válido."}, status=400)

    email = data.get("email")
    contrasenha = data.get("contrasenha")

    if not email or not contrasenha:
        return JsonResponse({"error": "Faltan datos requeridos."}, status=400)

    try:
        usuario = UsuarioPersonalizado.objects.get(email=email)
    except UsuarioPersonalizado.DoesNotExist:
        return JsonResponse({"error": "Credenciales inválidas."}, status=400)

    if usuario.contrasenha != contrasenha:
        return JsonResponse({"error": "Credenciales inválidas."}, status=400)

    return JsonResponse({"mensaje": "Inicio de sesión exitoso."})




#POST: Register
@csrf_exempt
def Register(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        # Cargar el JSON enviado en el cuerpo de la solicitud
        data = json.loads(request.body)

        # Obtener datos del JSON
        nombre = data.get('nombre')
        email = data.get('email')
        contrasenha = data.get('contrasenha')
        tipo = data.get('tipo')
        biografia = data.get('biografia', '')

        # Validación: verificar que todos los datos requeridos estén presentes
        if not all([nombre, email, contrasenha, tipo]):
            return JsonResponse({"error": "Faltan datos requeridos."}, status=400)

        # Verificar si ya existe un usuario con el mismo email
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            return JsonResponse({"error": "El email ya está registrado."}, status=400)

        # Crear el usuario
        usuario = UsuarioPersonalizado.objects.create(
            username=email,
            nombre=nombre,
            email=email,
            contrasenha=contrasenha,  # ⚠ Se guarda en texto plano (no recomendado para producción)
            tipo=tipo,
            biografia=biografia
        )
        usuario.save()

        return JsonResponse({"mensaje": "Usuario registrado correctamente."}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "El cuerpo de la solicitud no es un JSON válido."}, status=400)
