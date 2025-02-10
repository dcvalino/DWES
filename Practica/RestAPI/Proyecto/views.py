import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import UsuarioPersonalizado, Eventos, Comentarios, Reservas
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOrganizador, IsParticipante


# Create your views here.

# CRUD de eventos:
# GET: Listas todos los eventos disponibles
class ListarEventosView(APIView):
    """
    GET: Lista todos los eventos disponibles con filtros y paginación.
    """
    def get(self, request):
        titulo_filtro = request.query_params.get("titulo", "")
        fecha_filtro = request.query_params.get("fecha", "")
        limite = int(request.query_params.get("limite", 5))
        pagina = int(request.query_params.get("pagina", 1))

        eventos = Eventos.objects.all()
        if titulo_filtro:
            eventos = eventos.filter(titulo__icontains=titulo_filtro)
        if fecha_filtro:
            eventos = eventos.filter(fecha=fecha_filtro)
        eventos = eventos.order_by('fecha')

        paginator = Paginator(eventos, limite)
        try:
            eventos_pagina = paginator.page(pagina)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        for e in eventos_pagina:
            results.append({
                "id": e.id,
                "titulo": e.titulo,
                "descripcion": e.descripcion,
                "fecha": e.fecha.strftime("%Y-%m-%d") if e.fecha else "",
                "capacidad": e.capacidad,
                "url": e.url,
                "organizador": {
                    "id": e.organizador.id,
                    "nombre": e.organizador.nombre,
                    "email": e.organizador.email,
                } if e.organizador else None
            })

        data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": pagina,
            "next": pagina + 1 if eventos_pagina.has_next() else None,
            "previous": pagina - 1 if eventos_pagina.has_previous() else None,
            "results": results,
        }
        return Response(data, status=status.HTTP_200_OK)



class CrearEventoView(APIView):
    """
    POST: Crea un evento. (Acceso solo para organizadores)
    """
    permission_classes = [IsAuthenticated, IsOrganizador]

    def post(self, request):
        data = request.data
        # Se asume que el usuario autenticado es el organizador
        organizador = request.user
        evento = Eventos.objects.create(
            titulo=data.get("titulo", ""),
            descripcion=data.get("descripcion", ""),
            fecha=data.get("fecha"),
            capacidad=data.get("capacidad", 0),
            url=data.get("url", ""),
            organizador=organizador,
        )
        return Response({"id": evento.id, "mensaje": "Evento creado"}, status=status.HTTP_201_CREATED)



# PUT/PATCH: Actualizar un evento (solo organizadores)º
class ActualizarEventoView(APIView):
    """
    PUT/PATCH: Actualiza un evento. (Acceso solo para organizadores)
    """
    permission_classes = [IsAuthenticated, IsOrganizador]

    def put(self, request, id):
        data = request.data
        evento = get_object_or_404(Eventos, id=id)
        evento.titulo = data.get("titulo", evento.titulo)
        evento.descripcion = data.get("descripcion", evento.descripcion)
        evento.fecha = data.get("fecha", evento.fecha)
        evento.capacidad = data.get("capacidad", evento.capacidad)
        evento.url = data.get("url", evento.url)
        if "organizador" in data:
            evento.organizador = get_object_or_404(UsuarioPersonalizado, id=data.get("organizador"))
        evento.save()
        return Response({"mensaje": "Evento actualizado"}, status=status.HTTP_200_OK)

    def patch(self, request, id):
        # Se delega en el método PUT para actualizar parcialmente
        return self.put(request, id)

# DELETE: Eliminar un evento (solo organizadores)
class BorrarEventoView(APIView):
    """
    DELETE: Elimina un evento. (Acceso solo para organizadores)
    """
    permission_classes = [IsAuthenticated, IsOrganizador]

    def delete(self, request, id):
        evento = get_object_or_404(Eventos, id=id)
        evento.delete()
        return Response({"mensaje": "Evento eliminado"}, status=status.HTTP_200_OK)

        ##################################


# Gestion de reservas:

# GET: Listar reservas de un usuario autenticado.
class ListarReservasView(APIView):
    """
    GET: Lista las reservas de un evento.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        evento = get_object_or_404(Eventos, id=id)
        reservas = Reservas.objects.filter(evento=evento)
        data = []
        for reserva in reservas:
            data.append({
                "id": reserva.id,
                "usuario": reserva.usuario.id if reserva.usuario else None,
                "evento": reserva.evento.id,
                "entradas_reservadas": reserva.entradas_reservadas,
                "estado": reserva.estado,
            })
        return Response(data, status=status.HTTP_200_OK)


# POST: Crear una nueva reserva.
class CrearReservaView(APIView):
    """
    POST: Crea una reserva. (Acceso solo para participantes)
    """
    permission_classes = [IsAuthenticated, IsParticipante]

    def post(self, request):
        data = request.data
        usuario = get_object_or_404(UsuarioPersonalizado, id=data["usuario"])
        evento = get_object_or_404(Eventos, id=data["evento"])
        reserva = Reservas.objects.create(
            usuario=usuario,
            evento=evento,
            entradas_reservadas=data["entradas_reservadas"],
            estado=data["estado"],
        )
        return Response({"id": reserva.id, "mensaje": "Se ha creado la reserva"}, status=status.HTTP_201_CREATED)


# PUT/PATCH: Actualizar el estado de una reserva (solo organizadores).
class ActualizarReservaView(APIView):
    """
    PUT/PATCH: Actualiza una reserva. (Acceso solo para organizadores)
    """
    permission_classes = [IsAuthenticated, IsOrganizador]

    def put(self, request, id):
        data = request.data
        reserva = get_object_or_404(Reservas, id=id)
        if "usuario" in data:
            reserva.usuario = get_object_or_404(UsuarioPersonalizado, id=data["usuario"])
        if "evento" in data:
            reserva.evento = get_object_or_404(Eventos, id=data["evento"])
        reserva.entradas_reservadas = data.get("entradas_reservadas", reserva.entradas_reservadas)
        reserva.estado = data.get("estado", reserva.estado)
        reserva.save()
        return Response({"mensaje": "Reserva actualizada"}, status=status.HTTP_200_OK)

    def patch(self, request, id):
        return self.put(request, id)


# DELETE: Cancelar una reserva (solo participantes para sus reservas).
class CancelarReservaView(APIView):
    """
    DELETE: Cancela una reserva. (Solo el titular de la reserva, participante, puede cancelarla)
    """
    permission_classes = [IsAuthenticated, IsParticipante]

    def delete(self, request, id):
        reserva = get_object_or_404(Reservas, id=id)
        if request.user != reserva.usuario:
            return Response({"error": "¡No eres el titular!"}, status=status.HTTP_403_FORBIDDEN)
        reserva.delete()
        return Response({"mensaje": "Reserva eliminada"}, status=status.HTTP_200_OK)
        ###################################


# Comentario:
# GET: Listar comentarios de un evento.
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


# POST: Crear un comentario asociado a un evento (solo usuarios autenticados).
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


# Usuario:
# POST: Login
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


# POST: Register
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
